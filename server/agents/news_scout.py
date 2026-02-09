"""
NewsScout Agent
Specialized in tracking breaking news, patches, and gaming events
"""
import os
from dataclasses import dataclass

import ollama

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact


SYSTEM_PROMPT = """Eres 'Gaming Nexus - NewsScout', una IA especializada EXCLUSIVAMENTE en noticias de la industria del videojuego.

REGLAS CRÍTICAS:
1. Contexto Total: Cualquier término como "noticias", "eventos" o "parches" se refiere SIEMPRE a videojuegos.
2. NO uses conocimiento previo. Cada dato debe venir de live_web_search.
3. Filtro de Actualidad: Si la info tiene más de 6 meses y es un Live Service (LoL, Genshin, Valorant, Fortnite), ADVIERTE al usuario.
4. Atribución: Cada dato clave lleva su fuente en formato [Fuente](url).
5. Estructura: Respuesta breve en chat, datos técnicos en artifact lateral.

FORMATO DE RESPUESTA:
- Resumen ejecutivo (2-3 líneas máximo) centrado en el impacto para el jugador.
- Artifact con tabla de noticias gaming ordenadas por fecha.
- Fuentes citadas de sitios especializados (IGN, Kotaku, PC Gamer, etc).

Tono: Técnico, épico y eficiente."""


@dataclass 
class NewsResult:
    """Result from NewsScout analysis"""
    summary: str
    artifact: dict
    sources: list[dict]


class NewsScoutAgent:
    """Agent specialized in gaming news, patches, and events"""
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    
    async def search(self, game: str, query: str, version: str | None = None) -> NewsResult:
        """Search for gaming news and format results"""
        import asyncio
        
        # Build optimized search query - concise for the new engine
        search_query = f"{game} {query}"
        if version:
            search_query += f" {version}"
        
        # Execute web search with timeout
        try:
            search_results = await asyncio.wait_for(
                live_web_search(search_query, search_type="news"),
                timeout=20.0
            )
        except asyncio.TimeoutError:
            print("NewsScout: Search timeout")
            search_results = []
        
        if not search_results:
            return NewsResult(
                summary=f"No encontré noticias recientes sobre {game}. Intenta ser más específico.",
                artifact={"type": "empty", "message": "Sin resultados"},
                sources=[]
            )
        
        # Scrape top results for content in parallel with timeout
        scrape_tasks = []
        for result in search_results[:3]:
            scrape_tasks.append(scrape_gaming_content(result["url"]))
        
        contents = []
        if scrape_tasks:
            try:
                scraped_texts = await asyncio.wait_for(
                    asyncio.gather(*scrape_tasks, return_exceptions=True),
                    timeout=15.0
                )
                
                for i, content in enumerate(scraped_texts):
                    if isinstance(content, str) and content:
                        contents.append({
                            "title": search_results[i]["title"],
                            "url": search_results[i]["url"],
                            "content": content[:2000]
                        })
            except asyncio.TimeoutError:
                print("NewsScout: Scrape timeout")
        
        # Use LLM to synthesize - explicitly mention bilingual content
        synthesis_prompt = f"""Analiza estas noticias recopiladas sobre {game}. 
IMPORTANTE: Los resultados pueden incluir contenido en inglés que ha sido traducido o extraído. Combina lo mejor de ambas fuentes.

1. Un resumen ejecutivo de 2-3 líneas con impacto en el jugador.
2. Lista de noticias principales.

Contenido encontrado:
{contents}

Responde en JSON:
{{
    "summary": "resumen breve",
    "news_items": [
        {{"title": "...", "date": "...", "description": "...", "url": "...", "importance": "high|medium|low"}}
    ]
}}"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": synthesis_prompt}
                    ],
                    format="json"
                ),
                timeout=90.0
            )
            
            import json
            result = json.loads(response.message.content)
            
            artifact = format_to_artifact(
                data={"items": result.get("news_items", [])},
                template_type="table"
            )
            
            sources = [
                {"title": item["title"], "url": item["url"]}
                for item in result.get("news_items", [])
            ]
            
            return NewsResult(
                summary=result.get("summary", "Noticias encontradas."),
                artifact=artifact,
                sources=sources
            )
            
        except (asyncio.TimeoutError, Exception) as e:
            if isinstance(e, asyncio.TimeoutError):
                print("NewsScout: LLM synthesis timeout")
            # Fallback without LLM synthesis
            artifact = format_to_artifact(
                data={"items": [
                    {"title": r["title"], "url": r["url"], "description": r.get("snippet", "")}
                    for r in search_results[:5]
                ]},
                template_type="table"
            )
            
            return NewsResult(
                summary=f"Encontré {len(search_results)} noticias sobre {game}.",
                artifact=artifact,
                sources=[{"title": r["title"], "url": r["url"]} for r in search_results[:5]]
            )
