"""Reranker for EREN RAG Pipeline.

Implements various reranking strategies for retrieved chunks.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.rag.types import (
    RetrievedChunk,
    RerankStrategy,
    RerankingConfig,
    RerankingResult,
    RerankedChunk,
)

if TYPE_CHECKING:
    pass


class Reranker:
    """Reranks retrieved chunks using various strategies.

    Strategies:
    - CROSS_ENCODER: Use a cross-encoder model for reranking
    - DIVERSITY: Maximize diversity among results
    - MMR: Maximal Marginal Relevance for relevance-diversity tradeoff
    - RRF: Reciprocal Rank Fusion for combining multiple rankers
    - WEIGHTED: Simple weighted scoring
    """

    def __init__(self, config: RerankingConfig | None = None):
        """Initialize reranker.

        Args:
            config: Reranking configuration.
        """
        self._config = config or RerankingConfig()

    @property
    def config(self) -> RerankingConfig:
        """Get reranking configuration."""
        return self._config

    def rerank(
        self,
        chunks: list[RetrievedChunk],
        query: str,
        scores: list[float] | None = None,
    ) -> RerankingResult:
        """Rerank chunks.

        Args:
            chunks: Chunks to rerank.
            query: Original query.
            scores: Optional initial relevance scores.

        Returns:
            Reranking result.
        """
        if not chunks:
            return RerankingResult(
                original_chunks=chunks,
                reranked_chunks=[],
                strategy=self._config.strategy,
            )

        scores = scores or [c.relevance_score for c in chunks]

        if self._config.strategy == RerankStrategy.CROSS_ENCODER:
            return self._rerank_cross_encoder(chunks, query, scores)
        elif self._config.strategy == RerankStrategy.DIVERSITY:
            return self._rerank_diversity(chunks, scores)
        elif self._config.strategy == RerankStrategy.MMR:
            return self._rerank_mmr(chunks, query, scores)
        elif self._config.strategy == RerankStrategy.RRF:
            return self._rerank_rrf(chunks, scores)
        elif self._config.strategy == RerankStrategy.WEIGHTED:
            return self._rerank_weighted(chunks, scores)
        else:
            return self._rerank_weighted(chunks, scores)

    def _rerank_cross_encoder(
        self,
        chunks: list[RetrievedChunk],
        query: str,
        scores: list[float],
    ) -> RerankingResult:
        """Rerank using cross-encoder model.

        Args:
            chunks: Chunks to rerank.
            query: Query text.
            scores: Initial scores.

        Returns:
            Reranking result.
        """
        # For now, use initial scores as cross-encoder scores
        # In production, this would call an actual cross-encoder
        reranked = []
        for i, (chunk, score) in enumerate(zip(chunks, scores)):
            reranked.append(
                RerankedChunk(
                    chunk=chunk,
                    original_rank=i,
                    new_rank=i,
                    rerank_score=score,
                    final_score=score,
                )
            )

        # Sort by rerank score
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)

        # Update ranks
        for rank, item in enumerate(reranked):
            item.new_rank = rank

        return RerankingResult(
            original_chunks=chunks,
            reranked_chunks=reranked,
            strategy=RerankStrategy.CROSS_ENCODER,
        )

    def _rerank_diversity(
        self,
        chunks: list[RetrievedChunk],
        scores: list[float],
    ) -> RerankingResult:
        """Rerank to maximize diversity.

        Args:
            chunks: Chunks to rerank.
            scores: Initial scores.

        Returns:
            Reranking result.
        """
        reranked = []
        selected = []
        remaining = list(zip(chunks, scores, range(len(chunks))))

        while remaining and len(selected) < self._config.top_k:
            # Pick highest scoring item
            remaining.sort(key=lambda x: x[1], reverse=True)

            chunk, score, orig_rank = remaining.pop(0)

            # Check diversity against selected
            is_diverse = all(
                self._calculate_diversity(chunk, s_chunk) > 0.3
                for s_chunk in selected
            )

            if is_diverse or len(selected) < 3:  # Always include top 3
                selected.append(chunk)
                reranked.append(
                    RerankedChunk(
                        chunk=chunk,
                        original_rank=orig_rank,
                        new_rank=len(reranked),
                        rerank_score=score,
                        diversity_score=1.0 if is_diverse else 0.5,
                        final_score=score,
                    )
                )

        # Add remaining by score
        for chunk, score, orig_rank in remaining[:self._config.top_k - len(reranked)]:
            reranked.append(
                RerankedChunk(
                    chunk=chunk,
                    original_rank=orig_rank,
                    new_rank=len(reranked),
                    rerank_score=score,
                    final_score=score,
                )
            )

        return RerankingResult(
            original_chunks=chunks,
            reranked_chunks=reranked,
            strategy=RerankStrategy.DIVERSITY,
        )

    def _rerank_mmr(
        self,
        chunks: list[RetrievedChunk],
        query: str,
        scores: list[float],
    ) -> RerankingResult:
        """Rerank using Maximal Marginal Relevance.

        Args:
            chunks: Chunks to rerank.
            query: Query text.
            scores: Initial scores.

        Returns:
            Reranking result.
        """
        reranked = []
        remaining = list(zip(chunks, scores, range(len(chunks))))
        lambda_param = self._config.diversity_lambda

        while remaining and len(reranked) < self._config.top_k:
            # Sort by combined MMR score
            mmr_scores = []
            for chunk, score, orig_rank in remaining:
                relevance = score

                # Calculate diversity penalty
                diversity = max(
                    self._calculate_similarity(chunk, s_chunk)
                    for s_chunk in reranked
                ) if reranked else 0

                # MMR formula
                mmr = lambda_param * relevance - (1 - lambda_param) * diversity
                mmr_scores.append((mmr, relevance, chunk, orig_rank))

            mmr_scores.sort(key=lambda x: x[0], reverse=True)

            _, relevance, chunk, orig_rank = mmr_scores[0]
            remaining = [r for r in remaining if r[0] != chunk]

            reranked.append(
                RerankedChunk(
                    chunk=chunk,
                    original_rank=orig_rank,
                    new_rank=len(reranked),
                    rerank_score=relevance,
                    diversity_score=1 - diversity if remaining else 1.0,
                    final_score=mmr_scores[0][0],
                )
            )

        return RerankingResult(
            original_chunks=chunks,
            reranked_chunks=reranked,
            strategy=RerankStrategy.MMR,
        )

    def _rerank_rrf(
        self,
        chunks: list[RetrievedChunk],
        scores: list[float],
        rank_lists: list[list[int]] | None = None,
    ) -> RerankingResult:
        """Rerank using Reciprocal Rank Fusion.

        Args:
            chunks: Chunks to rerank.
            scores: Initial scores.
            rank_lists: Optional list of rank lists.

        Returns:
            Reranking result.
        """
        k = 60  # RRF constant

        # Calculate RRF scores
        rrf_scores = {}
        for i, chunk in enumerate(chunks):
            # Rank by score
            rrf_scores[chunk.chunk_id] = 1.0 / (k + i + 1)

        # Sort by RRF score
        sorted_chunks = sorted(
            zip(chunks, scores),
            key=lambda x: rrf_scores.get(x[0].chunk_id, 0),
            reverse=True,
        )

        reranked = []
        for rank, (chunk, score) in enumerate(sorted_chunks):
            reranked.append(
                RerankedChunk(
                    chunk=chunk,
                    original_rank=chunks.index(chunk),
                    new_rank=rank,
                    rerank_score=rrf_scores.get(chunk.chunk_id, 0),
                    final_score=rrf_scores.get(chunk.chunk_id, 0),
                )
            )

        return RerankingResult(
            original_chunks=chunks,
            reranked_chunks=reranked,
            strategy=RerankStrategy.RRF,
        )

    def _rerank_weighted(
        self,
        chunks: list[RetrievedChunk],
        scores: list[float],
    ) -> RerankingResult:
        """Rerank using simple weighted scoring.

        Args:
            chunks: Chunks to rerank.
            scores: Scores to use.

        Returns:
            Reranking result.
        """
        # Sort by score descending
        sorted_chunks = sorted(
            zip(chunks, scores, range(len(chunks))),
            key=lambda x: x[1],
            reverse=True,
        )

        reranked = []
        for rank, (chunk, score, orig_rank) in enumerate(sorted_chunks[:self._config.top_k]):
            reranked.append(
                RerankedChunk(
                    chunk=chunk,
                    original_rank=orig_rank,
                    new_rank=rank,
                    rerank_score=score,
                    final_score=score,
                )
            )

        return RerankingResult(
            original_chunks=chunks,
            reranked_chunks=reranked,
            strategy=RerankStrategy.WEIGHTED,
        )

    def _calculate_similarity(self, chunk1: RetrievedChunk, chunk2: RetrievedChunk) -> float:
        """Calculate similarity between two chunks.

        Args:
            chunk1: First chunk.
            chunk2: Second chunk.

        Returns:
            Similarity score (0-1).
        """
        # Simple word overlap similarity
        words1 = set(chunk1.content.lower().split())
        words2 = set(chunk2.content.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _calculate_diversity(self, chunk: RetrievedChunk, selected: list[RetrievedChunk]) -> float:
        """Calculate diversity of chunk against selected chunks.

        Args:
            chunk: Chunk to check.
            selected: Already selected chunks.

        Returns:
            Diversity score (0-1).
        """
        if not selected:
            return 1.0

        avg_similarity = sum(
            self._calculate_similarity(chunk, s)
            for s in selected
        ) / len(selected)

        return 1.0 - avg_similarity
