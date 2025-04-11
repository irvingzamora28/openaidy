"""
Screenshot agent implementation using direct MCP tools.
"""
from .base import BaseAgentSession, AgentConfig


class ScreenshotAgent(BaseAgentSession):
    """Agent specialized in taking website screenshots."""

    DEFAULT_CONFIG = AgentConfig(
        name="screenshot_agent",
        description="Takes screenshots of websites using browser automation",
        mcp_tools=["browser_screen_capture", "browser_navigate"],
        mcp_command="npx",
        mcp_args=["@playwright/mcp@latest", "--vision", "--headless"]
    )

    def __init__(self, config: AgentConfig = None):
        super().__init__(config or self.DEFAULT_CONFIG)

    async def run(self, task: str) -> dict:
        """Run the screenshot task."""
        if not self._tools:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        # Pass through the original task without modification
        return await super().run(task)
