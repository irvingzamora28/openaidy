"""
Agent package.

This package provides a scalable and maintainable architecture for creating agents
that can interact with various tools and services, including MCP servers and custom tools.
"""
from .base import BaseAgent, AgentConfig, AgentResult, SimpleAgent
from .mcp_agent import MCPAgent, MCPAgentConfig, MCPToolConfig
from .langchain_agent import LangChainAgent, LangChainAgentConfig, LangChainToolConfig, MCPServerConfig
from .factory import create_agent, register_agent, AGENT_REGISTRY

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentConfig',
    'AgentResult',
    'SimpleAgent',

    # MCP classes
    'MCPAgent',
    'MCPAgentConfig',
    'MCPToolConfig',

    # LangChain classes
    'LangChainAgent',
    'LangChainAgentConfig',
    'LangChainToolConfig',
    'MCPServerConfig',

    # No browser-specific classes - use MCPAgent with appropriate configuration

    # Factory functions
    'create_agent',
    'register_agent',
    'AGENT_REGISTRY'
]
