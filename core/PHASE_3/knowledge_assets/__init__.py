"""EREN Knowledge Asset Registry (KAR).

The official registry of all knowledge assets available in EREN.

Philosophy:
    EREN doesn't just manage documents.
    EREN manages any knowledge asset.

    The Registry is completely agnostic to asset type.
    It can register:
    - Documents
    - Manuals
    - Papers
    - Protocols
    - FHIR resources
    - HL7 messages
    - DICOM images
    - Videos
    - Firmware
    - CAD models
    - Datasets
    - Any future asset type

    The Registry NEVER stores:
    - Content
    - Embeddings
    - Vectors
    - Files

    It ONLY manages:
    - Asset metadata
    - Collections
    - Versions
    - Permissions
    - Audit logs
"""

from __future__ import annotations

# Components
from core.PHASE_3.knowledge_assets.catalog import (
    AssetCatalog,
    get_asset_catalog,
    reset_asset_catalog,
)
from core.PHASE_3.knowledge_assets.collections import (
    AssetCollections,
    get_asset_collections,
    reset_asset_collections,
)

# Exceptions
from core.PHASE_3.knowledge_assets.exceptions import (
    AssetNotFoundError,
    AssetRegistryError,
    AuditLogError,
    CollectionNotFoundError,
    ConfigurationError,
    DuplicateAssetError,
    DuplicateCollectionError,
    PermissionDeniedError,
    ValidationError,
    VersionNotFoundError,
)
from core.PHASE_3.knowledge_assets.permissions import (
    AuditLogger,
    PermissionChecker,
    get_audit_logger,
    get_permission_checker,
    reset_permissions,
)
from core.PHASE_3.knowledge_assets.registry import (
    KnowledgeAssetRegistry,
    get_asset_registry,
    reset_asset_registry,
)

# Types
from core.PHASE_3.knowledge_assets.types import (
    AssetCollection,
    AssetMetadata,
    AssetSearchQuery,
    AssetStatistics,
    AssetType,
    AssetVersion,
    AuditAction,
    AuditLog,
    LifecycleState,
    PermissionLevel,
)
from core.PHASE_3.knowledge_assets.versions import (
    VersionManager,
    get_version_manager,
    reset_version_manager,
)

__all__ = [
    # Types
    "AssetType",
    "LifecycleState",
    "PermissionLevel",
    "AuditAction",
    "AssetMetadata",
    "AssetVersion",
    "AssetCollection",
    "AuditLog",
    "AssetStatistics",
    "AssetSearchQuery",
    # Exceptions
    "AssetRegistryError",
    "AssetNotFoundError",
    "CollectionNotFoundError",
    "VersionNotFoundError",
    "DuplicateAssetError",
    "DuplicateCollectionError",
    "PermissionDeniedError",
    "ValidationError",
    "AuditLogError",
    "ConfigurationError",
    # Components
    "AssetCatalog",
    "get_asset_catalog",
    "reset_asset_catalog",
    "AssetCollections",
    "get_asset_collections",
    "reset_asset_collections",
    "VersionManager",
    "get_version_manager",
    "reset_version_manager",
    "AuditLogger",
    "PermissionChecker",
    "get_audit_logger",
    "get_permission_checker",
    "reset_permissions",
    "KnowledgeAssetRegistry",
    "get_asset_registry",
    "reset_asset_registry",
]
