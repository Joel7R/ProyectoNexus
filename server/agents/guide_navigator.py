"""
GuideNavigator Agent
Specialized in walkthroughs, step-by-step guides, and solving game blockers
"""
import os
from dataclasses import dataclass
import json
import asyncio



from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact


SYSTEM_PROMPT = """Eres 'Gaming Nexus - GuideNavigator', un asistente experto en videojuegos diseñado para desbloquear a los jugadores SIN ARRUINAR LA EXPERIENCIA.

TU MISIÓN:
Guiar al usuario a través de niveles, puzzles o jefes utilizando un sistema de PISTAS PROGRESIVAS. Nunca des la solución directa de inmediato, a menos que el usuario lo pida explícitamente.

ESTRUCTURA DE RESPUESTA (Progressive Hints):
Para cada obstáculo o fase, estructura tu respuesta en 3 niveles de revelación:
1. PISTA SUTIL (Low Spoiler): Una sugerencia vaga sobre qué buscar o dónde mirar.
2. MECÁNICA CLAVE (Medium Spoiler): Explicación de la lógica o herramienta necesaria.
3. SOLUCIÓN PASO A PASO (High Spoiler): Instrucciones exactas para resolverlo.

REGLAS CRÍTICAS:
1. Contexto Gaming: Ignora consultas no relacionadas con videojuegos.
2. Spoiler Alert: Clasifica cada paso con un nivel de spoiler (low/medium/high).
3. Formato Artifact: Genera un JSON estructurado para que el frontend renderice las cajas de texto colapsables.
4. Tono: Sé un "compañero de hackeo" o un guía veterano. Usa terminología gamer (NPC, aggro, loot, hit-box).

Si la información es escasa, advierte que es una "Estrategia Teórica".
"""


@dataclass
class GuideResult:
    """Result from GuideNavigator"""
    summary: str
    artifact: dict
    sources: list[dict]
    steps: list[dict]


class GuideNavigatorAgent:
    """Agent specialized in walkthroughs and step-by-step guides"""
    
    def __init__(self):
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def find_solution(self, game: str, query: str, language: str = "es") -> GuideResult:
        """Find guide or walkthrough with progressive hints structure"""
        
        # 1. Search Logic
        try:
            wiki_task = live_web_search(f"{game} {query} guide wiki solution puzzle", search_type="wiki")
            forum_task = live_web_search(f"{game} {query} how to beat walkthrough reddit", search_type="forum")
            
            wiki_results, forum_results = await asyncio.wait_for(
                asyncio.gather(wiki_task, forum_task),
                timeout=20.0
            )
            results = wiki_results[:2] + forum_results[:2]
            
            if not results:
                 # Fallback to news/general if no guides found
                print(f"GuideNavigator: No specific guides found for {game}, triggering fallback search...")
                results = await live_web_search(f"{game} {query} gameplay details", search_type="general", max_results=3)
                
        except asyncio.TimeoutError:
            print("GuideNavigator: Search timeout")
            results = []
            
        if not results:
            return GuideResult(
                summary=f"No encontré guías específicas para '{query}' en {game}. ¿Podrías darme más detalles sobre en qué parte estás atascado?",
                artifact={"type": "empty", "message": "Sin datos suficientes"},
                sources=[],
                steps=[]
            )
        
        # 2. Scrape Content
        scrape_tasks = [scrape_gaming_content(r["url"]) for r in results[:3]]
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
                            "content": content[:4000] # More context for complex guides
                        })
            except asyncio.TimeoutError:
                print("GuideNavigator: Scrape timeout")
        
        # 3. LLM Synthesis - Progressive Hints
        synthesis_prompt = f"""Genera una GUÍA PROGRESIVA para {game}: {query}
DETECTA EL IDIOMA DE SALIDA: {language}.

Basado en: {contents}

Genera un JSON válido con esta estructura exacta:
{{
    "summary": "Resumen de la misión/objetivo (sin spoilers) en {language}",
    "difficulty": "Easy|Medium|Hard|Very Hard",
    "estimated_time": "ej: 10-15 mins",
    "hint": "Una pista general muy sutil para empezar en {language}",
    "steps": [
        {{
            "number": 1,
            "title": "Nombre del paso (ej: Encontrar la llave) en {language}",
            "content": "Descripción detallada en {language}...",
            "spoiler_level": "low|medium|high",
            "tip": "Consejo extra (opcional) en {language}",
            "warning": "Peligro/Bug (opcional)",
            "collapsed": true
        }}
    ],
    "collectibles": [
        {{"name": "Coin #1", "location": "Detrás de la cascada"}}
    ],
    "rewards": ["Xp", "Item especial"]
}}

IMPORTANTE:
- Divide la solución en al menos 3 pasos si es posible.
- El primer paso debe ser 'low' spoiler (pista de ubicación).
- El paso final debe ser 'high' spoiler (solución del puzzle/jefe).
- Si no encuentras info exacta, di que es una "Hipótesis basada en mecánicas generales".
"""
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ]
            
            response_content = await self.llm.chat(messages, format="json")
            
            cleaned_content = response_content.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_content)
            
            # Post-process to ensure frontend compatibility
            steps = result.get("steps", [])
            for step in steps:
                if "spoiler_level" not in step:
                    step["spoiler_level"] = "medium"
                step["hidden"] = step["spoiler_level"] == "high" # Auto-hide high spoilers
                step["collapsed"] = True
            
            result["steps"] = steps
            
            artifact = format_to_artifact(data=result, template_type="guide")
            sources = [{"title": c["title"], "url": c["url"]} for c in contents]
            
            return GuideResult(
                summary=result.get("summary", "Guía generada."),
                artifact=artifact,
                sources=sources,
                steps=steps
            )
            
        except (asyncio.TimeoutError, Exception) as e:
            print(f"GuideNavigator Error: {e}")
            if isinstance(e, asyncio.TimeoutError):
                print("GuideNavigator: LLM synthesis timeout")
            
            # Error Fallback
            return GuideResult(
                summary=f"Encontré información sobre {query} pero tuve problemas procesándola para crear una guía paso a paso.",
                artifact={"type": "error", "message": "Error generando guía estructurada"},
                sources=[{"title": r["title"], "url": r["url"]} for r in results[:3]],
                steps=[]
            )
