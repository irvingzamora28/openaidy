from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME

async def run(url, mcp_server):
    """
    Navigate to the provided page.
    Args:
        url (str): The page URL to navigate to.
        mcp_server: MCP server instance for browser automation.
    Returns:
        dict: The navigation result (JSON-serializable)
    """
    agent = Agent(
        name="NavigationAgent",
        instructions=(
            "Navigate to the provided page."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        f"Navigate to {url}. "
    )
    result = await Runner.run(starting_agent=agent, input=message)
    return result.final_output
