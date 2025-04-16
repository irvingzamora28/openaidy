"""
Simple example of using MCP directly to take screenshots.

This example demonstrates how to use MCP directly with Playwright
to take screenshots of websites using just the essential tools.
"""
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Run the simple MCP screenshot example."""
    # Load environment variables from .env
    load_dotenv()

    print("=== Simple MCP Screenshot Example ===")
    print("This example demonstrates how to use MCP directly to take screenshots.")

    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)

        # Create server parameters for Playwright MCP
        server_params = StdioServerParameters(
            command="npx",
            args=["@playwright/mcp@latest", "--vision", "--headless"],
        )

        # Connect to the MCP server
        print("\nConnecting to Playwright MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()

                # No need to create a tab, just navigate directly

                # Navigate to GitHub
                print("\nNavigating to GitHub.com...")
                await session.call_tool("browser_navigate", {"url": "https://github.com"})

                # Wait for the page to load
                print("\nWaiting for page to load...")
                await asyncio.sleep(2)

                # Take a screenshot
                print("\nTaking screenshot...")
                screenshot_result = await session.call_tool("browser_screen_capture")
                print(f"Screenshot result type: {type(screenshot_result)}")

                # Process the screenshot result
                print("\nProcessing screenshot...")
                screenshot_data = None

                # Check if the result contains image data
                if hasattr(screenshot_result, "content") and screenshot_result.content:
                    # The screenshot is in the content field
                    for item in screenshot_result.content:
                        if hasattr(item, "data") and item.data:
                            # Found the image data
                            screenshot_data = item.data
                            print(f"Found screenshot data in content item")
                            break

                # Save the screenshot
                if screenshot_data:
                    screenshot_path = screenshots_dir / "simple_mcp_github.png"
                    with open(screenshot_path, "wb") as f:
                        f.write(base64.b64decode(screenshot_data))
                    print(f"Screenshot saved to {screenshot_path}")
                else:
                    print("No screenshot data found in the result.")
                    print(f"Result attributes: {dir(screenshot_result)}")
                    print(f"Result: {screenshot_result}")

                # Close the browser
                print("\nClosing browser...")
                await session.call_tool("browser_close")
                print("Browser closed")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
