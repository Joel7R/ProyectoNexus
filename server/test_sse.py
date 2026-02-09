import httpx
import json
import asyncio

async def test_sse():
    url = "http://localhost:8000/api/chat/stream"
    payload = {
        "message": "Últimas noticias de Elden Ring",
        "session_id": "test-session"
    }
    
    print(f"Connecting to {url}...")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Status Code: {response.status_code}")
                async for line in response.aiter_lines():
                    if line:
                        print(f"Received: {line}")
                        if "done" in line or "response" in line:
                            break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_sse())
