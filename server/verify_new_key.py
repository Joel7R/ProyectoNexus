
import os
import asyncio
try:
    from google.genai import Client
except ImportError:
    print("❌ ERROR: google-genai library not found.")
    exit(1)

# New API Key
API_KEY = "AIzaSyAJ4DZ_mRsD4fcHVJbw0Hf93g5hJrLIiq0"

async def verify_new_key():
    print(f"Connecting to Gemini API (v1) with NEW key: {API_KEY[:5]}...")
    
    try:
        # Force v1
        client = Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        # Validated model
        model_name = "models/gemini-2.5-flash"
        print(f"Attempting to generate content with '{model_name}'...")
        
        response = client.models.generate_content(
            model=model_name,
            contents="Say exactly: NEW KEY WORKING"
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ FAILED with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_new_key())
