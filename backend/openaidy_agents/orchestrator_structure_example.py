import shutil
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from dotenv import load_dotenv

# Load .env before any agent/model setup
load_dotenv()

from openaidy_agents.review_analysis_orchestrator import ReviewAnalysisOrchestrator


async def main():
    url = "https://chromewebstore.google.com/detail/momentum/laookkfknpbbblfpciffpaejjkokdgca/reviews"
    orchestrator = ReviewAnalysisOrchestrator()
    result = await orchestrator.run(url)
    print("Orchestrator result:")
    print(result)

if __name__ == "__main__":
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install Node.js and npx.")
    asyncio.run(main())
