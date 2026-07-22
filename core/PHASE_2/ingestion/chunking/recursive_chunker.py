"""Recursive chunker for EREN Knowledge Ingestion Pipeline.

Chunks text using recursive hierarchical splitting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.ingestion.chunking.chunk_builder import BaseChunkBuilder
from core.PHASE_2.ingestion.types import (
    ChunkedDocument,
    CleanedDocument,
    DocumentChunk,
    IngestionMetadata,
)

if TYPE_CHECKING:
    pass


class RecursiveChunkBuilder(BaseChunkBuilder):
    """Chunks recursively using hierarchical splitting.

    Single Responsibility: Only recursively split text.
    """

    def __init__(
        self,
        separators: list[str] | None = None,
        chunk_size: int = 500,
        overlap: int = 50,
    ):
        """Initialize recursive chunker.

        Args:
            separators: List of separators (in order of preference).
            chunk_size: Target chunk size.
            overlap: Overlap between chunks.
        """
        self.separators = separators or ["\n\n", "\n", ". ", " "]
        self.chunk_size = chunk_size
        self.overlap = overlap

    @property
    def strategy_name(self) -> str:
        """Get chunking strategy name."""
        return "recursive"

    async def build(
        self,
        cleaned: CleanedDocument,
        metadata: IngestionMetadata | None = None,
    ) -> ChunkedDocument:
        """Build chunks recursively.

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
        self._split_recursive(
            cleaned.document_id,
            cleaned.content,
            metadata or cleaned.metadata,
            self.separators,
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

    def _split_recursive(
        self,
        document_id: str,
        content: str,
        metadata: IngestionMetadata,
        separators: list[str],
        chunks: list[DocumentChunk],
    ) -> None:
        """Recursively split content."""
        if not separators:
            # Base case: no more separators, create chunk
            if content.strip():
                chunk_id = f"{document_id}_chunk_{len(chunks)}"
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=content.strip(),
                    index=len(chunks),
                    total_chunks=0,
                    metadata=metadata,
                    char_count=len(content.strip()),
                    word_count=len(content.strip().split()),
                )
                chunks.append(chunk)
            return

        separator = separators[0]
        remaining_separators = separators[1:]

        # Split by separator
        parts = content.split(separator)
        current_chunk = ""

        for part in parts:
            test_chunk = current_chunk + part + separator

            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk
                if current_chunk.strip():
                    self._create_chunk(
                        document_id,
                        current_chunk.strip(),
                        metadata,
                        chunks,
                    )

                # Handle overflow with next separator
                if len(part) > self.chunk_size:
                    self._split_recursive(
                        document_id,
                        part,
                        metadata,
                        remaining_separators,
                        chunks,
                    )
                    current_chunk = ""
                else:
                    current_chunk = part + separator

        # Don't forget last chunk
        if current_chunk.strip():
            self._create_chunk(
                document_id,
                current_chunk.strip(),
                metadata,
                chunks,
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
