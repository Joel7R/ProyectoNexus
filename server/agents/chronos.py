"""
Chronos Agent
Provides game lore, story summaries, and character relationships
"""
from typing import Dict, List, Any
from duckduckgo_search import DDGS
import re

class ChronosAgent:
    """Agent for game lore and story information"""
    
    SPOILER_LEVELS = {
        "none": "No spoilers - basic premise only",
        "light": "Light spoilers - main plot points without major reveals",
        "full": "Full story - all details including endings"
    }
    
    LORE_SOURCES = [
        "fextralife.com",
        "ign.com/wikis",
        "gamefaqs.com",
        "reddit.com/r/",
        "wiki.gg"
    ]
    
    def __init__(self):
        self.name = "Chronos"
    
    async def get_story(
        self, 
        game_name: str, 
        spoiler_level: str = "light"
    ) -> Dict[str, Any]:
        """
        Get game story summary with spoiler control
        
        Args:
            game_name: Name of the game
            spoiler_level: "none", "light", or "full"
            
        Returns:
            Story summary with spoiler warnings
        """
        if spoiler_level not in self.SPOILER_LEVELS:
            spoiler_level = "light"
        
        print(f"[Chronos] Getting story for '{game_name}' (spoiler level: {spoiler_level})")
        
        reasoning = [
            f"Searching lore for '{game_name}'",
            f"Spoiler level: {self.SPOILER_LEVELS[spoiler_level]}"
        ]
        
        # Search for story information
        ddgs = DDGS()
        
        # Build query based on spoiler level
        if spoiler_level == "none":
            query = f"{game_name} game premise plot summary no spoilers"
        elif spoiler_level == "light":
            query = f"{game_name} game story overview main plot"
        else:  # full
            query = f"{game_name} complete story explained ending"
        
        # Add site filters
        site_filter = " OR ".join([f"site:{source}" for source in self.LORE_SOURCES])
        full_query = f"{query} ({site_filter})"
        
        try:
            results = ddgs.text(full_query, max_results=5)
            
            if not results:
                return {
                    "success": False,
                    "game": game_name,
                    "message": f"No lore found for '{game_name}'",
                    "reasoning": reasoning
                }
            
            # Compile story from results
            story_parts = []
            key_events = []
            sources = []
            
            for result in results:
                title = result.get('title', '')
                body = result.get('body', '')
                url = result.get('href', '')
                
                story_parts.append(body)
                sources.append({
                    "title": title,
                    "url": url
                })
                
                # Extract potential key events (sentences with keywords)
                event_keywords = ['battle', 'defeat', 'discover', 'reveal', 'betray', 'death', 'victory']
                sentences = body.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in event_keywords):
                        key_events.append(sentence.strip())
            
            # Combine and truncate based on spoiler level
            full_story = " ".join(story_parts)
            
            if spoiler_level == "none":
                summary = full_story[:300] + "..."
                spoiler_warnings = ["This is a spoiler-free summary"]
            elif spoiler_level == "light":
                summary = full_story[:600] + "..."
                spoiler_warnings = ["Contains light spoilers about main plot"]
            else:
                summary = full_story[:1000] + "..."
                spoiler_warnings = ["⚠️ FULL SPOILERS - Complete story details"]
            
            reasoning.append(f"Found {len(results)} sources")
            reasoning.append(f"Extracted {len(key_events)} key events")
            
            return {
                "success": True,
                "game": game_name,
                "summary": summary,
                "spoiler_level": spoiler_level,
                "key_events": key_events[:5],  # Top 5 events
                "spoiler_warnings": spoiler_warnings,
                "sources": sources,
                "reasoning": reasoning
            }
            
        except Exception as e:
            print(f"[Chronos] Error: {e}")
            return {
                "success": False,
                "game": game_name,
                "message": f"Error retrieving lore: {str(e)}",
                "reasoning": reasoning
            }
    
    async def get_character_map(self, game_name: str) -> Dict[str, Any]:
        """
        Get character relationships for a game
        
        Args:
            game_name: Name of the game
            
        Returns:
            Character data with relationship graph
        """
        print(f"[Chronos] Getting character map for '{game_name}'")
        
        reasoning = [f"Searching character information for '{game_name}'"]
        
        ddgs = DDGS()
        query = f"{game_name} characters relationships wiki"
        
        try:
            results = ddgs.text(query, max_results=5)
            
            if not results:
                return {
                    "success": False,
                    "game": game_name,
                    "message": "No character data found",
                    "reasoning": reasoning
                }
            
            # Extract character names and relationships
            characters = []
            all_text = " ".join([r.get('body', '') for r in results])
            
            # Simple character extraction (names in title case)
            # This is a simplified version - real implementation would use NLP
            potential_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', all_text)
            
            # Count occurrences to find main characters
            from collections import Counter
            name_counts = Counter(potential_names)
            main_characters = [name for name, count in name_counts.most_common(10) if count > 2]
            
            # Build character list
            for char_name in main_characters:
                characters.append({
                    "name": char_name,
                    "role": "Character",  # Would need more analysis
                    "relationships": []  # Would need relationship extraction
                })
            
            # Generate Mermaid graph
            mermaid_graph = self._generate_mermaid_graph(characters)
            
            reasoning.append(f"Found {len(characters)} main characters")
            
            return {
                "success": True,
                "game": game_name,
                "characters": characters,
                "mermaid_graph": mermaid_graph,
                "reasoning": reasoning
            }
            
        except Exception as e:
            print(f"[Chronos] Error: {e}")
            return {
                "success": False,
                "game": game_name,
                "message": f"Error retrieving characters: {str(e)}",
                "reasoning": reasoning
            }
    
    def _generate_mermaid_graph(self, characters: List[Dict]) -> str:
        """Generate Mermaid diagram for character relationships"""
        lines = ["graph TD"]
        
        for i, char in enumerate(characters):
            char_id = f"C{i}"
            char_name = char['name'].replace(' ', '_')
            lines.append(f"    {char_id}[{char_name}]")
            
            # Add relationships if available
            for rel in char.get('relationships', []):
                # Find related character
                for j, other_char in enumerate(characters):
                    if other_char['name'] == rel:
                        other_id = f"C{j}"
                        lines.append(f"    {char_id} --> {other_id}")
        
        return "\n".join(lines)

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = ChronosAgent()
        
        # Test story with different spoiler levels
        print("\n=== Story (No Spoilers) ===")
        result = await agent.get_story("Elden Ring", "none")
        if result['success']:
            print(f"Summary: {result['summary'][:200]}...")
            print(f"Warnings: {result['spoiler_warnings']}")
        
        print("\n=== Story (Light Spoilers) ===")
        result = await agent.get_story("Elden Ring", "light")
        if result['success']:
            print(f"Summary: {result['summary'][:200]}...")
            print(f"Key Events: {len(result['key_events'])}")
        
        # Test character map
        print("\n=== Character Map ===")
        char_result = await agent.get_character_map("Elden Ring")
        if char_result['success']:
            print(f"Characters: {[c['name'] for c in char_result['characters'][:5]]}")
            print(f"\nMermaid Graph:\n{char_result['mermaid_graph'][:200]}...")
    
    asyncio.run(test())
