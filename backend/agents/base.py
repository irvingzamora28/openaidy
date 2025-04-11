"""
Direct MCP tool integration without smolagents dependency.
"""
from typing import List, Dict, Any, Optional
import asyncio
import os
import base64
from pydantic import BaseModel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    description: str
    mcp_tools: List[str]  # MCP tools to use
    custom_tools: List[str] = []  # Additional custom tools
    # MCP server configuration
    mcp_command: str
    mcp_args: List[str]

class BaseAgentSession:
    """Base class for agent sessions with direct MCP integration."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with the given configuration."""
        self.config = config
        self.mcp_session: Optional[ClientSession] = None
        self._transport = None
        self.client_ctx = None
        self.server_params = None
        self._tools: Dict[str, Any] = {}

    async def initialize(self, timeout=60):
        """Initialize MCP session and tools with timeout."""
        try:
            # Setup MCP server parameters
            print(f"Starting MCP server: {self.config.mcp_command} {' '.join(self.config.mcp_args)}")
            self.server_params = StdioServerParameters(
                command=self.config.mcp_command,
                args=self.config.mcp_args,
                env=os.environ.copy()  # Pass current environment
            )

            # Create MCP session using stdio_client
            print("Creating MCP session...")
            self.client_ctx = stdio_client(self.server_params)
            self._transport = await self.client_ctx.__aenter__()
            read_stream, write_stream = self._transport

            # Create the client session
            self.mcp_session = ClientSession(read_stream, write_stream)

            # Initialize the session with timeout
            print("Initializing session...")
            try:
                # Set a timeout for initialization
                init_task = asyncio.create_task(self.mcp_session.initialize())
                try:
                    await asyncio.wait_for(init_task, timeout)
                    print("Session initialized successfully")
                except asyncio.TimeoutError:
                    print(f"Session initialization timed out after {timeout} seconds, but continuing...")
                    # We'll continue anyway since the initialization might still be in progress
            except Exception as e:
                print(f"Error during initialization: {e}")
                await self.cleanup()
                raise

            # List available tools
            print("Listing tools...")
            try:
                # Set a timeout for listing tools
                tools_task = asyncio.create_task(self.mcp_session.list_tools())
                try:
                    tools_result = await asyncio.wait_for(tools_task, 10)
                    available_tools = [tool.name for tool in tools_result.tools]
                    print(f"Available tools: {available_tools}")

                    # Register requested tools
                    for tool_name in self.config.mcp_tools:
                        if tool_name in available_tools:
                            self._tools[tool_name] = tool_name
                            print(f"Registered tool: {tool_name}")
                        else:
                            print(f"Warning: Requested tool '{tool_name}' not available")
                except asyncio.TimeoutError:
                    print("Tool listing timed out, assuming tools are available...")
                    # Assume the requested tools are available
                    for tool_name in self.config.mcp_tools:
                        self._tools[tool_name] = tool_name
                        print(f"Assumed tool available: {tool_name}")
            except Exception as e:
                print(f"Error listing tools: {e}")
                # Continue anyway, we'll try to use the tools

            print("Initialization completed")

        except Exception as e:
            print(f"Initialization error: {str(e)}")
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize agent: {str(e)}") from e

    async def run(self, task: str) -> Dict[str, Any]:
        """Run a task using available tools."""
        if not self.mcp_session:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        print(f"Running task: {task}")
        try:
            if "navigate" in task.lower():
                return await self._navigate(task)
            elif "screenshot" in task.lower():
                return await self._take_screenshot()
            else:
                raise ValueError(f"Task not recognized: {task}")
        except Exception as e:
            print(f"Error executing task: {e}")
            raise

    async def _navigate(self, task: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        lower_task = task.lower()
        nav_index = lower_task.find("navigate to ")
        if nav_index != -1:
            url = task[nav_index + len("navigate to "):].strip()
            print(f"Navigating to URL: {url}")

            # Call the navigate tool with timeout
            try:
                navigate_task = asyncio.create_task(
                    self.mcp_session.call_tool("browser_navigate", {"url": url})
                )
                try:
                    await asyncio.wait_for(navigate_task, 30)
                    return {'response': f"Navigated to {url}"}
                except asyncio.TimeoutError:
                    print("Navigation timed out, but continuing...")
                    return {'response': f"Navigation to {url} started (timed out waiting for completion)"}
            except Exception as e:
                print(f"Error during navigation: {e}")
                raise
        else:
            raise ValueError(f"Could not extract URL from task: {task}")

    async def _take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot."""
        print("Taking screenshot...")

        # Call the screenshot tool with timeout
        try:
            screenshot_task = asyncio.create_task(
                self.mcp_session.call_tool("browser_screen_capture", {})
            )
            try:
                result = await asyncio.wait_for(screenshot_task, 30)

                # Process the result
                if result and result.content:
                    for content in result.content:
                        if hasattr(content, 'data') and content.data:
                            # Convert image data to base64 string
                            encoded_image = base64.b64encode(content.data).decode('utf-8')
                            return {'image_base64': encoded_image}

                    # If no image data found but we have content
                    return {'response': str(result.content)}
                else:
                    return {'response': "Screenshot taken, but no image data returned"}
            except asyncio.TimeoutError:
                print("Screenshot timed out, but continuing...")
                return {'response': "Screenshot started (timed out waiting for completion)"}
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            raise

    async def cleanup(self):
        """Cleanup MCP session and transport."""
        print("Cleaning up resources...")

        try:
            # Clear session
            self.mcp_session = None

            # Exit context manager
            if self.client_ctx:
                try:
                    # Set a timeout for exiting the context manager
                    exit_task = asyncio.create_task(
                        self.client_ctx.__aexit__(None, None, None)
                    )
                    try:
                        await asyncio.wait_for(exit_task, 5)
                        print("Context manager exited successfully")
                    except asyncio.TimeoutError:
                        print("Context manager exit timed out, continuing...")
                except Exception as e:
                    print(f"Error exiting context manager: {e}")

                self.client_ctx = None
                self._transport = None

            # Clear tools
            self._tools = {}
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")