
import os
import asyncio
from dotenv import load_dotenv

try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# Manually load the hardcoded key just in case, but rely on .env usually
# But user said .env is unreliable, so let's match the hardcoded one from llm_config
API_KEY = "AIzaSyAn_nJ7G_I5cYNyOmk4KSmRWnJ_6RQ6ojc"

async def debug_v1():
    print(f"Connecting to Gemini API (v1) with key: {API_KEY[:5]}...")
    
    try:
        # Force v1
        client = Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        print("\nAttempting to list models with v1...")
        count = 0
        for m in client.models.list(config={'page_size': 100}):
            print(f" - {m.name}")
            if "gemini-1.5-pro" in m.name:
                print(f"   ^-- FOUND IT! (Supports: {m.supported_generation_methods})")
            count += 1
            
        if count == 0:
            print("⚠️ No models returned. Check API Key or Quota.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_v1())
