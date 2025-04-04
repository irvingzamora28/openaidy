"""
Integration tests for the FastAPI application.
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_health_check(test_client):
    """Test the health check endpoint."""
    # Act
    response = test_client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.parametrize("provider", ["openai", "google-genai", "deepseek", "ollama"])
def test_chat_completions_with_different_providers(test_client, monkeypatch, provider):
    """Test the chat completions endpoint with different providers."""
    # Arrange
    # Set environment variables
    monkeypatch.setenv("LLM_API_PROVIDER", provider)
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    if provider in ["deepseek", "ollama"]:
        monkeypatch.setenv("LLM_API_URL", "https://test-url.com/v1")

    # Create a mock provider instance
    mock_instance = MagicMock()
    mock_instance.generate_completion = AsyncMock(return_value={
        "content": f"Response from {provider}",
        "role": "assistant",
        "model": "test-model"
    })

    # Mock the provider factory to return our mock provider
    monkeypatch.setattr(
        "backend.api.routes.create_llm_provider_from_env",
        lambda: mock_instance
    )

    # Act
    response = test_client.post(
        "/api/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ]
        }
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["role"] == "assistant"
    assert result["content"] == f"Response from {provider}"
    assert result["model"] == "test-model"


def test_chat_completions_with_invalid_request(test_client):
    """Test the chat completions endpoint with an invalid request."""
    # Act
    response = test_client.post(
        "/api/chat/completions",
        json={
            # Missing required 'messages' field
            "temperature": 0.7
        }
    )

    # Assert
    assert response.status_code == 422  # Unprocessable Entity


def test_chat_completions_with_server_error(test_client, monkeypatch):
    """Test the chat completions endpoint when there's a server error."""
    # Arrange
    # Mock the provider factory to raise an exception
    monkeypatch.setattr(
        "backend.api.routes.create_llm_provider_from_env",
        lambda: exec('raise ValueError("Test error")')
    )

    # Act
    response = test_client.post(
        "/api/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "Hello, world!"}
            ]
        }
    )

    # Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "Test error"
