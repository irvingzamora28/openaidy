"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A chat message."""
    role: str = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completion."""
    messages: List[Message] = Field(..., description="The messages to generate a completion for")
    model: Optional[str] = Field(None, description="The model to use for completion")
    temperature: float = Field(0.7, description="Controls randomness (0-1)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion."""
    role: str = Field(..., description="The role of the message sender (usually 'assistant')")
    content: str = Field(..., description="The generated completion")
    model: str = Field(..., description="The model used for completion")


class ChatCompletionChunk(BaseModel):
    """Response model for streaming chat completion chunks."""
    role: str = Field(..., description="The role of the message sender (usually 'assistant')")
    content: str = Field(..., description="The accumulated content so far")
    content_delta: str = Field(..., description="The new content in this chunk")
    model: str = Field(..., description="The model used for completion")
    finished: bool = Field(False, description="Whether this is the final chunk")
