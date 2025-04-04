"""
Google Gemini LLM provider.
"""
from typing import Dict, List, Optional, Any, AsyncGenerator
import google.generativeai as genai
from .base import LLMProvider
from ..utils.text_formatter import format_llm_response


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini API"""

    def __init__(self, api_key: str, default_model: str = "gemini-pro", genai_module=None):
        """
        Initialize the Google Gemini provider.

        Args:
            api_key: API key for authentication
            default_model: Default model to use
            genai_module: Optional pre-configured genai module (for testing)
        """
        self.default_model = default_model
        self.genai = genai_module or genai
        if not genai_module:
            self.genai.configure(api_key=api_key)

    async def generate_completion(self,
                                 messages: List[Dict[str, str]],
                                 model: Optional[str] = None,
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate a completion using the Google Gemini API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Returns:
            Dictionary containing the response
        """
        # Convert messages to Google's format
        # Google Gemini uses a different format than OpenAI
        gemini_model = self.genai.GenerativeModel(
            model_name=model or self.default_model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
        )

        # Create a chat session
        chat = gemini_model.start_chat()

        # Process messages
        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                # For user messages, we send them to the chat
                response = await chat.send_message_async(content)
            # We don't need to handle assistant messages as they're part of the chat history

        # Get the raw content
        raw_content = response.text

        # Format the content for better readability
        formatted_content = format_llm_response(raw_content)

        # Return the last response
        return {
            "content": formatted_content,
            "role": "assistant",
            "model": model or self.default_model,
            "raw_response": response
        }

    async def generate_completion_stream(self,
                                       messages: List[Dict[str, str]],
                                       model: Optional[str] = None,
                                       temperature: float = 0.7,
                                       max_tokens: Optional[int] = None,
                                       **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion using the Google Gemini API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Gemini-specific parameters

        Yields:
            Dictionaries containing partial responses
        """
        # Convert messages to Google's format
        gemini_model = self.genai.GenerativeModel(
            model_name=model or self.default_model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                **kwargs
            }
        )

        # Create a chat session
        chat = gemini_model.start_chat()

        # Process all previous messages to build context
        last_user_message = None
        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                # Store the last user message for streaming
                last_user_message = content
                # For all but the last user message, send normally
                if message != messages[-1]:
                    await chat.send_message_async(content)

        # If there's no user message, we can't stream
        if last_user_message is None:
            raise ValueError("No user message found for streaming")

        # Stream the response to the last user message
        stream = await chat.send_message_async(last_user_message, stream=True)

        full_content = ""

        async for chunk in stream:
            # Extract the content from the chunk
            if not hasattr(chunk, 'text') or chunk.text is None:
                continue

            # Append to the full content
            content_delta = chunk.text
            full_content += content_delta

            # Format the content for better readability
            formatted_content = format_llm_response(full_content)

            yield {
                "content": formatted_content,
                "content_delta": content_delta,
                "role": "assistant",
                "model": model or self.default_model,
                "finished": False
            }

        # Final yield with the complete content
        yield {
            "content": format_llm_response(full_content),
            "content_delta": "",
            "role": "assistant",
            "model": model or self.default_model,
            "finished": True
        }
