
import os
import asyncio
try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# Hardcoded key
API_KEY = "AIzaSyAn_nJ7G_I5cYNyOmk4KSmRWnJ_6RQ6ojc"

async def verify_flash_8b():
    print(f"Connecting to Gemini API (v1beta) with key: {API_KEY[:5]}...")
    
    try:
        # Force v1beta
        client = Client(api_key=API_KEY, http_options={'api_version': 'v1beta'})
        
        # 1.5 Flash 8B
        model_name = "models/gemini-1.5-flash-8b"
        print(f"Attempting to generate content with '{model_name}'...")
        
        response = client.models.generate_content(
            model=model_name,
            contents="Say exactly: HELLO WORLD"
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ FAILED with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_flash_8b())
