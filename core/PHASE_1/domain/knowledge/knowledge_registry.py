"""Knowledge Registry for the Cognitive Knowledge Engine.

Registry for managing knowledge sources.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from .knowledge_types import (
    KnowledgeSource,
    KnowledgeSourceStatus,
    KnowledgeSourceType,
    QueryType,
    SourceMetadata,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Knowledge Registry
# =============================================================================


class KnowledgeRegistry:
    """Registry for knowledge sources.

    Similar to CapabilityRegistry but for knowledge sources.
    Sources register themselves and the registry manages them.
    """

    def __init__(self) -> None:
        """Initialize the registry."""
        self._sources: dict[str, KnowledgeSource] = {}
        self._metadata: dict[str, SourceMetadata] = {}
        self._status: dict[str, KnowledgeSourceStatus] = {}
        self._lock = threading.RLock()
        self._subscribers: list[Callable] = []

    def register(self, source: KnowledgeSource) -> None:
        """Register a knowledge source.

        Args:
            source: The source to register.
        """
        with self._lock:
            self._sources[source.source_id] = source
            self._status[source.source_id] = KnowledgeSourceStatus.ACTIVE

            # Create metadata
            self._metadata[source.source_id] = SourceMetadata(
                source_id=source.source_id,
                source_type=source.source_type,
                name=source.name,
                description=f"Knowledge source: {source.name}",
                category=self._get_category(source.source_type),
                status=KnowledgeSourceStatus.ACTIVE,
                capabilities=[],
            )

        self._notify_subscribers("registered", source.source_id)

    def unregister(self, source_id: str) -> bool:
        """Unregister a knowledge source.

        Args:
            source_id: The source ID to unregister.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if source_id in self._sources:
                del self._sources[source_id]
                self._metadata.pop(source_id, None)
                self._status.pop(source_id, None)
                self._notify_subscribers("unregistered", source_id)
                return True
            return False

    def get(self, source_id: str) -> KnowledgeSource | None:
        """Get a source by ID.

        Args:
            source_id: The source ID.

        Returns:
            The source or None.
        """
        with self._lock:
            return self._sources.get(source_id)

    def get_all_sources(self) -> list[KnowledgeSource]:
        """Get all registered sources.

        Returns:
            List of all sources.
        """
        with self._lock:
            return list(self._sources.values())

    def get_active_sources(self) -> list[KnowledgeSource]:
        """Get all active sources.

        Returns:
            List of active sources.
        """
        with self._lock:
            return [
                s for s in self._sources.values()
                if self._status.get(s.source_id) == KnowledgeSourceStatus.ACTIVE
            ]

    def get_by_type(self, source_type: KnowledgeSourceType) -> list[KnowledgeSource]:
        """Get sources by type.

        Args:
            source_type: The source type.

        Returns:
            List of sources of this type.
        """
        with self._lock:
            return [s for s in self._sources.values() if s.source_type == source_type]

    def get_by_query_type(self, query_type: QueryType) -> list[KnowledgeSource]:
        """Get sources that support a query type.

        Args:
            query_type: The query type.

        Returns:
            List of supporting sources.
        """
        with self._lock:
            return [
                s for s in self._sources.values()
                if s.supports_query_type(query_type)
            ]

    def list_sources(self) -> list[str]:
        """List all registered source IDs.

        Returns:
            List of source IDs.
        """
        with self._lock:
            return list(self._sources.keys())

    def get_metadata(self, source_id: str) -> SourceMetadata | None:
        """Get metadata for a source.

        Args:
            source_id: The source ID.

        Returns:
            The metadata or None.
        """
        with self._lock:
            return self._metadata.get(source_id)

    def get_all_metadata(self) -> list[SourceMetadata]:
        """Get all source metadata.

        Returns:
            List of all metadata.
        """
        with self._lock:
            return list(self._metadata.values())

    def update_status(
        self,
        source_id: str,
        status: KnowledgeSourceStatus,
    ) -> bool:
        """Update source status.

        Args:
            source_id: The source ID.
            status: New status.

        Returns:
            True if updated.
        """
        with self._lock:
            if source_id in self._sources:
                self._status[source_id] = status
                if source_id in self._metadata:
                    self._metadata[source_id] = SourceMetadata(
                        source_id=self._metadata[source_id].source_id,
                        source_type=self._metadata[source_id].source_type,
                        name=self._metadata[source_id].name,
                        description=self._metadata[source_id].description,
                        category=self._metadata[source_id].category,
                        status=status,
                        version=self._metadata[source_id].version,
                        last_updated=self._metadata[source_id].last_updated,
                        capabilities=self._metadata[source_id].capabilities,
                        metadata=self._metadata[source_id].metadata,
                    )
                self._notify_subscribers("status_updated", source_id, status)
                return True
            return False

    def count(self) -> int:
        """Count registered sources.

        Returns:
            Number of sources.
        """
        with self._lock:
            return len(self._sources)

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to registry changes.

        Args:
            callback: Function to call on changes.
        """
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from changes.

        Args:
            callback: The callback to remove.
        """
        self._subscribers = [s for s in self._subscribers if s != callback]

    def _notify_subscribers(self, event: str, *args) -> None:
        """Notify subscribers of changes."""
        for callback in self._subscribers:
            try:
                callback(event, *args)
            except Exception:
                pass

    @staticmethod
    def _get_category(source_type: KnowledgeSourceType) -> str:
        """Get category for source type."""
        clinical_types = {
            KnowledgeSourceType.CLINICAL_DATABASE,
            KnowledgeSourceType.HOSPITAL_PROTOCOLS,
        }
        technical_types = {
            KnowledgeSourceType.EQUIPMENT_MANUALS,
            KnowledgeSourceType.TECHNICAL_DOCUMENTATION,
            KnowledgeSourceType.PROCEDURES,
        }
        regulatory_types = {
            KnowledgeSourceType.REGULATORY_STANDARDS,
        }
        scientific_types = {
            KnowledgeSourceType.SCIENTIFIC_LITERATURE,
        }

        if source_type in clinical_types:
            return "clinical"
        elif source_type in technical_types:
            return "technical"
        elif source_type in regulatory_types:
            return "regulatory"
        elif source_type in scientific_types:
            return "scientific"
        else:
            return "operational"
