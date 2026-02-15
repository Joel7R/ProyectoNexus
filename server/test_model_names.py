
import os
import asyncio
from dotenv import load_dotenv

try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

async def test_models():
    client = Client(api_key=api_key)
    
    models_to_test = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001"
    ]
    
    print(f"Testing models with key: {api_key[:5]}...")
    
    for model in models_to_test:
        print(f"\nTesting model name: '{model}'")
        try:
            response = client.models.generate_content(model=model, contents="Test")
            print(f"✅ SUCCESS: {model}")
            # print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ FAILED: {model} -> {e}")

if __name__ == "__main__":
    asyncio.run(test_models())
