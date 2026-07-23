"""RAG domain chunk entities."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    """Evidence source type."""
    KNOWLEDGE = "knowledge"
    ENTITY = "entity"
    TOOL = "tool"
    USER = "user"
    DOCUMENT = "document"
    WEB = "web"
    CLINICAL = "clinical"


class ChunkStatus(str, Enum):
    """Status of a knowledge chunk."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"


class ChunkType(str, Enum):
    """Type of knowledge chunk."""
    TEXT = "text"
    CODE = "code"
    TABLE = "table"
    IMAGE = "image"
    STRUCTURED = "structured"
    METADATA = "metadata"


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved evidence chunk."""
    id: str
    content: str
    source_type: SourceType
    source_id: str
    relevance_score: float
    metadata: dict = field(default_factory=dict)
    
    # Additional metadata
    title: str = ""
    url: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    chunk_type: ChunkType = ChunkType.TEXT
    status: ChunkStatus = ChunkStatus.ACTIVE
    
    # Medical-specific metadata
    medical_specialty: str = ""
    device_categories: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    
    # Citation info
    citation_id: str = ""
    page_number: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "chunk_type": self.chunk_type.value,
            "status": self.status.value,
            "medical_specialty": self.medical_specialty,
            "device_categories": self.device_categories,
            "standards": self.standards,
            "citation_id": self.citation_id,
            "page_number": self.page_number,
        }


@dataclass(frozen=True)
class Citation:
    """Citation for evidence."""
    id: str
    source_type: SourceType
    source_id: str
    citation_text: str
    citation_url: Optional[str] = None
    accessible: bool = True
    
    # Extended citation metadata
    title: str = ""
    authors: list[str] = field(default_factory=list)
    publication_date: str = ""
    journal: str = ""
    doi: str = ""
    
    # For clinical citations
    evidence_level: str = ""
    clinical_context: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "citation_text": self.citation_text,
            "citation_url": self.citation_url,
            "accessible": self.accessible,
            "title": self.title,
            "authors": self.authors,
            "publication_date": self.publication_date,
            "journal": self.journal,
            "doi": self.doi,
            "evidence_level": self.evidence_level,
            "clinical_context": self.clinical_context,
        }


@dataclass(frozen=True)
class Evidence:
    """Evidence used in reasoning."""
    chunks: list[RetrievedChunk]
    citations: list[Citation]
    total_sources: int
    relevance_threshold: float = 0.5
    
    # Extended evidence metadata
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = "general"
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def filtered_chunks(self, threshold: float = 0.5) -> list[RetrievedChunk]:
        """Get chunks above relevance threshold."""
        return [c for c in self.chunks if c.relevance_score >= threshold]
    
    def add_chunk(self, chunk: RetrievedChunk) -> None:
        """Add a chunk to evidence."""
        self.chunks.append(chunk)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type,
            "chunks": [c.to_dict() for c in self.chunks],
            "citations": [c.to_dict() for c in self.citations],
            "total_sources": self.total_sources,
            "relevance_threshold": self.relevance_threshold,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class KnowledgeChunk:
    """Knowledge chunk for storage in vector database."""
    chunk_id: str
    content: str
    
    # Source info
    source_type: SourceType
    source_id: str
    source_uri: str = ""
    
    # Embedding metadata
    embedding_vector: list[float] = field(default_factory=list)
    embedding_model: str = ""
    embedding_dimension: int = 0
    
    # Content metadata
    title: str = ""
    language: str = "en"
    chunk_type: ChunkType = ChunkType.TEXT
    
    # Classification
    medical_specialty: str = ""
    device_categories: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    # Medical codes
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    loinc_codes: list[str] = field(default_factory=list)
    
    # Ownership
    tenant_id: str = ""
    created_by: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Status
    status: ChunkStatus = ChunkStatus.ACTIVE
    
    # Versioning
    version: int = 1
    
    @classmethod
    def create(
        cls,
        content: str,
        source_type: SourceType,
        source_id: str,
        **kwargs,
    ) -> KnowledgeChunk:
        """Factory method to create a knowledge chunk."""
        return cls(
            chunk_id=str(uuid.uuid4()),
            content=content,
            source_type=source_type,
            source_id=source_id,
            **kwargs,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "source_uri": self.source_uri,
            "title": self.title,
            "language": self.language,
            "chunk_type": self.chunk_type.value,
            "medical_specialty": self.medical_specialty,
            "device_categories": self.device_categories,
            "standards": self.standards,
            "tags": self.tags,
            "icd_codes": self.icd_codes,
            "snomed_codes": self.snomed_codes,
            "loinc_codes": self.loinc_codes,
            "tenant_id": self.tenant_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value,
            "version": self.version,
        }


@dataclass
class ChunkSearchResult:
    """Result of a chunk search."""
    chunk: KnowledgeChunk
    relevance_score: float
    matched_terms: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    
    # Extended result metadata
    distance: float = 0.0
    rank: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk": self.chunk.to_dict(),
            "relevance_score": self.relevance_score,
            "matched_terms": self.matched_terms,
            "highlights": self.highlights,
            "distance": self.distance,
            "rank": self.rank,
        }


@dataclass
class ChunkSearchResponse:
    """Response from a chunk search."""
    query: str
    results: list[ChunkSearchResult]
    total_found: int = 0
    search_time_ms: int = 0
    
    # Metadata
    query_embedding_time_ms: int = 0
    retrieval_time_ms: int = 0
    
    # Filters used
    filters_applied: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_found": self.total_found,
            "search_time_ms": self.search_time_ms,
            "query_embedding_time_ms": self.query_embedding_time_ms,
            "retrieval_time_ms": self.retrieval_time_ms,
            "filters_applied": self.filters_applied,
        }
