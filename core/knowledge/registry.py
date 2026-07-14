"""Knowledge Registry for EREN OS.

Main registry class for managing knowledge metadata.
"""

from __future__ import annotations

import hashlib
import threading
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.knowledge.registry_types import (
    KnowledgeEntry,
    KnowledgeStatus,
    PermissionLevel,
    RegistrySearchQuery,
    RegistryStatistics,
    AuditAction,
)
from core.knowledge.registry_exceptions import (
    KnowledgeNotFoundError,
    DocumentNotFoundError,
    DuplicateKnowledgeError,
    PermissionDeniedError,
)
from core.knowledge.catalog import KnowledgeCatalog, get_knowledge_catalog
from core.knowledge.collections import KnowledgeCollections, get_knowledge_collections
from core.knowledge.versions import VersionManager, get_version_manager
from core.knowledge.permissions import AuditLogger, PermissionChecker, get_audit_logger

if TYPE_CHECKING:
    pass


class KnowledgeRegistry:
    """Knowledge Registry.

    Manages metadata catalog of all knowledge.
    NEVER stores documents, embeddings, vectors, or files.
    ONLY manages metadata.

    Philosophy:
        The Registry doesn't store:
        - documents
        - embeddings
        - vectors
        - files

        It ONLY stores:
        - metadata
        - catalog
        - collections
        - versions
        - permissions
        - audit logs
    """

    def __init__(
        self,
        catalog: KnowledgeCatalog | None = None,
        collections: KnowledgeCollections | None = None,
        versions: VersionManager | None = None,
        audit_logger: AuditLogger | None = None,
        permission_checker: PermissionChecker | None = None,
    ):
        """Initialize registry.

        Args:
            catalog: Knowledge catalog.
            collections: Knowledge collections.
            versions: Version manager.
            audit_logger: Audit logger.
            permission_checker: Permission checker.
        """
        self._catalog = catalog or get_knowledge_catalog()
        self._collections = collections or get_knowledge_collections()
        self._versions = versions or get_version_manager()
        self._audit = audit_logger or get_audit_logger()
        self._permissions = permission_checker or PermissionChecker()

    # =========================================================================
    # Knowledge Registration
    # =========================================================================

    def register(
        self,
        document_id: str,
        title: str,
        doc_type: str = "",
        category: str = "",
        medical_specialty: str = "",
        author: str = "",
        institution: str = "",
        language: str = "en",
        collection: str = "",
        tags: list[str] | None = None,
        metadata: dict | None = None,
        chunk_count: int = 0,
        embedding_count: int = 0,
        content_hash: str = "",
        user_id: str = "",
    ) -> KnowledgeEntry:
        """Register knowledge.

        Args:
            document_id: Document ID.
            title: Knowledge title.
            doc_type: Document type.
            category: Category.
            medical_specialty: Medical specialty.
            author: Author.
            institution: Institution.
            language: Language.
            collection: Collection name.
            tags: Tags.
            metadata: Custom metadata.
            chunk_count: Number of chunks.
            embedding_count: Number of embeddings.
            content_hash: Content hash.
            user_id: User registering.

        Returns:
            Created knowledge entry.
        """
        # Check for duplicate document
        existing = self._catalog.get_by_document(document_id)
        if existing:
            raise DuplicateKnowledgeError(existing.knowledge_id)

        # Generate IDs
        knowledge_id = str(uuid.uuid4())
        checksum = self._generate_checksum(knowledge_id, content_hash)

        # Create entry
        entry = KnowledgeEntry(
            knowledge_id=knowledge_id,
            document_id=document_id,
            title=title,
            doc_type=doc_type,
            category=category,
            medical_specialty=medical_specialty,
            author=author,
            institution=institution,
            language=language,
            collection=collection,
            tags=tags or [],
            custom_metadata=metadata or {},
            chunk_count=chunk_count,
            embedding_count=embedding_count,
            content_hash=content_hash,
            checksum=checksum,
            status=KnowledgeStatus.REGISTERED,
        )

        # Register in catalog
        self._catalog.register(entry)

        # Create initial version
        self._versions.create_version(
            knowledge_id=knowledge_id,
            version="1.0.0",
            created_by=author,
            content_hash=content_hash,
        )

        # Add to collection if specified
        if collection:
            coll = self._collections.get_by_name(collection)
            if coll:
                self._collections.add_knowledge(coll.collection_id, knowledge_id)

        # Audit log
        self._audit.log(
            action=AuditAction.REGISTER,
            knowledge_id=knowledge_id,
            user_id=user_id,
            details={"title": title, "document_id": document_id},
        )

        return entry

    def get(self, knowledge_id: str) -> KnowledgeEntry:
        """Get knowledge entry.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            Knowledge entry.

        Raises:
            KnowledgeNotFoundError: If not found.
        """
        entry = self._catalog.get(knowledge_id)
        if not entry:
            raise KnowledgeNotFoundError(knowledge_id)

        return entry

    def update(
        self,
        knowledge_id: str,
        title: str | None = None,
        description: str | None = None,
        medical_specialty: str | None = None,
        tags: list[str] | None = None,
        collection: str | None = None,
        status: KnowledgeStatus | None = None,
        version: str | None = None,
        changelog: str = "",
        user_id: str = "",
    ) -> KnowledgeEntry:
        """Update knowledge entry.

        Args:
            knowledge_id: Knowledge ID.
            title: New title.
            description: New description.
            medical_specialty: New specialty.
            tags: New tags.
            collection: New collection.
            status: New status.
            version: New version.
            changelog: Version changelog.
            user_id: User updating.

        Returns:
            Updated entry.

        Raises:
            KnowledgeNotFoundError: If not found.
        """
        entry = self._catalog.get(knowledge_id)
        if not entry:
            raise KnowledgeNotFoundError(knowledge_id)

        # Update fields
        if title is not None:
            entry.title = title
        if description is not None:
            entry.description = description
        if medical_specialty is not None:
            entry.medical_specialty = medical_specialty
        if tags is not None:
            entry.tags = tags
        if status is not None:
            entry.status = status
        if collection is not None:
            entry.collection = collection

        # Create new version if specified
        if version:
            entry.version = version
            entry.version_major, entry.version_minor, entry.version_patch = self._parse_version(version)
            self._versions.create_version(
                knowledge_id=knowledge_id,
                version=version,
                changelog=changelog,
                created_by=user_id,
            )

        # Save entry
        self._catalog.update(entry)

        # Audit log
        self._audit.log(
            action=AuditAction.UPDATE,
            knowledge_id=knowledge_id,
            user_id=user_id,
        )

        return entry

    def delete(
        self,
        knowledge_id: str,
        user_id: str = "",
    ) -> bool:
        """Delete knowledge entry.

        Args:
            knowledge_id: Knowledge ID.
            user_id: User deleting.

        Returns:
            True if deleted.

        Raises:
            KnowledgeNotFoundError: If not found.
        """
        if not self._catalog.exists(knowledge_id):
            raise KnowledgeNotFoundError(knowledge_id)

        # Update status to deleted
        entry = self._catalog.get(knowledge_id)
        entry.status = KnowledgeStatus.DELETED
        self._catalog.update(entry)

        # Audit log
        self._audit.log(
            action=AuditAction.DELETE,
            knowledge_id=knowledge_id,
            user_id=user_id,
        )

        return True

    # =========================================================================
    # Search
    # =========================================================================

    def search(self, query: RegistrySearchQuery) -> list[KnowledgeEntry]:
        """Search knowledge entries.

        Args:
            query: Search query.

        Returns:
            List of matching entries.
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

    def get_statistics(self) -> RegistryStatistics:
        """Get registry statistics.

        Returns:
            Statistics.
        """
        entries = self._catalog.list_all(limit=10000)

        stats = RegistryStatistics(
            total_entries=len(entries),
            total_collections=self._collections.count(),
            total_versions=self._versions.total_versions(),
        )

        # Count by status
        for entry in entries:
            stats.entries_by_status[entry.status.value] = (
                stats.entries_by_status.get(entry.status.value, 0) + 1
            )

            if entry.category:
                stats.entries_by_category[entry.category] = (
                    stats.entries_by_category.get(entry.category, 0) + 1
                )

            if entry.medical_specialty:
                stats.entries_by_specialty[entry.medical_specialty] = (
                    stats.entries_by_specialty.get(entry.medical_specialty, 0) + 1
                )

            if entry.language:
                stats.entries_by_language[entry.language] = (
                    stats.entries_by_language.get(entry.language, 0) + 1
                )

            if entry.collection:
                stats.entries_by_collection[entry.collection] = (
                    stats.entries_by_collection.get(entry.collection, 0) + 1
                )

            stats.total_chunks += entry.chunk_count
            stats.total_embeddings += entry.embedding_count

        return stats

    # =========================================================================
    # Helpers
    # =========================================================================

    def _generate_checksum(self, knowledge_id: str, content_hash: str) -> str:
        """Generate checksum.

        Args:
            knowledge_id: Knowledge ID.
            content_hash: Content hash.

        Returns:
            Checksum.
        """
        data = f"{knowledge_id}:{content_hash}".encode()
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
_global_registry: KnowledgeRegistry | None = None
_registry_lock = threading.Lock()


def get_knowledge_registry() -> KnowledgeRegistry:
    """Get the global knowledge registry.

    Returns:
        Global KnowledgeRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = KnowledgeRegistry()
        return _global_registry


def reset_knowledge_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        _global_registry = None
