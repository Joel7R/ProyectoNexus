from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import json
import asyncio

from server.services.llm_service import llm_service
from server.database.connection import db_manager
from server.utils.logger import logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

async def stream_agent_response(message: str, session_id: str) -> AsyncGenerator[dict, None]:
    """Streams the LLM response to the client."""
    logger.info(f"Starting chat stream for: {session_id}")
    
    # Store user message
    session = db_manager.get_session(session_id)
    session["messages"].append({"role": "user", "content": message})
    
    try:
        # Get response from LLM Service
        response_text = await llm_service.generate_response(message, session["messages"])
        
        # Store assistant message
        session["messages"].append({"role": "assistant", "content": response_text})
        
        # Structure for frontend
        final_event = {
            "type": "message",
            "role": "assistant",
            "content": response_text
        }
        
        logger.debug(f"Streaming response: {json.dumps(final_event, ensure_ascii=False)[:100]}...")
        yield {"data": json.dumps(final_event, ensure_ascii=False)}
        yield {"data": json.dumps({"type": "done"}, ensure_ascii=False)}
        
    except Exception as e:
        logger.error(f"Chat Stream Error: {e}")
        yield {"data": json.dumps({"type": "error", "content": str(e)}, ensure_ascii=False)}

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat responses using Server-Sent Events."""
    return EventSourceResponse(
        stream_agent_response(request.message, request.session_id),
        media_type="text/event-stream",
        ping=5
    )

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history"""
    session = db_manager.get_session(session_id)
    return {"messages": session["messages"]}

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history"""
    db_manager.clear_session(session_id)
    return {"status": "cleared"}
