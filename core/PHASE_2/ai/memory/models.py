"""Memory Models - Modelos de memoria."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    """Tipos de memoria."""
    WORKING = "working"       # Memoria de trabajo activa
    SHORT = "short"           # Memoria a corto plazo
    LONG = "long"             # Memoria a largo plazo
    EPISODIC = "episodic"    # Memoria de experiencias
    SEMANTIC = "semantic"     # Memoria de conocimiento


class MemoryImportance(int, Enum):
    """Importancia de un recuerdo."""
    CRITICAL = 1  # Nunca olvidar
    HIGH = 2      # Difícil de olvidar
    MEDIUM = 3    # Importancia normal
    LOW = 4       # Fácil de olvidar
    DISCARDABLE = 5  # Puede eliminarse


@dataclass
class MemoryItem:
    """Un ítem de memoria."""
    id: str
    memory_type: MemoryType
    content: str
    
    # Identificadores
    conversation_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None
    
    # Metadatos
    importance: MemoryImportance = MemoryImportance.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    # Consistencia
    consolidation_level: float = 0.0  # 0.0 = nuevo, 1.0 = completamente consolidado
    version: int = 1
    
    # Etiquetas y relaciones
    tags: list[str] = field(default_factory=list)
    related_ids: list[str] = field(default_factory=list)
    embeddings: list[float] | None = None
    
    # Contenido estructurado
    structured_data: dict[str, Any] | None = None
    
    # Metadatos adicionales
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def access(self) -> None:
        """Registra un acceso a la memoria."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def consolidate(self, level: float = 1.0) -> None:
        """Consolida la memoria."""
        self.consolidation_level = min(1.0, level)
    
    def update_content(self, new_content: str) -> None:
        """Actualiza el contenido de la memoria."""
        self.content = new_content
        self.version += 1


@dataclass
class MemoryQuery:
    """Consulta para recuperación de memoria."""
    memory_type: MemoryType | None = None
    user_id: str | None = None
    conversation_id: str | None = None
    session_id: str | None = None
    tenant_id: str | None = None
    
    # Búsqueda
    query: str | None = None
    tags: list[str] | None = None
    
    # Filtros
    min_importance: MemoryImportance | None = None
    min_access_count: int | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    
    # Límites
    limit: int = 100
    offset: int = 0
    
    # Ordenamiento
    sort_by: str = "relevance"  # relevance, created_at, access_count, importance


@dataclass
class MemoryResult:
    """Resultado de una consulta de memoria."""
    items: list[MemoryItem]
    total: int
    query: MemoryQuery
    search_time_ms: float = 0.0
    
    @property
    def content_summary(self) -> str:
        """Resumen del contenido de los ítems."""
        return "\n".join(f"- {item.content[:100]}..." for item in self.items[:5])


@dataclass
class MemorySummary:
    """Resumen de un grupo de memorias."""
    total_items: int
    by_type: dict[MemoryType, int]
    by_importance: dict[MemoryImportance, int]
    oldest_item: datetime | None = None
    newest_item: datetime | None = None
    most_accessed: MemoryItem | None = None


@dataclass
class MemoryConfig:
    """Configuración del sistema de memoria."""
    # Límites por tipo
    working_memory_limit: int = 50
    short_memory_limit: int = 500
    long_memory_limit: int = 10000
    episodic_memory_limit: int = 5000
    semantic_memory_limit: int = 20000
    
    # TTL en segundos (None = no expira)
    working_memory_ttl: int | None = 3600  # 1 hora
    short_memory_ttl: int | None = 86400 * 7  # 7 días
    long_memory_ttl: int | None = None  # No expira
    episodic_memory_ttl: int | None = None  # No expira
    semantic_memory_ttl: int | None = None  # No expira
    
    # Consolidación
    consolidation_threshold: float = 0.8  # Consolidar después de 80% de TTL
    auto_consolidate: bool = True
    
    # Olvido
    forget_threshold: float = 0.1  # Olvidar después de 10% de relevancia
    auto_forget: bool = True
    
    # Resumen
    auto_summarize: bool = True
    summarize_threshold: int = 10  # Resumir después de 10 ítems similares


class MemoryEventType(str, Enum):
    """Tipos de eventos de memoria."""
    STORED = "memory.stored"
    RETRIEVED = "memory.retrieved"
    FORGOTTEN = "memory.forgotten"
    CONSOLIDATED = "memory.consolidated"
    SUMMARIZED = "memory.summarized"
    UPDATED = "memory.updated"
    DELETED = "memory.deleted"


@dataclass
class MemoryEvent:
    """Evento de memoria."""
    type: MemoryEventType
    memory_id: str
    memory_type: MemoryType
    user_id: str | None = None
    tenant_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
