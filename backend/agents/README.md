# Agent Architecture

This package provides a scalable and maintainable architecture for creating agents that can interact with various tools and services, including MCP servers and custom tools.

## Architecture Overview

The agent architecture is designed to be:

1. **Scalable**: Easily add new agent types with different capabilities
2. **Maintainable**: Clear separation of concerns and well-defined interfaces
3. **Extensible**: Support for both MCP tools and custom tools
4. **Performant**: Efficient implementation with proper resource management
5. **Configurable**: Flexible configuration for different agent types

## Core Components

### BaseAgent

The `BaseAgent` class is the foundation of our agent architecture:

- Defines the common interface for all agents
- Provides basic lifecycle management (initialize, run, cleanup)
- Implements common utility methods

### MCPAgent

The `MCPAgent` class extends `BaseAgent` to provide MCP-specific functionality:

- Manages MCP session lifecycle
- Implements proper context management for optimal performance
- Supports running sequences of operations in a single session
- Handles different response formats
- Automatically discovers available tools

### Specialized Agents

Instead of creating specialized agent classes, we use the `MCPAgent` with appropriate configuration:

- **Browser Automation**: Use `MCPAgent` with Playwright MCP configuration
- **Web Search**: Use `MCPAgent` with DuckDuckGo MCP configuration
- **Custom Tools**: Use `MCPAgent` with custom MCP server configuration

### AgentFactory

The `create_agent` function provides a factory pattern for creating agents:

- Creates agents based on configuration
- Manages agent registration and discovery
- Supports dependency injection for testing

## Usage

### Creating an MCP Agent

```python
from backend.agents import create_agent, MCPAgentConfig

# Create a Playwright MCP agent
playwright_config = MCPAgentConfig(
    name="playwright_agent",
    description="Playwright browser automation agent",
    command="npx",
    args=["@playwright/mcp@latest", "--vision", "--headless"],
    tools=["browser_navigate", "browser_screen_capture"]
)

playwright_agent = create_agent("mcp", playwright_config)

# Initialize the agent
await playwright_agent.initialize()

# Run a task
result = await playwright_agent.run("Navigate to https://example.com")

# Run a sequence of tasks
results = await playwright_agent.run_sequence([
    "Navigate to https://example.com",
    "Take a screenshot"
])

# Clean up
await playwright_agent.cleanup()
```

### Creating a DuckDuckGo MCP Agent

```python
from backend.agents import create_agent, MCPAgentConfig

# Create a DuckDuckGo MCP agent
duckduckgo_config = MCPAgentConfig(
    name="duckduckgo_agent",
    description="DuckDuckGo search agent",
    command="uvx",
    args=["duckduckgo-mcp-server"],
    tools=["search", "fetch_content"]
)

duckduckgo_agent = create_agent("mcp", duckduckgo_config)

# Initialize the agent
await duckduckgo_agent.initialize()

# Run a search
result = await duckduckgo_agent.run("search How to use MCP")

# Clean up
await duckduckgo_agent.cleanup()
```

### Creating a Custom Agent

```python
from backend.agents import BaseAgent, AgentResult, register_agent

class MyCustomAgent(BaseAgent):
    """A custom agent implementation."""

    async def initialize(self):
        """Initialize the agent."""
        # Custom initialization
        return AgentResult(success=True, data="Initialized custom agent")

    async def run(self, task):
        """Run a task."""
        # Custom task execution
        return AgentResult(success=True, data=f"Executed task: {task}")

    async def run_sequence(self, tasks):
        """Run a sequence of tasks."""
        # Custom sequence execution
        return [AgentResult(success=True, data=f"Executed task: {task}") for task in tasks]

    async def cleanup(self):
        """Clean up resources."""
        # Custom cleanup
        return AgentResult(success=True, data="Cleaned up custom agent")

# Register the agent
register_agent("my_custom", MyCustomAgent)
```

## Best Practices

1. **Use Context Managers**: Always use context managers for MCP sessions
2. **Reuse Sessions**: Run sequences of operations in a single session
3. **Proper Error Handling**: Handle different response formats and errors
4. **Resource Cleanup**: Always clean up resources when done
5. **Tool Discovery**: Use automatic tool discovery when possible

## Performance Considerations

For optimal performance with MCP servers:

1. **Context Management**: Use context managers properly
2. **Session Reuse**: Reuse sessions for multiple operations
3. **Proper Initialization**: Initialize sessions correctly
4. **Error Handling**: Handle errors gracefully
5. **Resource Management**: Clean up resources properly
