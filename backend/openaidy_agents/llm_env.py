"""
llm_env.py: Shared LLM environment setup for all agent modules.
"""
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

# Load .env before any agent/model setup
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
