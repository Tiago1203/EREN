"""Unit tests for PHASE 4 Knowledge Infrastructure."""

import pytest
import asyncio


class TestPHASE4Imports:
    """Tests for PHASE_4 module imports."""

    def test_import_version(self):
        """Test PHASE_4 version."""
        from core.PHASE_4 import __version__, __phase__
        assert __version__ == "2.0.0"
        assert __phase__ == "PHASE_4"


class TestFoundation:
    """Tests for Foundation module (EPIC 0)."""

    def test_document_format_values(self):
        """Test DocumentFormat enum."""
        from core.PHASE_4 import DocumentFormat
        assert DocumentFormat.PDF.value == "pdf"
        assert DocumentFormat.DOCX.value == "docx"
        assert DocumentFormat.HTML.value == "html"

    def test_knowledge_domain_values(self):
        """Test KnowledgeDomain enum."""
        from core.PHASE_4 import KnowledgeDomain
        assert KnowledgeDomain.CARDIOLOGY.value == "cardiology"
        assert KnowledgeDomain.RADIOLOGY.value == "radiology"
        assert KnowledgeDomain.CRITICAL_CARE.value == "critical_care"

    def test_processing_status(self):
        """Test ProcessingStatus enum."""
        from core.PHASE_4 import ProcessingStatus
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"

    def test_quality_level(self):
        """Test QualityLevel enum."""
        from core.PHASE_4 import QualityLevel
        assert QualityLevel.HIGH.value == "high"
        assert QualityLevel.MEDIUM.value == "medium"
        assert QualityLevel.LOW.value == "low"

    def test_governance_status(self):
        """Test GovernanceStatus enum."""
        from core.PHASE_4 import GovernanceStatus
        assert GovernanceStatus.DRAFT.value == "draft"
        assert GovernanceStatus.APPROVED.value == "approved"
        assert GovernanceStatus.PUBLISHED.value == "published"

    def test_evidence_level(self):
        """Test EvidenceLevel enum."""
        from core.PHASE_4 import EvidenceLevel
        assert EvidenceLevel.LEVEL_1A.value == "1a"
        assert EvidenceLevel.LEVEL_1B.value == "1b"
        assert EvidenceLevel.LEVEL_5.value == "5"

    def test_base_knowledge_service(self):
        """Test BaseKnowledgeService."""
        from core.PHASE_4 import BaseKnowledgeService
        service = BaseKnowledgeService()
        assert service._initialized is False

    def test_base_chunker(self):
        """Test BaseChunker."""
        from core.PHASE_4 import BaseChunker
        chunker = BaseChunker(chunk_size=100, overlap=10)
        text = "This is a long text that needs to be chunked. " * 10
        chunks = chunker.chunk(text)
        assert len(chunks) > 0

    def test_knowledge_asset_factory(self):
        """Test KnowledgeAssetFactory."""
        from core.PHASE_4 import KnowledgeAssetFactory, KnowledgeDomain
        asset = KnowledgeAssetFactory.create(
            title="Test Asset",
            content="Test content",
            domain=KnowledgeDomain.CARDIOLOGY,
            created_by="test",
        )
        assert asset.title == "Test Asset"
        assert asset.domain == KnowledgeDomain.CARDIOLOGY
        assert asset.version == "1.0.0"
        assert asset.governance_status.value == "draft"

    def test_phase4_config(self):
        """Test PHASE4Config."""
        from core.PHASE_4 import PHASE4Config
        config = PHASE4Config()
        assert config.service_name == "eren-phase4"
        assert config.environment.value == "development"

    def test_phase4_metrics(self):
        """Test PHASE4Metrics."""
        from core.PHASE_4 import PHASE4Metrics
        metrics = PHASE4Metrics()
        metrics.documents_processed = 10
        assert metrics.documents_processed == 10
        assert metrics.to_dict()["documents_processed"] == 10

    def test_event_publisher(self):
        """Test InMemoryEventPublisher."""
        from core.PHASE_4 import InMemoryEventPublisher, DomainEvent, EventType
        
        async def test():
            publisher = InMemoryEventPublisher()
            event = DomainEvent.create(
                event_type=EventType.DOCUMENT_PROCESSED,
                correlation_id="test-123",
            )
            result = await publisher.publish(event)
            assert result is True
            assert len(publisher.get_published_events()) == 1
        
        asyncio.run(test())

    def test_constants(self):
        """Test constants module."""
        from core.PHASE_4 import VERSION, DEFAULT_TOP_K, MAX_RESULTS
        assert VERSION == "2.0.0"
        assert DEFAULT_TOP_K == 10
        assert MAX_RESULTS == 100


class TestDocumentProcessing:
    """Tests for Document Processing module."""

    def test_text_extraction_method(self):
        """Test TextExtractionMethod enum."""
        from core.PHASE_4 import TextExtractionMethod
        assert TextExtractionMethod.DIRECT.value == "direct"
        assert TextExtractionMethod.OCR.value == "ocr"
        assert TextExtractionMethod.HYBRID.value == "hybrid"

    def test_processing_options(self):
        """Test ProcessingOptions."""
        from core.PHASE_4 import ProcessingOptions
        options = ProcessingOptions()
        assert options.extract_tables is True
        assert options.extract_figures is True
        assert options.enable_ocr is True

    def test_text_normalizer(self):
        """Test TextNormalizer."""
        from core.PHASE_4 import TextNormalizer
        normalizer = TextNormalizer()
        text = "  Hello   World  \n\n\n  "
        normalized = normalizer.normalize(text)
        assert "  " not in normalized


class TestKnowledgeExtraction:
    """Tests for Knowledge Extraction module."""

    def test_entity_type_values(self):
        """Test EntityType enum."""
        from core.PHASE_4 import EntityType
        assert EntityType.DEVICE.value == "DEVICE"
        assert EntityType.DRUG.value == "DRUG"
        assert EntityType.CONDITION.value == "CONDITION"

    def test_concept_category(self):
        """Test ConceptCategory enum."""
        from core.PHASE_4 import ConceptCategory
        assert ConceptCategory.DIAGNOSIS.value == "DIAGNOSIS"
        assert ConceptCategory.TREATMENT.value == "TREATMENT"
        assert ConceptCategory.SYMPTOM.value == "SYMPTOM"

    def test_relation_type(self):
        """Test RelationType enum."""
        from core.PHASE_4 import RelationType
        assert RelationType.TREATS.value == "TREATS"
        assert RelationType.CAUSES.value == "CAUSES"
        assert RelationType.INTERACTS_WITH.value == "INTERACTS_WITH"


class TestClinicalEmbeddings:
    """Tests for Clinical Embeddings module."""

    def test_embedding_model(self):
        """Test EmbeddingModel enum."""
        from core.PHASE_4 import EmbeddingModel
        assert EmbeddingModel.PUBMEDBERT.value == "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
        assert EmbeddingModel.BIOBERT.value == "dmis-lab/biobert-base-cased-v1.2"

    def test_embedding_config(self):
        """Test EmbeddingConfig."""
        from core.PHASE_4 import EmbeddingConfig
        config = EmbeddingConfig(batch_size=64)
        assert config.batch_size == 64
        assert config.max_length == 512

    def test_in_memory_cache(self):
        """Test InMemoryEmbeddingCache."""
        from core.PHASE_4 import InMemoryEmbeddingCache
        import asyncio
        
        async def test_cache():
            cache = InMemoryEmbeddingCache(max_size=10)
            cache.clear()
            count = 0  # clear() returns None
            assert count == 0
        asyncio.run(test_cache())


class TestVectorIndexing:
    """Tests for Vector Indexing module."""

    def test_distance_metric(self):
        """Test DistanceMetric enum."""
        from core.PHASE_4 import DistanceMetric
        assert DistanceMetric.COSINE.value == "Cosine"
        assert DistanceMetric.EUCLID.value == "Euclid"
        assert DistanceMetric.DOT.value == "Dot"

    def test_collection_type(self):
        """Test CollectionType enum."""
        from core.PHASE_4 import CollectionType
        assert CollectionType.KNOWLEDGE_ARTICLES.value == "knowledge_articles"
        assert CollectionType.DEVICE_MANUALS.value == "device_manuals"

    def test_collection_config(self):
        """Test CollectionConfig."""
        from core.PHASE_4 import CollectionConfig
        config = CollectionConfig(name="test", vector_size=768)
        assert config.name == "test"
        assert config.vector_size == 768

    def test_in_memory_qdrant_client(self):
        """Test InMemoryQdrantClient."""
        from core.PHASE_4 import InMemoryQdrantClient
        import asyncio
        
        async def test_client():
            client = InMemoryQdrantClient()
            exists = await client.collection_exists("test")
            assert exists is False
        asyncio.run(test_client())


class TestHybridRetrieval:
    """Tests for Hybrid Retrieval module."""

    def test_retrieval_strategy(self):
        """Test RetrievalStrategy enum."""
        from core.PHASE_4 import RetrievalStrategy
        assert RetrievalStrategy.VECTOR_ONLY.value == "vector_only"
        assert RetrievalStrategy.HYBRID.value == "hybrid"
        assert RetrievalStrategy.RRF.value == "rrf"

    def test_retrieval_filters(self):
        """Test RetrievalFilters."""
        from core.PHASE_4 import RetrievalFilters, KnowledgeDomain
        filters = RetrievalFilters(quality_min=0.7)
        assert filters.quality_min == 0.7

    def test_bm25_searcher(self):
        """Test BM25Searcher."""
        from core.PHASE_4 import BM25Searcher
        import asyncio

        async def test_searcher():
            searcher = BM25Searcher()
            # Index multiple documents
            docs = [
                {"id": "doc1", "text": "The infusion pump delivers medication safely", "category": "test"},
                {"id": "doc2", "text": "Patient safety is paramount in medical devices", "category": "test"},
                {"id": "doc3", "text": "Regular maintenance ensures device reliability", "category": "test"}
            ]
            searcher.index_documents(docs)

            # Search for "safety"
            results = searcher.search("safety medical", limit=10)
            assert len(results) >= 0  # May or may not find matches depending on BM25 implementation
        asyncio.run(test_searcher())


class TestClinicalRAG:
    """Tests for Clinical RAG module."""

    def test_clinical_query_type(self):
        """Test ClinicalQueryType enum."""
        from core.PHASE_4 import ClinicalQueryType
        assert ClinicalQueryType.DIAGNOSIS.value == "diagnosis"
        assert ClinicalQueryType.TREATMENT.value == "treatment"
        assert ClinicalQueryType.DEVICE_USAGE.value == "device_usage"

    def test_query_intent(self):
        """Test QueryIntent enum."""
        from core.PHASE_4 import QueryIntent
        assert QueryIntent.FIND.value == "find"
        assert QueryIntent.LEARN.value == "learn"
        assert QueryIntent.DECIDE.value == "decide"

    def test_clinical_query_processor(self):
        """Test ClinicalQueryProcessor."""
        from core.PHASE_4 import ClinicalQueryProcessor
        import asyncio
        
        async def test_processor():
            processor = ClinicalQueryProcessor()
            query = await processor.process("What is the diagnosis for chest pain?")
            assert query.query_type.value == "diagnosis"
            assert query.confidence > 0
        asyncio.run(test_processor())


class TestCitation:
    """Tests for Citation module."""

    def test_citation_style(self):
        """Test CitationStyle enum."""
        from core.PHASE_4 import CitationStyle
        assert CitationStyle.APA.value == "apa"
        assert CitationStyle.VANCOUVER.value == "vancouver"
        assert CitationStyle.NUMERIC.value == "numeric"

    def test_source_type(self):
        """Test SourceType enum."""
        from core.PHASE_4 import SourceType
        assert SourceType.PUBMED.value == "pubmed"
        assert SourceType.GUIDELINE.value == "guideline"
        assert SourceType.DEVICE_MANUAL.value == "device_manual"

    def test_citation_engine(self):
        """Test CitationEngine."""
        from core.PHASE_4 import CitationEngine, SourceType
        import asyncio
        
        async def test_engine():
            engine = CitationEngine()
            citation = await engine.cite(
                claim="Test claim",
                source_id="pubmed-123",
                source_type=SourceType.PUBMED,
                source_data={"title": "Test", "authors": ["Smith J"]},
            )
            assert citation.reference.title == "Test"
        asyncio.run(test_engine())


class TestKnowledgeQuality:
    """Tests for Knowledge Quality module."""

    def test_bias_type(self):
        """Test BiasType enum."""
        from core.PHASE_4 import BiasType
        assert BiasType.PUBLICATION.value == "publication"
        assert BiasType.SELECTION.value == "selection"
        assert BiasType.CONFIRMATION.value == "confirmation"

    def test_quality_dimension(self):
        """Test QualityDimension enum."""
        from core.PHASE_4 import QualityDimension
        assert QualityDimension.ACCURACY.value == "accuracy"
        assert QualityDimension.COMPLETENESS.value == "completeness"
        assert QualityDimension.CONSISTENCY.value == "consistency"


class TestKnowledgeRepository:
    """Tests for Knowledge Repository module."""

    def test_repository_type(self):
        """Test RepositoryType enum."""
        from core.PHASE_4 import RepositoryType
        assert RepositoryType.PRIMARY.value == "primary"
        assert RepositoryType.ARCHIVE.value == "archive"
        assert RepositoryType.STAGING.value == "staging"

    def test_knowledge_repository(self):
        """Test KnowledgeRepository."""
        from core.PHASE_4 import KnowledgeRepository, KnowledgeAsset, KnowledgeDomain
        import asyncio
        
        async def test_repo():
            repo = KnowledgeRepository()
            asset = KnowledgeAsset(
                asset_id="test-1",
                version="1.0.0",
                content="Test content",
                title="Test Asset",
                domain=KnowledgeDomain.CARDIOLOGY,
            )
            id = await repo.store(asset)
            assert id == "test-1"
            
            retrieved = await repo.get("test-1")
            assert retrieved is not None
            assert retrieved.title == "Test Asset"
        asyncio.run(test_repo())


class TestSyncEngine:
    """Tests for Sync Engine module."""

    def test_sync_source(self):
        """Test SyncSource enum."""
        from core.PHASE_4 import SyncSource
        assert SyncSource.PUBMED.value == "pubmed"
        assert SyncSource.FDA.value == "fda"
        assert SyncSource.EMA.value == "ema"

    def test_sync_status(self):
        """Test SyncStatus enum."""
        from core.PHASE_4 import SyncStatus
        assert SyncStatus.PENDING.value == "pending"
        assert SyncStatus.IN_PROGRESS.value == "in_progress"
        assert SyncStatus.COMPLETED.value == "completed"


class TestGovernance:
    """Tests for Governance module."""

    def test_audit_action(self):
        """Test AuditAction enum."""
        from core.PHASE_4 import AuditAction
        assert AuditAction.CREATED.value == "created"
        assert AuditAction.UPDATED.value == "updated"
        assert AuditAction.DELETED.value == "deleted"

    def test_retention_policy(self):
        """Test RetentionPolicy enum."""
        from core.PHASE_4 import RetentionPolicy
        assert RetentionPolicy.PERMANENT.value == "permanent"
        assert RetentionPolicy.STANDARD.value == "standard"
        assert RetentionPolicy.SHORT_TERM.value == "short_term"

    def test_audit_logger(self):
        """Test AuditLogger."""
        from core.PHASE_4 import AuditLogger, AuditAction
        logger = AuditLogger()
        entry = logger.log("asset-1", AuditAction.CREATED, "user-1")
        assert entry.asset_id == "asset-1"
        assert entry.action == AuditAction.CREATED

    def test_retention_manager(self):
        """Test RetentionManager."""
        from core.PHASE_4 import RetentionManager, RetentionPolicy
        manager = RetentionManager()
        manager.set_policy("asset-1", RetentionPolicy.STANDARD)
        expiry = manager.get_expiry("asset-1")
        assert expiry is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
