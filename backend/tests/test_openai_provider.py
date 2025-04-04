"""
Tests for the OpenAI provider.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.llm.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_init():
    """Test OpenAI provider initialization."""
    # Arrange
    mock_client = AsyncMock()

    # Act
    provider = OpenAIProvider(api_key="test-key", default_model="test-model", client=mock_client)

    # Assert
    assert provider.default_model == "test-model"
    assert provider.client == mock_client


@pytest.mark.asyncio
async def test_openai_provider_init_with_base_url():
    """Test OpenAI provider initialization with base URL."""
    # Arrange
    mock_client = AsyncMock()

    # Act
    provider = OpenAIProvider(
        api_key="test-key",
        base_url="https://test-url.com",
        default_model="test-model",
        client=mock_client
    )

    # Assert
    assert provider.default_model == "test-model"
    assert provider.client == mock_client


@pytest.mark.asyncio
async def test_openai_provider_generate_completion():
    """Test OpenAI provider generate_completion method."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello, world!"}
    ]

    # Create mock response
    mock_message = AsyncMock()
    mock_message.content = "Hello, human!"

    mock_choice = AsyncMock()
    mock_choice.message = mock_message

    mock_completion = AsyncMock()
    mock_completion.choices = [mock_choice]
    mock_completion.model = "test-model"

    # Create mock client
    mock_completions = AsyncMock()
    mock_completions.create = AsyncMock(return_value=mock_completion)

    mock_chat = AsyncMock()
    mock_chat.completions = mock_completions

    mock_client = AsyncMock()
    mock_client.chat = mock_chat

    # Create provider with mocked client
    provider = OpenAIProvider(api_key="test-key", default_model="test-model", client=mock_client)

    # Act
    response = await provider.generate_completion(messages)

    # Assert
    mock_completions.create.assert_called_once_with(
        model="test-model",
        messages=messages,
        temperature=0.7,
        max_tokens=None
    )
    assert response["content"] == "Hello, human!"
    assert response["role"] == "assistant"
    assert response["model"] == "test-model"
    assert "raw_response" in response


@pytest.mark.asyncio
async def test_openai_provider_generate_completion_with_params():
    """Test OpenAI provider generate_completion with custom parameters."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello, world!"}
    ]

    # Create mock response
    mock_message = AsyncMock()
    mock_message.content = "Hello, human!"

    mock_choice = AsyncMock()
    mock_choice.message = mock_message

    mock_completion = AsyncMock()
    mock_completion.choices = [mock_choice]
    mock_completion.model = "custom-model"

    # Create mock client
    mock_completions = AsyncMock()
    mock_completions.create = AsyncMock(return_value=mock_completion)

    mock_chat = AsyncMock()
    mock_chat.completions = mock_completions

    mock_client = AsyncMock()
    mock_client.chat = mock_chat

    # Create provider with mocked client
    provider = OpenAIProvider(api_key="test-key", default_model="default-model", client=mock_client)

    # Act
    response = await provider.generate_completion(
        messages,
        model="custom-model",
        temperature=0.5,
        max_tokens=100,
        top_p=0.9
    )

    # Assert
    mock_completions.create.assert_called_once_with(
        model="custom-model",
        messages=messages,
        temperature=0.5,
        max_tokens=100,
        top_p=0.9
    )
    assert response["content"] == "Hello, human!"
    assert response["role"] == "assistant"
    assert response["model"] == "custom-model"
    assert "raw_response" in response
