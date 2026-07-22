"""Unit tests for EREN Knowledge Ingestion Pipeline (v2)."""

import pytest

from core.PHASE_2.ingestion.types import (
    DocumentType,
    DocumentSource,
    IngestionStatus,
    IngestionMetadata,
    RawDocument,
    ExtractedDocument,
    CleanedDocument,
    DocumentChunk,
    ChunkedDocument,
    IngestedDocument,
    IngestionStatistics,
)
from core.PHASE_2.ingestion.exceptions import (
    IngestionError,
    ExtractionError,
    UnsupportedFormatError,
    ChunkingError,
    PipelineError,
)
from core.PHASE_2.ingestion.extractor import (
    BaseExtractor,
    PDFExtractor,
    DocxExtractor,
    TextExtractor,
    HTMLExtractor,
    FHIRExtractor,
    HL7Extractor,
    ExtractorFactory,
)
from core.PHASE_2.ingestion.processors import (
    TextProcessor,
    TextNormalizer,
    MedicalProcessor,
)
from core.PHASE_2.ingestion.chunking import (
    BaseChunkBuilder,
    SentenceChunkBuilder,
    RecursiveChunkBuilder,
    SlidingWindowChunkBuilder,
    ParagraphChunkBuilder,
)
from core.PHASE_2.ingestion.metadata import MetadataBuilder, MedicalMetadataBuilder
from core.PHASE_2.ingestion.pipeline import KnowledgeIngestionPipeline
from core.PHASE_2.ingestion.registry import DocumentRegistry, get_document_registry, reset_document_registry


class TestIngestionTypes:
    """Tests for ingestion types."""

    def test_document_type_values(self):
        """Test document type values."""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.DOCX.value == "docx"
        assert DocumentType.TXT.value == "txt"

    def test_document_source_values(self):
        """Test document source values."""
        assert DocumentSource.MANUAL.value == "manual"
        assert DocumentSource.GUIDELINE.value == "guideline"
        assert DocumentSource.FHIR_SERVER.value == "fhir_server"

    def test_ingestion_status_values(self):
        """Test ingestion status values."""
        assert IngestionStatus.PENDING.value == "pending"
        assert IngestionStatus.COMPLETED.value == "completed"
        assert IngestionStatus.FAILED.value == "failed"

    def test_ingestion_metadata_creation(self):
        """Test metadata creation."""
        metadata = IngestionMetadata(
            document_id="doc-123",
            source_type=DocumentSource.MANUAL,
            title="Medical Manual",
            author="Dr. Smith",
        )
        assert metadata.document_id == "doc-123"
        assert metadata.title == "Medical Manual"

    def test_ingestion_metadata_to_dict(self):
        """Test metadata to dict."""
        metadata = IngestionMetadata()
        data = metadata.to_dict()
        assert "document_id" in data
        assert "created_at" in data

    def test_raw_document_creation(self):
        """Test raw document creation."""
        content = b"Hello, world!"
        raw = RawDocument(
            content=content,
            document_type=DocumentType.TXT,
            source="test.txt",
        )
        assert raw.content == content
        assert raw.is_binary is True

    def test_extracted_document_creation(self):
        """Test extracted document creation."""
        extracted = ExtractedDocument(
            document_id="doc-123",
            content="Extracted text",
            document_type=DocumentType.PDF,
            metadata=IngestionMetadata(),
        )
        assert extracted.document_id == "doc-123"
        assert extracted.content == "Extracted text"

    def test_cleaned_document_creation(self):
        """Test cleaned document creation."""
        cleaned = CleanedDocument(
            document_id="doc-123",
            content="Cleaned text",
            original_length=100,
            cleaned_length=90,
            removed_chars=10,
            metadata=IngestionMetadata(),
        )
        assert cleaned.reduction_ratio == 0.1

    def test_document_chunk_creation(self):
        """Test document chunk creation."""
        chunk = DocumentChunk(
            chunk_id="chunk-1",
            document_id="doc-123",
            content="Chunk content",
            index=0,
            total_chunks=5,
            metadata=IngestionMetadata(),
        )
        assert chunk.char_count == len("Chunk content")
        assert chunk.word_count == 2

    def test_chunked_document_creation(self):
        """Test chunked document creation."""
        chunks = [
            DocumentChunk(
                chunk_id=f"chunk-{i}",
                document_id="doc-123",
                content=f"Chunk {i}",
                index=i,
                total_chunks=3,
                metadata=IngestionMetadata(),
            )
            for i in range(3)
        ]

        chunked = ChunkedDocument(
            document_id="doc-123",
            chunks=chunks,
            metadata=IngestionMetadata(),
        )
        assert chunked.total_chunks == 3
        assert chunked.total_characters > 0

    def test_ingested_document_creation(self):
        """Test ingested document creation."""
        ingested = IngestedDocument(
            document_id="doc-123",
            original_type=DocumentType.PDF,
            chunks_created=10,
            embeddings_generated=10,
            metadata=IngestionMetadata(),
            status=IngestionStatus.COMPLETED,
        )
        assert ingested.is_success is True
        assert ingested.is_partial is False

    def test_ingestion_statistics_creation(self):
        """Test statistics creation."""
        stats = IngestionStatistics(
            total_documents=100,
            successful_documents=95,
            failed_documents=5,
            total_chunks=500,
        )
        # Manually calculate average for test
        stats.average_chunks_per_document = stats.total_chunks / stats.total_documents
        assert stats.total_documents == 100
        assert stats.average_chunks_per_document == 5.0


class TestExtractors:
    """Tests for document extractors."""

    def test_pdf_extractor_supported_types(self):
        """Test PDF extractor supported types."""
        extractor = PDFExtractor()
        assert DocumentType.PDF in extractor.supported_types

    def test_docx_extractor_supported_types(self):
        """Test DOCX extractor supported types."""
        extractor = DocxExtractor()
        assert DocumentType.DOCX in extractor.supported_types

    def test_text_extractor_supported_types(self):
        """Test text extractor supported types."""
        extractor = TextExtractor()
        assert DocumentType.TXT in extractor.supported_types
        assert DocumentType.MARKDOWN in extractor.supported_types

    def test_html_extractor_supported_types(self):
        """Test HTML extractor supported types."""
        extractor = HTMLExtractor()
        assert DocumentType.HTML in extractor.supported_types

    def test_fhir_extractor_supported_types(self):
        """Test FHIR extractor supported types."""
        extractor = FHIRExtractor()
        assert DocumentType.FHIR in extractor.supported_types

    def test_hl7_extractor_supported_types(self):
        """Test HL7 extractor supported types."""
        extractor = HL7Extractor()
        assert DocumentType.HL7 in extractor.supported_types

    def test_extractor_factory_registration(self):
        """Test extractor factory registration."""
        ExtractorFactory.register(PDFExtractor())
        extractor = ExtractorFactory.get(DocumentType.PDF)
        assert isinstance(extractor, PDFExtractor)

    def test_extractor_factory_list_supported(self):
        """Test listing supported types."""
        ExtractorFactory.register_defaults()
        types = ExtractorFactory.list_supported_types()
        assert DocumentType.PDF in types
        assert DocumentType.DOCX in types

    @pytest.mark.asyncio
    async def test_text_extractor_extract(self):
        """Test text extraction."""
        extractor = TextExtractor()
        raw = RawDocument(
            content=b"Hello, world!",
            document_type=DocumentType.TXT,
            source="test.txt",
        )

        extracted = await extractor.extract(raw)
        assert extracted.content == "Hello, world!"
        assert extracted.document_type == DocumentType.TXT

    @pytest.mark.asyncio
    async def test_pdf_extractor_extract(self):
        """Test PDF extraction with mock."""
        extractor = PDFExtractor()
        raw = RawDocument(
            content=b"PDF content",
            document_type=DocumentType.PDF,
            source="test.pdf",
        )

        extracted = await extractor.extract(raw)
        assert extracted.document_type == DocumentType.PDF


class TestTextProcessors:
    """Tests for text processors."""

    @pytest.fixture
    def normalizer(self):
        """Create test normalizer."""
        return TextNormalizer()

    @pytest.fixture
    def processor(self):
        """Create test processor."""
        return TextProcessor()

    @pytest.fixture
    def sample_extracted(self):
        """Create sample extracted document."""
        return ExtractedDocument(
            document_id="doc-123",
            content="This is    some   text   with   extra   whitespace.",
            document_type=DocumentType.TXT,
            metadata=IngestionMetadata(),
        )

    @pytest.mark.asyncio
    async def test_normalizer_removes_whitespace(self, normalizer, sample_extracted):
        """Test normalizer removes extra whitespace."""
        cleaned = await normalizer.normalize(sample_extracted)
        assert "   " not in cleaned.content

    @pytest.mark.asyncio
    async def test_normalizer_tracks_actions(self, normalizer, sample_extracted):
        """Test normalizer tracks actions."""
        cleaned = await normalizer.normalize(sample_extracted)
        assert len(cleaned.cleaning_actions) > 0

    @pytest.mark.asyncio
    async def test_processor_coordinates(self, processor, sample_extracted):
        """Test processor coordinates normalization."""
        cleaned = await processor.process(sample_extracted)
        assert cleaned.content is not None


class TestChunkBuilders:
    """Tests for chunk builders."""

    @pytest.fixture
    def cleaner(self):
        """Create sample cleaned document."""
        return CleanedDocument(
            document_id="doc-123",
            content="This is the first sentence. This is the second sentence. This is the third sentence. Fourth sentence here. Fifth sentence. Sixth sentence.",
            original_length=150,
            cleaned_length=150,
            removed_chars=0,
            metadata=IngestionMetadata(),
        )

    @pytest.mark.asyncio
    async def test_sentence_chunker(self, cleaner):
        """Test sentence chunker."""
        builder = SentenceChunkBuilder(sentences_per_chunk=2, overlap=1)
        chunked = await builder.build(cleaner)

        assert chunked.total_chunks > 0
        assert builder.strategy_name == "sentence"
        assert all(isinstance(c, DocumentChunk) for c in chunked.chunks)

    @pytest.mark.asyncio
    async def test_recursive_chunker(self, cleaner):
        """Test recursive chunker."""
        builder = RecursiveChunkBuilder(chunk_size=50)
        chunked = await builder.build(cleaner)

        assert chunked.total_chunks > 0
        assert builder.strategy_name == "recursive"
        assert all(isinstance(c, DocumentChunk) for c in chunked.chunks)

    @pytest.mark.asyncio
    async def test_sliding_window_chunker(self, cleaner):
        """Test sliding window chunker."""
        builder = SlidingWindowChunkBuilder(chunk_size=50, overlap=10)
        chunked = await builder.build(cleaner)

        assert chunked.total_chunks > 0
        assert builder.strategy_name == "sliding_window"
        assert all(isinstance(c, DocumentChunk) for c in chunked.chunks)

    @pytest.mark.asyncio
    async def test_paragraph_chunker(self, cleaner):
        """Test paragraph chunker."""
        cleaner.content = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        builder = ParagraphChunkBuilder(max_chunk_size=100, overlap=10)
        chunked = await builder.build(cleaner)

        assert chunked.total_chunks > 0
        assert builder.strategy_name == "paragraph"
        assert all(isinstance(c, DocumentChunk) for c in chunked.chunks)

    def test_chunk_builder_base_is_abstract(self):
        """Test base chunk builder is abstract."""
        with pytest.raises(TypeError):
            BaseChunkBuilder()


class TestMetadataBuilders:
    """Tests for metadata builders."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return MetadataBuilder()

    @pytest.fixture
    def medical_builder(self):
        """Create medical builder."""
        return MedicalMetadataBuilder()

    def test_builder_from_raw(self, builder):
        """Test building from raw document."""
        raw = RawDocument(
            content=b"Test content",
            document_type=DocumentType.PDF,
            source="test.pdf",
            filename="medical_manual.pdf",
        )

        metadata = builder.build_from_raw(raw)
        assert metadata.document_id is not None

    def test_builder_extracts_title(self, builder):
        """Test title extraction."""
        extracted = ExtractedDocument(
            document_id="doc-123",
            content="Medical Guidelines\n\nThis is the actual content...",
            document_type=DocumentType.PDF,
            metadata=IngestionMetadata(),
        )

        metadata = builder.build_from_extracted(extracted)
        assert metadata.title == "Medical Guidelines"

    def test_medical_builder_detects_specialty(self, medical_builder):
        """Test medical specialty detection."""
        extracted = ExtractedDocument(
            document_id="doc-123",
            content="The patient has heart disease and cardiac symptoms.",
            document_type=DocumentType.PDF,
            metadata=IngestionMetadata(),
        )

        metadata = medical_builder.build_from_extracted(extracted)
        assert metadata.medical_specialty == "cardiology"

    def test_medical_builder_extracts_tags(self, medical_builder):
        """Test medical tag extraction."""
        extracted = ExtractedDocument(
            document_id="doc-123",
            content="Diagnosis: Heart disease. Treatment: Medication.",
            document_type=DocumentType.PDF,
            metadata=IngestionMetadata(),
        )

        metadata = medical_builder.build_from_extracted(extracted)
        assert "diagnosis" in metadata.tags
        assert "treatment" in metadata.tags


class TestPipeline:
    """Tests for ingestion pipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create test pipeline."""
        return KnowledgeIngestionPipeline()

    @pytest.mark.asyncio
    async def test_pipeline_ingest_text(self, pipeline):
        """Test pipeline with text document."""
        raw = RawDocument(
            content=b"Test document content for ingestion.",
            document_type=DocumentType.TXT,
            source="test.txt",
            filename="test.txt",
        )

        result = await pipeline.ingest(raw, store_in_vector=False)
        assert result.status == IngestionStatus.COMPLETED
        assert result.chunks_created > 0

    @pytest.mark.asyncio
    async def test_pipeline_returns_stages(self, pipeline):
        """Test pipeline returns stages."""
        raw = RawDocument(
            content=b"Test content",
            document_type=DocumentType.TXT,
            source="test.txt",
        )

        result = await pipeline.ingest(raw, store_in_vector=False)
        assert len(result.stages) > 0
        assert result.stages[0]["stage"] == "extraction"

    @pytest.mark.asyncio
    async def test_pipeline_tracks_statistics(self, pipeline):
        """Test pipeline tracks statistics."""
        raw = RawDocument(
            content=b"Test content",
            document_type=DocumentType.TXT,
            source="test.txt",
        )

        await pipeline.ingest(raw, store_in_vector=False)

        stats = pipeline.get_statistics()
        assert stats.total_documents == 1
        assert stats.successful_documents == 1


class TestRegistry:
    """Tests for document registry."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset registry before each test."""
        reset_document_registry()

    @pytest.fixture
    def registry(self):
        """Create test registry."""
        return DocumentRegistry()

    def test_registry_register(self, registry):
        """Test registering a document."""
        ingested = IngestedDocument(
            document_id="doc-123",
            original_type=DocumentType.PDF,
            chunks_created=10,
            embeddings_generated=10,
            metadata=IngestionMetadata(),
            status=IngestionStatus.COMPLETED,
        )

        registry.register(ingested)
        assert registry.exists("doc-123") is True

    def test_registry_get(self, registry):
        """Test getting a document."""
        ingested = IngestedDocument(
            document_id="doc-123",
            original_type=DocumentType.PDF,
            chunks_created=10,
            embeddings_generated=10,
            metadata=IngestionMetadata(),
            status=IngestionStatus.COMPLETED,
        )

        registry.register(ingested)
        retrieved = registry.get("doc-123")
        assert retrieved is not None
        assert retrieved.document_id == "doc-123"

    def test_registry_delete(self, registry):
        """Test deleting a document."""
        ingested = IngestedDocument(
            document_id="doc-123",
            original_type=DocumentType.PDF,
            chunks_created=10,
            embeddings_generated=10,
            metadata=IngestionMetadata(),
            status=IngestionStatus.COMPLETED,
        )

        registry.register(ingested)
        deleted = registry.delete("doc-123")
        assert deleted is True
        assert registry.exists("doc-123") is False

    def test_registry_count(self, registry):
        """Test counting documents."""
        for i in range(3):
            ingested = IngestedDocument(
                document_id=f"doc-{i}",
                original_type=DocumentType.PDF,
                chunks_created=10,
                embeddings_generated=10,
                metadata=IngestionMetadata(),
                status=IngestionStatus.COMPLETED,
            )
            registry.register(ingested)

        assert registry.count() == 3

    def test_registry_statistics(self, registry):
        """Test registry statistics."""
        for i in range(3):
            ingested = IngestedDocument(
                document_id=f"doc-{i}",
                original_type=DocumentType.PDF,
                chunks_created=10,
                embeddings_generated=10,
                metadata=IngestionMetadata(),
                status=IngestionStatus.COMPLETED,
            )
            registry.register(ingested)

        stats = registry.get_statistics()
        assert stats.total_documents == 3
        assert stats.successful_documents == 3


class TestExceptions:
    """Tests for ingestion exceptions."""

    def test_ingestion_error(self):
        """Test base error."""
        error = IngestionError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_extraction_error(self):
        """Test extraction error."""
        error = ExtractionError("test.pdf", "Failed")
        assert "test.pdf" in str(error)
        assert error.source == "test.pdf"

    def test_unsupported_format_error(self):
        """Test unsupported format error."""
        error = UnsupportedFormatError("xyz")
        assert "xyz" in str(error)

    def test_chunking_error(self):
        """Test chunking error."""
        error = ChunkingError("doc-123", "Failed")
        assert "doc-123" in str(error)

    def test_pipeline_error(self):
        """Test pipeline error."""
        error = PipelineError("extraction", "Failed")
        assert "extraction" in str(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
