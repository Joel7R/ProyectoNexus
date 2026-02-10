"""
MetaAnalyst Agent
Analyzes game patch notes and predicts meta impact
"""
from typing import Dict, List, Any
from duckduckgo_search import DDGS
import re

class MetaAnalystAgent:
    """Agent for patch note analysis and meta prediction"""
    
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
        
        Args:
            game: Game name
            patch_version: Specific patch (optional)
            main_character: Filter by character (optional)
            
        Returns:
            Patch analysis with buff/nerf classification
        """
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
        
        ddgs = DDGS()
        changes = []
        
        try:
            results = ddgs.text(query, max_results=5)
            
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
                "message": f"No patch data found for {game} {patch_version or 'latest'}",
                "reasoning": reasoning
            }
        
        # Classify changes
        for change in changes:
            change['type'] = self._classify_change(change)
            change['severity'] = self._assess_severity(change)
        
        # Generate verdict
        verdict = self._generate_verdict(changes, game)
        
        return {
            "success": True,
            "game": game,
            "patch": patch_version or "Latest",
            "changes": changes,
            "verdict": verdict,
            "reasoning": reasoning
        }
    
    def _extract_changes(self, text: str, game: str) -> List[Dict]:
        """Extract stat changes from patch notes text"""
        changes = []
        
        # Look for patterns like:
        # "Yasuo: Q damage 20/40/60 → 15/35/55"
        # "Health increased from 500 to 550"
        # "Cooldown reduced from 10s to 8s"
        
        # Pattern 1: Character: Stat value → value
        pattern1 = r'(\w+(?:\s+\w+)?)\s*:?\s*([A-Za-z\s]+)\s+(\d+(?:/\d+)*)\s*(?:→|->|to)\s*(\d+(?:/\d+)*)'
        
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        
        for match in matches:
            character = match.group(1).strip()
            stat = match.group(2).strip()
            before = match.group(3)
            after = match.group(4)
            
            # Determine impact
            impact = self._determine_impact(stat, before, after)
            
            change = {
                "character": character,
                "stat": stat,
                "before": before,
                "after": after,
                "impact": impact
            }
            
            changes.append(change)
        
        # Pattern 2: Stat increased/decreased/reduced
        pattern2 = r'(\w+(?:\s+\w+)?)\s*:?\s*([A-Za-z\s]+)\s+(increased|decreased|reduced|buffed|nerfed)'
        
        matches2 = re.finditer(pattern2, text, re.IGNORECASE)
        
        for match in matches2:
            character = match.group(1).strip()
            stat = match.group(2).strip()
            direction = match.group(3).lower()
            
            impact = "Stronger" if direction in ['increased', 'buffed'] else "Weaker"
            
            change = {
                "character": character,
                "stat": stat,
                "before": "N/A",
                "after": "N/A",
                "impact": impact
            }
            
            changes.append(change)
        
        return changes[:20]  # Limit to 20 changes
    
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
            # Extract first number from each
            before_val = float(re.search(r'\d+', before).group())
            after_val = float(re.search(r'\d+', after).group())
            
            # Calculate percentage change
            change_pct = abs((after_val - before_val) / before_val * 100)
            
            if change_pct < 5:
                return 'minor'
            elif change_pct < 15:
                return 'moderate'
            else:
                return 'major'
        except:
            return 'moderate'
    
    def _determine_impact(self, stat: str, before: str, after: str) -> str:
        """Determine if change makes character stronger or weaker"""
        try:
            # Extract first number
            before_val = float(re.search(r'\d+', before).group())
            after_val = float(re.search(r'\d+', after).group())
            
            # Stats where higher is better
            positive_stats = ['damage', 'health', 'armor', 'range', 'healing']
            # Stats where lower is better
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
        """Generate AI verdict on meta impact"""
        # Count buffs vs nerfs
        buffs = sum(1 for c in changes if c['type'] == 'buff')
        nerfs = sum(1 for c in changes if c['type'] == 'nerf')
        
        # Determine overall direction
        if buffs > nerfs * 1.5:
            direction = "buff-heavy"
            summary = "This patch brings significant buffs across the board."
        elif nerfs > buffs * 1.5:
            direction = "nerf-heavy"
            summary = "This patch focuses on toning down overperforming elements."
        else:
            direction = "balanced"
            summary = "This patch aims for balance with mixed adjustments."
        
        # Get affected characters
        characters = list(set(c['character'] for c in changes))
        
        # Meta shift prediction
        if direction == "buff-heavy":
            meta_shift = "Expect increased diversity in viable picks."
        elif direction == "nerf-heavy":
            meta_shift = "Meta will shift away from previously dominant strategies."
        else:
            meta_shift = "Minor meta adjustments, core strategies remain viable."
        
        # Predict tier changes
        major_changes = [c for c in changes if c['severity'] == 'major']
        
        if major_changes:
            tier_prediction = "S/A tier shifts expected"
        else:
            tier_prediction = "Minimal tier changes"
        
        return {
            "summary": summary,
            "meta_shift": meta_shift,
            "direction": direction,
            "affected_characters": characters[:10],  # Top 10
            "tier_prediction": tier_prediction,
            "buff_count": buffs,
            "nerf_count": nerfs
        }

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = MetaAnalystAgent()
        
        print("\n=== Patch Analysis ===")
        result = await agent.analyze_patch("League of Legends", "14.3")
        
        if result['success']:
            print(f"\nGame: {result['game']}")
            print(f"Patch: {result['patch']}")
            print(f"\nChanges: {len(result['changes'])}")
            
            for change in result['changes'][:5]:
                print(f"\n{change['character']} - {change['stat']}")
                print(f"  {change['before']} → {change['after']}")
                print(f"  Type: {change['type'].upper()} ({change['severity']})")
            
            print(f"\n=== Verdict ===")
            print(f"{result['verdict']['summary']}")
            print(f"Meta: {result['verdict']['meta_shift']}")
            print(f"Buffs: {result['verdict']['buff_count']} | Nerfs: {result['verdict']['nerf_count']}")
        else:
            print(f"Error: {result['message']}")
    
    asyncio.run(test())
