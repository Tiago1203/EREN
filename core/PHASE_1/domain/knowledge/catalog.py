"""Knowledge Catalog for EREN Knowledge Registry.

Manages the catalog of knowledge entries.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.domain.knowledge.registry_types import (
    KnowledgeEntry,
    RegistrySearchQuery,
)

if TYPE_CHECKING:
    pass


class KnowledgeCatalog:
    """Catalog of knowledge entries.

    Manages the metadata catalog of all registered knowledge.
    """

    def __init__(self):
        """Initialize catalog."""
        self._lock = threading.RLock()
        self._entries: dict[str, KnowledgeEntry] = {}
        self._document_index: dict[str, str] = {}  # document_id -> knowledge_id

    def register(self, entry: KnowledgeEntry) -> str:
        """Register a knowledge entry.

        Args:
            entry: Knowledge entry to register.

        Returns:
            Knowledge ID.
        """
        with self._lock:
            # Generate ID if not provided
            if not entry.knowledge_id:
                entry.knowledge_id = str(uuid.uuid4())

            # Check for duplicates
            if entry.knowledge_id in self._entries:
                raise ValueError(f"Knowledge entry already exists: {entry.knowledge_id}")

            # Index by document_id
            self._document_index[entry.document_id] = entry.knowledge_id

            # Store entry
            self._entries[entry.knowledge_id] = entry

            return entry.knowledge_id

    def get(self, knowledge_id: str) -> KnowledgeEntry | None:
        """Get a knowledge entry.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            Knowledge entry or None.
        """
        with self._lock:
            return self._entries.get(knowledge_id)

    def get_by_document(self, document_id: str) -> KnowledgeEntry | None:
        """Get entry by document ID.

        Args:
            document_id: Document ID.

        Returns:
            Knowledge entry or None.
        """
        with self._lock:
            knowledge_id = self._document_index.get(document_id)
            if knowledge_id:
                return self._entries.get(knowledge_id)
            return None

    def update(self, entry: KnowledgeEntry) -> bool:
        """Update a knowledge entry.

        Args:
            entry: Updated knowledge entry.

        Returns:
            True if updated.
        """
        with self._lock:
            if entry.knowledge_id not in self._entries:
                return False

            entry.updated_at = datetime.now(UTC)
            self._entries[entry.knowledge_id] = entry
            return True

    def delete(self, knowledge_id: str) -> bool:
        """Delete a knowledge entry.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            if knowledge_id not in self._entries:
                return False

            entry = self._entries[knowledge_id]
            del self._document_index[entry.document_id]
            del self._entries[knowledge_id]
            return True

    def search(self, query: RegistrySearchQuery) -> list[KnowledgeEntry]:
        """Search knowledge entries.

        Args:
            query: Search query.

        Returns:
            List of matching entries.
        """
        with self._lock:
            results = []

            for entry in self._entries.values():
                # Apply filters
                if query.knowledge_ids and entry.knowledge_id not in query.knowledge_ids:
                    continue

                if query.document_ids and entry.document_id not in query.document_ids:
                    continue

                if query.categories and entry.category not in query.categories:
                    continue

                if query.specialties and entry.medical_specialty not in query.specialties:
                    continue

                if query.collections and entry.collection not in query.collections:
                    continue

                if query.languages and entry.language not in query.languages:
                    continue

                if query.tags and not any(t in entry.tags for t in query.tags):
                    continue

                if query.statuses and entry.status not in query.statuses:
                    continue

                if query.authors and entry.author not in query.authors:
                    continue

                if query.institutions and entry.institution not in query.institutions:
                    continue

                # Date filters
                if query.date_from and entry.created_at < query.date_from:
                    continue

                if query.date_to and entry.created_at > query.date_to:
                    continue

                results.append(entry)

            # Apply pagination
            results = results[query.offset:query.offset + query.limit]

            return results

    def list_all(self, limit: int = 100, offset: int = 0) -> list[KnowledgeEntry]:
        """List all knowledge entries.

        Args:
            limit: Maximum number of entries.
            offset: Offset for pagination.

        Returns:
            List of entries.
        """
        with self._lock:
            entries = sorted(
                self._entries.values(),
                key=lambda e: e.created_at,
                reverse=True,
            )
            return entries[offset:offset + limit]

    def count(self) -> int:
        """Count total entries.

        Returns:
            Total number of entries.
        """
        with self._lock:
            return len(self._entries)

    def exists(self, knowledge_id: str) -> bool:
        """Check if entry exists.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            True if exists.
        """
        with self._lock:
            return knowledge_id in self._entries

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries.clear()
            self._document_index.clear()


# Global catalog instance
_global_catalog: KnowledgeCatalog | None = None
_catalog_lock = threading.Lock()


def get_knowledge_catalog() -> KnowledgeCatalog:
    """Get the global knowledge catalog.

    Returns:
        Global KnowledgeCatalog instance.
    """
    global _global_catalog
    with _catalog_lock:
        if _global_catalog is None:
            _global_catalog = KnowledgeCatalog()
        return _global_catalog


def reset_knowledge_catalog() -> None:
    """Reset the global catalog."""
    global _global_catalog
    with _catalog_lock:
        if _global_catalog is not None:
            _global_catalog.clear()
        _global_catalog = None
