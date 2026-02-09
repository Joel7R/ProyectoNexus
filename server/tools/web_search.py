"""
Live Web Search Tool
Uses DuckDuckGo for real-time gaming information retrieval
"""
from typing import Literal
from duckduckgo_search import DDGS


# Domain filters by search type - Expanded for better coverage
DOMAIN_FILTERS = {
    "news": [
        "ign.com", "gamespot.com", "kotaku.com", "polygon.com", "pcgamer.com", 
        "eurogamer.net", "rockpapershotgun.com", "gematsu.com", "videogameschronicle.com",
        "3djuegos.com", "meristation.as.com", "vandal.elespanol.com", "hobbyconsolas.com",
        "vidaextra.com", "elotrolado.net", "gamesradar.com", "gameinformer.com", 
        "theverge.com", "dualshockers.com", "videogamer.com"
    ],
    "wiki": [
        "fextralife.com", "wiki.gg", "fandom.com", "eliteguias.com",
        "leagueoflegends.fandom.com", "genshin-impact.fandom.com", "eldenring.wiki.fextralife.com",
        "icy-veins.com", "mobafire.com", "u.gg", "op.gg", "wowhead.com", "game8.co",
        "maxroll.gg", "genshin.gg", "hoyolab.com", "metasrc.com", "tracker.gg", "vlr.gg",
        "primagames.com", "gamepressure.com", "powerpyx.com", "mapgenie.io", "gamerant.com",
        "thegamer.com", "gameskinny.com", "polygon.com/guides", "rockpapershotgun.com/guides"
    ],
    "forum": [
        "reddit.com/r/", "reddit.com", "gamefaqs.gamespot.com", "forums.unrealengine.com",
        "resetera.com", "neogaf.com", "steamcommunity.com/app", "boards.greenheartgames.com"
    ]
}

# Bilingual mapping for query expansion
TRANSLATIONS = {
    "noticias": ["news", "updates"],
    "parche": ["patch notes", "update"],
    "guía": ["guide", "walkthrough"],
    "estrategia": ["strategy", "meta"],
    "trucos": ["cheats", "tips"],
    "lanzamiento": ["release date", "launch"],
    "requisitos": ["requirements", "specs"],
    "mejor": ["best", "top tier"],
    "expedition 33": ["Clair Obscur: Expedition 33", "Expedition 33 gameplay preview"],
    "clair obscur": ["Clair Obscur: Expedition 33"]
}

async def live_web_search(
    query: str,
    search_type: Literal["news", "wiki", "forum"] = "wiki",
    max_results: int = 15
) -> list[dict]:
    """
    Search the web for gaming information using DuckDuckGo with bilingual optimization.
    """
    import asyncio
    
    try:
        ddgs = DDGS()
        
        # 1. Gaming Context Reinforcement
        # Always ensure 'gaming' or 'video game' is in the subconscious of the search
        gaming_query = f"{query} gaming video game"
        
        # 2. Bilingual Query Expansion (Smart Spanish -> English bridge)
        # Many gaming insights are only in English
        query_words = query.lower().split()
        english_terms = []
        for word in query_words:
            if word in TRANSLATIONS:
                english_terms.extend(TRANSLATIONS[word])
        
        if english_terms:
            # Create a combined query that covers both languages
            search_keywords = f"{gaming_query} {' '.join(english_terms)}"
        else:
            # Ensure we use the gaming_query anyway
            search_keywords = gaming_query
            
        # 3. Domain Hints (Not strictly limited, but suggested)
        domains = DOMAIN_FILTERS.get(search_type, [])
        site_hints = ""
        if domains:
            # We use site: hints for the top 5 relevant sites to boost them
            site_hints = " OR ".join([f"site:{d}" for d in domains[:5]])
        
        final_query = f"{search_keywords} ({site_hints})" if site_hints else search_keywords
        
        # Execute search in a thread
        def do_search():
            # Increase results to ensure enough quality after filtering
            fetch_count = max_results * 3 
            if search_type == "news":
                return list(ddgs.news(
                    keywords=search_keywords,
                    max_results=fetch_count,
                    timelimit="m" 
                ))
            else:
                return list(ddgs.text(
                    keywords=final_query,
                    max_results=fetch_count
                ))

        raw_results = await asyncio.to_thread(do_search)
        
        # 4. Filter and Rank Results
        results = []
        # Get the primary game name to ensure strong relevance
        # If it's "Gaming Industry", we are more lenient
        game_context = query.split()[0].lower()
        is_industry_search = "industry" in query.lower() or "noticias" in query.lower()

        for r in raw_results:
            url = r.get("href") or r.get("url", "")
            title = r.get("title", "").lower()
            snippet = (r.get("body") or r.get("description", "")).lower()
            
            # Score result based on domain authority and relevance
            score = 0
            
            # Domain check - HEAVY weight for expert sources
            is_gaming_domain = any(domain in url.lower() for domain in domains)
            if is_gaming_domain:
                score += 40  # Massive boost for expert sources
            
            # Sub-domain specificity
            if "fandom.com" in url.lower() and game_context in url.lower():
                score += 15
            
            # Strict Game Name check (Crucial to avoid "Act 3" of the wrong game)
            if game_context in title:
                score += 10
            elif game_context in snippet:
                score += 5
            elif not is_industry_search:
                # If searching for a specific game and it's NOT mentioned, it's likely noise
                score -= 10
                
            # If it's a known gaming news site but for a general topic, it still has value
            if is_gaming_domain and is_industry_search:
                score += 5
                
            # Penality for common non-gaming noise if it leaked through
            noise_words = ["jewelry", "cooking", "travel", "politics"]
            if any(noise in title or noise in snippet for noise in noise_words):
                score -= 20

            results.append({
                "title": r.get("title", ""),
                "url": url,
                "snippet": r.get("body") or r.get("description", ""),
                "score": score,
                "is_priority": is_gaming_domain
            })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:max_results]
        
    except Exception as e:
        print(f"Web search error: {e}")
        return []


async def search_gaming_news(game: str, topic: str = "") -> list[dict]:
    """Convenience function for news search"""
    query = f"{game} {topic} news update patch".strip()
    return await live_web_search(query, search_type="news")


async def search_gaming_builds(game: str, character: str = "") -> list[dict]:
    """Convenience function for build/meta search"""
    query = f"{game} {character} build meta tier guide".strip()
    return await live_web_search(query, search_type="wiki")


async def search_gaming_guides(game: str, topic: str) -> list[dict]:
    """Convenience function for guide search"""
    query = f"{game} {topic} guide walkthrough how to".strip()
    return await live_web_search(query, search_type="wiki")
