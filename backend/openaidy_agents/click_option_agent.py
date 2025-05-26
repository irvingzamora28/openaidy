from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json

async def run(option_label, options_mapping, mcp_server):
    """
    Clicks the UI element corresponding to the given option label using its ref from the options_mapping.
    Args:
        option_label (str): The label of the option to click (e.g., 'Lowest to highest rating').
        options_mapping (dict): Mapping of option labels to refs (e.g., from interaction_execution_agent).
        mcp_server: MCP server instance for browser automation.
    Returns:
        dict: Confirmation of the click and optionally a snapshot of the UI state after the click.
    """
    agent = Agent(
        name="ClickOptionAgent",
        instructions=(
            "You are an expert UI automation agent. Your job is to click UI elements based on provided references and report the result."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )
    message = (
        f"You are given a dictionary mapping option labels to refs: {json.dumps(options_mapping)}. "
        f"Click the element whose label is '{option_label}' (use its ref). After clicking, return a JSON object confirming the click and, if possible, a snapshot of the UI state after the click."
    )
    result = await Runner.run(starting_agent=agent, input=message)
    cleaned_result = deep_clean(result.final_output)
    with open("click_option_result.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)
    return cleaned_result
