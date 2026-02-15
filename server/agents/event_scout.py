"""
EventScout Agent
Detects gaming events, conferences, and aggregates rumors
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime, timedelta
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import re
from utils.cache_manager import cache_manager

class EventScoutAgent:
    """Agent for gaming event detection and rumor aggregation"""
    
    EVENT_SOURCES = {
        "nintendo": ["nintendo.com", "twitter.com/NintendoAmerica"],
        "playstation": ["blog.playstation.com", "twitter.com/PlayStation"],
        "xbox": ["news.xbox.com", "twitter.com/Xbox"],
        "general": ["ign.com", "gamespot.com", "polygon.com", "theverge.com/gaming"]
    }
    
    EVENT_KEYWORDS = [
        "Nintendo Direct",
        "State of Play",
        "Xbox Showcase",
        "Game Awards",
        "Summer Game Fest",
        "E3",
        "Gamescom",
        "Tokyo Game Show"
    ]
    
    RUMOR_SOURCES = {
        "reliable": ["bloomberg.com", "ign.com", "gamespot.com", "eurogamer.net"],
        "moderate": ["reddit.com/r/GamingLeaksAndRumours", "twitter.com"],
        "speculation": ["4chan.org", "resetera.com"]
    }
    
    def __init__(self):
        self.name = "EventScout"
    
    async def get_upcoming_events(self, hours: int = 48) -> Dict[str, Any]:
        """
        Get gaming events scheduled in the next X hours
        """
        cache_key = f"events_{hours}h".lower()
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        print(f"[EventScout] Searching events in next {hours} hours")
        
        reasoning = [f"Buscando eventos de videojuegos en las próximas {hours}h"]
        events = []
        
        # Search for each event type
        try:
            # Rate limit throttle for DDGS
            await asyncio.sleep(1.5)
            with DDGS() as ddgs:
                for event_name in self.EVENT_KEYWORDS:
                    query = f"{event_name} 2026 date announcement"
                    
                    try:
                        results = list(ddgs.text(query, max_results=3))
                        
                        for result in results:
                            title = result.get('title', '')
                            body = result.get('body', '')
                            url = result.get('href', '')
                            
                            # Extract date mentions
                            date_match = self._extract_date(body + " " + title)
                            
                            if date_match:
                                event = {
                                    "id": event_name.lower().replace(' ', '-'),
                                    "name": event_name,
                                    "category": self._categorize_event(event_name),
                                    "estimated_date": date_match,
                                    "source_url": url,
                                    "source_title": title
                                }
                                events.append(event)
                                reasoning.append(f"Encontrado: {event_name} - {date_match}")
                                break  # Only need one result per event
                                
                    except Exception as e:
                        print(f"[EventScout] Error searching {event_name}: {e}")
                        
        except Exception as global_e:
            err_str = str(global_e)
            if "429" in err_str or "Ratelimit" in err_str:
                print(f"[EventScout] DDGS Rate Limit (429). Skipping search.")
                reasoning.append("⚠️ Búsqueda limitada por cuota de motor de búsqueda.")
                # Continue with empty events is better than crash
            else:
                print(f"[EventScout] Global search error: {global_e}")
        
        # Calculate countdowns
        for event in events:
            event['countdown_seconds'] = self._calculate_countdown(event['estimated_date'])
            event['is_live'] = self._is_event_live(event)
        
        # Filter to only events within time window
        cutoff = datetime.now() + timedelta(hours=hours)
        events = [e for e in events if self._parse_date(e['estimated_date']) <= cutoff]
        
        result = {
            "success": True,
            "events": events,
            "count": len(events),
            "reasoning": reasoning
        }
        cache_manager.set(cache_key, result)
        return result
    
    async def get_live_events(self) -> Dict[str, Any]:
        """Get currently live events"""
        cache_key = "live_events_current"
        try:
            cached = cache_manager.get(cache_key)
            if cached:
                print(f"[EventScout] Cache HIT for {cache_key}")
                return cached
                
            print(f"[EventScout] CACHE MISS for {cache_key}. Checking for live events...")
            
            all_events = await self.get_upcoming_events(hours=2)
            live_events = [e for e in all_events['events'] if e.get('is_live', False)]
            
            result = {
                "success": True,
                "live_events": live_events,
                "count": len(live_events)
            }
            cache_manager.set(cache_key, result, ttl=300) # 5 min cache
            return result
        except Exception as e:
            print(f"[EventScout] Error in get_live_events: {e}")
            return {
                "success": False,
                "live_events": [],
                "count": 0,
                "error": str(e)
            }
    
    async def get_rumors(self, event_id: str) -> Dict[str, Any]:
        """
        Get rumors and leaks for a specific event
        """
        cache_key = f"rumors_{event_id.lower().replace(' ', '_')}"
        cached = cache_manager.get(cache_key)
        if cached:
            return cached
            
        print(f"[EventScout] Gathering rumors for: {event_id}")
        
        reasoning = [f"Searching leaks for {event_id}"]
        rumors = []
        
        # Search for leaks
        event_name = event_id.replace('-', ' ').title()
        query = f"{event_name} leaks rumors 2026"
        
        try:
            # Rate limit throttle for DDGS
            await asyncio.sleep(1.5)
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
                
                for result in results:
                    title = result.get('title', '')
                    body = result.get('body', '')
                    url = result.get('href', '')
                    
                    # Determine confidence based on source
                    confidence = self._assess_confidence(url)
                    
                    # Extract rumor content
                    rumor_text = self._extract_rumor(title, body)
                    
                    if rumor_text:
                        rumor = {
                            "title": rumor_text,
                            "confidence": confidence,
                            "source": self._get_source_name(url),
                            "url": url
                        }
                        rumors.append(rumor)
                        reasoning.append(f"Found rumor: {confidence} confidence")
            
        except Exception as e:
            print(f"[EventScout] Error gathering rumors: {e}")
        
        # Sort by confidence
        rumors.sort(key=lambda x: self._confidence_score(x['confidence']), reverse=True)
        
        result = {
            "success": True,
            "event_id": event_id,
            "rumors": rumors[:10],  # Top 10
            "reasoning": reasoning
        }
        cache_manager.set(cache_key, result)
        return result
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        patterns = [
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+2026)?',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,?\s+2026)?',
            r'\d{1,2}/\d{1,2}/2026'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "TBA"
    
    def _categorize_event(self, event_name: str) -> str:
        """Categorize event type"""
        name_lower = event_name.lower()
        if 'direct' in name_lower or 'state of play' in name_lower or 'showcase' in name_lower:
            return 'direct'
        elif 'awards' in name_lower:
            return 'awards'
        elif 'trailer' in name_lower:
            return 'trailer'
        else:
            return 'conference'
    
    def _calculate_countdown(self, date_str: str) -> int:
        """Calculate seconds until event"""
        try:
            event_date = self._parse_date(date_str)
            now = datetime.now()
            delta = event_date - now
            return max(0, int(delta.total_seconds()))
        except:
            return 0
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        try:
            for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
            
            for fmt in ['%B %d', '%b %d']:
                try:
                     target_year = 2026
                     full_date_str = f"{date_str}, {target_year}"
                     return datetime.strptime(full_date_str, fmt + ", %Y")
                except:
                    continue
        except:
            pass
        return datetime.now() + timedelta(days=7)
    
    def _is_event_live(self, event: Dict) -> bool:
        """Check if event is currently live"""
        try:
            event_date = self._parse_date(event['estimated_date'])
            now = datetime.now()
            delta = abs((event_date - now).total_seconds())
            return delta < 7200
        except:
            return False
    
    def _assess_confidence(self, url: str) -> str:
        """Assess rumor confidence based on source"""
        url_lower = url.lower()
        for source in self.RUMOR_SOURCES['reliable']:
            if source in url_lower:
                return 'probable'
        for source in self.RUMOR_SOURCES['moderate']:
            if source in url_lower:
                return 'possible'
        return 'dream'
    
    def _confidence_score(self, confidence: str) -> int:
        """Convert confidence to numeric score"""
        scores = {'probable': 3, 'possible': 2, 'dream': 1}
        return scores.get(confidence, 0)
    
    def _extract_rumor(self, title: str, body: str) -> str:
        """Extract rumor text"""
        rumor_keywords = ['leak', 'rumor', 'rumour', 'allegedly', 'reportedly', 'sources say']
        text = title if any(kw in title.lower() for kw in rumor_keywords) else body
        return text[:150] + "..." if len(text) > 150 else text
    
    def _get_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            domain = match.group(1).replace('www.', '').split('.')[0]
            return domain.title()
        return "Unknown"

# Test
if __name__ == "__main__":
    import asyncio
    async def test():
        agent = EventScoutAgent()
        events = await agent.get_upcoming_events(hours=48)
        print(f"Events found: {events['count']}")
    asyncio.run(test())
