from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json

async def run(url, element_discovery, mcp_server):
    """
    Clicks the 'Sort by' button using the ref from element_discovery, then discovers and returns all new interactive elements (e.g., dropdown options).
    Args:
        url (str): The page URL to analyze.
        element_discovery (dict): Output from element_discovery_agent.run (mapping labels to element info).
        mcp_server: MCP server instance for browser automation.
    Returns:
        dict: Newly discovered elements after clicking 'Sort by'.
    """
    agent = Agent(
        name="InteractionExecutionAgent",
        instructions=(
            "You are an expert UI interaction agent. Your job is to interact with UI elements based on provided references and extract information about newly visible elements."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        f"You are given a dictionary mapping labels to refs, for example: {json.dumps(element_discovery)}. "
        "Click the button whose ref is the value for 'Sort by'. After clicking, extract all sort options (their labels and refs) that become visible. "
        "Return a JSON object mapping each option label to its ref."
    )
    result = await Runner.run(starting_agent=agent, input=message)
    cleaned_result = deep_clean(result.final_output)
    with open("interaction_execution.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    return cleaned_result
