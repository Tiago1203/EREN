"""Chunker for EREN Vector Memory Plugin.

Splits documents into chunks for embedding.
"""

from __future__ import annotations

import re
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plugins.vector_memory.types import VectorChunk, VectorMetadata

if TYPE_CHECKING:
    pass


class BaseChunker(ABC):
    """Abstract base class for chunkers."""

    @abstractmethod
    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
    ) -> list[VectorChunk]:
        """Split content into chunks.

        Args:
            document_id: Document ID.
            content: Content to chunk.
            metadata: Document metadata.

        Returns:
            List of chunks.
        """
        pass


class SentenceChunker(BaseChunker):
    """Chunks by sentences.

    Splits content by sentence boundaries.
    """

    def __init__(self, chunk_size: int = 3, overlap: int = 1):
        """Initialize sentence chunker.

        Args:
            chunk_size: Number of sentences per chunk.
            overlap: Number of sentences to overlap.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
    ) -> list[VectorChunk]:
        """Split by sentences.

        Args:
            document_id: Document ID.
            content: Content to chunk.
            metadata: Document metadata.

        Returns:
            List of chunks.
        """
        # Split into sentences
        sentences = self._split_sentences(content)

        if not sentences:
            return []

        # Group into chunks
        chunks = []
        for i in range(0, len(sentences), self.chunk_size - self.overlap):
            chunk_sentences = sentences[i:i + self.chunk_size]
            if not chunk_sentences:
                continue

            chunk_content = " ".join(chunk_sentences)
            chunk_id = f"{document_id}_chunk_{len(chunks)}"

            chunk_metadata = VectorMetadata(
                document_id=document_id,
                chunk_id=chunk_id,
                source=metadata.source,
                author=metadata.author,
                medical_specialty=metadata.medical_specialty,
                device=metadata.device,
                patient=metadata.patient,
                tags=metadata.tags,
                language=metadata.language,
                embedding_model=metadata.embedding_model,
                chunk_index=len(chunks),
                total_chunks=0,  # Will be set after
            )

            chunk = VectorChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_content,
                metadata=chunk_metadata,
                index=len(chunks),
            )
            chunks.append(chunk)

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentence_endings = r"[.!?]+[\s\n]+"
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]


class ParagraphChunker(BaseChunker):
    """Chunks by paragraphs.

    Splits content by paragraph boundaries.
    """

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        """Initialize paragraph chunker.

        Args:
            max_chunk_size: Maximum characters per chunk.
            overlap: Character overlap between chunks.
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
    ) -> list[VectorChunk]:
        """Split by paragraphs.

        Args:
            document_id: Document ID.
            content: Content to chunk.
            metadata: Document metadata.

        Returns:
            List of chunks.
        """
        # Split by double newlines (paragraphs)
        paragraphs = content.split("\n\n")

        if not paragraphs:
            paragraphs = content.split("\n")

        if not paragraphs:
            return []

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
                    chunk_id = f"{document_id}_chunk_{len(chunks)}"
                    chunk_metadata = VectorMetadata(
                        document_id=document_id,
                        chunk_id=chunk_id,
                        source=metadata.source,
                        author=metadata.author,
                        medical_specialty=metadata.medical_specialty,
                        device=metadata.device,
                        patient=metadata.patient,
                        tags=metadata.tags,
                        language=metadata.language,
                        embedding_model=metadata.embedding_model,
                        chunk_index=len(chunks),
                        total_chunks=0,
                    )

                    chunk = VectorChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        content=current_chunk.strip(),
                        metadata=chunk_metadata,
                        index=len(chunks),
                    )
                    chunks.append(chunk)

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
            chunk_id = f"{document_id}_chunk_{len(chunks)}"
            chunk_metadata = VectorMetadata(
                document_id=document_id,
                chunk_id=chunk_id,
                source=metadata.source,
                author=metadata.author,
                medical_specialty=metadata.medical_specialty,
                device=metadata.device,
                patient=metadata.patient,
                tags=metadata.tags,
                language=metadata.language,
                embedding_model=metadata.embedding_model,
                chunk_index=len(chunks),
                total_chunks=0,
            )

            chunk = VectorChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=current_chunk.strip(),
                metadata=chunk_metadata,
                index=len(chunks),
            )
            chunks.append(chunk)

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)

        return chunks


class SlidingWindowChunker(BaseChunker):
    """Chunks using sliding window.

    Creates overlapping chunks of fixed size.
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """Initialize sliding window chunker.

        Args:
            chunk_size: Size of each chunk in characters.
            overlap: Overlap between chunks in characters.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
    ) -> list[VectorChunk]:
        """Split using sliding window.

        Args:
            document_id: Document ID.
            content: Content to chunk.
            metadata: Document metadata.

        Returns:
            List of chunks.
        """
        if not content:
            return []

        chunks = []
        step = self.chunk_size - self.overlap
        position = 0

        while position < len(content):
            end = min(position + self.chunk_size, len(content))
            chunk_content = content[position:end]

            # Try to break at word boundary
            if end < len(content):
                last_space = chunk_content.rfind(" ")
                if last_space > self.chunk_size // 2:
                    chunk_content = chunk_content[:last_space]
                    end = position + len(chunk_content)

            chunk_id = f"{document_id}_chunk_{len(chunks)}"
            chunk_metadata = VectorMetadata(
                document_id=document_id,
                chunk_id=chunk_id,
                source=metadata.source,
                author=metadata.author,
                medical_specialty=metadata.medical_specialty,
                device=metadata.device,
                patient=metadata.patient,
                tags=metadata.tags,
                language=metadata.language,
                embedding_model=metadata.embedding_model,
                chunk_index=len(chunks),
                total_chunks=0,
            )

            chunk = VectorChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=chunk_content.strip(),
                metadata=chunk_metadata,
                index=len(chunks),
            )
            chunks.append(chunk)

            position += step
            if position >= len(content):
                break

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)

        return chunks


class RecursiveChunker(BaseChunker):
    """Chunks recursively.

    Tries to split at multiple levels: paragraphs, sentences, words.
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

    def chunk(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
    ) -> list[VectorChunk]:
        """Split recursively.

        Args:
            document_id: Document ID.
            content: Content to chunk.
            metadata: Document metadata.

        Returns:
            List of chunks.
        """
        if not content:
            return []

        chunks = []
        self._split_recursive(
            document_id,
            content,
            metadata,
            self.separators,
            chunks,
        )

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata.total_chunks = len(chunks)

        return chunks

    def _split_recursive(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata,
        separators: list[str],
        chunks: list[VectorChunk],
    ) -> None:
        """Recursively split content."""
        if not separators:
            # Base case: no more separators, create chunk
            if content.strip():
                chunk_id = f"{document_id}_chunk_{len(chunks)}"
                chunk_metadata = VectorMetadata(
                    document_id=document_id,
                    chunk_id=chunk_id,
                    source=metadata.source,
                    author=metadata.author,
                    medical_specialty=metadata.medical_specialty,
                    device=metadata.device,
                    patient=metadata.patient,
                    tags=metadata.tags,
                    language=metadata.language,
                    embedding_model=metadata.embedding_model,
                    chunk_index=len(chunks),
                    total_chunks=0,
                )

                chunk = VectorChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=content.strip(),
                    metadata=chunk_metadata,
                    index=len(chunks),
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
                    chunk_id = f"{document_id}_chunk_{len(chunks)}"
                    chunk_metadata = VectorMetadata(
                        document_id=document_id,
                        chunk_id=chunk_id,
                        source=metadata.source,
                        author=metadata.author,
                        medical_specialty=metadata.medical_specialty,
                        device=metadata.device,
                        patient=metadata.patient,
                        tags=metadata.tags,
                        language=metadata.language,
                        embedding_model=metadata.embedding_model,
                        chunk_index=len(chunks),
                        total_chunks=0,
                    )

                    chunk = VectorChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        content=current_chunk.strip(),
                        metadata=chunk_metadata,
                        index=len(chunks),
                    )
                    chunks.append(chunk)

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
            chunk_id = f"{document_id}_chunk_{len(chunks)}"
            chunk_metadata = VectorMetadata(
                document_id=document_id,
                chunk_id=chunk_id,
                source=metadata.source,
                author=metadata.author,
                medical_specialty=metadata.medical_specialty,
                device=metadata.device,
                patient=metadata.patient,
                tags=metadata.tags,
                language=metadata.language,
                embedding_model=metadata.embedding_model,
                chunk_index=len(chunks),
                total_chunks=0,
            )

            chunk = VectorChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                content=current_chunk.strip(),
                metadata=chunk_metadata,
                index=len(chunks),
            )
            chunks.append(chunk)


# Factory for creating chunkers
class ChunkerFactory:
    """Factory for chunkers."""

    _chunker_types = {
        "sentence": SentenceChunker,
        "paragraph": ParagraphChunker,
        "sliding_window": SlidingWindowChunker,
        "recursive": RecursiveChunker,
    }

    @classmethod
    def create(cls, chunker_type: str, **kwargs) -> BaseChunker:
        """Create a chunker by type.

        Args:
            chunker_type: Type of chunker.
            **kwargs: Chunker arguments.

        Returns:
            Chunker instance.
        """
        chunker_class = cls._chunker_types.get(chunker_type, SentenceChunker)
        return chunker_class(**kwargs)

    @classmethod
    def register(cls, name: str, chunker_class: type[BaseChunker]) -> None:
        """Register a new chunker.

        Args:
            name: Chunker name.
            chunker_class: Chunker class.
        """
        cls._chunker_types[name] = chunker_class

    @classmethod
    def list_chunker_types(cls) -> list[str]:
        """List available chunker types.

        Returns:
            List of chunker type names.
        """
        return list(cls._chunker_types.keys())
