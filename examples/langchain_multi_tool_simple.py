"""
Example of using LangChain with multiple tools including MCP.

This example demonstrates how to create a LangChain agent with multiple tools:
1. Calculator tools for math operations
2. Weather API tool for getting weather information
3. Web browsing tools for navigating to websites, taking screenshots, and extracting content
"""
import os
import asyncio
import base64
from pathlib import Path
from typing import List, Tuple
from dotenv import load_dotenv

# Import LangChain components
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate

# Import MCP components
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define calculator functions
def add(numbers: str) -> str:
    """Add two numbers."""
    try:
        a, b = map(float, numbers.split(','))
        return str(a + b)
    except Exception as e:
        return f"Error: {str(e)}"

def subtract(numbers: str) -> str:
    """Subtract the second number from the first."""
    try:
        a, b = map(float, numbers.split(','))
        return str(a - b)
    except Exception as e:
        return f"Error: {str(e)}"

def multiply(numbers: str) -> str:
    """Multiply two numbers."""
    try:
        a, b = map(float, numbers.split(','))
        return str(a * b)
    except Exception as e:
        return f"Error: {str(e)}"

def divide(numbers: str) -> str:
    """Divide the first number by the second."""
    try:
        a, b = map(float, numbers.split(','))
        if b == 0:
            return "Error: Cannot divide by zero"
        return str(a / b)
    except Exception as e:
        return f"Error: {str(e)}"

# Define a weather API tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # This is a mock implementation
    weather_data = {
        "new york": {"temperature": 72, "condition": "Sunny"},
        "london": {"temperature": 65, "condition": "Cloudy"},
        "tokyo": {"temperature": 80, "condition": "Rainy"},
        "sydney": {"temperature": 85, "condition": "Clear"},
        "paris": {"temperature": 70, "condition": "Partly Cloudy"}
    }
    
    # Normalize location name for case-insensitive matching
    normalized_location = location.lower().strip()
    
    # Return weather data if available
    if normalized_location in weather_data:
        data = weather_data[normalized_location]
        return f"Weather in {location}: {data['temperature']}°F, {data['condition']}"
    else:
        # For demo purposes, return mock data even if location is not in our database
        return f"Weather in {location}: 75°F, Mostly Sunny (mock data)"

async def run_math_task(task: str) -> Tuple[bool, str]:
    """
    Run a math task using LangChain.
    
    Args:
        task: The math task to run
        
    Returns:
        A tuple of (success, result_text)
    """
    try:
        # Create LangChain tools
        tools = [
            Tool(
                name="add",
                func=add,
                description="Add two numbers. Input should be two numbers separated by a comma."
            ),
            Tool(
                name="subtract",
                func=subtract,
                description="Subtract the second number from the first. Input should be two numbers separated by a comma."
            ),
            Tool(
                name="multiply",
                func=multiply,
                description="Multiply two numbers. Input should be two numbers separated by a comma."
            ),
            Tool(
                name="divide",
                func=divide,
                description="Divide the first number by the second. Input should be two numbers separated by a comma."
            )
        ]
        
        # Create LangChain model
        model = ChatOpenAI(
            model=os.environ.get("LLM_MODEL", "gpt-4o"),
            api_key=os.environ.get("LLM_API_KEY"),
            base_url=os.environ.get("LLM_API_URL"),
            temperature=0.2
        )
        
        # Create a prompt template
        template = """
        You are a helpful assistant that can perform math calculations.
        Use the tools available to you to complete the user's request.

        You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(template)
        
        # Create agent
        agent = create_react_agent(
            llm=model,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            timeout=60
        )
        
        # Run the agent
        result = await asyncio.wait_for(
            agent_executor.ainvoke({"input": task}),
            timeout=60
        )
        
        return True, result["output"]
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Error running math task: {str(e)}"

async def run_weather_task(task: str) -> Tuple[bool, str]:
    """
    Run a weather task using LangChain.
    
    Args:
        task: The weather task to run
        
    Returns:
        A tuple of (success, result_text)
    """
    try:
        # Create LangChain tools
        tools = [
            Tool(
                name="get_weather",
                func=get_weather,
                description="Get the current weather for a location. Input should be a city name."
            )
        ]
        
        # Create LangChain model
        model = ChatOpenAI(
            model=os.environ.get("LLM_MODEL", "gpt-4o"),
            api_key=os.environ.get("LLM_API_KEY"),
            base_url=os.environ.get("LLM_API_URL"),
            temperature=0.2
        )
        
        # Create a prompt template
        template = """
        You are a helpful assistant that can check the weather.
        Use the tools available to you to complete the user's request.

        You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(template)
        
        # Create agent
        agent = create_react_agent(
            llm=model,
            tools=tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            timeout=60
        )
        
        # Run the agent
        result = await asyncio.wait_for(
            agent_executor.ainvoke({"input": task}),
            timeout=60
        )
        
        return True, result["output"]
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Error running weather task: {str(e)}"

async def run_web_task(task: str, url: str, screenshots_dir: Path) -> Tuple[bool, str]:
    """
    Run a web task using MCP and LangChain.
    
    Args:
        task: The web task to run
        url: The URL to navigate to
        screenshots_dir: Directory to save screenshots
        
    Returns:
        A tuple of (success, result_text)
    """
    try:
        # Create server parameters for Playwright MCP
        server_params = StdioServerParameters(
            command="npx",
            args=["@playwright/mcp@latest", "--vision", "--headless"],
        )
        
        # Connect to the MCP server
        print(f"\nConnecting to Playwright MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Navigate to the URL
                print(f"\nNavigating to {url}...")
                await session.call_tool("browser_navigate", {"url": url})
                
                # Wait for the page to load
                print("\nWaiting for page to load...")
                await asyncio.sleep(3)
                
                # Take a screenshot
                print("\nTaking screenshot...")
                screenshot_result = await session.call_tool("browser_screen_capture", {"format": "jpeg"})
                
                # Process the screenshot result
                screenshot_data = None
                if hasattr(screenshot_result, "content") and screenshot_result.content:
                    for item in screenshot_result.content:
                        if hasattr(item, "data") and item.data:
                            if isinstance(item.data, bytes):
                                screenshot_data = item.data
                            elif isinstance(item.data, str):
                                screenshot_data = base64.b64decode(item.data)
                            break
                
                # Save the screenshot
                screenshot_path = None
                if screenshot_data:
                    screenshot_path = screenshots_dir / f"web_task_screenshot.png"
                    with open(screenshot_path, "wb") as f:
                        f.write(screenshot_data)
                    print(f"Screenshot saved to {screenshot_path}")
                else:
                    print("No screenshot data found in the result.")
                
                # Extract text content
                print("\nExtracting text content...")
                text_result = await session.call_tool("browser_extract_text", {})
                
                # Process the text result
                page_text = ""
                if hasattr(text_result, "text") and text_result.text:
                    page_text = text_result.text
                elif isinstance(text_result, str):
                    page_text = text_result
                elif hasattr(text_result, "content") and text_result.content:
                    for item in text_result.content:
                        if hasattr(item, "text") and item.text:
                            page_text = item.text
                            break
                
                # Close the browser
                print("\nClosing browser...")
                await session.call_tool("browser_close")
                
                # Check if we got text content
                if not page_text:
                    return False, "No text content found on the page."
                
                # Truncate text if it's too long
                if len(page_text) > 10000:
                    print(f"\nText content is {len(page_text)} characters long. Truncating to 10000 characters.")
                    page_text = page_text[:10000] + "..."
                else:
                    print(f"\nText content is {len(page_text)} characters long.")
                
                # Create LangChain model
                print("\nCreating LangChain model...")
                model = ChatOpenAI(
                    model=os.environ.get("LLM_MODEL", "gpt-4o"),
                    api_key=os.environ.get("LLM_API_KEY"),
                    base_url=os.environ.get("LLM_API_URL"),
                    temperature=0.2
                )
                
                # Create a prompt template
                prompt = PromptTemplate.from_template(
                    "You are a helpful assistant that analyzes web content. "
                    "Based on the following text extracted from {url}, please answer this question: {task}\n\n"
                    "Content: {content}"
                )
                
                # Generate the answer
                print("\nGenerating answer...")
                chain = prompt | model
                answer = await chain.ainvoke({"url": url, "task": task, "content": page_text})
                
                return True, answer.content
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Error running web task: {str(e)}"

async def main():
    """Run the LangChain multi-tool agent example."""
    # Load environment variables from .env
    load_dotenv()
    
    print("=== LangChain Multi-Tool Agent Example (Simple Approach) ===")
    print("This example demonstrates how to create a LangChain agent with multiple tools.")
    
    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        
        # Run a math task
        # print("\n=== Running Math Task ===")
        # math_task = "What is the result of (23 * 45) - (12 / 4)?"
        # print(f"Task: {math_task}")
        # math_success, math_result = await run_math_task(math_task)
        # if math_success:
        #     print(f"Result: {math_result}")
        # else:
        #     print(f"Failed: {math_result}")
        
        # # Run a weather task
        # print("\n=== Running Weather Task ===")
        # weather_task = "What's the weather like in New York?"
        # print(f"Task: {weather_task}")
        # weather_success, weather_result = await run_weather_task(weather_task)
        # if weather_success:
        #     print(f"Result: {weather_result}")
        # else:
        #     print(f"Failed: {weather_result}")
        
        # # Run a web task for LaMelo Ball
        # print("\n=== Running Web Task (LaMelo Ball) ===")
        # lamelo_url = "https://en.wikipedia.org/wiki/LaMelo_Ball"
        # lamelo_task = "Who is LaMelo Ball and what are his career achievements?"
        # print(f"Task: {lamelo_task}")
        # print(f"URL: {lamelo_url}")
        # lamelo_success, lamelo_result = await run_web_task(lamelo_task, lamelo_url, screenshots_dir)
        # if lamelo_success:
        #     print(f"Result: {lamelo_result}")
        # else:
        #     print(f"Failed: {lamelo_result}")
        
        # Run a web task for NBA
        # print("\n=== Running Web Task (NBA) ===")
        # nba_url = "https://en.wikipedia.org/wiki/NBA"
        # nba_task = "How many teams are in the NBA and how many games are played in a regular season if each team plays 82 games?"
        # print(f"Task: {nba_task}")
        # print(f"URL: {nba_url}")
        # nba_success, nba_result = await run_web_task(nba_task, nba_url, screenshots_dir)
        # if nba_success:
        #     print(f"Result: {nba_result}")
        # else:
        #     print(f"Failed: {nba_result}")
        
        # Run a web task for Playwright
        print("\n=== Running Web Task (Playwright) ===")
        lamelo_url = "https://github.com/microsoft/playwright-mcp"
        lamelo_task = "List all the tools of Playwright MCP."
        print(f"Task: {lamelo_task}")
        print(f"URL: {lamelo_url}")
        lamelo_success, lamelo_result = await run_web_task(lamelo_task, lamelo_url, screenshots_dir)
        if lamelo_success:
            print(f"Result: {lamelo_result}")
        else:
            print(f"Failed: {lamelo_result}")
            
        # Print completion message
        print("\nAll tasks completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
