"""
LangGraph Workflow for Gaming Nexus
Orchestrates agent flow with state persistence
"""
import asyncio
from typing import AsyncGenerator, Any, Literal
from dataclasses import dataclass

from langgraph.graph import StateGraph, END

from .state import ConversationState
from .orchestrator import IntentOrchestrator, IntentResult
from .news_scout import NewsScoutAgent
from .tactician import TacticianAgent
from .guide_navigator import GuideNavigatorAgent


@dataclass
class GraphState:
    """Internal state for the graph execution"""
    user_message: str
    intent: IntentResult | None = None
    result: dict | None = None
    error: str | None = None


class GamingNexusGraph:
    """
    LangGraph-based workflow for Gaming Nexus.
    Routes user queries to specialized agents based on intent.
    """
    
    def __init__(self):
        self.orchestrator = IntentOrchestrator()
        self.news_scout = NewsScoutAgent()
        self.tactician = TacticianAgent()
        self.guide_navigator = GuideNavigatorAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Define the graph with state schema
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("news_scout", self._news_scout_node)
        workflow.add_node("tactician", self._tactician_node)
        workflow.add_node("guide_navigator", self._guide_navigator_node)
        workflow.add_node("format_response", self._format_response_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_intent")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "analyze_intent",
            self._route_by_category,
            {
                "news": "news_scout",
                "build": "tactician",
                "guide": "guide_navigator"
            }
        )
        
        # All agents lead to format_response
        workflow.add_edge("news_scout", "format_response")
        workflow.add_edge("tactician", "format_response")
        workflow.add_edge("guide_navigator", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    async def _analyze_intent_node(self, state: dict) -> dict:
        """Analyze user intent"""
        context = state.get("context", "")
        intent = await self.orchestrator.analyze(state["user_message"], context)
        state["intent"] = intent
        return state
    
    def _route_by_category(self, state: dict) -> Literal["news", "build", "guide"]:
        """Route to appropriate agent based on category"""
        intent = state.get("intent")
        if intent:
            return intent.category
        return "build"  # Default
    
    async def _news_scout_node(self, state: dict) -> dict:
        """Execute NewsScout agent"""
        intent = state["intent"]
        result = await self.news_scout.search(
            game=intent.game,
            query=intent.search_query,
            version=intent.version
        )
        state["agent_result"] = {
            "type": "news",
            "summary": result.summary,
            "artifact": result.artifact,
            "sources": result.sources
        }
        return state
    
    async def _tactician_node(self, state: dict) -> dict:
        """Execute Tactician agent"""
        intent = state["intent"]
        result = await self.tactician.analyze(
            game=intent.game,
            query=intent.search_query,
            version=intent.version
        )
        state["agent_result"] = {
            "type": "build",
            "summary": result.summary,
            "artifact": result.artifact,
            "sources": result.sources,
            "items": result.items
        }
        return state
    
    async def _guide_navigator_node(self, state: dict) -> dict:
        """Execute GuideNavigator agent"""
        intent = state["intent"]
        result = await self.guide_navigator.find_solution(
            game=intent.game,
            query=intent.search_query
        )
        state["agent_result"] = {
            "type": "guide",
            "summary": result.summary,
            "artifact": result.artifact,
            "sources": result.sources
        }
        return state
    
    async def _format_response_node(self, state: dict) -> dict:
        """Format final response"""
        agent_result = state.get("agent_result", {})
        intent = state.get("intent")
        
        state["final_response"] = {
            "message": agent_result.get("summary", "Búsqueda completada."),
            "artifact": agent_result.get("artifact"),
            "sources": agent_result.get("sources", []),
            "context": {
                "game": intent.game if intent else None,
                "category": intent.category if intent else None,
                "version": intent.version if intent else None
            }
        }
        return state
    
    async def astream(
        self, 
        message: str, 
        conversation_state: ConversationState
    ) -> AsyncGenerator[dict, None]:
        """
        Stream events from graph execution.
        Yields thinking steps and final result.
        """
        
        # Initial state
        state = {
            "user_message": message,
            "context": conversation_state.get_context_summary()
        }
        
        # Yield thinking event
        yield {
            "type": "thinking",
            "content": "Analizando tu solicitud..."
        }
        
        # Run intent analysis
        state = await self._analyze_intent_node(state)
        intent = state["intent"]
        
        yield {
            "type": "thinking",
            "content": f"Detectado: {intent.game} | {intent.category} | Confianza: {intent.confidence:.0%}"
        }
        
        # Route to agent
        category = self._route_by_category(state)
        
        # Handle REJECT state (Non-gaming query)
        if intent.game.upper() == "REJECT":
            yield {
                "type": "thinking",
                "content": "Aviso: Consulta fuera de contexto detectada."
            }
            state["agent_result"] = {
                "type": "reject",
                "summary": f"Lo siento, pero '{message}' no parece estar relacionado con videojuegos. Mi especialidad es Gaming Nexus y solo puedo ayudarte con temas del mundo del gaming.\n\n{intent.search_query}",
                "artifact": {"type": "info", "title": "Fuera de Contexto", "content": "Por favor, realiza consultas relacionadas con videojuegos."},
                "sources": []
            }
        else:
            agent_names = {
                "news": "NewsScout - Rastreando noticias...",
                "build": "Tactician - Analizando meta y builds...",
                "guide": "GuideNavigator - Buscando guías..."
            }
            
            yield {
                "type": "thinking",
                "content": agent_names.get(category, "Procesando...")
            }
            
            yield {
                "type": "thinking",
                "content": agent_names.get(category, "Procesando...")
            }
            
            # Execute agent
            if category == "news":
                yield {"type": "thinking", "content": "NewsScout: Buscando noticias en tiempo real..."}
                state = await self._news_scout_node(state)
            elif category == "build":
                yield {"type": "thinking", "content": "Tactician: Analizando el meta y builds recomendadas..."}
                state = await self._tactician_node(state)
            else:
                yield {"type": "thinking", "content": "GuideNavigator: Consultando wikis y guías especializadas..."}
                state = await self._guide_navigator_node(state)
        
        yield {
            "type": "thinking", 
            "content": "Formateando resultados..."
        }
        
        # Format response
        state = await self._format_response_node(state)
        
        # Update conversation state
        final = state["final_response"]
        conversation_state.update_context(
            game=final["context"].get("game"),
            category=final["context"].get("category"),
            version=final["context"].get("version"),
            items=state.get("agent_result", {}).get("items", [])
        )
        
        conversation_state.add_message(
            role="assistant",
            content=final["message"],
            artifact=final["artifact"],
            sources=final["sources"]
        )
        
        # Yield final response
        yield {
            "type": "response",
            "content": final["message"],
            "artifact": final["artifact"],
            "sources": final["sources"]
        }
