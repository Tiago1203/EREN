"""Unit tests for Qdrant service."""

import pytest

from core.PHASE_2.cognitive.rag.domain.entities import (
    SourceType,
    ChunkStatus,
    ChunkType,
    KnowledgeChunk,
)
from core.PHASE_2.cognitive.rag.domain.services.qdrant_service import (
    QdrantConfig,
    ChunkFilter,
    QdrantCollection,
    QdrantServiceFactory,
)
from core.PHASE_2.cognitive.rag.domain.services.memory_qdrant_service import (
    InMemoryQdrantService,
)


class TestQdrantConfig:
    """Tests for QdrantConfig."""

    def test_config_defaults(self):
        """Test config default values."""
        config = QdrantConfig(url="http://localhost:6333")
        
        assert config.url == "http://localhost:6333"
        assert config.default_vector_size == 1536
        assert config.distance_metric == "Cosine"
        assert config.default_top_k == 10

    def test_config_custom(self):
        """Test config with custom values."""
        config = QdrantConfig(
            url="https://qdrant.example.com",
            api_key="secret-key",
            default_vector_size=768,
            distance_metric="Dot",
        )
        
        assert config.url == "https://qdrant.example.com"
        assert config.api_key == "secret-key"
        assert config.default_vector_size == 768


class TestChunkFilter:
    """Tests for ChunkFilter."""

    def test_filter_defaults(self):
        """Test filter default values."""
        filter_params = ChunkFilter()
        
        assert filter_params.tenant_id is None
        # Note: status defaults to ACTIVE in ChunkFilter

    def test_filter_with_values(self):
        """Test filter with values."""
        filter_params = ChunkFilter(
            tenant_id="tenant-1",
            medical_specialty="Cardiology",
            device_categories=["Pacemaker"],
            standards=["ISO-13485"],
        )
        
        assert filter_params.tenant_id == "tenant-1"
        assert filter_params.medical_specialty == "Cardiology"

    def test_filter_to_qdrant(self):
        """Test conversion to Qdrant filter."""
        filter_params = ChunkFilter(
            tenant_id="tenant-1",
            medical_specialty="Radiology",
            status=None,  # Don't include status
        )
        
        qdrant_filter = filter_params.to_qdrant_filter()
        
        assert "must" in qdrant_filter
        # Should have tenant_id and medical_specialty
        assert len(qdrant_filter["must"]) >= 2


class TestQdrantCollection:
    """Tests for QdrantCollection constants."""

    def test_collection_names(self):
        """Test collection name constants."""
        assert QdrantCollection.KNOWLEDGE == "knowledge"
        assert QdrantCollection.DEVICE == "device"
        assert QdrantCollection.CLINICAL == "clinical"
        assert QdrantCollection.STANDARDS == "standards"


class TestQdrantServiceFactory:
    """Tests for QdrantServiceFactory."""

    def test_create_memory_service(self):
        """Test creating in-memory service."""
        service = QdrantServiceFactory.create_memory_service()
        assert isinstance(service, InMemoryQdrantService)


class TestInMemoryQdrantService:
    """Tests for InMemoryQdrantService."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        return InMemoryQdrantService()

    @pytest.fixture
    def sample_chunk(self):
        """Create sample chunk."""
        return KnowledgeChunk.create(
            content="Infusion pump safety guidelines",
            source_type=SourceType.KNOWLEDGE,
            source_id="guidelines-1",
            title="Pump Safety",
            medical_specialty="Critical Care",
            device_categories=["Infusion Pump"],
            standards=["ISO-13485"],
            tags=["safety", "pumps"],
        )

    @pytest.mark.asyncio
    async def test_create_collection(self, service):
        """Test creating a collection."""
        result = await service.create_collection("test", 1536)
        assert result is True
        
        # Should return False if exists
        result = await service.create_collection("test", 1536)
        assert result is False

    @pytest.mark.asyncio
    async def test_collection_exists(self, service):
        """Test checking collection existence."""
        await service.create_collection("test", 1536)
        
        assert await service.collection_exists("test") is True
        assert await service.collection_exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_delete_collection(self, service):
        """Test deleting a collection."""
        await service.create_collection("test", 1536)
        
        result = await service.delete_collection("test")
        assert result is True
        assert await service.collection_exists("test") is False

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, service):
        """Test getting collection stats."""
        await service.create_collection("test", 1536)
        
        stats = await service.get_collection_stats("test")
        
        assert stats.name == "test"
        assert stats.vector_count == 0
        assert stats.vector_dimension == 1536

    @pytest.mark.asyncio
    async def test_upsert_chunk(self, service, sample_chunk):
        """Test inserting a chunk."""
        chunk_id = await service.upsert_chunk(sample_chunk)
        
        assert chunk_id is not None
        assert sample_chunk.chunk_id == chunk_id

    @pytest.mark.asyncio
    async def test_upsert_chunks(self, service):
        """Test batch insert."""
        chunks = [
            KnowledgeChunk.create(
                content=f"Content {i}",
                source_type=SourceType.KNOWLEDGE,
                source_id=f"source-{i}",
            )
            for i in range(3)
        ]
        
        result = await service.upsert_chunks(chunks)
        
        assert result.total == 3
        assert result.successful == 3
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_search_chunks_by_text(self, service, sample_chunk):
        """Test text search."""
        await service.upsert_chunk(sample_chunk)
        
        results = await service.search_chunks_by_text(
            query_text="infusion",
            collection="default",
            top_k=5,
        )
        
        assert results.total_found >= 1
        assert results.results[0].relevance_score > 0

    @pytest.mark.asyncio
    async def test_search_with_filter(self, service, sample_chunk):
        """Test search with filters."""
        await service.upsert_chunk(sample_chunk)
        
        filter_params = ChunkFilter(
            medical_specialty="Critical Care",
        )
        
        results = await service.search_chunks_by_text(
            query_text="infusion",
            collection="default",
            filter_params=filter_params,
        )
        
        assert results.total_found >= 1

    @pytest.mark.asyncio
    async def test_get_chunk(self, service, sample_chunk):
        """Test getting a chunk."""
        chunk_id = await service.upsert_chunk(sample_chunk)
        
        retrieved = await service.get_chunk(chunk_id, "default")
        
        assert retrieved is not None
        assert retrieved.title == "Pump Safety"

    @pytest.mark.asyncio
    async def test_delete_chunk(self, service, sample_chunk):
        """Test deleting a chunk."""
        chunk_id = await service.upsert_chunk(sample_chunk)
        
        result = await service.delete_chunk(chunk_id, "default")
        assert result is True
        
        retrieved = await service.get_chunk(chunk_id, "default")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_chunks(self, service):
        """Test batch delete."""
        chunks = [
            KnowledgeChunk.create(
                content=f"Content {i}",
                source_type=SourceType.KNOWLEDGE,
                source_id=f"source-{i}",
            )
            for i in range(3)
        ]
        
        result = await service.upsert_chunks(chunks)
        chunk_ids = result.chunk_ids
        
        delete_result = await service.delete_chunks(chunk_ids, "default")
        
        assert delete_result.successful == 3

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test health check."""
        health = await service.health_check()
        
        assert health["status"] == "healthy"


class TestChunkFilterConversion:
    """Tests for ChunkFilter to Qdrant conversion."""

    def test_filter_with_values(self):
        """Test filter with values."""
        filter_params = ChunkFilter(
            tenant_id="tenant-1",
            medical_specialty="Cardiology",
            status=None,  # Don't include status
        )
        result = filter_params.to_qdrant_filter()
        
        assert "must" in result
        assert len(result["must"]) >= 2

    def test_source_types_filter(self):
        """Test source types filter."""
        filter_params = ChunkFilter(
            source_types=[SourceType.KNOWLEDGE, SourceType.ENTITY],
            status=None,
        )
        result = filter_params.to_qdrant_filter()
        
        assert "must" in result
        assert len(result["must"]) >= 1

    def test_date_range_filter(self):
        """Test date range filter."""
        filter_params = ChunkFilter(
            date_from="2024-01-01",
            date_to="2024-12-31",
            status=None,
        )
        result = filter_params.to_qdrant_filter()
        
        assert "must" in result
        assert len(result["must"]) >= 2

    def test_multiple_filters(self):
        """Test multiple filters."""
        filter_params = ChunkFilter(
            tenant_id="tenant-1",
            medical_specialty="Cardiology",
            device_categories=["Pacemaker"],
            tags=["critical"],
            status=None,
        )
        result = filter_params.to_qdrant_filter()
        
        assert "must" in result
        # Should have at least 4 filters (tenant_id, medical_specialty, device_categories, tags)
        assert len(result["must"]) >= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
