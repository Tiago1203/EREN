"""RAG domain services."""
from typing import Protocol
from core.PHASE_2.cognitive.rag.domain.entities import RetrievedChunk, Evidence, Citation


class RetrievalFilters(Protocol):
    """Filters for retrieval."""
    tenant_id: str
    domain: str | None = None
    categories: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None


class KnowledgeRetriever(Protocol):
    """Protocol for knowledge retrieval."""
    
    async def retrieve(
        self,
        query: str,
        filters: RetrievalFilters,
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant knowledge chunks."""
        ...


class EntityRetriever(Protocol):
    """Protocol for entity retrieval."""
    
    async def retrieve(
        self,
        query: str,
        entity_types: list[str],
        filters: RetrievalFilters,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant entities."""
        ...


class RAGOrchestrator:
    """Orchestrates RAG retrieval from multiple sources."""
    
    def __init__(
        self,
        knowledge_retriever: KnowledgeRetriever,
        entity_retriever: EntityRetriever | None = None,
    ):
        self.knowledge_retriever = knowledge_retriever
        self.entity_retriever = entity_retriever
    
    async def retrieve(
        self,
        query: str,
        filters: RetrievalFilters,
        top_k: int = 10,
    ) -> Evidence:
        """Retrieve evidence from all sources."""
        chunks = []
        citations = []
        
        # Knowledge retrieval
        knowledge_chunks = await self.knowledge_retriever.retrieve(query, filters, top_k)
        chunks.extend(knowledge_chunks)
        
        # Entity retrieval if available
        if self.entity_retriever:
            entity_chunks = await self.entity_retriever.retrieve(
                query,
                ["device", "incident", "staff"],
                filters,
            )
            chunks.extend(entity_chunks)
        
        # Sort by relevance
        chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Take top K
        chunks = chunks[:top_k]
        
        # Create citations
        seen_sources = set()
        for chunk in chunks:
            if chunk.source_id not in seen_sources:
                citations.append(Citation(
                    id=chunk.id,
                    source_type=chunk.source_type,
                    source_id=chunk.source_id,
                    citation_text=chunk.content[:100] + "...",
                ))
                seen_sources.add(chunk.source_id)
        
        return Evidence(
            chunks=chunks,
            citations=citations,
            total_sources=len(seen_sources),
        )
