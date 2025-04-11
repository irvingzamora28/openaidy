# MCP Agents Architecture (Proof of Concept)

This package provides a proof of concept for a scalable architecture that enables creating agents using the Model Context Protocol (MCP). These agents can interact with various tools and services, and will ultimately be integrated with LLMs and frontend components.

## Architecture Overview

This proof of concept demonstrates an agent architecture designed to be:

1. **Scalable**: Easily add new agent types with different capabilities
2. **Flexible**: Support multiple MCP servers and tool sets
3. **Extensible**: Allow for custom tool handling and result processing
4. **Modular**: Separate agent types for different use cases
5. **Integrable**: Designed to work with LLMs and frontend components

### Vision

The ultimate vision for this architecture is to create a system where:

1. **LLM Integration**: LLMs will be able to use these agents as tools to perform actions
2. **Frontend Interaction**: Users will interact with agents through a web frontend
3. **Custom Tools**: The system can be extended with custom tools beyond the built-in MCP capabilities
4. **Multiple Providers**: Support for various LLM providers (OpenAI, Google, etc.) and MCP servers

## Core Components

### BaseAgentSession

The `BaseAgentSession` class provides the foundation for all agents:

- Manages MCP session lifecycle (initialization, execution, cleanup)
- Handles tool discovery and registration
- Provides basic task parsing and execution
- Implements error handling and resource management

### AgentConfig

The `AgentConfig` class defines the configuration for an agent:

- Agent metadata (name, description)
- MCP tools to use
- MCP server configuration (command, arguments)

### Specialized Agents

Specialized agents extend the base agent with specific capabilities:

- **ScreenshotAgent**: Focused on browser screenshots and navigation
- **MCPAgent**: General-purpose agent that can use any MCP tools

### Agent Factory

The `create_agent` function provides a factory pattern for creating agents:

```python
from backend.agents import create_agent

# Create a screenshot agent
screenshot_agent = create_agent("screenshot")

# Create a Playwright agent
playwright_agent = create_agent("playwright")
```

## Adding New Agent Types

To add a new agent type:

1. Create a new class that extends `BaseAgentSession`
2. Implement specialized task handling in the `run` method
3. Register the agent in `factory.py` and `__init__.py`

Example:

```python
from .base import BaseAgentSession, AgentConfig

class MyCustomAgent(BaseAgentSession):
    DEFAULT_CONFIG = AgentConfig(
        name="custom_agent",
        description="My custom agent",
        mcp_tools=["tool1", "tool2"],
        mcp_command="npx",
        mcp_args=["@my-package/mcp"]
    )

    def __init__(self, config: AgentConfig = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    async def run(self, task: str) -> dict:
        # Custom task handling
        # ...

        # Fall back to base implementation for standard tasks
        return await super().run(task)
```

Then register it in `factory.py`:

```python
from .custom_agent import MyCustomAgent

AGENT_REGISTRY["custom"] = MyCustomAgent
```

## Usage Examples

See the `examples` directory for usage examples:

- `take_screenshot.py`: Using the ScreenshotAgent
- `playwright_agent.py`: Using the general-purpose Playwright agent

## Performance Considerations

During testing, we identified some performance limitations with the MCP Python library approach:

- **Timeouts**: Operations like screenshot capture may time out but still complete in the background
- **Latency**: The MCP library adds some overhead compared to direct JSON-RPC communication
- **Resource Management**: Proper cleanup is essential to prevent resource leaks

In a production implementation, we may need to consider:

1. **Hybrid Approach**: Using direct JSON-RPC for performance-critical operations
2. **Optimized Communication**: Reducing unnecessary abstraction layers
3. **Better Error Recovery**: Implementing more sophisticated error recovery mechanisms

## Next Steps

This proof of concept validates the approach, but several steps remain for a production implementation:

1. **LLM Integration**: Connect these agents to our LLM pipeline
2. **Frontend Components**: Create UI components for interacting with agents
3. **API Endpoints**: Develop RESTful APIs for agent operations
4. **Authentication**: Add proper authentication and authorization
5. **Monitoring**: Implement logging and monitoring for agent operations
6. **Testing**: Comprehensive testing of the entire system
