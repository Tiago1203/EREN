"""Knowledge Ingestion Pipeline for EREN OS.

Orchestrates the full document ingestion process.
Pipeline ONLY orchestrates - never implements extraction, cleaning, chunking, or storage logic.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from core.ingestion.chunking import BaseChunkBuilder, SentenceChunkBuilder
from core.ingestion.exceptions import (
    ChunkingError,
    ExtractionError,
    UnsupportedFormatError,
)
from core.ingestion.extractor import ExtractorFactory
from core.ingestion.processors import TextProcessor
from core.ingestion.types import (
    ChunkedDocument,
    CleanedDocument,
    DocumentType,
    ExtractedDocument,
    IngestedDocument,
    IngestionStatistics,
    IngestionStatus,
    RawDocument,
)

if TYPE_CHECKING:
    from plugins.vector_memory import VectorMemoryPlugin


class KnowledgeIngestionPipeline:
    """Knowledge Ingestion Pipeline.

    Philosophy: The Pipeline ONLY orchestrates.
    It NEVER knows about:
    - PDF, DOCX, TXT, FHIR, HL7 (Extractor knows)
    - Embeddings (EmbeddingManager knows)
    - Chroma, PostgreSQL (VectorMemory knows)

    Pipeline ONLY coordinates the flow.
    """

    def __init__(
        self,
        text_processor: TextProcessor | None = None,
        chunk_builder: BaseChunkBuilder | None = None,
        vector_plugin: VectorMemoryPlugin | None = None,
    ):
        """Initialize pipeline.

        Args:
            text_processor: Text processor for cleaning/normalization.
            chunk_builder: Chunk builder for splitting text.
            vector_plugin: Vector memory plugin for storage.
        """
        # Pipeline NEVER creates processors - they must be injected
        self._text_processor = text_processor or TextProcessor()
        self._chunk_builder = chunk_builder or SentenceChunkBuilder()
        self._vector_plugin = vector_plugin

        # Statistics
        self._statistics = IngestionStatistics()

        # Register default extractors
        ExtractorFactory.register_defaults()

    # =========================================================================
    # Pipeline Configuration (Setter-based for dependency injection)
    # =========================================================================

    def set_text_processor(self, processor: TextProcessor) -> None:
        """Set text processor.

        Args:
            processor: Text processor to use.
        """
        self._text_processor = processor

    def set_chunk_builder(self, builder: BaseChunkBuilder) -> None:
        """Set chunk builder.

        Args:
            builder: Chunk builder to use.
        """
        self._chunk_builder = builder

    def set_vector_plugin(self, plugin: VectorMemoryPlugin | None) -> None:
        """Set vector memory plugin.

        Args:
            plugin: Vector memory plugin.
        """
        self._vector_plugin = plugin

    # =========================================================================
    # Main Ingestion Methods
    # =========================================================================

    async def ingest(
        self,
        raw: RawDocument,
        store_in_vector: bool = True,
    ) -> IngestedDocument:
        """Ingest a document.

        Pipeline orchestrates:
        1. Extraction (via ExtractorFactory)
        2. Processing (via TextProcessor)
        3. Chunking (via ChunkBuilder)
        4. Storage (via VectorMemoryPlugin)

        Args:
            raw: Raw document.
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
            # Stage 1: Extract (delegates to ExtractorFactory)
            stages.append({"stage": "extraction", "start": time.time()})
            extracted = await self._extract(raw)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            document_id = extracted.document_id
            extracted.metadata.document_id = document_id
            warnings.extend(extracted.warnings)

            # Stage 2: Process (delegates to TextProcessor)
            stages.append({"stage": "processing", "start": time.time()})
            cleaned = await self._process(extracted)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)
            warnings.extend(cleaned.cleaning_actions)

            # Stage 3: Chunk (delegates to ChunkBuilder)
            stages.append({"stage": "chunking", "start": time.time()})
            chunked = await self._chunk(cleaned)
            stages[-1]["end"] = time.time()
            stages[-1]["duration_ms"] = int((stages[-1]["end"] - stages[-1]["start"]) * 1000)

            chunks_created = len(chunked.chunks)

            # Stage 4: Store (delegates to VectorMemoryPlugin)
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
                    errors.append(f"Storage failed: {e!s}")
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
                warnings=warnings,
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
        store_in_vector: bool = True,
    ) -> list[IngestedDocument]:
        """Ingest multiple documents.

        Args:
            documents: List of raw documents.
            store_in_vector: Whether to store in vector memory.

        Returns:
            List of ingestion results.
        """
        results = []
        for raw in documents:
            result = await self.ingest(raw, store_in_vector)
            results.append(result)
        return results

    # =========================================================================
    # Pipeline Stages (Delegation Only)
    # =========================================================================

    async def _extract(self, raw: RawDocument) -> ExtractedDocument:
        """Extract text from document.

        Delegates to ExtractorFactory - Pipeline doesn't know document formats.

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

    async def _process(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Process extracted text.

        Delegates to TextProcessor - Pipeline doesn't know cleaning logic.

        Args:
            extracted: Extracted document.

        Returns:
            Cleaned document.
        """
        return await self._text_processor.process(extracted)

    async def _chunk(self, cleaned: CleanedDocument) -> ChunkedDocument:
        """Chunk cleaned text.

        Delegates to ChunkBuilder - Pipeline doesn't know chunking logic.

        Args:
            cleaned: Cleaned document.

        Returns:
            Chunked document.

        Raises:
            ChunkingError: If chunking fails.
        """
        try:
            return await self._chunk_builder.build(cleaned)
        except Exception as e:
            raise ChunkingError(cleaned.document_id, str(e))

    # =========================================================================
    # Statistics
    # =========================================================================

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
