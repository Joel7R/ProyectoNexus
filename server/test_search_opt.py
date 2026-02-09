import httpx
import json
import asyncio

async def test_search():
    url = "http://localhost:8000/api/chat/stream"
    payload = {
        "message": "best weapons for each character in Expedition 33 guide",
        "session_id": "test-expedition"
    }
    
    print(f"Testing Expedition 33 query...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data = json.loads(line[5:])
                        if data.get("type") == "thinking":
                            print(f"Thinking: {data['content']}")
                        elif data.get("type") == "response":
                            print(f"\nResponse: {data['content']}")
                            if data.get("artifact"):
                                print(f"Artifact Title: {data['artifact']['title']}")
                                if "steps" in data["artifact"].get("content", {}):
                                    print(f"Found {len(data['artifact']['content']['steps'])} steps.")
                        elif data.get("type") == "done":
                            break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())
