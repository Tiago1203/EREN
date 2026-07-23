"""
PHASE 4 - EPIC 0: Exceptions Module

Excepciones específicas para la plataforma de conocimiento.
"""

from __future__ import annotations


class PHASE4BaseException(Exception):
    """Base exception for PHASE 4."""
    
    def __init__(self, message: str, code: str = "P4000", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


# =============================================================================
# KNOWLEDGE EXCEPTIONS
# =============================================================================

class KnowledgeNotFoundError(PHASE4BaseException):
    """Raised when knowledge asset is not found."""
    
    def __init__(self, asset_id: str, details: dict = None):
        super().__init__(
            message=f"Knowledge asset not found: {asset_id}",
            code="P4001",
            details={"asset_id": asset_id, **(details or {})},
        )


class KnowledgeVersionNotFoundError(PHASE4BaseException):
    """Raised when knowledge version is not found."""
    
    def __init__(self, asset_id: str, version: str, details: dict = None):
        super().__init__(
            message=f"Version {version} not found for asset: {asset_id}",
            code="P4002",
            details={"asset_id": asset_id, "version": version, **(details or {})},
        )


class KnowledgeValidationError(PHASE4BaseException):
    """Raised when knowledge validation fails."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=f"Knowledge validation failed: {message}",
            code="P4003",
            details=details,
        )


class KnowledgeGovernanceError(PHASE4BaseException):
    """Raised when governance rules are violated."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=f"Governance violation: {message}",
            code="P4004",
            details=details,
        )


# =============================================================================
# DOCUMENT PROCESSING EXCEPTIONS
# =============================================================================

class DocumentParseError(PHASE4BaseException):
    """Raised when document parsing fails."""
    
    def __init__(self, document_id: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Failed to parse document {document_id}: {reason}",
            code="P4010",
            details={"document_id": document_id, "reason": reason, **(details or {})},
        )


class UnsupportedFormatError(PHASE4BaseException):
    """Raised when document format is not supported."""
    
    def __init__(self, format: str, details: dict = None):
        super().__init__(
            message=f"Unsupported document format: {format}",
            code="P4011",
            details={"format": format, **(details or {})},
        )


class DocumentTooLargeError(PHASE4BaseException):
    """Raised when document exceeds size limit."""
    
    def __init__(self, size_mb: float, max_size_mb: float, details: dict = None):
        super().__init__(
            message=f"Document size {size_mb}MB exceeds limit of {max_size_mb}MB",
            code="P4012",
            details={"size_mb": size_mb, "max_size_mb": max_size_mb, **(details or {})},
        )


class OCRFailedError(PHASE4BaseException):
    """Raised when OCR processing fails."""
    
    def __init__(self, page: int, reason: str, details: dict = None):
        super().__init__(
            message=f"OCR failed on page {page}: {reason}",
            code="P4013",
            details={"page": page, "reason": reason, **(details or {})},
        )


# =============================================================================
# KNOWLEDGE EXTRACTION EXCEPTIONS
# =============================================================================

class ExtractionFailedError(PHASE4BaseException):
    """Raised when knowledge extraction fails."""
    
    def __init__(self, document_id: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Extraction failed for document {document_id}: {reason}",
            code="P4020",
            details={"document_id": document_id, "reason": reason, **(details or {})},
        )


class EntityRecognitionError(PHASE4BaseException):
    """Raised when entity recognition fails."""
    
    def __init__(self, text: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Entity recognition failed: {reason}",
            code="P4021",
            details={"text_preview": text[:100], "reason": reason, **(details or {})},
        )


class CodeLinkingError(PHASE4BaseException):
    """Raised when medical code linking fails."""
    
    def __init__(self, term: str, code_system: str, details: dict = None):
        super().__init__(
            message=f"Failed to link term to {code_system}: {term}",
            code="P4022",
            details={"term": term, "code_system": code_system, **(details or {})},
        )


# =============================================================================
# EMBEDDING EXCEPTIONS
# =============================================================================

class EmbeddingFailedError(PHASE4BaseException):
    """Raised when embedding generation fails."""
    
    def __init__(self, text: str, model: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Embedding generation failed for model {model}: {reason}",
            code="P4030",
            details={"model": model, "reason": reason, **(details or {})},
        )


class ModelNotFoundError(PHASE4BaseException):
    """Raised when embedding model is not available."""
    
    def __init__(self, model: str, details: dict = None):
        super().__init__(
            message=f"Embedding model not found: {model}",
            code="P4031",
            details={"model": model, **(details or {})},
        )


class EmbeddingDimensionMismatchError(PHASE4BaseException):
    """Raised when embedding dimensions don't match."""
    
    def __init__(self, expected: int, actual: int, details: dict = None):
        super().__init__(
            message=f"Embedding dimension mismatch: expected {expected}, got {actual}",
            code="P4032",
            details={"expected": expected, "actual": actual, **(details or {})},
        )


# =============================================================================
# VECTOR INDEX EXCEPTIONS
# =============================================================================

class IndexFailedError(PHASE4BaseException):
    """Raised when vector indexing fails."""
    
    def __init__(self, collection: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Indexing failed for collection {collection}: {reason}",
            code="P4040",
            details={"collection": collection, "reason": reason, **(details or {})},
        )


class CollectionNotFoundError(PHASE4BaseException):
    """Raised when collection doesn't exist."""
    
    def __init__(self, collection: str, details: dict = None):
        super().__init__(
            message=f"Collection not found: {collection}",
            code="P4041",
            details={"collection": collection, **(details or {})},
        )


class CollectionExistsError(PHASE4BaseException):
    """Raised when trying to create existing collection."""
    
    def __init__(self, collection: str, details: dict = None):
        super().__init__(
            message=f"Collection already exists: {collection}",
            code="P4042",
            details={"collection": collection, **(details or {})},
        )


class VectorStoreError(PHASE4BaseException):
    """Raised when vector store operation fails."""
    
    def __init__(self, operation: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Vector store operation '{operation}' failed: {reason}",
            code="P4043",
            details={"operation": operation, "reason": reason, **(details or {})},
        )


# =============================================================================
# RETRIEVAL EXCEPTIONS
# =============================================================================

class RetrievalFailedError(PHASE4BaseException):
    """Raised when retrieval operation fails."""
    
    def __init__(self, query: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Retrieval failed for query: {reason}",
            code="P4050",
            details={"query_preview": query[:100], "reason": reason, **(details or {})},
        )


class QueryValidationError(PHASE4BaseException):
    """Raised when query validation fails."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=f"Invalid query: {message}",
            code="P4051",
            details=details,
        )


class NoResultsError(PHASE4BaseException):
    """Raised when no results are found."""
    
    def __init__(self, query: str, details: dict = None):
        super().__init__(
            message="No results found for query",
            code="P4052",
            details={"query_preview": query[:100], **(details or {})},
        )


# =============================================================================
# CITATION EXCEPTIONS
# =============================================================================

class CitationFailedError(PHASE4BaseException):
    """Raised when citation generation fails."""
    
    def __init__(self, source_id: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Citation generation failed for source {source_id}: {reason}",
            code="P4060",
            details={"source_id": source_id, "reason": reason, **(details or {})},
        )


class DOIResolveError(PHASE4BaseException):
    """Raised when DOI resolution fails."""
    
    def __init__(self, doi: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Failed to resolve DOI {doi}: {reason}",
            code="P4061",
            details={"doi": doi, "reason": reason, **(details or {})},
        )


class SourceNotAccessibleError(PHASE4BaseException):
    """Raised when citation source is not accessible."""
    
    def __init__(self, source_id: str, url: str, details: dict = None):
        super().__init__(
            message=f"Citation source not accessible: {url}",
            code="P4062",
            details={"source_id": source_id, "url": url, **(details or {})},
        )


# =============================================================================
# QUALITY EXCEPTIONS
# =============================================================================

class QualityAssessmentFailedError(PHASE4BaseException):
    """Raised when quality assessment fails."""
    
    def __init__(self, asset_id: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Quality assessment failed for asset {asset_id}: {reason}",
            code="P4070",
            details={"asset_id": asset_id, "reason": reason, **(details or {})},
        )


class BiasDetectionError(PHASE4BaseException):
    """Raised when bias detection fails."""
    
    def __init__(self, content: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Bias detection failed: {reason}",
            code="P4071",
            details={"content_preview": content[:100], "reason": reason, **(details or {})},
        )


# =============================================================================
# SYNC EXCEPTIONS
# =============================================================================

class SyncFailedError(PHASE4BaseException):
    """Raised when synchronization fails."""
    
    def __init__(self, source: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Sync failed for source {source}: {reason}",
            code="P4080",
            details={"source": source, "reason": reason, **(details or {})},
        )


class SourceUnavailableError(PHASE4BaseException):
    """Raised when sync source is unavailable."""
    
    def __init__(self, source: str, details: dict = None):
        super().__init__(
            message=f"Sync source unavailable: {source}",
            code="P4081",
            details={"source": source, **(details or {})},
        )


# =============================================================================
# GOVERNANCE EXCEPTIONS
# =============================================================================

class GovernanceViolationError(PHASE4BaseException):
    """Raised when governance rules are violated."""
    
    def __init__(self, rule: str, asset_id: str, details: dict = None):
        super().__init__(
            message=f"Governance violation: {rule} for asset {asset_id}",
            code="P4090",
            details={"rule": rule, "asset_id": asset_id, **(details or {})},
        )


class RetentionPolicyError(PHASE4BaseException):
    """Raised when retention policy is violated."""
    
    def __init__(self, asset_id: str, policy: str, details: dict = None):
        super().__init__(
            message=f"Retention policy violation: {policy} for asset {asset_id}",
            code="P4091",
            details={"asset_id": asset_id, "policy": policy, **(details or {})},
        )


class RollbackError(PHASE4BaseException):
    """Raised when rollback operation fails."""
    
    def __init__(self, asset_id: str, version: str, reason: str, details: dict = None):
        super().__init__(
            message=f"Rollback failed for asset {asset_id} to version {version}: {reason}",
            code="P4092",
            details={"asset_id": asset_id, "version": version, "reason": reason, **(details or {})},
        )


__all__ = [
    "PHASE4BaseException",
    # Knowledge
    "KnowledgeNotFoundError",
    "KnowledgeVersionNotFoundError",
    "KnowledgeValidationError",
    "KnowledgeGovernanceError",
    # Document
    "DocumentParseError",
    "UnsupportedFormatError",
    "DocumentTooLargeError",
    "OCRFailedError",
    # Extraction
    "ExtractionFailedError",
    "EntityRecognitionError",
    "CodeLinkingError",
    # Embedding
    "EmbeddingFailedError",
    "ModelNotFoundError",
    "EmbeddingDimensionMismatchError",
    # Index
    "IndexFailedError",
    "CollectionNotFoundError",
    "CollectionExistsError",
    "VectorStoreError",
    # Retrieval
    "RetrievalFailedError",
    "QueryValidationError",
    "NoResultsError",
    # Citation
    "CitationFailedError",
    "DOIResolveError",
    "SourceNotAccessibleError",
    # Quality
    "QualityAssessmentFailedError",
    "BiasDetectionError",
    # Sync
    "SyncFailedError",
    "SourceUnavailableError",
    # Governance
    "GovernanceViolationError",
    "RetentionPolicyError",
    "RollbackError",
]
