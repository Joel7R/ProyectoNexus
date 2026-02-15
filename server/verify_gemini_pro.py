
import os
import asyncio
try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# Hardcoded key just to be absolutely sure
API_KEY = "AIzaSyA628pOW1C66r4a_HFzC2WXxU5aCatZ1bU"

async def verify_pro():
    print(f"Connecting to Gemini API (v1) with key: {API_KEY[:5]}...")
    
    try:
        # Force v1, no extra headers
        client = Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        # Validated model from debug list
        model_name = "models/gemini-2.5-pro"
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
    asyncio.run(verify_pro())
