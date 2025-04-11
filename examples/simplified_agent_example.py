"""
Example of using the simplified agent architecture.

This example demonstrates how to create and use MCP agents with different configurations.
"""
import asyncio
import sys
import time
from dotenv import load_dotenv
from backend.agents import create_agent, MCPAgentConfig

async def main():
    """Run the simplified agent example."""
    # Load environment variables from .env
    load_dotenv()
    
    # Create a Playwright MCP agent for browser automation
    print("=== Creating Playwright MCP Agent ===")
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
        start_time = time.time()
        result = await playwright_agent.initialize()
        init_time = time.time() - start_time
        print(f"Agent initialized in {init_time:.2f} seconds")
        print(f"Initialization result: {result.data}")
        
        if result.success:
            print("Taking screenshot of GitHub...")
            start_time = time.time()
            results = await playwright_agent.run_sequence([
                "Navigate to https://github.com",
                "Take a screenshot"
            ])
            sequence_time = time.time() - start_time
            print(f"Sequence completed in {sequence_time:.2f} seconds")
            
            for i, result in enumerate(results):
                print(f"Result {i+1}: {'Success' if result.success else 'Failure'}")
                if result.success and isinstance(result.data, dict) and 'image_base64' in result.data:
                    print(f"Screenshot base64 preview: {result.data['image_base64'][:50]}...")
        
        await playwright_agent.cleanup()
        print("Playwright agent cleaned up")
    except Exception as e:
        print(f"Error with Playwright agent: {e}")
        await playwright_agent.cleanup()
    
    print("\nWith our simplified architecture, we can create different types of MCP agents")
    print("by simply providing the appropriate configuration, without needing specialized classes.")
    print("\nFor example, to create a DuckDuckGo search agent:")
    print("""
    duckduckgo_config = MCPAgentConfig(
        name="duckduckgo_agent",
        description="DuckDuckGo search agent",
        command="uvx",
        args=["duckduckgo-mcp-server"],
        tools=["search", "fetch_content"]
    )
    
    duckduckgo_agent = create_agent("mcp", duckduckgo_config)
    """)
    
    print("\nOr to create a custom MCP agent:")
    print("""
    custom_config = MCPAgentConfig(
        name="custom_agent",
        description="Custom MCP agent",
        command="python",
        args=["custom_mcp_server.py"],
        tools=[]  # Will auto-discover available tools
    )
    
    custom_agent = create_agent("mcp", custom_config)
    """)

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
