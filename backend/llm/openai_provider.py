"""
OpenAI-compatible LLM provider.
This provider works with OpenAI, DeepSeek, and other OpenAI API-compatible services.
"""
from typing import Dict, List, Optional, Any, AsyncGenerator

from openai import AsyncOpenAI
from .base import LLMProvider
from ..utils.text_formatter import format_llm_response


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

        # Get the raw content
        raw_content = response.choices[0].message.content

        # Format the content for better readability
        formatted_content = format_llm_response(raw_content)

        return {
            "content": formatted_content,
            "role": "assistant",
            "model": response.model,
            "raw_response": response
        }

    async def generate_completion_stream(self,
                                       messages: List[Dict[str, str]],
                                       model: Optional[str] = None,
                                       temperature: float = 0.7,
                                       max_tokens: Optional[int] = None,
                                       **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion using the OpenAI API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific parameters

        Yields:
            Dictionaries containing partial responses
        """
        stream = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,  # Enable streaming
            **kwargs
        )

        full_content = ""
        model_name = ""

        async for chunk in stream:
            # Extract the content from the chunk
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Get model name from the first chunk
            if not model_name and hasattr(chunk, 'model'):
                model_name = chunk.model

            # Skip chunks without content
            if not hasattr(delta, 'content') or delta.content is None:
                continue

            # Append to the full content
            content_delta = delta.content
            full_content += content_delta

            # Format the content for better readability
            formatted_content = format_llm_response(full_content)

            yield {
                "content": formatted_content,
                "content_delta": content_delta,
                "role": "assistant",
                "model": model_name or model or self.default_model,
                "finished": False
            }

        # Final yield with the complete content
        yield {
            "content": format_llm_response(full_content),
            "content_delta": "",
            "role": "assistant",
            "model": model_name or model or self.default_model,
            "finished": True
        }
