"""Asset Collections for EREN Knowledge Asset Registry.

Manages collections of knowledge assets.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_3.knowledge_assets.types import AssetCollection

if TYPE_CHECKING:
    pass


class AssetCollections:
    """Manager of asset collections.

    Organizes assets into collections.
    """

    def __init__(self):
        """Initialize collections manager."""
        self._lock = threading.RLock()
        self._collections: dict[str, AssetCollection] = {}

    def create(
        self,
        name: str,
        description: str = "",
        owner: str = "",
        parent_collection: str = "",
        tags: list[str] | None = None,
        is_public: bool = False,
    ) -> AssetCollection:
        """Create a new collection.

        Args:
            name: Collection name.
            description: Collection description.
            owner: Collection owner.
            parent_collection: Parent collection ID.
            tags: Collection tags.
            is_public: Whether collection is public.

        Returns:
            Created collection.
        """
        with self._lock:
            collection_id = str(uuid.uuid4())

            collection = AssetCollection(
                collection_id=collection_id,
                name=name,
                description=description,
                owner=owner,
                parent_collection=parent_collection,
                tags=tags or [],
                is_public=is_public,
            )

            self._collections[collection_id] = collection
            return collection

    def get(self, collection_id: str) -> AssetCollection | None:
        """Get a collection.

        Args:
            collection_id: Collection ID.

        Returns:
            Collection or None.
        """
        with self._lock:
            return self._collections.get(collection_id)

    def get_by_name(self, name: str) -> AssetCollection | None:
        """Get collection by name.

        Args:
            name: Collection name.

        Returns:
            Collection or None.
        """
        with self._lock:
            for collection in self._collections.values():
                if collection.name == name:
                    return collection
            return None

    def update(self, collection: AssetCollection) -> bool:
        """Update a collection.

        Args:
            collection: Updated collection.

        Returns:
            True if updated.
        """
        with self._lock:
            if collection.collection_id not in self._collections:
                return False

            collection.updated_at = datetime.now(UTC)
            self._collections[collection.collection_id] = collection
            return True

    def delete(self, collection_id: str) -> bool:
        """Delete a collection.

        Args:
            collection_id: Collection ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            if collection_id not in self._collections:
                return False

            del self._collections[collection_id]
            return True

    def add_asset(
        self,
        collection_id: str,
        asset_id: str,
    ) -> bool:
        """Add asset to collection.

        Args:
            collection_id: Collection ID.
            asset_id: Asset ID.

        Returns:
            True if added.
        """
        with self._lock:
            collection = self._collections.get(collection_id)
            if not collection:
                return False

            if asset_id not in collection.asset_ids:
                collection.asset_ids.append(asset_id)
                collection.updated_at = datetime.now(UTC)

            return True

    def remove_asset(
        self,
        collection_id: str,
        asset_id: str,
    ) -> bool:
        """Remove asset from collection.

        Args:
            collection_id: Collection ID.
            asset_id: Asset ID.

        Returns:
            True if removed.
        """
        with self._lock:
            collection = self._collections.get(collection_id)
            if not collection:
                return False

            if asset_id in collection.asset_ids:
                collection.asset_ids.remove(asset_id)
                collection.updated_at = datetime.now(UTC)

            return True

    def list_all(self) -> list[AssetCollection]:
        """List all collections.

        Returns:
            List of collections.
        """
        with self._lock:
            return sorted(
                self._collections.values(),
                key=lambda c: c.name,
            )

    def list_public(self) -> list[AssetCollection]:
        """List public collections.

        Returns:
            List of public collections.
        """
        with self._lock:
            return [
                c for c in self._collections.values()
                if c.is_public
            ]

    def count(self) -> int:
        """Count collections.

        Returns:
            Number of collections.
        """
        with self._lock:
            return len(self._collections)

    def clear(self) -> None:
        """Clear all collections."""
        with self._lock:
            self._collections.clear()


# Global collections instance
_global_collections: AssetCollections | None = None
_collections_lock = threading.Lock()


def get_asset_collections() -> AssetCollections:
    """Get the global asset collections manager.

    Returns:
        Global AssetCollections instance.
    """
    global _global_collections
    with _collections_lock:
        if _global_collections is None:
            _global_collections = AssetCollections()
        return _global_collections


def reset_asset_collections() -> None:
    """Reset the global collections manager."""
    global _global_collections
    with _collections_lock:
        if _global_collections is not None:
            _global_collections.clear()
        _global_collections = None
