"""
Interaction Discovery Agent

Discovers interactive elements (buttons, sorting, etc.) on the Chrome Web Store reviews page, using the structure data discovered previously.
"""
from agents.mcp import MCPServerStdio
from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME

async def run(url):
    """
    Discover interactive elements (e.g., load more, sorting buttons).
    Args:
        url (str): The Chrome Web Store reviews page URL.
    Returns:
        dict: Interaction discovery result (JSON-serializable)
    """
    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
        },
    ) as mcp_server:
        agent = Agent(
            name="InteractionDiscoveryAgent",
            instructions=(
                "Analyze the Chrome Web Store reviews page and identify ALL interactive elements that could affect review extraction. "
                "This includes (but is not limited to): load more buttons, filters, sorting controls, pagination controls, tabs, dropdowns, and any other element that changes which reviews are visible. "
                "Return a JSON object with arrays for each type: 'load_more_buttons', 'sort_buttons', 'filters', 'pagination', 'tabs', 'dropdowns', and any other relevant group, each containing their refs and a short description. "
                "Do not include review content, only references and descriptions."
            ),
            model=MODEL_NAME,
            mcp_servers=[mcp_server],
        )
        message = (
            f"Navigate to {url} and extract all interactive elements from the accessibility tree or DOM snapshot. "
            "Return a JSON object with one array: 'interactive_elements'. "
            "Identify and list ALL interactive elements that could affect which reviews are shown: load more buttons, filters, sorting controls, pagination, tabs, dropdowns, and any other relevant controls. "
            "Return a JSON object with arrays for each type ('load_more_buttons', 'sort_buttons', 'filters', 'pagination', 'tabs', 'dropdowns', etc.), each containing refs and a short description."
            "Output only the JSON object, nothing else."
        )
        result = await Runner.run(starting_agent=agent, input=message)
        return result.final_output
