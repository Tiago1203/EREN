"""Unit tests for PHASE 4 Knowledge Infrastructure."""

import pytest


class TestPHASE4Imports:
    """Tests for PHASE_4 module imports."""

    def test_import_phase4(self):
        """Test PHASE_4 module import."""
        from core.PHASE_4 import __version__, __phase__
        assert __version__ == "1.0.0"
        assert __phase__ == "PHASE_4"

    def test_import_embeddings(self):
        """Test embeddings module import."""
        from core.PHASE_4.embeddings import (
            MedicalEmbeddingModel,
            ChunkingStrategy,
            ClinicalChunker,
            EmbeddingManager,
        )
        assert MedicalEmbeddingModel.PUBMED_BERT.value == "pubmedbert"
        assert ChunkingStrategy.MEDICAL_SECTION.value == "medical_section"

    def test_import_qdrant(self):
        """Test qdrant module import."""
        from core.PHASE_4.qdrant import (
            ClinicalCollection,
            QdrantClient,
            CollectionManager,
            VectorStore,
            HybridSearch,
        )
        assert ClinicalCollection.MEDICAL_LITERATURE.value == "medical_literature"

    def test_import_knowledge(self):
        """Test knowledge module import."""
        from core.PHASE_4.knowledge import (
            KnowledgeSource,
            KnowledgeQuery,
            KnowledgeResult,
            KnowledgeRetriever,
        )
        assert KnowledgeSource.KNOWLEDGE_ARTICLES.value == "knowledge_articles"

    def test_import_rag(self):
        """Test rag module import."""
        from core.PHASE_4.rag import (
            ClinicalQueryType,
            ClinicalRAGQuery,
            ClinicalRAGContext,
            ClinicalRAGPipeline,
            QueryProcessor,
        )
        assert ClinicalQueryType.DIAGNOSIS.value == "diagnosis"

    def test_import_citations(self):
        """Test citations module import."""
        from core.PHASE_4.citations import (
            CitationFormat,
            SourceType,
            Citation,
            CitationBuilder,
            SourceAttributor,
            EvidenceTracer,
        )
        assert CitationFormat.APA.value == "apa"
        assert SourceType.PUBMED.value == "pubmed"


class TestMedicalEmbeddingProvider:
    """Tests for MedicalEmbeddingProvider."""

    def test_embedding_model_values(self):
        """Test medical embedding model values."""
        from core.PHASE_4.embeddings import MedicalEmbeddingModel
        
        assert MedicalEmbeddingModel.PUBMED_BERT.value == "pubmedbert"
        assert MedicalEmbeddingModel.BIOBERT.value == "biobert"
        assert MedicalEmbeddingModel.CLINICAL_BERT.value == "clinical-bert"


class TestClinicalChunker:
    """Tests for ClinicalChunker."""

    def test_chunker_creation(self):
        """Test chunker creation."""
        from core.PHASE_4.embeddings import ClinicalChunker, ChunkingStrategy
        
        chunker = ClinicalChunker(
            strategy=ChunkingStrategy.MEDICAL_SECTION,
            chunk_size=512,
            overlap=50,
        )
        
        assert chunker.strategy == ChunkingStrategy.MEDICAL_SECTION
        assert chunker.chunk_size == 512
        assert chunker.overlap == 50

    def test_chunk_method(self):
        """Test chunk method."""
        from core.PHASE_4.embeddings import ClinicalChunker
        
        chunker = ClinicalChunker()
        chunks = chunker.chunk("Test content")
        
        assert len(chunks) > 0
        assert "content" in chunks[0]


class TestQdrantClient:
    """Tests for QdrantClient."""

    def test_client_creation(self):
        """Test client creation."""
        from core.PHASE_4.qdrant import QdrantClient
        
        client = QdrantClient(
            url="http://localhost:6333",
            api_key="test-key",
        )
        
        assert client.url == "http://localhost:6333"
        assert client.api_key == "test-key"

    @pytest.mark.asyncio
    async def test_search_empty_collection(self):
        """Test search on empty collection."""
        from core.PHASE_4.qdrant import QdrantClient
        
        client = QdrantClient()
        results = await client.search(
            collection="test",
            query_vector=[0.0] * 768,
        )
        
        assert len(results) == 0


class TestKnowledgeQuery:
    """Tests for KnowledgeQuery."""

    def test_query_creation(self):
        """Test query creation."""
        from core.PHASE_4.knowledge import KnowledgeQuery, KnowledgeSource
        
        query = KnowledgeQuery(
            query_text="infusion pump safety",
            sources=[KnowledgeSource.DEVICE_MANUALS],
            medical_specialty="Critical Care",
            max_results=10,
        )
        
        assert query.query_text == "infusion pump safety"
        assert query.medical_specialty == "Critical Care"
        assert query.max_results == 10


class TestQueryProcessor:
    """Tests for QueryProcessor."""

    def test_classify_diagnosis(self):
        """Test diagnosis query classification."""
        from core.PHASE_4.rag import QueryProcessor, ClinicalQueryType
        
        processor = QueryProcessor()
        query_type = processor.classify_query("What is the diagnosis for patient with fever?")
        
        assert query_type == ClinicalQueryType.DIAGNOSIS

    def test_classify_treatment(self):
        """Test treatment query classification."""
        from core.PHASE_4.rag import QueryProcessor, ClinicalQueryType
        
        processor = QueryProcessor()
        query_type = processor.classify_query("What treatment is recommended?")
        
        assert query_type == ClinicalQueryType.TREATMENT

    def test_classify_device_usage(self):
        """Test device usage query classification."""
        from core.PHASE_4.rag import QueryProcessor, ClinicalQueryType
        
        processor = QueryProcessor()
        query_type = processor.classify_query("How to use the infusion pump?")
        
        assert query_type == ClinicalQueryType.DEVICE_USAGE

    def test_classify_general(self):
        """Test general query classification."""
        from core.PHASE_4.rag import QueryProcessor, ClinicalQueryType
        
        processor = QueryProcessor()
        query_type = processor.classify_query("What is EREN?")
        
        assert query_type == ClinicalQueryType.GENERAL


class TestCitationBuilder:
    """Tests for CitationBuilder."""

    def test_builder_creation(self):
        """Test builder creation."""
        from core.PHASE_4.citations import CitationBuilder, CitationFormat
        
        builder = CitationBuilder(format_style=CitationFormat.APA)
        assert builder.format_style == CitationFormat.APA

    def test_format_apa(self):
        """Test APA formatting."""
        from core.PHASE_4.citations import CitationBuilder, Citation
        
        builder = CitationBuilder()
        citation = Citation(
            citation_id="1",
            source_type="pubmed",
            source_id="pubmed-123",
            title="Test Study",
            authors=["Smith J", "Doe J"],
            year="2024",
            doi="10.1234/test",
        )
        
        formatted = builder.format_citation(citation)
        assert "Smith J, Doe J" in formatted
        assert "2024" in formatted


class TestEvidenceTracer:
    """Tests for EvidenceTracer."""

    def test_add_trace(self):
        """Test adding evidence trace."""
        from core.PHASE_4.citations import EvidenceTracer
        
        tracer = EvidenceTracer()
        trace = tracer.add_trace(
            claim="Device X is safe",
            supporting=["citation-1"],
            confidence=0.8,
        )
        
        assert trace.claim == "Device X is safe"
        assert trace.confidence == 0.8
        assert "citation-1" in trace.supporting_evidence

    def test_get_trace(self):
        """Test getting trace by ID."""
        from core.PHASE_4.citations import EvidenceTracer
        
        tracer = EvidenceTracer()
        trace = tracer.add_trace("Test claim")
        
        retrieved = tracer.get_trace(trace.trace_id)
        assert retrieved is not None
        assert retrieved.claim == "Test claim"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
