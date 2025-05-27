import asyncio
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openaidy_agents import playwright_navigation_agent, playwright_snapshot_agent, element_discovery_agent, playwright_click_agent, review_extraction_agent, review_analysis_agent
import json

async def run_orchestrator(url, snapshot_filename="snapshot.json"):
    """
    Orchestrates navigation, snapshot, and element discovery using custom low-level MCP functions and LLM agent chunking.
    1. Starts MCP server.
    2. Navigates to the URL.
    3. Takes a snapshot and saves it to a file.
    4. Loads the snapshot and discovers elements in chunks.
    """
    server_params = StdioServerParameters(
        command="bunx",
        args=["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as mcp_server:
            await mcp_server.initialize()
            # Step 1: Navigate using custom tool
            nav_result = await playwright_navigation_agent.navigate_with_mcp(url, mcp_server)
            print(f"Navigation result: {nav_result}")
            # Step 2: Snapshot using custom tool
            snap_result = await playwright_snapshot_agent.snapshot_with_mcp(mcp_server, filename=snapshot_filename)
            print(f"Snapshot saved to {snapshot_filename}")

            # Step 3: Run element discovery on the in-memory snapshot (snap_result)
            labels = ["Sort by", "Load more"]
            element_discovery = await element_discovery_agent.discover_elements_from_snapshot(snap_result, labels)
            print(f"Element discovery result: {element_discovery}")

            # Step 4: Click on 'Sort by' if found
            click_result = None
            if "Sort by" in element_discovery:
                # element_discovery["Sort by"] is a string ref, not a dict
                ref = element_discovery["Sort by"]
                click_result = await playwright_click_agent.click_with_mcp(
                    "Sort by", ref, mcp_server
                )
                print(f"Click result: {click_result}")
            else:
                print("'Sort by' element not found, skipping click.")
                
            # Step 5: Snapshot using custom tool
            snap_result = await playwright_snapshot_agent.snapshot_with_mcp(mcp_server, filename="post_click_snapshot.json")
            print(f"Snapshot saved to post_click_snapshot.json")
            
            # Step 6: Discover elements in the post-click snapshot
            labels = ["Lowest to highest rating"]
            post_click_element_discovery = await element_discovery_agent.discover_elements_from_snapshot(snap_result, labels)
            print(f"Post-click element discovery result: {post_click_element_discovery}")
            
            # Step 7: Click on the 'Lowest to highest rating' option
            ref = post_click_element_discovery["Lowest to highest rating"]
            if not ref:
                print("'Lowest to highest rating' element not found, skipping click.")
                return
            click_result = await playwright_click_agent.click_with_mcp(
                "Lowest to highest rating", ref, mcp_server
            )
            print(f"Click result: {click_result}")
            
            # Step 8: Take a post-click snapshot for debugging
            post_click_snapshot = await playwright_snapshot_agent.snapshot_with_mcp(mcp_server, filename="post_click_snapshot.json")
            print(f"Snapshot saved to post_click_snapshot.json")

            # Step 9: Paginate 'Load more' up to 10 times
            import asyncio
            max_load_more_clicks = 10
            load_more_click_results = []
            load_more_snapshots = []

            # Use the first 'Load more' from initial element_discovery (raise if not found)
            try:
                load_more_ref = element_discovery["Load more"]
            except KeyError:
                print("'Load more' element not found in initial element_discovery, skipping pagination.")
                load_more_ref = None
            iteration = 0
            while load_more_ref and iteration < max_load_more_clicks:
                print(f"[Pagination] Iteration {iteration+1}: Clicking 'Load more' (ref={load_more_ref})")
                click_result = await playwright_click_agent.click_with_mcp("Load more", load_more_ref, mcp_server)
                load_more_click_results.append(click_result)
                await asyncio.sleep(5)  # Wait for content to load
                # Take snapshot after click
                snapshot = await playwright_snapshot_agent.snapshot_with_mcp(mcp_server, filename=f"load_more_snapshot_{iteration+1}.json")
                load_more_snapshots.append(snapshot)
                # Discover 'Load more' in the new snapshot
                labels = ["Load more"]
                discovery = await element_discovery_agent.discover_elements_from_snapshot(snapshot, labels, reverse=True)
                load_more_ref = discovery["Load more"] if "Load more" in discovery else None
                iteration += 1
                if not load_more_ref:
                    print(f"[Pagination] 'Load more' not found after {iteration} iterations. Stopping.")
                    break
            print(f"[Pagination] Completed {iteration} iterations or reached end of 'Load more'.")
            
            # Step 10: Take a last snapshot for debugging
            last_snapshot = await playwright_snapshot_agent.snapshot_with_mcp(mcp_server, filename="last_snapshot.json")
            print(f"Snapshot saved to last_snapshot.json")

            # Step 11: Extract reviews from the last snapshot
            extracted_reviews = await review_extraction_agent.extract_reviews_from_snapshot(last_snapshot)
            print(f"Extracted {len(extracted_reviews)} reviews.")
            if extracted_reviews:
                print("First review:", json.dumps(extracted_reviews[0], indent=2, ensure_ascii=False))
            with open("extracted_reviews_chatgpt_summarize.json", "w", encoding="utf-8") as f:
                json.dump(extracted_reviews, f, indent=2, ensure_ascii=False)
                
            # Step 12: Analyze reviews
            review_analysis = await review_analysis_agent.analyze_reviews_in_chunks(extracted_reviews, output_file="review_analysis_chatgpt_summarize.json")
            print(f"Review analysis result: {review_analysis}")

            return {
                "navigation_result": nav_result,
                "snapshot_result": snap_result,
                "element_discovery": element_discovery,
                "click_result": click_result,
                "post_click_snapshot": post_click_snapshot,
                "load_more_click_results": load_more_click_results,
                "load_more_snapshots": load_more_snapshots,
                "extracted_reviews": extracted_reviews,
                "review_analysis": review_analysis,
                # Add further results as needed
            }

def orchestrate_reviews_pipeline(url, snapshot_filename="snapshot.json"):
    """
    Run the full review extraction and analysis pipeline for a given URL.
    Args:
        url (str): Target reviews page URL.
        snapshot_filename (str): Filename for saving the main snapshot (default: 'snapshot.json').
    Returns:
        dict: Results from the pipeline, including extracted reviews and analysis.
    """
    return asyncio.run(run_orchestrator(url, snapshot_filename=snapshot_filename))

def main():
    import sys
    url = None
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Default URL (can be changed)
        url = "https://chromewebstore.google.com/detail/chatgpt-summarize/cbgecfllfhmmnknmamkejadjmnmpfjmp/reviews"
    if not shutil.which("bunx"):
        raise RuntimeError("bunx is not installed. Please install Node.js and bunx.")
    result = orchestrate_reviews_pipeline(url)
    print(result)

if __name__ == "__main__":
    main()