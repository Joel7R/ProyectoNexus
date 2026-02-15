"""
GuideNavigator Agent
Specialized in walkthroughs, step-by-step guides, and solving game blockers
"""
import json
import asyncio
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

SYSTEM_PROMPT = """Eres 'Gaming Nexus - GuideNavigator', asistente experto en guías de videojuegos."""

class GuideResult(BaseModel):
    """Pydantic V2 Model for Guide Results"""
    summary: str
    artifact: Dict[str, Any]
    sources: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]

class GuideNavigatorAgent:
    """Agent specialized in walkthroughs and step-by-step guides"""
    
    def __init__(self):
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def find_solution(self, game: str, query: str, language: str = "es") -> Dict[str, Any]:
        """Find guide or walkthrough - Returns dict for compatibility"""
        cache_key = f"guide_{game}_{query}_{language}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        try:
            results = await live_web_search(f"{game} {query} guide wiki", search_type="wiki")
        except:
            results = []
            
        if not results:
            return {"summary": "No encontré guías.", "artifact": {"type": "empty"}, "sources": [], "steps": []}
            
        scrape_tasks = [scrape_gaming_content(r["url"]) for r in results[:2]]
        contents = []
        try:
            texts = await asyncio.wait_for(asyncio.gather(*scrape_tasks, return_exceptions=True), timeout=15.0)
            for i, c in enumerate(texts):
                if isinstance(c, str):
                    contents.append({"title": results[i]["title"], "url": results[i]["url"], "content": c[:2500]})
        except: pass
        
        synthesis_prompt = f"Genera guía para {game}: {query}. Contexto: {contents}. Responde en JSON."
        
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": synthesis_prompt}]
            response_content = await self.llm.chat(messages, format="json")
            result = json.loads(response_content)
            artifact = format_to_artifact(data=result, template_type="guide")
            result_output = {
                "summary": result.get("summary", "Guía generada."),
                "artifact": artifact,
                "sources": [{"title": c["title"], "url": c["url"]} for c in contents],
                "steps": result.get("steps", [])
            }
            cache_manager.set(cache_key, result_output)
            return result_output
        except:
            return {"summary": "Error procesando guía.", "artifact": {"type": "error"}, "sources": [], "steps": []}
