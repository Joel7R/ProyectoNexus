"""
DealScout Agent
Searches and compares game prices across multiple stores
"""
from typing import Dict, List, Any
import re
import asyncio
from pydantic import BaseModel, Field
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import json
from pathlib import Path
from tools.formatter import format_to_artifact
from utils.cache_manager import cache_manager

# Cache file
CACHE_FILE = Path(__file__).parent.parent / "cache" / "deals_cache.json"

SYSTEM_PROMPT = """Eres 'Gaming Nexus - DealScout', un cazador de ofertas implacable.

TU OBJETIVO:
1. Analizar una lista de precios de videojuegos.
2. Identificar la MEJOR oferta (menor precio).
3. Generar un resumen atractivo que incite a la compra.

FORMATO DE SALIDA (JSON):
{
    "summary": "¡Oferta histórica! Minecraft por solo $15 en Instant Gaming (-40%).",
    "best_deal_store": "Instant Gaming",
    "reasoning": "Es $5 más barato que Steam y Microsoft Store.",
    "savings_text": "Ahorras el precio de un café ($5.00)"
}
"""

class DealScoutAgent:
    """Agent for finding and comparing game prices"""
    
    STORES = {
        "steam": {
            "name": "Steam",
            "domain": "store.steampowered.com",
            "icon": "🎮"
        },
        "epic": {
            "name": "Epic Games",
            "domain": "store.epicgames.com",
            "icon": "🎯"
        },
        "eneba": {
            "name": "Eneba",
            "domain": "eneba.com",
            "icon": "💎"
        },
        "g2a": {
            "name": "G2A",
            "domain": "g2a.com",
            "icon": "🔸"
        },
        "instant_gaming": {
            "name": "Instant Gaming",
            "domain": "instant-gaming.com",
            "icon": "⚡"
        },
        "microsoft": {
            "name": "Microsoft Store",
            "domain": "microsoft.com",
            "icon": "🪟"
        }
    }
    
    def __init__(self):
        from llm_config import llm_manager
        self.name = "DealScout"
        self.llm = llm_manager
    
    
    
    def _is_cache_valid(self, cached_data: dict, max_age_days: int = 1) -> bool:
        """Check if cached data is still valid"""
        if 'cached_at' not in cached_data:
            return False
        
        cached_time = datetime.fromisoformat(cached_data['cached_at'])
        age = datetime.now() - cached_time
        return age < timedelta(days=max_age_days)
    
    def _extract_price(self, text: str) -> float | None:
        """Extract price from text with enhanced pattern matching"""
        # Enhanced patterns to capture various price formats
        patterns = [
            r'\$\s*(\d+(?:\.\d{2})?)',           # $XX.XX
            r'(\d+(?:\.\d{2})?)\s*\$',           # XX.XX$
            r'(\d+(?:\.\d{2})?)\s*€',            # XX.XX€
            r'€\s*(\d+(?:\.\d{2})?)',            # €XX.XX
            r'(\d+(?:\.\d{2})?)\s*USD',          # XX.XX USD
            r'(\d+(?:\.\d{2})?)\s*EUR',          # XX.XX EUR
            r'(\d+,\d{2})\s*€',                  # XX,XX€ (European format)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        
        return None
    
    async def _llm_price_estimation(self, game_name: str, text_fragments: List[str]) -> float | None:
        """Use LLM to heuristically estimate price from text fragments"""
        if not text_fragments:
            return None
            
        combined_text = "\n\n".join(text_fragments[:3])  # Use first 3 fragments
        
        prompt = f"""Analiza estos fragmentos de texto de búsqueda web para '{game_name}' y extrae el PRECIO más probable.

Fragmentos:
{combined_text[:1500]}

Devuelve SOLO un JSON con:
{{
    "price": <número flotante>,
    "currency": "USD",
    "confidence": "high/medium/low"
}}

Si no encuentras ningún precio, devuelve {{"price": null}}."""

        try:
            messages = [
                {"role": "system", "content": "Eres un experto en extracción de precios de videojuegos. Analiza el texto y extrae el precio de forma precisa."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.llm.chat(messages, format="json")
            result = json.loads(response)
            
            price = result.get("price")
            if price and isinstance(price, (int, float)):
                print(f"[DealScout] LLM estimated price: ${price}")
                return float(price)
                
        except Exception as e:
            print(f"[DealScout] LLM price estimation failed: {e}")
        
        return None
    
    async def analyze(self, game_name: str, stores: List[str] = None) -> Dict[str, Any]:
        """
        Search for deals and synthesize comparison (STRICT FILTERS)
        """
        cache_key = f"deals_{game_name.lower().replace(' ', '_')}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        """
        Search for deals and synthesize comparison (STRICT FILTERS)
        """
        # Strict search query combining requested domains
        query = f'"{game_name}" site:eneba.com OR site:g2a.com OR site:instant-gaming.com OR site:store.steampowered.com'
        
        deals = []
        text_fragments = []
        
        print(f"[DealScout] Strict Scout: {game_name}")
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=8))
            
            for r in results:
                href = r.get('href', '').lower()
                
                # Identify store from domain
                store_key = None
                for k, v in self.STORES.items():
                    if v['domain'] in href:
                        store_key = k
                        break
                
                if not store_key:
                    continue
                    
                text = f"{r.get('title')} {r.get('body')}"
                price = self._extract_price(text)
                
                if price is not None:
                    deals.append({
                        "store": self.STORES[store_key]['name'],
                        "store_id": store_key,
                        "icon": self.STORES[store_key]['icon'],
                        "price": price,
                        "currency": "USD", 
                        "url": r.get('href'),
                        "is_best": False
                    })
                else:
                    text_fragments.append(f"Store: {self.STORES[store_key]['name']}\n{text}")

        except Exception as e:
            print(f"[DealScout] Search error: {e}")

        # Fallback for stores where regex failed but we have text
        if text_fragments and not any(d['store_id'] in ['eneba', 'g2a', 'instant_gaming'] for d in deals):
            llm_price = await self._llm_price_estimation(game_name, text_fragments)
            if llm_price:
                deals.append({
                    "store": "Precio detectado (IA)",
                    "store_id": "ai_detected",
                    "icon": "🔍",
                    "price": llm_price,
                    "currency": "USD",
                    "url": None,
                    "is_best": False
                })

        best_deal = None
        savings = 0
        
        if deals:
            deals.sort(key=lambda x: x['price'])
            best_deal = deals[0]
            best_deal['is_best'] = True
            
            if len(deals) > 1:
                highest = max(d['price'] for d in deals)
                savings = highest - best_deal['price']

        if deals:
            prompt = f"""Genera un resumen para '{game_name}' con estas ofertas:
{json.dumps(deals, indent=2)}
Incluye qué tienda es la granadora y cuánto se ahorra vs el máximo."""
            
            try:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                response_content = await self.llm.chat(messages, format="json")
                llm_result = json.loads(response_content)
                summary = llm_result.get("summary", f"Mejor precio: {best_deal['store']} ${best_deal['price']}")
            except:
                summary = f"Mejor precio encontrado en {best_deal['store']} por ${best_deal['price']}"
        else:
            summary = f"No encontré ofertas en las tiendas seleccionadas (Eneba, G2A, Instant Gaming, Steam) para '{game_name}'."

        artifact_data = {
            "game": game_name,
            "best_price": best_deal['price'] if best_deal else 0,
            "currency": "USD",
            "deals": deals,
            "savings": round(savings, 2)
        }
        
        result = {
            "success": bool(deals),
            "summary": summary,
            "artifact": format_to_artifact(artifact_data, "price"),
            "deals": deals
        }
        cache_manager.set(cache_key, result)
        return result

    async def search_deals(self, game_name: str) -> Dict[str, Any]:
        """Alias for convenience"""
        return await self.analyze(game_name)

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = DealScoutAgent()
        print("\n=== Test Minecraft Price Hunter ===")
        result = await agent.analyze("Minecraft")
        print(f"Summary: {result['summary']}")
        print(f"Deals: {len(result['deals'])}")
        
    asyncio.run(test())
