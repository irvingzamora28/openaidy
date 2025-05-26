from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
import json
from openaidy_agents.utils import deep_clean

async def run(url, target_labels, mcp_server):
    """
    Discovers elements on the page matching the given labels (e.g., 'Sort by', 'Load more').
    Args:
        url (str): The page URL to analyze.
        target_labels (list): List of labels to search for (e.g., ['Sort by', 'Load more']).
        mcp_server: MCP server instance for browser automation.
    Returns:
        dict: Mapping of label to discovered element refs and metadata.
    """
    labels_str = ', '.join(f'"{lbl}"' for lbl in target_labels)
    agent = Agent(
        name="ElementDiscoveryAgent",
        instructions=(
            "You are an expert UI element discovery agent. Your job is to identify and return the refs of interactive elements based on their visible labels."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        f"Take a snapshot of the DOM or accessibility tree. For each element whose visible label matches any of: {labels_str}, find and return its ref in a JSON object. "
        "Only include labels in the output if a matching element is found. If a label is not present, omit it from the JSON result. Do not include nulls, empty strings, or explanations for missing labels."
    )
    result = await Runner.run(starting_agent=agent, input=message)
    cleaned_result = deep_clean(result.final_output)
    with open("element_discovery.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    return cleaned_result
