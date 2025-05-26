"""
Review Analysis Orchestrator

Coordinates the workflow for Chrome Web Store review analysis using specialized agents.
Currently: structure discovery and interaction discovery.
"""
from openaidy_agents import navigation_agent, snapshot_agent, element_discovery_agent, interaction_execution_agent, click_option_agent, review_extraction_agent
from openaidy_agents.utils import deep_clean
from agents.mcp import MCPServerStdio
import asyncio

class ReviewAnalysisOrchestrator:
    def __init__(self):
        pass

    async def run(self, url: str):
        """
        Run the orchestrator pipeline on the given Chrome Web Store reviews URL.
        All agents share the same MCPServerStdio session for browser state continuity.
        Returns the structure discovery, interaction discovery, and extracted reviews (all cleaned).
        """
        try:
            async with MCPServerStdio(
                cache_tools_list=True,
                params={
                    "command": "npx",
                    "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
                },
            ) as mcp_server:
                # Navigate to the page
                await navigation_agent.run(url, mcp_server)
                
                # 0. Take initial snapshot for debugging
                initial_snapshot = await snapshot_agent.run(url, mcp_server)
                # 1. Discover elements of interest first
                element_discovery = await element_discovery_agent.run(url, ["Sort by", "Load more"], mcp_server)
                # 2. Execute interaction: click the discovered sort button and rediscover elements
                interaction_execution = await interaction_execution_agent.run(url, element_discovery, mcp_server)
                # 3. Click the 'Lowest to highest rating' option
                click_option_result = await click_option_agent.run(
                    "Lowest to highest rating", interaction_execution, mcp_server
                )
                # 4. Take a post-click snapshot for debugging
                post_click_snapshot = await snapshot_agent.run(url, mcp_server, filename="post_click_snapshot.json")
                # 5. Extract reviews from the current page
                extracted_reviews = await review_extraction_agent.run(mcp_server)

                # 6. Paginate 'Load more' up to 10 times, always keeping only the latest extraction
                last_load_more_click_result = None
                max_load_more_clicks = 10
                for i in range(max_load_more_clicks):
                    # Discover 'Load more' button
                    # Add a time delay of 10 seconds
                    await asyncio.sleep(10)
                    element_discovery = await element_discovery_agent.run(url, ["Load more"], mcp_server)
                    if "Load more" not in element_discovery:
                        break
                    # Click 'Load more'
                    # Add a time delay of 10 seconds
                    await asyncio.sleep(10)
                    last_load_more_click_result = await click_option_agent.run(
                        "Load more", element_discovery, mcp_server
                    )
                # Extract reviews after loading more (overwrite each time)
                extracted_reviews = await review_extraction_agent.run(mcp_server)

                result = {
                    "success": True,
                    "initial_snapshot": initial_snapshot,
                    "element_discovery": element_discovery,
                    "interaction_execution": interaction_execution,
                    "click_option_result": click_option_result,
                    "post_click_snapshot": post_click_snapshot,
                    "extracted_reviews": extracted_reviews,
                    "last_load_more_click_result": last_load_more_click_result,
                }
                return deep_clean(result)

        except Exception as e:
            return {
                "success": False,
                "error": f"Orchestrator failed: {e}"
            }
