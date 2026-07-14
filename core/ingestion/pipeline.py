"""Knowledge Ingestion Pipeline for EREN OS.

Orchestrates the full document ingestion process.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from core.ingestion.types import (
    DocumentType,
    RawDocument,
    ExtractedDocument,
    CleanedDocument,
    ChunkedDocument,
    DocumentChunk,
    IngestedDocument,
    IngestionStatus,
    IngestionStatistics,
)
from core.ingestion.extractor import ExtractorFactory, BaseExtractor
from core.ingestion.cleaner import TextCleaner
from core.ingestion.metadata import MetadataBuilder
from core.ingestion.exceptions import (
    ExtractionError,
    UnsupportedFormatError,
    ChunkingError,
    PipelineError,
)

if TYPE_CHECKING:
    from plugins.vector_memory import VectorMemoryPlugin


class KnowledgeIngestionPipeline:
    """Knowledge Ingestion Pipeline.

    Orchestrates the full document ingestion process:
    1. Extract text from document
    2. Clean and normalize text
    3. Chunk text into manageable pieces
    4. Generate embeddings
    5. Store in vector memory
    """

    def __init__(
        self,
        vector_memory_plugin: "VectorMemoryPlugin | None" = None,
        extractor_factory: ExtractorFactory | None = None,
        cleaner: TextCleaner | None = None,
        metadata_builder: MetadataBuilder | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        """Initialize pipeline.

        Args:
            vector_memory_plugin: Vector memory plugin for storage.
            extractor_factory: Extractor factory.
            cleaner: Text cleaner.
            metadata_builder: Metadata builder.
            chunk_size: Default chunk size.
            chunk_overlap: Default chunk overlap.
        """
        self._vector_plugin = vector_memory_plugin
        self._extractor_factory = extractor_factory or ExtractorFactory()
        self._cleaner = cleaner or TextCleaner()
        self._metadata_builder = metadata_builder or MetadataBuilder()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

        # Statistics
        self._statistics = IngestionStatistics()

        # Register default extractors
        ExtractorFactory.register_defaults()

    @property
    def vector_plugin(self) -> "VectorMemoryPlugin | None":
        """Get vector memory plugin."""
        return self._vector_plugin

    @vector_plugin.setter
    def vector_plugin(self, plugin: "VectorMemoryPlugin | None") -> None:
        """Set vector memory plugin."""
        self._vector_plugin = plugin

    async def ingest(
        self,
        raw: RawDocument,
        generate_embeddings: bool = True,
        store_in_vector: bool = True,
    ) -> IngestedDocument:
        """Ingest a document.

        Args:
            raw: Raw document.
            generate_embeddings: Whether to generate embeddings.
            store_in_vector: Whether to store in vector memory.

        Returns:
            Ingested document result.
        """
        start_time = time.time()
        stages = []
        errors = []
        warnings = []

        document_id = str(uuid.uuid4())

        try:
            # Stage 1: Extract
            stages.append({"stage": "extraction", "start": time.time()})
            extracted = await self._extract(raw)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            # Update document ID
            document_id = extracted.document_id
            extracted.metadata.document_id = document_id

            # Stage 2: Clean
            stages.append({"stage": "cleaning", "start": time.time()})
            cleaned = await self._clean(extracted)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            # Stage 3: Chunk
            stages.append({"stage": "chunking", "start": time.time()})
            chunked = await self._chunk(cleaned)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            # Stage 4: Store
            chunks_created = len(chunked.chunks)
            embeddings_generated = 0

            if store_in_vector and self._vector_plugin:
                stages.append({"stage": "storage", "start": time.time()})
                try:
                    for chunk in chunked.chunks:
                        await self._vector_plugin.add_document(
                            document_id=chunk.document_id,
                            content=chunk.content,
                            metadata=chunk.metadata,
                        )
                        embeddings_generated += 1
                    stages[-1]["end"] = time.time()
                except Exception as e:
                    errors.append(f"Storage failed: {str(e)}")
                    stages[-1]["error"] = str(e)
                    stages[-1]["end"] = time.time()

            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            # Update statistics
            self._update_statistics(
                raw.document_type,
                extracted.metadata.source_type,
                chunks_created,
                IngestionStatus.COMPLETED if not errors else IngestionStatus.PARTIAL,
            )

            total_time = int((time.time() - start_time) * 1000)

            return IngestedDocument(
                document_id=document_id,
                original_type=raw.document_type,
                chunks_created=chunks_created,
                embeddings_generated=embeddings_generated,
                metadata=extracted.metadata,
                status=IngestionStatus.COMPLETED if not errors else IngestionStatus.PARTIAL,
                total_time_ms=total_time,
                stages=stages,
                errors=errors,
                warnings=warnings + extracted.warnings + cleaned.cleaning_actions,
            )

        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            errors.append(str(e))

            self._update_statistics(
                raw.document_type,
                raw.metadata.source_type,
                0,
                IngestionStatus.FAILED,
            )

            return IngestedDocument(
                document_id=document_id,
                original_type=raw.document_type,
                chunks_created=0,
                embeddings_generated=0,
                metadata=raw.metadata,
                status=IngestionStatus.FAILED,
                total_time_ms=total_time,
                stages=stages,
                errors=errors,
                warnings=warnings,
            )

    async def ingest_batch(
        self,
        documents: list[RawDocument],
        generate_embeddings: bool = True,
        store_in_vector: bool = True,
    ) -> list[IngestedDocument]:
        """Ingest multiple documents.

        Args:
            documents: List of raw documents.
            generate_embeddings: Whether to generate embeddings.
            store_in_vector: Whether to store in vector memory.

        Returns:
            List of ingestion results.
        """
        results = []
        for raw in documents:
            result = await self.ingest(raw, generate_embeddings, store_in_vector)
            results.append(result)
        return results

    async def _extract(self, raw: RawDocument) -> ExtractedDocument:
        """Extract text from document.

        Args:
            raw: Raw document.

        Returns:
            Extracted document.

        Raises:
            ExtractionError: If extraction fails.
        """
        extractor = ExtractorFactory.get_for_document(raw)

        if not extractor:
            raise UnsupportedFormatError(raw.document_type.value)

        try:
            return await extractor.extract(raw)
        except Exception as e:
            raise ExtractionError(raw.source, str(e))

    async def _clean(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Clean extracted document.

        Args:
            extracted: Extracted document.

        Returns:
            Cleaned document.
        """
        return await self._cleaner.clean(extracted)

    async def _chunk(self, cleaned: CleanedDocument) -> ChunkedDocument:
        """Chunk cleaned document.

        Args:
            cleaned: Cleaned document.

        Returns:
            Chunked document.

        Raises:
            ChunkingError: If chunking fails.
        """
        try:
            # Try to import from vector_memory plugin
            try:
                from plugins.vector_memory import SentenceChunker
                from plugins.vector_memory.types import VectorMetadata

                # Use SentenceChunker from vector_memory plugin
                chunker = SentenceChunker(chunk_size=3, overlap=1)

                # Convert to vector_memory format
                vector_meta = VectorMetadata(
                    document_id=cleaned.document_id,
                    source=cleaned.metadata.source_type.value,
                    author=cleaned.metadata.author,
                    medical_specialty=cleaned.metadata.medical_specialty,
                    tags=cleaned.metadata.tags,
                    language=cleaned.metadata.language,
                )

                # Chunk using vector_memory chunker
                vector_chunks = chunker.chunk(
                    document_id=cleaned.document_id,
                    content=cleaned.content,
                    metadata=vector_meta,
                )

                # Convert back to ingestion format
                chunks = [
                    DocumentChunk(
                        chunk_id=c.chunk_id,
                        document_id=c.document_id,
                        content=c.content,
                        index=c.index,
                        total_chunks=c.metadata.total_chunks,
                        metadata=cleaned.metadata,
                        char_count=len(c.content),
                        word_count=len(c.content.split()),
                    )
                    for c in vector_chunks
                ]

                return ChunkedDocument(
                    document_id=cleaned.document_id,
                    chunks=chunks,
                    metadata=cleaned.metadata,
                    chunking_time_ms=0,
                    chunking_strategy="sentence",
                )

            except ImportError:
                # Fallback: simple chunking without vector_memory
                return self._simple_chunk(cleaned)

        except Exception as e:
            raise ChunkingError(cleaned.document_id, str(e))

    def _simple_chunk(self, cleaned: CleanedDocument) -> ChunkedDocument:
        """Simple chunking without vector_memory plugin.

        Args:
            cleaned: Cleaned document.

        Returns:
            Chunked document.
        """
        import re

        # Split by sentences
        sentences = re.split(r"[.!?]+\s+", cleaned.content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Group into chunks
        chunks = []
        chunk_size = 3
        for i in range(0, len(sentences), chunk_size):
            chunk_sentences = sentences[i:i + chunk_size]
            if not chunk_sentences:
                continue

            chunk_content = ". ".join(chunk_sentences) + "."
            chunk_id = f"{cleaned.document_id}_chunk_{len(chunks)}"

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=cleaned.document_id,
                content=chunk_content,
                index=len(chunks),
                total_chunks=0,  # Will be updated
                metadata=cleaned.metadata,
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
            metadata=cleaned.metadata,
            chunking_time_ms=0,
            chunking_strategy="simple",
        )

    def _update_statistics(
        self,
        doc_type: DocumentType,
        source_type,
        chunks: int,
        status: IngestionStatus,
    ) -> None:
        """Update ingestion statistics.

        Args:
            doc_type: Document type.
            source_type: Source type.
            chunks: Number of chunks created.
            status: Ingestion status.
        """
        self._statistics.total_documents += 1

        if status == IngestionStatus.COMPLETED:
            self._statistics.successful_documents += 1
        elif status == IngestionStatus.FAILED:
            self._statistics.failed_documents += 1
        else:
            self._statistics.partial_documents += 1

        self._statistics.total_chunks += chunks

        # Track by type
        type_key = doc_type.value
        self._statistics.by_type[type_key] = self._statistics.by_type.get(type_key, 0) + 1

        # Track by source
        source_key = source_type.value if hasattr(source_type, 'value') else str(source_type)
        self._statistics.by_source[source_key] = self._statistics.by_source.get(source_key, 0) + 1

        # Calculate averages
        if self._statistics.total_documents > 0:
            self._statistics.average_chunks_per_document = (
                self._statistics.total_chunks / self._statistics.total_documents
            )

    def get_statistics(self) -> IngestionStatistics:
        """Get ingestion statistics.

        Returns:
            Statistics.
        """
        return self._statistics

    def reset_statistics(self) -> None:
        """Reset statistics."""
        self._statistics = IngestionStatistics()
