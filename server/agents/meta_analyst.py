"""
MetaAnalyst Agent
Analyzes game patch notes and predicts meta impact
"""
from typing import Dict, List, Any
import asyncio
from pydantic import BaseModel, Field
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import re

from utils.cache_manager import cache_manager

class MetaAnalystAgent:
    """Agent for patch note analysis and meta prediction - Pydantic V2 Ready"""
    
    SUPPORTED_GAMES = {
        "league of legends": {
            "patch_url": "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/",
            "stats": ["damage", "health", "armor", "cooldown", "mana", "range"]
        },
        "valorant": {
            "patch_url": "https://playvalorant.com/en-us/news/tags/patch-notes/",
            "stats": ["damage", "fire rate", "magazine", "reload", "accuracy"]
        },
        "overwatch 2": {
            "patch_url": "https://overwatch.blizzard.com/en-us/news/patch-notes/",
            "stats": ["damage", "health", "healing", "cooldown", "ultimate"]
        },
        "apex legends": {
            "patch_url": "https://www.ea.com/games/apex-legends/news",
            "stats": ["damage", "fire rate", "magazine", "reload", "tactical"]
        },
        "dota 2": {
            "patch_url": "https://www.dota2.com/patches/",
            "stats": ["damage", "health", "mana", "cooldown", "armor"]
        }
    }
    
    def __init__(self):
        self.name = "MetaAnalyst"
    
    async def analyze_patch(
        self,
        game: str,
        patch_version: str = None,
        main_character: str = None
    ) -> Dict[str, Any]:
        """
        Analyze patch notes for a game
        """
        cache_key = f"patch_{game}_{patch_version}_{main_character}".lower().replace(" ", "_")
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        game_lower = game.lower()
        
        if game_lower not in self.SUPPORTED_GAMES:
            return {
                "success": False,
                "message": f"Game '{game}' not supported. Supported: {list(self.SUPPORTED_GAMES.keys())}"
            }
        
        print(f"[MetaAnalyst] Analyzing patch for {game}")
        
        reasoning = [f"Searching patch notes for {game}"]
        
        # Search for patch notes
        query = f"{game} patch notes {patch_version or 'latest'} 2026"
        
        changes = []
        try:
            # Rate limit throttle for DDGS
            await asyncio.sleep(1.5)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                
                for result in results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    url = result.get('href', '')
                    
                    # Extract changes from text
                    extracted_changes = self._extract_changes(body, game_lower)
                    
                    for change in extracted_changes:
                        # Filter by main character if specified
                        if main_character and main_character.lower() not in change['character'].lower():
                            continue
                        
                        changes.append(change)
                    
                    reasoning.append(f"Extracted {len(extracted_changes)} changes from {url}")
                    
                    if changes:
                        break  # Got data, stop searching
                    
        except Exception as e:
            print(f"[MetaAnalyst] Error: {e}")
            return {
                "success": False,
                "message": f"Error analyzing patch: {str(e)}"
            }
        
        if not changes:
            return {
                "success": False,
                "message": f"No patch data found for {game}",
                "reasoning": reasoning
            }
        
        # Classify changes
        for change in changes:
            change['type'] = self._classify_change(change)
            change['severity'] = self._assess_severity(change)
        
        # Generate verdict
        verdict = self._generate_verdict(changes, game)
        
        result = {
            "success": True,
            "game": game,
            "patch": patch_version or "Latest",
            "changes": changes,
            "verdict": verdict,
            "reasoning": reasoning
        }
        cache_manager.set(cache_key, result)
        return result
    
    def _extract_changes(self, text: str, game: str) -> List[Dict]:
        """Extract stat changes from patch notes text"""
        changes = []
        pattern1 = r'(\w+(?:\s+\w+)?)\s*:?\s*([A-Za-z\s]+)\s+(\d+(?:/\d+)*)\s*(?:→|->|to)\s*(\d+(?:/\d+)*)'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            character = match.group(1).strip()
            stat = match.group(2).strip()
            before = match.group(3)
            after = match.group(4)
            impact = self._determine_impact(stat, before, after)
            changes.append({
                "character": character, "stat": stat, "before": before, "after": after, "impact": impact
            })
        
        pattern2 = r'(\w+(?:\s+\w+)?)\s*:?\s*([A-Za-z\s]+)\s+(increased|decreased|reduced|buffed|nerfed)'
        matches2 = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches2:
            character = match.group(1).strip()
            stat = match.group(2).strip()
            direction = match.group(3).lower()
            impact = "Stronger" if direction in ['increased', 'buffed'] else "Weaker"
            changes.append({
                "character": character, "stat": stat, "before": "N/A", "after": "N/A", "impact": impact
            })
        return changes[:20]
    
    def _classify_change(self, change: Dict) -> str:
        """Classify change as buff, nerf, or neutral"""
        impact = change.get('impact', '').lower()
        if 'stronger' in impact or 'buff' in impact:
            return 'buff'
        elif 'weaker' in impact or 'nerf' in impact:
            return 'nerf'
        else:
            return 'neutral'
    
    def _assess_severity(self, change: Dict) -> str:
        """Assess severity of change"""
        before = change.get('before', 'N/A')
        after = change.get('after', 'N/A')
        if before == 'N/A' or after == 'N/A':
            return 'moderate'
        try:
            before_val = float(re.search(r'\d+', before).group())
            after_val = float(re.search(r'\d+', after).group())
            change_pct = abs((after_val - before_val) / before_val * 100)
            if change_pct < 5: return 'minor'
            elif change_pct < 15: return 'moderate'
            else: return 'major'
        except:
            return 'moderate'
    
    def _determine_impact(self, stat: str, before: str, after: str) -> str:
        """Determine if change makes character stronger or weaker"""
        try:
            before_val = float(re.search(r'\d+', before).group())
            after_val = float(re.search(r'\d+', after).group())
            positive_stats = ['damage', 'health', 'armor', 'range', 'healing']
            negative_stats = ['cooldown', 'reload', 'cost']
            stat_lower = stat.lower()
            if any(ps in stat_lower for ps in positive_stats):
                return "Stronger" if after_val > before_val else "Weaker"
            elif any(ns in stat_lower for ns in negative_stats):
                return "Stronger" if after_val < before_val else "Weaker"
            else:
                return "Changed"
        except:
            return "Changed"
    
    def _generate_verdict(self, changes: List[Dict], game: str) -> Dict:
        """Generate verdict on meta impact"""
        buffs = sum(1 for c in changes if c['type'] == 'buff')
        nerfs = sum(1 for c in changes if c['type'] == 'nerf')
        direction = "balanced"
        if buffs > nerfs * 1.5: direction = "buff-heavy"
        elif nerfs > buffs * 1.5: direction = "nerf-heavy"
        return {
            "summary": "Analizando el impacto del parche...",
            "direction": direction,
            "buff_count": buffs,
            "nerf_count": nerfs
        }

# Test
if __name__ == "__main__":
    import asyncio
    async def test():
        agent = MetaAnalystAgent()
        result = await agent.analyze_patch("League of Legends", "14.3")
        print(f"Success: {result['success']}")
    asyncio.run(test())
