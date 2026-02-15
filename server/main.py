"""
Gaming Nexus - Live Web Agent System
FastAPI server with SSE streaming for real-time agent responses
"""
import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import utilities and services
from server.utils.logger import logger
from server.services.llm_service import llm_service
from server.database.connection import db_manager

# Import Routes
from server.routes import health, chat, news, deals, lore

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup"""
    logger.info("AI Engine: Gemini 2.5 Flash (Stable)")
    
    # Initialize LLM Service check
    health_status = llm_service.check_health()
    logger.info(f"LLM Service Status: {health_status}")

    yield
    
    logger.info("Gaming Nexus Server Shutting Down...")

app = FastAPI(
    title="Gaming Nexus API",
    description="Live Web Agent System for Gaming Assistance",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix="/api", tags=["System"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(deals.router, prefix="/api/deals", tags=["Deals"])
app.include_router(lore.router, prefix="/api/lore", tags=["Lore"])

@app.get("/")
async def root():
    """Root endpoint to verify server is running"""
    return {
        "message": "Gaming Nexus API is running (Refactored)",
        "health": "/api/health",
        "frontend": "http://localhost:4200",
        "doc": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
