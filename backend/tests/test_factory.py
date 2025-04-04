"""
Tests for the LLM provider factory.
"""
import os
import sys
import pytest
from unittest.mock import patch

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.llm.factory import create_llm_provider, create_llm_provider_from_env
from backend.llm.openai_provider import OpenAIProvider
from backend.llm.google_provider import GoogleProvider


def test_create_llm_provider_openai():
    """Test creating an OpenAI provider."""
    # Arrange & Act
    with patch("backend.llm.factory.OpenAIProvider") as mock_provider:
        provider = create_llm_provider(
            provider="openai",
            api_key="test-key",
            model="test-model"
        )

        # Assert
        mock_provider.assert_called_once_with(
            api_key="test-key",
            default_model="test-model"
        )


def test_create_llm_provider_deepseek():
    """Test creating a DeepSeek provider."""
    # Arrange & Act
    with patch("backend.llm.factory.OpenAIProvider") as mock_provider:
        provider = create_llm_provider(
            provider="deepseek",
            api_key="test-key",
            model="test-model",
            api_url="https://api.deepseek.com/v1"
        )

        # Assert
        mock_provider.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.deepseek.com/v1",
            default_model="test-model"
        )


def test_create_llm_provider_ollama():
    """Test creating an Ollama provider."""
    # Arrange & Act
    with patch("backend.llm.factory.OpenAIProvider") as mock_provider:
        provider = create_llm_provider(
            provider="ollama",
            api_key="test-key",
            model="test-model",
            api_url="http://localhost:11434/v1"
        )

        # Assert
        mock_provider.assert_called_once_with(
            api_key="test-key",
            base_url="http://localhost:11434/v1",
            default_model="test-model"
        )


def test_create_llm_provider_google():
    """Test creating a Google provider."""
    # Arrange & Act
    with patch("backend.llm.factory.GoogleProvider") as mock_provider:
        provider = create_llm_provider(
            provider="google-genai",
            api_key="test-key",
            model="test-model"
        )

        # Assert
        mock_provider.assert_called_once_with(
            api_key="test-key",
            default_model="test-model"
        )


def test_create_llm_provider_unsupported():
    """Test creating an unsupported provider."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
        create_llm_provider(
            provider="unsupported",
            api_key="test-key",
            model="test-model"
        )


def test_create_llm_provider_case_insensitive():
    """Test that provider names are case-insensitive."""
    # Arrange & Act
    with patch("backend.llm.factory.OpenAIProvider") as mock_provider:
        provider = create_llm_provider(
            provider="OpEnAi",  # Mixed case
            api_key="test-key",
            model="test-model"
        )

        # Assert
        mock_provider.assert_called_once()


def test_create_llm_provider_from_env(mock_env_vars):
    """Test creating a provider from environment variables."""
    # Arrange
    os.environ["LLM_API_PROVIDER"] = "openai"
    os.environ["LLM_API_KEY"] = "test-key"
    os.environ["LLM_MODEL"] = "test-model"

    # Act
    with patch("backend.llm.factory.create_llm_provider") as mock_create:
        provider = create_llm_provider_from_env()

        # Assert
        mock_create.assert_called_once_with(
            "openai", "test-key", "test-model", None
        )


def test_create_llm_provider_from_env_with_url(mock_env_vars):
    """Test creating a provider from environment variables with URL."""
    # Arrange
    os.environ["LLM_API_PROVIDER"] = "deepseek"
    os.environ["LLM_API_KEY"] = "test-key"
    os.environ["LLM_MODEL"] = "test-model"
    os.environ["LLM_API_URL"] = "https://api.deepseek.com/v1"

    # Act
    with patch("backend.llm.factory.create_llm_provider") as mock_create:
        provider = create_llm_provider_from_env()

        # Assert
        mock_create.assert_called_once_with(
            "deepseek", "test-key", "test-model", "https://api.deepseek.com/v1"
        )


def test_create_llm_provider_from_env_missing_provider(mock_env_vars):
    """Test error when LLM_API_PROVIDER is missing."""
    # Arrange
    os.environ.pop("LLM_API_PROVIDER", None)

    # Act & Assert
    with pytest.raises(ValueError, match="LLM_API_PROVIDER environment variable is required"):
        create_llm_provider_from_env()


def test_create_llm_provider_from_env_missing_api_key(mock_env_vars):
    """Test error when LLM_API_KEY is missing."""
    # Arrange
    os.environ.pop("LLM_API_KEY", None)

    # Act & Assert
    with pytest.raises(ValueError, match="LLM_API_KEY environment variable is required"):
        create_llm_provider_from_env()


def test_create_llm_provider_from_env_missing_model(mock_env_vars):
    """Test error when LLM_MODEL is missing."""
    # Arrange
    os.environ.pop("LLM_MODEL", None)

    # Act & Assert
    with pytest.raises(ValueError, match="LLM_MODEL environment variable is required"):
        create_llm_provider_from_env()


def test_create_llm_provider_from_env_missing_url_for_deepseek(mock_env_vars):
    """Test error when LLM_API_URL is missing for DeepSeek."""
    # Arrange
    os.environ["LLM_API_PROVIDER"] = "deepseek"
    os.environ.pop("LLM_API_URL", None)

    # Act & Assert
    with pytest.raises(ValueError, match="LLM_API_URL environment variable is required for deepseek"):
        create_llm_provider_from_env()


def test_create_llm_provider_from_env_missing_url_for_ollama(mock_env_vars):
    """Test error when LLM_API_URL is missing for Ollama."""
    # Arrange
    os.environ["LLM_API_PROVIDER"] = "ollama"
    os.environ.pop("LLM_API_URL", None)

    # Act & Assert
    with pytest.raises(ValueError, match="LLM_API_URL environment variable is required for ollama"):
        create_llm_provider_from_env()
