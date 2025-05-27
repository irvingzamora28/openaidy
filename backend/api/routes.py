"""
API routes for the backend.
"""
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, AsyncGenerator
import json

from .models import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChunk
from ..llm.factory import create_llm_provider_from_env
from ..llm.base import LLMProvider

router = APIRouter()

from openaidy_agents.playwright_orchestrator_agent import run_orchestrator
from pydantic import BaseModel
from fastapi import Body

class ReviewAnalysisRequest(BaseModel):
    url: str

class ReviewAnalysisResponse(BaseModel):
    navigation_result: dict
    snapshot_result: dict
    element_discovery: dict
    click_result: dict
    post_click_snapshot: dict
    load_more_click_results: list
    load_more_snapshots: list
    extracted_reviews: list
    review_analysis: list

async def event_generator(url: str):
    """Generate server-sent events for the review analysis process"""
    try:
        # Send initial progress update
        yield {"event": "progress", "data": "Starting review analysis..."}
        
        # Create a queue to collect progress updates
        progress_queue = asyncio.Queue()
        
        async def run_orchestrator_with_progress():
            """Run the orchestrator and send progress updates"""
            try:
                # This would be called from within the orchestrator to send updates
                async def update_progress(message: str):
                    await progress_queue.put({"event": "progress", "data": message})
                
                # Run the actual orchestrator with progress callback
                result = await run_orchestrator(url, progress_callback=update_progress)
                await progress_queue.put({"event": "complete", "data": result})
            except Exception as e:
                await progress_queue.put({"event": "error", "data": str(e)})
        
        # Start the orchestrator in the background
        task = asyncio.create_task(run_orchestrator_with_progress())
        
        # Process updates from the queue
        while True:
            try:
                # Wait for the next update with a timeout
                try:
                    update = await asyncio.wait_for(progress_queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    yield {"event": "progress", "data": "Still processing, please wait..."}
                    continue
                    
                # Send the update
                yield update
                
                # If this was the final update, we're done
                if update["event"] in ("complete", "error"):
                    if update["event"] == "error":
                        raise HTTPException(status_code=500, detail=update["data"])
                    break
                    
            except Exception as e:
                yield {"event": "error", "data": str(e)}
                break
                
    except Exception as e:
        yield {"event": "error", "data": str(e)}

# Store active SSE streams
active_streams = {}

@router.post("/reviews/analyze")
async def analyze_reviews(request: ReviewAnalysisRequest):
    """
    Start a review analysis job.
    
    This endpoint starts a background task to analyze reviews and returns a stream URL
    that the client can connect to for progress updates.
    
    Request body should be a JSON object with a 'url' field.
    """
    import uuid
    from fastapi.background import BackgroundTasks
    
    # Generate a unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    stream_url = f"/api/reviews/stream/{analysis_id}"
    
    # Create a queue to collect progress updates
    progress_queue = asyncio.Queue()
    active_streams[analysis_id] = progress_queue
    
    # Start the analysis in the background
    async def run_analysis():
        try:
            # Run the orchestrator and capture the results
            results = await run_orchestrator(
                request.url,
                progress_callback=lambda msg: asyncio.create_task(progress_queue.put({"event": "progress", "data": msg}))
            )
            # Send the complete event with the full results
            await progress_queue.put({
                "event": "complete",
                "data": {
                    "status": "completed",
                    "results": results
                }
            })
        except Exception as e:
            await progress_queue.put({"event": "error", "data": str(e)})
        finally:
            # Clean up after completion
            await asyncio.sleep(5)  # Give client time to receive final message
            if analysis_id in active_streams:
                del active_streams[analysis_id]
    
    asyncio.create_task(run_analysis())
    
    # Return the stream URL to the client
    return {"stream_url": stream_url}

@router.get("/reviews/stream/{analysis_id}")
async def stream_reviews(analysis_id: str):
    """
    Stream progress updates for a review analysis job.
    
    This endpoint streams Server-Sent Events (SSE) with progress updates
    for the specified analysis job.
    """
    if analysis_id not in active_streams:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    progress_queue = active_streams[analysis_id]
    
    async def event_generator():
        try:
            while True:
                update = await progress_queue.get()
                if update["event"] in ("complete", "error"):
                    # This is the final message, clean up after sending
                    if analysis_id in active_streams:
                        del active_streams[analysis_id]
                yield f"data: {json.dumps(update)}\n\n"
                if update["event"] in ("complete", "error"):
                    break
        except asyncio.CancelledError:
            # Client disconnected
            pass
        except Exception as e:
            print(f"Error in event generator: {e}")
        finally:
            # Clean up if not already done
            if analysis_id in active_streams:
                del active_streams[analysis_id]
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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
