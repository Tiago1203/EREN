"""
PHASE 4 - EPIC 0: Events Module

Eventos de dominio para la plataforma de conocimiento.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
import uuid


class EventType(str, Enum):
    """Tipos de eventos de dominio."""
    # Document events
    DOCUMENT_RECEIVED = "knowledge.document.received"
    DOCUMENT_PROCESSED = "knowledge.document.processed"
    DOCUMENT_FAILED = "knowledge.document.failed"
    
    # Extraction events
    EXTRACTION_STARTED = "knowledge.extraction.started"
    EXTRACTION_COMPLETED = "knowledge.extraction.completed"
    EXTRACTION_FAILED = "knowledge.extraction.failed"
    
    # Embedding events
    EMBEDDING_GENERATED = "knowledge.embedding.generated"
    EMBEDDING_FAILED = "knowledge.embedding.failed"
    EMBEDDING_CACHED = "knowledge.embedding.cached"
    
    # Index events
    INDEXING_STARTED = "knowledge.indexing.started"
    INDEXING_COMPLETED = "knowledge.indexing.completed"
    INDEXING_FAILED = "knowledge.indexing.failed"
    
    # Retrieval events
    RETRIEVAL_STARTED = "knowledge.retrieval.started"
    RETRIEVAL_COMPLETED = "knowledge.retrieval.completed"
    RETRIEVAL_FAILED = "knowledge.retrieval.failed"
    
    # Citation events
    CITATION_CREATED = "knowledge.citation.created"
    CITATION_FAILED = "knowledge.citation.failed"
    CITATION_ACCESSED = "knowledge.citation.accessed"
    
    # Quality events
    QUALITY_ASSESSED = "knowledge.quality.assessed"
    BIAS_DETECTED = "knowledge.bias.detected"
    DUPLICATE_DETECTED = "knowledge.duplicate.detected"
    
    # Governance events
    ASSET_CREATED = "knowledge.asset.created"
    ASSET_UPDATED = "knowledge.asset.updated"
    ASSET_PUBLISHED = "knowledge.asset.published"
    ASSET_ARCHIVED = "knowledge.asset.archived"
    ASSET_SUPERSEDED = "knowledge.asset.superseded"
    AUDIT_LOGGED = "knowledge.audit.logged"
    
    # Sync events
    SYNC_STARTED = "knowledge.sync.started"
    SYNC_COMPLETED = "knowledge.sync.completed"
    SYNC_FAILED = "knowledge.sync.failed"
    NEW_PUBLICATION_DETECTED = "knowledge.sync.new_publication"
    RECORD_UPDATED = "knowledge.sync.record_updated"


@dataclass
class DomainEvent:
    """Evento de dominio base."""
    event_id: str
    event_type: EventType
    timestamp: datetime
    
    # Context
    correlation_id: str = ""
    causation_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    
    # Metadata
    source: str = "PHASE_4"
    version: str = "1.0"
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        event_type: EventType,
        correlation_id: str = "",
        tenant_id: str = "",
        user_id: str = "",
        **kwargs,
    ) -> "DomainEvent":
        """Factory method to create domain event."""
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(UTC),
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            metadata=kwargs,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "source": self.source,
            "version": self.version,
            "metadata": self.metadata,
        }


# =============================================================================
# DOCUMENT EVENTS
# =============================================================================

@dataclass
class DocumentReceivedEvent(DomainEvent):
    """Evento cuando se recibe un documento."""
    document_id: str = ""
    format: str = ""
    source_uri: str = ""
    size_bytes: int = 0


@dataclass
class DocumentProcessedEvent(DomainEvent):
    """Evento cuando se procesa un documento."""
    document_id: str = ""
    pages: int = 0
    word_count: int = 0
    processing_time_ms: int = 0


@dataclass
class DocumentFailedEvent(DomainEvent):
    """Evento cuando falla el procesamiento."""
    document_id: str = ""
    error: str = ""
    error_code: str = ""


# =============================================================================
# EXTRACTION EVENTS
# =============================================================================

@dataclass
class ExtractionCompletedEvent(DomainEvent):
    """Evento cuando se completa la extracción."""
    document_id: str = ""
    extraction_id: str = ""
    entities_count: int = 0
    concepts_count: int = 0
    relations_count: int = 0
    quality_score: float = 0.0


@dataclass
class ExtractionFailedEvent(DomainEvent):
    """Evento cuando falla la extracción."""
    document_id: str = ""
    error: str = ""


# =============================================================================
# EMBEDDING EVENTS
# =============================================================================

@dataclass
class EmbeddingGeneratedEvent(DomainEvent):
    """Evento cuando se genera embedding."""
    embedding_id: str = ""
    model: str = ""
    dimension: int = 0
    cached: bool = False


@dataclass
class EmbeddingFailedEvent(DomainEvent):
    """Evento cuando falla generación de embedding."""
    text_hash: str = ""
    model: str = ""
    error: str = ""


# =============================================================================
# INDEX EVENTS
# =============================================================================

@dataclass
class IndexingCompletedEvent(DomainEvent):
    """Evento cuando se completa indexación."""
    collection: str = ""
    vectors_indexed: int = 0
    indexing_time_ms: int = 0


@dataclass
class IndexingFailedEvent(DomainEvent):
    """Evento cuando falla indexación."""
    collection: str = ""
    error: str = ""


# =============================================================================
# RETRIEVAL EVENTS
# =============================================================================

@dataclass
class RetrievalCompletedEvent(DomainEvent):
    """Evento cuando se completa retrieval."""
    query_id: str = ""
    query_preview: str = ""
    results_count: int = 0
    retrieval_time_ms: int = 0


@dataclass
class RetrievalFailedEvent(DomainEvent):
    """Evento cuando falla retrieval."""
    query_id: str = ""
    error: str = ""


# =============================================================================
# CITATION EVENTS
# =============================================================================

@dataclass
class CitationCreatedEvent(DomainEvent):
    """Evento cuando se crea citación."""
    citation_id: str = ""
    source_id: str = ""
    source_type: str = ""


@dataclass
class CitationAccessedEvent(DomainEvent):
    """Evento cuando se accede a citación."""
    citation_id: str = ""
    user_id: str = ""


# =============================================================================
# QUALITY EVENTS
# =============================================================================

@dataclass
class QualityAssessedEvent(DomainEvent):
    """Evento cuando se evalúa calidad."""
    asset_id: str = ""
    quality_score: float = 0.0
    quality_level: str = ""


@dataclass
class BiasDetectedEvent(DomainEvent):
    """Evento cuando se detecta sesgo."""
    asset_id: str = ""
    bias_type: str = ""
    severity: float = 0.0


@dataclass
class DuplicateDetectedEvent(DomainEvent):
    """Evento cuando se detecta duplicado."""
    original_id: str = ""
    duplicate_ids: list[str] = field(default_factory=list)


# =============================================================================
# GOVERNANCE EVENTS
# =============================================================================

@dataclass
class AssetCreatedEvent(DomainEvent):
    """Evento cuando se crea asset."""
    asset_id: str = ""
    title: str = ""
    domain: str = ""


@dataclass
class AssetUpdatedEvent(DomainEvent):
    """Evento cuando se actualiza asset."""
    asset_id: str = ""
    previous_version: str = ""
    new_version: str = ""


@dataclass
class AssetPublishedEvent(DomainEvent):
    """Evento cuando se publica asset."""
    asset_id: str = ""
    approved_by: str = ""


@dataclass
class AssetArchivedEvent(DomainEvent):
    """Evento cuando se archiva asset."""
    asset_id: str = ""
    reason: str = ""


@dataclass
class AuditLoggedEvent(DomainEvent):
    """Evento cuando se registra auditoría."""
    audit_id: str = ""
    action: str = ""
    asset_id: str = ""


# =============================================================================
# SYNC EVENTS
# =============================================================================

@dataclass
class SyncCompletedEvent(DomainEvent):
    """Evento cuando se completa sincronización."""
    source: str = ""
    records_processed: int = 0
    records_added: int = 0
    records_updated: int = 0
    sync_time_ms: int = 0


@dataclass
class NewPublicationDetectedEvent(DomainEvent):
    """Evento cuando se detecta nueva publicación."""
    source: str = ""
    publication_id: str = ""
    title: str = ""


# =============================================================================
# EVENT PUBLISHER
# =============================================================================

class IEventPublisher:
    """Protocolo para publicador de eventos."""
    
    async def publish(self, event: DomainEvent) -> bool:
        """Publica un evento."""
        ...
    
    async def subscribe(
        self,
        event_type: EventType,
        handler: callable,
    ) -> None:
        """Suscribe handler a tipo de evento."""
        ...


class InMemoryEventPublisher(IEventPublisher):
    """Publicador de eventos en memoria."""
    
    def __init__(self):
        self._subscribers: dict[EventType, list[callable]] = {}
        self._published_events: list[DomainEvent] = []
    
    async def publish(self, event: DomainEvent) -> bool:
        """Publica un evento."""
        self._published_events.append(event)
        
        # Notify subscribers
        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                pass  # Log error but don't fail
        
        return True
    
    async def subscribe(
        self,
        event_type: EventType,
        handler: callable,
    ) -> None:
        """Suscribe handler a tipo de evento."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def get_published_events(self) -> list[DomainEvent]:
        """Obtiene eventos publicados (para testing)."""
        return self._published_events.copy()
    
    def clear(self) -> None:
        """Limpia eventos publicados."""
        self._published_events.clear()


__all__ = [
    "EventType",
    "DomainEvent",
    # Document events
    "DocumentReceivedEvent",
    "DocumentProcessedEvent",
    "DocumentFailedEvent",
    # Extraction events
    "ExtractionCompletedEvent",
    "ExtractionFailedEvent",
    # Embedding events
    "EmbeddingGeneratedEvent",
    "EmbeddingFailedEvent",
    # Index events
    "IndexingCompletedEvent",
    "IndexingFailedEvent",
    # Retrieval events
    "RetrievalCompletedEvent",
    "RetrievalFailedEvent",
    # Citation events
    "CitationCreatedEvent",
    "CitationAccessedEvent",
    # Quality events
    "QualityAssessedEvent",
    "BiasDetectedEvent",
    "DuplicateDetectedEvent",
    # Governance events
    "AssetCreatedEvent",
    "AssetUpdatedEvent",
    "AssetPublishedEvent",
    "AssetArchivedEvent",
    "AuditLoggedEvent",
    # Sync events
    "SyncCompletedEvent",
    "NewPublicationDetectedEvent",
    # Publisher
    "IEventPublisher",
    "InMemoryEventPublisher",
]
