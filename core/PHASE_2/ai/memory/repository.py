"""Memory Repository - Repositorio de memoria."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_2.ai.memory.models import MemoryItem, MemoryQuery, MemoryType

if TYPE_CHECKING:
    from core.PHASE_2.ai.memory.models import MemoryResult, MemorySummary


class MemoryRepository(ABC):
    """Repositorio abstracto para memoria."""

    @abstractmethod
    def save(self, item: MemoryItem) -> None:
        """Guarda un ítem de memoria."""
        ...

    @abstractmethod
    def get(self, memory_id: str) -> MemoryItem | None:
        """Obtiene un ítem por ID."""
        ...

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Elimina un ítem."""
        ...

    @abstractmethod
    def query(self, query: MemoryQuery) -> MemoryResult:
        """Busca memorias."""
        ...

    @abstractmethod
    def count(self, memory_type: MemoryType | None = None) -> int:
        """Cuenta memorias por tipo."""
        ...

    @abstractmethod
    def get_summary(self, tenant_id: str) -> MemorySummary:
        """Obtiene resumen de memorias."""
        ...

    @abstractmethod
    def get_by_type(
        self,
        memory_type: MemoryType,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[MemoryItem]:
        """Obtiene memorias por tipo."""
        ...

    @abstractmethod
    def get_oldest(
        self,
        memory_type: MemoryType,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """Obtiene las memorias más antiguas."""
        ...

    @abstractmethod
    def get_least_accessed(
        self,
        memory_type: MemoryType,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """Obtiene las memorias menos accedidas."""
        ...


class InMemoryMemoryRepository(MemoryRepository):
    """Repositorio en memoria para desarrollo y testing."""

    def __init__(self) -> None:
        self._items: dict[str, MemoryItem] = {}
        self._by_type: dict[MemoryType, set[str]] = {t: set() for t in MemoryType}
        self._by_user: dict[str, set[str]] = {}

    def save(self, item: MemoryItem) -> None:
        """Guarda un ítem de memoria."""
        old_type = None
        old_user = None
        
        if item.id in self._items:
            old_item = self._items[item.id]
            old_type = old_item.memory_type
            if old_item.user_id:
                old_user = old_item.user_id
                self._by_user[old_item.user_id].discard(item.id)
        
        self._items[item.id] = item
        
        # Index por tipo
        if old_type:
            self._by_type[old_type].discard(item.id)
        self._by_type[item.memory_type].add(item.id)
        
        # Index por usuario
        if item.user_id:
            if item.user_id not in self._by_user:
                self._by_user[item.user_id] = set()
            self._by_user[item.user_id].add(item.id)

    def get(self, memory_id: str) -> MemoryItem | None:
        """Obtiene un ítem por ID."""
        item = self._items.get(memory_id)
        if item:
            item.access()
        return item

    def delete(self, memory_id: str) -> bool:
        """Elimina un ítem."""
        if memory_id in self._items:
            item = self._items[memory_id]
            self._by_type[item.memory_type].discard(memory_id)
            if item.user_id and item.user_id in self._by_user:
                self._by_user[item.user_id].discard(memory_id)
            del self._items[memory_id]
            return True
        return False

    def query(self, query: MemoryQuery) -> MemoryResult:
        """Busca memorias."""
        from datetime import datetime
        import time
        
        start = time.time()
        
        results: list[MemoryItem] = []
        
        # Filtrar por tipo
        if query.memory_type:
            ids = self._by_type[query.memory_type]
            items = [self._items[mid] for mid in ids if mid in self._items]
        else:
            items = list(self._items.values())
        
        # Filtrar por usuario
        if query.user_id:
            if query.user_id in self._by_user:
                user_ids = self._by_user[query.user_id]
                items = [i for i in items if i.id in user_ids]
            else:
                items = []
        
        # Filtrar por conversación
        if query.conversation_id:
            items = [i for i in items if i.conversation_id == query.conversation_id]
        
        # Filtrar por sesión
        if query.session_id:
            items = [i for i in items if i.session_id == query.session_id]
        
        # Filtrar por tenant
        if query.tenant_id:
            items = [i for i in items if i.tenant_id == query.tenant_id]
        
        # Filtrar por tags
        if query.tags:
            items = [
                i for i in items
                if any(tag in i.tags for tag in query.tags)
            ]
        
        # Filtrar por importancia
        if query.min_importance:
            items = [
                i for i in items
                if i.importance.value <= query.min_importance.value
            ]
        
        # Filtrar por accesos
        if query.min_access_count is not None:
            items = [i for i in items if i.access_count >= query.min_access_count]
        
        # Filtrar por fecha
        if query.created_after:
            items = [i for i in items if i.created_at >= query.created_after]
        if query.created_before:
            items = [i for i in items if i.created_at <= query.created_before]
        
        # Búsqueda por texto
        if query.query:
            query_lower = query.query.lower()
            items = [
                i for i in items
                if query_lower in i.content.lower()
                or any(query_lower in tag.lower() for tag in i.tags)
            ]
        
        # Ordenar
        if query.sort_by == "created_at":
            items.sort(key=lambda i: i.created_at, reverse=True)
        elif query.sort_by == "access_count":
            items.sort(key=lambda i: i.access_count, reverse=True)
        elif query.sort_by == "importance":
            items.sort(key=lambda i: i.importance.value)
        else:  # relevance (combina factores)
            items.sort(
                key=lambda i: (
                    i.importance.value * 0.3 +
                    i.access_count * 0.2 +
                    (1.0 - i.consolidation_level) * 0.5
                )
            )
        
        total = len(items)
        
        # Aplicar paginación
        results = items[query.offset:query.offset + query.limit]
        
        return MemoryResult(
            items=results,
            total=total,
            query=query,
            search_time_ms=(time.time() - start) * 1000,
        )

    def count(self, memory_type: MemoryType | None = None) -> int:
        """Cuenta memorias por tipo."""
        if memory_type:
            return len(self._by_type[memory_type])
        return len(self._items)

    def get_summary(self, tenant_id: str) -> MemorySummary:
        """Obtiene resumen de memorias."""
        from core.PHASE_2.ai.memory.models import MemoryImportance, MemorySummary
        
        items = [i for i in self._items.values() if i.tenant_id == tenant_id]
        
        by_type = {t: 0 for t in MemoryType}
        by_importance = {imp: 0 for imp in MemoryImportance}
        
        for item in items:
            by_type[item.memory_type] += 1
            by_importance[item.importance] += 1
        
        sorted_items = sorted(items, key=lambda i: i.created_at)
        
        return MemorySummary(
            total_items=len(items),
            by_type=by_type,
            by_importance=by_importance,
            oldest_item=sorted_items[0].created_at if sorted_items else None,
            newest_item=sorted_items[-1].created_at if sorted_items else None,
            most_accessed=max(items, key=lambda i: i.access_count) if items else None,
        )

    def get_by_type(
        self,
        memory_type: MemoryType,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[MemoryItem]:
        """Obtiene memorias por tipo."""
        ids = self._by_type[memory_type]
        items = [self._items[mid] for mid in ids if mid in self._items]
        
        if user_id:
            items = [i for i in items if i.user_id == user_id]
        
        return items[:limit]

    def get_oldest(
        self,
        memory_type: MemoryType,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """Obtiene las memorias más antiguas."""
        items = self.get_by_type(memory_type)
        items.sort(key=lambda i: i.created_at)
        return items[:limit]

    def get_least_accessed(
        self,
        memory_type: MemoryType,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """Obtiene las memorias menos accedidas."""
        items = self.get_by_type(memory_type)
        items.sort(key=lambda i: i.access_count)
        return items[:limit]

    def clear(self) -> None:
        """Limpia todas las memorias."""
        self._items.clear()
        for t in MemoryType:
            self._by_type[t].clear()
        self._by_user.clear()
