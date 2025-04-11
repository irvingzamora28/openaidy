"""
Agent factory.

This module provides a factory for creating agents.
"""
from typing import Dict, Any, Type, Optional, Union

from .base import BaseAgent, AgentConfig, SimpleAgent
from .mcp_agent import MCPAgent, MCPAgentConfig

# Registry of agent types
AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "simple": SimpleAgent,
    "mcp": MCPAgent
}

def register_agent(name: str, agent_class: Type[BaseAgent]) -> None:
    """
    Register an agent type.

    Args:
        name: The name of the agent type
        agent_class: The agent class
    """
    AGENT_REGISTRY[name] = agent_class

def create_agent(
    agent_type: str,
    config: Optional[Union[Dict[str, Any], AgentConfig]] = None
) -> BaseAgent:
    """
    Create an agent of the specified type.

    Args:
        agent_type: The type of agent to create
        config: The agent configuration

    Returns:
        An agent of the specified type

    Raises:
        ValueError: If the agent type is not registered
    """
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}")

    agent_class = AGENT_REGISTRY[agent_type]

    # No factory functions in the registry anymore

    # Create the appropriate configuration
    if config is None:
        if agent_class == SimpleAgent:
            config = AgentConfig(name=f"{agent_type}_agent")
        elif agent_class == MCPAgent:
            # For MCPAgent, we require explicit configuration
            raise ValueError("MCPAgent requires explicit configuration. Please provide command and args.")

        else:
            raise ValueError(f"No default configuration for agent type: {agent_type}")
    elif isinstance(config, dict):
        if agent_class == SimpleAgent:
            config = AgentConfig(**config)
        elif agent_class == MCPAgent:
            config = MCPAgentConfig(**config)
        else:
            raise ValueError(f"No configuration class for agent type: {agent_type}")

    return agent_class(config)
