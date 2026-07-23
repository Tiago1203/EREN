"""
PHASE 4 - EPIC 5: Hybrid Retrieval Engine

Búsqueda híbrida combinando:
- Vector Search (embeddings)
- BM25 (keyword search)
- Filtros estructurados
- Hybrid Ranking (RRF, weighted)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import math

from core.PHASE_4.foundation import (
    EmbeddingVector,
    KnowledgeQuery,
    RetrievalResult,
    SearchResult,
    KnowledgeDomain,
)


class RetrievalStrategy(str, Enum):
    """Estrategias de retrieval."""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    RRF = "rrf"  # Reciprocal Rank Fusion
    WEIGHTED = "weighted"


class BM25Variant(str, Enum):
    """Variantes de BM25."""
    CLASSIC = "classic"
    BM25L = "bm25l"
    BM25PLUS = "bm25plus"


@dataclass
class RetrievalFilters:
    """Filtros para retrieval."""
    domains: list[KnowledgeDomain] | None = None
    medical_specialties: list[str] | None = None
    device_categories: list[str] | None = None
    evidence_levels: list[str] | None = None
    quality_min: float | None = None
    date_from: str | None = None
    date_to: str | None = None
    source_types: list[str] | None = None
    governance_status: str | None = "published"


@dataclass
class VectorSearchParams:
    """Parámetros para búsqueda vectorial."""
    top_k: int = 10
    min_score: float = 0.5
    ef_search: int = 128  # HNSW ef_search parameter


@dataclass
class KeywordSearchParams:
    """Parámetros para búsqueda por keywords."""
    top_k: int = 10
    min_score: float = 0.3
    use_bm25: bool = True
    bm25_variant: BM25Variant = BM25Variant.CLASSIC
    k1: float = 1.5  # BM25 k1 parameter
    b: float = 0.75  # BM25 b parameter


@dataclass
class HybridSearchConfig:
    """Configuración para búsqueda híbrida."""
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    
    # Vector search
    vector_weight: float = 0.7
    vector_params: VectorSearchParams = field(default_factory=VectorSearchParams)
    
    # Keyword search
    keyword_weight: float = 0.3
    keyword_params: KeywordSearchParams = field(default_factory=KeywordSearchParams)
    
    # Fusion
    rrf_k: int = 60  # RRF k parameter


@dataclass
class ScoredResult:
    """Resultado con score individual."""
    result: SearchResult
    vector_score: float = 0.0
    keyword_score: float = 0.0
    combined_score: float = 0.0
    source: str = ""  # vector, keyword, hybrid


@dataclass
class FusionResult:
    """Resultado de fusión de búsquedas."""
    query_id: str
    results: list[ScoredResult]
    total_found: int
    vector_search_time_ms: int = 0
    keyword_search_time_ms: int = 0
    fusion_time_ms: int = 0


class IVectorSearcher(Protocol):
    """Protocolo para búsqueda vectorial."""
    
    async def search(
        self,
        query_vector: EmbeddingVector,
        collection: str,
        filters: RetrievalFilters | None,
        top_k: int,
    ) -> list[SearchResult]:
        """Busca vectores similares."""
        ...


class IKeywordSearcher(Protocol):
    """Protocolo para búsqueda por keywords."""
    
    async def search(
        self,
        query_text: str,
        collection: str,
        filters: RetrievalFilters | None,
        top_k: int,
    ) -> list[SearchResult]:
        """Busca por keywords."""
        ...


class BM25Searcher:
    """Buscador BM25."""
    
    def __init__(self):
        self._index: dict[str, dict] = {}  # collection -> inverted index
    
    def index_document(self, doc_id: str, content: str, collection: str):
        """Indexa documento para BM25."""
        if collection not in self._index:
            self._index[collection] = {"docs": {}, "doc_count": 0, "avg_len": 0}
        
        # Tokenize
        tokens = self._tokenize(content)
        self._index[collection]["docs"][doc_id] = tokens
        self._index[collection]["doc_count"] += 1
        
        # Update average length
        total_len = sum(len(self._index[collection]["docs"][d]) 
                       for d in self._index[collection]["docs"])
        self._index[collection]["avg_len"] = total_len / self._index[collection]["doc_count"]
    
    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza texto."""
        import re
        # Simple tokenization
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        return [t for t in tokens if t not in stopwords and len(t) > 2]
    
    async def search(
        self,
        query_text: str,
        collection: str,
        filters: RetrievalFilters | None,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Busca usando BM25."""
        if collection not in self._index:
            return []
        
        tokens = self._tokenize(query_text)
        index_data = self._index[collection]
        
        scores = {}
        N = index_data["doc_count"]
        avg_len = index_data["avg_len"]
        
        for doc_id, doc_tokens in index_data["docs"].items():
            score = self._bm25_score(tokens, doc_tokens, N, avg_len)
            if score > 0:
                scores[doc_id] = score
        
        # Sort and return top k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:top_k]:
            results.append(SearchResult(
                result_id=doc_id,
                score=float(score),
                payload={},
            ))
        
        return results
    
    def _bm25_score(
        self,
        query_tokens: list[str],
        doc_tokens: list[str],
        N: int,
        avg_len: float,
    ) -> float:
        """Calcula score BM25."""
        k1 = 1.5
        b = 0.75
        
        doc_len = len(doc_tokens)
        doc_tf = {}
        for token in doc_tokens:
            doc_tf[token] = doc_tf.get(token, 0) + 1
        
        score = 0.0
        for token in query_tokens:
            if token in doc_tf:
                tf = doc_tf[token]
                # Simplified IDF (assuming uniform distribution)
                idf = math.log((N + 1) / 2)
                
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / avg_len))
                
                score += idf * (numerator / denominator)
        
        return score


class HybridRetrievalEngine:
    """Motor de retrieval híbrido."""
    
    def __init__(
        self,
        vector_searcher: IVectorSearcher | None = None,
        keyword_searcher: IKeywordSearcher | None = None,
        config: HybridSearchConfig | None = None,
    ):
        self.vector_searcher = vector_searcher
        self.keyword_searcher = keyword_searcher or BM25Searcher()
        self.config = config or HybridSearchConfig()
    
    async def retrieve(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None = None,
    ) -> RetrievalResult:
        """Realiza retrieval híbrido."""
        import time
        import uuid
        
        query_id = query.query_id or str(uuid.uuid4())
        start = time.time()
        
        # Determine strategy
        strategy = self.config.strategy
        
        if strategy == RetrievalStrategy.VECTOR_ONLY:
            results = await self._vector_only(query, collection, filters)
        elif strategy == RetrievalStrategy.KEYWORD_ONLY:
            results = await self._keyword_only(query, collection, filters)
        elif strategy == RetrievalStrategy.RRF:
            results = await self._rrf_fusion(query, collection, filters)
        elif strategy == RetrievalStrategy.WEIGHTED:
            results = await self._weighted_fusion(query, collection, filters)
        else:  # HYBRID
            results = await self._hybrid_search(query, collection, filters)
        
        total_time_ms = int((time.time() - start) * 1000)
        
        return RetrievalResult(
            query_id=query_id,
            results=[r.result for r in results],
            total_found=len(results),
            retrieval_time_ms=total_time_ms,
            metadata={
                "strategy": strategy.value,
                "vector_weight": self.config.vector_weight,
                "keyword_weight": self.config.keyword_weight,
            },
        )
    
    async def _vector_only(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None,
    ) -> list[ScoredResult]:
        """Búsqueda solo vectorial."""
        if not self.vector_searcher:
            return []
        
        # Generate embedding for query
        # Placeholder - would use embedding engine
        query_vector = EmbeddingVector(values=[0.0] * 768, model="", dimension=768)
        
        results = await self.vector_searcher.search(
            query_vector,
            collection,
            filters,
            self.config.vector_params.top_k,
        )
        
        return [ScoredResult(
            result=r,
            vector_score=r.score,
            combined_score=r.score,
            source="vector",
        ) for r in results]
    
    async def _keyword_only(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None,
    ) -> list[ScoredResult]:
        """Búsqueda solo por keywords."""
        results = await self.keyword_searcher.search(
            query.text,
            collection,
            filters,
            self.config.keyword_params.top_k,
        )
        
        return [ScoredResult(
            result=r,
            keyword_score=r.score,
            combined_score=r.score,
            source="keyword",
        ) for r in results]
    
    async def _hybrid_search(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None,
    ) -> list[ScoredResult]:
        """Búsqueda híbrida simple."""
        import time
        
        # Run both searches in parallel
        vector_start = time.time()
        vector_results = await self._vector_only(query, collection, filters)
        vector_time_ms = int((time.time() - vector_start) * 1000)
        
        keyword_start = time.time()
        keyword_results = await self._keyword_only(query, collection, filters)
        keyword_time_ms = int((time.time() - keyword_start) * 1000)
        
        # Merge results
        merged = self._merge_results(
            vector_results,
            keyword_results,
            self.config.vector_weight,
            self.config.keyword_weight,
        )
        
        return merged[:query.top_k]
    
    async def _rrf_fusion(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None,
    ) -> list[ScoredResult]:
        """Fusión RRF (Reciprocal Rank Fusion)."""
        vector_results = await self._vector_only(query, collection, filters)
        keyword_results = await self._keyword_only(query, collection, filters)
        
        # RRF scoring
        scores: dict[str, ScoredResult] = {}
        k = self.config.rrf_k
        
        for rank, sr in enumerate(vector_results):
            rrf_score = 1 / (k + rank + 1)
            sr.combined_score = self.config.vector_weight * rrf_score
            scores[sr.result.result_id] = sr
        
        for rank, sr in enumerate(keyword_results):
            rrf_score = 1 / (k + rank + 1)
            if sr.result.result_id in scores:
                scores[sr.result.result_id].keyword_score = sr.result.score
                scores[sr.result.result_id].combined_score += self.config.keyword_weight * rrf_score
            else:
                sr.combined_score = self.config.keyword_weight * rrf_score
                sr.source = "keyword"
                scores[sr.result.result_id] = sr
        
        # Sort by combined score
        sorted_results = sorted(
            scores.values(),
            key=lambda x: x.combined_score,
            reverse=True,
        )
        
        return sorted_results
    
    async def _weighted_fusion(
        self,
        query: KnowledgeQuery,
        collection: str,
        filters: RetrievalFilters | None,
    ) -> list[ScoredResult]:
        """Fusión ponderada."""
        vector_results = await self._vector_only(query, collection, filters)
        keyword_results = await self._keyword_only(query, collection, filters)
        
        # Normalize scores and combine
        merged = self._merge_results(
            vector_results,
            keyword_results,
            self.config.vector_weight,
            self.config.keyword_weight,
        )
        
        return merged
    
    def _merge_results(
        self,
        vector_results: list[ScoredResult],
        keyword_results: list[ScoredResult],
        vector_weight: float,
        keyword_weight: float,
    ) -> list[ScoredResult]:
        """Combina resultados de ambas búsquedas."""
        # Normalize scores
        max_vector = max((r.vector_score for r in vector_results), default=1.0)
        max_keyword = max((r.keyword_score for r in keyword_results), default=1.0)
        
        merged: dict[str, ScoredResult] = {}
        
        for sr in vector_results:
            norm_score = sr.vector_score / max_vector if max_vector > 0 else 0
            sr.combined_score = vector_weight * norm_score
            sr.source = "vector"
            merged[sr.result.result_id] = sr
        
        for sr in keyword_results:
            norm_score = sr.keyword_score / max_keyword if max_keyword > 0 else 0
            if sr.result.result_id in merged:
                merged[sr.result.result_id].keyword_score = sr.keyword_score
                merged[sr.result.result_id].combined_score += keyword_weight * norm_score
            else:
                sr.combined_score = keyword_weight * norm_score
                sr.source = "keyword"
                merged[sr.result.result_id] = sr
        
        return sorted(merged.values(), key=lambda x: x.combined_score, reverse=True)


class QueryExpander:
    """Expande queries para mejor retrieval."""
    
    def __init__(self):
        self._synonyms: dict[str, list[str]] = {
            "ecg": ["electrocardiogram", "EKG"],
            "ct": ["computed tomography"],
            "mri": ["magnetic resonance imaging"],
            "bp": ["blood pressure"],
            "hr": ["heart rate"],
            "mi": ["myocardial infarction"],
            "chf": ["congestive heart failure"],
        }
    
    def expand(self, query_text: str) -> list[str]:
        """Expande query con sinónimos."""
        expanded = [query_text]
        
        words = query_text.lower().split()
        for word in words:
            if word in self._synonyms:
                for synonym in self._synonyms[word]:
                    expanded.append(query_text.lower().replace(word, synonym))
        
        return expanded


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Search
from core.PHASE_4.epic5_hybrid_retrieval.search import (
    SearchParams,
    ScoredResult,
    SearchResponse,
    BaseSearcher,
    VectorSearcher,
    KeywordSearcher,
    SemanticSearcher,
)

# BM25
from core.PHASE_4.epic5_hybrid_retrieval.bm25 import (
    BaseBM25,
    BM25Classic,
    BM25L,
    BM25Plus,
    BM25Searcher,
)

# Fusion
from core.PHASE_4.epic5_hybrid_retrieval.fusion import (
    FusionResult,
    BaseFusionMethod,
    ReciprocalRankFusion,
    WeightedAverageFusion,
    CombSUMFusion,
    CombMNZFusion,
    ScoreNormalizer,
    HybridRanker,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    # Enums
    "RetrievalStrategy",
    "BM25Variant",
    # Data Classes
    "RetrievalFilters",
    "VectorSearchParams",
    "KeywordSearchParams",
    "HybridSearchConfig",
    "ScoredResult",
    "FusionResult",
    # Protocols
    "IVectorSearcher",
    "IKeywordSearcher",
    # Implementations
    "BM25Searcher",
    "HybridRetrievalEngine",
    "QueryExpander",
    # Search (new)
    "SearchParams",
    "SearchResponse",
    "BaseSearcher",
    "VectorSearcher",
    "KeywordSearcher",
    "SemanticSearcher",
    # BM25 (new)
    "BaseBM25",
    "BM25Classic",
    "BM25L",
    "BM25Plus",
    # Fusion (new)
    "ReciprocalRankFusion",
    "WeightedAverageFusion",
    "CombSUMFusion",
    "CombMNZFusion",
    "ScoreNormalizer",
    "HybridRanker",
]
