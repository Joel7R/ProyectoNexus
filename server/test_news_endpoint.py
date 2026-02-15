import asyncio
import httpx

async def test_news_cache():
    url = "http://localhost:8000/api/news"
    payload = {"category": "general", "limit": 6}
    
    print("--- First Call (Fetching) ---")
    async with httpx.AsyncClient() as client:
        try:
            resp1 = await client.post(url, json=payload, timeout=30.0)
            print(f"Status 1: {resp1.status_code}")
            
            print("\n--- Second Call (Should be Cache Hit) ---")
            resp2 = await client.post(url, json=payload, timeout=5.0)
            print(f"Status 2: {resp2.status_code}")
            
            if resp1.status_code == 200 and resp2.status_code == 200:
                print("\n[SUCCESS] News endpoint test completed.")
            else:
                print("\n[FAILED] One or more requests failed.")
        except Exception as e:
            print(f"\n[ERROR] Ensure server is running on port 8000. {e}")

if __name__ == "__main__":
    asyncio.run(test_news_cache())
