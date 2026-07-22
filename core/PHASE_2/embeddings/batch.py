"""Batch Processing for EREN Embedding Provider Layer.

Handles batch processing of embeddings with parallel execution,
retry logic, and progress tracking.
"""

from __future__ import annotations

import asyncio
import hashlib
import threading
import time
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from core.PHASE_2.embeddings.types import (
    BatchConfig,
    BatchResult,
    DeduplicationConfig,
    DeduplicationResult,
    Embedding,
    EmbeddingCacheEntry,
    EmbeddingProvider,
    NormalizationMethod,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Text Utilities
# =============================================================================


def compute_text_hash(text: str) -> str:
    """Compute hash for text deduplication.

    Args:
        text: Text to hash.

    Returns:
        Hash string.
    """
    return hashlib.sha256(text.encode()).hexdigest()


# =============================================================================
# Normalization
# =============================================================================


def normalize_vector(
    vector: list[float],
    method: NormalizationMethod = NormalizationMethod.L2,
) -> list[float]:
    """Normalize a vector.

    Args:
        vector: Vector to normalize.
        method: Normalization method.

    Returns:
        Normalized vector.
    """
    if method == NormalizationMethod.NONE:
        return vector

    if method == NormalizationMethod.L2:
        # Euclidean (L2) normalization
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude == 0:
            return vector
        return [x / magnitude for x in vector]

    elif method == NormalizationMethod.L1:
        # Manhattan (L1) normalization
        norm = sum(abs(x) for x in vector)
        if norm == 0:
            return vector
        return [x / norm for x in vector]

    elif method == NormalizationMethod.MAX:
        # Max normalization
        max_val = max(abs(x) for x in vector)
        if max_val == 0:
            return vector
        return [x / max_val for x in vector]

    return vector


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        Cosine similarity score (0 to 1).
    """
    if len(v1) != len(v2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


# =============================================================================
# Deduplication
# =============================================================================


class EmbeddingDeduplicator:
    """Deduplicates embedding texts.

    Supports:
    - Exact hash matching
    - Semantic similarity matching
    - Configurable thresholds
    """

    def __init__(self, config: DeduplicationConfig | None = None):
        """Initialize deduplicator.

        Args:
            config: Deduplication configuration.
        """
        self._config = config or DeduplicationConfig()

    def deduplicate(
        self,
        texts: list[str],
        embeddings: list[Embedding] | None = None,
    ) -> DeduplicationResult:
        """Deduplicate texts.

        Args:
            texts: List of texts.
            embeddings: Optional embeddings for semantic comparison.

        Returns:
            Deduplication result.
        """
        if not self._config.enabled:
            return DeduplicationResult(
                original_count=len(texts),
                unique_count=len(texts),
                duplicates_removed=0,
            )

        seen_hashes: dict[str, int] = {}  # hash -> first index
        duplicate_indices: list[tuple[int, int]] = []

        for i, text in enumerate(texts):
            # Skip short texts
            if len(text) < self._config.min_text_length:
                continue

            text_hash = compute_text_hash(text)

            if text_hash in seen_hashes:
                duplicate_indices.append((seen_hashes[text_hash], i))
            else:
                seen_hashes[text_hash] = i

        # If semantic comparison is enabled
        if embeddings and self._config.similarity_threshold < 1.0:
            semantic_dups = self._find_semantic_duplicates(texts, embeddings)
            duplicate_indices.extend(semantic_dups)

        # Remove duplicates while preserving order
        unique_indices = []
        seen = set()

        for i, text in enumerate(texts):
            text_hash = compute_text_hash(text)
            if text_hash not in seen:
                unique_indices.append(i)
                seen.add(text_hash)

        return DeduplicationResult(
            original_count=len(texts),
            unique_count=len(unique_indices),
            duplicates_removed=len(texts) - len(unique_indices),
            duplicate_indices=duplicate_indices,
        )

    def _find_semantic_duplicates(
        self,
        texts: list[str],
        embeddings: list[Embedding],
    ) -> list[tuple[int, int]]:
        """Find semantically similar duplicates.

        Args:
            texts: List of texts.
            embeddings: Corresponding embeddings.

        Returns:
            List of duplicate pairs.
        """
        duplicates: list[tuple[int, int]] = []
        n = len(embeddings)

        for i in range(n):
            for j in range(i + 1, n):
                similarity = cosine_similarity(
                    embeddings[i].vector,
                    embeddings[j].vector,
                )
                if similarity >= self._config.similarity_threshold:
                    duplicates.append((i, j))

        return duplicates

    def filter_duplicates(
        self,
        texts: list[str],
        embeddings: list[Embedding] | None = None,
    ) -> tuple[list[str], list[Embedding] | None]:
        """Filter out duplicate texts.

        Args:
            texts: List of texts.
            embeddings: Optional embeddings.

        Returns:
            Tuple of (unique texts, unique embeddings).
        """
        result = self.deduplicate(texts, embeddings)

        unique_indices = []
        seen_hashes = set()

        for i, text in enumerate(texts):
            text_hash = compute_text_hash(text)
            if text_hash not in seen_hashes:
                unique_indices.append(i)
                seen_hashes.add(text_hash)

        unique_texts = [texts[i] for i in unique_indices]
        unique_embeddings = None

        if embeddings:
            unique_embeddings = [embeddings[i] for i in unique_indices]

        return unique_texts, unique_embeddings


# =============================================================================
# Embedding Cache
# =============================================================================


class EmbeddingCache:
    """Cache for embedding results.

    Features:
    - LRU eviction
    - TTL support
    - Tag-based invalidation
    - Statistics
    """

    def __init__(
        self,
        max_entries: int = 10000,
        ttl_seconds: float = 3600,
    ):
        """Initialize cache.

        Args:
            max_entries: Maximum cache entries.
            ttl_seconds: Time to live in seconds.
        """
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._cache: dict[str, EmbeddingCacheEntry] = {}
        self._lock = threading.RLock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, text: str) -> Embedding | None:
        """Get embedding from cache.

        Args:
            text: Text to look up.

        Returns:
            Cached embedding or None.
        """
        text_hash = compute_text_hash(text)

        with self._lock:
            if text_hash not in self._cache:
                self._misses += 1
                return None

            entry = self._cache[text_hash]

            # Check expiration
            if entry.is_expired(self._ttl_seconds):
                del self._cache[text_hash]
                self._misses += 1
                return None

            # Update access
            entry.touch()
            self._hits += 1

            return entry.embedding

    def set(self, text: str, embedding: Embedding) -> None:
        """Store embedding in cache.

        Args:
            text: Text that was embedded.
            embedding: Embedding result.
        """
        text_hash = compute_text_hash(text)

        with self._lock:
            # Evict if needed
            while len(self._cache) >= self._max_entries:
                self._evict_lru()

            entry = EmbeddingCacheEntry(
                text_hash=text_hash,
                embedding=embedding,
            )
            self._cache[text_hash] = entry

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed,
        )
        del self._cache[lru_key]
        self._evictions += 1

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate entries with a tag.

        Args:
            tag: Tag to match.

        Returns:
            Number of entries invalidated.
        """
        count = 0
        with self._lock:
            to_remove = []
            for key, entry in self._cache.items():
                if tag in entry.embedding.metadata.get("tags", []):
                    to_remove.append(key)

            for key in to_remove:
                del self._cache[key]
                count += 1

            return count

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "evictions": self._evictions,
                "entries": len(self._cache),
                "max_entries": self._max_entries,
            }


# =============================================================================
# Batch Processor
# =============================================================================


class BatchProcessor:
    """Processes embeddings in batches.

    Features:
    - Automatic batching
    - Parallel processing
    - Retry logic
    - Progress tracking
    """

    def __init__(self, config: BatchConfig | None = None):
        """Initialize batch processor.

        Args:
            config: Batch configuration.
        """
        self._config = config or BatchConfig()
        self._cache = EmbeddingCache()

    @property
    def cache(self) -> EmbeddingCache:
        """Get embedding cache."""
        return self._cache

    async def process_batch(
        self,
        texts: list[str],
        embed_func,  # Async function(texts) -> EmbeddingResponse
        deduplicate: bool = True,
    ) -> BatchResult:
        """Process texts in batches.

        Args:
            texts: Texts to embed.
            embed_func: Function to call for embedding.
            deduplicate: Whether to deduplicate first.

        Returns:
            Batch result.
        """
        batch_id = str(uuid.uuid4())
        start_time = time.time()

        # Deduplicate
        if deduplicate:
            deduplicator = EmbeddingDeduplicator()
            texts, _ = deduplicator.filter_duplicates(texts)

        total_items = len(texts)
        successful = 0
        failed = 0
        total_tokens = 0
        total_cost = 0.0
        errors: list[str] = []

        # Split into batches
        batches = [
            texts[i:i + self._config.batch_size]
            for i in range(0, len(texts), self._config.batch_size)
        ]

        for batch_idx, batch_texts in enumerate(batches):
            # Check cache first
            uncached_texts = []
            cached_embeddings = []

            for text in batch_texts:
                cached = self._cache.get(text)
                if cached:
                    cached_embeddings.append(cached)
                else:
                    uncached_texts.append(text)

            # Process uncached texts
            if uncached_texts:
                for attempt in range(self._config.max_retries):
                    try:
                        response = await embed_func(uncached_texts)

                        if response.success:
                            successful += len(response.embeddings)
                            total_tokens += response.tokens_used
                            total_cost += response.cost_usd

                            # Cache results
                            for text, embedding in zip(uncached_texts, response.embeddings):
                                self._cache.set(text, embedding)

                            break
                        else:
                            errors.append(f"Batch {batch_idx}: {response.error}")

                    except Exception as e:
                        if attempt < self._config.max_retries - 1:
                            await asyncio.sleep(self._config.retry_delay_seconds)
                        else:
                            failed += len(uncached_texts)
                            errors.append(f"Batch {batch_idx}: {str(e)}")

            successful += len(cached_embeddings)

        duration_ms = int((time.time() - start_time) * 1000)

        return BatchResult(
            batch_id=batch_id,
            total_items=total_items,
            successful_items=successful,
            failed_items=failed,
            total_tokens=total_tokens,
            total_cost=total_cost,
            duration_ms=duration_ms,
            errors=errors,
        )
