"""
Qdrant Vector Database Integration Module

Provides vector storage and search capabilities for clinical knowledge.
Extends PHASE_2 cognitive/rag with specialized clinical collections.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol


class ClinicalCollection(str, Enum):
    """Clinical knowledge collections."""
    MEDICAL_LITERATURE = "medical_literature"
    DEVICE_MANUALS = "device_manuals"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    REGULATORY_DOCS = "regulatory_docs"
    KNOWLEDGE_ARTICLES = "knowledge_articles"
    EVIDENCE_BASE = "evidence_base"


@dataclass
class VectorPoint:
    """Vector point in Qdrant."""
    id: str
    vector: list[float]
    payload: dict = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result with score."""
    id: str
    score: float
    payload: dict = field(default_factory=dict)
    content: str = ""


@dataclass
class CollectionConfig:
    """Qdrant collection configuration."""
    name: str
    vector_size: int
    distance: str = "Cosine"
    description: str = ""


class IQdrantClient(Protocol):
    """Protocol for Qdrant client."""
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filter_query: dict | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        ...
    
    async def upsert(
        self,
        collection: str,
        points: list[VectorPoint],
    ) -> bool:
        """Insert or update points."""
        ...


class QdrantClient:
    """Qdrant client wrapper for clinical knowledge."""
    
    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
    ):
        """Initialize client."""
        self.url = url
        self.api_key = api_key
        self._collections: dict[str, list[VectorPoint]] = {}
    
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filter_query: dict | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        # Placeholder - in-memory implementation
        if collection not in self._collections:
            return []
        
        results = []
        for point in self._collections[collection][:top_k]:
            results.append(SearchResult(
                id=point.id,
                score=0.9,  # Placeholder
                payload=point.payload,
                content=point.payload.get("content", ""),
            ))
        return results
    
    async def upsert(
        self,
        collection: str,
        points: list[VectorPoint],
    ) -> bool:
        """Insert or update points."""
        if collection not in self._collections:
            self._collections[collection] = []
        self._collections[collection].extend(points)
        return True


class CollectionManager:
    """Manages clinical collections in Qdrant."""
    
    def __init__(self, client: QdrantClient):
        """Initialize manager."""
        self.client = client
        self._configs: dict[str, CollectionConfig] = {}
    
    async def create_collection(self, config: CollectionConfig) -> bool:
        """Create a collection."""
        self._configs[config.name] = config
        return True
    
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        if name in self._configs:
            del self._configs[name]
        return True
    
    async def get_config(self, name: str) -> CollectionConfig | None:
        """Get collection configuration."""
        return self._configs.get(name)
    
    def list_collections(self) -> list[str]:
        """List all collections."""
        return list(self._configs.keys())


class VectorStore:
    """Clinical vector store operations."""
    
    def __init__(self, client: QdrantClient):
        """Initialize store."""
        self.client = client
    
    async def store_chunk(
        self,
        collection: str,
        chunk_id: str,
        vector: list[float],
        content: str,
        metadata: dict,
    ) -> bool:
        """Store a knowledge chunk."""
        point = VectorPoint(
            id=chunk_id,
            vector=vector,
            payload={
                "content": content,
                **metadata,
            },
        )
        return await self.client.upsert(collection, [point])
    
    async def search_similar(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        """Search for similar chunks."""
        return await self.client.search(
            collection=collection,
            query_vector=query_vector,
            top_k=top_k,
            filter_query=filters,
        )


class HybridSearch:
    """Hybrid search combining dense and sparse retrieval."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_manager,
    ):
        """Initialize hybrid search."""
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager
    
    async def search(
        self,
        collection: str,
        query_text: str,
        top_k: int = 10,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
    ) -> list[SearchResult]:
        """Perform hybrid search."""
        # Generate query embedding
        embedding = await self.embedding_manager.embed_text(query_text)
        
        # Vector search
        vector_results = await self.vector_store.search_similar(
            collection=collection,
            query_vector=embedding.vector,
            top_k=top_k,
        )
        
        # Keyword search (placeholder)
        keyword_results = []  # Would implement BM25 or similar
        
        # Fuse results
        fused_results = self._fuse_results(
            vector_results,
            keyword_results,
            dense_weight,
            sparse_weight,
        )
        
        return fused_results[:top_k]
    
    def _fuse_results(
        self,
        dense: list[SearchResult],
        sparse: list[SearchResult],
        dense_weight: float,
        sparse_weight: float,
    ) -> list[SearchResult]:
        """Fuse dense and sparse results using RRF."""
        # Simplified RRF fusion
        scores: dict[str, float] = {}
        
        for i, result in enumerate(dense):
            rrf_score = 1 / (60 + i + 1)
            scores[result.id] = scores.get(result.id, 0) + dense_weight * rrf_score
        
        for i, result in enumerate(sparse):
            rrf_score = 1 / (60 + i + 1)
            scores[result.id] = scores.get(result.id, 0) + sparse_weight * rrf_score
        
        all_results = {**{r.id: r for r in dense}, **{r.id: r for r in sparse}}
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return [all_results[id] for id in sorted_ids if id in all_results]
