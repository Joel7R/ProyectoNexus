"""
Conversation State Management for Gaming Nexus
Persists search history and context for follow-up questions
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Message:
    """Single message in conversation"""
    role: Literal["user", "assistant", "system", "thinking"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    artifact: dict | None = None
    sources: list[dict] | None = None


@dataclass
class SearchContext:
    """Context from previous searches for follow-up questions"""
    game: str | None = None
    category: str | None = None
    version: str | None = None
    last_items: list[dict] = field(default_factory=list)
    last_urls: list[str] = field(default_factory=list)


@dataclass
class ConversationState:
    """
    Full conversation state with history and search context.
    Enables follow-up questions like "Dime más sobre ese ítem"
    """
    messages: list[Message] = field(default_factory=list)
    search_context: SearchContext = field(default_factory=SearchContext)
    
    def add_message(
        self, 
        role: str, 
        content: str, 
        artifact: dict | None = None,
        sources: list[dict] | None = None
    ) -> None:
        """Add a new message to history"""
        self.messages.append(Message(
            role=role,
            content=content,
            artifact=artifact,
            sources=sources
        ))
    
    def get_messages(self, limit: int = 20) -> list[dict]:
        """Get recent messages as dicts for API response"""
        recent = self.messages[-limit:] if len(self.messages) > limit else self.messages
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "artifact": msg.artifact,
                "sources": msg.sources
            }
            for msg in recent
        ]
    
    def get_context_summary(self) -> str:
        """Generate context summary for the agent"""
        ctx = self.search_context
        parts = []
        
        if ctx.game:
            parts.append(f"Juego actual: {ctx.game}")
        if ctx.category:
            parts.append(f"Categoría: {ctx.category}")
        if ctx.version:
            parts.append(f"Versión/Parche: {ctx.version}")
        if ctx.last_items:
            items_str = ", ".join([item.get("name", "?") for item in ctx.last_items[:5]])
            parts.append(f"Ítems mencionados: {items_str}")
        
        return " | ".join(parts) if parts else "Sin contexto previo"
    
    def update_context(
        self,
        game: str | None = None,
        category: str | None = None,
        version: str | None = None,
        items: list[dict] | None = None,
        urls: list[str] | None = None
    ) -> None:
        """Update search context from agent results"""
        if game:
            self.search_context.game = game
        if category:
            self.search_context.category = category
        if version:
            self.search_context.version = version
        if items:
            self.search_context.last_items = items
        if urls:
            self.search_context.last_urls = urls
