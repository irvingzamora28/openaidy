"""
Tests for streaming functionality.
"""
import os
import sys
import pytest
import json
from unittest.mock import AsyncMock, MagicMock

# Add the project root directory to the Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import models needed for testing


@pytest.mark.asyncio
async def test_create_chat_completion_stream(mock_llm_provider):
    """Test streaming chat completion endpoint."""
    from backend.api.routes import create_chat_completion_stream
    from backend.api.models import ChatCompletionRequest, Message

    # Arrange
    request = ChatCompletionRequest(
        messages=[
            Message(role="user", content="Hello, world!")
        ],
        temperature=0.7
    )

    # Set up the mock to yield a specific sequence
    async def mock_stream(*args, **kwargs):
        yield {
            "content": "Hello",
            "content_delta": "Hello",
            "role": "assistant",
            "model": "test-model",
            "finished": False
        }
        yield {
            "content": "Hello, human!",
            "content_delta": ", human!",
            "role": "assistant",
            "model": "test-model",
            "finished": True
        }

    mock_llm_provider.generate_completion_stream = mock_stream

    # Act
    response = await create_chat_completion_stream(request, mock_llm_provider)

    # Assert
    assert response.media_type == "text/event-stream"

    # Collect the streamed content
    chunks = []
    async for chunk in response.body_iterator:
        # Convert bytes to string if needed
        if isinstance(chunk, bytes):
            chunk = chunk.decode('utf-8')

        if chunk.startswith('data: '):
            data = json.loads(chunk.replace('data: ', ''))
            chunks.append(data)

    # Verify we got the expected chunks
    assert len(chunks) == 2
    assert chunks[0]["content"] == "Hello"
    assert chunks[0]["content_delta"] == "Hello"
    assert chunks[0]["finished"] is False

    assert chunks[1]["content"] == "Hello, human!"
    assert chunks[1]["content_delta"] == ", human!"
    assert chunks[1]["finished"] is True


@pytest.mark.asyncio
async def test_openai_provider_streaming():
    """Test OpenAI provider streaming functionality."""
    from backend.llm.openai_provider import OpenAIProvider

    # Create mock response chunks
    class MockChunk1:
        def __init__(self):
            self.choices = [MagicMock()]
            self.choices[0].delta = MagicMock()
            self.choices[0].delta.content = "Hello"
            self.model = "test-model"

    class MockChunk2:
        def __init__(self):
            self.choices = [MagicMock()]
            self.choices[0].delta = MagicMock()
            self.choices[0].delta.content = ", world!"
            self.model = "test-model"

    # Create a proper async iterator for our mock stream
    class MockAsyncIterator:
        def __init__(self, items):
            self.items = items
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index < len(self.items):
                item = self.items[self.index]
                self.index += 1
                return item
            raise StopAsyncIteration

    # Create mock stream as an async iterator
    mock_stream = MockAsyncIterator([MockChunk1(), MockChunk2()])

    # Mock the OpenAI client
    mock_completions = AsyncMock()
    mock_completions.create = AsyncMock(return_value=mock_stream)

    mock_chat = AsyncMock()
    mock_chat.completions = mock_completions

    mock_client = AsyncMock()
    mock_client.chat = mock_chat

    # Create provider with mocked client
    provider = OpenAIProvider(api_key="test-key", default_model="test-model", client=mock_client)

    # Test the streaming method
    messages = [{"role": "user", "content": "Test message"}]
    chunks = []

    async for chunk in provider.generate_completion_stream(messages):
        chunks.append(chunk)

    # Verify the chunks
    assert len(chunks) == 3  # 2 content chunks + 1 final chunk

    assert chunks[0]["content_delta"] == "Hello"
    assert chunks[0]["content"] == "Hello"
    assert chunks[0]["finished"] is False

    assert chunks[1]["content_delta"] == ", world!"
    assert chunks[1]["content"] == "Hello, world!"
    assert chunks[1]["finished"] is False

    assert chunks[2]["content"] == "Hello, world!"
    assert chunks[2]["finished"] is True


@pytest.mark.asyncio
async def test_google_provider_streaming():
    """Test Google provider streaming functionality."""
    from backend.llm.google_provider import GoogleProvider

    # Create mock response chunks
    class MockChunk1:
        def __init__(self):
            self.text = "Hello"

    class MockChunk2:
        def __init__(self):
            self.text = ", world!"

    # Create a proper async iterator for our mock stream
    class MockAsyncIterator:
        def __init__(self, items):
            self.items = items
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index < len(self.items):
                item = self.items[self.index]
                self.index += 1
                return item
            raise StopAsyncIteration

    # Create mock stream as an async iterator
    mock_stream = MockAsyncIterator([MockChunk1(), MockChunk2()])

    # Mock the chat session
    mock_chat = MagicMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_stream)

    # Mock the generative model
    mock_model = MagicMock()
    mock_model.start_chat = MagicMock(return_value=mock_chat)

    # Mock genai module
    mock_genai = MagicMock()
    mock_genai.GenerativeModel = MagicMock(return_value=mock_model)

    # Create provider with mocked dependencies
    provider = GoogleProvider(api_key="test-key", default_model="test-model", genai_module=mock_genai)

    # Test the streaming method
    messages = [{"role": "user", "content": "Test message"}]
    chunks = []

    async for chunk in provider.generate_completion_stream(messages):
        chunks.append(chunk)

    # Verify the chunks
    assert len(chunks) == 3  # 2 content chunks + 1 final chunk

    assert chunks[0]["content_delta"] == "Hello"
    assert chunks[0]["content"] == "Hello"
    assert chunks[0]["finished"] is False

    assert chunks[1]["content_delta"] == ", world!"
    assert chunks[1]["content"] == "Hello, world!"
    assert chunks[1]["finished"] is False

    assert chunks[2]["content"] == "Hello, world!"
    assert chunks[2]["finished"] is True
