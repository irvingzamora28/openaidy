"""
Efficient MCP client implementation using the official Python MCP SDK.

This module provides a more efficient implementation of MCP client
communication, following the official documentation and best practices.
"""
from typing import Dict, Any, List
import os
import base64
from pydantic import BaseModel

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class EfficientMCPConfig(BaseModel):
    """Configuration for the EfficientMCP client."""
    name: str
    description: str
    command: str
    args: List[str]
    tools: List[str]

class EfficientMCPAgent:
    """
    An efficient MCP agent implementation using the official Python MCP SDK.

    This implementation follows the official documentation and best practices
    for better performance.
    """

    def __init__(self, config: EfficientMCPConfig):
        """Initialize the EfficientMCP agent with the given configuration."""
        self.config = config
        self.session = None
        self._client_ctx = None
        self._tools = {}

    async def initialize(self):
        """Initialize the agent."""
        print(f"Starting MCP server: {self.config.command} {' '.join(self.config.args)}")

        # Create server parameters
        self.server_params = StdioServerParameters(
            command=self.config.command,
            args=self.config.args,
            env=os.environ.copy()
        )

        # We'll store the transport and session for later use
        # but we won't enter the context managers yet
        # This will be done in each method call

        # List the tools we expect to use
        self._tools = {tool: tool for tool in self.config.tools}
        print(f"Agent initialized with tools: {list(self._tools.keys())}")

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        print(f"Navigating to URL: {url}")

        # Use the context managers as shown in the documentation
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # Call the navigate tool
                await session.call_tool("browser_navigate", {"url": url})

                return {"response": f"Navigated to {url}"}

    async def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot."""
        print("Taking screenshot...")

        # Use the context managers as shown in the documentation
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # Call the screenshot tool
                result = await session.call_tool("browser_screen_capture", {})

                # Process the result
                if result and hasattr(result, 'content') and result.content:
                    for content in result.content:
                        if hasattr(content, 'data') and content.data:
                            # Convert image data to base64 string
                            encoded_image = base64.b64encode(content.data).decode('utf-8')
                            return {"image_base64": encoded_image}

                    # If no image data found in the expected format, try to inspect the result
                    print(f"Screenshot result structure: {type(result)}")
                    if hasattr(result, '__dict__'):
                        print(f"Screenshot result attributes: {result.__dict__}")

                    # Try to extract data from different possible formats
                    if hasattr(result, 'data') and result.data:
                        encoded_image = base64.b64encode(result.data).decode('utf-8')
                        return {"image_base64": encoded_image}

                    # If we still can't find the data, return a detailed response
                    return {"response": f"Screenshot taken, but couldn't extract image data. Result type: {type(result)}"}

                return {"response": "Screenshot taken, but unexpected response format"}

    async def run(self, task: str) -> Dict[str, Any]:
        """Run a task."""
        print(f"Running task: {task}")

        try:
            if "navigate" in task.lower():
                # Extract URL from task
                lower_task = task.lower()
                nav_index = lower_task.find("navigate to ")
                if nav_index != -1:
                    url = task[nav_index + len("navigate to "):].strip()
                    return await self.navigate(url)
                else:
                    raise ValueError(f"Could not extract URL from task: {task}")

            elif "screenshot" in task.lower():
                return await self.take_screenshot()

            else:
                raise ValueError(f"Task not recognized: {task}")

        except Exception as e:
            print(f"Error executing task: {e}")
            raise

    async def run_sequence(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Run a sequence of tasks in a single session."""
        print(f"Running sequence of {len(tasks)} tasks")

        results = []

        # Use a single session for all tasks
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                for task in tasks:
                    print(f"Running task: {task}")

                    try:
                        if "navigate" in task.lower():
                            # Extract URL from task
                            lower_task = task.lower()
                            nav_index = lower_task.find("navigate to ")
                            if nav_index != -1:
                                url = task[nav_index + len("navigate to "):].strip()
                                print(f"Navigating to URL: {url}")
                                await session.call_tool("browser_navigate", {"url": url})
                                results.append({"response": f"Navigated to {url}"})
                            else:
                                raise ValueError(f"Could not extract URL from task: {task}")

                        elif "screenshot" in task.lower():
                            print("Taking screenshot...")
                            result = await session.call_tool("browser_screen_capture", {})

                            # Process the result
                            if result and hasattr(result, 'content') and result.content:
                                for content in result.content:
                                    if hasattr(content, 'data') and content.data:
                                        # Check if data is already a string or bytes
                                        if isinstance(content.data, str):
                                            # If it's already a string, assume it's already base64 encoded
                                            results.append({"image_base64": content.data})
                                        else:
                                            # Convert image data to base64 string
                                            encoded_image = base64.b64encode(content.data).decode('utf-8')
                                            results.append({"image_base64": encoded_image})
                                        break
                                else:
                                    # If no image data found in the expected format, try to inspect the result
                                    print(f"Screenshot result structure: {type(result)}")
                                    if hasattr(result, '__dict__'):
                                        print(f"Screenshot result attributes: {result.__dict__}")

                                    # Try to extract data from different possible formats
                                    if hasattr(result, 'data') and result.data:
                                        if isinstance(result.data, str):
                                            # If it's already a string, assume it's already base64 encoded
                                            results.append({"image_base64": result.data})
                                        else:
                                            # Convert image data to base64 string
                                            encoded_image = base64.b64encode(result.data).decode('utf-8')
                                            results.append({"image_base64": encoded_image})
                                    else:
                                        results.append({"response": f"Screenshot taken, but couldn't extract image data. Result type: {type(result)}"})
                            else:
                                results.append({"response": "Screenshot taken, but unexpected response format"})

                        else:
                            raise ValueError(f"Task not recognized: {task}")

                    except Exception as e:
                        print(f"Error executing task: {e}")
                        results.append({"error": str(e)})

        return results

    async def cleanup(self):
        """Clean up resources."""
        print("Cleaning up resources...")

        # Since we're using context managers properly now,
        # there's no need to manually clean up resources

        # Clear tools
        self._tools = {}

        print("Cleanup completed")


def create_efficient_playwright_agent() -> EfficientMCPAgent:
    """
    Create an efficient Playwright MCP agent.

    Returns:
        An EfficientMCPAgent configured for Playwright.
    """
    config = EfficientMCPConfig(
        name="efficient_playwright_agent",
        description="Efficient Playwright MCP agent using the official SDK",
        command="npx",
        args=["@playwright/mcp@latest", "--vision", "--headless"],
        tools=["browser_navigate", "browser_screen_capture"]
    )

    return EfficientMCPAgent(config)
