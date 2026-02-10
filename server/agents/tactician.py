"""
Tactician Agent
Specialized in meta-builds, item stats, and tier lists
"""
import os
from dataclasses import dataclass

import ollama

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact


SYSTEM_PROMPT = """Eres 'Gaming Nexus - Tactician', experto en teoría y mecánica de VIDEOJUEGOS.

Tu misión es analizar el meta, builds y estadísticas de personajes o equipo de un juego.

REGLAS CRÍTICAS:
1. Enfoque Mecánico: Céntrate en números, sinergias, items y tácticas de juego.
2. Contexto Gaming: Si el usuario menciona un nombre ambiguo, busca su relación con videojuegos conocidos.
3. NO inventes datos. Si los resultados de búsqueda son escasos, informa de la falta de datos actualizados.
4. Artifact: Usa 'build_dashboard' para presentar la información técnica.

FORMATO:
- Análisis breve del estado actual del meta.
- Artifact con build recomendada, stats y matchups.
- Advertencia si la versión del juego ha cambiado recientemente."""


@dataclass
class BuildResult:
    """Result from Tactician analysis"""
    summary: str
    artifact: dict
    sources: list[dict]
    items: list[dict]  # For context tracking


class TacticianAgent:
    """Agent specialized in builds, stats, and meta analysis"""
    
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(
            host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    
    async def analyze(self, game: str, query: str, version: str | None = None, language: str = "es") -> BuildResult:
        """Analyze builds and meta for a game"""
        
        # Build optimized search query - leverage engine's year biasing
        search_query = f"{game} {query} build meta"
        if version:
            search_query = f"{game} {query} {version} build"
        
        # Search multiple sources in parallel with timeout
        try:
            wiki_task = live_web_search(search_query, search_type="wiki")
            forum_task = live_web_search(search_query, search_type="forum")
            
            import asyncio
            wiki_results, forum_results = await asyncio.wait_for(
                asyncio.gather(wiki_task, forum_task),
                timeout=20.0
            )
        except asyncio.TimeoutError:
            print("Tactician: Search timeout, proceeding with empty results")
            wiki_results, forum_results = [], []
        
        all_results = wiki_results[:2] + forum_results[:1]
        
        if not all_results:
            return BuildResult(
                summary=f"No encontré builds actuales para {query} en {game}.",
                artifact={"type": "empty"},
                sources=[],
                items=[]
            )
        
        # Scrape content in parallel with timeout
        scrape_tasks = []
        for result in all_results[:3]:
            scrape_tasks.append(scrape_gaming_content(result["url"]))
        
        contents = []
        if scrape_tasks:
            try:
                import asyncio
                scraped_texts = await asyncio.wait_for(
                    asyncio.gather(*scrape_tasks, return_exceptions=True),
                    timeout=15.0
                )
                
                for i, content in enumerate(scraped_texts):
                    if isinstance(content, str) and content:
                        contents.append({
                            "title": all_results[i]["title"],
                            "url": all_results[i]["url"],
                            "content": content[:2000]
                        })
            except asyncio.TimeoutError:
                print("Tactician: Scrape timeout")
        
        # Synthesize with LLM
        synthesis_prompt = f"""Analiza esta información sobre builds/meta de {game} para: {query}
DETECTA EL IDIOMA DE SALIDA: {language}.

Contenido:
{contents}

TU TAREA:
1. Extrae la mejor build/estrategia.
2. Responde en {language}, PERO MANTÉN EN INGLÉS LOS TÉRMINOS TÉCNICOS (Items, Runas, Skills, Stats) si es lo estándar en la comunidad.
   (Ej: "Usa 'Infinity Edge' para más 'Crit Damage'", NO "Filo Infinito").

Genera un JSON con:
{{
    "summary": "veredicto táctico de 1-2 líneas en {language}",
    "character": "nombre del personaje/clase",
    "tier": "S/A/B/C/D",
    "win_rate": "XX%" o null,
    "pick_rate": "XX%" o null,
    "items": [
        {{"name": "...", "slot": "...", "stats": "...", "priority": 1-5}}
    ],
    "skills": [
        {{"name": "...", "description": "...", "max_first": true/false}}
    ],
    "runes": [...] o null,
    "playstyle": "descripción breve del estilo de juego en {language}",
    "counters": ["counter1", "counter2"] o null,
    "synergies": ["synergy1", "synergy2"] o null,
    "source_warning": "mensaje si la info es vieja" o null
}}"""
        
        try:
            import asyncio
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
            
            artifact = format_to_artifact(data=result, template_type="build")
            
            sources = [{"title": c["title"], "url": c["url"]} for c in contents]
            items = result.get("items", [])
            
            summary = result.get("summary", f"Build encontrada para {query}")
            if result.get("source_warning"):
                summary += f"\n⚠️ {result['source_warning']}"
            
            return BuildResult(
                summary=summary,
                artifact=artifact,
                sources=sources,
                items=items
            )
            
        except (asyncio.TimeoutError, Exception) as e:
            if isinstance(e, asyncio.TimeoutError):
                print("Tactician: LLM synthesis timeout")
            
            # Fallback
            artifact = format_to_artifact(
                data={"items": [{"name": r["title"], "url": r["url"]} for r in all_results]},
                template_type="build"
            )
            
            return BuildResult(
                summary=f"Encontré {len(all_results)} recursos sobre {query} en {game}.",
                artifact=artifact,
                sources=[{"title": r["title"], "url": r["url"]} for r in all_results],
                items=[]
            )
