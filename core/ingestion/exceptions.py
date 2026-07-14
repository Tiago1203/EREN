"""Knowledge Ingestion exceptions for EREN OS."""

from __future__ import annotations


class IngestionError(Exception):
    """Base exception for ingestion errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ExtractionError(IngestionError):
    """Raised when text extraction fails."""

    def __init__(self, source: str, reason: str = ""):
        super().__init__(f"Extraction failed for {source}: {reason}")
        self.source = source
        self.reason = reason


class UnsupportedFormatError(IngestionError):
    """Raised when document format is not supported."""

    def __init__(self, format: str):
        super().__init__(f"Unsupported document format: {format}")
        self.format = format


class CleaningError(IngestionError):
    """Raised when text cleaning fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Text cleaning failed: {reason}")
        self.reason = reason


class ChunkingError(IngestionError):
    """Raised when document chunking fails."""

    def __init__(self, document_id: str, reason: str = ""):
        super().__init__(f"Chunking failed for {document_id}: {reason}")
        self.document_id = document_id
        self.reason = reason


class EmbeddingError(IngestionError):
    """Raised when embedding generation fails."""

    def __init__(self, document_id: str, reason: str = ""):
        super().__init__(f"Embedding failed for {document_id}: {reason}")
        self.document_id = document_id
        self.reason = reason


class StorageError(IngestionError):
    """Raised when storage fails."""

    def __init__(self, document_id: str, reason: str = ""):
        super().__init__(f"Storage failed for {document_id}: {reason}")
        self.document_id = document_id
        self.reason = reason


class PipelineError(IngestionError):
    """Raised when pipeline execution fails."""

    def __init__(self, stage: str, reason: str = ""):
        super().__init__(f"Pipeline failed at {stage}: {reason}")
        self.stage = stage
        self.reason = reason


class ValidationError(IngestionError):
    """Raised when validation fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Validation failed: {reason}")
        self.reason = reason


class ConfigurationError(IngestionError):
    """Raised when configuration is invalid."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Configuration error: {reason}")
        self.reason = reason


class RegistryError(IngestionError):
    """Raised when registry operation fails."""

    def __init__(self, operation: str, reason: str = ""):
        super().__init__(f"Registry error during {operation}: {reason}")
        self.operation = operation
        self.reason = reason
