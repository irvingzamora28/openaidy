"""
Example of using the efficient Playwright MCP agent.

This example demonstrates how to use the efficient Playwright agent to navigate and take screenshots
with better performance by following the official MCP SDK documentation.
It's part of the MCP agents architecture proof of concept.
"""
import asyncio
import sys
import time
from dotenv import load_dotenv
from backend.agents import create_efficient_playwright_agent

async def main():
    """Run the efficient Playwright agent example."""
    # Load environment variables from .env
    load_dotenv()

    # Create and initialize the efficient Playwright agent
    agent = create_efficient_playwright_agent()

    try:
        start_time = time.time()
        print("Initializing agent...")
        await agent.initialize()
        init_time = time.time() - start_time
        print(f"Agent initialized in {init_time:.2f} seconds")

        # Run a sequence of tasks in a single session
        start_time = time.time()
        print("Running sequence of tasks...")
        tasks = [
            "Navigate to https://github.com",
            "Take a screenshot"
        ]
        results = await agent.run_sequence(tasks)
        sequence_time = time.time() - start_time
        print(f"Sequence completed in {sequence_time:.2f} seconds")

        # Process the results
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            if isinstance(result, dict):
                if 'image_base64' in result:
                    print("Screenshot base64 data preview (first 100 chars):")
                    print(result['image_base64'][:100] + "...")
                elif 'response' in result:
                    print("Response:", result['response'])
                elif 'error' in result:
                    print("Error:", result['error'])
                else:
                    print("Unexpected result:", result)
            else:
                print("Unexpected result type:", type(result))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise

    finally:
        # Always cleanup resources
        print("Cleaning up...")
        start_time = time.time()
        await agent.cleanup()
        cleanup_time = time.time() - start_time
        print(f"Cleanup completed in {cleanup_time:.2f} seconds")

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
