"""Asset Catalog for EREN Knowledge Asset Registry.

Manages the catalog of knowledge assets.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.domain.knowledge_assets.types import (
    AssetMetadata,
    AssetSearchQuery,
)

if TYPE_CHECKING:
    pass


class AssetCatalog:
    """Catalog of knowledge assets.

    Manages the metadata catalog of all registered assets.
    """

    def __init__(self):
        """Initialize catalog."""
        self._lock = threading.RLock()
        self._assets: dict[str, AssetMetadata] = {}
        self._uri_index: dict[str, str] = {}  # storage_uri -> asset_id

    def register(self, asset: AssetMetadata) -> str:
        """Register an asset.

        Args:
            asset: Asset metadata to register.

        Returns:
            Asset ID.
        """
        with self._lock:
            # Generate ID if not provided
            if not asset.asset_id:
                asset.asset_id = str(uuid.uuid4())

            # Check for duplicates
            if asset.asset_id in self._assets:
                raise ValueError(f"Asset already exists: {asset.asset_id}")

            # Index by storage URI if provided
            if asset.storage_uri:
                self._uri_index[asset.storage_uri] = asset.asset_id

            # Store asset
            self._assets[asset.asset_id] = asset

            return asset.asset_id

    def get(self, asset_id: str) -> AssetMetadata | None:
        """Get an asset.

        Args:
            asset_id: Asset ID.

        Returns:
            Asset metadata or None.
        """
        with self._lock:
            return self._assets.get(asset_id)

    def get_by_uri(self, storage_uri: str) -> AssetMetadata | None:
        """Get asset by storage URI.

        Args:
            storage_uri: Storage URI.

        Returns:
            Asset metadata or None.
        """
        with self._lock:
            asset_id = self._uri_index.get(storage_uri)
            if asset_id:
                return self._assets.get(asset_id)
            return None

    def update(self, asset: AssetMetadata) -> bool:
        """Update an asset.

        Args:
            asset: Updated asset metadata.

        Returns:
            True if updated.
        """
        with self._lock:
            if asset.asset_id not in self._assets:
                return False

            asset.updated_at = datetime.now(UTC)
            self._assets[asset.asset_id] = asset
            return True

    def delete(self, asset_id: str) -> bool:
        """Delete an asset.

        Args:
            asset_id: Asset ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            if asset_id not in self._assets:
                return False

            asset = self._assets[asset_id]
            if asset.storage_uri:
                del self._uri_index[asset.storage_uri]
            del self._assets[asset_id]
            return True

    def search(self, query: AssetSearchQuery) -> list[AssetMetadata]:
        """Search assets.

        Args:
            query: Search query.

        Returns:
            List of matching assets.
        """
        with self._lock:
            results = []

            for asset in self._assets.values():
                # Apply filters
                if query.asset_ids and asset.asset_id not in query.asset_ids:
                    continue

                if query.asset_types and asset.asset_type not in query.asset_types:
                    continue

                if query.collections and asset.collection not in query.collections:
                    continue

                if query.languages and asset.language not in query.languages:
                    continue

                if query.tags and not any(t in asset.tags for t in query.tags):
                    continue

                if query.lifecycle_states and asset.lifecycle_state not in query.lifecycle_states:
                    continue

                if query.authors and asset.author not in query.authors:
                    continue

                if query.institutions and asset.institution not in query.institutions:
                    continue

                # Date filters
                if query.date_from and asset.created_at < query.date_from:
                    continue

                if query.date_to and asset.created_at > query.date_to:
                    continue

                results.append(asset)

            # Apply pagination
            results = results[query.offset:query.offset + query.limit]

            return results

    def list_all(self, limit: int = 100, offset: int = 0) -> list[AssetMetadata]:
        """List all assets.

        Args:
            limit: Maximum number of assets.
            offset: Offset for pagination.

        Returns:
            List of assets.
        """
        with self._lock:
            assets = sorted(
                self._assets.values(),
                key=lambda a: a.created_at,
                reverse=True,
            )
            return assets[offset:offset + limit]

    def count(self) -> int:
        """Count total assets.

        Returns:
            Total number of assets.
        """
        with self._lock:
            return len(self._assets)

    def exists(self, asset_id: str) -> bool:
        """Check if asset exists.

        Args:
            asset_id: Asset ID.

        Returns:
            True if exists.
        """
        with self._lock:
            return asset_id in self._assets

    def clear(self) -> None:
        """Clear all assets."""
        with self._lock:
            self._assets.clear()
            self._uri_index.clear()


# Global catalog instance
_global_catalog: AssetCatalog | None = None
_catalog_lock = threading.Lock()


def get_asset_catalog() -> AssetCatalog:
    """Get the global asset catalog.

    Returns:
        Global AssetCatalog instance.
    """
    global _global_catalog
    with _catalog_lock:
        if _global_catalog is None:
            _global_catalog = AssetCatalog()
        return _global_catalog


def reset_asset_catalog() -> None:
    """Reset the global catalog."""
    global _global_catalog
    with _catalog_lock:
        if _global_catalog is not None:
            _global_catalog.clear()
        _global_catalog = None
