"""
Intent Orchestrator Agent
Analyzes user prompts and routes to specialized agents
"""
import os
from typing import Literal
from dataclasses import dataclass

import ollama


SYSTEM_PROMPT = """Eres el Orquestador de 'Gaming Nexus', una IA especializada EXCLUSIVAMENTE en videojuegos. 

REGLAS DE INTERPRETACIÓN:
1. **Prioridad Gaming**: Todo prompt debe ser interpretado dentro del contexto de los videojuegos.
2. **Noticias Generales**: Si el usuario pide "noticias", "novedades" o "qué hay de nuevo" sin especificar un juego, usa "Gaming Industry" como nombre del juego y categoría "news". **JAMÁS** rechaces una búsqueda de noticias genérica.
3. **Identificación**: Si no se menciona el juego pero sí elementos (ej: "Yasuo", "Ranni", "V-Bucks"), identifica el juego correspondiente.
4. **Títulos Completos**: Intenta usar el nombre oficial completo del juego si lo conoces (ej: 'Clair Obscur: Expedition 33' en lugar de solo 'Expedition 33').
5. **Juegos Nuevos**: Si el juego no ha salido o es muy reciente, ajusta el `search_query` para incluir "preview", "news" o "mechanics" si la categoría es "guide" o "build".

REGLA DE SEGURIDAD (REJECT): 
- Usa "REJECT" como nombre del juego SOLO si el usuario pregunta por temas totalmente ajenos (ej: cocina, política, medicina, consejos de amor, tareas escolares no relacionadas).
- En el campo `search_query` de un REJECT, explica brevemente por qué es off-topic.

Responde SOLO en formato JSON:
{
    "game": "nombre del juego o 'Gaming Industry' o 'REJECT'",
    "category": "news|build|guide",
    "version": "versión o null",
    "search_query": "query optimizada (ej: 'videojuegos noticias hoy' o 'Elden Ring DLC update')",
    "confidence": 0.0-1.0
}

Si es una continuación ("¿y cómo lo equipo?"), usa "FOLLOW_UP" como juego."""


@dataclass
class IntentResult:
    """Result of intent analysis"""
    game: str
    category: Literal["news", "build", "guide"]
    version: str | None
    search_query: str
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
            confidence=0.3,
            is_followup=False
        )
