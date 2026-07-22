"""Asset Version Manager for EREN Knowledge Asset Registry.

Manages versions of knowledge assets.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.domain.knowledge_assets.types import AssetVersion

if TYPE_CHECKING:
    pass


class VersionManager:
    """Manager of asset versions.

    Tracks version history of assets.
    """

    def __init__(self):
        """Initialize version manager."""
        self._lock = threading.RLock()
        self._versions: dict[str, list[AssetVersion]] = {}  # asset_id -> versions
        self._version_index: dict[str, AssetVersion] = {}  # version_id -> version

    def create_version(
        self,
        asset_id: str,
        version: str,
        changelog: str = "",
        created_by: str = "",
        content_hash: str = "",
    ) -> AssetVersion:
        """Create a new version.

        Args:
            asset_id: Asset ID.
            version: Version string (e.g., "1.0.0").
            changelog: Version changelog.
            created_by: User who created version.
            content_hash: Hash of content at this version.

        Returns:
            Created version.
        """
        with self._lock:
            version_id = str(uuid.uuid4())

            version_obj = AssetVersion(
                version_id=version_id,
                asset_id=asset_id,
                version=version,
                changelog=changelog,
                created_at=datetime.now(UTC),
                created_by=created_by,
                content_hash=content_hash,
            )

            # Store version
            if asset_id not in self._versions:
                self._versions[asset_id] = []

            self._versions[asset_id].append(version_obj)
            self._version_index[version_id] = version_obj

            return version_obj

    def get(self, version_id: str) -> AssetVersion | None:
        """Get a version by ID.

        Args:
            version_id: Version ID.

        Returns:
            Version or None.
        """
        with self._lock:
            return self._version_index.get(version_id)

    def get_versions(self, asset_id: str) -> list[AssetVersion]:
        """Get all versions for asset.

        Args:
            asset_id: Asset ID.

        Returns:
            List of versions (sorted by creation date).
        """
        with self._lock:
            versions = self._versions.get(asset_id, [])
            return sorted(versions, key=lambda v: v.created_at, reverse=True)

    def get_latest(self, asset_id: str) -> AssetVersion | None:
        """Get latest version for asset.

        Args:
            asset_id: Asset ID.

        Returns:
            Latest version or None.
        """
        with self._lock:
            versions = self._versions.get(asset_id, [])
            if versions:
                return max(versions, key=lambda v: v.created_at)
            return None

    def get_version_by_number(
        self,
        asset_id: str,
        version: str,
    ) -> AssetVersion | None:
        """Get version by version number.

        Args:
            asset_id: Asset ID.
            version: Version string.

        Returns:
            Version or None.
        """
        with self._lock:
            versions = self._versions.get(asset_id, [])
            for v in versions:
                if v.version == version:
                    return v
            return None

    def delete_version(self, version_id: str) -> bool:
        """Delete a version.

        Args:
            version_id: Version ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            version = self._version_index.get(version_id)
            if not version:
                return False

            # Remove from index
            del self._version_index[version_id]

            # Remove from asset versions
            if version.asset_id in self._versions:
                versions = self._versions[version.asset_id]
                versions = [v for v in versions if v.version_id != version_id]
                self._versions[version.asset_id] = versions

            return True

    def count_versions(self, asset_id: str) -> int:
        """Count versions for asset.

        Args:
            asset_id: Asset ID.

        Returns:
            Number of versions.
        """
        with self._lock:
            return len(self._versions.get(asset_id, []))

    def total_versions(self) -> int:
        """Count total versions.

        Returns:
            Total number of versions.
        """
        with self._lock:
            return len(self._version_index)

    def clear(self) -> None:
        """Clear all versions."""
        with self._lock:
            self._versions.clear()
            self._version_index.clear()


# Global version manager instance
_global_version_manager: VersionManager | None = None
_version_lock = threading.Lock()


def get_version_manager() -> VersionManager:
    """Get the global version manager.

    Returns:
        Global VersionManager instance.
    """
    global _global_version_manager
    with _version_lock:
        if _global_version_manager is None:
            _global_version_manager = VersionManager()
        return _global_version_manager


def reset_version_manager() -> None:
    """Reset the global version manager."""
    global _global_version_manager
    with _version_lock:
        if _global_version_manager is not None:
            _global_version_manager.clear()
        _global_version_manager = None
