
import os
import asyncio
try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# Hardcoded key
API_KEY = "AIzaSyA628pOW1C66r4a_HFzC2WXxU5aCatZ1bU"

async def verify_flash():
    print(f"Connecting to Gemini API (v1) with key: {API_KEY[:5]}...")
    
    try:
        # Force v1
        client = Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        # 2.0 Flash
        model_name = "models/gemini-2.0-flash"
        print(f"Attempting to generate content with '{model_name}'...")
        
        response = client.models.generate_content(
            model=model_name,
            contents="Respond with '200 OK'"
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ FAILED with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_flash())
