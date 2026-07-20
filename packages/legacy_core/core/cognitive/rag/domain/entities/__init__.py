"""RAG domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    """Evidence source type."""
    KNOWLEDGE = "knowledge"
    ENTITY = "entity"
    TOOL = "tool"
    USER = "user"


@dataclass(frozen=True)
class RetrievedChunk:
    """Retrieved evidence chunk."""
    id: str
    content: str
    source_type: SourceType
    source_id: str
    relevance_score: float
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Citation:
    """Citation for evidence."""
    id: str
    source_type: SourceType
    source_id: str
    citation_text: str
    citation_url: Optional[str] = None
    accessible: bool = True


@dataclass
class Evidence:
    """Evidence used in reasoning."""
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
