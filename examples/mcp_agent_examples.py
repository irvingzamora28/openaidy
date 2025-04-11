"""
Examples of creating MCP agents with different configurations.

This example demonstrates how to create MCP agents for different MCP servers.
"""
import asyncio
import sys
import time
from dotenv import load_dotenv
from backend.agents import create_agent, MCPAgentConfig

async def main():
    """Run the MCP agent examples."""
    # Load environment variables from .env
    load_dotenv()

    # Example 1: Create a Playwright MCP agent
    print("=== Example 1: Playwright MCP Agent ===")
    playwright_config = MCPAgentConfig(
        name="playwright_agent",
        description="Playwright browser automation agent",
        command="npx",
        args=["@playwright/mcp@latest", "--vision", "--headless"],
        tools=["browser_navigate", "browser_screen_capture"]
    )

    # Create the agent using the factory
    playwright_agent = create_agent("mcp", playwright_config)

    # Initialize and use the agent
    try:
        print("Initializing Playwright agent...")
        result = await playwright_agent.initialize()
        print(f"Initialization result: {result.data}")

        if result.success:
            print("Taking screenshot of GitHub...")
            results = await playwright_agent.run_sequence([
                "Navigate to https://github.com",
                "Take a screenshot"
            ])

            for i, result in enumerate(results):
                print(f"Result {i+1}: {'Success' if result.success else 'Failure'}")
                if result.success and isinstance(result.data, dict) and 'image_base64' in result.data:
                    print(f"Screenshot base64 preview: {result.data['image_base64'][:50]}...")

        await playwright_agent.cleanup()
        print("Playwright agent cleaned up")
    except Exception as e:
        print(f"Error with Playwright agent: {e}")
        await playwright_agent.cleanup()

    print()

    # Example 2: Create a DuckDuckGo MCP agent
    print("=== Example 2: DuckDuckGo MCP Agent ===")
    duckduckgo_config = MCPAgentConfig(
        name="duckduckgo_agent",
        description="DuckDuckGo search agent",
        command="uvx",
        args=["duckduckgo-mcp-server"],
        tools=["search", "fetch_content"]
    )

    # Create the agent using the factory
    duckduckgo_agent = create_agent("mcp", duckduckgo_config)

    # Initialize and use the agent
    try:
        print("Initializing DuckDuckGo agent...")
        start_time = time.time()
        result = await duckduckgo_agent.initialize()
        init_time = time.time() - start_time
        print(f"Agent initialized in {init_time:.2f} seconds")
        print(f"Initialization result: {result.data}")

        if result.success:
            print("Searching for 'pandas'...")
            start_time = time.time()
            # The task format depends on how the DuckDuckGo MCP server parses tasks
            # We'll try a few different formats
            search_result = await duckduckgo_agent.run("search pandas")
            search_time = time.time() - start_time
            print(f"Search completed in {search_time:.2f} seconds")

            if search_result.success:
                print("\nSearch results:")
                print(search_result.data)

                # Now let's try fetching content from one of the search results
                print("\nFetching content from pandas.pydata.org...")
                start_time = time.time()
                fetch_result = await duckduckgo_agent.run("fetch content from https://pandas.pydata.org/")
                fetch_time = time.time() - start_time
                print(f"Fetch completed in {fetch_time:.2f} seconds")

                if fetch_result.success:
                    print("\nFetched content (first 500 chars):")
                    content = fetch_result.data.get('content', '')
                    if isinstance(content, list) and content and hasattr(content[0], 'text'):
                        print(content[0].text[:500] + "...")
                    else:
                        print(str(content)[:500] + "...")
                else:
                    print(f"\nFetch failed: {fetch_result.error}")
            else:
                print(f"\nSearch failed: {search_result.error}")

        await duckduckgo_agent.cleanup()
        print("DuckDuckGo agent cleaned up")
    except Exception as e:
        print(f"Error with DuckDuckGo agent: {e}")
        await duckduckgo_agent.cleanup()


    # Example 3: Create a custom MCP agent
    print("=== Example 3: Custom MCP Agent ===")
    custom_config = MCPAgentConfig(
        name="custom_agent",
        description="Custom MCP agent",
        command="python",
        args=["custom_mcp_server.py"],
        tools=["custom_tool_1", "custom_tool_2"]
    )

    # Create the agent using the factory
    custom_agent = create_agent("mcp", custom_config)

    # Note: We're not actually running this agent since it requires a custom MCP server
    print("Custom agent created with configuration:")
    print(f"  Command: {custom_agent.mcp_config.command}")
    print(f"  Args: {custom_agent.mcp_config.args}")
    print(f"  Tools: {custom_agent.mcp_config.tools}")

if __name__ == "__main__":
    try:
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Run the main function
        loop.run_until_complete(main())

        # Clean up
        loop.close()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
