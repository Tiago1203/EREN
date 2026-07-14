"""EREN Knowledge Ingestion Pipeline (KIP v2).

Refactored with strict Single Responsibility Principle.
Pipeline ONLY orchestrates - never implements logic.
"""

from __future__ import annotations

# Chunking (NEW: separated by strategy)
from core.ingestion.chunking import (
    BaseChunkBuilder,
    ParagraphChunkBuilder,
    RecursiveChunkBuilder,
    SentenceChunkBuilder,
    SlidingWindowChunkBuilder,
)

# Exceptions
from core.ingestion.exceptions import (
    ChunkingError,
    CleaningError,
    ConfigurationError,
    EmbeddingError,
    ExtractionError,
    IngestionError,
    PipelineError,
    RegistryError,
    StorageError,
    UnsupportedFormatError,
    ValidationError,
)

# Extractors
from core.ingestion.extractor import (
    BaseExtractor,
    DocxExtractor,
    ExtractorFactory,
    FHIRExtractor,
    HL7Extractor,
    HTMLExtractor,
    PDFExtractor,
    TextExtractor,
)

# Pipeline
from core.ingestion.pipeline import KnowledgeIngestionPipeline

# Processors (NEW: separated by responsibility)
from core.ingestion.processors import (
    MedicalProcessor,
    MedicalTerminologyNormalizer,
    TextNormalizer,
    TextProcessor,
)

# Registry
from core.ingestion.registry import (
    DocumentRegistry,
    get_document_registry,
    reset_document_registry,
)

# Types
from core.ingestion.types import (
    ChunkedDocument,
    CleanedDocument,
    DocumentChunk,
    DocumentSource,
    DocumentType,
    ExtractedDocument,
    IngestedDocument,
    IngestionMetadata,
    IngestionStatistics,
    IngestionStatus,
    RawDocument,
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
