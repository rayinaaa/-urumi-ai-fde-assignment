import asyncio
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import orchestrator

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str = Field(default="default-session", description="Unique conversation session identifier")
    message: str = Field(..., description="User prompt or inquiry for the agent")

class TraceItem(BaseModel):
    tool: str
    arguments: Dict[str, Any]
    result: Any
    duration_ms: float

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    traces: List[TraceItem] = []
    timestamp: float

@router.post("/message", response_model=ChatResponse)
async def handle_message(payload: ChatRequest):
    """Executes an agent turn and returns the full assistant reply with tool traces."""
    result = await orchestrator.execute_turn(
        session_id=payload.session_id,
        user_prompt=payload.message
    )
    return ChatResponse(
        session_id=result["session_id"],
        reply=result["reply"],
        traces=result.get("traces", []),
        timestamp=result["timestamp"]
    )

@router.post("/stream")
async def stream_message(payload: ChatRequest):
    """Streams agent tokens and tool execution traces over Server-Sent Events (SSE)."""
    async def event_generator():
        yield f"event: thinking\ndata: {json.dumps({'status': 'Analyzing query and consulting MCP tools...'})}\n\n"
        await asyncio.sleep(0.05)

        result = await orchestrator.execute_turn(
            session_id=payload.session_id,
            user_prompt=payload.message
        )

        for trace in result.get("traces", []):
            yield f"event: tool_call\ndata: {json.dumps(trace)}\n\n"
            await asyncio.sleep(0.02)

        # Stream words in chunks for typing effect
        words = result["reply"].split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + (" " if i+3 < len(words) else "")
            yield f"event: token\ndata: {json.dumps({'token': chunk})}\n\n"
            await asyncio.sleep(0.02)

        yield f"event: done\ndata: {json.dumps({'session_id': payload.session_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
