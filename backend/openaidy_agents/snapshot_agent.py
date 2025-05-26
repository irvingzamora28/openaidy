from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json

async def run(url, mcp_server, filename="initial_snapshot.json"):
    """
    Takes a snapshot of the DOM or accessibility tree and saves it to a JSON file.
    Args:
        url (str): The page URL to analyze.
        mcp_server: MCP server instance for browser automation.
        filename (str): Where to save the snapshot (default: 'initial_snapshot.json').
    Returns:
        dict: The snapshot structure (JSON-serializable)
    """
    agent = Agent(
        name="SnapshotAgent",
        instructions=(
            "You are an expert UI snapshot agent. Your job is to capture and return the full DOM or accessibility tree as JSON when requested."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        "Take a snapshot of the full accessibility tree or DOM structure as JSON. "
        "Output the entire raw JSON object, nothing else."
    )
    # agent = Agent(
    #     name="SnapshotAgent",
    #     instructions=(
    #         "Navigate to the provided page and take a snapshot of the full accessibility tree or DOM structure as JSON. "
    #         "Output only the JSON object, nothing else."
    #     ),
    #     model=MODEL_NAME,
    #     mcp_servers=[mcp_server],
    # )
    # message = (
    #     f"Navigate to {url}. "
    #     "Take a snapshot of the full accessibility tree or DOM structure as JSON. "
    #     "Output only the JSON object, nothing else."
    # )
    result = await Runner.run(starting_agent=agent, input=message)
    cleaned_result = deep_clean(result.final_output)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    return cleaned_result
