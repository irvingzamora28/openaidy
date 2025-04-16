"""
Simple example of using the fetch tool directly.

This example demonstrates how to:
1. Connect to the Fetch MCP server
2. Use the fetch tool to get content from a website
3. Print the content
"""
import os
import asyncio
from dotenv import load_dotenv

# Import MCP components
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Run the simple fetch example."""
    # Load environment variables from .env
    load_dotenv()
    
    print("=== Simple Fetch Example ===")
    print("This example demonstrates how to use the fetch tool to get content from a website.")
    
    try:
        # URL to fetch
        url = "https://en.wikipedia.org/wiki/LaMelo_Ball"
        print(f"\nTarget URL: {url}")
        
        # Create server parameters for Fetch MCP
        server_params = StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch"],
        )
        
        # Connect to the Fetch MCP server
        print("\nConnecting to Fetch MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Fetch the URL
                print(f"\nFetching {url}...")
                fetch_result = await session.call_tool("fetch", {"url": url, "max_length": 5000})
                
                # Process the fetch result
                content = ""
                if hasattr(fetch_result, "text") and fetch_result.text:
                    content = fetch_result.text
                elif isinstance(fetch_result, str):
                    content = fetch_result
                else:
                    content = str(fetch_result)
                
                # Print the content
                print(f"\nExtracted content (first 500 characters):")
                print(content[:500] + "..." if len(content) > 500 else content)
                
                # Print completion message
                print("\nFetch complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
