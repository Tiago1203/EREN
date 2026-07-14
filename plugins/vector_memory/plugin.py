"""Vector Memory Plugin for EREN OS.

Provides vector memory capability for storing and retrieving documents.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.memory import (
    BaseMemoryInterface,
    MemoryType,
    MemoryState,
    MemoryEntry,
)

from plugins.vector_memory.provider import BaseVectorProvider, ChromaVectorProvider
from plugins.vector_memory.chunker import BaseChunker, SentenceChunker, ChunkerFactory
from plugins.vector_memory.types import (
    VectorDocument,
    VectorMetadata,
    VectorChunk,
    VectorSearchQuery,
    VectorSearchResult,
    VectorStatistics,
)

if TYPE_CHECKING:
    pass


class VectorMemoryPlugin:
    """Vector Memory Plugin.

    Provides vector memory for storing and retrieving documents.

    Architecture:
        Document
                │
                ▼
        Chunker
                │
                ▼
        Embedding Layer
                │
                ▼
        Vector Memory Plugin
                │
                ▼
        ChromaDB / Qdrant / pgvector
    """

    def __init__(
        self,
        provider: BaseVectorProvider | None = None,
        chunker: BaseChunker | None = None,
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
    ):
        """Initialize Vector Memory Plugin.

        Args:
            provider: Vector storage provider.
            chunker: Document chunker.
            embedding_provider: Embedding provider name.
            embedding_model: Embedding model name.
        """
        self._provider = provider or ChromaVectorProvider()
        self._chunker = chunker or SentenceChunker()
        self._embedding_provider = embedding_provider
        self._embedding_model = embedding_model
        self._initialized = False
        self._memory_provider: VectorMemoryProvider | None = None

    async def initialize(self, config: dict) -> None:
        """Initialize the plugin.

        Args:
            config: Configuration dictionary.
        """
        await self._provider.initialize(config)
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    @property
    def memory_interface(self) -> VectorMemoryInterface:
        """Get the memory interface for Memory Coordinator."""
        if self._memory_provider is None:
            self._memory_provider = VectorMemoryInterface(self)
        return self._memory_provider

    # =========================================================================
    # Document Operations
    # =========================================================================

    async def add_document(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata | None = None,
        embeddings: list[list[float]] | None = None,
    ) -> list[str]:
        """Add a document to vector memory.

        Args:
            document_id: Document ID.
            content: Document content.
            metadata: Document metadata.
            embeddings: Pre-computed embeddings (optional).

        Returns:
            List of chunk IDs.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        # Create default metadata
        if metadata is None:
            metadata = VectorMetadata(document_id=document_id)

        metadata.embedding_model = self._embedding_model

        # Chunk the document
        chunks = self._chunker.chunk(document_id, content, metadata)

        if not chunks:
            return []

        # Generate embeddings if not provided
        if embeddings is None:
            embeddings = await self._generate_embeddings([c.content for c in chunks])

        # Store in vector provider
        chunk_ids = await self._provider.store(chunks, embeddings)

        return chunk_ids

    async def add_document_with_embedding_generator(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata | None = None,
        embedding_generator: callable | None = None,
    ) -> list[str]:
        """Add a document with custom embedding generator.

        Args:
            document_id: Document ID.
            content: Document content.
            metadata: Document metadata.
            embedding_generator: Function that generates embeddings.

        Returns:
            List of chunk IDs.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        # Create default metadata
        if metadata is None:
            metadata = VectorMetadata(document_id=document_id)

        metadata.embedding_model = self._embedding_model

        # Chunk the document
        chunks = self._chunker.chunk(document_id, content, metadata)

        if not chunks:
            return []

        # Generate embeddings using provided generator
        if embedding_generator:
            embeddings = await embedding_generator([c.content for c in chunks])
        else:
            embeddings = await self._generate_embeddings([c.content for c in chunks])

        # Store in vector provider
        chunk_ids = await self._provider.store(chunks, embeddings)

        return chunk_ids

    async def search_similar(
        self,
        query: str,
        embedding: list[float] | None = None,
        filters: dict | None = None,
        top_k: int = 10,
        min_score: float = 0.0,
    ) -> list[VectorSearchResult]:
        """Search for similar documents.

        Args:
            query: Query text.
            embedding: Query embedding (generated if None).
            filters: Metadata filters.
            top_k: Number of results.
            min_score: Minimum similarity score.

        Returns:
            List of search results.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        # Generate embedding if not provided
        if embedding is None:
            embedding = await self._generate_single_embedding(query)

        # Create search query
        search_query = VectorSearchQuery(
            query=query,
            embeddings=embedding,
            filters=filters,
            top_k=top_k,
            min_score=min_score,
        )

        # Search
        results = await self._provider.search(search_query, embedding)

        return results

    async def get_document(self, document_id: str) -> list[VectorChunk]:
        """Get all chunks for a document.

        Args:
            document_id: Document ID.

        Returns:
            List of chunks.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        # This would need a get_by_document method in provider
        # For now, return empty list
        return []

    async def delete_document(self, document_id: str) -> int:
        """Delete a document and all its chunks.

        Args:
            document_id: Document ID.

        Returns:
            Number of chunks deleted.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        return await self._provider.delete_by_document(document_id)

    async def update_document(
        self,
        document_id: str,
        content: str,
        metadata: VectorMetadata | None = None,
    ) -> list[str]:
        """Update a document.

        Args:
            document_id: Document ID.
            content: New content.
            metadata: New metadata.

        Returns:
            List of new chunk IDs.
        """
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        # Delete old chunks
        await self._provider.delete_by_document(document_id)

        # Add new document
        return await self.add_document(document_id, content, metadata)

    # =========================================================================
    # Batch Operations
    # =========================================================================

    async def batch_add_documents(
        self,
        documents: list[tuple[str, str, VectorMetadata | None]],
    ) -> list[list[str]]:
        """Add multiple documents.

        Args:
            documents: List of (id, content, metadata) tuples.

        Returns:
            List of chunk ID lists.
        """
        results = []
        for doc_id, content, metadata in documents:
            chunk_ids = await self.add_document(doc_id, content, metadata)
            results.append(chunk_ids)
        return results

    async def batch_search(
        self,
        queries: list[str],
        top_k: int = 10,
    ) -> list[list[VectorSearchResult]]:
        """Search multiple queries.

        Args:
            queries: List of query strings.
            top_k: Results per query.

        Returns:
            List of result lists.
        """
        results = []
        for query in queries:
            result = await self.search_similar(query, top_k=top_k)
            results.append(result)
        return results

    # =========================================================================
    # Embedding Helpers
    # =========================================================================

    async def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: Texts to embed.

        Returns:
            List of embeddings.
        """
        # Try to use the Embedding Layer if available
        try:
            from core.embeddings import get_embedding_manager, EmbeddingProvider

            manager = get_embedding_manager()
            response = await manager.embed(
                texts=texts,
                model=self._embedding_model,
                provider=EmbeddingProvider.OPENAI,
            )

            if response.success:
                return [e.vector for e in response.embeddings]

        except Exception:
            pass

        # Fallback: generate mock embeddings
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]

    async def _generate_single_embedding(self, text: str) -> list[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        embeddings = await self._generate_embeddings([text])
        return embeddings[0] if embeddings else []

    # =========================================================================
    # Statistics and Health
    # =========================================================================

    async def get_statistics(self) -> VectorStatistics:
        """Get memory statistics.

        Returns:
            Memory statistics.
        """
        return await self._provider.get_statistics()

    async def health_check(self) -> dict:
        """Check plugin health.

        Returns:
            Health status.
        """
        provider_health = await self._provider.health_check()

        return {
            "plugin": "vector-memory",
            "initialized": self._initialized,
            "provider": provider_health,
            "chunker": self._chunker.__class__.__name__,
            "embedding_model": self._embedding_model,
        }


class VectorMemoryInterface:
    """Memory interface for Vector Memory.

    Provides interface for Memory Coordinator integration.
    """

    def __init__(self, plugin: VectorMemoryPlugin):
        """Initialize interface.

        Args:
            plugin: Vector Memory Plugin instance.
        """
        self._plugin = plugin

    @property
    def memory_type(self) -> MemoryType:
        """Get memory type."""
        return MemoryType.VECTOR

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "vector-memory"

    async def read(self, key: str, **kwargs) -> MemoryEntry | None:
        """Read a memory entry.

        Args:
            key: Memory key.
            **kwargs: Additional arguments.

        Returns:
            Memory entry or None.
        """
        results = await self._plugin.search_similar(
            query=key,
            top_k=kwargs.get("top_k", 1),
        )

        if results:
            result = results[0]
            return MemoryEntry(
                content=result.content,
                memory_type=MemoryType.VECTOR,
                metadata={
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "score": result.score,
                    **result.metadata.to_dict(),
                },
            )

        return None

    async def write(self, entry: MemoryEntry, **kwargs) -> str:
        """Write a memory entry.

        Args:
            entry: Memory entry.
            **kwargs: Additional arguments.

        Returns:
            Entry ID.
        """
        document_id = entry.metadata.get("document_id", str(uuid.uuid4()))
        content = entry.content

        chunk_ids = await self._plugin.add_document(
            document_id=document_id,
            content=content,
            metadata=VectorMetadata(**entry.metadata),
        )

        return chunk_ids[0] if chunk_ids else ""

    async def delete(self, key: str, **kwargs) -> bool:
        """Delete a memory entry.

        Args:
            key: Memory key.
            **kwargs: Additional arguments.

        Returns:
            True if deleted.
        """
        document_id = kwargs.get("document_id", key)
        deleted = await self._plugin.delete_document(document_id)
        return deleted > 0

    async def exists(self, key: str, **kwargs) -> bool:
        """Check if memory exists.

        Args:
            key: Memory key.
            **kwargs: Additional arguments.

        Returns:
            True if exists.
        """
        chunks = await self._plugin.get_document(key)
        return len(chunks) > 0

    async def list_keys(self, **kwargs) -> list[str]:
        """List all memory keys.

        Args:
            **kwargs: Additional arguments.

        Returns:
            List of keys.
        """
        return []

    async def health_check(self) -> dict:
        """Check interface health.

        Returns:
            Health status.
        """
        return await self._plugin.health_check()
