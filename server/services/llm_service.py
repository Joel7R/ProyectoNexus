import os
import asyncio
import json
import re
from typing import Optional, List, Dict, Any
from google.genai import Client
from dotenv import load_dotenv
from server.utils.logger import logger

load_dotenv()

class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Fallback hardcoded key if env var fails (Temporary Fix)
        if not self.api_key:
             self.api_key = "AIzaSyAJ4DZ_mRsD4fcHVJbw0Hf93g5hJrLIiq0"
             logger.warning("Using hardcoded API Key as fallback.")

        self.model_name = "models/gemini-2.5-flash"
        self.client = None
        self._setup_client()
        self._initialized = True

    def _setup_client(self):
        try:
            if self.api_key:
                self.client = Client(api_key=self.api_key, http_options={'api_version': 'v1'})
                logger.info(f"LLM Service initialized with model: {self.model_name}")
            else:
                logger.error("No API Key found for LLM Service.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Client: {e}")

    async def generate_response(self, prompt: str, history: List[Dict[str, str]] = None, format: str = None) -> str:
        """
        Generates a response from the LLM. 
        Falls back to a mock response if the API call fails.
        """
        if not self.client:
            logger.warning("LLM Client not available. Returning mock response.")
            return self._get_mock_response(prompt)

        try:
            # Construct strict prompt
            combined_prompt = "Eres Nexus, un asistente experto en videojuegos. Responde de forma concisa.\n\n"
            if history:
                for msg in history[-10:]:
                    role = "Usuario" if msg.get("role") == "user" else "Nexus"
                    combined_prompt += f"{role}: {msg.get('content')}\n"
            
            combined_prompt += f"Usuario: {prompt}\nNexus:"

            if format == "json":
                combined_prompt += "\n\nResponde exclusivamente en formato JSON válido."

            logger.info(f"Sending request to {self.model_name}...")
            
            # Execute in thread pool to keep async loop unblocked
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=combined_prompt
                )
            )

            text = response.text
            if format == "json":
                text = self._clean_json(text)
            
            return text if text else "Nexus no devolvió texto."

        except Exception as e:
            logger.error(f"LLM Generation Failed: {e}")
            return self._get_mock_response(prompt)

    def _get_mock_response(self, prompt: str) -> str:
        """Returns a safe fallback response."""
        logger.info("Serving Mock Response.")
        return "⚠️ [MODO SIMULACIÓN] Nexus está experimentando problemas de conexión. Intenta más tarde."

    def _clean_json(self, text: str) -> str:
        """Cleans JSON output from Markdown."""
        if "```json" in text:
            text = re.sub(r"```json\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
        elif "```" in text:
            text = re.sub(r"```\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
        return text.strip()

    def check_health(self) -> Dict[str, Any]:
        """Checks the health of the LLM service."""
        return {
            "status": "online" if self.client else "offline",
            "model": self.model_name,
            "has_key": bool(self.api_key)
        }

# Global instance
llm_service = LLMService()
