"""
Factory for creating LLM providers based on configuration.
"""
import os
from typing import Optional

from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .google_provider import GoogleProvider


def create_llm_provider(
    provider: str,
    api_key: str,
    model: str,
    api_url: Optional[str] = None
) -> LLMProvider:
    """
    Create an LLM provider based on the specified provider type.
    
    Args:
        provider: The provider type (openai, google-genai, deepseek, ollama)
        api_key: The API key for the provider
        model: The model to use
        api_url: Optional API URL for the provider
        
    Returns:
        An instance of the appropriate LLM provider
        
    Raises:
        ValueError: If the provider type is not supported
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    provider = provider.lower()
    logging.info(f"Requested LLM provider: {provider}")
    logging.info(f"API key: {api_key}")
    logging.info(f"Model: {model}")
    logging.info(f"API URL: {api_url}")
    if provider == "openai":
        return OpenAIProvider(api_key=api_key, default_model=model)
    elif provider in ["deepseek", "ollama"]:
        # DeepSeek and Ollama use OpenAI-compatible API but with different base URLs
        return OpenAIProvider(api_key=api_key, base_url=api_url, default_model=model)
    elif provider == "google-genai":
        return GoogleProvider(api_key=api_key, default_model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_llm_provider_from_env() -> LLMProvider:
    """
    Create an LLM provider based on environment variables.
    
    Required environment variables:
    - LLM_API_PROVIDER: The provider type (openai, google-genai, deepseek, ollama)
    - LLM_API_KEY: The API key for the provider
    - LLM_MODEL: The model to use
    - LLM_API_URL: Optional API URL for the provider (required for deepseek and ollama)
    
    Returns:
        An instance of the appropriate LLM provider
        
    Raises:
        ValueError: If required environment variables are missing
    """
    provider = os.getenv("LLM_API_PROVIDER")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    api_url = os.getenv("LLM_API_URL")
    
    if not provider:
        raise ValueError("LLM_API_PROVIDER environment variable is required")
    if not api_key:
        raise ValueError("LLM_API_KEY environment variable is required")
    if not model:
        raise ValueError("LLM_MODEL environment variable is required")
    
    # API URL is required for deepseek and ollama
    if provider.lower() in ["deepseek", "ollama"] and not api_url:
        raise ValueError(f"LLM_API_URL environment variable is required for {provider}")
    
    return create_llm_provider(provider, api_key, model, api_url)
