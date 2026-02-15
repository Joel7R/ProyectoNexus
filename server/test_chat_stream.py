import asyncio
import httpx
import json

async def test_chat_stream():
    url = "http://localhost:8000/api/chat/stream"
    payload = {
        "message": "Hola Nexus, ¿qué juegos me recomiendas para este fin de semana?",
        "session_id": "test_debug_stream"
    }
    
    print(f"--- Posting to {url} ---")
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                print(f"Status: {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            print(f"\n[RECEIVED CHUNK]: {json.dumps(data, indent=2, ensure_ascii=False)}")
                            if data.get("type") == "done":
                                break
                        except:
                            print(f"\n[RAW DATA ERR]: {data_str}")
        except Exception as e:
            print(f"\n[ERROR]: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_stream())
