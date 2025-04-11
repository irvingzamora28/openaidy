"""
Example of using the general-purpose Playwright MCP agent.

This example demonstrates how to use the Playwright agent to navigate, take screenshots,
and interact with web elements. It's part of the MCP agents architecture proof of concept.
"""
import asyncio
import sys
from dotenv import load_dotenv
from backend.agents import create_playwright_agent

async def main():
    """Run the Playwright agent example."""
    # Load environment variables from .env
    load_dotenv()

    # Create and initialize the Playwright agent
    agent = create_playwright_agent()

    try:
        await agent.initialize()

        # Navigate to a website
        nav_result = await agent.run("navigate https://github.com")
        print("Navigation result:", nav_result.get('response', nav_result))

        # Take a screenshot
        screenshot_result = await agent.run("screen_capture")

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

        # Try clicking on an element
        click_result = await agent.run("click text=Sign in")
        print("\nClick result:", click_result.get('response', click_result))

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
