"""In-memory Qdrant service for testing and development."""

from __future__ import annotations

import time
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
from core.PHASE_2.cognitive.rag.domain.services.qdrant_service import (
    IQdrantService,
    CollectionStats,
    ChunkBatchResult,
    ChunkFilter,
)


class InMemoryQdrantService(IQdrantService):
    """In-memory implementation of Qdrant service."""
    
    def __init__(self):
        """Initialize in-memory store."""
        self._collections: dict[str, dict[str, KnowledgeChunk]] = {}
        self._vectors: dict[str, dict[str, list[float]]] = {}
        self._metadata: dict[str, dict] = {}
    
    async def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> bool:
        """Create a collection."""
        if name not in self._collections:
            self._collections[name] = {}
            self._vectors[name] = {}
            self._metadata[name] = {
                "vector_size": vector_size,
                "distance": distance,
                "created_at": datetime.now(UTC).isoformat(),
            }
            return True
        return False
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if name in self._collections:
            del self._collections[name]
            del self._vectors[name]
            del self._metadata[name]
            return True
        return False
    
    async def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        return name in self._collections
    
    async def get_collection_stats(self, name: str) -> CollectionStats:
        """Get collection statistics."""
        if name not in self._collections:
            raise ValueError(f"Collection {name} does not exist")
        
        return CollectionStats(
            name=name,
            vector_count=len(self._vectors[name]),
            point_count=len(self._collections[name]),
            segments_count=1,
            status="green",
            vector_dimension=self._metadata[name].get("vector_size", 1536),
            distance_metric=self._metadata[name].get("distance", "Cosine"),
            index_parameters={},
        )
    
    async def upsert_chunk(self, chunk: KnowledgeChunk) -> str:
        """Insert or update a chunk."""
        collection = "default"
        self._collections.setdefault(collection, {})
        self._vectors.setdefault(collection, {})
        
        chunk.chunk_id = chunk.chunk_id or str(uuid.uuid4())
        chunk.updated_at = datetime.now(UTC)
        
        self._collections[collection][chunk.chunk_id] = chunk
        
        # Store vector if provided
        if chunk.embedding_vector:
            self._vectors[collection][chunk.chunk_id] = chunk.embedding_vector
        
        return chunk.chunk_id
    
    async def upsert_chunks(self, chunks: list[KnowledgeChunk]) -> ChunkBatchResult:
        """Insert or update multiple chunks."""
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        
        successful = 0
        failed = 0
        errors = []
        chunk_ids = []
        
        for chunk in chunks:
            try:
                chunk_id = await self.upsert_chunk(chunk)
                chunk_ids.append(chunk_id)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(f"Chunk {chunk.chunk_id}: {str(e)}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return ChunkBatchResult(
            batch_id=batch_id,
            total=len(chunks),
            successful=successful,
            failed=failed,
            errors=errors,
            chunk_ids=chunk_ids,
            duration_ms=duration_ms,
        )
    
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
        start_time = time.time()
        
        collection_data = self._collections.get(collection, {})
        vectors_data = self._vectors.get(collection, {})
        
        results = []
        
        for chunk_id, chunk in collection_data.items():
            # Apply filters
            if filter_params:
                if not self._matches_filter(chunk, filter_params):
                    continue
            
            # Calculate similarity (cosine)
            chunk_vector = vectors_data.get(chunk_id, chunk.embedding_vector)
            if chunk_vector:
                similarity = self._cosine_similarity(query_vector, chunk_vector)
                
                if similarity >= (filter_params.min_relevance_score if filter_params else 0.5):
                    results.append(ChunkSearchResult(
                        chunk=chunk,
                        relevance_score=similarity,
                        distance=1 - similarity,  # Distance is inverse of similarity
                        rank=0,
                    ))
        
        # Sort by relevance and assign ranks
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        for i, result in enumerate(results[:top_k]):
            result.rank = i + 1
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return ChunkSearchResponse(
            query="",
            results=results[:top_k],
            total_found=len(results),
            search_time_ms=search_time_ms,
            filters_applied=filter_params.to_qdrant_filter() if filter_params else {},
        )
    
    async def search_chunks_by_text(
        self,
        query_text: str,
        collection: str,
        filter_params: ChunkFilter | None = None,
        top_k: int = 10,
    ) -> ChunkSearchResponse:
        """Search for chunks by text."""
        # For in-memory, simulate with simple text matching
        start_time = time.time()
        
        collection_data = self._collections.get(collection, {})
        results = []
        
        for chunk_id, chunk in collection_data.items():
            # Apply filters
            if filter_params:
                if not self._matches_filter(chunk, filter_params):
                    continue
            
            # Simple text matching (in real implementation, would use embeddings)
            query_lower = query_text.lower()
            content_lower = chunk.content.lower()
            
            if query_lower in content_lower or chunk.title.lower().find(query_lower) >= 0:
                # Calculate a simple relevance score based on matches
                matches = content_lower.count(query_lower)
                relevance = min(1.0, matches * 0.1 + 0.5)  # Base 0.5 + 0.1 per match
                
                results.append(ChunkSearchResult(
                    chunk=chunk,
                    relevance_score=relevance,
                    matched_terms=[query_text],
                    rank=0,
                ))
        
        # Sort and rank
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        for i, result in enumerate(results[:top_k]):
            result.rank = i + 1
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return ChunkSearchResponse(
            query=query_text,
            results=results[:top_k],
            total_found=len(results),
            search_time_ms=search_time_ms,
            filters_applied=filter_params.to_qdrant_filter() if filter_params else {},
        )
    
    async def get_chunk(self, chunk_id: str, collection: str) -> KnowledgeChunk | None:
        """Get a chunk by ID."""
        collection_data = self._collections.get(collection, {})
        return collection_data.get(chunk_id)
    
    async def delete_chunk(self, chunk_id: str, collection: str) -> bool:
        """Delete a chunk."""
        if collection in self._collections and chunk_id in self._collections[collection]:
            del self._collections[collection][chunk_id]
            if collection in self._vectors and chunk_id in self._vectors[collection]:
                del self._vectors[collection][chunk_id]
            return True
        return False
    
    async def delete_chunks(
        self,
        chunk_ids: list[str],
        collection: str,
    ) -> ChunkBatchResult:
        """Delete multiple chunks."""
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        
        successful = 0
        failed = 0
        errors = []
        
        for chunk_id in chunk_ids:
            try:
                if await self.delete_chunk(chunk_id, collection):
                    successful += 1
                else:
                    failed += 1
                    errors.append(f"Chunk {chunk_id} not found")
            except Exception as e:
                failed += 1
                errors.append(f"Chunk {chunk_id}: {str(e)}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        return ChunkBatchResult(
            batch_id=batch_id,
            total=len(chunk_ids),
            successful=successful,
            failed=failed,
            errors=errors,
            duration_ms=duration_ms,
        )
    
    async def health_check(self) -> dict:
        """Check Qdrant health."""
        return {
            "status": "healthy",
            "collections": len(self._collections),
            "total_points": sum(len(c) for c in self._collections.values()),
        }
    
    def _matches_filter(self, chunk: KnowledgeChunk, filter_params: ChunkFilter) -> bool:
        """Check if chunk matches filter."""
        if filter_params.tenant_id and chunk.tenant_id != filter_params.tenant_id:
            return False
        
        if filter_params.source_types and chunk.source_type not in filter_params.source_types:
            return False
        
        if filter_params.medical_specialty and chunk.medical_specialty != filter_params.medical_specialty:
            return False
        
        if filter_params.device_categories:
            if not any(c in chunk.device_categories for c in filter_params.device_categories):
                return False
        
        if filter_params.standards:
            if not any(s in chunk.standards for s in filter_params.standards):
                return False
        
        if filter_params.tags:
            if not any(t in chunk.tags for t in filter_params.tags):
                return False
        
        if filter_params.status and chunk.status != filter_params.status:
            return False
        
        return True
    
    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
