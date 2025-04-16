"""
Example of using the LangChain agent with multiple tools.

This example demonstrates how to create and use a LangChain agent with multiple tools:
1. Web browsing tools for navigating to websites and taking screenshots
2. Fetch tool for getting content from websites and summarizing it
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Import our agent factory and configuration classes
from backend.agents import (
    create_agent,
    LangChainAgentConfig,
    LangChainToolConfig,
    MCPServerConfig
)

# No need for custom functions as we'll use the built-in tools from our agent architecture

async def main():
    """Run the LangChain multi-tool agent example."""
    # Load environment variables from .env
    load_dotenv()

    print("=== LangChain Multi-Tool Agent Example ===")
    print("This example demonstrates how to create and use a LangChain agent with multiple tools.")

    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)

        # Create a LangChain agent configuration
        config = LangChainAgentConfig(
            name="multi_tool_agent",
            agent_type="react",  # Use ReAct agent
            system_message="You are a helpful assistant that can perform various tasks including fetching content from websites, navigating to web pages, and taking screenshots. Use the tools available to you to complete the user's request.",
            # Add MCP servers for web browsing and content fetching
            mcp_servers={
                "fetch": MCPServerConfig(
                    name="fetch",
                    command="uvx",
                    args=["mcp-server-fetch"],
                    tools=["fetch"],
                    screenshots_dir=str(screenshots_dir)
                ),
                "playwright": MCPServerConfig(
                    name="playwright",
                    command="npx",
                    args=["@playwright/mcp@latest", "--vision", "--headless"],
                    tools=["browser_navigate", "browser_screen_capture"],
                    screenshots_dir=str(screenshots_dir)
                )
            },
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )

        # Create the agent using our factory
        agent = create_agent("langchain", config)

        # Initialize the agent
        print("\nInitializing agent...")
        result = await agent.initialize()
        print(f"Initialization result: {result.data if result.success else result.error}")

        if not result.success:
            print("Failed to initialize agent. Exiting.")
            return

        # Run a series of tasks to demonstrate different capabilities
        # Note: Each task can only use tools from one MCP server due to implementation limitations
        tasks = [
            # Task 1: Use the fetch MCP server
            "Task for fetch MCP server: Use the fetch tool to get the content of https://en.wikipedia.org/wiki/LaMelo_Ball and provide a brief summary of who LaMelo Ball is based on the content.",

            # Task 2: Use the playwright MCP server
            "Task for playwright MCP server: Use the browser_navigate tool to navigate to https://en.wikipedia.org/wiki/NBA and then use the browser_screen_capture tool to take a screenshot of the page."
        ]

        # Run each task separately
        for i, task in enumerate(tasks):
            print(f"\nRunning task {i+1}: {task}")
            try:
                # Use asyncio.wait_for to add a timeout
                task_result = await asyncio.wait_for(
                    agent.run(task),
                    timeout=120  # 2 minute timeout per task
                )
                print(f"Task result: {task_result.data if task_result.success else task_result.error}")
            except asyncio.TimeoutError:
                print(f"Task timed out after 120 seconds")
            except Exception as e:
                print(f"Error running task: {str(e)}")

        # Clean up the agent
        print("\nCleaning up agent...")
        cleanup_result = await agent.cleanup()
        print(f"Cleanup result: {cleanup_result.data if cleanup_result.success else cleanup_result.error}")

        # Print completion message
        print("\nAll tasks completed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
