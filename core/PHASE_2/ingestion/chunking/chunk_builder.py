"""Chunk builder base for EREN Knowledge Ingestion Pipeline.

Abstract base for all chunking strategies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_2.ingestion.types import (
    ChunkedDocument,
    CleanedDocument,
    IngestionMetadata,
)

if TYPE_CHECKING:
    pass


class BaseChunkBuilder(ABC):
    """Abstract base for chunk builders.

    Single Responsibility: Only divide text into chunks.
    """

    @abstractmethod
    async def build(
        self,
        cleaned: CleanedDocument,
        metadata: IngestionMetadata | None = None,
    ) -> ChunkedDocument:
        """Build chunks from cleaned document.

        Args:
            cleaned: Cleaned document.
            metadata: Optional metadata override.

        Returns:
            Chunked document.
        """
        pass

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Get chunking strategy name."""
        pass
