"""
Agent factory for creating different types of agents.
"""
from typing import Dict, Type, Optional
from .base import BaseAgentSession, AgentConfig
from .screenshot import ScreenshotAgent

# Registry of available agent types
AGENT_REGISTRY: Dict[str, Type[BaseAgentSession]] = {
    "screenshot": ScreenshotAgent,
}

def create_agent(agent_type: str, config: Optional[AgentConfig] = None) -> BaseAgentSession:
    """
    Create an agent of the specified type.
    
    Args:
        agent_type: The type of agent to create (e.g., "screenshot")
        config: Optional custom configuration for the agent
        
    Returns:
        An instance of the requested agent
        
    Raises:
        ValueError: If the agent type is not supported
    """
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {list(AGENT_REGISTRY.keys())}")
    
    agent_class = AGENT_REGISTRY[agent_type]
    return agent_class(config)
