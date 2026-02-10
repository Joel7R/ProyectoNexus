"""
TimeEstimator Agent
Estimates game completion times and provides backlog management
"""
from typing import Dict, List, Any
from tools.hltb_search import search_hltb

class TimeEstimatorAgent:
    """Agent for estimating game completion times"""
    
    def __init__(self):
        self.name = "TimeEstimator"
    
    async def estimate_game_time(self, game_name: str) -> Dict[str, Any]:
        """
        Get completion time estimates for a single game
        
        Args:
            game_name: Name of the game
            
        Returns:
            Dictionary with time estimates and metadata
        """
        # Search HLTB
        hltb_data = search_hltb(game_name)
        
        if not hltb_data['found']:
            return {
                "success": False,
                "game": game_name,
                "message": f"No data found for '{game_name}'. Try a different spelling or check HowLongToBeat.com manually.",
                "reasoning": [
                    f"Searched HowLongToBeat for '{game_name}'",
                    "No completion time data found",
                    "Game may not be in HLTB database or name doesn't match"
                ]
            }
        
        # Calculate worth metrics
        worth_analysis = self._analyze_worth(hltb_data)
        
        return {
            "success": True,
            "game": game_name,
            "times": {
                "main_story": hltb_data['main_story'],
                "main_extras": hltb_data['main_extras'],
                "completionist": hltb_data['completionist']
            },
            "worth": worth_analysis,
            "source": hltb_data['source'],
            "reasoning": [
                f"Found '{game_name}' on HowLongToBeat",
                f"Main Story: {hltb_data['main_story']}h" if hltb_data['main_story'] else "Main Story: N/A",
                f"Main+Extras: {hltb_data['main_extras']}h" if hltb_data['main_extras'] else "Main+Extras: N/A",
                f"Completionist: {hltb_data['completionist']}h" if hltb_data['completionist'] else "Completionist: N/A"
            ]
        }
    
    async def calculate_backlog(self, games: List[str]) -> Dict[str, Any]:
        """
        Calculate total time for multiple games (backlog)
        
        Args:
            games: List of game names
            
        Returns:
            Dictionary with total times and breakdown
        """
        results = []
        totals = {
            "main_story": 0,
            "main_extras": 0,
            "completionist": 0
        }
        
        reasoning = [f"Calculating backlog for {len(games)} games..."]
        
        for game in games:
            hltb_data = search_hltb(game)
            
            if hltb_data['found']:
                results.append({
                    "game": game,
                    "main_story": hltb_data['main_story'],
                    "main_extras": hltb_data['main_extras'],
                    "completionist": hltb_data['completionist']
                })
                
                # Add to totals
                if hltb_data['main_story']:
                    totals['main_story'] += hltb_data['main_story']
                if hltb_data['main_extras']:
                    totals['main_extras'] += hltb_data['main_extras']
                if hltb_data['completionist']:
                    totals['completionist'] += hltb_data['completionist']
                
                reasoning.append(f"✓ {game}: {hltb_data['completionist'] or hltb_data['main_extras'] or hltb_data['main_story']}h")
            else:
                reasoning.append(f"✗ {game}: No data found")
        
        # Calculate days at different paces
        time_estimates = {
            "casual_2h_per_day": round(totals['completionist'] / 2, 1) if totals['completionist'] else None,
            "moderate_4h_per_day": round(totals['completionist'] / 4, 1) if totals['completionist'] else None,
            "hardcore_8h_per_day": round(totals['completionist'] / 8, 1) if totals['completionist'] else None
        }
        
        return {
            "success": True,
            "total_games": len(games),
            "found_games": len(results),
            "games": results,
            "totals": totals,
            "time_estimates": time_estimates,
            "reasoning": reasoning
        }
    
    async def marathon_mode(self, game_name: str, hours_per_day: float) -> Dict[str, Any]:
        """
        Calculate how many days it will take to complete a game
        
        Args:
            game_name: Name of the game
            hours_per_day: Hours available per day
            
        Returns:
            Dictionary with completion estimates
        """
        hltb_data = search_hltb(game_name)
        
        if not hltb_data['found']:
            return {
                "success": False,
                "game": game_name,
                "message": f"No data found for '{game_name}'"
            }
        
        # Calculate days for each completion level
        estimates = {}
        
        if hltb_data['main_story']:
            estimates['main_story_days'] = round(hltb_data['main_story'] / hours_per_day, 1)
        
        if hltb_data['main_extras']:
            estimates['main_extras_days'] = round(hltb_data['main_extras'] / hours_per_day, 1)
        
        if hltb_data['completionist']:
            estimates['completionist_days'] = round(hltb_data['completionist'] / hours_per_day, 1)
        
        reasoning = [
            f"Marathon Mode for '{game_name}'",
            f"Playing {hours_per_day}h per day:",
        ]
        
        if 'main_story_days' in estimates:
            reasoning.append(f"  Main Story: {estimates['main_story_days']} days ({hltb_data['main_story']}h)")
        if 'main_extras_days' in estimates:
            reasoning.append(f"  Main+Extras: {estimates['main_extras_days']} days ({hltb_data['main_extras']}h)")
        if 'completionist_days' in estimates:
            reasoning.append(f"  100% Complete: {estimates['completionist_days']} days ({hltb_data['completionist']}h)")
        
        return {
            "success": True,
            "game": game_name,
            "hours_per_day": hours_per_day,
            "estimates": estimates,
            "reasoning": reasoning
        }
    
    def _analyze_worth(self, hltb_data: dict, price: float = 60.0) -> dict:
        """
        Analyze if game is worth the price based on hours
        
        Args:
            hltb_data: HLTB data dictionary
            price: Game price (default $60)
            
        Returns:
            Worth analysis dictionary
        """
        # Use completionist time if available, otherwise main+extras, otherwise main
        hours = hltb_data['completionist'] or hltb_data['main_extras'] or hltb_data['main_story']
        
        if not hours:
            return {
                "verdict": "Unknown",
                "reason": "No time data available"
            }
        
        cost_per_hour = round(price / hours, 2)
        
        # Determine verdict
        if cost_per_hour < 0.50:
            verdict = "Excellent Value"
            emoji = "💎"
        elif cost_per_hour < 1.00:
            verdict = "Good Value"
            emoji = "👍"
        elif cost_per_hour < 2.00:
            verdict = "Fair Value"
            emoji = "👌"
        else:
            verdict = "Expensive"
            emoji = "💸"
        
        return {
            "verdict": verdict,
            "emoji": emoji,
            "cost_per_hour": cost_per_hour,
            "total_hours": hours,
            "price": price,
            "reason": f"${price} ÷ {hours}h = ${cost_per_hour}/hour"
        }

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = TimeEstimatorAgent()
        
        # Test single game
        result = await agent.estimate_game_time("Elden Ring")
        print("\n=== Single Game ===")
        print(result)
        
        # Test backlog
        backlog = await agent.calculate_backlog(["Elden Ring", "Baldur's Gate 3", "Cyberpunk 2077"])
        print("\n=== Backlog ===")
        print(backlog)
        
        # Test marathon mode
        marathon = await agent.marathon_mode("Elden Ring", 2.5)
        print("\n=== Marathon Mode ===")
        print(marathon)
    
    asyncio.run(test())
