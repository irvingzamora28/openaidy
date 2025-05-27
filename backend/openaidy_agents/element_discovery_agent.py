from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
import json
from openaidy_agents.utils import deep_clean

async def discover_elements_from_snapshot(snapshot, target_labels, chunk_size=12000, reverse=False):
    """
    Discovers elements in a large snapshot by chunking and running the agent on each chunk.
    Args:
        snapshot (dict or list): The full DOM/accessibility snapshot (already loaded, not a file path).
        target_labels (list): List of labels to search for (e.g., ['Sort by', 'Load more']).
        chunk_size (int): Approximate number of characters per chunk (default: 12000).
        reverse (bool): If True, process chunks from last to first (useful if target is likely at the end).
    Returns:
        dict: Mapping of label to discovered element refs and metadata (merged from all chunks).
    """
    import json
    from openaidy_agents.utils import deep_clean
    labels_str = ', '.join(f'"{lbl}"' for lbl in target_labels)
    # Serialize snapshot to JSON string and break into chunks
    snapshot_str = json.dumps(snapshot, ensure_ascii=False)
    chunks = [snapshot_str[i:i+chunk_size] for i in range(0, len(snapshot_str), chunk_size)]
    if reverse:
        chunks = list(reversed(chunks))
    merged_result = {}
    import asyncio
    for idx, chunk in enumerate(chunks):
        agent = Agent(
            name=f"ElementDiscoveryAgentChunk{(len(chunks)-idx) if reverse else (idx+1)}",
            instructions=(
                "You are an expert UI element discovery agent. Your job is to identify and return the refs of interactive elements based on their visible labels."
            ),
            model=MODEL_NAME,
        )
        message = (
            f"Given this partial DOM/accessibility snapshot (as JSON):\n{chunk}\n\n"
            f"For each element whose visible label matches any of: {labels_str}, find and return its ref in a JSON object. "
            "Only include labels in the output if a matching element is found. If a label is not present, omit it from the JSON result. Do not include nulls, empty strings, or explanations for missing labels."
        )
        result = await Runner.run(starting_agent=agent, input=message)
        cleaned_result = deep_clean(result.final_output)
        # Merge results: if a label is found in multiple chunks, prefer the first occurrence
        for label, value in cleaned_result.items():
            if label not in merged_result:
                merged_result[label] = value
        # Early exit: if all target_labels are found, break
        if all(label in merged_result for label in target_labels):
            break
        # Sleep 10 seconds between chunk runs
        if idx < len(chunks) - 1:
            await asyncio.sleep(10)
    with open("element_discovery.json", "w", encoding="utf-8") as f:
        json.dump(merged_result, f, indent=2, ensure_ascii=False)
    return merged_result
