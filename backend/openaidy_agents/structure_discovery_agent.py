
from agents.mcp import MCPServerStdio
from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME


async def run(url):
    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
        },
    ) as mcp_server:
        agent = Agent(
            name="StructureDiscoveryAgent",
            instructions=(
                "Navigate to a Chrome Web Store reviews page, extract all reviews from the accessibility tree or DOM snapshot, and return their references (ref values) as a JSON array. "
                "For each review, include the review container ref, heading ref, review text ref, and any developer reply ref (if present). "
                "Output only a JSON object with one array: 'reviews', each containing the relevant refs and a short description. Do not include review content, only references."
            ),
            model=MODEL_NAME,
            mcp_servers=[mcp_server],
        )

        message = (
            f"Navigate to {url} and extract all reviews from the accessibility tree or DOM snapshot. "
            "Return a JSON object with one array: 'reviews'. "
            "For each review in 'reviews', include: review container ref, heading ref, review text ref, and any developer reply ref (if present). "
            "Output only the JSON object, nothing else."
        )
        result = await Runner.run(starting_agent=agent, input=message)
        return result.final_output
