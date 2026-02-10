"""
Intent Orchestrator Agent
Analyzes user prompts and routes to specialized agents
"""
import os
from typing import Literal
from dataclasses import dataclass

import ollama


SYSTEM_PROMPT = """Eres el Orquestador de 'Gaming Nexus', IA especialista en videojuegos.

TU OBJETIVO:
1. Analizar la intención del usuario.
2. Detectar el IDIOMA del usuario (es, en, fr, etc.).
3. Generar una `search_query` optimizada.

LOGICA DE BÚSQUEDA (CLR - Cross Language Retrieval):
- Si el usuario busca "builds", "parches", "stats", "tier list" o datos técnicos:
  GENERA LA `search_query` EN INGLÉS, independientemente del idioma del usuario.
  (Ej: User: "mejor build yasuo" -> Query: "Yasuo best build s14 guide")
  (Esto es vital para encontrar datos de calidad en wikis globales).

- Si el usuario busca "noticias" o "eventos":
  Mantén el idioma original para encontrar noticias locales, o usa inglés si busca fuentes primarias.

FORMATO JSON:
{
    "game": "nombre del juego o 'Gaming Industry' o 'REJECT'",
    "category": "news|build|guide",
    "version": "versión o null",
    "search_query": "query optimizada (EN para builds/tech, ES para noticias locales)",
    "language": "código iso (es, en)",
    "confidence": 0.0-1.0
}"""


@dataclass
class IntentResult:
    """Result of intent analysis"""
    game: str
    category: Literal["news", "build", "guide"]
    version: str | None
    search_query: str
    language: str
    confidence: float
    is_followup: bool = False


class IntentOrchestrator:
    """
    Analyzes user intent and routes to appropriate agent.
    Uses Ollama for local LLM inference.
    """
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    
    async def analyze(self, user_message: str, context: str = "") -> IntentResult:
        """Analyze user message and extract intent"""
        
        prompt = user_message
        if context:
            prompt = f"Contexto previo: {context}\n\nMensaje del usuario: {user_message}"
        
        try:
            import asyncio
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                format="json"
            )
            
            import json
            result = json.loads(response.message.content)
            
            is_followup = result.get("game", "").upper() == "FOLLOW_UP"
            
            return IntentResult(
                game=result.get("game", "Unknown"),
                category=result.get("category", "build"),
                version=result.get("version"),
                search_query=result.get("search_query", user_message),
                language=result.get("language", "es"),
                confidence=result.get("confidence", 0.5),
                is_followup=is_followup
            )
            
        except Exception as e:
            # Fallback: basic keyword extraction
            return self._fallback_analysis(user_message)
    
    def _fallback_analysis(self, message: str) -> IntentResult:
        """Fallback when LLM fails"""
        message_lower = message.lower()
        
        # Simple game detection
        games = {
            "lol": "League of Legends",
            "league": "League of Legends",
            "elden ring": "Elden Ring",
            "genshin": "Genshin Impact",
            "wow": "World of Warcraft",
            "valorant": "Valorant",
            "fortnite": "Fortnite"
        }
        
        detected_game = "Unknown"
        for key, value in games.items():
            if key in message_lower:
                detected_game = value
                break
        
        # Category detection
        category = "build"
        if any(w in message_lower for w in ["noticia", "parche", "update", "evento"]):
            category = "news"
        elif any(w in message_lower for w in ["guía", "como", "cómo", "pasar", "resolver"]):
            category = "guide"
        
        return IntentResult(
            game=detected_game,
            category=category,
            version=None,
            search_query=message,
            language="es",
            confidence=0.3,
            is_followup=False
        )
