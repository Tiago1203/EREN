"""Document registry for EREN Knowledge Ingestion Pipeline.

Tracks ingested documents.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import TYPE_CHECKING

from core.ingestion.types import IngestedDocument, IngestionStatistics

if TYPE_CHECKING:
    pass


class DocumentRegistry:
    """Registry for ingested documents.

    Tracks document metadata and ingestion results.
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize registry.

        Args:
            storage_path: Path to store registry data.
        """
        self._lock = threading.RLock()
        self._documents: dict[str, IngestedDocument] = {}
        self._storage_path = Path(storage_path) if storage_path else None

    def register(self, document: IngestedDocument) -> None:
        """Register an ingested document.

        Args:
            document: Ingested document.
        """
        with self._lock:
            self._documents[document.document_id] = document

            if self._storage_path:
                self._save_to_disk(document)

    def get(self, document_id: str) -> IngestedDocument | None:
        """Get a document by ID.

        Args:
            document_id: Document ID.

        Returns:
            Ingested document or None.
        """
        with self._lock:
            return self._documents.get(document_id)

    def list(self, limit: int = 100) -> list[IngestedDocument]:
        """List all documents.

        Args:
            limit: Maximum number of documents.

        Returns:
            List of documents.
        """
        with self._lock:
            documents = sorted(
                self._documents.values(),
                key=lambda d: d.metadata.created_at,
                reverse=True,
            )
            return documents[:limit]

    def list_by_source(self, source: str) -> list[IngestedDocument]:
        """List documents by source.

        Args:
            source: Source type.

        Returns:
            List of documents.
        """
        with self._lock:
            return [
                d for d in self._documents.values()
                if d.metadata.source_type.value == source
            ]

    def list_by_status(self, status: str) -> list[IngestedDocument]:
        """List documents by status.

        Args:
            status: Ingestion status.

        Returns:
            List of documents.
        """
        with self._lock:
            return [
                d for d in self._documents.values()
                if d.status.value == status
            ]

    def delete(self, document_id: str) -> bool:
        """Delete a document.

        Args:
            document_id: Document ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            if document_id in self._documents:
                del self._documents[document_id]

                if self._storage_path:
                    self._delete_from_disk(document_id)

                return True
            return False

    def exists(self, document_id: str) -> bool:
        """Check if document exists.

        Args:
            document_id: Document ID.

        Returns:
            True if exists.
        """
        with self._lock:
            return document_id in self._documents

    def count(self) -> int:
        """Count documents.

        Returns:
            Number of documents.
        """
        with self._lock:
            return len(self._documents)

    def get_statistics(self) -> IngestionStatistics:
        """Get registry statistics.

        Returns:
            Statistics.
        """
        with self._lock:
            stats = IngestionStatistics(
                total_documents=len(self._documents),
            )

            for doc in self._documents.values():
                if doc.is_success:
                    stats.successful_documents += 1
                elif doc.is_partial:
                    stats.partial_documents += 1
                else:
                    stats.failed_documents += 1

                stats.total_chunks += doc.chunks_created

                # By type
                type_key = doc.original_type.value
                stats.by_type[type_key] = stats.by_type.get(type_key, 0) + 1

                # By source
                source_key = doc.metadata.source_type.value
                stats.by_source[source_key] = stats.by_source.get(source_key, 0) + 1

            if stats.total_documents > 0:
                stats.average_chunks_per_document = (
                    stats.total_chunks / stats.total_documents
                )

            return stats

    def clear(self) -> None:
        """Clear all documents."""
        with self._lock:
            self._documents.clear()

    def _save_to_disk(self, document: IngestedDocument) -> None:
        """Save document to disk.

        Args:
            document: Document to save.
        """
        if not self._storage_path:
            return

        try:
            self._storage_path.mkdir(parents=True, exist_ok=True)
            file_path = self._storage_path / f"{document.document_id}.json"

            with open(file_path, "w") as f:
                json.dump(document.to_dict(), f, indent=2)

        except Exception:
            pass  # Silently fail on disk errors

    def _delete_from_disk(self, document_id: str) -> None:
        """Delete document from disk.

        Args:
            document_id: Document ID.
        """
        if not self._storage_path:
            return

        try:
            file_path = self._storage_path / f"{document_id}.json"
            if file_path.exists():
                file_path.unlink()

        except Exception:
            pass


# Global registry instance
_global_registry: DocumentRegistry | None = None
_registry_lock = threading.Lock()


def get_document_registry() -> DocumentRegistry:
    """Get the global document registry.

    Returns:
        Global DocumentRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = DocumentRegistry()
        return _global_registry


def reset_document_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
