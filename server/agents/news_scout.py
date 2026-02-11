"""
NewsScout Agent
Specialized in tracking breaking news, patches, and gaming events
"""
import os
from dataclasses import dataclass



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
        # We now use the centralized LLM manager
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def search(self, game: str, query: str, version: str | None = None, language: str = "es") -> NewsResult:
        """Search for gaming news and format results with CLR (Cross-Language Retrieval)"""
        import asyncio
        
        # Build base query
        base_query = f"{game} {query}"
        if version:
            base_query += f" {version}"
        
        search_tasks = []
        
        # 1. Primary Strategy: Parallel Search
        # If language is Spanish, search both Local (ES) and Global (EN) sources
        if language == "es":
            # Task 1: Local News
            search_tasks.append(live_web_search(base_query, search_type="ES_NEWS"))
            # Task 2: Global/Source News (Force English context for better recall)
            global_query = f"{game} news update" # Simplified for global search
            search_tasks.append(live_web_search(global_query, search_type="GLOBAL_NEWS"))
        else:
            # Default/English: Just global search
            search_tasks.append(live_web_search(base_query, search_type="GLOBAL_NEWS"))
        
        # Execute searches
        try:
            results_list = await asyncio.wait_for(
                asyncio.gather(*search_tasks),
                timeout=25.0
            )
            # Flatten results
            search_results = [item for sublist in results_list for item in sublist]
            
            # Remove duplicates by URL
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
            print("NewsScout: Search timeout or empty")
            return NewsResult(
                summary=f"No encontré noticias recientes sobre {game}. Intenta ser más específico.",
                artifact={"type": "empty", "message": "Sin resultados"},
                sources=[]
            )
        
        # Scrape top results (mix of ES and EN)
        scrape_tasks = []
        # Prioritize keeping a mix: 2 ES + 2 EN if available
        for result in search_results[:5]:
            scrape_tasks.append(scrape_gaming_content(result["url"]))
        
        contents = []
        if scrape_tasks:
            try:
                scraped_texts = await asyncio.wait_for(
                    asyncio.gather(*scrape_tasks, return_exceptions=True),
                    timeout=20.0
                )
                
                for i, content in enumerate(scraped_texts):
                    if isinstance(content, str) and content:
                        contents.append({
                            "title": search_results[i]["title"],
                            "url": search_results[i]["url"],
                            "domain": search_results[i]["url"].split("/")[2],
                            "content": content[:2500] 
                        })
            except asyncio.TimeoutError:
                print("NewsScout: Scrape timeout")
        
        # Use LLM to synthesize with CLR awareness
        synthesis_prompt = f"""Analiza estas noticias sobre {game}. DETECTA EL IDIOMA DEL USUARIO: {language}.
        
FUENTES ENCONTRADAS:
{contents}

TU TAREA:
1. Sintetiza las noticias más importantes.
2. Si la fuente es en INGLÉS (ej: IGN, Bloomberg), TRADUCE el resumen al {language} pero mantén términos técnicos (nerf, buff, tier).
3. Si hay rumores/leaks, indícalo claramente.

Responde en JSON:
{{
    "summary": "Resumen ejecutivo en {language}...",
    "news_items": [
        {{
            "title": "Título traducido o original",
            "date": "Fecha approx",
            "description": "Resumen en {language}...",
            "url": "url_original",
            "source_lang": "en|es",
            "importance": "high|medium|low"
        }}
    ]
}}"""
        
        try:
            # Use unified LLM manager
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ]
            
            response_content = await self.llm.chat(messages, format="json")
            
            import json
            # Handle potential markdown code blocks from Gemini
            cleaned_content = response_content.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_content)
            
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
            print(f"NewsScout: LLM synthesis error: {e}")
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
