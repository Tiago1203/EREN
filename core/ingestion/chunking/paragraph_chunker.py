"""Paragraph chunker for EREN Knowledge Ingestion Pipeline.

Chunks text by paragraph boundaries.
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


class ParagraphChunkBuilder(BaseChunkBuilder):
    """Chunks by paragraph boundaries.

    Single Responsibility: Only split by paragraphs.
    """

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        """Initialize paragraph chunker.

        Args:
            max_chunk_size: Maximum characters per chunk.
            overlap: Character overlap between chunks.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    @property
    def strategy_name(self) -> str:
        """Get chunking strategy name."""
        return "paragraph"

    async def build(
        self,
        cleaned: CleanedDocument,
        metadata: IngestionMetadata | None = None,
    ) -> ChunkedDocument:
        """Build chunks by paragraphs.

        Args:
            cleaned: Cleaned document.
            metadata: Optional metadata.

        Returns:
            Chunked document.
        """
        # Split by double newlines (paragraphs)
        paragraphs = cleaned.content.split("\n\n")

        if not paragraphs:
            paragraphs = cleaned.content.split("\n")

        if not paragraphs:
            return ChunkedDocument(
                document_id=cleaned.document_id,
                chunks=[],
                metadata=metadata or cleaned.metadata,
                chunking_time_ms=0,
                chunking_strategy=self.strategy_name,
            )

        chunks = []
        current_chunk = ""
        current_size = 0

        for paragraph in paragraphs:
            para_size = len(paragraph)

            if current_size + para_size <= self.max_chunk_size:
                current_chunk += paragraph + "\n\n"
                current_size += para_size + 2
            else:
                # Save current chunk
                if current_chunk.strip():
                    self._create_chunk(
                        cleaned.document_id,
                        current_chunk.strip(),
                        metadata or cleaned.metadata,
                        chunks,
                    )

                # Start new chunk with overlap
                if self.overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-self.overlap:]
                    current_chunk = overlap_text + paragraph + "\n\n"
                    current_size = len(current_chunk)
                else:
                    current_chunk = paragraph + "\n\n"
                    current_size = para_size

        # Don't forget last chunk
        if current_chunk.strip():
            self._create_chunk(
                cleaned.document_id,
                current_chunk.strip(),
                metadata or cleaned.metadata,
                chunks,
            )

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

    def _create_chunk(
        self,
        document_id: str,
        content: str,
        metadata: IngestionMetadata,
        chunks: list[DocumentChunk],
    ) -> None:
        """Create a single chunk."""
        chunk_id = f"{document_id}_chunk_{len(chunks)}"
        chunk = DocumentChunk(
            chunk_id=chunk_id,
            document_id=document_id,
            content=content,
            index=len(chunks),
            total_chunks=0,
            metadata=metadata,
            char_count=len(content),
            word_count=len(content.split()),
        )
        chunks.append(chunk)
