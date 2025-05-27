"""
Review Analysis Agent: Analyzes a large list of extracted reviews in context-friendly chunks using an LLM agent.
Useful for summarization, sentiment, topic extraction, and more.
"""

from openaidy_agents.llm_env import MODEL_NAME
from openaidy_agents.utils import deep_clean
import json
import asyncio

async def analyze_reviews_in_chunks(reviews, chunk_size=30, overlap=5, analysis_tasks=None, output_file="review_analysis_results.json"):
    """
    Analyzes a large list of reviews in overlapping chunks. Each chunk is analyzed by the agent, and results are aggregated.
    Args:
        reviews (list): List of review dicts (as output by extract_reviews_from_snapshot).
        chunk_size (int): Number of reviews per chunk (default: 30).
        overlap (int): Number of overlapping reviews between chunks (default: 5).
        analysis_tasks (list): List of analysis tasks (strings) to perform. If None, use defaults.
        output_file (str): File to save aggregated chunk analysis results.
    Returns:
        list: List of analysis results (one per chunk).
    """
    from agents import Agent, Runner
    if analysis_tasks is None:
        analysis_tasks = [
            "Summarize the overall sentiment (positive/negative/neutral) and why.",
            "List the most common themes or topics mentioned.",
            "Highlight the most frequent complaints and praises.",
            "Identify any patterns in ratings (e.g., clusters of 1-star/5-star reviews).",
            "Extract 3 representative reviews with their text, author, and rating.",
        ]
    instructions = (
        "You are an expert product review analyst. Given a JSON array of user reviews (each with text, author, rating, etc.), "
        "perform the following analyses:\n- " + "\n- ".join(analysis_tasks) + "\nOutput your results as a JSON object with clear keys for each task."
    )
    results = []
    n = len(reviews)
    i = 0
    chunk_id = 1
    while i < n:
        chunk = reviews[i:i+chunk_size]
        agent = Agent(
            name=f"ReviewAnalysisAgentChunk{chunk_id}",
            instructions=instructions,
            model=MODEL_NAME,
        )
        message = (
            "Analyze the following reviews (in JSON array format):\n" + json.dumps(chunk, ensure_ascii=False) + "\n\n"
            "Return your analysis as a JSON object."
        )
        result = await Runner.run(starting_agent=agent, input=message)
        cleaned_result = deep_clean(result.final_output)
        results.append(cleaned_result)
        print(f"[ReviewAnalysis] Chunk {chunk_id}: analyzed {len(chunk)} reviews.")
        i += chunk_size - overlap
        chunk_id += 1
        if i < n:
            await asyncio.sleep(10)
    # Save all chunk analyses to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return results

# Example usage (not run automatically)
# reviews = ... # Load your extracted_reviews.json
# asyncio.run(analyze_reviews_in_chunks(reviews))
