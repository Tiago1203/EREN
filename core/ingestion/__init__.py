"""EREN Knowledge Ingestion Pipeline (KIP v2).

Refactored with strict Single Responsibility Principle.
Pipeline ONLY orchestrates - never implements logic.
"""

from __future__ import annotations

# Types
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

# Exceptions
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

# Extractors
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

# Processors (NEW: separated by responsibility)
from core.ingestion.processors import (
    TextProcessor,
    TextNormalizer,
    MedicalProcessor,
    MedicalTerminologyNormalizer,
)

# Chunking (NEW: separated by strategy)
from core.ingestion.chunking import (
    BaseChunkBuilder,
    SentenceChunkBuilder,
    RecursiveChunkBuilder,
    SlidingWindowChunkBuilder,
    ParagraphChunkBuilder,
)

# Pipeline
from core.ingestion.pipeline import KnowledgeIngestionPipeline

# Registry
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
    # Processors
    "TextProcessor",
    "TextNormalizer",
    "MedicalProcessor",
    "MedicalTerminologyNormalizer",
    # Chunking
    "BaseChunkBuilder",
    "SentenceChunkBuilder",
    "RecursiveChunkBuilder",
    "SlidingWindowChunkBuilder",
    "ParagraphChunkBuilder",
    # Pipeline
    "KnowledgeIngestionPipeline",
    # Registry
    "DocumentRegistry",
    "get_document_registry",
    "reset_document_registry",
]
