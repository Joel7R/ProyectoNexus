"""
HowLongToBeat Search Tool
Searches game completion times using DuckDuckGo with site filter
"""
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from duckduckgo_search import DDGS

# Cache file path
CACHE_FILE = Path(__file__).parent.parent / "cache" / "hltb_cache.json"

def load_cache() -> dict:
    """Load cached HLTB data"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    """Save HLTB data to cache"""
    CACHE_FILE.parent.mkdir(exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def is_cache_valid(cached_data: dict, max_age_days: int = 30) -> bool:
    """Check if cached data is still valid"""
    if 'cached_at' not in cached_data:
        return False
    
    cached_time = datetime.fromisoformat(cached_data['cached_at'])
    age = datetime.now() - cached_time
    return age < timedelta(days=max_age_days)

def extract_hours(text: str) -> float | None:
    """Extract hours from text like '52.5 Hours' or '52½ Hours'"""
    # Pattern for decimal hours
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    
    # Pattern for fractional hours (e.g., "52½")
    match = re.search(r'(\d+)½\s*(?:hours?|hrs?)', text, re.IGNORECASE)
    if match:
        return float(match.group(1)) + 0.5
    
    return None

def search_hltb(game_name: str) -> dict:
    """
    Search HowLongToBeat for game completion times
    
    Returns:
        {
            "game": str,
            "main_story": float | None,
            "main_extras": float | None,
            "completionist": float | None,
            "found": bool,
            "source": str
        }
    """
    # Normalize game name for cache
    cache_key = game_name.lower().strip()
    
    # Check cache first
    cache = load_cache()
    if cache_key in cache and is_cache_valid(cache[cache_key]):
        print(f"[HLTB] Cache hit for '{game_name}'")
        return cache[cache_key]
    
    print(f"[HLTB] Searching for '{game_name}'...")
    
    result = {
        "game": game_name,
        "main_story": None,
        "main_extras": None,
        "completionist": None,
        "found": False,
        "source": "howlongtobeat.com",
        "cached_at": datetime.now().isoformat()
    }
    
    try:
        # Search with DuckDuckGo
        ddgs = DDGS()
        query = f"{game_name} site:howlongtobeat.com"
        results = ddgs.text(query, max_results=5)
        
        if not results:
            print(f"[HLTB] No results found for '{game_name}'")
            return result
        
        # Parse results to extract times
        all_text = ""
        for r in results:
            all_text += r.get('body', '') + " " + r.get('title', '') + " "
        
        # Look for specific patterns
        # Main Story
        main_patterns = [
            r'main\s+story[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
            r'story[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
        ]
        for pattern in main_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                result['main_story'] = float(match.group(1))
                break
        
        # Main + Extras
        extras_patterns = [
            r'main\s*\+\s*extras?[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
            r'extras?[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
        ]
        for pattern in extras_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                result['main_extras'] = float(match.group(1))
                break
        
        # Completionist
        comp_patterns = [
            r'completionist[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
            r'100%[:\s]+(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
        ]
        for pattern in comp_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                result['completionist'] = float(match.group(1))
                break
        
        # Mark as found if we got at least one metric
        result['found'] = any([
            result['main_story'],
            result['main_extras'],
            result['completionist']
        ])
        
        if result['found']:
            print(f"[HLTB] Found data for '{game_name}': Main={result['main_story']}h, Extras={result['main_extras']}h, 100%={result['completionist']}h")
            # Save to cache
            cache[cache_key] = result
            save_cache(cache)
        else:
            print(f"[HLTB] Could not extract time data for '{game_name}'")
        
    except Exception as e:
        print(f"[HLTB] Error searching for '{game_name}': {e}")
    
    return result

# Test function
if __name__ == "__main__":
    test_games = ["Elden Ring", "Baldur's Gate 3", "Cyberpunk 2077"]
    for game in test_games:
        result = search_hltb(game)
        print(f"\n{game}:")
        print(f"  Main Story: {result['main_story']}h")
        print(f"  Main+Extras: {result['main_extras']}h")
        print(f"  Completionist: {result['completionist']}h")
