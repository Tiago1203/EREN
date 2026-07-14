"""Knowledge Registry types for EREN OS.

Types for the Knowledge Registry Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Registry Enums
# =============================================================================


class KnowledgeStatus(str, Enum):
    """Status of knowledge in registry."""

    REGISTERED = "registered"
    INDEXED = "indexed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    DELETED = "deleted"


class PermissionLevel(str, Enum):
    """Permission levels for knowledge."""

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class AuditAction(str, Enum):
    """Audit log actions."""

    REGISTER = "register"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    SEARCH = "search"
    ACCESS = "access"


# =============================================================================
# Knowledge Entry
# =============================================================================


@dataclass
class KnowledgeEntry:
    """A knowledge entry in the registry.

    Contains metadata ONLY - never stores documents, embeddings, or vectors.
    """

    # Core identifiers
    knowledge_id: str
    document_id: str

    # Descriptive info
    title: str
    description: str = ""
    doc_type: str = ""
    category: str = ""
    medical_specialty: str = ""

    # Versioning
    version: str = "1.0.0"
    version_major: int = 1
    version_minor: int = 0
    version_patch: int = 0

    # Language and authorship
    language: str = "en"
    author: str = ""
    institution: str = ""
    hospital: str = ""
    department: str = ""

    # Origin
    source: str = ""
    source_type: str = ""

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: datetime | None = None

    # Content metrics
    chunk_count: int = 0
    embedding_count: int = 0
    content_hash: str = ""
    checksum: str = ""

    # Status and permissions
    status: KnowledgeStatus = KnowledgeStatus.REGISTERED
    permission_level: PermissionLevel = PermissionLevel.INTERNAL

    # Organization
    collection: str = ""
    tags: list[str] = field(default_factory=list)

    # Quality and metadata
    confidence_level: float = 1.0
    custom_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "knowledge_id": self.knowledge_id,
            "document_id": self.document_id,
            "title": self.title,
            "description": self.description,
            "doc_type": self.doc_type,
            "category": self.category,
            "medical_specialty": self.medical_specialty,
            "version": self.version,
            "version_major": self.version_major,
            "version_minor": self.version_minor,
            "version_patch": self.version_patch,
            "language": self.language,
            "author": self.author,
            "institution": self.institution,
            "hospital": self.hospital,
            "department": self.department,
            "source": self.source,
            "source_type": self.source_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "chunk_count": self.chunk_count,
            "embedding_count": self.embedding_count,
            "content_hash": self.content_hash,
            "checksum": self.checksum,
            "status": self.status.value,
            "permission_level": self.permission_level.value,
            "collection": self.collection,
            "tags": self.tags,
            "confidence_level": self.confidence_level,
            "custom_metadata": self.custom_metadata,
        }


# =============================================================================
# Knowledge Version
# =============================================================================


@dataclass
class KnowledgeVersion:
    """A version of a knowledge entry."""

    version_id: str
    knowledge_id: str
    version: str
    changelog: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""
    content_hash: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "knowledge_id": self.knowledge_id,
            "version": self.version,
            "changelog": self.changelog,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "content_hash": self.content_hash,
        }


# =============================================================================
# Knowledge Collection
# =============================================================================


@dataclass
class KnowledgeCollection:
    """A collection of knowledge entries."""

    collection_id: str
    name: str
    description: str = ""
    owner: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    knowledge_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_public: bool = False
    parent_collection: str = ""

    @property
    def size(self) -> int:
        """Get collection size."""
        return len(self.knowledge_ids)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "knowledge_ids": self.knowledge_ids,
            "tags": self.tags,
            "is_public": self.is_public,
            "parent_collection": self.parent_collection,
            "size": self.size,
        }


# =============================================================================
# Audit Log
# =============================================================================


@dataclass
class AuditLog:
    """Audit log entry."""

    audit_id: str
    action: AuditAction
    knowledge_id: str = ""
    user_id: str = ""
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "audit_id": self.audit_id,
            "action": self.action.value,
            "knowledge_id": self.knowledge_id,
            "user_id": self.user_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
        }


# =============================================================================
# Registry Statistics
# =============================================================================


@dataclass
class RegistryStatistics:
    """Statistics for the knowledge registry."""

    total_entries: int = 0
    total_collections: int = 0
    total_versions: int = 0
    entries_by_status: dict[str, int] = field(default_factory=dict)
    entries_by_category: dict[str, int] = field(default_factory=dict)
    entries_by_specialty: dict[str, int] = field(default_factory=dict)
    entries_by_language: dict[str, int] = field(default_factory=dict)
    entries_by_collection: dict[str, int] = field(default_factory=dict)
    total_chunks: int = 0
    total_embeddings: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_entries": self.total_entries,
            "total_collections": self.total_collections,
            "total_versions": self.total_versions,
            "entries_by_status": self.entries_by_status,
            "entries_by_category": self.entries_by_category,
            "entries_by_specialty": self.entries_by_specialty,
            "entries_by_language": self.entries_by_language,
            "entries_by_collection": self.entries_by_collection,
            "total_chunks": self.total_chunks,
            "total_embeddings": self.total_embeddings,
        }


# =============================================================================
# Search Query
# =============================================================================


@dataclass
class RegistrySearchQuery:
    """Query for searching the registry."""

    query: str = ""
    knowledge_ids: list[str] | None = None
    document_ids: list[str] | None = None
    titles: list[str] | None = None
    categories: list[str] | None = None
    specialties: list[str] | None = None
    collections: list[str] | None = None
    tags: list[str] | None = None
    languages: list[str] | None = None
    statuses: list[KnowledgeStatus] | None = None
    permission_levels: list[PermissionLevel] | None = None
    authors: list[str] | None = None
    institutions: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 100
    offset: int = 0
