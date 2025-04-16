"""
Example of using our agent architecture with the fetch tool.

This example demonstrates how to:
1. Create an agent with the fetch tool
2. Use the agent to fetch and summarize content from a website
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from backend.agents import (
    create_agent,
    LangChainAgentConfig,
    MCPServerConfig
)

async def main():
    """Run the agent fetch summary example."""
    # Load environment variables from .env
    load_dotenv()
    
    print("=== Agent Fetch Summary Example ===")
    print("This example demonstrates how to create an agent with the fetch tool.")
    
    try:
        # Create a LangChain agent configuration
        config = LangChainAgentConfig(
            name="fetch_summary_agent",
            agent_type="react",  # Use ReAct agent
            system_message="You are a helpful assistant that can fetch and summarize content from websites. "
                          "Your task is to fetch the content from a URL and provide a comprehensive summary.",
            # Add MCP server for fetch
            mcp_servers={
                "fetch": MCPServerConfig(
                    name="fetch",
                    command="uvx",
                    args=["mcp-server-fetch"],
                    tools=["fetch"],
                    screenshots_dir="screenshots"  # Not used for fetch, but required by the config
                )
            },
            verbose=True
        )
        
        # Create the agent
        agent = create_agent("langchain", config)
        
        # Initialize the agent
        print("\nInitializing agent...")
        result = await agent.initialize()
        print(f"Initialization result: {result.data if result.success else result.error}")
        
        if not result.success:
            print("Failed to initialize agent. Exiting.")
            return
        
        # Run a fetch and summarize task
        print("\nRunning fetch and summarize task...")
        url = "https://en.wikipedia.org/wiki/LaMelo_Ball"
        task = f"Fetch the content of {url} and provide a comprehensive summary of who LaMelo Ball is, his career, achievements, and any other important information."
        task_result = await agent.run(task)
        
        if task_result.success:
            print("\nTask completed successfully!")
            print("\nSummary:")
            print(task_result.data)
        else:
            print(f"\nTask failed: {task_result.error}")
        
        # Clean up the agent
        print("\nCleaning up agent...")
        cleanup_result = await agent.cleanup()
        print(f"Cleanup result: {cleanup_result.data if cleanup_result.success else cleanup_result.error}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
