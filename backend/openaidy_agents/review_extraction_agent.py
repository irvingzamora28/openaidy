from agents import Agent, Runner
from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json
import asyncio

async def extract_reviews_from_snapshot(snapshot, chunk_size=12000, overlap=512):
    """
    Extracts reviews from a large page snapshot by chunking (with overlap) and running the agent on each chunk.
    Args:
        snapshot (dict or list): The full DOM/accessibility snapshot (already loaded, not a file path).
        chunk_size (int): Approximate number of characters per chunk (default: 12000).
        overlap (int): Number of overlapping characters between chunks (default: 512).
    Returns:
        list: List of extracted reviews (merged from all chunks).
    """
    snapshot_str = json.dumps(snapshot, ensure_ascii=False)
    chunks = []
    i = 0
    while i < len(snapshot_str):
        chunk = snapshot_str[i:i+chunk_size]
        chunks.append(chunk)
        # Overlap: move start forward by chunk_size - overlap
        i += chunk_size - overlap
    all_reviews = []
    for idx, chunk in enumerate(chunks):
        agent = Agent(
            name=f"ReviewExtractionAgentChunk{idx+1}",
            instructions=(
                "You are an expert review extraction agent. Extract all user reviews as a JSON array of objects. Each review must include at least the text, author, and rating if available. Only return valid, complete reviews."
            ),
            model=MODEL_NAME,
        )
        message = (
            f"Given this partial DOM/accessibility snapshot (as JSON):\n{chunk}\n\n"
            "Extract all user reviews you can find as a JSON array. Do not repeat reviews found in previous chunks."
        )
        result = await Runner.run(starting_agent=agent, input=message)
        cleaned_result = deep_clean(result.final_output)
        # Ensure cleaned_result is a list of reviews
        if isinstance(cleaned_result, dict):
            reviews = [cleaned_result]
        elif isinstance(cleaned_result, list):
            reviews = cleaned_result
        else:
            reviews = []
        all_reviews.extend(reviews)
        # Sleep 10 seconds between chunk runs
        if idx < len(chunks) - 1:
            await asyncio.sleep(10)
    # Deduplicate reviews by text (can be improved)
    seen = set()
    merged_reviews = []
    for review in all_reviews:
        text = review.get('text') if isinstance(review, dict) else None
        if text and text not in seen:
            merged_reviews.append(review)
            seen.add(text)
    with open("extracted_reviews.json", "w", encoding="utf-8") as f:
        json.dump(merged_reviews, f, indent=2, ensure_ascii=False)
    return merged_reviews