"""
HowLongToBeat Search Tool
Searches game completion times using DuckDuckGo with site filter
"""
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
try:
    from ddgs import DDGS
except ImportError:
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
    """
    # Normalize game name for cache
    cache_key = game_name.lower().strip()
    
    # Check cache first
    cache = load_cache()
    if cache_key in cache and is_cache_valid(cache[cache_key]):
        print(f"[HLTB] Cache hit for '{game_name}'")
        return cache[cache_key]
    
    print(f"[HLTB] Searching HowLongToBeat for '{game_name}'...")
    
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
        # Strictly search with site filter
        with DDGS() as ddgs:
            query = f"site:howlongtobeat.com {game_name}"
            results = list(ddgs.text(query, max_results=3))
        
        if not results:
            print(f"[HLTB] No results found on site for '{game_name}'")
            return result
        
        # Parse results to extract times
        all_text = ""
        for r in results:
            all_text += r.get('body', '') + " " + r.get('title', '') + " "
        
        # Refined patterns for HLTB specific display strings
        main_patterns = [
            r'Main\s*Story[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
            r'Story[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
        ]
        extras_patterns = [
            r'Main\s*\+\s*Extras?[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
            r'Extras[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
        ]
        comp_patterns = [
            r'Completionist[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
            r'100%[:\s]*(\d+(?:\.\d+)?)\s*(?:Hours|h)',
        ]

        def find_first_match(patterns, text):
            for p in patterns:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    return float(m.group(1))
            return None

        result['main_story'] = find_first_match(main_patterns, all_text)
        result['main_extras'] = find_first_match(extras_patterns, all_text)
        result['completionist'] = find_first_match(comp_patterns, all_text)
        
        # Mark as found if we got at least one metric
        result['found'] = any([
            result['main_story'],
            result['main_extras'],
            result['completionist']
        ])
        
        if result['found']:
            print(f"[HLTB] Data acquired: Main={result['main_story']}h, Extras={result['main_extras']}h, 100%={result['completionist']}h")
            cache[cache_key] = result
            save_cache(cache)
        else:
            print(f"[HLTB] Could not find specific HLTB metrics in snippets for '{game_name}'")
        
    except Exception as e:
        print(f"[HLTB] Error: {e}")
    
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
