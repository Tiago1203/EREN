"""Knowledge Registry exceptions for EREN OS."""

from __future__ import annotations


class RegistryError(Exception):
    """Base exception for registry errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class KnowledgeNotFoundError(RegistryError):
    """Raised when knowledge entry is not found."""

    def __init__(self, knowledge_id: str):
        super().__init__(f"Knowledge entry not found: {knowledge_id}")
        self.knowledge_id = knowledge_id


class DocumentNotFoundError(RegistryError):
    """Raised when document is not found."""

    def __init__(self, document_id: str):
        super().__init__(f"Document not found: {document_id}")
        self.document_id = document_id


class CollectionNotFoundError(RegistryError):
    """Raised when collection is not found."""

    def __init__(self, collection_id: str):
        super().__init__(f"Collection not found: {collection_id}")
        self.collection_id = collection_id


class VersionNotFoundError(RegistryError):
    """Raised when version is not found."""

    def __init__(self, version_id: str, knowledge_id: str = ""):
        msg = f"Version not found: {version_id}"
        if knowledge_id:
            msg += f" for knowledge {knowledge_id}"
        super().__init__(msg)
        self.version_id = version_id
        self.knowledge_id = knowledge_id


class DuplicateKnowledgeError(RegistryError):
    """Raised when knowledge entry already exists."""

    def __init__(self, knowledge_id: str):
        super().__init__(f"Knowledge entry already exists: {knowledge_id}")
        self.knowledge_id = knowledge_id


class DuplicateCollectionError(RegistryError):
    """Raised when collection already exists."""

    def __init__(self, collection_id: str):
        super().__init__(f"Collection already exists: {collection_id}")
        self.collection_id = collection_id


class PermissionDeniedError(RegistryError):
    """Raised when permission is denied."""

    def __init__(self, action: str, resource: str = ""):
        msg = f"Permission denied: {action}"
        if resource:
            msg += f" on {resource}"
        super().__init__(msg)
        self.action = action
        self.resource = resource


class ValidationError(RegistryError):
    """Raised when validation fails."""

    def __init__(self, field: str, reason: str = ""):
        msg = f"Validation error on {field}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
        self.field = field
        self.reason = reason


class AuditLogError(RegistryError):
    """Raised when audit logging fails."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Audit log error: {reason}")
        self.reason = reason


class ConfigurationError(RegistryError):
    """Raised when configuration is invalid."""

    def __init__(self, reason: str = ""):
        super().__init__(f"Configuration error: {reason}")
        self.reason = reason
