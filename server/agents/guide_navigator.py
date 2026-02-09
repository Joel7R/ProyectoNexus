"""
GuideNavigator Agent
Specialized in walkthroughs, step-by-step guides, and solving game blockers
"""
import os
from dataclasses import dataclass

import ollama

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact


SYSTEM_PROMPT = """Eres 'Gaming Nexus - GuideNavigator', experto en guías y walkthroughs de VIDEOJUEGOS.

Tu misión es ayudar al usuario a completar misiones, resolver puzzles y encontrar secretos en cualquier juego.

REGLAS CRÍTICAS:
1. Contexto Gaming: Ignora cualquier consulta que no sea sobre un videojuego.
2. Spoiler Alert: Si la solución revela un giro importante de la trama, advierte al usuario.
3. Precisión de Pasos: Divide la guía en pasos claros y numerados.
4. Artifact: Usa el artifact lateral para presentar la guía estructurada.

FORMATO DE RESPUESTA:
Tono: Guía paciente, evita frustración del jugador."""


@dataclass
class GuideResult:
    """Result from GuideNavigator"""
    summary: str
    artifact: dict
    sources: list[dict]
    steps: list[dict] # Added steps


class GuideNavigatorAgent:
    """Agent specialized in walkthroughs and step-by-step guides"""
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    
    async def find_solution(self, game: str, query: str) -> GuideResult:
        """Find guide or walkthrough with parallel execution and timeouts"""
        import asyncio
        
        # 1. Primary technical search (Wikis) and Fallback Forums in parallel
        try:
            wiki_task = live_web_search(f"{game} {query} guide wiki fextralife wiki.gg", search_type="wiki")
            forum_task = live_web_search(f"{game} {query} walkthrough strategy Reddit", search_type="forum")
            
            wiki_results, forum_results = await asyncio.wait_for(
                asyncio.gather(wiki_task, forum_task),
                timeout=20.0
            )
            results = wiki_results[:2] + forum_results[:1]
            
            # FALLBACK: If no specific guides found, search in news/previews
            if not results:
                print(f"GuideNavigator: No specific guides found for {game}, triggering fallback search...")
                news_results = await live_web_search(f"{game} {query} preview news details info", search_type="news", max_results=5)
                results = news_results[:3]
                
        except asyncio.TimeoutError:
            print("GuideNavigator: Search timeout")
            results = []
            
        if not results:
            return GuideResult(
                summary=f"No encontré guías detalladas para '{query}' en {game}, y tampoco hay avances informativos disponibles aún.",
                artifact={"type": "empty", "message": "Guía no encontrada"},
                sources=[],
                steps=[]
            )
        
        # 2. Scrape best results in parallel with timeout
        scrape_tasks = []
        for result in results[:3]: # Increased to 3 for fallback richness
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
                            "title": results[i]["title"],
                            "url": results[i]["url"],
                            "content": content[:3000] # Increased content length for better synthesis
                        })
            except asyncio.TimeoutError:
                print("GuideNavigator: Scrape timeout")
        
        # 3. LLM Synthesis with strict timeout
        is_fallback = "preview" in str(results) or "news" in str(results)
        
        fallback_instruction = ""
        if is_fallback:
            fallback_instruction = "\nNOTA: No hay guías oficiales disponibles. Usa la información de los AVANCES y NOTICIAS para inferir cómo funcionan las mecánicas. ADVIERTE que la info es preliminar."

        synthesis_prompt = f"""Genera una guía informativa para {game}: {query}
Basado en este contenido: {contents}
{fallback_instruction}

Si el juego es nuevo o la info es escasa, genera una guía 'Especulativa' basada en mecánicas habituales, pero ADVIERTE claramente.

JSON:
{{
    "summary": "resumen ejecutivo (incluye advertencia si es preliminar)",
    "difficulty": "Easy|Medium|Hard|Unknown",
    "required_level": "X o null",
    "steps": [
        {{"title": "...", "description": "...", "is_spoiler": true/false}}
    ],
    "collectibles": ["item1", "item2"] o null,
    "warning": "mensaje de advertencia sobre la veracidad de los datos" o null
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
                timeout=120.0
            )
            
            import json
            result = json.loads(response.message.content)
            
            artifact = format_to_artifact(data=result, template_type="guide")
            sources = [{"title": c["title"], "url": c["url"]} for c in contents]
            
            return GuideResult(
                summary=result.get("summary", "Guía generada."),
                artifact=artifact,
                sources=sources,
                steps=result.get("steps", [])
            )
            
        except (asyncio.TimeoutError, Exception) as e:
            if isinstance(e, asyncio.TimeoutError):
                print("GuideNavigator: LLM synthesis timeout")
            
            # Fallback
            artifact = format_to_artifact(
                data={"steps": [
                    {"title": r["title"], "description": r.get("snippet", ""), "is_spoiler": False}
                    for r in results[:5]
                ]},
                template_type="guide"
            )
            return GuideResult(
                summary=f"He encontrado {len(results)} recursos para tu guía.",
                artifact=artifact,
                sources=[{"title": r["title"], "url": r["url"]} for r in results[:5]],
                steps=[]
            )
