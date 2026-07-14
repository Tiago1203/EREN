"""Sliding window chunker for EREN Knowledge Ingestion Pipeline.

Chunks text using fixed-size sliding window.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.ingestion.types import (
    CleanedDocument,
    ChunkedDocument,
    DocumentChunk,
    IngestionMetadata,
)
from core.ingestion.chunking.chunk_builder import BaseChunkBuilder

if TYPE_CHECKING:
    pass


class SlidingWindowChunkBuilder(BaseChunkBuilder):
    """Chunks using fixed-size sliding window.

    Single Responsibility: Only create overlapping chunks.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """Initialize sliding window chunker.

        Args:
            chunk_size: Size of each chunk in characters.
            overlap: Overlap between chunks in characters.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    @property
    def strategy_name(self) -> str:
        """Get chunking strategy name."""
        return "sliding_window"

    async def build(
        self,
        cleaned: CleanedDocument,
        metadata: IngestionMetadata | None = None,
    ) -> ChunkedDocument:
        """Build chunks using sliding window.

        Args:
            cleaned: Cleaned document.
            metadata: Optional metadata.

        Returns:
            Chunked document.
        """
        if not cleaned.content:
            return ChunkedDocument(
                document_id=cleaned.document_id,
                chunks=[],
                metadata=metadata or cleaned.metadata,
                chunking_time_ms=0,
                chunking_strategy=self.strategy_name,
            )

        chunks = []
        step = self.chunk_size - self.overlap
        position = 0
        content = cleaned.content

        while position < len(content):
            end = min(position + self.chunk_size, len(content))
            chunk_content = content[position:end]

            # Try to break at word boundary
            if end < len(content):
                last_space = chunk_content.rfind(" ")
                if last_space > self.chunk_size // 2:
                    chunk_content = chunk_content[:last_space]
                    end = position + len(chunk_content)

            chunk_id = f"{cleaned.document_id}_chunk_{len(chunks)}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=cleaned.document_id,
                content=chunk_content.strip(),
                index=len(chunks),
                total_chunks=0,
                metadata=metadata or cleaned.metadata,
                char_count=len(chunk_content.strip()),
                word_count=len(chunk_content.strip().split()),
            )
            chunks.append(chunk)

            position += step
            if position >= len(content):
                break

        # Update total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)

        return ChunkedDocument(
            document_id=cleaned.document_id,
            chunks=chunks,
            metadata=metadata or cleaned.metadata,
            chunking_time_ms=0,
            chunking_strategy=self.strategy_name,
        )
