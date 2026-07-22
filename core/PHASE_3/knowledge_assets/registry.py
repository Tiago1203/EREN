"""Knowledge Asset Registry (KAR) for EREN OS.

Main registry class for managing knowledge assets.
"""

from __future__ import annotations

import hashlib
import threading
import uuid
from typing import TYPE_CHECKING

from core.PHASE_1.domain.knowledge_assets.catalog import AssetCatalog, get_asset_catalog
from core.PHASE_1.domain.knowledge_assets.collections import AssetCollections, get_asset_collections
from core.PHASE_1.domain.knowledge_assets.exceptions import (
    AssetNotFoundError,
)
from core.PHASE_1.domain.knowledge_assets.permissions import AuditLogger, PermissionChecker, get_audit_logger
from core.PHASE_1.domain.knowledge_assets.types import (
    AssetMetadata,
    AssetSearchQuery,
    AssetStatistics,
    AssetType,
    AuditAction,
    LifecycleState,
)
from core.PHASE_1.domain.knowledge_assets.versions import VersionManager, get_version_manager

if TYPE_CHECKING:
    pass


class KnowledgeAssetRegistry:
    """Knowledge Asset Registry (KAR).

    Manages metadata catalog of all knowledge assets.
    NEVER stores content, embeddings, vectors, or files.
    ONLY manages metadata.

    Philosophy:
        The Registry doesn't know about:
        - SQLite, PostgreSQL, Chroma, Qdrant
        - Files, embeddings, vectors
        - Content storage

        It ONLY knows about:
        - Asset metadata
        - Collections
        - Versions
        - Permissions
        - Audit logs

    Can register any type of asset:
    - Documents
    - Manuals
    - Papers
    - Protocols
    - FHIR resources
    - HL7 messages
    - DICOM images
    - Videos
    - Firmware
    - Models
    - Datasets
    - Any future asset type
    """

    def __init__(
        self,
        catalog: AssetCatalog | None = None,
        collections: AssetCollections | None = None,
        versions: VersionManager | None = None,
        audit_logger: AuditLogger | None = None,
        permission_checker: PermissionChecker | None = None,
    ):
        """Initialize registry.

        Args:
            catalog: Asset catalog.
            collections: Asset collections.
            versions: Version manager.
            audit_logger: Audit logger.
            permission_checker: Permission checker.
        """
        self._catalog = catalog or get_asset_catalog()
        self._collections = collections or get_asset_collections()
        self._versions = versions or get_version_manager()
        self._audit = audit_logger or get_audit_logger()
        self._permissions = permission_checker or PermissionChecker()

    # =========================================================================
    # Asset Registration
    # =========================================================================

    def register(
        self,
        asset_type: AssetType,
        title: str,
        storage_uri: str = "",
        doc_type: str = "",
        author: str = "",
        institution: str = "",
        hospital: str = "",
        language: str = "en",
        collection: str = "",
        tags: list[str] | None = None,
        metadata: dict | None = None,
        chunk_count: int = 0,
        embedding_count: int = 0,
        content_hash: str = "",
        vector_collection: str = "",
        user_id: str = "",
    ) -> AssetMetadata:
        """Register an asset.

        Args:
            asset_type: Type of asset.
            title: Asset title.
            storage_uri: URI where content is stored.
            doc_type: Document type.
            author: Author.
            institution: Institution.
            hospital: Hospital.
            language: Language.
            collection: Collection name.
            tags: Tags.
            metadata: Custom metadata.
            chunk_count: Number of chunks.
            embedding_count: Number of embeddings.
            content_hash: Content hash.
            vector_collection: Vector collection name.
            user_id: User registering.

        Returns:
            Created asset metadata.
        """
        # Generate asset ID
        asset_id = str(uuid.uuid4())

        # Generate checksum
        checksum = self._generate_checksum(asset_id, content_hash)

        # Create metadata
        asset = AssetMetadata(
            asset_id=asset_id,
            asset_type=asset_type,
            title=title,
            version="1.0.0",
            language=language,
            author=author,
            institution=institution,
            hospital=hospital,
            storage_uri=storage_uri,
            collection=collection,
            tags=tags or [],
            custom_metadata=metadata or {},
            chunk_count=chunk_count,
            embedding_count=embedding_count,
            content_hash=content_hash,
            checksum=checksum,
            vector_collection=vector_collection,
            lifecycle_state=LifecycleState.REGISTERED,
        )

        # Register in catalog
        self._catalog.register(asset)

        # Create initial version
        self._versions.create_version(
            asset_id=asset_id,
            version="1.0.0",
            created_by=author,
            content_hash=content_hash,
        )

        # Add to collection if specified
        if collection:
            coll = self._collections.get_by_name(collection)
            if coll:
                self._collections.add_asset(coll.collection_id, asset_id)

        # Audit log
        self._audit.log(
            action=AuditAction.REGISTER,
            asset_id=asset_id,
            user_id=user_id,
            details={"title": title, "asset_type": asset_type.value},
        )

        return asset

    def get(self, asset_id: str) -> AssetMetadata:
        """Get asset metadata.

        Args:
            asset_id: Asset ID.

        Returns:
            Asset metadata.

        Raises:
            AssetNotFoundError: If not found.
        """
        asset = self._catalog.get(asset_id)
        if not asset:
            raise AssetNotFoundError(asset_id)

        return asset

    def update(
        self,
        asset_id: str,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        collection: str | None = None,
        lifecycle_state: LifecycleState | None = None,
        version: str | None = None,
        changelog: str = "",
        user_id: str = "",
    ) -> AssetMetadata:
        """Update asset metadata.

        Args:
            asset_id: Asset ID.
            title: New title.
            description: New description.
            tags: New tags.
            collection: New collection.
            lifecycle_state: New lifecycle state.
            version: New version.
            changelog: Version changelog.
            user_id: User updating.

        Returns:
            Updated asset.

        Raises:
            AssetNotFoundError: If not found.
        """
        asset = self._catalog.get(asset_id)
        if not asset:
            raise AssetNotFoundError(asset_id)

        # Update fields
        if title is not None:
            asset.title = title
        if description is not None:
            asset.description = description
        if tags is not None:
            asset.tags = tags
        if collection is not None:
            asset.collection = collection
        if lifecycle_state is not None:
            asset.lifecycle_state = lifecycle_state

        # Create new version if specified
        if version:
            asset.version = version
            asset.version_major, asset.version_minor, asset.version_patch = self._parse_version(version)
            self._versions.create_version(
                asset_id=asset_id,
                version=version,
                changelog=changelog,
                created_by=user_id,
            )

        # Save asset
        self._catalog.update(asset)

        # Audit log
        self._audit.log(
            action=AuditAction.UPDATE,
            asset_id=asset_id,
            user_id=user_id,
        )

        return asset

    def delete(
        self,
        asset_id: str,
        user_id: str = "",
    ) -> bool:
        """Delete asset.

        Args:
            asset_id: Asset ID.
            user_id: User deleting.

        Returns:
            True if deleted.

        Raises:
            AssetNotFoundError: If not found.
        """
        if not self._catalog.exists(asset_id):
            raise AssetNotFoundError(asset_id)

        # Update lifecycle state to deleted
        asset = self._catalog.get(asset_id)
        asset.lifecycle_state = LifecycleState.DELETED
        self._catalog.update(asset)

        # Audit log
        self._audit.log(
            action=AuditAction.DELETE,
            asset_id=asset_id,
            user_id=user_id,
        )

        return True

    def archive(
        self,
        asset_id: str,
        user_id: str = "",
    ) -> AssetMetadata:
        """Archive asset.

        Args:
            asset_id: Asset ID.
            user_id: User archiving.

        Returns:
            Archived asset.

        Raises:
            AssetNotFoundError: If not found.
        """
        return self.update(
            asset_id=asset_id,
            lifecycle_state=LifecycleState.ARCHIVED,
            user_id=user_id,
        )

    def restore(
        self,
        asset_id: str,
        user_id: str = "",
    ) -> AssetMetadata:
        """Restore archived asset.

        Args:
            asset_id: Asset ID.
            user_id: User restoring.

        Returns:
            Restored asset.

        Raises:
            AssetNotFoundError: If not found.
        """
        return self.update(
            asset_id=asset_id,
            lifecycle_state=LifecycleState.ACTIVE,
            user_id=user_id,
        )

    # =========================================================================
    # Search
    # =========================================================================

    def search(self, query: AssetSearchQuery) -> list[AssetMetadata]:
        """Search assets.

        Args:
            query: Search query.

        Returns:
            List of matching assets.
        """
        results = self._catalog.search(query)

        # Audit log
        self._audit.log(
            action=AuditAction.SEARCH,
            details={"query": query.query, "results": len(results)},
        )

        return results

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_statistics(self) -> AssetStatistics:
        """Get registry statistics.

        Returns:
            Statistics.
        """
        assets = self._catalog.list_all(limit=10000)

        stats = AssetStatistics(
            total_assets=len(assets),
            total_collections=self._collections.count(),
            total_versions=self._versions.total_versions(),
        )

        # Count by type and state
        for asset in assets:
            stats.assets_by_type[asset.asset_type.value] = (
                stats.assets_by_type.get(asset.asset_type.value, 0) + 1
            )

            stats.assets_by_state[asset.lifecycle_state.value] = (
                stats.assets_by_state.get(asset.lifecycle_state.value, 0) + 1
            )

            if asset.language:
                stats.assets_by_language[asset.language] = (
                    stats.assets_by_language.get(asset.language, 0) + 1
                )

            if asset.collection:
                stats.assets_by_collection[asset.collection] = (
                    stats.assets_by_collection.get(asset.collection, 0) + 1
                )

            stats.total_chunks += asset.chunk_count
            stats.total_embeddings += asset.embedding_count

        return stats

    # =========================================================================
    # Helpers
    # =========================================================================

    def _generate_checksum(self, asset_id: str, content_hash: str) -> str:
        """Generate checksum.

        Args:
            asset_id: Asset ID.
            content_hash: Content hash.

        Returns:
            Checksum.
        """
        data = f"{asset_id}:{content_hash}".encode()
        return hashlib.sha256(data).hexdigest()[:16]

    def _parse_version(self, version: str) -> tuple[int, int, int]:
        """Parse version string.

        Args:
            version: Version string.

        Returns:
            Tuple of (major, minor, patch).
        """
        parts = version.split(".")
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return major, minor, patch


# Global registry instance
_global_registry: KnowledgeAssetRegistry | None = None
_registry_lock = threading.Lock()


def get_asset_registry() -> KnowledgeAssetRegistry:
    """Get the global asset registry.

    Returns:
        Global KnowledgeAssetRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = KnowledgeAssetRegistry()
        return _global_registry


def reset_asset_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        _global_registry = None
