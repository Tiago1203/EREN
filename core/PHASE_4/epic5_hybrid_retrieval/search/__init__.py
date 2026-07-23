"""
PHASE 4 - EPIC 5: Search Module

Componentes de búsqueda:
- Semantic Search
- Keyword Search
- Vector Search
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import asyncio


@dataclass
class SearchParams:
    """Parámetros de búsqueda."""
    query: str
    limit: int = 10
    offset: int = 0
    score_threshold: float = 0.0
    filters: dict | None = None


@dataclass
class ScoredResult:
    """Resultado con score."""
    result_id: str
    score: float
    payload: dict = field(default_factory=dict)
    source: str = ""  # vector, keyword, hybrid


@dataclass
class SearchResponse:
    """Respuesta de búsqueda."""
    query: str
    results: list[ScoredResult] = field(default_factory=list)
    total: int = 0
    search_time_ms: int = 0
    strategy_used: str = ""


class BaseSearcher(ABC):
    """Clase base para searchers."""
    
    @abstractmethod
    async def search(self, params: SearchParams) -> SearchResponse:
        """Ejecuta búsqueda."""
        ...


class VectorSearcher(BaseSearcher):
    """Búsqueda vectorial usando Qdrant."""
    
    def __init__(self, vector_client=None):
        self.client = vector_client
    
    async def search(self, params: SearchParams) -> SearchResponse:
        """Ejecuta búsqueda vectorial."""
        import time
        start = time.time()
        
        if not self.client:
            # Return mock results
            return SearchResponse(
                query=params.query,
                results=[],
                total=0,
                search_time_ms=int((time.time() - start) * 1000),
                strategy_used="vector",
            )
        
        try:
            # Generate query vector
            query_vector = await self._generate_query_vector(params.query)
            
            # Search in vector DB
            vector_results = await self.client.search(
                collection_name="knowledge",
                vector=query_vector,
                limit=params.limit,
                score_threshold=params.score_threshold,
            )
            
            # Convert to ScoredResult
            results = [
                ScoredResult(
                    result_id=r.get("id", ""),
                    score=r.get("score", 0.0),
                    payload=r.get("payload", {}),
                    source="vector",
                )
                for r in vector_results
            ]
            
            return SearchResponse(
                query=params.query,
                results=results,
                total=len(results),
                search_time_ms=int((time.time() - start) * 1000),
                strategy_used="vector",
            )
        except Exception:
            return SearchResponse(
                query=params.query,
                results=[],
                total=0,
                search_time_ms=int((time.time() - start) * 1000),
                strategy_used="vector",
            )
    
    async def _generate_query_vector(self, query: str) -> list[float]:
        """Genera vector para query."""
        # Placeholder - in production would use embedding model
        import random
        return [random.random() for _ in range(384)]


class KeywordSearcher(BaseSearcher):
    """Búsqueda por keywords."""
    
    def __init__(self, document_store=None):
        self.document_store = document_store
        self._in_memory_index: dict[str, dict] = {}
    
    async def search(self, params: SearchParams) -> SearchResponse:
        """Ejecuta búsqueda por keywords."""
        import time
        start = time.time()
        
        # Extract keywords from query
        keywords = self._extract_keywords(params.query)
        
        # Search in index
        results = []
        for doc_id, doc in self._in_memory_index.items():
            text = doc.get("text", "").lower()
            
            # Calculate keyword match score
            matches = sum(1 for kw in keywords if kw.lower() in text)
            if matches > 0:
                score = matches / len(keywords)
                results.append(ScoredResult(
                    result_id=doc_id,
                    score=score,
                    payload=doc,
                    source="keyword",
                ))
        
        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)
        results = results[:params.limit]
        
        return SearchResponse(
            query=params.query,
            results=results,
            total=len(results),
            search_time_ms=int((time.time() - start) * 1000),
            strategy_used="keyword",
        )
    
    def _extract_keywords(self, query: str) -> list[str]:
        """Extrae keywords del query."""
        # Simple extraction - remove stopwords
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "is", "are", "was",
            "what", "how", "when", "where", "why", "patient", "case",
        }
        
        words = query.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords
    
    def index_document(self, doc_id: str, document: dict) -> None:
        """Indexa documento."""
        self._in_memory_index[doc_id] = document
    
    def clear_index(self) -> None:
        """Limpia índice."""
        self._in_memory_index.clear()


class SemanticSearcher(BaseSearcher):
    """Búsqueda semántica combinando múltiples fuentes."""
    
    def __init__(
        self,
        vector_searcher: VectorSearcher | None = None,
        keyword_searcher: KeywordSearcher | None = None,
    ):
        self.vector_searcher = vector_searcher or VectorSearcher()
        self.keyword_searcher = keyword_searcher or KeywordSearcher()
    
    async def search(self, params: SearchParams) -> SearchResponse:
        """Ejecuta búsqueda semántica."""
        import time
        start = time.time()
        
        # Run both searches in parallel
        vector_task = self.vector_searcher.search(params)
        keyword_task = self.keyword_searcher.search(params)
        
        vector_response, keyword_response = await asyncio.gather(
            vector_task, keyword_task
        )
        
        # Combine results
        combined = {}
        
        for result in vector_response.results:
            combined[result.result_id] = {
                "result": result,
                "vector_score": result.score,
                "keyword_score": 0.0,
            }
        
        for result in keyword_response.results:
            if result.result_id in combined:
                combined[result.result_id]["keyword_score"] = result.score
            else:
                combined[result.result_id] = {
                    "result": result,
                    "vector_score": 0.0,
                    "keyword_score": result.score,
                }
        
        # Calculate hybrid score (weighted average)
        for doc_id, data in combined.items():
            hybrid_score = (
                0.7 * data["vector_score"] +
                0.3 * data["keyword_score"]
            )
            data["result"].score = hybrid_score
        
        # Sort by hybrid score
        results = [d["result"] for d in combined.values()]
        results.sort(key=lambda r: r.score, reverse=True)
        results = results[:params.limit]
        
        return SearchResponse(
            query=params.query,
            results=results,
            total=len(results),
            search_time_ms=int((time.time() - start) * 1000),
            strategy_used="semantic",
        )


__all__ = [
    "SearchParams",
    "ScoredResult",
    "SearchResponse",
    "BaseSearcher",
    "VectorSearcher",
    "KeywordSearcher",
    "SemanticSearcher",
]
