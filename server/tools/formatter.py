"""
Artifact Formatter Tool
Transforms raw data into structured JSON schemas for frontend
"""
from typing import Literal
from datetime import datetime


def format_to_artifact(
    data: dict,
    template_type: Literal["table", "build", "guide", "time", "price", "lore"]
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
    elif template_type == "time":
        return _format_time_artifact(data, base_artifact)
    elif template_type == "price":
        return _format_price_artifact(data, base_artifact)
    elif template_type == "lore":
        return _format_lore_artifact(data, base_artifact)
    else:
        return {**base_artifact, "data": data}


def _format_table_artifact(data: dict, base: dict) -> dict:
    """Format data as a table artifact (for news, comparisons)"""
    
    items = data.get("items", [])
    
    # Determine columns from first item
    if items:
        # Sort logic: if 'Game' is present, put it first
        keys = list(items[0].keys())
        if "Game" in keys:
            keys.remove("Game")
            columns = ["Game"] + keys
        else:
            columns = keys
    else:
        columns = ["title", "date", "description", "url"]
    
    return {
        **base,
        "display": "table",
        "title": data.get("title", "Tabla de Datos"),
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


def _format_time_artifact(data: dict, base: dict) -> dict:
    """Format data as HLTB time bars artifact with strict schema"""
    # Validate and ensure all required fields exist
    marathon_mode = data.get("marathon_mode", {})
    
    return {
        **base,
        "display": "time_tracker",
        "game": str(data.get("game", "Unknown")),
        "image": data.get("image"),
        "times": {
            "main": float(data.get("main_story", 0)),
            "extra": float(data.get("main_extras", 0)),
            "completionist": float(data.get("completionist", 0))
        },
        "marathon_mode": {
            "hours_per_day": float(marathon_mode.get("hours_per_day", 3.0)),
            "days_main": float(marathon_mode.get("days_main", 0)),
            "days_extras": float(marathon_mode.get("days_extras", 0)),
            "days_completionist": float(marathon_mode.get("days_completionist", 0)),
            "verdict": str(marathon_mode.get("verdict", "N/A"))
        }
    }


def _format_price_artifact(data: dict, base: dict) -> dict:
    """Format data as Price Hunter artifact with strict best deal calculation"""
    deals = data.get("deals", [])
    
    # Recalculate is_best to ensure correctness
    if deals:
        min_price = min(d.get("price", float('inf')) for d in deals)
        for deal in deals:
            is_best = deal.get("price", float('inf')) == min_price
            deal["is_best"] = is_best
            if is_best:
                deal["highlight"] = True
                deal["color"] = "#39ff14"  # Neon Green
            else:
                deal["highlight"] = False
                deal.pop("color", None)
    
    # Calculate savings
    if len(deals) > 1:
        prices = [d.get("price", 0) for d in deals]
        savings = max(prices) - min(prices)
    else:
        savings = 0.0
            
    return {
        **base,
        "display": "price_comparison",
        "game": str(data.get("game", "Unknown")),
        "best_price": float(min(d.get("price", 0) for d in deals)) if deals else 0.0,
        "currency": str(data.get("currency", "USD")),
        "deals": deals,
        "savings": round(float(savings), 2)
    }


def _format_lore_artifact(data: dict, base: dict) -> dict:
    """Format data as Lore Master artifact with cleaned Mermaid content"""
    mermaid_raw = data.get("mermaid_graph", "")
    
    # Clean Mermaid content - remove markdown code blocks
    mermaid_clean = mermaid_raw.replace("```mermaid", "").replace("```", "").strip()
    
    # Ensure it starts with graph declaration
    if mermaid_clean and not mermaid_clean.startswith("graph"):
        mermaid_clean = "graph TD\n" + mermaid_clean
    
    return {
        **base,
        "display": "lore_graph",
        "title": str(data.get("title", "Lore Map")),
        "mermaid_content": mermaid_clean,
        "spoiler_level": str(data.get("spoiler_level", "light")),
        "nodes": data.get("nodes", []),
        "summary": str(data.get("summary", ""))
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
