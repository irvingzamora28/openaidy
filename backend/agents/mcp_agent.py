"""
MCP agent implementation.

This module provides an implementation of the BaseAgent interface for MCP servers.
"""
import os
import base64
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .base import BaseAgent, AgentConfig, AgentResult

class MCPToolConfig(BaseModel):
    """Configuration for an MCP tool."""
    name: str
    description: str = ""
    arguments: Dict[str, Any] = Field(default_factory=dict)

class MCPAgentConfig(AgentConfig):
    """Configuration for an MCP agent."""
    command: str
    args: List[str]
    tools: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)

# No default configuration for MCP agent
# Each MCP server requires specific configuration

class MCPAgent(BaseAgent):
    """
    MCP agent implementation.

    This class provides an implementation of the BaseAgent interface for MCP servers.
    """

    def __init__(self, config: MCPAgentConfig):
        """
        Initialize the MCP agent with the given configuration.

        Args:
            config: The agent configuration
        """
        super().__init__(config)
        self.mcp_config = config
        self.server_params = None
        self._tools = {}

    async def initialize(self) -> AgentResult:
        """
        Initialize the agent.

        Returns:
            An AgentResult indicating success or failure
        """
        try:
            # Create server parameters
            self.server_params = StdioServerParameters(
                command=self.mcp_config.command,
                args=self.mcp_config.args,
                env=self.mcp_config.env or os.environ.copy()
            )

            # Test the connection to make sure the server is available
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # List available tools
                    tools_result = await session.list_tools()
                    available_tools = [tool.name for tool in tools_result.tools]

                    # If specific tools are requested, register only those
                    if self.mcp_config.tools:
                        for tool_name in self.mcp_config.tools:
                            if tool_name in available_tools:
                                self._tools[tool_name] = tool_name
                            else:
                                return AgentResult(
                                    success=False,
                                    error=f"Requested tool '{tool_name}' not available"
                                )
                    else:
                        # If no specific tools are requested, register all available tools
                        for tool_name in available_tools:
                            self._tools[tool_name] = tool_name
                        print(f"Automatically discovered and registered tools: {list(self._tools.keys())}")

            # Call the parent initialize method to set _initialized to True
            await super().initialize()

            # Set the initialized flag explicitly
            self._initialized = True

            return AgentResult(
                success=True,
                data=f"Initialized {self.config.name} with tools: {list(self._tools.keys())}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to initialize agent: {str(e)}"
            )

    async def run(self, task: str) -> AgentResult:
        """
        Run a task.

        Args:
            task: The task to run

        Returns:
            An AgentResult containing the result of the task
        """
        if not self._initialized:
            return AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )

        try:
            # Parse the task to identify the tool and arguments
            tool_name, args = self._parse_task(task)

            if not tool_name:
                return AgentResult(
                    success=False,
                    error=f"Could not identify tool for task: {task}"
                )

            # Use a single session for the operation
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # Call the tool
                    result = await session.call_tool(tool_name, args)

                    # Process the result
                    processed_result = self._process_result(result)

                    return AgentResult(
                        success=True,
                        data=processed_result,
                        metadata={"tool": tool_name, "args": args}
                    )

        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to run task: {str(e)}"
            )

    async def run_sequence(self, tasks: List[str]) -> List[AgentResult]:
        """
        Run a sequence of tasks.

        Args:
            tasks: The tasks to run

        Returns:
            A list of AgentResults containing the results of the tasks
        """
        if not self._initialized:
            return [AgentResult(
                success=False,
                error="Agent not initialized. Call initialize() first."
            )]

        results = []

        try:
            # Use a single session for all tasks
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    for task in tasks:
                        try:
                            # Parse the task to identify the tool and arguments
                            tool_name, args = self._parse_task(task)

                            if not tool_name:
                                results.append(AgentResult(
                                    success=False,
                                    error=f"Could not identify tool for task: {task}"
                                ))
                                continue

                            # Call the tool
                            result = await session.call_tool(tool_name, args)

                            # Process the result
                            processed_result = self._process_result(result)

                            results.append(AgentResult(
                                success=True,
                                data=processed_result,
                                metadata={"tool": tool_name, "args": args}
                            ))

                        except Exception as e:
                            results.append(AgentResult(
                                success=False,
                                error=f"Failed to run task: {str(e)}"
                            ))

        except Exception as e:
            if not results:
                results.append(AgentResult(
                    success=False,
                    error=f"Failed to run sequence: {str(e)}"
                ))

        return results

    async def cleanup(self) -> AgentResult:
        """
        Clean up resources.

        Returns:
            An AgentResult indicating success or failure
        """
        try:
            # Clear tools
            self._tools = {}

            await super().cleanup()
            return AgentResult(
                success=True,
                data=f"Cleaned up {self.config.name}"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to clean up agent: {str(e)}"
            )

    def _parse_task(self, task: str) -> tuple:
        """
        Parse a task to identify the tool and arguments.

        Args:
            task: The task to parse

        Returns:
            A tuple of (tool_name, arguments)
        """
        # This is a simple implementation that can be extended
        # for more sophisticated task parsing

        # Check for navigation tasks
        if "navigate" in task.lower():
            lower_task = task.lower()
            nav_index = lower_task.find("navigate to ")
            if nav_index != -1:
                url = task[nav_index + len("navigate to "):].strip()
                return "browser_navigate", {"url": url}

        # Check for screenshot tasks
        if "screenshot" in task.lower():
            return "browser_screen_capture", {}

        # Check for click tasks
        if "click" in task.lower():
            lower_task = task.lower()
            click_index = lower_task.find("click ")
            if click_index != -1:
                selector = task[click_index + len("click "):].strip()
                return "browser_click", {"selector": selector}

        # Check for fill tasks
        if "fill" in task.lower():
            lower_task = task.lower()
            fill_index = lower_task.find("fill ")
            if fill_index != -1:
                parts = task[fill_index + len("fill "):].strip().split(" with ")
                if len(parts) == 2:
                    selector, value = parts
                    return "browser_fill", {"selector": selector.strip(), "value": value.strip()}

        # Check for search tasks
        if "search" in task.lower():
            lower_task = task.lower()
            search_index = lower_task.find("search")
            if search_index != -1:
                # Extract the query
                query_start = search_index + len("search")
                # Skip "for" if present
                if lower_task[query_start:].strip().startswith("for"):
                    query_start += len("for")
                query = task[query_start:].strip()
                if query:
                    return "search", {"query": query}

        # Check for fetch content tasks
        if "fetch" in task.lower() and "content" in task.lower():
            lower_task = task.lower()
            fetch_index = lower_task.find("fetch content")
            if fetch_index != -1:
                # Extract the URL
                url_start = fetch_index + len("fetch content")
                # Skip "from" if present
                if lower_task[url_start:].strip().startswith("from"):
                    url_start += len("from")
                url = task[url_start:].strip()
                if url:
                    return "fetch_content", {"url": url}

        # No matching tool found
        return None, {}

    def _process_result(self, result: Any) -> Any:
        """
        Process the result from an MCP tool.

        Args:
            result: The result to process

        Returns:
            The processed result
        """
        # Check for image data
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'data') and content.data:
                    if isinstance(content.data, str):
                        # If it's already a string, assume it's already base64 encoded
                        return {"image_base64": content.data}
                    else:
                        # Convert image data to base64 string
                        encoded_image = base64.b64encode(content.data).decode('utf-8')
                        return {"image_base64": encoded_image}

            # If no image data found but we have content
            return {"content": str(result.content)}

        # If we have a data attribute
        if hasattr(result, 'data') and result.data:
            if isinstance(result.data, str):
                # If it's already a string, assume it's already base64 encoded
                return {"data": result.data}
            else:
                # Convert data to base64 string
                encoded_data = base64.b64encode(result.data).decode('utf-8')
                return {"data": encoded_data}

        # Default case
        return {"result": str(result)}
