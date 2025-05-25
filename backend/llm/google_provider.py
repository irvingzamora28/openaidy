"""
Google Gemini LLM provider.
"""
from typing import Dict, List, Optional, Any, AsyncGenerator
import logging
from google import genai
from google.genai import types
from .base import LLMProvider
from ..utils.text_formatter import format_llm_response


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini API"""

    def __init__(self, api_key: str, default_model: str = "gemini-pro", genai_module=None):
        logging.info(f"Initializing GoogleProvider with api_key={api_key[:6]}... and model={default_model}")
        """
        Initialize the Google Gemini provider (new SDK pattern).

        Args:
            api_key: API key for authentication
            default_model: Default model to use
            genai_module: Optional pre-configured genai module (for testing)
        """
        self.default_model = default_model
        # Use the provided module for testing, otherwise use the real one
        self.genai = genai_module or genai
        # Create a sync and async client
        if genai_module and hasattr(genai_module, 'Client'):
            self.client = genai_module.Client(api_key=api_key)
            self.async_client = genai_module.Client(api_key=api_key).aio
        else:
            self.client = genai.Client(api_key=api_key)
            self.async_client = self.client.aio

    def generate_completion(self,
                           messages: List[Dict[str, str]],
                           model: Optional[str] = None,
                           temperature: float = 0.7,
                           max_tokens: Optional[int] = None,
                           **kwargs) -> Dict[str, Any]:
        logging.info(f"GoogleProvider.generate_completion called with model={model}, temp={temperature}, max_tokens={max_tokens}, messages={messages}")
        """
        Generate a completion using the Google Gemini API (new SDK).

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Dictionary containing the response
        """
        # Prepare the contents argument according to new SDK rules
        user_contents = []
        for message in messages:
            if message["role"] == "user":
                user_contents.append(message["content"])
        if not user_contents:
            raise ValueError("No user message found for completion")
        # The latest user message is the one to generate on
        last_user_message = user_contents[-1]
        context_messages = user_contents[:-1]
        contents = context_messages + [last_user_message]

        # Build config
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs
        )
        model_name = model or self.default_model
        try:
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            logging.info(f"GoogleProvider.generate_completion response: {response}")
            return {
                "content": format_llm_response(response.text),
                "role": "assistant",
                "model": model_name
            }
        except Exception as e:
            logging.error(f"Error in GoogleProvider.generate_completion: {e}")
            raise


    async def generate_completion_stream(self,
                                       messages: List[Dict[str, str]],
                                       model: Optional[str] = None,
                                       temperature: float = 0.7,
                                       max_tokens: Optional[int] = None,
                                       **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        logging.info(f"GoogleProvider.generate_completion_stream called with model={model}, temp={temperature}, max_tokens={max_tokens}, messages={messages}")
        """
        Generate a streaming completion using the Google Gemini API (new SDK).

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Yields:
            Dictionaries containing partial responses
        """
        # Prepare the contents argument according to new SDK rules
        # Concatenate user and assistant messages as a single string for context
        user_contents = []
        for message in messages:
            if message["role"] == "user":
                user_contents.append(message["content"])
        if not user_contents:
            raise ValueError("No user message found for streaming")
        # The latest user message is the one to stream on
        last_user_message = user_contents[-1]
        # Previous messages as context (if needed)
        context_messages = user_contents[:-1]

        # Build config
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs
        )

        # Use the async streaming API from the new SDK
        # Note: self.genai should be a genai.Client instance
        model_name = model or self.default_model
        client = self.genai.aio if hasattr(self.genai, 'aio') else self.genai

        # Combine context and last message if needed
        # The SDK supports a list of strings as contents
        contents = context_messages + [last_user_message]

        # Start streaming
        full_content = ""
        try:
            # Use self.async_client for streaming
            models_obj = self.async_client.models
            if not hasattr(models_obj, "generate_content_stream"):
                logging.error(f"generate_content_stream is missing! models_obj dir: {dir(models_obj)}")
                raise AttributeError("google.genai.models has no attribute 'generate_content_stream'")
            async for chunk in await models_obj.generate_content_stream(
                model=model_name,
                contents=contents,
                config=config
            ):
                if not hasattr(chunk, 'text') or chunk.text is None:
                    continue
                content_delta = chunk.text
                full_content += content_delta
                formatted_content = format_llm_response(full_content)
                yield {
                    "content": formatted_content,
                    "content_delta": content_delta,
                    "role": "assistant",
                    "model": model_name,
                    "finished": False
                }
            # Final yield with the complete content
            yield {
                "content": format_llm_response(full_content),
                "content_delta": "",
                "role": "assistant",
                "model": model_name,
                "finished": True
            }
        except Exception as e:
            logging.error(f"Error in GoogleProvider.generate_completion_stream: {e}")
            raise
