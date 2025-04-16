"""
LangChain agent implementation.

This module provides an implementation of the BaseAgent interface using LangChain.
"""
import os
import base64
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable, Type
from pathlib import Path
from pydantic import BaseModel, Field

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent, create_openai_functions_agent
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool, Tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Local imports
from .base import BaseAgent, AgentConfig, AgentResult

class LangChainToolConfig(BaseModel):
    """Configuration for a LangChain tool."""
    name: str
    description: str = ""
    function: Optional[Callable] = None
    args_schema: Optional[Dict[str, Any]] = None
    return_direct: bool = False
    coroutine: Optional[Callable] = None

class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    transport: str = "stdio"
    env: Dict[str, str] = Field(default_factory=dict)
    tools: List[str] = Field(default_factory=list)
    screenshots_dir: Optional[str] = "screenshots"


class BrowserNavigateTool(BaseTool):
    """Tool for navigating to a URL in a browser."""

    name: str = "browser_navigate"
    description: str = "Navigate to a URL in the browser. Input should be a URL."
    session: ClientSession = None

    def __init__(self, session: ClientSession):
        """Initialize the tool with an MCP session."""
        super().__init__()
        self._session = session

    def _run(self, url: str) -> str:
        """This method is not used as we're using the async version."""
        raise NotImplementedError("Use _arun instead")

    async def _arun(self, url: str) -> str:
        """Navigate to a URL in the browser."""
        try:
            await self._session.call_tool("browser_navigate", {"url": url})
            # Wait for the page to load
            await asyncio.sleep(2)
            return f"Successfully navigated to {url}"
        except Exception as e:
            return f"Error navigating to {url}: {str(e)}"


class BrowserScreenshotTool(BaseTool):
    """Tool for taking a screenshot of the current browser page."""

    name: str = "browser_screenshot"  # This should match the tool name in the configuration
    description: str = "Take a screenshot of the current browser page. No input is needed."
    session: ClientSession = None
    screenshots_dir: Path = None
    screenshot_count: int = 0

    def __init__(self, session: ClientSession, screenshots_dir: Path):
        """Initialize the tool with an MCP session and screenshots directory."""
        super().__init__()
        self._session = session
        self._screenshots_dir = screenshots_dir
        self._screenshot_count = 0

    def _run(self, _: Optional[str] = None) -> str:
        """This method is not used as we're using the async version."""
        raise NotImplementedError("Use _arun instead")

    async def _arun(self, _: Optional[str] = None) -> str:
        """Take a screenshot of the current browser page."""
        try:
            # Take a screenshot
            screenshot_result = await self._session.call_tool("browser_screen_capture", {"format": "jpeg"})

            # Process the screenshot result
            screenshot_data = None

            # Check if the result has content attribute
            if hasattr(screenshot_result, "content") and screenshot_result.content:
                for item in screenshot_result.content:
                    if hasattr(item, "data") and item.data:
                        if isinstance(item.data, bytes):
                            screenshot_data = item.data
                        elif isinstance(item.data, str):
                            # Convert string to bytes if it's base64
                            screenshot_data = base64.b64decode(item.data)
                        break

            # Save the screenshot
            if screenshot_data:
                self._screenshot_count += 1
                screenshot_path = self._screenshots_dir / f"langchain_screenshot_{self._screenshot_count}.png"
                with open(screenshot_path, "wb") as f:
                    # Write the screenshot data directly (it's already bytes)
                    f.write(screenshot_data)

                # Don't include the base64 data in the response as it can be very large
                # and cause issues with the agent
                return f"Screenshot saved to {screenshot_path}."
            else:
                return "No screenshot data found in the result."
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"


class FetchTool(BaseTool):
    """Tool for fetching a URL and extracting its contents as markdown."""

    name: str = "fetch"
    description: str = "Fetch a URL and extract its contents as markdown. Input should be a URL."
    session: ClientSession = None
    return_direct: bool = False

    def __init__(self, session: ClientSession):
        """Initialize the tool with an MCP session."""
        super().__init__()
        self._session = session

    def _run(self, url: str) -> str:
        """This method is not used as we're using the async version."""
        raise NotImplementedError("Use _arun instead")

    async def _arun(self, url: str) -> str:
        """Fetch a URL and extract its contents as markdown."""
        try:
            # Parse the input to handle cases where additional parameters are provided
            params = {"url": url, "max_length": 5000}

            # Check if start_index is specified in the input
            if "start_index:" in url:
                parts = url.split("start_index:")
                url = parts[0].strip()
                try:
                    start_index = int(parts[1].strip())
                    params["url"] = url
                    params["start_index"] = start_index
                except ValueError:
                    # If start_index is not a valid integer, ignore it
                    pass

            # Fetch the URL
            result = await self._session.call_tool("fetch", params)

            # Process the result
            content = ""

            # Check if the result has content attribute
            if hasattr(result, "content") and result.content:
                for item in result.content:
                    if hasattr(item, "text") and item.text:
                        content = item.text
                        break

            # If no content was found in the content attribute, check other attributes
            if not content and hasattr(result, "text") and result.text:
                content = result.text
            elif not content and isinstance(result, str):
                content = result

            # If still no content, return a message
            if not content:
                content = str(result)
                if len(content) < 100:
                    content = f"Successfully fetched {url}, but no content was found. Raw result: {content}"

            return content
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

class LangChainAgentConfig(AgentConfig):
    """Configuration for a LangChain agent."""
    # LLM configuration
    model_name: str = os.environ.get("LLM_MODEL", "gpt-4o")
    api_key: Optional[str] = os.environ.get("LLM_API_KEY")
    api_base: Optional[str] = os.environ.get("LLM_API_URL")
    temperature: float = 0.2
    max_tokens: int = 1000

    # Agent configuration
    agent_type: str = "react"  # "react" or "openai_functions"
    system_message: str = "You are a helpful assistant that can use tools to accomplish tasks."

    # Tool configuration
    tools: List[Union[LangChainToolConfig, Dict[str, Any]]] = Field(default_factory=list)

    # MCP configuration
    # Note: Due to implementation limitations, each task can only use tools from one MCP server.
    # The server is selected based on keywords in the task description.
    mcp_servers: Dict[str, MCPServerConfig] = Field(default_factory=dict)

    # Additional configuration
    verbose: bool = False
    handle_parsing_errors: bool = True
    max_iterations: int = 10

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

class LangChainAgent(BaseAgent):
    """
    LangChain agent implementation.

    This class provides an implementation of the BaseAgent interface using LangChain.
    """

    def __init__(self, config: LangChainAgentConfig):
        """
        Initialize the LangChain agent with the given configuration.

        Args:
            config: The agent configuration
        """
        super().__init__(config)
        self.langchain_config = config
        self._llm = None
        self._tools = []
        self._agent_executor = None
        self._mcp_client = None
        self._chat_history = []

    async def initialize(self) -> AgentResult:
        """
        Initialize the agent.

        Returns:
            An AgentResult indicating success or failure
        """
        try:
            # Initialize the LLM
            self._llm = self._create_llm()

            # Initialize tools
            self._tools = await self._create_tools()

            # Create the agent
            agent = self._create_agent(self._tools)

            # Create the agent executor
            self._agent_executor = AgentExecutor(
                agent=agent,
                tools=self._tools,
                verbose=self.langchain_config.verbose,
                handle_parsing_errors=self.langchain_config.handle_parsing_errors,
                max_iterations=self.langchain_config.max_iterations
            )

            # Call the parent initialize method to set _initialized to True
            await super().initialize()

            return AgentResult(
                success=True,
                data=f"Initialized {self.config.name} with {len(self._tools)} tools"
            )

        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to initialize agent: {str(e)}"
            )

    async def run(self, task: str) -> AgentResult:
        """
        Run a task.

        Note: Due to implementation limitations, each task can only use tools from one MCP server.
        The server is selected based on keywords in the task description.
        For example, if the task contains "fetch", the fetch MCP server will be used.
        If the task contains "browser", "navigate", or "screenshot", the playwright MCP server will be used.

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
            # Check if we need to use MCP tools
            if self.langchain_config.mcp_servers:
                # Determine which MCP server to use based on the task content
                # This is a simple heuristic - in a real implementation, you might want to use a more sophisticated approach
                server_priority = {}

                # Check for keywords in the task to determine which server to use
                if "fetch" in task.lower():
                    server_priority["fetch"] = 10
                if any(keyword in task.lower() for keyword in ["browser", "navigate", "screenshot", "screen_capture"]):
                    server_priority["playwright"] = 10

                # Sort servers by priority (highest first)
                sorted_servers = sorted(
                    self.langchain_config.mcp_servers.items(),
                    key=lambda x: server_priority.get(x[0], 0),
                    reverse=True
                )

                # Process each MCP server in priority order
                for server_name, server_config in sorted_servers:
                    print(f"\nUsing MCP server: {server_name} (priority: {server_priority.get(server_name, 0)})")
                    # Create server parameters
                    server_params = StdioServerParameters(
                        command=server_config.command,
                        args=server_config.args,
                        env=server_config.env or os.environ.copy()
                    )

                    # Create screenshots directory if needed
                    screenshots_dir = Path(server_config.screenshots_dir)
                    screenshots_dir.mkdir(exist_ok=True)

                    # Connect to the MCP server
                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            # Initialize the connection
                            await session.initialize()

                            # Create tools based on the server configuration
                            server_tools = []

                            # Create the appropriate tools based on the server type and tools list
                            if server_name == "playwright":
                                if "browser_navigate" in server_config.tools:
                                    browser_navigate_tool = BrowserNavigateTool(session)
                                    server_tools.append(browser_navigate_tool)
                                    print(f"Added MCP tool: browser_navigate")

                                if "browser_screen_capture" in server_config.tools:
                                    browser_screenshot_tool = BrowserScreenshotTool(session, screenshots_dir)
                                    server_tools.append(browser_screenshot_tool)
                                    print(f"Added MCP tool: browser_screen_capture")

                            elif server_name == "fetch":
                                if "fetch" in server_config.tools:
                                    fetch_tool = FetchTool(session)
                                    server_tools.append(fetch_tool)
                                    print(f"Added MCP tool: fetch")

                            # Combine with existing tools
                            all_tools = self._tools + server_tools

                            # Print the available tools for debugging
                            print(f"Available tools: {[tool.name for tool in all_tools]}")

                            # Create a new agent with all tools
                            agent = self._create_agent(all_tools)

                            # Create a new agent executor
                            agent_executor = AgentExecutor(
                                agent=agent,
                                tools=all_tools,
                                verbose=self.langchain_config.verbose,
                                handle_parsing_errors=self.langchain_config.handle_parsing_errors,
                                max_iterations=self.langchain_config.max_iterations
                            )

                            # Run the agent
                            result = await agent_executor.ainvoke({
                                "input": task,
                                "chat_history": self._chat_history
                            })

                            # Close the browser if it was used
                            try:
                                if server_name == "playwright":
                                    await session.call_tool("browser_close")
                            except Exception:
                                # Ignore errors when closing the browser
                                pass

                            # Return the result after the first successful execution
                            # This means we're only using one MCP server per task
                            # In a more advanced implementation, we could combine tools from multiple servers
                            return AgentResult(
                                success=True,
                                data=result["output"],
                                metadata={"intermediate_steps": result.get("intermediate_steps", [])}
                            )
            else:
                # Run the agent with existing tools
                result = await self._agent_executor.ainvoke({
                    "input": task,
                    "chat_history": self._chat_history
                })

            # Update chat history
            self._chat_history.append(HumanMessage(content=task))
            self._chat_history.append(AIMessage(content=result["output"]))

            return AgentResult(
                success=True,
                data=result["output"],
                metadata={"intermediate_steps": result.get("intermediate_steps", [])}
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

        for task in tasks:
            result = await self.run(task)
            results.append(result)

        return results

    async def cleanup(self) -> AgentResult:
        """
        Clean up resources.

        Returns:
            An AgentResult indicating success or failure
        """
        try:
            # We don't need to clean up MCP client as it's used as a context manager

            # Clear tools and agent executor
            self._tools = []
            self._agent_executor = None
            self._chat_history = []

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

    def _create_llm(self) -> BaseLanguageModel:
        """
        Create the LLM for the agent.

        Returns:
            A LangChain language model
        """
        # Create the LLM
        return ChatOpenAI(
            model=self.langchain_config.model_name,
            temperature=self.langchain_config.temperature,
            max_tokens=self.langchain_config.max_tokens,
            api_key=self.langchain_config.api_key,
            base_url=self.langchain_config.api_base
        )

    async def _create_tools(self) -> List[BaseTool]:
        """
        Create the tools for the agent.

        Returns:
            A list of LangChain tools
        """
        tools = []

        # Create custom tools
        for tool_config in self.langchain_config.tools:
            if isinstance(tool_config, dict):
                tool_config = LangChainToolConfig(**tool_config)

            # Create a LangChain tool from the configuration
            if tool_config.function:
                # Use the Tool class instead of BaseTool
                tool = Tool(
                    name=tool_config.name,
                    description=tool_config.description,
                    func=tool_config.function,
                    coroutine=tool_config.coroutine,
                    return_direct=tool_config.return_direct
                )
                tools.append(tool)

        # We'll handle MCP tools separately since they require a context manager
        # The actual MCP tools will be created when the agent is run

        return tools

    def _create_agent(self, tools):
        """
        Create the LangChain agent.

        Args:
            tools: The tools to use with the agent

        Returns:
            A LangChain agent
        """
        if self.langchain_config.agent_type == "react":
            # Create a ReAct agent
            template = f"""
            {self.langchain_config.system_message}

            You have access to the following tools:

            {{tools}}

            Use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do
            Action: the action to take, should be one of {{tool_names}}
            Action Input: the input to the action
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Begin!

            Question: {{input}}
            {{agent_scratchpad}}
            """

            prompt = PromptTemplate.from_template(template)

            return create_react_agent(
                llm=self._llm,
                tools=tools,
                prompt=prompt
            )

        elif self.langchain_config.agent_type == "openai_functions":
            # Create an OpenAI functions agent
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.langchain_config.system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            return create_openai_functions_agent(
                llm=self._llm,
                tools=tools,
                prompt=prompt
            )

        else:
            raise ValueError(f"Unknown agent type: {self.langchain_config.agent_type}")


