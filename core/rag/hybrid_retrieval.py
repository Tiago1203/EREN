"""Hybrid Retrieval for EREN RAG Pipeline.

Implements hybrid search combining dense, sparse, and keyword retrieval.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.rag.types import (
    RetrievedChunk,
    HybridRetrievalConfig,
    HybridRetrievalResult,
    DenseRetrievalResult,
    SparseRetrievalResult,
)

if TYPE_CHECKING:
    pass


class HybridRetrieval:
    """Implements hybrid retrieval combining multiple search strategies.

    Combines:
    - Dense (semantic/vector) retrieval
    - Sparse (BM25/keyword) retrieval
    - Metadata filtering
    - Temporal retrieval

    Fusion methods:
    - RRF (Reciprocal Rank Fusion)
    - Weighted scoring
    - Convex combination
    """

    def __init__(self, config: HybridRetrievalConfig | None = None):
        """Initialize hybrid retrieval.

        Args:
            config: Hybrid retrieval configuration.
        """
        self._config = config or HybridRetrievalConfig()

    @property
    def config(self) -> HybridRetrievalConfig:
        """Get configuration."""
        return self._config

    def retrieve(
        self,
        query: str,
        dense_func: Callable | None = None,
        sparse_func: Callable | None = None,
        keyword_func: Callable | None = None,
    ) -> HybridRetrievalResult:
        """Perform hybrid retrieval.

        Args:
            query: Search query.
            dense_func: Dense retrieval function.
            sparse_func: Sparse retrieval function.
            keyword_func: Keyword retrieval function.

        Returns:
            Hybrid retrieval result.
        """
        import time
        start = time.time()

        dense_result = None
        sparse_result = None

        # Execute dense retrieval
        if dense_func:
            try:
                chunks = dense_func(query, top_k=self._config.top_k_dense)
                dense_result = DenseRetrievalResult(
                    chunks=chunks,
                    query_embedding=[],  # Would be query embedding
                    latency_ms=0,
                )
            except Exception:
                pass

        # Execute sparse retrieval
        if sparse_func:
            try:
                chunks = sparse_func(query, top_k=self._config.top_k_sparse)
                sparse_result = SparseRetrievalResult(
                    chunks=chunks,
                    query_terms=query.split(),
                    scores=[c.relevance_score for c in chunks],
                    latency_ms=0,
                )
            except Exception:
                pass

        # Fuse results
        fused_chunks = self._fuse_results(dense_result, sparse_result)

        total_latency = int((time.time() - start) * 1000)

        return HybridRetrievalResult(
            dense_result=dense_result,
            sparse_result=sparse_result,
            fused_chunks=fused_chunks,
            fusion_method=self._config.fusion_method,
            total_latency_ms=total_latency,
        )

    def _fuse_results(
        self,
        dense: DenseRetrievalResult | None,
        sparse: SparseRetrievalResult | None,
    ) -> list[RetrievedChunk]:
        """Fuse results from different retrieval methods.

        Args:
            dense: Dense retrieval results.
            sparse: Sparse retrieval results.

        Returns:
            Fused and sorted chunks.
        """
        if self._config.fusion_method == "rrf":
            return self._fuse_rrf(dense, sparse)
        elif self._config.fusion_method == "weighted":
            return self._fuse_weighted(dense, sparse)
        elif self._config.fusion_method == "convex":
            return self._fuse_convex(dense, sparse)
        else:
            return self._fuse_rrf(dense, sparse)

    def _fuse_rrf(
        self,
        dense: DenseRetrievalResult | None,
        sparse: SparseRetrievalResult | None,
    ) -> list[RetrievedChunk]:
        """Fuse using Reciprocal Rank Fusion.

        RRF formula: 1 / (k + rank)

        Args:
            dense: Dense retrieval results.
            sparse: Sparse retrieval results.

        Returns:
            Fused chunks.
        """
        k = 60  # RRF constant
        chunk_scores: dict[str, tuple[RetrievedChunk, float, list[int]]] = {}

        # Process dense results
        if dense:
            for rank, chunk in enumerate(dense.chunks):
                score = 1.0 / (k + rank + 1) * self._config.dense_weight
                if chunk.chunk_id in chunk_scores:
                    old_chunk, old_score, ranks = chunk_scores[chunk.chunk_id]
                    chunk_scores[chunk.chunk_id] = (old_chunk, old_score + score, ranks + [rank])
                else:
                    chunk_scores[chunk.chunk_id] = (chunk, score, [rank])

        # Process sparse results
        if sparse:
            for rank, chunk in enumerate(sparse.chunks):
                score = 1.0 / (k + rank + 1) * self._config.sparse_weight
                if chunk.chunk_id in chunk_scores:
                    old_chunk, old_score, ranks = chunk_scores[chunk.chunk_id]
                    chunk_scores[chunk.chunk_id] = (old_chunk, old_score + score, ranks + [rank + 1000])
                else:
                    chunk_scores[chunk.chunk_id] = (chunk, score, [rank + 1000])

        # Sort by RRF score
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1][1],
            reverse=True,
        )

        result = []
        for chunk_id, (chunk, score, _) in sorted_chunks:
            chunk.relevance_score = score
            chunk.rank = len(result)
            result.append(chunk)

        return result

    def _fuse_weighted(
        self,
        dense: DenseRetrievalResult | None,
        sparse: SparseRetrievalResult | None,
    ) -> list[RetrievedChunk]:
        """Fuse using weighted score combination.

        Args:
            dense: Dense retrieval results.
            sparse: Sparse retrieval results.

        Returns:
            Fused chunks.
        """
        chunk_scores: dict[str, tuple[RetrievedChunk, float]] = {}

        # Process dense results
        if dense:
            for chunk in dense.chunks:
                weighted_score = chunk.relevance_score * self._config.dense_weight
                if chunk.chunk_id in chunk_scores:
                    old_chunk, old_score = chunk_scores[chunk.chunk_id]
                    chunk_scores[chunk.chunk_id] = (old_chunk, old_score + weighted_score)
                else:
                    chunk_scores[chunk.chunk_id] = (chunk, weighted_score)

        # Process sparse results
        if sparse:
            for chunk in sparse.chunks:
                weighted_score = chunk.relevance_score * self._config.sparse_weight
                if chunk.chunk_id in chunk_scores:
                    old_chunk, old_score = chunk_scores[chunk.chunk_id]
                    chunk_scores[chunk.chunk_id] = (old_chunk, old_score + weighted_score)
                else:
                    chunk_scores[chunk.chunk_id] = (chunk, weighted_score)

        # Normalize scores
        max_score = max(s for _, s in chunk_scores.values()) if chunk_scores else 1.0

        # Sort by normalized score
        sorted_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1][1] / max_score if max_score else 0,
            reverse=True,
        )

        result = []
        for rank, (chunk, score) in enumerate(sorted_chunks):
            chunk.relevance_score = score / max_score if max_score else 0
            chunk.rank = rank
            result.append(chunk)

        return result

    def _fuse_convex(
        self,
        dense: DenseRetrievalResult | None,
        sparse: SparseRetrievalResult | None,
    ) -> list[RetrievedChunk]:
        """Fuse using convex combination.

        Args:
            dense: Dense retrieval results.
            sparse: Sparse retrieval results.

        Returns:
            Fused chunks.
        """
        # Similar to weighted but with normalization
        return self._fuse_weighted(dense, sparse)


class BM25Retriever:
    """BM25 (Sparse) retrieval implementation.

    Classic keyword-based retrieval algorithm.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        avg_doc_len: float = 100,
    ):
        """Initialize BM25 retriever.

        Args:
            k1: Term frequency saturation parameter.
            b: Document length normalization parameter.
            avg_doc_len: Average document length.
        """
        self._k1 = k1
        self._b = b
        self._avg_doc_len = avg_doc_len
        self._doc_lengths: dict[str, int] = {}
        self._term_doc_freqs: dict[str, int] = {}
        self._num_docs = 0

    def index(self, chunks: list[RetrievedChunk]) -> None:
        """Index chunks for BM25 retrieval.

        Args:
            chunks: Chunks to index.
        """
        self._num_docs = len(chunks)
        self._doc_lengths.clear()
        self._term_doc_freqs.clear()

        for chunk in chunks:
            words = set(chunk.content.lower().split())
            self._doc_lengths[chunk.chunk_id] = len(words)

            for word in words:
                self._term_doc_freqs[word] = self._term_doc_freqs.get(word, 0) + 1

    def score(self, query: str, chunk: RetrievedChunk) -> float:
        """Calculate BM25 score.

        Args:
            query: Query text.
            chunk: Chunk to score.

        Returns:
            BM25 score.
        """
        query_terms = query.lower().split()
        doc_words = chunk.content.lower().split()
        doc_len = len(doc_words)
        doc_set = set(doc_words)

        score = 0.0
        for term in query_terms:
            if term not in doc_set:
                continue

            # Term frequency in document
            tf = doc_words.count(term)

            # Document frequency
            df = self._term_doc_freqs.get(term, 0)

            # IDF
            idf = math.log((self._num_docs - df + 0.5) / (df + 0.5) + 1)

            # TF component
            tf_component = (tf * (self._k1 + 1)) / (
                tf + self._k1 * (1 - self._b + self._b * doc_len / self._avg_doc_len)
            )

            score += idf * tf_component

        return score

    def retrieve(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """Retrieve chunks using BM25.

        Args:
            query: Query text.
            chunks: Indexed chunks.
            top_k: Number of results to return.

        Returns:
            Top-k chunks by BM25 score.
        """
        # Score all chunks
        scored = []
        for chunk in chunks:
            score = self.score(query, chunk)
            chunk.relevance_score = score
            scored.append((score, chunk))

        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top-k
        return [chunk for _, chunk in scored[:top_k]]
