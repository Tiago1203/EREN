"""Tool Registry - Registro de herramientas."""

from __future__ import annotations

from typing import Any

from core.ai.tools.models import (
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolInterface,
)


class ToolRegistry:
    """
    Registro de herramientas disponibles.
    
    Gestiona el registro, búsqueda y recuperación
    de herramientas.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._tools_by_category: dict[ToolCategory, set[str]] = {
            cat: set() for cat in ToolCategory
        }
        self._tools_by_name: dict[str, str] = {}  # name -> id
        self._implementations: dict[str, ToolInterface] = {}

    def register(
        self,
        tool: ToolDefinition,
        implementation: ToolInterface | None = None,
    ) -> None:
        """
        Registra una nueva herramienta.
        
        Args:
            tool: Definición de la herramienta
            implementation: Implementación de la herramienta
        """
        if tool.id in self._tools:
            raise ValueError(f"Tool {tool.id} ya está registrada")
        
        self._tools[tool.id] = tool
        self._tools_by_category[tool.category].add(tool.id)
        self._tools_by_name[tool.name.lower()] = tool.id
        
        if implementation:
            self._implementations[tool.id] = implementation

    def unregister(self, tool_id: str) -> bool:
        """Elimina una herramienta del registro."""
        if tool_id not in self._tools:
            return False
        
        tool = self._tools[tool_id]
        del self._tools[tool_id]
        self._tools_by_category[tool.category].discard(tool_id)
        del self._tools_by_name[tool.name.lower()]
        
        if tool_id in self._implementations:
            del self._implementations[tool_id]
        
        return True

    def get(self, tool_id: str) -> ToolDefinition | None:
        """Obtiene una herramienta por ID."""
        return self._tools.get(tool_id)

    def get_by_name(self, name: str) -> ToolDefinition | None:
        """Obtiene una herramienta por nombre."""
        tool_id = self._tools_by_name.get(name.lower())
        if tool_id:
            return self._tools.get(tool_id)
        return None

    def get_implementation(self, tool_id: str) -> ToolInterface | None:
        """Obtiene la implementación de una herramienta."""
        return self._implementations.get(tool_id)

    def list_all(self) -> list[ToolDefinition]:
        """Lista todas las herramientas."""
        return list(self._tools.values())

    def list_by_category(
        self,
        category: ToolCategory,
    ) -> list[ToolDefinition]:
        """Lista herramientas por categoría."""
        tool_ids = self._tools_by_category[category]
        return [self._tools[tid] for tid in tool_ids if tid in self._tools]

    def list_enabled(self) -> list[ToolDefinition]:
        """Lista solo herramientas habilitadas."""
        return [t for t in self._tools.values() if t.enabled]

    def search(
        self,
        query: str | None = None,
        category: ToolCategory | None = None,
        tags: list[str] | None = None,
        capability: str | None = None,
    ) -> list[ToolDefinition]:
        """
        Busca herramientas.
        
        Args:
            query: Texto a buscar en nombre/descripción
            category: Filtrar por categoría
            tags: Filtrar por etiquetas
            capability: Filtrar por capacidad
            
        Returns:
            Lista de herramientas que coinciden
        """
        results = list(self._tools.values())
        
        # Filtrar por categoría
        if category:
            results = [t for t in results if t.category == category]
        
        # Filtrar por query
        if query:
            query_lower = query.lower()
            results = [
                t for t in results
                if query_lower in t.name.lower()
                or query_lower in t.description.lower()
            ]
        
        # Filtrar por tags
        if tags:
            results = [
                t for t in results
                if any(tag in t.tags for tag in tags)
            ]
        
        # Filtrar por capacidad
        if capability:
            from core.ai.tools.models import ToolCapability
            try:
                cap = ToolCapability(capability)
                results = [t for t in results if cap in t.capabilities]
            except ValueError:
                pass
        
        # Filtrar solo habilitadas
        results = [t for t in results if t.enabled]
        
        return results

    def enable(self, tool_id: str) -> bool:
        """Habilita una herramienta."""
        tool = self._tools.get(tool_id)
        if tool:
            tool.enabled = True
            return True
        return False

    def disable(self, tool_id: str) -> bool:
        """Deshabilita una herramienta."""
        tool = self._tools.get(tool_id)
        if tool:
            tool.enabled = False
            return True
        return False

    def update(
        self,
        tool_id: str,
        updates: dict[str, Any],
    ) -> ToolDefinition | None:
        """Actualiza una herramienta."""
        tool = self._tools.get(tool_id)
        if not tool:
            return None
        
        for key, value in updates.items():
            if hasattr(tool, key):
                setattr(tool, key, value)
        
        return tool

    def count(self) -> int:
        """Cuenta el total de herramientas."""
        return len(self._tools)

    def count_by_category(self) -> dict[ToolCategory, int]:
        """Cuenta herramientas por categoría."""
        return {
            cat: len(ids)
            for cat, ids in self._tools_by_category.items()
        }


# Instancia global
_global_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """Obtiene la instancia global del registro."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def set_registry(registry: ToolRegistry) -> None:
    """Establece la instancia global del registro."""
    global _global_registry
    _global_registry = registry
