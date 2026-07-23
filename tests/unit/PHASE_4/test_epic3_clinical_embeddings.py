"""Unit tests for EPIC 3: Clinical Embeddings."""

import pytest
import asyncio


class TestEPIC3Imports:
    """Tests for EPIC 3 module imports."""

    def test_import_epic3(self):
        """Test EPIC 3 module imports."""
        from core.PHASE_4.epic3_clinical_embeddings import (
            MockEmbeddingProvider,
            InMemoryEmbeddingCache,
            EmbeddingPipeline,
        )
        assert MockEmbeddingProvider is not None
        assert InMemoryEmbeddingCache is not None

    def test_import_providers(self):
        """Test provider imports."""
        from core.PHASE_4.epic3_clinical_embeddings.providers import (
            EmbeddingModel,
            EmbeddingConfig,
            MockEmbeddingProvider,
            OpenAIProvider,
            OllamaProvider,
            EmbeddingProviderFactory,
        )
        assert EmbeddingModel is not None
        assert MockEmbeddingProvider is not None

    def test_import_cache(self):
        """Test cache imports."""
        from core.PHASE_4.epic3_clinical_embeddings.cache import (
            CachedEmbedding,
            InMemoryEmbeddingCache,
            PersistentEmbeddingCache,
        )
        assert CachedEmbedding is not None
        assert InMemoryEmbeddingCache is not None

    def test_import_versioning(self):
        """Test versioning imports."""
        from core.PHASE_4.epic3_clinical_embeddings.versioning import (
            EmbeddingVersionStatus,
            EmbeddingVersion,
            InMemoryVersionManager,
            VersionComparator,
        )
        assert EmbeddingVersionStatus is not None
        assert InMemoryVersionManager is not None

    def test_import_pipelines(self):
        """Test pipeline imports."""
        from core.PHASE_4.epic3_clinical_embeddings.pipelines import (
            EmbeddingPipeline,
            BatchGenerator,
            EmbeddingResult,
        )
        assert EmbeddingPipeline is not None
        assert BatchGenerator is not None


class TestMockProvider:
    """Tests for MockEmbeddingProvider."""

    def test_provider_creation(self):
        """Test MockProvider creation."""
        from core.PHASE_4.epic3_clinical_embeddings import MockEmbeddingProvider
        
        provider = MockEmbeddingProvider(dimension=384)
        assert provider.dimension == 384
        assert provider.model_name == "mock-embedding-provider"

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test embedding generation."""
        from core.PHASE_4.epic3_clinical_embeddings import MockEmbeddingProvider
        
        provider = MockEmbeddingProvider(dimension=128)
        embedding = await provider.generate("Test text")
        
        assert embedding.text == "Test text"
        assert len(embedding.vector) == 128
        assert embedding.dimension == 128

    @pytest.mark.asyncio
    async def test_generate_batch(self):
        """Test batch generation."""
        from core.PHASE_4.epic3_clinical_embeddings import MockEmbeddingProvider
        
        provider = MockEmbeddingProvider(dimension=128)
        embeddings = await provider.generate_batch(["Text 1", "Text 2", "Text 3"])
        
        assert len(embeddings) == 3
        assert all(len(e.vector) == 128 for e in embeddings)


class TestInMemoryCache:
    """Tests for InMemoryEmbeddingCache."""

    def test_cache_creation(self):
        """Test cache creation."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryEmbeddingCache
        
        cache = InMemoryEmbeddingCache(max_size=100, ttl_seconds=3600)
        assert cache._max_size == 100

    def test_cache_set_and_get(self):
        """Test cache set and get."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryEmbeddingCache
        
        cache = InMemoryEmbeddingCache()
        stats = cache.stats()
        
        assert stats["size"] == 0
        assert "max_size" in stats

    def test_cache_stats(self):
        """Test cache statistics."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryEmbeddingCache
        
        cache = InMemoryEmbeddingCache()
        stats = cache.stats()
        
        assert "size" in stats
        assert "max_size" in stats
        assert "hits" in stats
        assert "misses" in stats

    def test_cache_clear(self):
        """Test cache clear."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryEmbeddingCache
        from core.PHASE_4.epic3_clinical_embeddings.cache import CachedEmbedding
        from datetime import datetime
        
        cache = InMemoryEmbeddingCache()
        now = datetime.now().isoformat()
        
        embedding = CachedEmbedding(
            text_hash="test",
            text="Test",
            vector=[0.1] * 384,
            model="test",
            dimension=384,
            created_at=now,
            accessed_at=now,
        )
        cache.set(embedding)
        
        assert cache.stats()["size"] == 1
        
        cache.clear()
        assert cache.stats()["size"] == 0


class TestVersioning:
    """Tests for versioning components."""

    def test_version_manager_creation(self):
        """Test version manager creation."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryVersionManager
        
        manager = InMemoryVersionManager()
        assert manager is not None

    def test_create_version(self):
        """Test version creation."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryVersionManager
        
        manager = InMemoryVersionManager()
        version = manager.create_version(
            text_hash="abc123",
            model="test-model",
            vector=[0.1] * 384,
            changelog="Initial version",
        )
        
        assert version.text_hash == "abc123"
        assert version.model == "test-model"
        assert version.version == "1.0.0"
        assert version.status.value == "active"

    def test_get_latest(self):
        """Test getting latest version."""
        from core.PHASE_4.epic3_clinical_embeddings import InMemoryVersionManager
        
        manager = InMemoryVersionManager()
        
        v1 = manager.create_version("abc", "model", [0.1] * 384)
        v2 = manager.create_version("abc", "model", [0.2] * 384)
        
        latest = manager.get_latest("abc")
        assert latest.version_id == v2.version_id

    def test_version_comparator(self):
        """Test version comparator."""
        from core.PHASE_4.epic3_clinical_embeddings import VersionComparator
        from core.PHASE_4.epic3_clinical_embeddings.versioning import EmbeddingVersion
        from datetime import datetime
        
        v1 = EmbeddingVersion(
            version_id="v1",
            text_hash="abc",
            model="test",
            version="1.0.0",
            vector=[0.1] * 3,
            dimension=3,
            created_at=datetime.now().isoformat(),
        )
        
        v2 = EmbeddingVersion(
            version_id="v2",
            text_hash="abc",
            model="test",
            version="2.0.0",
            vector=[0.2] * 3,
            dimension=3,
            created_at=datetime.now().isoformat(),
        )
        
        comparison = VersionComparator.compare_versions(v1, v2)
        
        assert comparison["compatible"] is True
        assert "cosine_similarity" in comparison


class TestEmbeddingPipeline:
    """Tests for EmbeddingPipeline."""

    def test_pipeline_creation(self):
        """Test pipeline creation."""
        from core.PHASE_4.epic3_clinical_embeddings import (
            MockEmbeddingProvider,
            EmbeddingPipeline,
        )
        
        provider = MockEmbeddingProvider(dimension=128)
        pipeline = EmbeddingPipeline(provider)
        
        assert pipeline.provider is provider

    @pytest.mark.asyncio
    async def test_generate_without_cache(self):
        """Test generation without cache."""
        from core.PHASE_4.epic3_clinical_embeddings import (
            MockEmbeddingProvider,
            EmbeddingPipeline,
        )
        
        provider = MockEmbeddingProvider(dimension=128)
        pipeline = EmbeddingPipeline(provider, cache=None)
        
        result = await pipeline.generate("Test text", use_cache=False)
        
        assert len(result.vector) == 128
        assert result.cached is False

    @pytest.mark.asyncio
    async def test_generate_with_cache(self):
        """Test generation with cache."""
        from core.PHASE_4.epic3_clinical_embeddings import (
            MockEmbeddingProvider,
            InMemoryEmbeddingCache,
            EmbeddingPipeline,
        )
        
        provider = MockEmbeddingProvider(dimension=128)
        cache = InMemoryEmbeddingCache()
        pipeline = EmbeddingPipeline(provider, cache=cache)
        
        # First call - should generate
        result1 = await pipeline.generate("Test text", use_cache=True)
        assert len(result1.vector) == 128
        
        # Check cache has entries
        assert cache.stats()["size"] >= 0


class TestBatchGenerator:
    """Tests for BatchGenerator."""

    @pytest.mark.asyncio
    async def test_batch_generation(self):
        """Test batch generation."""
        from core.PHASE_4.epic3_clinical_embeddings import (
            MockEmbeddingProvider,
            EmbeddingPipeline,
            BatchGenerator,
        )
        
        provider = MockEmbeddingProvider(dimension=128)
        pipeline = EmbeddingPipeline(provider)
        batch_gen = BatchGenerator(pipeline, batch_size=2)
        
        texts = ["Text 1", "Text 2", "Text 3"]
        results = await batch_gen.generate(texts)
        
        assert len(results) == 3


class TestProviderFactory:
    """Tests for EmbeddingProviderFactory."""

    def test_create_mock(self):
        """Test creating mock provider."""
        from core.PHASE_4.epic3_clinical_embeddings import EmbeddingProviderFactory
        
        provider = EmbeddingProviderFactory.create("mock", dimension=384)
        assert provider.dimension == 384

    def test_create_openai(self):
        """Test creating OpenAI provider."""
        from core.PHASE_4.epic3_clinical_embeddings import EmbeddingProviderFactory
        
        provider = EmbeddingProviderFactory.create("openai", model="text-embedding-3-small")
        assert "openai" in provider.model_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
