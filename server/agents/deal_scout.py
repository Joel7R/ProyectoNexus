"""
DealScout Agent
Searches and compares game prices across multiple stores
"""
from typing import Dict, List, Any
import re
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import json
from pathlib import Path

# Cache file
CACHE_FILE = Path(__file__).parent.parent / "cache" / "deals_cache.json"

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
        "gog": {
            "name": "GOG",
            "domain": "gog.com",
            "icon": "🕹️"
        },
        "instant_gaming": {
            "name": "Instant Gaming",
            "domain": "instant-gaming.com",
            "icon": "⚡"
        }
    }
    
    def __init__(self):
        self.name = "DealScout"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cached deals"""
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save deals to cache"""
        CACHE_FILE.parent.mkdir(exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _is_cache_valid(self, cached_data: dict, max_age_days: int = 7) -> bool:
        """Check if cached data is still valid"""
        if 'cached_at' not in cached_data:
            return False
        
        cached_time = datetime.fromisoformat(cached_data['cached_at'])
        age = datetime.now() - cached_time
        return age < timedelta(days=max_age_days)
    
    def _extract_price(self, text: str) -> float | None:
        """Extract price from text"""
        # Patterns for different currencies
        patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $59.99
            r'(\d+(?:\.\d{2})?)\s*€',  # 59.99€
            r'€\s*(\d+(?:\.\d{2})?)',  # € 59.99
            r'(\d+(?:\.\d{2})?)\s*USD',  # 59.99 USD
            r'(\d+(?:\.\d{2})?)\s*EUR',  # 59.99 EUR
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    async def search_deals(self, game_name: str) -> Dict[str, Any]:
        """
        Search for game prices across all stores
        
        Args:
            game_name: Name of the game
            
        Returns:
            Dictionary with deals from all stores
        """
        cache_key = game_name.lower().strip()
        
        # Check cache
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            print(f"[DealScout] Cache hit for '{game_name}'")
            return self.cache[cache_key]
        
        print(f"[DealScout] Searching deals for '{game_name}'...")
        
        deals = []
        reasoning = [f"Buscando precios para '{game_name}' en múltiples tiendas..."]
        
        ddgs = DDGS()
        
        for store_id, store_info in self.STORES.items():
            try:
                query = f"{game_name} price {store_info['name']}"
                results = ddgs.text(query, max_results=3)
                
                if not results:
                    reasoning.append(f"✗ {store_info['name']}: Sin resultados")
                    continue
                
                # Extract price from results
                all_text = " ".join([r.get('body', '') + " " + r.get('title', '') for r in results])
                price = self._extract_price(all_text)
                
                if price:
                    deals.append({
                        "store": store_info['name'],
                        "store_id": store_id,
                        "icon": store_info['icon'],
                        "price": price,
                        "currency": "USD",  # Simplified for now
                        "url": results[0].get('href', '#'),
                        "is_best": False
                    })
                    reasoning.append(f"✓ {store_info['name']}: ${price}")
                else:
                    reasoning.append(f"✗ {store_info['name']}: Price not found")
                    
            except Exception as e:
                print(f"[DealScout] Error searching {store_info['name']}: {e}")
                reasoning.append(f"✗ {store_info['name']}: Error")
        
        # Find best deal
        best_deal = None
        if deals:
            deals.sort(key=lambda x: x['price'])
            best_deal = deals[0]
            best_deal['is_best'] = True
            
            # Calculate savings
            if len(deals) > 1:
                highest_price = max(d['price'] for d in deals)
                savings = highest_price - best_deal['price']
                savings_percent = (savings / highest_price) * 100
            else:
                savings = 0
                savings_percent = 0
        else:
            savings = 0
            savings_percent = 0
        
        result = {
            "success": len(deals) > 0,
            "game": game_name,
            "deals": deals,
            "best_deal": best_deal,
            "savings": round(savings, 2) if savings else 0,
            "savings_percent": round(savings_percent, 1) if savings_percent else 0,
            "reasoning": reasoning,
            "cached_at": datetime.now().isoformat()
        }
        
        # Cache result
        if result['success']:
            self.cache[cache_key] = result
            self._save_cache()
        
        return result
    
    async def compare_stores(self, game_name: str, store_ids: List[str]) -> Dict[str, Any]:
        """
        Compare prices for specific stores only
        
        Args:
            game_name: Name of the game
            store_ids: List of store IDs to compare
            
        Returns:
            Comparison data
        """
        all_deals = await self.search_deals(game_name)
        
        if not all_deals['success']:
            return all_deals
        
        # Filter to requested stores
        filtered_deals = [d for d in all_deals['deals'] if d['store_id'] in store_ids]
        
        # Recalculate best deal
        if filtered_deals:
            filtered_deals.sort(key=lambda x: x['price'])
            for deal in filtered_deals:
                deal['is_best'] = False
            filtered_deals[0]['is_best'] = True
        
        return {
            **all_deals,
            "deals": filtered_deals,
            "best_deal": filtered_deals[0] if filtered_deals else None
        }

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = DealScoutAgent()
        
        # Test search
        result = await agent.search_deals("Elden Ring")
        print("\n=== Deal Search ===")
        print(f"Game: {result['game']}")
        print(f"Found {len(result['deals'])} deals")
        
        if result['best_deal']:
            print(f"\nBest Deal:")
            print(f"  {result['best_deal']['store']}: ${result['best_deal']['price']}")
            print(f"  Save: ${result['savings']} ({result['savings_percent']}%)")
        
        print(f"\nAll Deals:")
        for deal in result['deals']:
            marker = "🏆" if deal['is_best'] else "  "
            print(f"{marker} {deal['icon']} {deal['store']}: ${deal['price']}")
    
    asyncio.run(test())
