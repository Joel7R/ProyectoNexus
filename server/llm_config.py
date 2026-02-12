import os
import json
from typing import Literal, Optional
from dataclasses import dataclass
import google.generativeai as genai
import ollama

from dotenv import load_dotenv

# Load environment variables immediately
load_dotenv()

# Configure persistence file
CONFIG_FILE = "config.json"

@dataclass
class LLMConfig:
    provider: Literal["ollama", "gemini"] = "ollama"
    api_key: Optional[str] = None
    model_ollama: str = "llama3.2"
    model_gemini: str = "gemini-pro"

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
        self._initialized = True
    
    def _load_config(self):
        """Load configuration from file or env"""
        # Load from file if exists
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.config.provider = data.get("provider", "ollama")
                    self.config.api_key = data.get("api_key")
                    self.config.model_ollama = data.get("model_ollama", "llama3.2")
                    self.config.model_gemini = data.get("model_gemini", "gemini-pro")
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Override with env vars if not set in config (first run or env var priority)
        # Override with env vars (priority over config file for OLLAMA_MODEL if env is set)
        env_model = os.getenv("OLLAMA_MODEL")
        if env_model:
             self.config.model_ollama = env_model
             
        # Load API key from env if not in config
        if not self.config.api_key:
            self.config.api_key = os.getenv("GEMINI_API_KEY")
    
    def save_config(self):
        """Save current configuration to file"""
        data = {
            "provider": self.config.provider,
            "api_key": self.config.api_key,
            "model_ollama": self.config.model_ollama,
            "model_gemini": self.config.model_gemini
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_settings(self, provider: str, api_key: str = None):
        """Update LLM settings"""
        if provider in ["ollama", "gemini"]:
            self.config.provider = provider
        
        if api_key is not None:
             self.config.api_key = api_key
            
        self.save_config()
        
    def get_settings(self):
        """Get current settings (masking API key)"""
        return {
            "provider": self.config.provider,
            "has_key": bool(self.config.api_key),
            "model": self.config.model_gemini if self.config.provider == "gemini" else self.config.model_ollama
        }

    async def chat(self, messages: list, format: str = None) -> str:
        """Unified chat interface for both providers"""
        
        if self.config.provider == "gemini":
            if not self.config.api_key:
                raise ValueError("Gemini API key not configured")
                
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(self.config.model_gemini)
            
            # Convert messages to Gemini format
            # Gemini expects history + last message
            # For simplicity in this one-shot style usage:
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            if format == "json":
                prompt += "\n\nRESPONSE MUST BE VALID JSON."
                generation_config = {"response_mime_type": "application/json"}
                response = await model.generate_content_async(prompt, generation_config=generation_config)
            else:
                response = await model.generate_content_async(prompt)
                
            return response.text
            
        else:
            # Ollama (Default)
            client = ollama.Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
            response = await client.chat(
                model=self.config.model_ollama,
                messages=messages,
                format=format
            )
            return response['message']['content']

# Global instance
llm_manager = LLMManager()
