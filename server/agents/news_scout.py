"""
NewsScout Agent
Specialized in tracking breaking news, patches, and gaming events
"""
import os
import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

SYSTEM_PROMPT = """Eres 'Gaming Nexus - NewsScout', una IA especializada EXCLUSIVAMENTE en noticias de la industria del videojuego.

REGLAS CRÍTICAS:
1. Contexto Total: Cualquier término como "noticias", "eventos" o "parches" se refiere SIEMPRE a videojuegos.
2. NO uses conocimiento previo. Cada dato debe venir de live_web_search.
3. Filtro de Actualidad: Si la info tiene más de 6 meses y es un Live Service (LoL, Genshin, Valorant, Fortnite), ADVIERTE al usuario.
4. Atribución: Cada dato clave lleva su fuente en formato [Fuente](url).
5. Estructura: Respuesta breve en chat, datos técnicos en artifact lateral.
6. IDIOMA: Responde SIEMPRE en ESPAÑOL.

FORMATO DE RESPUESTA:
- Resumen ejecutivo (2-3 líneas máximo) centrado en el impacto para el jugador.
- Artifact con tabla de noticias gaming ordenadas por fecha.
- Fuentes citadas de sitios especializados (IGN, Kotaku, PC Gamer, etc).

Tono: Técnico, épico y eficiente."""

class NewsResult(BaseModel):
    """Result from NewsScout analysis - Pydantic V2"""
    summary: str
    artifact: Dict[str, Any]
    sources: List[Dict[str, Any]]

class NewsScoutAgent:
    """Agent specialized in gaming news, patches, and events"""
    
    def __init__(self):
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def search(self, game: str, query: str, version: str | None = None, language: str = "es") -> NewsResult:
        """Search for gaming news and format results"""
        cache_key = f"news_{game}_{query}_{language}".lower().replace(" ", "_")
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return NewsResult(**cached_result)
        
        base_query = f"{game} {query}"
        if version:
            base_query += f" {version}"
        
        search_tasks = []
        if language == "es":
            search_tasks.append(live_web_search(base_query, search_type="ES_NEWS"))
            global_query = f"{game} news update"
            search_tasks.append(live_web_search(global_query, search_type="GLOBAL_NEWS"))
        else:
            search_tasks.append(live_web_search(base_query, search_type="GLOBAL_NEWS"))
        
        try:
            results_list = await asyncio.wait_for(
                asyncio.gather(*search_tasks),
                timeout=25.0
            )
            search_results = [item for sublist in results_list for item in sublist]
            
            seen_urls = set()
            unique_results = []
            for r in search_results:
                if r["url"] not in seen_urls:
                    unique_results.append(r)
                    seen_urls.add(r["url"])
            search_results = unique_results
            
            if not search_results:
                raise ValueError("No results found")
                
        except (asyncio.TimeoutError, ValueError):
            return NewsResult(
                summary=f"No encontré noticias recientes sobre {game}.",
                artifact={"type": "empty", "message": "Sin resultados"},
                sources=[]
            )
        
        scrape_tasks = []
        # Target 3 successful scrapes max to save time/quota
        # Optimization: Limit to top 5 promising URLs for detailed scraping
        # (The previous loop logic was buggy and overwritten here, fixing it)
        
        candidates = search_results[:5]
        scrape_tasks = [scrape_gaming_content(r["url"]) for r in candidates]
        
        contents = []
        if scrape_tasks:
            try:
                scraped_texts = await asyncio.wait_for(
                    asyncio.gather(*scrape_tasks, return_exceptions=True),
                    timeout=20.0
                )
                
                for i, content in enumerate(scraped_texts):
                    # Check for exceptions and empty strings
                    if isinstance(content, str) and content and not isinstance(content, Exception):
                        contents.append({
                            "title": candidates[i]["title"],
                            "url": candidates[i]["url"],
                            "content": content[:2500] 
                        })
                        # Stop if we have enough content (optimization)
                        if len(contents) >= 3:
                            break
            except asyncio.TimeoutError:
                print(f"[NewsScout] Scraping timed out for {game}")
                pass
            except Exception as e:
                print(f"[NewsScout] Async gathering error: {e}")
                pass

        # FALLBACK: If scraping failed or returned no content, return basic results without LLM
        if not contents:
            print(f"[NewsScout] No content scraped for {game}. Returning basic results.")
            sources = [
                {"title": item["title"], "url": item["url"]}
                for item in search_results[:5]
            ]
            
            # Create a simple artifact with links
            artifact = format_to_artifact(
                data={"items": [{"title": s["title"], "url": s["url"]} for s in sources]},
                template_type="table"
            )
            
            res = NewsResult(
                summary=f"No pude extraer los detalles, pero aquí tienes los enlaces más recientes sobre {game}.",
                artifact=artifact,
                sources=sources
            )
            cache_manager.set(cache_key, res.model_dump())
            return res
        
        synthesis_prompt = f"Analiza estas noticias sobre {game}.\n\nFUENTES ENCONTRADAS:\n{contents}\n\nResponde en JSON con summary y news_items list."
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ]
            response_content = await self.llm.chat(messages, format="json")
            
            import json
            result = json.loads(response_content)
            
            # Standard processing
            news_items_list = result.get("news_items", [])
            summary_text = result.get("summary", "Noticias encontradas.")
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "Quota exceeded" in error_str:
                print(f"[NewsScout] Quota exceeded (429). Generating simplified result.")
                # Power Saving Mode: Use scraped content titles/urls directly
                news_items_list = [
                    {"title": c["title"], "url": c["url"]} for c in contents
                ]
                summary_text = "⚠️ Modo Ahorro: Resumen no disponible por alta demanda. Aquí tienes los enlaces directos."
            else:
                raise e # Re-raise other errors
            
        # Common artifact creation from news_items_list
        artifact = format_to_artifact(
            data={"items": news_items_list},
            template_type="table"
        )
        
        sources = [
            {"title": item.get("title", "News"), "url": item.get("url", "#")}
            for item in news_items_list
        ]
        
        res = NewsResult(
            summary=summary_text,
            artifact=artifact,
            sources=sources
        )
        cache_manager.set(cache_key, res.model_dump())
        return res
