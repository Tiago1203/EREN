"""Unit tests for RAG domain chunk entities."""

import pytest

from core.PHASE_2.cognitive.rag.domain.entities import (
    SourceType,
    RetrievedChunk,
    Citation,
    Evidence,
    ChunkStatus,
    ChunkType,
    KnowledgeChunk,
    ChunkSearchResult,
    ChunkSearchResponse,
)


class TestChunkEntities:
    """Tests for chunk entities."""

    def test_source_type_values(self):
        """Test source type enum values."""
        assert SourceType.KNOWLEDGE.value == "knowledge"
        assert SourceType.ENTITY.value == "entity"
        assert SourceType.TOOL.value == "tool"
        assert SourceType.USER.value == "user"

    def test_chunk_status_values(self):
        """Test chunk status enum values."""
        assert ChunkStatus.ACTIVE.value == "active"
        assert ChunkStatus.ARCHIVED.value == "archived"
        assert ChunkStatus.DELETED.value == "deleted"
        assert ChunkStatus.PENDING.value == "pending"

    def test_chunk_type_values(self):
        """Test chunk type enum values."""
        assert ChunkType.TEXT.value == "text"
        assert ChunkType.CODE.value == "code"
        assert ChunkType.TABLE.value == "table"
        assert ChunkType.IMAGE.value == "image"


class TestRetrievedChunk:
    """Tests for RetrievedChunk."""

    def test_chunk_creation(self):
        """Test chunk creation."""
        chunk = RetrievedChunk(
            id="chunk-1",
            content="Test content",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-1",
            relevance_score=0.8,
        )
        
        assert chunk.id == "chunk-1"
        assert chunk.content == "Test content"
        assert chunk.relevance_score == 0.8

    def test_chunk_to_dict(self):
        """Test chunk to_dict conversion."""
        chunk = RetrievedChunk(
            id="chunk-1",
            content="Test content",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-1",
            relevance_score=0.8,
        )
        
        data = chunk.to_dict()
        assert data["id"] == "chunk-1"
        assert data["source_type"] == "knowledge"


class TestCitation:
    """Tests for Citation."""

    def test_citation_creation(self):
        """Test citation creation."""
        citation = Citation(
            id="citation-1",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-123",
            citation_text="Smith et al. (2024)",
        )
        
        assert citation.id == "citation-1"
        assert citation.citation_text == "Smith et al. (2024)"

    def test_citation_with_url(self):
        """Test citation with URL."""
        citation = Citation(
            id="citation-2",
            source_type=SourceType.USER,
            source_id="user-1",
            citation_text="FDA Guidelines",
            citation_url="https://fda.gov/guidelines",
        )
        
        assert citation.citation_url == "https://fda.gov/guidelines"
        assert citation.accessible is True


class TestEvidence:
    """Tests for Evidence."""

    def test_evidence_creation(self):
        """Test evidence creation."""
        chunk = RetrievedChunk(
            id="chunk-1",
            content="Test content",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-1",
            relevance_score=0.8,
        )
        
        citation = Citation(
            id="citation-1",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-1",
            citation_text="Reference",
        )
        
        evidence = Evidence(
            chunks=[chunk],
            citations=[citation],
            total_sources=2,
        )
        
        assert evidence.total_sources == 2
        assert len(evidence.chunks) == 1

    def test_filtered_chunks(self):
        """Test filtering chunks by threshold."""
        chunks = [
            RetrievedChunk(
                id=f"chunk-{i}",
                content=f"Content {i}",
                source_type=SourceType.KNOWLEDGE,
                source_id=f"source-{i}",
                relevance_score=score,
            )
            for i, score in enumerate([0.3, 0.5, 0.7, 0.9])
        ]
        
        evidence = Evidence(
            chunks=chunks,
            citations=[],
            total_sources=4,
            relevance_threshold=0.5,
        )
        
        filtered = evidence.filtered_chunks(0.5)
        # Should include 0.5, 0.7, 0.9 (3 items)
        assert len(filtered) == 3
        assert all(c.relevance_score >= 0.5 for c in filtered)

    def test_add_chunk(self):
        """Test adding chunk to evidence."""
        evidence = Evidence(
            chunks=[],
            citations=[],
            total_sources=0,
        )
        
        chunk = RetrievedChunk(
            id="chunk-1",
            content="Test",
            source_type=SourceType.KNOWLEDGE,
            source_id="source-1",
            relevance_score=0.8,
        )
        
        evidence.add_chunk(chunk)
        
        assert len(evidence.chunks) == 1


class TestKnowledgeChunk:
    """Tests for KnowledgeChunk."""

    def test_knowledge_chunk_creation(self):
        """Test knowledge chunk creation."""
        chunk = KnowledgeChunk(
            chunk_id="kc-1",
            content="Medical device safety guidelines",
            source_type=SourceType.KNOWLEDGE,
            source_id="guidelines-1",
            title="Device Safety Guidelines",
        )
        
        assert chunk.chunk_id == "kc-1"
        assert chunk.title == "Device Safety Guidelines"

    def test_knowledge_chunk_create_factory(self):
        """Test factory method."""
        chunk = KnowledgeChunk.create(
            content="Test content",
            source_type=SourceType.KNOWLEDGE,
            source_id="knowledge-1",
            tenant_id="tenant-1",
        )
        
        assert chunk.chunk_id is not None
        assert chunk.tenant_id == "tenant-1"

    def test_knowledge_chunk_to_dict(self):
        """Test to_dict conversion."""
        chunk = KnowledgeChunk(
            chunk_id="kc-1",
            content="Test",
            source_type=SourceType.KNOWLEDGE,
            source_id="source-1",
            icd_codes=["T82", "T85"],
            snomed_codes=["SNOMED-1"],
            device_categories=["Infusion Pump"],
        )
        
        data = chunk.to_dict()
        assert data["icd_codes"] == ["T82", "T85"]
        assert data["device_categories"] == ["Infusion Pump"]


class TestChunkSearchResult:
    """Tests for ChunkSearchResult."""

    def test_search_result_creation(self):
        """Test search result creation."""
        chunk = KnowledgeChunk(
            chunk_id="kc-1",
            content="Test",
            source_type=SourceType.KNOWLEDGE,
            source_id="source-1",
        )
        
        result = ChunkSearchResult(
            chunk=chunk,
            relevance_score=0.85,
            matched_terms=["test"],
        )
        
        assert result.relevance_score == 0.85
        assert result.rank == 0

    def test_search_result_to_dict(self):
        """Test to_dict conversion."""
        chunk = KnowledgeChunk(
            chunk_id="kc-1",
            content="Test",
            source_type=SourceType.KNOWLEDGE,
            source_id="source-1",
        )
        
        result = ChunkSearchResult(
            chunk=chunk,
            relevance_score=0.85,
            distance=0.15,
            rank=1,
        )
        
        data = result.to_dict()
        assert data["relevance_score"] == 0.85
        assert data["rank"] == 1


class TestChunkSearchResponse:
    """Tests for ChunkSearchResponse."""

    def test_search_response_creation(self):
        """Test search response creation."""
        chunk = KnowledgeChunk(
            chunk_id="kc-1",
            content="Test",
            source_type=SourceType.KNOWLEDGE,
            source_id="source-1",
        )
        
        results = [
            ChunkSearchResult(
                chunk=chunk,
                relevance_score=0.85,
                rank=1,
            )
        ]
        
        response = ChunkSearchResponse(
            query="test query",
            results=results,
            total_found=1,
            search_time_ms=50,
        )
        
        assert response.query == "test query"
        assert response.total_found == 1

    def test_search_response_to_dict(self):
        """Test to_dict conversion."""
        response = ChunkSearchResponse(
            query="test",
            results=[],
            total_found=0,
            search_time_ms=100,
            query_embedding_time_ms=30,
            retrieval_time_ms=70,
        )
        
        data = response.to_dict()
        assert data["search_time_ms"] == 100
        assert data["query_embedding_time_ms"] == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
