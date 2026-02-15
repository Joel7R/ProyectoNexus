
import os
import re
import asyncio
from google.genai import Client

# Hardcoded key
API_KEY = "AIzaSyAn_nJ7G_I5cYNyOmk4KSmRWnJ_6RQ6ojc"
CONFIG_FILE = "llm_config.py"

async def find_and_configure():
    versions = ["v1", "v1beta"]
    
    print(f"🔎 Starting Inventory Scan with Key: {API_KEY[:5]}...\n")
    
    for version in versions:
        print(f"--- Checking API Version: {version} ---")
        try:
            client = Client(api_key=API_KEY, http_options={'api_version': version})
            
            # List models
            print("   Requesting model list...")
            try:
                # The SDK list method returns an iterator or list of models
                # We need to handle potential differences in exact return type
                models_pager = client.models.list() 
                models = list(models_pager)
            except Exception as e:
                print(f"   ❌ Failed to list models on {version}: {e}")
                continue

            print(f"   Found {len(models)} models.")
            
            for m in models:
                # m is likely an object with .name, .supported_generation_methods, etc.
                # Inspect structure if needed, but assuming standard attributes
                name = m.name if hasattr(m, 'name') else str(m)
                
                # Filter for useful models (generative)
                if "gemini" not in name.lower():
                    continue
                    
                print(f"   👉 Testing: {name}")
                
                try:
                    response = client.models.generate_content(
                        model=name,
                        contents="Return code 200"
                    )
                    
                    if response and response.text:
                        print(f"   ✅ SUCCESS! {name} works on {version}.")
                        update_config(name, version)
                        return
                except Exception as e:
                    reason = str(e)
                    if "404" in reason: status = "404 Not Found"
                    elif "429" in reason: status = "429 Quota Exceeded"
                    else: status = f"Error: {reason[:50]}..."
                    print(f"      ❌ {status}")
                    
        except Exception as e:
            print(f"   ❌ Error initializing client for {version}: {e}")

    print("\n❌ CRITICAL: No working model found in any version.")

def update_config(model_name, api_version):
    print(f"\n📝 Updating {CONFIG_FILE}...")
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update Model String
        # Regex to find: self.config.model_gemini = "..."
        new_content = re.sub(
            r'self\.config\.model_gemini\s*=\s*["\'].*?["\']', 
            f'self.config.model_gemini = "{model_name}"', 
            content
        )
        
        # Update API Version
        # Regex to find: http_options={'api_version': '...'}
        new_content = re.sub(
            r"http_options=\{['\"]api_version['\"]\s*:\s*['\"].*?['\"]\}", 
            f"http_options={{'api_version': '{api_version}'}}", 
            new_content
        )
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("✅ Configuration updated successfully!")
        
    except Exception as e:
        print(f"❌ Failed to update config file: {e}")

if __name__ == "__main__":
    asyncio.run(find_and_configure())
