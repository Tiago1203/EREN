"""Knowledge Versions for EREN Knowledge Registry.

Manages versions of knowledge entries.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.knowledge.registry_types import KnowledgeVersion

if TYPE_CHECKING:
    pass


class VersionManager:
    """Manager of knowledge versions.

    Tracks version history of knowledge entries.
    """

    def __init__(self):
        """Initialize version manager."""
        self._lock = threading.RLock()
        self._versions: dict[str, list[KnowledgeVersion]] = {}  # knowledge_id -> versions
        self._version_index: dict[str, KnowledgeVersion] = {}  # version_id -> version

    def create_version(
        self,
        knowledge_id: str,
        version: str,
        changelog: str = "",
        created_by: str = "",
        content_hash: str = "",
    ) -> KnowledgeVersion:
        """Create a new version.

        Args:
            knowledge_id: Knowledge ID.
            version: Version string (e.g., "1.0.0").
            changelog: Version changelog.
            created_by: User who created version.
            content_hash: Hash of content at this version.

        Returns:
            Created version.
        """
        with self._lock:
            version_id = str(uuid.uuid4())

            # Parse version components
            version_parts = version.split(".")
            major = int(version_parts[0]) if len(version_parts) > 0 else 1
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            patch = int(version_parts[2]) if len(version_parts) > 2 else 0

            version_obj = KnowledgeVersion(
                version_id=version_id,
                knowledge_id=knowledge_id,
                version=version,
                changelog=changelog,
                created_at=datetime.now(UTC),
                created_by=created_by,
                content_hash=content_hash,
            )

            # Store version
            if knowledge_id not in self._versions:
                self._versions[knowledge_id] = []

            self._versions[knowledge_id].append(version_obj)
            self._version_index[version_id] = version_obj

            return version_obj

    def get(self, version_id: str) -> KnowledgeVersion | None:
        """Get a version by ID.

        Args:
            version_id: Version ID.

        Returns:
            Version or None.
        """
        with self._lock:
            return self._version_index.get(version_id)

    def get_versions(self, knowledge_id: str) -> list[KnowledgeVersion]:
        """Get all versions for knowledge.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            List of versions (sorted by creation date).
        """
        with self._lock:
            versions = self._versions.get(knowledge_id, [])
            return sorted(versions, key=lambda v: v.created_at, reverse=True)

    def get_latest(self, knowledge_id: str) -> KnowledgeVersion | None:
        """Get latest version for knowledge.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            Latest version or None.
        """
        with self._lock:
            versions = self._versions.get(knowledge_id, [])
            if versions:
                return max(versions, key=lambda v: v.created_at)
            return None

    def get_version_by_number(
        self,
        knowledge_id: str,
        version: str,
    ) -> KnowledgeVersion | None:
        """Get version by version number.

        Args:
            knowledge_id: Knowledge ID.
            version: Version string.

        Returns:
            Version or None.
        """
        with self._lock:
            versions = self._versions.get(knowledge_id, [])
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

            # Remove from knowledge versions
            if version.knowledge_id in self._versions:
                versions = self._versions[version.knowledge_id]
                versions = [v for v in versions if v.version_id != version_id]
                self._versions[version.knowledge_id] = versions

            return True

    def count_versions(self, knowledge_id: str) -> int:
        """Count versions for knowledge.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            Number of versions.
        """
        with self._lock:
            return len(self._versions.get(knowledge_id, []))

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
