"""Example script demonstrating how to take screenshots with an MCP agent.

This example shows how to use an MCP agent with Playwright configuration
to navigate to a URL and take a screenshot.

NOTE: This example is deprecated. Use simplified_agent_example.py instead.
"""
import asyncio
import sys
from dotenv import load_dotenv
from backend.agents import create_agent, MCPAgentConfig

async def main():
    # Load environment variables from .env
    load_dotenv()

    # Create and initialize the MCP agent with Playwright configuration
    playwright_config = MCPAgentConfig(
        name="screenshot_agent",
        description="Screenshot agent using Playwright",
        command="npx",
        args=["@playwright/mcp@latest", "--vision", "--headless"],
        tools=["browser_navigate", "browser_screen_capture"]
    )

    # Create the agent using the factory
    agent = create_agent("mcp", playwright_config)

    try:
        await agent.initialize()

        # First navigate to the page
        nav_result = await agent.run("Navigate to https://github.com")
        print("Navigation result:", nav_result.get('response', nav_result))

        # Then take the screenshot
        screenshot_result = await agent.run("Take a screenshot")

        # Print the first 100 chars of base64 data if available
        if isinstance(screenshot_result, dict):
            if 'image_base64' in screenshot_result:
                print("\nScreenshot base64 data preview (first 100 chars):")
                print(screenshot_result['image_base64'][:100] + "...")
            elif 'response' in screenshot_result:
                print("\nResponse:", screenshot_result['response'])
            else:
                print("\nUnexpected screenshot result:", screenshot_result)
        else:
            print("\nUnexpected result type:", type(screenshot_result))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

    finally:
        # Always cleanup resources
        await agent.cleanup()

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
