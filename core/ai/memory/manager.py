"""Memory Manager - Gestor de memoria."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from core.ai.memory.models import (
    MemoryConfig,
    MemoryEvent,
    MemoryEventType,
    MemoryImportance,
    MemoryItem,
    MemoryQuery,
    MemoryResult,
    MemoryType,
)
from core.ai.memory.repository import InMemoryMemoryRepository, MemoryRepository


class MemoryManager:
    """
    Gestor de memoria del sistema cognitivo.
    
    Administra los diferentes tipos de memoria:
    - Working: Memoria de trabajo activa
    - Short: Memoria a corto plazo
    - Long: Memoria a largo plazo
    - Episodic: Memoria de experiencias
    - Semantic: Memoria de conocimiento
    """

    def __init__(
        self,
        repository: MemoryRepository | None = None,
        config: MemoryConfig | None = None,
    ) -> None:
        self._repository = repository or InMemoryMemoryRepository()
        self._config = config or MemoryConfig()
        self._events: list[MemoryEvent] = []

    @property
    def config(self) -> MemoryConfig:
        """Obtiene la configuración."""
        return self._config

    @property
    def repository(self) -> MemoryRepository:
        """Obtiene el repositorio."""
        return self._repository

    # ========== Operaciones Básicas ==========

    def store(
        self,
        content: str,
        memory_type: MemoryType,
        user_id: str | None = None,
        tenant_id: str | None = None,
        conversation_id: str | None = None,
        session_id: str | None = None,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        """
        Guarda un ítem en memoria.
        
        Args:
            content: Contenido a guardar
            memory_type: Tipo de memoria
            user_id: ID del usuario
            tenant_id: ID del tenant
            conversation_id: ID de conversación
            session_id: ID de sesión
            importance: Importancia del ítem
            tags: Etiquetas
            metadata: Metadatos adicionales
            
        Returns:
            Ítem de memoria creado
        """
        item = MemoryItem(
            id=str(uuid.uuid4()),
            memory_type=memory_type,
            content=content,
            user_id=user_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            session_id=session_id,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )

        self._repository.save(item)
        
        # Verificar límites
        self._enforce_limits(memory_type, tenant_id)
        
        # Emitir evento
        self._emit_event(MemoryEventType.STORED, item)
        
        return item

    def retrieve(
        self,
        memory_id: str,
    ) -> MemoryItem | None:
        """Recupera un ítem de memoria por ID."""
        item = self._repository.get(memory_id)
        if item:
            self._emit_event(MemoryEventType.RETRIEVED, item)
        return item

    def search(
        self,
        query: str | None = None,
        memory_type: MemoryType | None = None,
        user_id: str | None = None,
        tenant_id: str | None = None,
        conversation_id: str | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> MemoryResult:
        """
        Busca memorias.
        
        Args:
            query: Texto a buscar
            memory_type: Filtrar por tipo
            user_id: Filtrar por usuario
            tenant_id: Filtrar por tenant
            conversation_id: Filtrar por conversación
            tags: Filtrar por etiquetas
            limit: Límite de resultados
            
        Returns:
            Resultados de la búsqueda
        """
        memory_query = MemoryQuery(
            query=query,
            memory_type=memory_type,
            user_id=user_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            tags=tags,
            limit=limit,
        )
        
        result = self._repository.query(memory_query)
        
        # Emitir eventos
        for item in result.items:
            self._emit_event(MemoryEventType.RETRIEVED, item)
        
        return result

    def delete(self, memory_id: str) -> bool:
        """Elimina un ítem de memoria."""
        item = self._repository.get(memory_id)
        if item:
            result = self._repository.delete(memory_id)
            if result:
                self._emit_event(MemoryEventType.DELETED, item)
            return result
        return False

    # ========== Funciones de Memoria ==========

    def update_content(
        self,
        memory_id: str,
        new_content: str,
    ) -> MemoryItem | None:
        """Actualiza el contenido de una memoria."""
        item = self._repository.get(memory_id)
        if not item:
            return None
        
        old_content = item.content
        item.update_content(new_content)
        self._repository.save(item)
        
        self._emit_event(MemoryEventType.UPDATED, item, {
            "old_content": old_content,
            "new_content": new_content,
        })
        
        return item

    def summarize(
        self,
        memory_type: MemoryType,
        user_id: str | None = None,
        tenant_id: str | None = None,
    ) -> str:
        """
        Resume memorias de un tipo.
        
        Args:
            memory_type: Tipo de memoria
            user_id: Filtrar por usuario
            tenant_id: Filtrar por tenant
            
        Returns:
            Resumen de las memorias
        """
        query = MemoryQuery(
            memory_type=memory_type,
            user_id=user_id,
            tenant_id=tenant_id,
            limit=50,
        )
        
        result = self._repository.query(query)
        
        if not result.items:
            return "No hay memorias para resumir."
        
        # Emitir evento
        for item in result.items:
            self._emit_event(MemoryEventType.SUMMARIZED, item)
        
        # Generar resumen simple
        summary_parts = [
            f"Resumen de {memory_type.value} ({len(result.items)} ítems):",
        ]
        
        # Agrupar por tags
        by_tag: dict[str, list[MemoryItem]] = {}
        for item in result.items:
            for tag in item.tags:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(item)
        
        for tag, items in by_tag.items():
            summary_parts.append(f"\n[{tag}] ({len(items)} ítems)")
            for item in items[:3]:
                summary_parts.append(f"  - {item.content[:100]}...")
        
        return "\n".join(summary_parts)

    def consolidate(
        self,
        memory_id: str,
        level: float = 1.0,
    ) -> MemoryItem | None:
        """
        Consolida una memoria (fortalece su recuerdo).
        
        Args:
            memory_id: ID de la memoria
            level: Nivel de consolidación (0.0 - 1.0)
            
        Returns:
            Memoria consolidada o None
        """
        item = self._repository.get(memory_id)
        if not item:
            return None
        
        item.consolidate(level)
        self._repository.save(item)
        
        self._emit_event(MemoryEventType.CONSOLIDATED, item, {"level": level})
        
        return item

    def forget(
        self,
        memory_id: str,
        permanent: bool = False,
    ) -> bool:
        """
        Olvida una memoria (marca para eliminación o elimina).
        
        Args:
            memory_id: ID de la memoria
            permanent: Si es True, elimina inmediatamente
            
        Returns:
            True si se olvidó correctamente
        """
        item = self._repository.get(memory_id)
        if not item:
            return False
        
        if permanent:
            result = self._repository.delete(memory_id)
            if result:
                self._emit_event(MemoryEventType.FORGOTTEN, item, {"permanent": True})
            return result
        else:
            # Reducir consolidación (marcar para olvido)
            item.consolidation_level = max(0.0, item.consolidation_level - 0.3)
            self._repository.save(item)
            self._emit_event(MemoryEventType.FORGOTTEN, item, {"permanent": False})
            return True

    def consolidate_batch(
        self,
        memory_ids: list[str],
    ) -> list[MemoryItem]:
        """Consolida múltiples memorias."""
        results = []
        for memory_id in memory_ids:
            item = self.consolidate(memory_id)
            if item:
                results.append(item)
        return results

    def forget_by_criteria(
        self,
        memory_type: MemoryType | None = None,
        older_than_days: int | None = None,
        access_count_below: int | None = None,
        importance_below: MemoryImportance | None = None,
        dry_run: bool = True,
    ) -> list[MemoryItem]:
        """
        Olvida memorias según criterios.
        
        Args:
            memory_type: Tipo de memoria
            older_than_days: Olvidar las más antiguas que N días
            access_count_below: Olvidar las con menos de N accesos
            importance_below: Olvidar las de menor importancia que N
            dry_run: Si True, no elimina realmente
            
        Returns:
            Lista de memorias olvidadas
        """
        query = MemoryQuery(
            memory_type=memory_type,
            limit=1000,
        )
        
        if older_than_days:
            query.created_before = datetime.now() - timedelta(days=older_than_days)
        
        if access_count_below is not None:
            query.min_access_count = 0  # Permitir cualquier acceso bajo
        
        result = self._repository.query(query)
        
        forgotten = []
        for item in result.items:
            should_forget = True
            
            # Verificar criterios específicos
            if access_count_below is not None and item.access_count >= access_count_below:
                should_forget = False
            
            if importance_below and item.importance.value <= importance_below.value:
                should_forget = False
            
            # No olvidar memorias críticas
            if item.importance == MemoryImportance.CRITICAL:
                should_forget = False
            
            if should_forget:
                if not dry_run:
                    self.forget(item.id, permanent=True)
                forgotten.append(item)
        
        return forgotten

    # ========== Transferencia entre Memorias ==========

    def transfer_to_long(
        self,
        memory_id: str,
    ) -> MemoryItem | None:
        """Transfiere una memoria a largo plazo."""
        item = self._repository.get(memory_id)
        if not item:
            return None
        
        if item.memory_type == MemoryType.WORKING:
            item.memory_type = MemoryType.LONG
            item.consolidate(0.8)  # Consolidar al transferir
            self._repository.save(item)
            self._emit_event(MemoryEventType.CONSOLIDATED, item, {
                "transfer": "working_to_long"
            })
        
        return item

    def transfer_to_short(
        self,
        memory_id: str,
    ) -> MemoryItem | None:
        """Transfiere una memoria a corto plazo."""
        item = self._repository.get(memory_id)
        if not item:
            return None
        
        if item.memory_type == MemoryType.WORKING:
            item.memory_type = MemoryType.SHORT
            self._repository.save(item)
        
        return item

    # ========== Utilidades ==========

    def get_summary(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Obtiene resumen de memorias."""
        summary = self._repository.get_summary(tenant_id)
        
        return {
            "total_items": summary.total_items,
            "by_type": {t.value: c for t, c in summary.by_type.items()},
            "by_importance": {i.name: c for i, c in summary.by_importance.items()},
            "oldest_item": summary.oldest_item.isoformat() if summary.oldest_item else None,
            "newest_item": summary.newest_item.isoformat() if summary.newest_item else None,
            "most_accessed": summary.most_accessed.content[:100] if summary.most_accessed else None,
        }

    def _enforce_limits(
        self,
        memory_type: MemoryType,
        tenant_id: str | None,
    ) -> None:
        """Aplica límites de memoria."""
        if tenant_id is None:
            return
        
        # Obtener límite según tipo
        limits = {
            MemoryType.WORKING: self._config.working_memory_limit,
            MemoryType.SHORT: self._config.short_memory_limit,
            MemoryType.LONG: self._config.long_memory_limit,
            MemoryType.EPISODIC: self._config.episodic_memory_limit,
            MemoryType.SEMANTIC: self._config.semantic_memory_limit,
        }
        
        limit = limits.get(memory_type, 1000)
        current_count = self._repository.count(memory_type)
        
        if current_count > limit:
            # Obtener las menos importantes para eliminar
            excess = current_count - limit
            oldest = self._repository.get_oldest(memory_type, limit=excess)
            
            for item in oldest:
                # No eliminar memorias críticas
                if item.importance != MemoryImportance.CRITICAL:
                    self._repository.delete(item.id)

    def _emit_event(
        self,
        event_type: MemoryEventType,
        item: MemoryItem,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emite un evento."""
        event = MemoryEvent(
            type=event_type,
            memory_id=item.id,
            memory_type=item.memory_type,
            user_id=item.user_id,
            tenant_id=item.tenant_id,
            metadata=metadata or {},
        )
        self._events.append(event)

    def get_events(
        self,
        memory_id: str | None = None,
        event_type: MemoryEventType | None = None,
        limit: int = 100,
    ) -> list[MemoryEvent]:
        """Obtiene eventos de memoria."""
        events = self._events
        
        if memory_id:
            events = [e for e in events if e.memory_id == memory_id]
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[-limit:]

    def clear_events(self) -> None:
        """Limpia los eventos."""
        self._events.clear()
