"""
Agent package for MCP-based agents.
"""
from .base import BaseAgentSession, AgentConfig
from .screenshot import ScreenshotAgent
from .mcp_agent import MCPAgent, create_playwright_agent
from .factory import create_agent, AGENT_REGISTRY

# Add the MCPAgent to the registry
AGENT_REGISTRY["mcp"] = MCPAgent
AGENT_REGISTRY["playwright"] = create_playwright_agent

__all__ = [
    'BaseAgentSession',
    'AgentConfig',
    'ScreenshotAgent',
    'MCPAgent',
    'create_agent',
    'create_playwright_agent',
]
