"""EREN Knowledge Ingestion Pipeline (KIP).

This is where EREN really starts to "study".

Pipeline:
    PDF / DOCX / TXT / FHIR / HL7
            │
            ▼
    Knowledge Ingestion Pipeline
            │
            ├── Extractor
            ├── Cleaner
            ├── Chunker
            ├── Metadata Builder
            ├── Embedding Generator
            └── Vector Memory Writer
            │
            ▼
    Knowledge indexed in Vector Memory
"""

from __future__ import annotations

from core.ingestion.types import (
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
from core.ingestion.exceptions import (
    IngestionError,
    ExtractionError,
    UnsupportedFormatError,
    CleaningError,
    ChunkingError,
    EmbeddingError,
    StorageError,
    PipelineError,
    ValidationError,
    ConfigurationError,
    RegistryError,
)
from core.ingestion.extractor import (
    BaseExtractor,
    PDFExtractor,
    DocxExtractor,
    TextExtractor,
    HTMLExtractor,
    FHIRExtractor,
    HL7Extractor,
    ExtractorFactory,
)
from core.ingestion.cleaner import (
    TextCleaner,
    MedicalTextCleaner,
)
from core.ingestion.metadata import (
    MetadataBuilder,
    MedicalMetadataBuilder,
)
from core.ingestion.pipeline import KnowledgeIngestionPipeline
from core.ingestion.registry import (
    DocumentRegistry,
    get_document_registry,
    reset_document_registry,
)

__all__ = [
    # Types
    "DocumentType",
    "DocumentSource",
    "IngestionStatus",
    "IngestionMetadata",
    "RawDocument",
    "ExtractedDocument",
    "CleanedDocument",
    "DocumentChunk",
    "ChunkedDocument",
    "IngestedDocument",
    "IngestionStatistics",
    # Exceptions
    "IngestionError",
    "ExtractionError",
    "UnsupportedFormatError",
    "CleaningError",
    "ChunkingError",
    "EmbeddingError",
    "StorageError",
    "PipelineError",
    "ValidationError",
    "ConfigurationError",
    "RegistryError",
    # Extractors
    "BaseExtractor",
    "PDFExtractor",
    "DocxExtractor",
    "TextExtractor",
    "HTMLExtractor",
    "FHIRExtractor",
    "HL7Extractor",
    "ExtractorFactory",
    # Cleaners
    "TextCleaner",
    "MedicalTextCleaner",
    # Metadata
    "MetadataBuilder",
    "MedicalMetadataBuilder",
    # Pipeline
    "KnowledgeIngestionPipeline",
    # Registry
    "DocumentRegistry",
    "get_document_registry",
    "reset_document_registry",
]
