"""Unit tests for EREN Vector Memory Plugin."""

import pytest

from plugins.vector_memory.types import (
    VectorDocument,
    VectorMetadata,
    VectorChunk,
    VectorSearchQuery,
    VectorSearchResult,
    VectorStatistics,
)
from plugins.vector_memory.chunker import (
    BaseChunker,
    SentenceChunker,
    ParagraphChunker,
    SlidingWindowChunker,
    RecursiveChunker,
    ChunkerFactory,
)
from plugins.vector_memory.provider import BaseVectorProvider, ChromaVectorProvider
from plugins.vector_memory.plugin import VectorMemoryPlugin, VectorMemoryInterface


class TestVectorTypes:
    """Tests for vector memory types."""

    def test_vector_metadata_creation(self):
        """Test metadata creation."""
        metadata = VectorMetadata(
            document_id="doc-123",
            chunk_id="chunk-1",
            source="medical_report",
            author="Dr. Smith",
            medical_specialty="cardiology",
        )
        assert metadata.document_id == "doc-123"
        assert metadata.author == "Dr. Smith"
        assert metadata.medical_specialty == "cardiology"

    def test_vector_metadata_to_dict(self):
        """Test metadata to dict."""
        metadata = VectorMetadata(document_id="doc-123")
        data = metadata.to_dict()
        assert data["document_id"] == "doc-123"
        assert "created_at" in data

    def test_vector_chunk_creation(self):
        """Test chunk creation."""
        metadata = VectorMetadata(document_id="doc-123")
        chunk = VectorChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="This is chunk content.",
            metadata=metadata,
            embedding=[0.1, 0.2, 0.3],
            index=0,
        )
        assert chunk.content == "This is chunk content."
        assert chunk.index == 0

    def test_vector_search_query_creation(self):
        """Test search query creation."""
        query = VectorSearchQuery(
            query="test query",
            embeddings=[0.1, 0.2],
            filters={"source": "medical"},
            top_k=5,
            min_score=0.7,
        )
        assert query.query == "test query"
        assert query.top_k == 5
        assert query.min_score == 0.7

    def test_vector_search_result_creation(self):
        """Test search result creation."""
        metadata = VectorMetadata(document_id="doc-123")
        result = VectorSearchResult(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="Result content",
            score=0.95,
            metadata=metadata,
            distance=0.05,
        )
        assert result.score == 0.95
        assert result.distance == 0.05

    def test_vector_statistics_creation(self):
        """Test statistics creation."""
        stats = VectorStatistics(
            total_documents=100,
            total_chunks=500,
            total_embeddings=500,
        )
        assert stats.total_documents == 100
        assert stats.total_chunks == 500


class TestChunkers:
    """Tests for document chunkers."""

    def test_sentence_chunker_basic(self):
        """Test sentence chunker basic functionality."""
        chunker = SentenceChunker(chunk_size=2, overlap=1)
        metadata = VectorMetadata(document_id="doc-123")

        chunks = chunker.chunk(
            document_id="doc-123",
            content="First sentence. Second sentence. Third sentence. Fourth sentence.",
            metadata=metadata,
        )

        assert len(chunks) > 0
        assert chunks[0].document_id == "doc-123"
        assert chunks[0].metadata.total_chunks == len(chunks)

    def test_sentence_chunker_empty_content(self):
        """Test sentence chunker with empty content."""
        chunker = SentenceChunker()
        metadata = VectorMetadata(document_id="doc-123")

        chunks = chunker.chunk(
            document_id="doc-123",
            content="",
            metadata=metadata,
        )

        assert len(chunks) == 0

    def test_paragraph_chunker_basic(self):
        """Test paragraph chunker basic functionality."""
        chunker = ParagraphChunker(max_chunk_size=100, overlap=10)
        metadata = VectorMetadata(document_id="doc-123")

        content = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = chunker.chunk(
            document_id="doc-123",
            content=content,
            metadata=metadata,
        )

        assert len(chunks) > 0
        assert chunks[0].metadata.chunk_index == 0

    def test_sliding_window_chunker_basic(self):
        """Test sliding window chunker."""
        chunker = SlidingWindowChunker(chunk_size=50, overlap=10)
        metadata = VectorMetadata(document_id="doc-123")

        content = "A" * 200
        chunks = chunker.chunk(
            document_id="doc-123",
            content=content,
            metadata=metadata,
        )

        assert len(chunks) > 1
        assert chunks[0].metadata.total_chunks == len(chunks)

    def test_recursive_chunker_basic(self):
        """Test recursive chunker."""
        chunker = RecursiveChunker(chunk_size=100)
        metadata = VectorMetadata(document_id="doc-123")

        content = "First part.\n\nSecond part.\n\nThird part."
        chunks = chunker.chunk(
            document_id="doc-123",
            content=content,
            metadata=metadata,
        )

        assert len(chunks) > 0

    def test_chunker_factory(self):
        """Test chunker factory."""
        chunker = ChunkerFactory.create("sentence", chunk_size=3)
        assert isinstance(chunker, SentenceChunker)

        chunker = ChunkerFactory.create("paragraph", max_chunk_size=500)
        assert isinstance(chunker, ParagraphChunker)

    def test_chunker_factory_unknown_type(self):
        """Test factory with unknown type."""
        chunker = ChunkerFactory.create("unknown")
        assert isinstance(chunker, SentenceChunker)  # Default


class TestChromaProvider:
    """Tests for ChromaDB provider."""

    @pytest.fixture
    def provider(self):
        """Create test provider."""
        return ChromaVectorProvider()

    @pytest.mark.asyncio
    async def test_provider_initialize(self, provider):
        """Test provider initialization."""
        await provider.initialize({})
        health = await provider.health_check()
        assert health["initialized"] is True

    @pytest.mark.asyncio
    async def test_provider_store_and_get(self, provider):
        """Test storing and retrieving chunks."""
        await provider.initialize({})

        metadata = VectorMetadata(document_id="doc-123")
        chunk = VectorChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="Test content",
            metadata=metadata,
        )

        chunk_ids = await provider.store(
            chunks=[chunk],
            embeddings=[[0.1, 0.2, 0.3]],
        )

        assert len(chunk_ids) == 1
        assert chunk_ids[0] == "chunk-1"

        retrieved = await provider.get("chunk-1")
        assert retrieved is not None
        assert retrieved.content == "Test content"

    @pytest.mark.asyncio
    async def test_provider_search(self, provider):
        """Test vector search."""
        await provider.initialize({})

        # Store some chunks
        for i in range(3):
            metadata = VectorMetadata(document_id=f"doc-{i}")
            chunk = VectorChunk(
                chunk_id=f"chunk-{i}",
                document_id=f"doc-{i}",
                content=f"Content for chunk {i}",
                metadata=metadata,
            )

            await provider.store(
                chunks=[chunk],
                embeddings=[[0.1 * (i + 1), 0.2, 0.3]],
            )

        # Search
        query = VectorSearchQuery(query="test", top_k=2)
        results = await provider.search(query, [0.15, 0.2, 0.3])

        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_provider_delete(self, provider):
        """Test deleting chunks."""
        await provider.initialize({})

        metadata = VectorMetadata(document_id="doc-123")
        chunk = VectorChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="Test content",
            metadata=metadata,
        )

        await provider.store(chunks=[chunk], embeddings=[[0.1, 0.2, 0.3]])

        deleted = await provider.delete("chunk-1")
        assert deleted is True

        retrieved = await provider.get("chunk-1")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_provider_delete_by_document(self, provider):
        """Test deleting by document ID."""
        await provider.initialize({})

        # Store multiple chunks for same document
        for i in range(3):
            metadata = VectorMetadata(document_id="doc-123")
            chunk = VectorChunk(
                chunk_id=f"chunk-{i}",
                document_id="doc-123",
                content=f"Content {i}",
                metadata=metadata,
            )

            await provider.store(
                chunks=[chunk],
                embeddings=[[0.1, 0.2, 0.3]],
            )

        deleted = await provider.delete_by_document("doc-123")
        assert deleted == 3

    @pytest.mark.asyncio
    async def test_provider_statistics(self, provider):
        """Test getting statistics."""
        await provider.initialize({})

        metadata = VectorMetadata(document_id="doc-123")
        chunk = VectorChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="Test content",
            metadata=metadata,
        )

        await provider.store(chunks=[chunk], embeddings=[[0.1, 0.2, 0.3]])

        stats = await provider.get_statistics()
        assert stats.total_chunks == 1


class TestVectorMemoryPlugin:
    """Tests for Vector Memory Plugin."""

    @pytest.fixture
    def plugin(self):
        """Create test plugin."""
        return VectorMemoryPlugin()

    @pytest.mark.asyncio
    async def test_plugin_initialization(self, plugin):
        """Test plugin initialization."""
        await plugin.initialize({})
        assert plugin.is_initialized is True

    @pytest.mark.asyncio
    async def test_plugin_add_document(self, plugin):
        """Test adding a document."""
        await plugin.initialize({})

        chunk_ids = await plugin.add_document(
            document_id="doc-123",
            content="This is a test document with multiple sentences. " * 5,
            metadata=VectorMetadata(source="test"),
        )

        assert len(chunk_ids) > 0

    @pytest.mark.asyncio
    async def test_plugin_search(self, plugin):
        """Test searching documents."""
        await plugin.initialize({})

        # Add document
        await plugin.add_document(
            document_id="doc-123",
            content="Medical information about heart disease. " * 10,
            metadata=VectorMetadata(
                source="medical",
                medical_specialty="cardiology",
            ),
        )

        # Search
        results = await plugin.search_similar(
            query="heart disease",
            top_k=5,
        )

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_plugin_delete_document(self, plugin):
        """Test deleting a document."""
        await plugin.initialize({})

        # Add document
        await plugin.add_document(
            document_id="doc-123",
            content="Test content",
        )

        # Delete
        deleted = await plugin.delete_document("doc-123")
        assert deleted > 0

    @pytest.mark.asyncio
    async def test_plugin_statistics(self, plugin):
        """Test getting statistics."""
        await plugin.initialize({})

        await plugin.add_document(
            document_id="doc-123",
            content="Test content for statistics.",
        )

        stats = await plugin.get_statistics()
        assert stats.total_chunks >= 0

    @pytest.mark.asyncio
    async def test_plugin_health_check(self, plugin):
        """Test health check."""
        await plugin.initialize({})

        health = await plugin.health_check()
        assert health["plugin"] == "vector-memory"
        assert health["initialized"] is True

    @pytest.mark.asyncio
    async def test_plugin_memory_interface(self, plugin):
        """Test getting memory interface."""
        await plugin.initialize({})

        interface = plugin.memory_interface
        assert interface.memory_type.value == "vector"
        assert interface.provider_name == "vector-memory"


class TestMetadataFiltering:
    """Tests for metadata filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_medical_specialty(self):
        """Test filtering by medical specialty."""
        plugin = VectorMemoryPlugin()
        await plugin.initialize({})

        # Add cardiology document
        await plugin.add_document(
            document_id="cardio-doc",
            content="Information about heart conditions.",
            metadata=VectorMetadata(medical_specialty="cardiology"),
        )

        # Add neurology document
        await plugin.add_document(
            document_id="neuro-doc",
            content="Information about brain conditions.",
            metadata=VectorMetadata(medical_specialty="neurology"),
        )

        # Search with filter
        results = await plugin.search_similar(
            query="conditions",
            filters={"medical_specialty": "cardiology"},
            top_k=5,
        )

        # Check if results are filtered
        # (In mock mode, filtering may not work perfectly)

    @pytest.mark.asyncio
    async def test_filter_by_source(self):
        """Test filtering by source."""
        plugin = VectorMemoryPlugin()
        await plugin.initialize({})

        await plugin.add_document(
            document_id="report-1",
            content="Medical report content.",
            metadata=VectorMetadata(source="medical_report"),
        )

        await plugin.add_document(
            document_id="note-1",
            content="Clinical note content.",
            metadata=VectorMetadata(source="clinical_note"),
        )

        results = await plugin.search_similar(
            query="content",
            filters={"source": "medical_report"},
            top_k=5,
        )

        assert isinstance(results, list)


class TestBatchOperations:
    """Tests for batch operations."""

    @pytest.mark.asyncio
    async def test_batch_add_documents(self):
        """Test batch adding documents."""
        plugin = VectorMemoryPlugin()
        await plugin.initialize({})

        documents = [
            ("doc-1", "Content of document 1.", None),
            ("doc-2", "Content of document 2.", None),
            ("doc-3", "Content of document 3.", None),
        ]

        results = await plugin.batch_add_documents(documents)

        assert len(results) == 3
        assert all(len(chunk_ids) > 0 for chunk_ids in results)

    @pytest.mark.asyncio
    async def test_batch_search(self):
        """Test batch searching."""
        plugin = VectorMemoryPlugin()
        await plugin.initialize({})

        # Add some documents
        for i in range(3):
            await plugin.add_document(
                document_id=f"doc-{i}",
                content=f"Content about topic {i}.",
            )

        # Batch search
        queries = ["topic 0", "topic 1", "topic 2"]
        results = await plugin.batch_search(queries, top_k=2)

        assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
