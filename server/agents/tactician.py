"""
Tactician Agent
Specialized in meta-builds, item stats, and tier lists
"""
import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from tools.web_search import live_web_search
from tools.scraper import scrape_gaming_content
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

SYSTEM_PROMPT = """Eres 'Gaming Nexus - Tactician', experto en teoría y mecánica de VIDEOJUEGOS.
Tu misión es analizar el meta, builds y estadísticas en Español."""

class TacticianAgent:
    """Agent specialized in builds, stats, and meta analysis - Pydantic V2 Ready"""
    
    def __init__(self):
        from llm_config import llm_manager
        self.llm = llm_manager
    
    async def analyze(self, game: str, query: str, version: Optional[str] = None, language: str = "es") -> Dict[str, Any]:
        """Analyze builds and meta for a game"""
        cache_key = f"tactician_{game}_{query}_{version}_{language}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        search_query = f"{game} {query} build meta"
        
        try:
            wiki_results = await live_web_search(search_query, search_type="wiki")
            forum_results = await live_web_search(search_query, search_type="forum")
            all_results = wiki_results[:2] + forum_results[:1]
        except:
            all_results = []
            
        if not all_results:
            return {"success": False, "summary": "No encontré builds actuales.", "artifact": {"display": "empty"}, "sources": []}
            
        scrape_tasks = [scrape_gaming_content(r["url"]) for r in all_results[:3]]
        contents = []
        try:
            scraped_texts = await asyncio.wait_for(asyncio.gather(*scrape_tasks, return_exceptions=True), timeout=15.0)
            for i, content in enumerate(scraped_texts):
                if isinstance(content, str):
                    contents.append({"title": all_results[i]["title"], "url": all_results[i]["url"], "content": content[:2000]})
        except: pass
        
        synthesis_prompt = f"Analiza builds para {game}: {query}. Contexto: {contents}. Responde en JSON."
        
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": synthesis_prompt}]
            response_content = await self.llm.chat(messages, format="json")
            import json
            result = json.loads(response_content)
            artifact = format_to_artifact(data=result, template_type="build")
            result_output = {
                "success": True, 
                "summary": result.get("summary", "Build encontrada"), 
                "artifact": artifact, 
                "sources": [{"title": c["title"], "url": c["url"]} for c in contents]
            }
            cache_manager.set(cache_key, result_output)
            return result_output
        except Exception:
            return {"success": True, "summary": "Encontré recursos sobre la build.", "artifact": {"display": "list"}, "sources": [{"title": r["title"], "url": r["url"]} for r in all_results]}
