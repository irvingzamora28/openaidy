"""
OpenAI-compatible LLM provider.
This provider works with OpenAI, DeepSeek, and other OpenAI API-compatible services.
"""
from typing import Dict, List, Optional, Any

from openai import AsyncOpenAI
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI and OpenAI-compatible APIs (DeepSeek, Ollama, etc.)"""

    def __init__(self, api_key: str, base_url: Optional[str] = None, default_model: str = "gpt-3.5-turbo", client=None):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: API key for authentication
            base_url: Optional base URL for the API (for non-OpenAI services)
            default_model: Default model to use
            client: Optional pre-configured client (for testing)
        """
        self.default_model = default_model
        self.client = client or AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    async def generate_completion(self,
                                 messages: List[Dict[str, str]],
                                 model: Optional[str] = None,
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate a completion using the OpenAI API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            Dictionary containing the response
        """
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return {
            "content": response.choices[0].message.content,
            "role": "assistant",
            "model": response.model,
            "raw_response": response
        }
