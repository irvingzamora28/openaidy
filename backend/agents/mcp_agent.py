"""
General purpose MCP agent that can use any MCP tools.
"""
from typing import Dict, Any, List, Optional
from .base import BaseAgentSession, AgentConfig

class MCPAgent(BaseAgentSession):
    """
    A general purpose agent that can use any MCP tools.
    This agent is more flexible than specialized agents and can be configured
    with any set of MCP tools.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the MCP agent with the given configuration.
        
        Args:
            config: The agent configuration including tools to use
        """
        super().__init__(config)
        self.available_commands = {}
    
    async def initialize(self):
        """Initialize the agent and build command registry."""
        await super().initialize()
        
        # Build a registry of available commands based on tools
        for tool_name in self._tools:
            # Convert tool names to commands (e.g., browser_navigate -> navigate)
            command = tool_name.split('_')[-1] if '_' in tool_name else tool_name
            self.available_commands[command] = tool_name
    
    async def run(self, task: str) -> Dict[str, Any]:
        """
        Run a task using available tools.
        
        Args:
            task: The task description to execute
            
        Returns:
            A dictionary containing the result
            
        Raises:
            RuntimeError: If the agent is not initialized
            ValueError: If the task cannot be parsed or executed
        """
        if not self._tools:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        # First try the specialized handlers in the base class
        try:
            return await super().run(task)
        except ValueError:
            # If the base class can't handle it, try our generic approach
            pass
        
        # Parse the task to identify the command and arguments
        parts = task.strip().split(maxsplit=1)
        if not parts:
            raise ValueError("Empty task")
        
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Check if we have a matching command
        for cmd_name, tool_name in self.available_commands.items():
            if command == cmd_name or command in cmd_name:
                print(f"Executing command '{command}' with tool '{tool_name}'")
                
                # Parse arguments based on the command
                tool_args = self._parse_args_for_tool(tool_name, args)
                
                # Execute the tool
                result = await self.mcp_session.call_tool(tool_name, tool_args)
                
                # Process and return the result
                return self._process_tool_result(tool_name, result)
        
        raise ValueError(f"Unknown command: {command}. Available commands: {list(self.available_commands.keys())}")
    
    def _parse_args_for_tool(self, tool_name: str, args_str: str) -> Dict[str, Any]:
        """
        Parse arguments for a specific tool.
        
        Args:
            tool_name: The name of the tool
            args_str: The string containing arguments
            
        Returns:
            A dictionary of arguments to pass to the tool
        """
        # This is a simple implementation - in a real system, you would
        # inspect the tool's schema and parse arguments accordingly
        
        if tool_name == "browser_navigate":
            return {"url": args_str.strip()}
        
        # For tools that don't need arguments
        return {}
    
    def _process_tool_result(self, tool_name: str, result: Any) -> Dict[str, Any]:
        """
        Process the result from a tool execution.
        
        Args:
            tool_name: The name of the tool that was executed
            result: The result from the tool execution
            
        Returns:
            A dictionary containing the processed result
        """
        # Handle image results
        if result and result.content:
            for content in result.content:
                if hasattr(content, 'data') and content.data:
                    import base64
                    # Convert image data to base64 string
                    encoded_image = base64.b64encode(content.data).decode('utf-8')
                    return {'image_base64': encoded_image}
            
            # If no special handling, return the content as a string
            return {'response': str(result.content)}
        
        # Default response
        return {'response': str(result)}


def create_playwright_agent() -> MCPAgent:
    """
    Create a pre-configured Playwright MCP agent.
    
    Returns:
        An MCPAgent configured with Playwright tools
    """
    config = AgentConfig(
        name="playwright_agent",
        description="General purpose browser automation agent using Playwright",
        mcp_tools=[
            "browser_navigate", 
            "browser_screen_capture",
            "browser_click",
            "browser_fill",
            "browser_press"
        ],
        mcp_command="npx",
        mcp_args=["@playwright/mcp@latest", "--vision", "--headless"]
    )
    
    return MCPAgent(config)
