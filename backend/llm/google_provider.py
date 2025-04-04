"""
Google Gemini LLM provider.
"""
import os
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from .base import LLMProvider


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini API"""
    
    def __init__(self, api_key: str, default_model: str = "gemini-pro"):
        """
        Initialize the Google Gemini provider.
        
        Args:
            api_key: API key for authentication
            default_model: Default model to use
        """
        self.default_model = default_model
        genai.configure(api_key=api_key)
    
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
        gemini_model = genai.GenerativeModel(
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
        
        # Return the last response
        return {
            "content": response.text,
            "role": "assistant",
            "model": model or self.default_model,
            "raw_response": response
        }
