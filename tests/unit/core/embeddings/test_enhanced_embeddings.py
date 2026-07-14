"""Tests for enhanced embedding platform (PR-057)."""

import pytest
import time
from core.embeddings.enhanced_embeddings import (
    EmbeddingModelType,
    EmbeddingRequest,
    BatchEmbeddingRequest,
    EmbeddingVector,
    EmbeddingCache,
    EmbeddingCacheConfig,
    BatchProcessor,
    BatchProcessingConfig,
    EmbeddingNormalizer,
    EmbeddingVersionManager,
    EmbeddingVersion,
    HybridSearchEngine,
    HybridQuery,
    EmbeddingMetrics,
)


class TestEmbeddingCache:
    """Tests for EmbeddingCache."""

    def test_set_and_get(self):
        """Test set and get."""
        cache = EmbeddingCache()
        vector = EmbeddingVector([0.1, 0.2, 0.3], "test", 3)
        
        cache.set("hello", "model1", vector)
        retrieved = cache.get("hello", "model1")
        
        assert retrieved is not None
        assert retrieved.vector == [0.1, 0.2, 0.3]

    def test_cache_miss(self):
        """Test cache miss."""
        cache = EmbeddingCache()
        result = cache.get("nonexistent", "model1")
        assert result is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = EmbeddingCache(EmbeddingCacheConfig(ttl_seconds=0.1))
        vector = EmbeddingVector([0.1], "test", 1)
        
        cache.set("hello", "model1", vector, ttl=0.05)
        assert cache.get("hello", "model1") is not None
        
        time.sleep(0.1)
        assert cache.get("hello", "model1") is None

    def test_eviction(self):
        """Test LRU eviction."""
        cache = EmbeddingCache(EmbeddingCacheConfig(max_size=2))
        v1 = EmbeddingVector([0.1], "test", 1)
        v2 = EmbeddingVector([0.2], "test", 1)
        v3 = EmbeddingVector([0.3], "test", 1)
        
        cache.set("a", "m", v1)
        cache.set("b", "m", v2)
        cache.set("c", "m", v3)  # Should evict 'a'
        
        assert cache.get("a", "m") is None
        assert cache.get("c", "m") is not None

    def test_clear(self):
        """Test clear."""
        cache = EmbeddingCache()
        vector = EmbeddingVector([0.1], "test", 1)
        cache.set("hello", "model1", vector)
        
        cache.clear()
        assert cache.get("hello", "model1") is None


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    def test_create_batches(self):
        """Test batch creation."""
        processor = BatchProcessor(BatchProcessingConfig(batch_size=3))
        texts = list(range(10))
        
        batches = processor.create_batches(texts)
        
        assert len(batches) == 4
        assert batches[0] == [0, 1, 2]
        assert batches[-1] == [9]

    def test_deduplication(self):
        """Test deduplication."""
        processor = BatchProcessor(BatchProcessingConfig(enable_deduplication=True))
        texts = ["hello", "world", "hello", "test"]
        
        unique, indices = processor.deduplicate(texts)
        
        assert len(unique) == 3
        assert "hello" in unique
        assert "world" in unique
        assert "test" in unique

    def test_no_deduplication(self):
        """Test when deduplication disabled."""
        processor = BatchProcessor(BatchProcessingConfig(enable_deduplication=False))
        texts = ["hello", "hello"]
        
        unique, indices = processor.deduplicate(texts)
        
        assert len(unique) == 2


class TestEmbeddingNormalizer:
    """Tests for EmbeddingNormalizer."""

    def test_l2_normalize(self):
        """Test L2 normalization."""
        vector = [3.0, 4.0]
        normalized = EmbeddingNormalizer.normalize(vector)
        
        magnitude = sum(v * v for v in normalized) ** 0.5
        assert abs(magnitude - 1.0) < 0.0001

    def test_cosine_similarity(self):
        """Test cosine similarity."""
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        
        similarity = EmbeddingNormalizer.cosine_similarity(a, b)
        assert abs(similarity - 1.0) < 0.0001

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors."""
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        
        similarity = EmbeddingNormalizer.cosine_similarity(a, b)
        assert abs(similarity) < 0.0001

    def test_truncate(self):
        """Test truncation."""
        vector = [1.0, 2.0, 3.0, 4.0, 5.0]
        truncated = EmbeddingNormalizer.truncate(vector, 3)
        
        assert len(truncated) == 3
        assert truncated == [1.0, 2.0, 3.0]

    def test_pad(self):
        """Test padding."""
        vector = [1.0, 2.0]
        padded = EmbeddingNormalizer.pad(vector, 5)
        
        assert len(padded) == 5
        assert padded[:2] == [1.0, 2.0]
        assert padded[2:] == [0.0, 0.0, 0.0]


class TestEmbeddingVersionManager:
    """Tests for EmbeddingVersionManager."""

    def test_register_version(self):
        """Test version registration."""
        manager = EmbeddingVersionManager()
        version = EmbeddingVersion("1.0", "model1", 768)
        
        manager.register_version("model1", version)
        retrieved = manager.get_latest_version("model1")
        
        assert retrieved is not None
        assert retrieved.version == "1.0"

    def test_deprecate_version(self):
        """Test version deprecation."""
        manager = EmbeddingVersionManager()
        v1 = EmbeddingVersion("1.0", "model1", 768)
        v2 = EmbeddingVersion("2.0", "model1", 768)
        
        manager.register_version("model1", v1)
        manager.register_version("model1", v2)
        manager.deprecate_version("model1", "1.0")
        
        latest = manager.get_latest_version("model1")
        assert latest.version == "2.0"

    def test_get_all_versions(self):
        """Test getting all versions."""
        manager = EmbeddingVersionManager()
        v1 = EmbeddingVersion("1.0", "model1", 768)
        v2 = EmbeddingVersion("2.0", "model1", 1024)
        
        manager.register_version("model1", v1)
        manager.register_version("model1", v2)
        
        all_versions = manager.get_all_versions("model1")
        assert len(all_versions) == 2


class TestHybridSearchEngine:
    """Tests for HybridSearchEngine."""

    def test_index(self):
        """Test indexing."""
        engine = HybridSearchEngine()
        vector = EmbeddingVector([0.1, 0.2, 0.3], "model1", 3)
        
        engine.index("hello world", vector)
        
        assert "hello world" in engine._dense_index

    def test_search(self):
        """Test hybrid search."""
        engine = HybridSearchEngine()
        vector = EmbeddingVector([0.1, 0.2, 0.3], "model1", 3)
        
        engine.index("machine learning", vector)
        
        query = HybridQuery(
            dense_text="AI",
            sparse_keywords=["machine", "learning"],
            top_k=1,
        )
        
        results = engine.search(query)
        assert len(results) <= 1


class TestEmbeddingMetrics:
    """Tests for EmbeddingMetrics."""

    def test_record_request(self):
        """Test recording request."""
        metrics = EmbeddingMetrics()
        
        metrics.record_request("model1", 100, 50.0, cache_hit=False)
        
        assert metrics.total_requests == 1
        assert metrics.total_tokens == 100
        assert metrics.cache_misses == 1

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation."""
        metrics = EmbeddingMetrics()
        
        metrics.record_request("model1", 100, 50.0, cache_hit=True)
        metrics.record_request("model1", 100, 50.0, cache_hit=False)
        
        assert metrics.cache_hit_rate == 0.5

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metrics = EmbeddingMetrics()
        metrics.record_request("model1", 100, 50.0)
        
        data = metrics.to_dict()
        
        assert "total_requests" in data
        assert "cache_hit_rate" in data
        assert "average_latency_ms" in data
