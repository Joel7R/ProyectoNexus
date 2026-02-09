"""
Gaming Nexus - Live Web Agent System
FastAPI server with SSE streaming for real-time agent responses
"""
import os
import json
import asyncio
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from agents.graph import GamingNexusGraph
from agents.state import ConversationState

load_dotenv()

# Global state for conversation histories
conversation_states: dict[str, ConversationState] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    print("Gaming Nexus Server Starting...")
    print(f"Using Ollama model: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
    yield
    print("Gaming Nexus Server Shutting Down...")

app = FastAPI(
    title="Gaming Nexus API",
    description="Live Web Agent System for Gaming Assistance",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development to avoid CORS issues
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: str = "default"


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # 'user', 'assistant', 'system', 'thinking'
    content: str
    artifact: dict | None = None
    sources: list[dict] | None = None


async def stream_agent_response(
    message: str, 
    session_id: str
) -> AsyncGenerator[dict, None]:
    """Stream agent responses as SSE events"""
    
    print(f"Iniciando stream para sesion: {session_id}")
    # Get or create conversation state
    if session_id not in conversation_states:
        print(f"Creando nueva sesion: {session_id}")
        conversation_states[session_id] = ConversationState()
    
    state = conversation_states[session_id]
    state.add_message("user", message)
    
    # Initialize the agent graph
    graph = GamingNexusGraph()
    
    try:
        # Stream events from the agent
        async for event in graph.astream(message, state):
            yield {"data": json.dumps(event, ensure_ascii=False)}
            await asyncio.sleep(0.01)  # Small delay for smooth streaming
        
        # Send completion event
        yield {"data": json.dumps({"type": "done"}, ensure_ascii=False)}
        
    except Exception as e:
        import traceback
        error_msg = f"Error en el agente: {str(e)}"
        print(f"Error: {error_msg}")
        traceback.print_exc()
        
        yield {"data": json.dumps({"type": "error", "content": error_msg}, ensure_ascii=False)}
        await asyncio.sleep(0.1)  # Ensure event is sent before closing


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses using Server-Sent Events.
    Allows real-time visualization of agent thinking process.
    """
    print(f"Nueva solicitud de chat: {request.session_id}")
    return EventSourceResponse(
        stream_agent_response(request.message, request.session_id),
        media_type="text/event-stream",
        ping=5  # Send a ping every 5 seconds to keep connection alive
    )


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversation_states:
        return {"messages": []}
    
    state = conversation_states[session_id]
    return {"messages": state.get_messages()}


@app.delete("/api/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_states:
        del conversation_states[session_id]
    return {"status": "cleared"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
