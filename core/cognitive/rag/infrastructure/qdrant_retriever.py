"""Qdrant-based Knowledge Retriever."""
from typing import Any
from dataclasses import dataclass

from core.cognitive.rag.domain.entities import RetrievedChunk, SourceType
from core.cognitive.reasoning.infrastructure.llm_adapters.openai_adapter import OpenAIAdapter


@dataclass
class QdrantConfig:
    """Qdrant configuration."""
    url: str
    api_key: str | None = None
    collection_name: str = "knowledge"
    vector_size: int = 1536  # OpenAI embedding dimension


class QdrantKnowledgeRetriever:
    """Knowledge retriever using Qdrant vector database."""
    
    def __init__(
        self,
        qdrant_client: Any,
        embedder: OpenAIAdapter,
        config: QdrantConfig,
    ):
        self.client = qdrant_client
        self.embedder = embedder
        self.config = config
    
    async def retrieve(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant knowledge chunks.
        
        Args:
            query: Search query
            tenant_id: Tenant ID for multi-tenancy
            filters: Additional filters (category, date, etc.)
            top_k: Number of results to return
        
        Returns:
            List of retrieved chunks
        """
        # Generate query embedding
        embedding_result = await self.embedder.embed([query])
        query_vector = embedding_result.embeddings[0]
        
        # Build filter
        must_conditions = [
            {"key": "tenant_id", "match": {"value": tenant_id}}
        ]
        
        if filters:
            if filters.get("category"):
                must_conditions.append({
                    "key": "category",
                    "match": {"value": filters["category"]}
                })
            if filters.get("date_from"):
                must_conditions.append({
                    "key": "created_at",
                    "range": {"gte": filters["date_from"]}
                })
        
        # Search Qdrant
        results = await self.client.search(
            collection_name=self.config.collection_name,
            query_vector=query_vector,
            query_filter={
                "must": must_conditions
            },
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        
        chunks = []
        for result in results:
            payload = result.payload
            
            chunks.append(RetrievedChunk(
                id=str(result.id),
                content=payload.get("content", ""),
                source_type=SourceType.KNOWLEDGE,
                source_id=payload.get("source_id", str(result.id)),
                relevance_score=result.score,
                metadata={
                    "title": payload.get("title"),
                    "category": payload.get("category"),
                    "source": payload.get("source"),
                    "url": payload.get("url"),
                },
            ))
        
        return chunks
    
    async def retrieve_hybrid(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """
        Hybrid search: vector + keyword.
        
        Combines semantic search with keyword matching.
        """
        # Get vector results
        vector_results = await self.retrieve(query, tenant_id, filters, top_k * 2)
        
        # In production, would also do keyword search
        # and combine results using RRF (Reciprocal Rank Fusion)
        
        # For now, just return vector results
        return vector_results[:top_k]
    
    async def add_chunk(
        self,
        chunk: RetrievedChunk,
        content: str,
        metadata: dict,
    ) -> str:
        """
        Add a new chunk to the knowledge base.
        
        Args:
            chunk: Chunk metadata
            content: Text content to embed
            metadata: Additional metadata
        
        Returns:
            Chunk ID
        """
        # Generate embedding
        embedding_result = await self.embedder.embed([content])
        vector = embedding_result.embeddings[0]
        
        # Prepare payload
        payload = {
            "content": content,
            "source_id": chunk.source_id,
            "source_type": chunk.source_type.value,
            **metadata,
        }
        
        # Insert into Qdrant
        result = await self.client.upsert(
            collection_name=self.config.collection_name,
            points=[{
                "id": chunk.id,
                "vector": vector,
                "payload": payload,
            }]
        )
        
        return chunk.id
    
    async def delete_chunk(self, chunk_id: str) -> None:
        """Delete a chunk from the knowledge base."""
        await self.client.delete(
            collection_name=self.config.collection_name,
            points_selector=[chunk_id],
        )
    
    async def create_collection(self) -> None:
        """Create the knowledge collection if it doesn't exist."""
        try:
            await self.client.get_collection(self.config.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            await self.client.create_collection(
                collection_name=self.config.collection_name,
                vectors_config={
                    "size": self.config.vector_size,
                    "distance": "Cosine",
                },
            )


# Factory function
def create_qdrant_retriever(
    qdrant_url: str,
    qdrant_api_key: str | None,
    openai_api_key: str,
    collection_name: str = "knowledge",
) -> QdrantKnowledgeRetriever:
    """Create a Qdrant knowledge retriever."""
    try:
        from qdrant_client import AsyncQdrantClient
    except ImportError:
        raise ImportError(
            "qdrant-client not installed. "
            "Install with: pip install qdrant-client"
        )
    
    qdrant_client = AsyncQdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )
    
    embedder = OpenAIAdapter(
        api_key=openai_api_key,
        model="text-embedding-3-small",
    )
    
    config = QdrantConfig(
        url=qdrant_url,
        api_key=qdrant_api_key,
        collection_name=collection_name,
    )
    
    return QdrantKnowledgeRetriever(qdrant_client, embedder, config)
