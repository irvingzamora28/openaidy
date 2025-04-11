"""
Agent package for MCP-based agents.
"""
from .base import BaseAgentSession, AgentConfig
from .screenshot import ScreenshotAgent
from .mcp_agent import MCPAgent, create_playwright_agent
from .efficient_mcp import EfficientMCPAgent, create_efficient_playwright_agent, EfficientMCPConfig
from .factory import create_agent, AGENT_REGISTRY

# Add the agents to the registry
AGENT_REGISTRY["mcp"] = MCPAgent
AGENT_REGISTRY["playwright"] = create_efficient_playwright_agent  # Use the efficient implementation by default
AGENT_REGISTRY["legacy_playwright"] = create_playwright_agent  # Keep the legacy implementation for reference
AGENT_REGISTRY["efficient_playwright"] = create_efficient_playwright_agent

__all__ = [
    'BaseAgentSession',
    'AgentConfig',
    'ScreenshotAgent',
    'MCPAgent',
    'EfficientMCPAgent',
    'EfficientMCPConfig',
    'create_agent',
    'create_playwright_agent',
    'create_efficient_playwright_agent',
]
