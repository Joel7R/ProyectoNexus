from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from server.utils.logger import logger
# Assuming agents are still in the original location for now, but we import them here
# If agents are not refactored yet, we import from server.agents but need to adjust path
import sys
import os

# Add parent directory to path to import agents if needed, strictly for now
# Ideally agents should be moved to services or kept as is but imported cleanly
from agents.news_scout import NewsScoutAgent 

router = APIRouter()

class NewsRequest(BaseModel):
    category: str = "general"
    limit: int = 6

@router.post("/")
async def get_gaming_news(request: NewsRequest):
    """Get latest gaming news"""
    logger.info(f"Fetching news for category: {request.category}")
    
    agent = NewsScoutAgent()
    query_map = {
        "general": "latest major gaming news headlines today",
        "patches": "new game updates and patch notes this week",
        "releases": "new video game releases this week",
        "esports": "major esports tournament results and news today"
    }
    
    query = query_map.get(request.category, query_map["general"])
    
    try:
        result = await agent.search(game="Gaming Industry", query=query)
        
        # Transform result (simplified logic from original main.py)
        news_items = []
        
        if result.artifact and isinstance(result.artifact, dict) and result.artifact.get("rows"):
            for item in result.artifact["rows"]:
                news_items.append({
                    "title": item.get("title", "News Item"),
                    "date": item.get("date", "Recently"),
                    "summary": item.get("description", result.summary[:100] + "..."),
                    "url": item.get("url", "#"),
                    "source_lang": item.get("source_lang", "en"),
                    "image": None
                })
        else:
             for source in result.sources:
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
            "items": news_items
        }
        
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        return {"summary": "Error fetching news", "items": []}
