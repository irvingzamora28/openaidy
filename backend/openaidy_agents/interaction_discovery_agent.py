"""
Interaction Discovery Agent

Discovers interactive elements (buttons, sorting, etc.) on the Chrome Web Store reviews page, using the structure data discovered previously.
"""
from agents.mcp import MCPServerStdio
from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME

async def run(url, mcp_server=None):
    """
    Discover interactive elements (e.g., load more, sorting buttons).
    Args:
        url (str): The Chrome Web Store reviews page URL.
    Returns:
        dict: Interaction discovery result (JSON-serializable)
    """
    if mcp_server is None:
        async with MCPServerStdio(
            cache_tools_list=True,
            params={
                "command": "npx",
                "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
            },
        ) as mcp_server_:
            return await run(url, mcp_server_)
    # Use the provided mcp_server below
    agent = Agent(
        name="InteractionDiscoveryAgent",
        instructions=(
            "1. Navigate to the Chrome Web Store reviews page. "
            "2. Find and press/click the button labeled 'Sort by' (do not use a fixed ref; use the visible label). "
            "3. After pressing the button, take and return a snapshot of the full accessibility tree or DOM structure as JSON. "
            "Output only the JSON object, nothing else."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        f"Navigate to {url}. "
        "Find and press/click the button labeled 'Sort by'. "
        "After pressing, take a snapshot of the full accessibility tree or DOM structure as JSON. "
        "Return only this snapshot as JSON. "
        "Output only the JSON object, nothing else."
    )
    result = await Runner.run(starting_agent=agent, input=message)
    import json
    with open("interaction_discovery.json", "w", encoding="utf-8") as f:
        json.dump(result.final_output, f, indent=2, ensure_ascii=False)
    return result.final_output

