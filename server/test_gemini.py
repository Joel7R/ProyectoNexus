
import os
import asyncio
from dotenv import load_dotenv

# Try importing the new SDK as llm_config does
try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: No API key found in .env")
    exit(1)

async def test_genai():
    print(f"Testing google.genai SDK with key: {api_key[:5]}...")
    
    try:
        # Test 1: Gemini 2.0 Flash Lite (No API Version constraint)
        print("\nTest 1: Gemini 2.0 Flash Lite (Default/Auto)")
        client = Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents="Hello 2.0")
        print(f"✅ 2.0 Flash Lite Response: {response.text}")
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")

    try:
        # Test 2: Gemini 2.5 Flash (Stable)
        print("\nTest 2: Gemini 2.5 Flash (Stable)")
        client = Client(api_key=api_key, http_options={'api_version': 'v1'})
        response = client.models.generate_content(model="models/gemini-2.5-flash", contents="Hello 2.5")
        print(f"✅ 2.5 Flash Response: {response.text}")
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_genai())
