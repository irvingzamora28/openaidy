"""
Pytest configuration file.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app
from backend.llm.base import LLMProvider


@pytest.fixture
def test_client():
    """
    Create a test client for the FastAPI application.
    """
    return TestClient(app)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self):
        self.generate_completion_mock = AsyncMock()
        self.generate_completion_mock.return_value = {
            "content": "This is a mock response",
            "role": "assistant",
            "model": "mock-model"
        }

    async def generate_completion(self,
                                 messages,
                                 model=None,
                                 temperature=0.7,
                                 max_tokens=None,
                                 **kwargs):
        """Mock implementation that delegates to the mock."""
        return await self.generate_completion_mock(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


@pytest.fixture
def mock_llm_provider():
    """
    Create a mock LLM provider for testing.
    """
    return MockLLMProvider()


@pytest.fixture
def mock_env_vars():
    """
    Set up mock environment variables for testing.
    """
    original_env = os.environ.copy()

    # Set default test environment variables
    os.environ["LLM_API_PROVIDER"] = "openai"
    os.environ["LLM_API_KEY"] = "test-api-key"
    os.environ["LLM_MODEL"] = "test-model"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_openai_client():
    """
    Create a mock for the OpenAI client.
    """
    with patch("openai.AsyncOpenAI") as mock_client:
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content="This is a mock OpenAI response"))
        ]
        mock_response.model = "gpt-3.5-turbo"

        # Set up the chat completions create method
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        yield mock_client


@pytest.fixture
def mock_google_genai():
    """
    Create a mock for the Google Gemini API.
    """
    with patch("google.generativeai") as mock_genai:
        # Set up the mock response
        mock_response = AsyncMock()
        mock_response.text = "This is a mock Gemini response"

        # Set up the chat session
        mock_chat = AsyncMock()
        mock_chat.send_message_async = AsyncMock(return_value=mock_response)

        # Set up the generative model
        mock_model = AsyncMock()
        mock_model.start_chat = AsyncMock(return_value=mock_chat)

        # Set up the GenerativeModel constructor
        mock_genai.GenerativeModel = AsyncMock(return_value=mock_model)

        yield mock_genai
