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
from agents.news_scout import NewsScoutAgent
from agents.time_estimator import TimeEstimatorAgent
from agents.deal_scout import DealScoutAgent
from agents.chronos import ChronosAgent

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


# Valid categories for news
VALID_CATEGORIES = ["general", "patches", "releases", "esports"]

class NewsRequest(BaseModel):
    category: str = "general"
    limit: int = 6

@app.post("/api/news")
async def get_gaming_news(request: NewsRequest):
    """Get latest gaming news using NewsScout Agent"""
    print(f"Fetching news for category: {request.category}")
    
    agent = NewsScoutAgent()
    
    # Map category to search query
    queries = {
        "general": "latest major gaming news headlines today",
        "patches": "new game updates and patch notes this week",
        "releases": "new video game releases this week",
        "esports": "major esports tournament results and news today"
    }
    
    query = queries.get(request.category, queries["general"])
    
    # Use the agent to search
    # We pass "Global" as game context for general news
    result = await agent.search(game="Gaming Industry", query=query)
    
    # Transform result for frontend
    news_items = []
    
    # Try to extract items from artifact if structured (Preferred method)
    if result.artifact and isinstance(result.artifact, dict) and result.artifact.get("rows"):
        for item in result.artifact["rows"]:
            news_items.append({
                "title": item.get("title", "News Item"),
                "date": item.get("date", "Recently"),
                "summary": item.get("description", result.summary[:100] + "..."),
                "url": item.get("url", "#"),
                "source_lang": item.get("source_lang", "en"), # Default to 'en' if missing
                "image": None 
            })
    else:
        # Fallback to sources list
        for i, source in enumerate(result.sources):
            news_items.append({
                "title": source.get("title", "News Item"),
                "date": "Today", 
                "summary": result.summary[:100] + "...", 
                "url": source.get("url", "#"),
                "source_lang": "en",
                "image": None 
            })
        
    return {
        "summary": result.summary,
        "items": news_items if news_items else []
    }

# ============= TIME2PLAY ENDPOINTS =============

class HLTBRequest(BaseModel):
    """Request for single game time estimation"""
    game_name: str

class BacklogRequest(BaseModel):
    """Request for backlog calculation"""
    games: list[str]

class MarathonRequest(BaseModel):
    """Request for marathon mode calculation"""
    game_name: str
    hours_per_day: float

# ============= PRICE HUNTER MODELS =============

class DealSearchRequest(BaseModel):
    """Request for price search"""
    game_name: str

class DealCompareRequest(BaseModel):
    """Request for price comparison"""
    game_name: str
    store_ids: list[str]

# ============= LORE MASTER MODELS =============

class LoreRequest(BaseModel):
    """Request for game lore"""
    game_name: str
    spoiler_level: str = "light"  # none, light, full

class CharacterMapRequest(BaseModel):
    """Request for character relationships"""
    game_name: str

@app.post("/api/hltb/game")
async def get_game_time(request: HLTBRequest):
    """Get completion time estimates for a single game"""
    print(f"HLTB request for: {request.game_name}")
    
    agent = TimeEstimatorAgent()
    result = await agent.estimate_game_time(request.game_name)
    
    return result

@app.post("/api/hltb/backlog")
async def calculate_backlog(request: BacklogRequest):
    """Calculate total time for multiple games"""
    print(f"Backlog calculation for {len(request.games)} games")
    
    agent = TimeEstimatorAgent()
    result = await agent.calculate_backlog(request.games)
    
    return result

@app.post("/api/hltb/marathon")
async def marathon_mode(request: MarathonRequest):
    """Calculate days to complete based on hours per day"""
    print(f"Marathon mode for {request.game_name} @ {request.hours_per_day}h/day")
    
    agent = TimeEstimatorAgent()
    result = await agent.marathon_mode(request.game_name, request.hours_per_day)
    
    return result

# ============= END TIME2PLAY ENDPOINTS =============

# ============= PRICE HUNTER ENDPOINTS =============

@app.post("/api/deals/search")
async def search_deals(request: DealSearchRequest):
    """Search for game prices across all stores"""
    print(f"Price search for: {request.game_name}")
    
    agent = DealScoutAgent()
    result = await agent.search_deals(request.game_name)
    
    return result

@app.post("/api/deals/compare")
async def compare_deals(request: DealCompareRequest):
    """Compare prices for specific stores"""
    print(f"Price comparison for: {request.game_name} across {len(request.store_ids)} stores")
    
    agent = DealScoutAgent()
    result = await agent.compare_stores(request.game_name, request.store_ids)
    
    return result

# ============= END PRICE HUNTER ENDPOINTS =============

# ============= LORE MASTER ENDPOINTS =============

@app.post("/api/lore/story")
async def get_game_lore(request: LoreRequest):
    """Get game story with spoiler control"""
    print(f"Lore request for: {request.game_name} (spoiler level: {request.spoiler_level})")
    
    agent = ChronosAgent()
    result = await agent.get_story(request.game_name, request.spoiler_level)
    
    return result

@app.post("/api/lore/characters")
async def get_character_map(request: CharacterMapRequest):
    """Get character relationships"""
    print(f"Character map for: {request.game_name}")
    
    agent = ChronosAgent()
    result = await agent.get_character_map(request.game_name)
    
    return result

# ============= END LORE MASTER ENDPOINTS =============



@app.get("/api/calendar")
async def get_upcoming_games():
    """Get upcoming game releases"""
    print("Fetching upcoming games...")
    
    # We can use NewsScout or a specialized routine here.
    # For simplicity, we use NewsScout with a specific query for now.
    agent = NewsScoutAgent()
    
    query = "upcoming video game releases next 3 months dates"
    result = await agent.search(game="Upcoming Games", query=query)
    
    # Return the raw result for now, frontend will need to adapt or we parse here
    # A real implementation would parse the dates strictly.
    # For this 'MVP', we return the summary and let the frontend display it, 
    # or we try to structure it if the agent was successful.
    
    return {
        "summary": result.summary,
        "raw_data": result.sources
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
