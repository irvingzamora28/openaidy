"""
Review Analysis Orchestrator

Coordinates the workflow for Chrome Web Store review analysis using specialized agents.
Currently: structure discovery and interaction discovery.
"""
from openaidy_agents import snapshot_agent, element_discovery_agent, structure_discovery_agent, interaction_discovery_agent, review_extraction_agent, click_option_agent
import re
import json
from openaidy_agents.utils import deep_clean

class ReviewAnalysisOrchestrator:
    def __init__(self):
        pass

    async def run(self, url: str):
        """
        Run the orchestrator pipeline on the given Chrome Web Store reviews URL.
        All agents share the same MCPServerStdio session for browser state continuity.
        Returns the structure discovery, interaction discovery, and extracted reviews (all cleaned).
        """
        from agents.mcp import MCPServerStdio
        try:
            async with MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "npx",
                    "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
                },
            ) as mcp_server:
                # 0. Take initial snapshot for debugging
                initial_snapshot = await snapshot_agent.run(url, mcp_server)
                # 1. Discover elements of interest first
                element_discovery = await element_discovery_agent.run(url, ["Sort by", "Load more"], mcp_server)
                # 2. Execute interaction: click the discovered sort button and rediscover elements
                from openaidy_agents import interaction_execution_agent
                interaction_execution = await interaction_execution_agent.run(url, element_discovery, mcp_server)
                # 3. Click the 'Lowest to highest rating' option
                click_option_result = await click_option_agent.run(
                    "Lowest to highest rating", interaction_execution, mcp_server
                )
                # 4. Take a post-click snapshot for debugging
                post_click_snapshot = await snapshot_agent.run(url, mcp_server, filename="post_click_snapshot.json")
                # 5. (Optional) Continue with the rest of the pipeline
                # structure_data = await structure_discovery_agent.run(url, mcp_server)
                # interaction_data = await interaction_discovery_agent.run(url, mcp_server)
                # extracted_reviews = await review_extraction_agent.run(url, interaction_data, mcp_server)
                result = {
                    "success": True,
                    "initial_snapshot": initial_snapshot,
                    "element_discovery": element_discovery,
                    "interaction_execution": interaction_execution,
                    "click_option_result": click_option_result,
                    "post_click_snapshot": post_click_snapshot,
                    # "structure": structure_data,
                    # "interactions": interaction_data,
                    # "extracted_reviews": extracted_reviews,
                    # "sentiment": ...,
                }
                return deep_clean(result)

        except Exception as e:
            return {
                "success": False,
                "error": f"Orchestrator failed: {e}"
            }
