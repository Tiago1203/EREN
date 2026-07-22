"""Context Builder - Constructor de contexto."""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from core.PHASE_2.ai.context_builder.compressor import ContextCompressor, IntelligentCompressor
from core.PHASE_2.ai.context_builder.models import (
    ContextConfig,
    ContextItem,
    ContextPriority,
    ContextQuery,
    ContextResult,
    ContextSource,
    ContextSourceConfig,
    ContextWindow,
)
from core.PHASE_2.ai.context_builder.prioritizer import ContextPrioritizer, RelevanceCalculator


class ContextBuilder:
    """
    Constructor de contexto principal.
    
    Orchestrates la construcción de contexto
    desde múltiples fuentes.
    """

    def __init__(
        self,
        config: ContextConfig | None = None,
        sources: dict[ContextSource, ContextSourceGetter] | None = None,
    ) -> None:
        self.config = config or ContextConfig()
        self.sources = sources or {}
        self.prioritizer = ContextPrioritizer()
        self.compressor = IntelligentCompressor()
        self.relevance_calculator = RelevanceCalculator()

    def register_source(
        self,
        source: ContextSource,
        getter: ContextSourceGetter,
    ) -> None:
        """Registra un getter para una fuente de contexto."""
        self.sources[source] = getter

    async def build(self, query: ContextQuery) -> ContextResult:
        """
        Construye contexto para una query.
        
        Args:
            query: Consulta de contexto
            
        Returns:
            Resultado con contexto construido
        """
        start_time = time.time()
        
        # Recolectar ítems de todas las fuentes
        all_items: list[ContextItem] = []
        included_sources: list[ContextSource] = []
        excluded_sources: list[ContextSource] = []
        
        for source, getter in self.sources.items():
            # Verificar si la fuente está habilitada
            if not self.config.is_source_enabled(source):
                excluded_sources.append(source)
                continue
            
            # Verificar filtros de inclusión/exclusión
            if query.include_sources and source not in query.include_sources:
                excluded_sources.append(source)
                continue
            if query.exclude_sources and source in query.exclude_sources:
                excluded_sources.append(source)
                continue
            
            try:
                # Obtener ítems de la fuente
                items = await getter(query)
                all_items.extend(items)
                included_sources.append(source)
            except Exception:
                excluded_sources.append(source)
        
        # Aplicar relevance scoring
        all_items = self._score_items(all_items, query.query)
        
        # Comprimir si es necesario
        target_tokens = query.max_tokens
        if self.config.compression_enabled:
            all_items = self.compressor.compress(
                all_items,
                target_tokens=target_tokens,
            )
        
        # Crear ventana y priorizar
        window = ContextWindow(
            max_tokens=target_tokens,
            min_critical_tokens=self.config.min_critical_tokens,
        )
        window = self.prioritizer.fill_window(all_items, window)
        
        # Construir resultado
        build_time_ms = (time.time() - start_time) * 1000
        
        return ContextResult(
            items=window.items,
            window=window,
            total_tokens=window.current_tokens,
            included_sources=included_sources,
            excluded_sources=excluded_sources,
            build_time_ms=build_time_ms,
            metadata={
                "query": {
                    "conversation_id": query.conversation_id,
                    "session_id": query.session_id,
                    "user_id": query.user_id,
                },
                "stats": {
                    "total_items": len(all_items),
                    "included_items": len(window.items),
                },
            },
        )

    def _score_items(
        self,
        items: list[ContextItem],
        query: str | None,
    ) -> list[ContextItem]:
        """Calcula scores de relevancia para ítems."""
        for item in items:
            score = self.relevance_calculator.calculate(item, query)
            # Combinar con score existente
            item.relevance_score = (item.relevance_score + score) / 2
        
        return items

    def build_sync(self, query: ContextQuery) -> ContextResult:
        """Versión síncrona de build."""
        start_time = time.time()
        
        all_items: list[ContextItem] = []
        included_sources: list[ContextSource] = []
        excluded_sources: list[ContextSource] = []
        
        for source, getter in self.sources.items():
            if not self.config.is_source_enabled(source):
                excluded_sources.append(source)
                continue
            
            if query.include_sources and source not in query.include_sources:
                excluded_sources.append(source)
                continue
            if query.exclude_sources and source in query.exclude_sources:
                excluded_sources.append(source)
                continue
            
            try:
                # Llamada síncrona
                items = getter(query)
                if hasattr(items, '__await__'):
                    # Es un coroutine, no podemos esperar
                    continue
                all_items.extend(items)
                included_sources.append(source)
            except Exception:
                excluded_sources.append(source)
        
        all_items = self._score_items(all_items, query.query)
        
        target_tokens = query.max_tokens
        if self.config.compression_enabled:
            all_items = self.compressor.compress(all_items, target_tokens=target_tokens)
        
        window = ContextWindow(
            max_tokens=target_tokens,
            min_critical_tokens=self.config.min_critical_tokens,
        )
        window = self.prioritizer.fill_window(all_items, window)
        
        build_time_ms = (time.time() - start_time) * 1000
        
        return ContextResult(
            items=window.items,
            window=window,
            total_tokens=window.current_tokens,
            included_sources=included_sources,
            excluded_sources=excluded_sources,
            build_time_ms=build_time_ms,
        )


# Type alias para getters de fuente
ContextSourceGetter = Callable[[ContextQuery], list[ContextItem] | Any]


class ContextAssembler:
    """
    Ensamblador de contexto.
    
    Combina ítems de contexto en un
    formato listo para el LLM.
    """

    def __init__(
        self,
        config: ContextConfig | None = None,
    ) -> None:
        self.config = config or ContextConfig()

    def assemble(
        self,
        result: ContextResult,
        format_type: str = "default",
    ) -> str:
        """
        Ensambla contexto en formato de texto.
        
        Args:
            result: Resultado del ContextBuilder
            format_type: Tipo de formato (default, minimal, detailed)
            
        Returns:
            Contexto formateado como string
        """
        if format_type == "minimal":
            return self._assemble_minimal(result)
        elif format_type == "detailed":
            return self._assemble_detailed(result)
        else:
            return self._assemble_default(result)

    def _assemble_default(self, result: ContextResult) -> str:
        """Ensamblaje estándar."""
        parts = []
        
        # Agregar system prompt si existe
        if self.config.system_prompt:
            parts.append(f"[SYSTEM]\n{self.config.system_prompt}")
        
        # Agregar ítems por fuente
        by_source = result.window.get_items_by_source()
        
        for source in ContextSource:
            if source in by_source and by_source[source]:
                items = by_source[source]
                source_name = source.value.upper()
                parts.append(f"\n[{source_name}]\n")
                
                for item in items:
                    parts.append(item.content)
        
        return "\n".join(parts)

    def _assemble_minimal(self, result: ContextResult) -> str:
        """Ensamblaje minimalista."""
        parts = []
        
        for item in result.items:
            if item.priority in (ContextPriority.CRITICAL, ContextPriority.HIGH):
                parts.append(f"[{item.source.value}] {item.content}")
        
        return "\n".join(parts) if parts else ""

    def _assemble_detailed(self, result: ContextResult) -> str:
        """Ensamblaje detallado con metadatos."""
        parts = []
        
        # Header
        parts.append("=" * 50)
        parts.append("CONTEXT BUILD")
        parts.append("=" * 50)
        parts.append(f"Total tokens: {result.total_tokens}")
        parts.append(f"Included sources: {[s.value for s in result.included_sources]}")
        parts.append(f"Build time: {result.build_time_ms:.2f}ms")
        parts.append("=" * 50)
        parts.append("")
        
        # Contenido por fuente
        by_source = result.window.get_items_by_source()
        
        for source in ContextSource:
            if source in by_source and by_source[source]:
                parts.append(f"\n## {source.value.upper()}")
                parts.append("-" * 40)
                
                for item in by_source[source]:
                    parts.append(f"\n[{item.priority.name}] (tokens: {item.token_count})")
                    parts.append(item.content)
                    if item.metadata:
                        parts.append(f"  metadata: {item.metadata}")
        
        return "\n".join(parts)

    def assemble_messages(
        self,
        result: ContextResult,
    ) -> list[dict[str, str]]:
        """
        Ensambla contexto como mensajes para API.
        
        Returns:
            Lista de mensajes en formato API
        """
        messages = []
        
        # System message
        if self.config.system_prompt:
            messages.append({
                "role": "system",
                "content": self.config.system_prompt,
            })
        
        # User context
        user_context = self._get_user_context(result)
        if user_context:
            messages.append({
                "role": "user",
                "content": user_context,
            })
        
        return messages

    def _get_user_context(self, result: ContextResult) -> str:
        """Obtiene contexto formateado para usuario."""
        parts = ["[CONTEXT]\n"]
        
        by_source = result.window.get_items_by_source()
        
        for source in by_source:
            if by_source[source]:
                items_content = "\n".join(item.content for item in by_source[source])
                parts.append(f"[{source.value}]\n{items_content}\n")
        
        return "\n".join(parts)


def create_context_item(
    source: ContextSource,
    content: str,
    priority: ContextPriority = ContextPriority.MEDIUM,
    metadata: dict[str, Any] | None = None,
) -> ContextItem:
    """Factory para crear ContextItems."""
    return ContextItem(
        id=str(uuid.uuid4()),
        source=source,
        content=content,
        priority=priority,
        metadata=metadata or {},
    )
