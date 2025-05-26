import asyncio
import shutil
import os
from dotenv import load_dotenv

# Load .env before any agent/model setup
load_dotenv()

from agents.mcp import MCPServerStdio
from agents import Agent, Runner, trace
import os
from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

# Load .env before any agent/model setup
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("LLM_API_URL") or ""
API_KEY = os.getenv("LLM_API_KEY") or ""
MODEL_NAME = os.getenv("LLM_MODEL") or ""

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set LLM_API_URL, LLM_API_KEY, LLM_MODEL via env var or code."
    )

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)
set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)

# Print LLM env config for debugging
def print_llm_env():
    print("LLM_API_PROVIDER:", os.getenv("LLM_API_PROVIDER"))
    print("LLM_API_KEY:", os.getenv("LLM_API_KEY")[:6] + "..." if os.getenv("LLM_API_KEY") else None)
    print("LLM_MODEL:", os.getenv("LLM_MODEL"))
    print("LLM_API_URL:", os.getenv("LLM_API_URL"))

async def run(mcp_server, url):
    print(f"[INFO] Using Gemini model: {MODEL_NAME}")
    agent = Agent(
        name="StructureDiscoveryAgent",
        instructions=(
            "Navigate to a Chrome Web Store reviews page, extract all reviews from the accessibility tree or DOM snapshot, and return their references (ref values) as a JSON array. "
            "For each review, include the review container ref, heading ref, review text ref, and any developer reply ref (if present). "
            "Also, extract and include the refs for any 'Load more' buttons and review sorting buttons, with a short description of each. "
            "Output only a JSON object with three arrays: 'reviews', 'load_more_buttons', and 'sort_buttons', each containing the relevant refs and a short description. Do not include review content, only references."
        ),
        model=MODEL_NAME,
        mcp_servers=[mcp_server],
    )

    message = (
        f"Navigate to {url} and extract all reviews from the accessibility tree or DOM snapshot. "
        "Return a JSON object with three arrays: 'reviews', 'load_more_buttons', and 'sort_buttons'. "
        "For each review in 'reviews', include: review container ref, heading ref, review text ref, and any developer reply ref (if present). "
        "For 'load_more_buttons' and 'sort_buttons', include the ref and a short description of the button. Output only the JSON object, nothing else."
    )
    print("\n" + "-" * 40)
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

async def main():
    print("Loaded LLM environment configuration:")
    print_llm_env()
    url = "https://chromewebstore.google.com/detail/momentum/laookkfknpbbblfpciffpaejjkokdgca/reviews"
    print(f"[INFO] Using hardcoded reviews URL: {url}")

    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--headless", "--viewport-size=1720,920"],
        },
    ) as server:
        with trace(workflow_name="MCP Playwright Example"):
            await run(server, url)

if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install Node.js and npx.")
    asyncio.run(main())
