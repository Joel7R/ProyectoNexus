import asyncio
import os
import sys

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.web_search import live_web_search

async def test_news():
    print("Testing live_web_search with 'news'...")
    try:
        results = await live_web_search("Elden Ring", search_type="news")
        print(f"Results found: {len(results)}")
        if results:
            print(f"First result: {results[0]}")
    except Exception as e:
        print(f"Error in live_web_search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_news())
