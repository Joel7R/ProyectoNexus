import os
import json
import re
import asyncio
from typing import Literal, Optional
from dataclasses import dataclass
try:
    from google.genai import Client
except ImportError:
    import sys
    print(f"ERROR: Libreria google-genai no encontrada en {sys.executable}")
    raise

from dotenv import load_dotenv

# Load environment variables immediately
load_dotenv()

# Configure persistence file
CONFIG_FILE = "config.json"

@dataclass
class LLMConfig:
    api_key: Optional[str] = None
    model_gemini: str = "models/gemini-2.5-flash"

class LLMManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self.config = LLMConfig()
        self._load_config()
        self.client = None
        if self.config.api_key:
            # Use default API version (v1beta/v1) determined by SDK
            # AGGRESSIVE DISPLAY
            print(f"[LLM] STARTUP WITH KEY: {self.config.api_key[:5]}... | Model: {self.config.model_gemini}")
            self.client = Client(api_key=self.config.api_key, http_options={'api_version': 'v1'})
        self._initialized = True
    
    def _load_config(self):
        """Load configuration from file or env"""
        # Hardcoded API Key as requested for temporal fix
        self.config.api_key = "AIzaSyAJ4DZ_mRsD4fcHVJbw0Hf93g5hJrLIiq0" 
        self.config.model_gemini = "models/gemini-2.5-flash" # Switched to 1.5 Flash 8B for quota bypass

    def save_config(self):
        # Disabled saving to avoid overwriting the hardcoded fix
        pass

    def update_settings(self, api_key: str = None):
        """Update LLM settings"""
        if api_key is not None:
             self.config.api_key = api_key
             self.client = Client(api_key=api_key, http_options={'api_version': 'v1'})
            
        # self.save_config() # Disabled
        
    def get_settings(self):
        """Get current settings (masking API key)"""
        return {
            "provider": "gemini",
            "has_key": bool(self.config.api_key),
            "model": self.config.model_gemini
        }

    async def quick_chat(self, prompt: str, session_id: str = "default", history: list = None) -> str:
        """
        TOTAL BYPASS: Direct chat with Gemini (Knowledge Base only)
        """
        # AGGRESSIVE HARDCODE
        api_key = "AIzaSyAJ4DZ_mRsD4fcHVJbw0Hf93g5hJrLIiq0"
        
        if not self.client:
            self.client = Client(api_key=api_key, http_options={'api_version': 'v1'})

        # Use the same logic as chat method for consistency
        combined_prompt = "Eres Nexus, un asistente experto en videojuegos. Responde de forma concisa.\n\n"
        if history:
            for msg in history[-10:]:
                role = "Usuario" if msg.get("role") == "user" else "Nexus"
                combined_prompt += f"{role}: {msg.get('content')}\n"
        
        combined_prompt += f"Usuario: {prompt}\nNexus:"

        # Simplified Model Logic for Gemini 2.5 Flash
        try:
            print(f"[LLM] Attempting connection with model: {self.config.model_gemini}")
            # Running synchronous call in executor to keep it async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.models.generate_content(
                    model=self.config.model_gemini,
                    contents=combined_prompt
                )
            )
            return response.text if response.text else "Nexus no devolvió texto."
            
        except Exception as e:
            err_str = str(e)
            print(f"[LLM] Primary model failed: {err_str}")
            return f"Lo siento, tuve un problema con la conexión directa (Error: {str(e)})"

    async def chat(self, messages: list, format: str = None) -> str:
        """Unified chat interface for Gemini 2.5 Flash with retries"""
        
        # AGGRESSIVE HARDCODE
        api_key = "AIzaSyAJ4DZ_mRsD4fcHVJbw0Hf93g5hJrLIiq0"
        
        if not self.client:
            self.client = Client(api_key=api_key, http_options={'api_version': 'v1'})
        
        # Prepare content
        combined_prompt = ""
        for m in messages:
            combined_prompt += f"{m['role']}: {m['content']}\n"
            
        config_dict = {}
        if format == "json":
            combined_prompt += "\n\nResponde exclusivamente en formato JSON válido. No incluyas explicaciones fuera del JSON."

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Running synchronous call in executor to keep it async
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.client.models.generate_content(
                        model=self.config.model_gemini,
                        contents=combined_prompt
                    )
                )
                
                text = response.text
                
                if format == "json":
                    # Remove markdown delimiters
                    if "```json" in text:
                        text = re.sub(r"```json\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
                    elif "```" in text:
                        text = re.sub(r"```\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
                    
                    # Robust extraction: find first { and last }
                    try:
                        start_idx = text.find('{')
                        end_idx = text.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            text = text[start_idx:end_idx+1]
                    except:
                        pass
                        
                    return text.strip()
                else:
                    return text
                    
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    # 429 Error: Reduce retries to just 1 to avoid long waits as requested
                    if attempt < 1: # Only retry once (attempt 0)
                        wait_time = 5 # Short wait
                        print(f"[LLM] Cuota 429. Reintento rápido en {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        # Fail fast after 1 retry
                        print(f"[LLM] Abortando por cuota 429 tras reintento.")
                        raise e 

                if "404" in err_str:
                    print(f"[LLM] 404 en chat(). No se reintentará.")
                    raise  # No reintentar en 404
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Gemini API Error (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"Gemini SDK Final Error: {e}")
                    raise

# Global instance
llm_manager = LLMManager()
