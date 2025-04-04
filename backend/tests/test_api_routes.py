"""
Tests for the API routes.
"""
import os
import sys
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.api.routes import get_llm_provider, create_chat_completion
from backend.api.models import ChatCompletionRequest, Message


@pytest.mark.asyncio
async def test_get_llm_provider_success():
    """Test get_llm_provider when successful."""
    # Arrange
    mock_provider = AsyncMock()

    # Act
    with patch("backend.api.routes.create_llm_provider_from_env", return_value=mock_provider):
        provider = await get_llm_provider()

        # Assert
        assert provider == mock_provider


@pytest.mark.asyncio
async def test_get_llm_provider_error():
    """Test get_llm_provider when there's an error."""
    # Arrange
    with patch("backend.api.routes.create_llm_provider_from_env",
               side_effect=ValueError("Test error")):
        # Act & Assert
        with pytest.raises(HTTPException) as excinfo:
            await get_llm_provider()

        assert excinfo.value.status_code == 500
        assert excinfo.value.detail == "Test error"


@pytest.mark.asyncio
async def test_create_chat_completion_success(mock_llm_provider):
    """Test create_chat_completion when successful."""
    # Arrange
    request = ChatCompletionRequest(
        messages=[
            Message(role="user", content="Hello, world!")
        ],
        temperature=0.7
    )

    mock_llm_provider.generate_completion_mock.return_value = {
        "content": "Hello, human!",
        "role": "assistant",
        "model": "test-model"
    }

    # Act
    response = await create_chat_completion(request, mock_llm_provider)

    # Assert
    # Check that generate_completion was called with the right arguments
    # The first argument should be the messages list
    args, kwargs = mock_llm_provider.generate_completion_mock.call_args
    assert len(args) > 0
    assert args[0] == [{"role": "user", "content": "Hello, world!"}]
    assert kwargs.get("temperature") == 0.7
    assert kwargs.get("model") is None
    assert kwargs.get("max_tokens") is None

    assert response.role == "assistant"
    assert response.content == "Hello, human!"
    assert response.model == "test-model"


@pytest.mark.asyncio
async def test_create_chat_completion_with_model(mock_llm_provider):
    """Test create_chat_completion with a specified model."""
    # Arrange
    request = ChatCompletionRequest(
        messages=[
            Message(role="user", content="Hello, world!")
        ],
        model="custom-model",
        temperature=0.5,
        max_tokens=100
    )

    mock_llm_provider.generate_completion_mock.return_value = {
        "content": "Hello, human!",
        "role": "assistant",
        "model": "custom-model"
    }

    # Act
    response = await create_chat_completion(request, mock_llm_provider)

    # Assert
    # Check that generate_completion was called with the right arguments
    args, kwargs = mock_llm_provider.generate_completion_mock.call_args
    assert len(args) > 0
    assert args[0] == [{"role": "user", "content": "Hello, world!"}]
    assert kwargs.get("temperature") == 0.5
    assert kwargs.get("model") == "custom-model"
    assert kwargs.get("max_tokens") == 100

    assert response.role == "assistant"
    assert response.content == "Hello, human!"
    assert response.model == "custom-model"


@pytest.mark.asyncio
async def test_create_chat_completion_error(mock_llm_provider):
    """Test create_chat_completion when there's an error."""
    # Arrange
    request = ChatCompletionRequest(
        messages=[
            Message(role="user", content="Hello, world!")
        ]
    )

    mock_llm_provider.generate_completion_mock.side_effect = Exception("Test error")

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await create_chat_completion(request, mock_llm_provider)

    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Test error"
