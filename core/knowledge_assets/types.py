"""Knowledge Asset Registry types for EREN OS.

Types for the Knowledge Asset Registry (KAR).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Asset Types
# =============================================================================


class AssetType(str, Enum):
    """Types of knowledge assets.

    EREN can register any type of knowledge asset.
    The Registry is completely agnostic to content type.
    """

    # Documents
    DOCUMENT = "document"
    
    # Medical
    MEDICAL_GUIDELINE = "medical_guideline"
    CLINICAL_PROTOCOL = "clinical_protocol"
    FHIR_RESOURCE = "fhir_resource"
    HL7_MESSAGE = "hl7_message"
    
    # Technical
    TECHNICAL_MANUAL = "technical_manual"
    DEVICE_CONFIGURATION = "device_configuration"
    FIRMWARE = "firmware"
    CALIBRATION_FILE = "calibration_file"
    
    # Media
    DICOM_IMAGE = "dicom_image"
    VIDEO = "video"
    AUDIO = "audio"
    
    # Research
    RESEARCH_PAPER = "research_paper"
    DATASET = "dataset"
    MODEL = "model"
    CAD_FILE = "cad_file"
    
    # Custom
    CUSTOM = "custom"


class LifecycleState(str, Enum):
    """Lifecycle states for assets."""

    DRAFT = "draft"
    REGISTERED = "registered"
    INDEXED = "indexed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"


class PermissionLevel(str, Enum):
    """Permission levels for assets."""

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
    ARCHIVE = "archive"
    RESTORE = "restore"


# =============================================================================
# Asset Entry
# =============================================================================


@dataclass
class AssetMetadata:
    """Metadata for a knowledge asset.

    Contains metadata ONLY - never stores content.
    """

    # Core identifiers
    asset_id: str
    asset_type: AssetType
    title: str
    description: str = ""

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

    # Origin and source
    source: str = ""
    source_uri: str = ""
    storage_uri: str = ""

    # Vector storage
    vector_collection: str = ""
    chunk_count: int = 0
    embedding_count: int = 0

    # Integrity
    content_hash: str = ""
    checksum: str = ""

    # Lifecycle
    lifecycle_state: LifecycleState = LifecycleState.REGISTERED
    permission_level: PermissionLevel = PermissionLevel.INTERNAL

    # Organization
    collection: str = ""
    tags: list[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: datetime | None = None

    # Quality
    confidence_level: float = 1.0
    custom_metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type.value,
            "title": self.title,
            "description": self.description,
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
            "source_uri": self.source_uri,
            "storage_uri": self.storage_uri,
            "vector_collection": self.vector_collection,
            "chunk_count": self.chunk_count,
            "embedding_count": self.embedding_count,
            "content_hash": self.content_hash,
            "checksum": self.checksum,
            "lifecycle_state": self.lifecycle_state.value,
            "permission_level": self.permission_level.value,
            "collection": self.collection,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "confidence_level": self.confidence_level,
            "custom_metadata": self.custom_metadata,
        }


# =============================================================================
# Asset Version
# =============================================================================


@dataclass
class AssetVersion:
    """A version of an asset."""

    version_id: str
    asset_id: str
    version: str
    changelog: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""
    content_hash: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "asset_id": self.asset_id,
            "version": self.version,
            "changelog": self.changelog,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "content_hash": self.content_hash,
        }


# =============================================================================
# Asset Collection
# =============================================================================


@dataclass
class AssetCollection:
    """A collection of assets."""

    collection_id: str
    name: str
    description: str = ""
    owner: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    asset_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_public: bool = False
    parent_collection: str = ""

    @property
    def size(self) -> int:
        """Get collection size."""
        return len(self.asset_ids)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "asset_ids": self.asset_ids,
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
    asset_id: str = ""
    user_id: str = ""
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "audit_id": self.audit_id,
            "action": self.action.value,
            "asset_id": self.asset_id,
            "user_id": self.user_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
        }


# =============================================================================
# Asset Statistics
# =============================================================================


@dataclass
class AssetStatistics:
    """Statistics for the asset registry."""

    total_assets: int = 0
    total_collections: int = 0
    total_versions: int = 0
    assets_by_type: dict[str, int] = field(default_factory=dict)
    assets_by_state: dict[str, int] = field(default_factory=dict)
    assets_by_language: dict[str, int] = field(default_factory=dict)
    assets_by_collection: dict[str, int] = field(default_factory=dict)
    total_chunks: int = 0
    total_embeddings: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_assets": self.total_assets,
            "total_collections": self.total_collections,
            "total_versions": self.total_versions,
            "assets_by_type": self.assets_by_type,
            "assets_by_state": self.assets_by_state,
            "assets_by_language": self.assets_by_language,
            "assets_by_collection": self.assets_by_collection,
            "total_chunks": self.total_chunks,
            "total_embeddings": self.total_embeddings,
        }


# =============================================================================
# Asset Search Query
# =============================================================================


@dataclass
class AssetSearchQuery:
    """Query for searching the registry."""

    query: str = ""
    asset_ids: list[str] | None = None
    asset_types: list[AssetType] | None = None
    titles: list[str] | None = None
    collections: list[str] | None = None
    tags: list[str] | None = None
    languages: list[str] | None = None
    lifecycle_states: list[LifecycleState] | None = None
    permission_levels: list[PermissionLevel] | None = None
    authors: list[str] | None = None
    institutions: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 100
    offset: int = 0
