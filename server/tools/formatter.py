"""
Artifact Formatter Tool
Transforms raw data into structured JSON schemas for frontend
"""
from typing import Literal
from datetime import datetime


def format_to_artifact(
    data: dict,
    template_type: Literal["table", "build", "guide"]
) -> dict:
    """
    Transform raw data into a structured artifact for the frontend.
    
    Args:
        data: Raw data from agent processing
        template_type: Type of artifact template to use
        
    Returns:
        Structured artifact JSON ready for frontend rendering
    """
    
    base_artifact = {
        "type": template_type,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    if template_type == "table":
        return _format_table_artifact(data, base_artifact)
    elif template_type == "build":
        return _format_build_artifact(data, base_artifact)
    elif template_type == "guide":
        return _format_guide_artifact(data, base_artifact)
    else:
        return {**base_artifact, "data": data}


def _format_table_artifact(data: dict, base: dict) -> dict:
    """Format data as a table artifact (for news, comparisons)"""
    
    items = data.get("items", [])
    
    # Determine columns from first item
    if items:
        columns = list(items[0].keys())
    else:
        columns = ["title", "date", "description", "url"]
    
    return {
        **base,
        "display": "table",
        "columns": [
            {"key": col, "label": col.replace("_", " ").title()}
            for col in columns
        ],
        "rows": items,
        "sortable": True,
        "filterable": True,
        "pagination": len(items) > 10
    }


def _format_build_artifact(data: dict, base: dict) -> dict:
    """Format data as a build dashboard artifact"""
    
    # Extract character info
    character = data.get("character", "Unknown")
    tier = data.get("tier", "?")
    win_rate = data.get("win_rate")
    pick_rate = data.get("pick_rate")
    
    # Format items with priority bars
    items = []
    for item in data.get("items", []):
        items.append({
            "name": item.get("name", "?"),
            "slot": item.get("slot", ""),
            "stats": item.get("stats", ""),
            "priority": item.get("priority", 3),
            "priority_bar": item.get("priority", 3) * 20  # 0-100 scale
        })
    
    # Format skills
    skills = []
    for skill in data.get("skills", []):
        skills.append({
            "name": skill.get("name", "?"),
            "description": skill.get("description", ""),
            "max_first": skill.get("max_first", False),
            "key": skill.get("key", "")
        })
    
    # Format runes/talents if available
    runes = data.get("runes", [])
    
    return {
        **base,
        "display": "build_dashboard",
        "character": {
            "name": character,
            "tier": tier,
            "tier_color": _get_tier_color(tier)
        },
        "stats": {
            "win_rate": win_rate,
            "pick_rate": pick_rate,
            "display_bars": True
        },
        "items": items,
        "skills": skills,
        "runes": runes,
        "playstyle": data.get("playstyle", ""),
        "counters": data.get("counters", []),
        "synergies": data.get("synergies", []),
        "source_warning": data.get("source_warning")
    }


def _format_guide_artifact(data: dict, base: dict) -> dict:
    """Format data as a step-by-step guide artifact"""
    
    steps = []
    for step in data.get("steps", []):
        spoiler_level = step.get("spoiler_level", "low")
        steps.append({
            "number": step.get("number", 0),
            "title": step.get("title", ""),
            "content": step.get("content", ""),
            "tip": step.get("tip"),
            "warning": step.get("warning"),
            "spoiler_level": spoiler_level,
            "collapsed": spoiler_level in ["medium", "high"],
            "hidden": spoiler_level == "high"
        })
    
    return {
        **base,
        "display": "step_guide",
        "hint": data.get("hint", ""),
        "steps": steps,
        "collectibles": data.get("collectibles", []),
        "rewards": data.get("rewards", []),
        "difficulty": data.get("difficulty", "medium"),
        "difficulty_color": _get_difficulty_color(data.get("difficulty", "medium")),
        "estimated_time": data.get("estimated_time"),
        "progressive_reveal": True
    }


def _get_tier_color(tier: str) -> str:
    """Get color for tier display"""
    tier_colors = {
        "S": "#ff0055",  # Hot pink/red
        "A": "#00f3ff",  # Cyan
        "B": "#00ff88",  # Green
        "C": "#ffcc00",  # Yellow
        "D": "#888888",  # Gray
        "F": "#ff4444"   # Red
    }
    return tier_colors.get(tier.upper() if tier else "?", "#ffffff")


def _get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty display"""
    difficulty_colors = {
        "easy": "#00ff88",
        "medium": "#ffcc00",
        "hard": "#ff8800",
        "very_hard": "#ff0055"
    }
    return difficulty_colors.get(difficulty.lower(), "#ffffff")


def create_empty_artifact(message: str = "Sin resultados") -> dict:
    """Create an empty state artifact"""
    return {
        "type": "empty",
        "display": "empty_state",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }


def create_error_artifact(error: str) -> dict:
    """Create an error state artifact"""
    return {
        "type": "error",
        "display": "error_state",
        "message": error,
        "timestamp": datetime.now().isoformat()
    }
