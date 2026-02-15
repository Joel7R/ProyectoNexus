"""
Chronos Agent
Provides game lore, story summaries, and character relationships
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field
import asyncio
import re
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import json
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

SYSTEM_PROMPT = """Eres 'Gaming Nexus - Chronos', el archivista del lore.

TU OBJETIVO:
1. Explicar el lore de un personaje o evento.
2. Aplicar el 'SPOILER SHIELD':
   - Spoiler Level 'low': Solo premisa básica. CERO revelaciones de trama.
   - Spoiler Level 'medium': Trama principal hasta la mitad. Sin finales.
   - Spoiler Level 'high': Todo permitido. Finales y secretos.

3. Generar un Grafo Mermaid de relaciones.

FORMATO DE SALIDA (JSON):
{
    "summary": "Explicación narrativa adaptada al nivel de spoiler.",
    "relationships": [
        {"source": "Personaje A", "target": "Personaje B", "label": "Aliado/Enemigo/Hijo"},
        {"source": "Personaje A", "target": "Lugar X", "label": "Gobierna"}
    ],
    "mermaid": "graph TD; A[Personaje A] -- Label --> B[Personaje B]; ...",
    "spoiler_warning": "Warning text"
}
"""

class ChronosAgent:
    """Agent for game lore and story information"""
    
    SPOILER_LEVELS = {
        "none": "No spoilers - basic premise only",
        "low": "No spoilers - basic premise only",
        "medium": "Light spoilers - main plot points without major reveals",
        "high": "Full story - all details including endings",
        "full": "Full story - all details including endings"
    }
    
    def __init__(self):
        from llm_config import llm_manager
        self.name = "Chronos"
        self.llm = llm_manager
    
    async def get_lore(
        self, 
        game_name: str, 
        query: str,
        spoiler_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Get game lore with spoiler protection and relationship graph
        """
        cache_key = f"lore_{game_name}_{query}_{spoiler_level}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        
        search_query = f"{game_name} {query} lore story site:fandom.com OR site:wiki"
        
        print(f"[Chronos] Searching lore (CONFIDENCE SOURCES): {query} / {game_name}")
        
        context_text = ""
        try:
            await asyncio.sleep(1.0)
            with DDGS() as ddgs:
                # Limit to 3 high-quality results
                results = list(ddgs.text(search_query, max_results=3))
                for r in results:
                    context_text += f"-- SOURCE: {r.get('title')} --\n{r.get('body')}\n\n"
        except Exception as e:
            print(f"[Chronos] Search failed: {e}")
            context_text = "No se encontraron fuentes externas. Usa tu base de conocimientos."

        prompt = f"""Explícame quién/qué es '{query}' en '{game_name}'.
NIVEL DE SPOILER PERMITIDO: {spoiler_level.upper()}.
{self.SPOILER_LEVELS.get(spoiler_level, "Evita spoilers.")}

CONTEXTO DE BÚSQUEDA:
{context_text[:3000]}

REGLA DE PROCESAMIENTO:
Si el contexto es muy extenso, genera un RESUMEN EJECUTIVO inicial y luego profundiza en los detalles. 
Tu respuesta DEBE ser un JSON válido. Si hay errores en el texto, sánitiza la salida."""
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            # Use specific timeout or handle potential long response
            response_content = await self.llm.chat(messages, format="json")
            
            # Robust JSON cleaning (pre-parsing sanitization)
            if "```json" in response_content:
                response_content = re.sub(r"```json\s*(.*?)\s*```", r"\1", response_content, flags=re.DOTALL)
            
            llm_result = json.loads(response_content)
            summary = llm_result.get("summary", "Resumen no disponible.")
            mermaid_graph = llm_result.get("mermaid", "graph TD; A[Lore] --> B[Data];")
            
        except Exception as e:
            print(f"[Chronos] Critical Processing Error: {e}")
            # Dynamic fallback summary
            summary = f"Hubo un problema procesando la historia de {query}. En resumen: es un elemento clave de {game_name}."
            mermaid_graph = "graph TD; Lore[Lore Master] -- Error --> Retry[Reintentar más tarde];"

        artifact_data = {
            "title": f"Lore: {query}",
            "summary": summary,
            "mermaid_graph": mermaid_graph,
            "spoiler_level": spoiler_level,
            "game": game_name
        }
        
        result = {
            "success": True,
            "summary": summary,
            "artifact": format_to_artifact(artifact_data, "lore")
        }
        cache_manager.set(cache_key, result)
        return result

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ChronosAgent()
        print("\n=== Test Miquella (Lore Master) ===")
        result = await agent.get_lore("Elden Ring", "Miquella", "medium")
        print(f"Summary: {result['summary'][:100]}...")
        print(f"Graph: {result['artifact']['mermaid_content'][:50]}...")
        
    asyncio.run(test())
