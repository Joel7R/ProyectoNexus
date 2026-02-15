"""
Intent Orchestrator Agent
Analyzes user prompts and routes to specialized agents
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field

SYSTEM_PROMPT = """Eres el Orquestador de 'Gaming Nexus', IA especialista en videojuegos.

TU OBJETIVO:
1. Analizar la intención del usuario.
2. Detectar el IDIOMA del usuario (es, en, fr, etc.).
3. Generar una `search_query` optimizada.

LOGICA DE BÚSQUEDA (CLR - Cross Language Retrieval):
- Si el usuario busca "builds", "parches", "stats", "tier list" o datos técnicos:
  GENERA LA `search_query` EN INGLÉS, independientemente del idioma del usuario.

FORMATO JSON:
{
    "game": "nombre del juego o 'Gaming Industry' o 'REJECT'",
    "category": "news|build|guide",
    "version": "versión o null",
    "search_query": "query optimizada",
    "language": "código iso",
    "confidence": 0.0-1.0
}"""

class IntentResult(BaseModel):
    """Result of intent analysis - Pydantic V2"""
    game: str
    category: Literal["news", "build", "guide"]
    version: Optional[str] = None
    search_query: str
    language: str = "es"
    confidence: float = 0.5
    is_followup: bool = False

class IntentOrchestrator:
    """
    Analyzes user intent and routes to appropriate agent.
    """
    
    def __init__(self):
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def analyze(self, user_message: str, context: str = "") -> IntentResult:
        """Analyze user message and extract intent"""
        prompt = f"Contexto previo: {context}\n\nMensaje: {user_message}" if context else user_message
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response_content = await self.llm.chat(messages, format="json")
            
            import json
            result = json.loads(response_content)
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
        except Exception:
            return IntentResult(game="Unknown", category="build", search_query=user_message)
