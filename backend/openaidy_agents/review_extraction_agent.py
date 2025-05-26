from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json

async def run(mcp_server):
    """
    Extracts all reviews from the current page state using the MCP server session and returns them in a nicely formatted JSON.
    Args:
        mcp_server: MCP server instance for browser automation (must already be on the reviews page).
    Returns:
        dict: The extracted reviews in structured JSON format.
    """
    agent = Agent(
        name="ReviewExtractionAgent",
        instructions=(
            "You are an expert at extracting structured review data from a live DOM or accessibility tree using browser automation. "
            "Given access to the current page via MCP, extract all visible reviews and return them as a JSON array. "
            "Each review should include: reviewer name, rating, date, review text, and any developer reply (if present). "
            "Format your output as a list of review objects under the key 'reviews'. Do not summarize or omit any reviews."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        "Extract all reviews from the current page. "
        "Return a JSON object with a single key 'reviews', whose value is a list of objects with: 'reviewer', 'rating', 'date', 'text', and 'developer_reply' (if present). "
        "Output only the JSON object, nothing else."
    )
    result = await Runner.run(starting_agent=agent, input=message)
    cleaned_result = deep_clean(result.final_output)
    with open("review_extraction.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    return cleaned_result
