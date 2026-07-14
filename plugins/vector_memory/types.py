"""Vector memory types for EREN Vector Memory Plugin."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Vector Metadata (defined first to avoid circular reference)
# =============================================================================


@dataclass
class VectorMetadata:
    """Metadata for vector documents."""

    document_id: str = ""
    chunk_id: str = ""
    source: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    medical_specialty: str = ""
    device: str = ""
    patient: str = ""
    tags: list[str] = field(default_factory=list)
    language: str = "en"
    embedding_model: str = ""
    chunk_index: int = 0
    total_chunks: int = 1
    custom: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "source": self.source,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "medical_specialty": self.medical_specialty,
            "device": self.device,
            "patient": self.patient,
            "tags": self.tags,
            "language": self.language,
            "embedding_model": self.embedding_model,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            **{k: v for k, v in self.custom.items()},
        }


# =============================================================================
# Vector Document
# =============================================================================


@dataclass
class VectorDocument:
    """A document to be stored in vector memory."""

    id: str
    content: str
    metadata: VectorMetadata = field(default_factory=VectorMetadata)
    embeddings: list[float] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "embeddings": self.embeddings,
        }


# =============================================================================
# Vector Chunk
# =============================================================================


@dataclass
class VectorChunk:
    """A chunk of a document."""

    chunk_id: str
    document_id: str
    content: str
    metadata: VectorMetadata
    embedding: list[float] | None = None
    index: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "embedding": self.embedding,
            "index": self.index,
        }


# =============================================================================
# Vector Search Result
# =============================================================================


@dataclass
class VectorSearchResult:
    """Result from vector search."""

    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: VectorMetadata
    distance: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata.to_dict(),
            "distance": self.distance,
        }


# =============================================================================
# Vector Search Query
# =============================================================================


@dataclass
class VectorSearchQuery:
    """Query for vector search."""

    query: str
    embeddings: list[float] | None = None
    filters: dict | None = None
    top_k: int = 10
    min_score: float = 0.0
    include_embeddings: bool = False


# =============================================================================
# Vector Statistics
# =============================================================================


@dataclass
class VectorStatistics:
    """Statistics for vector memory."""

    total_documents: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    average_chunks_per_document: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "total_chunks": self.total_chunks,
            "total_embeddings": self.total_embeddings,
            "average_chunks_per_document": self.average_chunks_per_document,
            "last_updated": self.last_updated.isoformat(),
        }
