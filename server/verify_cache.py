import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'server'))

from agents.news_scout import NewsScoutAgent
from utils.cache_manager import cache_manager
from unittest.mock import AsyncMock, patch

async def test_caching():
    agent = NewsScoutAgent()
    
    # Mock LLM and Search to avoid external calls and errors
    with patch('agents.news_scout.live_web_search', new_callable=AsyncMock) as mock_search, \
         patch.object(agent.llm, 'chat', new_callable=AsyncMock) as mock_chat:
        
        mock_search.return_value = [{"title": "Test News", "url": "http://test.com"}]
        mock_chat.return_value = '{"summary": "Test Summary", "news_items": []}'
        
        print("--- First Call (Cache Miss) ---")
        await agent.search("test", "news")
        
        print("\n--- Second Call (Cache Hit) ---")
        await agent.search("test", "news")

if __name__ == "__main__":
    asyncio.run(test_caching())
