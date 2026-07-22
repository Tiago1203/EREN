"""Tool Router - Enrutador de herramientas."""

from __future__ import annotations

from typing import Any

from core.PHASE_2.ai.tools.models import ToolCategory, ToolDefinition
from core.PHASE_2.ai.tools.registry import ToolRegistry, get_registry


class ToolRouter:
    """
    Enrutador de herramientas.
    
    Selecciona la herramienta más apropiada según
    el contexto de la solicitud.
    """

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self._registry = registry or get_registry()
        self._routes: dict[str, str] = {}  # intent -> tool_id

    def register_route(
        self,
        intent: str,
        tool_id: str,
    ) -> None:
        """Registra una ruta intent -> tool."""
        self._routes[intent.lower()] = tool_id

    def unregister_route(self, intent: str) -> bool:
        """Elimina una ruta."""
        intent_lower = intent.lower()
        if intent_lower in self._routes:
            del self._routes[intent_lower]
            return True
        return False

    def route(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> ToolDefinition | None:
        """
        Determina qué herramienta usar para una query.
        
        Args:
            query: Query o intent del usuario
            context: Contexto adicional
            
        Returns:
            Herramienta seleccionada o None
        """
        query_lower = query.lower()
        
        # 1. Buscar en rutas registradas
        for intent, tool_id in self._routes.items():
            if intent in query_lower:
                tool = self._registry.get(tool_id)
                if tool and tool.enabled:
                    return tool
        
        # 2. Buscar por categoría según keywords
        category = self._detect_category(query_lower, context)
        if category:
            tools = self._registry.list_by_category(category)
            tools = [t for t in tools if t.enabled]
            if tools:
                # Seleccionar la primera o la más específica
                return self._select_best_tool(tools, query_lower)
        
        # 3. Búsqueda general
        results = self._registry.search(query)
        if results:
            return self._select_best_tool(results, query_lower)
        
        return None

    def _detect_category(
        self,
        query: str,
        context: dict[str, Any] | None,
    ) -> ToolCategory | None:
        """Detecta la categoría más probable."""
        keywords: dict[str, list[str]] = {
            ToolCategory.DATABASE: [
                "base de datos", "database", "sql", "query",
                "buscar", "select", "insert", "datos",
            ],
            ToolCategory.VECTOR_STORE: [
                "vector", "embeddings", "similar", "búsqueda semántica",
                "semantic", "embed", "embedding",
            ],
            ToolCategory.MESSAGE_QUEUE: [
                "cola", "queue", "mensaje", "evento", "publish",
                "subscribe", "rabbitmq", "kafka",
            ],
            ToolCategory.API: [
                "api", "http", "request", "rest", "endpoint",
                "servicio", "web service",
            ],
            ToolCategory.CODE: [
                "código", "code", "python", "script", "ejecutar",
                "run", "execute", "program",
            ],
            ToolCategory.WEB: [
                "internet", "web", "http", "url", "navegar",
                "browse", "fetch", "download",
            ],
            ToolCategory.FILE: [
                "archivo", "file", "carpeta", "directorio", "leer",
                "escribir", "read", "write", "folder",
            ],
            ToolCategory.SYSTEM: [
                "sistema", "system", "comando", "shell", "bash",
                "linux", "windows", "cmd",
            ],
            ToolCategory.MCP: [
                "mcp", "model context", "protocol", "tool",
            ],
        }
        
        # Detectar por keywords
        for category, words in keywords.items():
            for word in words:
                if word in query:
                    return category
        
        # Detectar por contexto
        if context:
            if context.get("requires_database"):
                return ToolCategory.DATABASE
            if context.get("requires_vector"):
                return ToolCategory.VECTOR_STORE
            if context.get("requires_messaging"):
                return ToolCategory.MESSAGE_QUEUE
        
        return None

    def _select_best_tool(
        self,
        tools: list[ToolDefinition],
        query: str,
    ) -> ToolDefinition | None:
        """Selecciona la mejor herramienta."""
        if not tools:
            return None
        
        if len(tools) == 1:
            return tools[0]
        
        # Puntuación por relevancia
        scored = []
        for tool in tools:
            score = 0
            
            # Nombre contiene query
            if tool.name.lower() in query:
                score += 10
            
            # Descripción contiene keywords
            for word in query.split():
                if word in tool.description.lower():
                    score += 2
            
            # Tags coinciden
            for tag in tool.tags:
                if tag.lower() in query:
                    score += 5
            
            scored.append((score, tool))
        
        # Ordenar por score descendente
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return scored[0][1]

    def route_to_tool_id(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """Obtiene solo el ID de la herramienta."""
        tool = self.route(query, context)
        return tool.id if tool else None

    def get_available_routes(self) -> dict[str, str]:
        """Lista todas las rutas registradas."""
        return self._routes.copy()

    def suggest_intents(self, query: str) -> list[str]:
        """Sugiere intents para una query."""
        suggestions = []
        query_lower = query.lower()
        
        for intent in self._routes.keys():
            if any(word in query_lower for word in intent.split()):
                suggestions.append(intent)
        
        return suggestions[:5]
