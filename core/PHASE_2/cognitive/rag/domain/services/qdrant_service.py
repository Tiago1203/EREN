"""Qdrant service for RAG domain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from core.PHASE_2.cognitive.rag.domain.entities.chunk import (
    SourceType,
    ChunkStatus,
    KnowledgeChunk,
    ChunkSearchResult,
    ChunkSearchResponse,
)


class QdrantCollection:
    """Qdrant collection configuration."""
    
    KNOWLEDGE = "knowledge"
    DEVICE = "device"
    CLINICAL = "clinical"
    STANDARDS = "standards"
    GUIDELINES = "guidelines"


@dataclass
class QdrantConfig:
    """Configuration for Qdrant client."""
    url: str
    api_key: Optional[str] = None
    timeout: int = 30
    prefer_grpc: bool = True
    
    # Collection settings
    default_vector_size: int = 1536
    distance_metric: str = "Cosine"  # Cosine, Euclid, Dot
    
    # Search settings
    default_top_k: int = 10
    min_relevance_score: float = 0.5
    
    # Performance
    max_workers: int = 4
    batch_size: int = 100


@dataclass
class ChunkFilter:
    """Filter for chunk search."""
    tenant_id: Optional[str] = None
    source_types: list[SourceType] | None = None
    medical_specialty: Optional[str] = None
    device_categories: list[str] | None = None
    standards: list[str] | None = None
    tags: list[str] | None = None
    icd_codes: list[str] | None = None
    snomed_codes: list[str] | None = None
    status: ChunkStatus | None = ChunkStatus.ACTIVE
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    
    def to_qdrant_filter(self) -> dict:
        """Convert to Qdrant filter format."""
        conditions = []
        
        if self.tenant_id:
            conditions.append({
                "key": "tenant_id",
                "match": {"value": self.tenant_id}
            })
        
        if self.source_types:
            conditions.append({
                "key": "source_type",
                "match": {"any": [s.value for s in self.source_types]}
            })
        
        if self.medical_specialty:
            conditions.append({
                "key": "medical_specialty",
                "match": {"value": self.medical_specialty}
            })
        
        if self.device_categories:
            conditions.append({
                "key": "device_categories",
                "match": {"any": self.device_categories}
            })
        
        if self.standards:
            conditions.append({
                "key": "standards",
                "match": {"any": self.standards}
            })
        
        if self.tags:
            conditions.append({
                "key": "tags",
                "match": {"any": self.tags}
            })
        
        if self.status:
            conditions.append({
                "key": "status",
                "match": {"value": self.status.value}
            })
        
        if self.date_from:
            conditions.append({
                "key": "created_at",
                "range": {"gte": self.date_from}
            })
        
        if self.date_to:
            conditions.append({
                "key": "created_at",
                "range": {"lte": self.date_to}
            })
        
        if not conditions:
            return {}
        
        return {"must": conditions}


@dataclass
class ChunkBatchResult:
    """Result of batch chunk operations."""
    batch_id: str
    total: int
    successful: int
    failed: int
    errors: list[str] = field(default_factory=list)
    chunk_ids: list[str] = field(default_factory=list)
    duration_ms: int = 0


@dataclass
class CollectionStats:
    """Statistics for a collection."""
    name: str
    vector_count: int
    point_count: int
    segments_count: int
    status: str
    vector_dimension: int
    distance_metric: str
    index_parameters: dict = field(default_factory=dict)


class IQdrantService:
    """Interface for Qdrant service operations."""
    
    async def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """Create a collection."""
        ...
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        ...
    
    async def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        ...
    
    async def get_collection_stats(self, name: str) -> CollectionStats:
        """Get collection statistics."""
        ...
    
    async def upsert_chunk(self, chunk: KnowledgeChunk) -> str:
        """Insert or update a chunk."""
        ...
    
    async def upsert_chunks(self, chunks: list[KnowledgeChunk]) -> ChunkBatchResult:
        """Insert or update multiple chunks."""
        ...
    
    async def search_chunks(
        self,
        query_vector: list[float],
        collection: str,
        filter_params: ChunkFilter | None = None,
        top_k: int = 10,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> ChunkSearchResponse:
        """Search for similar chunks."""
        ...
    
    async def search_chunks_by_text(
        self,
        query_text: str,
        collection: str,
        filter_params: ChunkFilter | None = None,
        top_k: int = 10,
    ) -> ChunkSearchResponse:
        """Search for chunks by text (uses embedding)."""
        ...
    
    async def get_chunk(self, chunk_id: str, collection: str) -> KnowledgeChunk | None:
        """Get a chunk by ID."""
        ...
    
    async def delete_chunk(self, chunk_id: str, collection: str) -> bool:
        """Delete a chunk."""
        ...
    
    async def delete_chunks(
        self,
        chunk_ids: list[str],
        collection: str,
    ) -> ChunkBatchResult:
        """Delete multiple chunks."""
        ...
    
    async def health_check(self) -> dict:
        """Check Qdrant health."""
        ...


class QdrantServiceFactory:
    """Factory for creating Qdrant services."""
    
    @staticmethod
    def create_memory_service() -> IQdrantService:
        """Create an in-memory Qdrant service for testing."""
        from core.PHASE_2.cognitive.rag.domain.services.memory_qdrant_service import (
            InMemoryQdrantService,
        )
        return InMemoryQdrantService()
    
    @staticmethod
    def create_from_config(config: QdrantConfig) -> IQdrantService:
        """Create a real Qdrant service from config."""
        # This would return a real Qdrant service
        # For now, return in-memory
        return QdrantServiceFactory.create_memory_service()
