"""Context Models - Modelos de contexto."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContextSource(str, Enum):
    """Fuentes de contexto."""
    CONVERSATION = "conversation"
    MEMORY = "memory"
    INCIDENT = "incident"
    DEVICE = "device"
    KNOWLEDGE = "knowledge"
    USER = "user"
    HOSPITAL = "hospital"
    SESSION = "session"
    SYSTEM = "system"


class ContextPriority(int, Enum):
    """Prioridades de contexto."""
    CRITICAL = 1  # Información crítica que siempre debe incluirse
    HIGH = 2      # Información importante
    MEDIUM = 3    # Información estándar
    LOW = 4       # Información que puede omitirse si hay límite
    DISCARDABLE = 5  # Información que puede descartarse


@dataclass
class ContextItem:
    """
    Un ítem individual de contexto.
    
    Representa una pieza de información que será
    incluida en el contexto del LLM.
    """
    id: str
    source: ContextSource
    content: str
    priority: ContextPriority = ContextPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 0.0  # 0.0 a 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    
    def __post_init__(self) -> None:
        """Calcula el conteo de tokens aproximado."""
        if self.token_count == 0:
            # Estimación: ~4 caracteres por token en promedio
            self.token_count = len(self.content) // 4
    
    def should_include(self, min_priority: ContextPriority = ContextPriority.LOW) -> bool:
        """Determina si el ítem debe incluirse basándose en prioridad."""
        return self.priority.value <= min_priority.value


@dataclass
class ContextWindow:
    """
    Ventana de contexto con limitación de tokens.
    
    Define el espacio disponible para contexto y
    gestiona qué ítems caben dentro.
    """
    max_tokens: int = 8192
    min_critical_tokens: int = 1024  # Mínimo para información crítica
    current_tokens: int = 0
    items: list[ContextItem] = field(default_factory=list)
    
    @property
    def available_tokens(self) -> int:
        """Tokens disponibles restantes."""
        return self.max_tokens - self.current_tokens
    
    @property
    def is_full(self) -> bool:
        """Verifica si la ventana está llena."""
        return self.current_tokens >= self.max_tokens
    
    @property
    def has_minimum(self) -> bool:
        """Verifica si se alcanzó el mínimo de tokens críticos."""
        critical_tokens = sum(
            item.token_count for item in self.items
            if item.priority == ContextPriority.CRITICAL
        )
        return critical_tokens >= self.min_critical_tokens
    
    def add_item(self, item: ContextItem) -> bool:
        """
        Agrega un ítem a la ventana.
        
        Returns:
            True si se agregó, False si no hay espacio
        """
        if self.current_tokens + item.token_count <= self.max_tokens:
            self.items.append(item)
            self.current_tokens += item.token_count
            return True
        return False
    
    def remove_item(self, item_id: str) -> bool:
        """Remueve un ítem de la ventana."""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.current_tokens -= item.token_count
                self.items.pop(i)
                return True
        return False
    
    def get_items_by_priority(self) -> dict[ContextPriority, list[ContextItem]]:
        """Agrupa ítems por prioridad."""
        result: dict[ContextPriority, list[ContextItem]] = {p: [] for p in ContextPriority}
        for item in self.items:
            result[item.priority].append(item)
        return result
    
    def get_items_by_source(self) -> dict[ContextSource, list[ContextItem]]:
        """Agrupa ítems por fuente."""
        result: dict[ContextSource, list[ContextItem]] = {s: [] for s in ContextSource}
        for item in self.items:
            result[item.source].append(item)
        return result
    
    def clear(self) -> None:
        """Limpia la ventana."""
        self.items.clear()
        self.current_tokens = 0


@dataclass
class ContextQuery:
    """Consulta para construir contexto."""
    conversation_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    hospital_id: str | None = None
    query: str | None = None  # Query para búsqueda semántica
    filters: dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 8192
    include_sources: list[ContextSource] | None = None
    exclude_sources: list[ContextSource] | None = None


@dataclass
class ContextResult:
    """Resultado de la construcción de contexto."""
    items: list[ContextItem]
    window: ContextWindow
    total_tokens: int
    included_sources: list[ContextSource]
    excluded_sources: list[ContextSource]
    build_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @property
    def content(self) -> str:
        """Obtiene el contenido formateado del contexto."""
        return "\n\n".join(
            f"[{item.source.value}] {item.content}"
            for item in self.items
        )
    
    @property
    def sources_summary(self) -> dict[str, int]:
        """Resumen de fuentes incluidas."""
        summary: dict[str, int] = {}
        for item in self.items:
            source = item.source.value
            summary[source] = summary.get(source, 0) + 1
        return summary


@dataclass
class ContextSourceConfig:
    """Configuración para una fuente de contexto."""
    source: ContextSource
    enabled: bool = True
    max_items: int = 50
    max_tokens: int = 2048
    priority: ContextPriority = ContextPriority.MEDIUM
    relevance_threshold: float = 0.0
    ttl_seconds: int | None = None  # None = no expiration


@dataclass
class ContextConfig:
    """Configuración global del constructor de contexto."""
    default_max_tokens: int = 8192
    min_critical_tokens: int = 1024
    compression_enabled: bool = True
    compression_threshold: float = 0.8  # Comprimir cuando 80% lleno
    prioritization_enabled: bool = True
    sources: dict[ContextSource, ContextSourceConfig] = field(default_factory=dict)
    system_prompt: str | None = None
    user_context_template: str | None = None
    
    def get_source_config(self, source: ContextSource) -> ContextSourceConfig:
        """Obtiene configuración de fuente."""
        if source not in self.sources:
            return ContextSourceConfig(source=source)
        return self.sources[source]
    
    def is_source_enabled(self, source: ContextSource) -> bool:
        """Verifica si una fuente está habilitada."""
        config = self.get_source_config(source)
        return config.enabled
