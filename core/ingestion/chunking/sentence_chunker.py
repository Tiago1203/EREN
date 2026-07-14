"""Sentence chunker for EREN Knowledge Ingestion Pipeline.

Chunks text by sentence boundaries.
"""

from __future__ import annotations

import re
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


class SentenceChunkBuilder(BaseChunkBuilder):
    """Chunks by sentence boundaries.

    Single Responsibility: Only split by sentences.
    """

    def __init__(self, sentences_per_chunk: int = 3, overlap: int = 1):
        """Initialize sentence chunker.

        Args:
            sentences_per_chunk: Number of sentences per chunk.
            overlap: Number of sentences to overlap.
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap = overlap

    @property
    def strategy_name(self) -> str:
        """Get chunking strategy name."""
        return "sentence"

    async def build(
        self,
        cleaned: CleanedDocument,
        metadata: IngestionMetadata | None = None,
    ) -> ChunkedDocument:
        """Build chunks by sentences.

        Args:
            cleaned: Cleaned document.
            metadata: Optional metadata.

        Returns:
            Chunked document.
        """
        # Split into sentences
        sentences = self._split_sentences(cleaned.content)

        if not sentences:
            return ChunkedDocument(
                document_id=cleaned.document_id,
                chunks=[],
                metadata=metadata or cleaned.metadata,
                chunking_time_ms=0,
                chunking_strategy=self.strategy_name,
            )

        # Group into chunks
        chunks = []
        step = self.sentences_per_chunk - self.overlap

        for i in range(0, len(sentences), step):
            chunk_sentences = sentences[i:i + self.sentences_per_chunk]
            if not chunk_sentences:
                continue

            chunk_content = " ".join(chunk_sentences)
            chunk_id = f"{cleaned.document_id}_chunk_{len(chunks)}"

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=cleaned.document_id,
                content=chunk_content,
                index=len(chunks),
                total_chunks=0,  # Will be updated
                metadata=metadata or cleaned.metadata,
                char_count=len(chunk_content),
                word_count=len(chunk_content.split()),
            )
            chunks.append(chunk)

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

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentence_endings = r"[.!?]+[\s\n]+"
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
