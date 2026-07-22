"""Knowledge Ingestion types for EREN OS."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Document Types
# =============================================================================


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    HTML = "html"
    FHIR = "fhir"
    HL7 = "hl7"
    UNKNOWN = "unknown"


# =============================================================================
# Document Source
# =============================================================================


class DocumentSource(str, Enum):
    """Document source types."""

    MANUAL = "manual"
    GUIDELINE = "guideline"
    PROTOCOL = "protocol"
    TEXTBOOK = "textbook"
    JOURNAL = "journal"
    WEBSITE = "website"
    FHIR_SERVER = "fhir_server"
    HL7_INTERFACE = "hl7_interface"
    UNKNOWN = "unknown"


# =============================================================================
# Ingestion Status
# =============================================================================


class IngestionStatus(str, Enum):
    """Ingestion status."""

    PENDING = "pending"
    EXTRACTING = "extracting"
    CLEANING = "cleaning"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# =============================================================================
# Document Metadata
# =============================================================================


@dataclass
class IngestionMetadata:
    """Metadata for ingested document."""

    document_id: str = ""
    source_type: DocumentSource = DocumentSource.UNKNOWN
    title: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    medical_specialty: str = ""
    language: str = "en"
    tags: list[str] = field(default_factory=list)
    version: str = ""
    institution: str = ""
    department: str = ""
    patient_info: bool = False
    custom: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "source_type": self.source_type.value,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "medical_specialty": self.medical_specialty,
            "language": self.language,
            "tags": self.tags,
            "version": self.version,
            "institution": self.institution,
            "department": self.department,
            "patient_info": self.patient_info,
            **{k: v for k, v in self.custom.items()},
        }


# =============================================================================
# Raw Document
# =============================================================================


@dataclass
class RawDocument:
    """Raw document before processing."""

    content: bytes
    document_type: DocumentType
    source: str
    filename: str = ""
    metadata: IngestionMetadata = field(default_factory=IngestionMetadata)

    @property
    def is_binary(self) -> bool:
        """Check if document is binary."""
        return isinstance(self.content, bytes)


# =============================================================================
# Extracted Document
# =============================================================================


@dataclass
class ExtractedDocument:
    """Document after text extraction."""

    document_id: str
    content: str
    document_type: DocumentType
    metadata: IngestionMetadata
    extraction_time_ms: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "content": self.content,
            "document_type": self.document_type.value,
            "metadata": self.metadata.to_dict(),
            "extraction_time_ms": self.extraction_time_ms,
            "warnings": self.warnings,
        }


# =============================================================================
# Cleaned Document
# =============================================================================


@dataclass
class CleanedDocument:
    """Document after text cleaning."""

    document_id: str
    content: str
    original_length: int
    cleaned_length: int
    removed_chars: int
    metadata: IngestionMetadata
    cleaning_time_ms: int = 0
    cleaning_actions: list[str] = field(default_factory=list)

    @property
    def reduction_ratio(self) -> float:
        """Get content reduction ratio."""
        if self.original_length == 0:
            return 0.0
        return (self.original_length - self.cleaned_length) / self.original_length

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "original_length": self.original_length,
            "cleaned_length": self.cleaned_length,
            "removed_chars": self.removed_chars,
            "reduction_ratio": self.reduction_ratio,
            "cleaning_time_ms": self.cleaning_time_ms,
            "cleaning_actions": self.cleaning_actions,
        }


# =============================================================================
# Chunked Document
# =============================================================================


@dataclass
class DocumentChunk:
    """A chunk of a document."""

    chunk_id: str
    document_id: str
    content: str
    index: int
    total_chunks: int
    metadata: IngestionMetadata
    char_count: int = 0
    word_count: int = 0

    def __post_init__(self):
        """Post initialization."""
        if self.char_count == 0:
            self.char_count = len(self.content)
        if self.word_count == 0:
            self.word_count = len(self.content.split())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "index": self.index,
            "total_chunks": self.total_chunks,
            "char_count": self.char_count,
            "word_count": self.word_count,
        }


@dataclass
class ChunkedDocument:
    """Document after chunking."""

    document_id: str
    chunks: list[DocumentChunk]
    metadata: IngestionMetadata
    chunking_time_ms: int = 0
    chunking_strategy: str = "sentence"

    @property
    def total_chunks(self) -> int:
        """Get total chunks."""
        return len(self.chunks)

    @property
    def total_characters(self) -> int:
        """Get total characters."""
        return sum(c.char_count for c in self.chunks)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "total_chunks": self.total_chunks,
            "total_characters": self.total_characters,
            "chunking_time_ms": self.chunking_time_ms,
            "chunking_strategy": self.chunking_strategy,
        }


# =============================================================================
# Ingested Document
# =============================================================================


@dataclass
class IngestedDocument:
    """Document after full ingestion."""

    document_id: str
    original_type: DocumentType
    chunks_created: int
    embeddings_generated: int
    metadata: IngestionMetadata
    status: IngestionStatus
    total_time_ms: int = 0
    stages: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        """Check if ingestion was successful."""
        return self.status == IngestionStatus.COMPLETED

    @property
    def is_partial(self) -> bool:
        """Check if ingestion was partial."""
        return self.status == IngestionStatus.PARTIAL

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "original_type": self.original_type.value,
            "chunks_created": self.chunks_created,
            "embeddings_generated": self.embeddings_generated,
            "status": self.status.value,
            "total_time_ms": self.total_time_ms,
            "stages": self.stages,
            "errors": self.errors,
            "warnings": self.warnings,
        }


# =============================================================================
# Ingestion Statistics
# =============================================================================


@dataclass
class IngestionStatistics:
    """Statistics for ingestion operations."""

    total_documents: int = 0
    successful_documents: int = 0
    failed_documents: int = 0
    partial_documents: int = 0
    total_chunks: int = 0
    total_characters: int = 0
    average_chunks_per_document: float = 0.0
    average_time_ms: float = 0.0
    by_type: dict[str, int] = field(default_factory=dict)
    by_source: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "successful_documents": self.successful_documents,
            "failed_documents": self.failed_documents,
            "partial_documents": self.partial_documents,
            "total_chunks": self.total_chunks,
            "total_characters": self.total_characters,
            "average_chunks_per_document": self.average_chunks_per_document,
            "average_time_ms": self.average_time_ms,
            "by_type": self.by_type,
            "by_source": self.by_source,
        }
