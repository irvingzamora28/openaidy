"""
Tests for the Google Gemini provider.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.llm.google_provider import GoogleProvider


@pytest.mark.asyncio
async def test_google_provider_init():
    """Test Google provider initialization."""
    # Arrange
    mock_genai = AsyncMock()

    # Act
    provider = GoogleProvider(api_key="test-key", default_model="test-model", genai_module=mock_genai)

    # Assert
    assert provider.default_model == "test-model"
    assert provider.genai == mock_genai
    # Should not call configure when genai_module is provided
    mock_genai.configure.assert_not_called()


@pytest.mark.asyncio
async def test_google_provider_generate_completion():
    """Test Google provider generate_completion method."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello, world!"}
    ]

    # Mock the response
    mock_response = AsyncMock()
    mock_response.text = "Hello, human!"

    # Mock chat session
    mock_chat = AsyncMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    # Mock generative model
    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    # Mock genai module
    mock_genai = AsyncMock()
    # Use MagicMock instead of AsyncMock for GenerativeModel
    mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

    # Create provider with mocked dependencies
    provider = GoogleProvider(api_key="test-key", default_model="test-model", genai_module=mock_genai)

    # Act
    response = await provider.generate_completion(messages)

    # Assert
    mock_genai.GenerativeModel.assert_called_once_with(
        model_name="test-model",
        generation_config={
            "temperature": 0.7,
            "max_output_tokens": None
        }
    )
    mock_model.start_chat.assert_called_once()
    mock_chat.send_message_async.assert_called_once_with("Hello, world!")

    # The content should be the original text, possibly with some formatting
    assert response["content"] == "Hello, human!"
    assert response["role"] == "assistant"
    assert response["model"] == "test-model"
    assert "raw_response" in response


@pytest.mark.asyncio
async def test_google_provider_generate_completion_with_params():
    """Test Google provider generate_completion with custom parameters."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello, world!"}
    ]

    # Mock the response
    mock_response = AsyncMock()
    mock_response.text = "Hello, human!"

    # Mock chat session
    mock_chat = AsyncMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    # Mock generative model
    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    # Mock genai module
    mock_genai = AsyncMock()
    # Use MagicMock instead of AsyncMock for GenerativeModel
    mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

    # Create provider with mocked dependencies
    provider = GoogleProvider(api_key="test-key", default_model="default-model", genai_module=mock_genai)

    # Act
    response = await provider.generate_completion(
        messages,
        model="custom-model",
        temperature=0.5,
        max_tokens=100,
        top_k=40
    )

    # Assert
    mock_genai.GenerativeModel.assert_called_once_with(
        model_name="custom-model",
        generation_config={
            "temperature": 0.5,
            "max_output_tokens": 100,
            "top_k": 40
        }
    )
    mock_model.start_chat.assert_called_once()
    mock_chat.send_message_async.assert_called_once_with("Hello, world!")

    # The content should be the original text, possibly with some formatting
    assert response["content"] == "Hello, human!"
    assert response["role"] == "assistant"
    assert response["model"] == "custom-model"
    assert "raw_response" in response


@pytest.mark.asyncio
async def test_google_provider_multiple_messages():
    """Test Google provider with multiple messages."""
    # Arrange
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"},
        {"role": "user", "content": "How are you?"}
    ]

    # Mock the response
    mock_response = AsyncMock()
    mock_response.text = "I'm doing well, thanks for asking!"

    # Mock chat session
    mock_chat = AsyncMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    # Mock generative model
    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    # Mock genai module
    mock_genai = AsyncMock()
    # Use MagicMock instead of AsyncMock for GenerativeModel
    mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

    # Create provider with mocked dependencies
    provider = GoogleProvider(api_key="test-key", default_model="test-model", genai_module=mock_genai)

    # Act
    response = await provider.generate_completion(messages)

    # Assert
    # Should only send the user messages to the chat
    assert mock_chat.send_message_async.call_count == 2
    mock_chat.send_message_async.assert_any_call("Hello")
    mock_chat.send_message_async.assert_any_call("How are you?")

    # The content should be the original text, possibly with some formatting
    assert response["content"] == "I'm doing well, thanks for asking!"
    assert response["role"] == "assistant"
    assert response["model"] == "test-model"
    assert "raw_response" in response
