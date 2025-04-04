"""
API routes for the backend.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
import json

from .models import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk
from ..llm.factory import create_llm_provider_from_env
from ..llm.base import LLMProvider

router = APIRouter()


async def get_llm_provider() -> LLMProvider:
    """
    Dependency to get the LLM provider from environment variables.

    Returns:
        LLMProvider: The configured LLM provider

    Raises:
        HTTPException: If there's an error creating the provider
    """
    try:
        return create_llm_provider_from_env()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    request: ChatCompletionRequest,
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Generate a chat completion using the configured LLM provider.

    Args:
        request: The chat completion request
        llm_provider: The LLM provider (injected dependency)

    Returns:
        ChatCompletionResponse: The generated completion

    Raises:
        HTTPException: If there's an error generating the completion
    """
    try:
        # Convert Pydantic models to dictionaries
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Generate completion
        response = await llm_provider.generate_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Return formatted response
        return ChatCompletionResponse(
            role=response["role"],
            content=response["content"],
            model=response["model"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/completions/stream")
async def create_chat_completion_stream(
    request: ChatCompletionRequest,
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    """
    Generate a streaming chat completion using the configured LLM provider.

    Args:
        request: The chat completion request
        llm_provider: The LLM provider (injected dependency)

    Returns:
        StreamingResponse: A streaming response with SSE format

    Raises:
        HTTPException: If there's an error generating the completion
    """
    try:
        # Convert Pydantic models to dictionaries
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        async def event_generator():
            try:
                # Generate streaming completion
                async for chunk in llm_provider.generate_completion_stream(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    # Convert chunk to ChatCompletionChunk model
                    response_chunk = ChatCompletionChunk(
                        role=chunk["role"],
                        content=chunk["content"],
                        content_delta=chunk["content_delta"],
                        model=chunk["model"],
                        finished=chunk["finished"]
                    )

                    # Format as SSE
                    yield f"data: {json.dumps(response_chunk.model_dump())}\n\n"
            except Exception as e:
                # Send error as SSE
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
