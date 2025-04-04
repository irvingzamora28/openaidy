"""
Base class for LLM providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_completion(self,
                                 messages: List[Dict[str, str]],
                                 model: Optional[str] = None,
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None,
                                 **kwargs) -> Dict[str, Any]:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary containing the response
        """
        pass

    @abstractmethod
    async def generate_completion_stream(self,
                                       messages: List[Dict[str, str]],
                                       model: Optional[str] = None,
                                       temperature: float = 0.7,
                                       max_tokens: Optional[int] = None,
                                       **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate a streaming completion from the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Optional model override (defaults to configured model)
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            AsyncGenerator yielding dictionaries containing partial responses
        """
        pass
