"""RAG domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from core.PHASE_2.cognitive.rag.domain.entities.chunk import (
    SourceType as ExtendedSourceType,
    ChunkStatus,
    ChunkType,
    RetrievedChunk,
    Citation,
    Evidence,
    KnowledgeChunk,
    ChunkSearchResult,
    ChunkSearchResponse,
)


class SourceType(str, Enum):
    """Evidence source type (legacy compatibility)."""
    KNOWLEDGE = "knowledge"
    ENTITY = "entity"
    TOOL = "tool"
    USER = "user"


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved evidence chunk (legacy compatibility)."""
    id: str
    content: str
    source_type: SourceType
    source_id: str
    relevance_score: float
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Citation:
    """Citation for evidence (legacy compatibility)."""
    id: str
    source_type: SourceType
    source_id: str
    citation_text: str
    citation_url: Optional[str] = None
    accessible: bool = True


@dataclass
class Evidence:
    """Evidence used in reasoning (legacy compatibility)."""
    chunks: list[RetrievedChunk]
    citations: list[Citation]
    total_sources: int
    relevance_threshold: float = 0.5
    
    def filtered_chunks(self, threshold: float = 0.5) -> list[RetrievedChunk]:
        """Get chunks above relevance threshold."""
        return [c for c in self.chunks if c.relevance_score >= threshold]
    
    def add_chunk(self, chunk: RetrievedChunk) -> None:
        """Add a chunk to evidence."""
        self.chunks.append(chunk)


__all__ = [
    # Legacy classes
    "SourceType",
    "RetrievedChunk",
    "Citation",
    "Evidence",
    # Extended classes
    "ExtendedSourceType",
    "ChunkStatus",
    "ChunkType",
    "KnowledgeChunk",
    "ChunkSearchResult",
    "ChunkSearchResponse",
]
