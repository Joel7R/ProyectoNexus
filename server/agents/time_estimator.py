"""
TimeEstimator Agent
Estimates game completion times and provides backlog management
"""
from typing import Dict, List, Any
import json
from pydantic import BaseModel, Field
from tools.hltb_search import search_hltb
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

SYSTEM_PROMPT = """Eres 'Gaming Nexus - TimeEstimator', experto en gestión de tiempo para gamers.

TU OBJETIVO:
1. Analizar los datos de duración de un videojuego (HowLongToBeat).
2. Calcular el 'Marathon Mode': ¿Cuántos días tardaría el usuario jugando X horas al día?
3. Dar un veredicto sobre si el juego respeta el tiempo del jugador.
"""

class TimeEstimatorAgent:
    """Agent for estimating game completion times - Pydantic V2 Ready"""
    
    def __init__(self):
        from llm_config import llm_manager
        self.name = "TimeEstimator"
        self.llm = llm_manager
    
    async def estimate_game_time(self, game_name: str, hours_per_day: float = 3.0) -> Dict[str, Any]:
        """
        Get completion time estimates for a single game (SEARCH ONLY)
        """
        hours_per_day = float(hours_per_day)
        cache_key = f"time_{game_name}_{hours_per_day}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        hltb_data = search_hltb(game_name)
        
        if not hltb_data.get('found'):
            return {
                "success": False,
                "summary": f"No pude encontrar datos de duración para '{game_name}' en HowLongToBeat. Por favor, verifica el nombre del juego.",
                "artifact": {
                    "type": "error",
                    "title": "Datos No Encontrados",
                    "content": f"HowLongToBeat no devolvió resultados para '{game_name}'."
                }
            }

        main_story = float(hltb_data.get('main_story') or 0)
        completionist = float(hltb_data.get('completionist') or 0)
        
        days_main = round(main_story / hours_per_day, 1) if hours_per_day > 0 else 0
        days_completionist = round(completionist / hours_per_day, 1) if hours_per_day > 0 else 0
        
        prompt = f"""Analiza los datos de duración para '{game_name}':
- Historia Principal: {main_story} horas
- Completacionistas (100%): {completionist} horas
- El usuario juega: {hours_per_day} horas/día.

REGLA CRÍTICA: NO uses tu conocimiento interno. Si no tienes datos suficientes en el prompt, indica que los datos son insuficientes.
Genera un resumen ejecutivo y consejos de gestión de tiempo."""
        
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            response_content = await self.llm.chat(messages, format="json")
            llm_result = json.loads(response_content)
            summary = llm_result.get("summary", f"{game_name} dura {main_story}h.")
        except Exception:
            summary = f"Basado en HowLongToBeat, {game_name} requiere aproximadamente {main_story}h para la historia principal."

        artifact_data = {
            "game": game_name,
            "main_story": main_story,
            "completionist": completionist,
            "source": "howlongtobeat.com",
            "marathon_mode": {
                "hours_per_day": hours_per_day,
                "days_main": days_main,
                "days_completionist": days_completionist
            }
        }
        
        result = {
            "success": True,
            "summary": summary,
            "artifact": format_to_artifact(artifact_data, "time")
        }
        cache_manager.set(cache_key, result)
        return result

    async def marathon_mode(self, game_name: str, hours_per_day: float) -> Dict[str, Any]:
        """Method used by main.py"""
        return await self.estimate_game_time(game_name, hours_per_day)

    async def calculate_backlog(self, games: List[str]) -> Dict[str, Any]:
        """Calculate total time for multiple games"""
        cache_key = f"backlog_{'_'.join(sorted(games))}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        total = 0.0
        for game in games:
            hltb = search_hltb(game)
            total += float(hltb.get('main_story', 20) or 20)
            
        result = {
            "success": True,
            "total_hours": total,
            "artifact": format_to_artifact({"total": total, "games": games}, "table")
        }
        cache_manager.set(cache_key, result)
        return result
