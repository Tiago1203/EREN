"""Vector memory provider for EREN Vector Memory Plugin.

Interface for vector storage backends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plugins.vector_memory.types import (
    VectorChunk,
    VectorSearchQuery,
    VectorSearchResult,
    VectorStatistics,
)

if TYPE_CHECKING:
    pass


class BaseVectorProvider(ABC):
    """Abstract base class for vector memory providers.

    This is the contract for all vector storage backends.
    The Kernel Cognitivo never knows:
    - ChromaDB
    - Qdrant
    - Pinecone
    - Milvus
    - Weaviate
    - pgvector

    It only knows this interface.
    """

    @abstractmethod
    async def initialize(self, config: dict) -> None:
        """Initialize the provider.

        Args:
            config: Configuration dictionary.
        """
        pass

    @abstractmethod
    async def store(
        self,
        chunks: list[VectorChunk],
        embeddings: list[list[float]],
    ) -> list[str]:
        """Store chunks with embeddings.

        Args:
            chunks: Chunks to store.
            embeddings: Corresponding embeddings.

        Returns:
            List of stored chunk IDs.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: VectorSearchQuery,
        embedding: list[float],
    ) -> list[VectorSearchResult]:
        """Search for similar vectors.

        Args:
            query: Search query.
            embedding: Query embedding.

        Returns:
            List of search results.
        """
        pass

    @abstractmethod
    async def get(self, chunk_id: str) -> VectorChunk | None:
        """Get a chunk by ID.

        Args:
            chunk_id: Chunk ID.

        Returns:
            Chunk or None.
        """
        pass

    @abstractmethod
    async def delete(self, chunk_id: str) -> bool:
        """Delete a chunk.

        Args:
            chunk_id: Chunk ID.

        Returns:
            True if deleted.
        """
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document.

        Args:
            document_id: Document ID.

        Returns:
            Number of chunks deleted.
        """
        pass

    @abstractmethod
    async def update(
        self,
        chunk_id: str,
        content: str | None = None,
        embedding: list[float] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """Update a chunk.

        Args:
            chunk_id: Chunk ID.
            content: New content (optional).
            embedding: New embedding (optional).
            metadata: New metadata (optional).

        Returns:
            True if updated.
        """
        pass

    @abstractmethod
    async def get_statistics(self) -> VectorStatistics:
        """Get memory statistics.

        Returns:
            Memory statistics.
        """
        pass

    @abstractmethod
    async def health_check(self) -> dict:
        """Check provider health.

        Returns:
            Health status.
        """
        pass


class ChromaVectorProvider(BaseVectorProvider):
    """ChromaDB vector provider.

    Implementation for ChromaDB (development).
    """

    def __init__(self):
        """Initialize ChromaDB provider."""
        self._client = None
        self._collection = None
        self._initialized = False

    async def initialize(self, config: dict) -> None:
        """Initialize ChromaDB.

        Args:
            config: Configuration dictionary.
        """
        try:
            import chromadb
            from chromadb.config import Settings

            persist_directory = config.get("persist_directory", "./chroma_data")
            collection_name = config.get("collection_name", "eren_vectors")

            # Create client
            self._client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )

            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "EREN Vector Memory"},
            )

            self._initialized = True

        except ImportError:
            # ChromaDB not installed, use mock
            self._initialized = True
            self._mock_data: dict[str, dict] = {}

    async def store(
        self,
        chunks: list[VectorChunk],
        embeddings: list[list[float]],
    ) -> list[str]:
        """Store chunks with embeddings.

        Args:
            chunks: Chunks to store.
            embeddings: Corresponding embeddings.

        Returns:
            List of stored chunk IDs.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have same length")

        chunk_ids = []

        if self._collection is not None:
            # Use real ChromaDB
            ids = [chunk.chunk_id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata.to_dict() for chunk in chunks]

            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            chunk_ids = ids
        else:
            # Use mock storage
            for chunk, embedding in zip(chunks, embeddings):
                self._mock_data[chunk.chunk_id] = {
                    "chunk": chunk,
                    "embedding": embedding,
                }
                chunk_ids.append(chunk.chunk_id)

        return chunk_ids

    async def search(
        self,
        query: VectorSearchQuery,
        embedding: list[float],
    ) -> list[VectorSearchResult]:
        """Search for similar vectors.

        Args:
            query: Search query.
            embedding: Query embedding.

        Returns:
            List of search results.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        results = []

        if self._collection is not None:
            # Use real ChromaDB
            where = query.filters if query.filters else None

            search_results = self._collection.query(
                query_embeddings=[embedding],
                n_results=query.top_k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            if search_results["ids"]:
                for i, chunk_id in enumerate(search_results["ids"][0]):
                    content = search_results["documents"][0][i]
                    distance = search_results["distances"][0][i]
                    metadata = search_results["metadatas"][0][i]

                    # Convert distance to similarity score
                    score = 1.0 - distance

                    if score >= query.min_score:
                        from plugins.vector_memory.types import VectorMetadata
                        meta = VectorMetadata(**metadata) if metadata else VectorMetadata()

                        result = VectorSearchResult(
                            chunk_id=chunk_id,
                            document_id=meta.document_id,
                            content=content,
                            score=score,
                            metadata=meta,
                            distance=distance,
                        )
                        results.append(result)
        else:
            # Use mock storage (simple cosine similarity)
            import math

            query_norm = math.sqrt(sum(x * x for x in embedding))

            for chunk_id, data in self._mock_data.items():
                chunk = data["chunk"]
                stored_embedding = data["embedding"]

                # Cosine similarity
                dot_product = sum(a * b for a, b in zip(embedding, stored_embedding))
                stored_norm = math.sqrt(sum(x * x for x in stored_embedding))

                if query_norm > 0 and stored_norm > 0:
                    similarity = dot_product / (query_norm * stored_norm)
                else:
                    similarity = 0

                if similarity >= query.min_score:
                    result = VectorSearchResult(
                        chunk_id=chunk_id,
                        document_id=chunk.document_id,
                        content=chunk.content,
                        score=similarity,
                        metadata=chunk.metadata,
                        distance=1 - similarity,
                    )
                    results.append(result)

            # Sort by score and limit
            results.sort(key=lambda r: r.score, reverse=True)
            results = results[:query.top_k]

        return results

    async def get(self, chunk_id: str) -> VectorChunk | None:
        """Get a chunk by ID.

        Args:
            chunk_id: Chunk ID.

        Returns:
            Chunk or None.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        if self._collection is not None:
            result = self._collection.get(ids=[chunk_id])
            if result["ids"]:
                from plugins.vector_memory.types import VectorMetadata
                metadata = VectorMetadata(**result["metadatas"][0]) if result["metadatas"] else VectorMetadata()

                return VectorChunk(
                    chunk_id=chunk_id,
                    document_id=metadata.document_id,
                    content=result["documents"][0],
                    metadata=metadata,
                )
        else:
            if chunk_id in self._mock_data:
                return self._mock_data[chunk_id]["chunk"]

        return None

    async def delete(self, chunk_id: str) -> bool:
        """Delete a chunk.

        Args:
            chunk_id: Chunk ID.

        Returns:
            True if deleted.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        if self._collection is not None:
            self._collection.delete(ids=[chunk_id])
        else:
            if chunk_id in self._mock_data:
                del self._mock_data[chunk_id]

        return True

    async def delete_by_document(self, document_id: str) -> int:
        """Delete all chunks for a document.

        Args:
            document_id: Document ID.

        Returns:
            Number of chunks deleted.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        deleted = 0

        if self._collection is not None:
            result = self._collection.get(
                where={"document_id": document_id},
                include=["ids"],
            )
            if result["ids"]:
                self._collection.delete(ids=result["ids"])
                deleted = len(result["ids"])
        else:
            to_delete = [
                cid for cid, data in self._mock_data.items()
                if data["chunk"].document_id == document_id
            ]
            for cid in to_delete:
                del self._mock_data[cid]
                deleted += 1

        return deleted

    async def update(
        self,
        chunk_id: str,
        content: str | None = None,
        embedding: list[float] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """Update a chunk.

        Args:
            chunk_id: Chunk ID.
            content: New content (optional).
            embedding: New embedding (optional).
            metadata: New metadata (optional).

        Returns:
            True if updated.
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        # ChromaDB doesn't have direct update, so we delete and add
        chunk = await self.get(chunk_id)
        if not chunk:
            return False

        if content:
            chunk.content = content
        if metadata:
            for key, value in metadata.items():
                setattr(chunk.metadata, key, value)

        if embedding:
            await self.delete(chunk_id)
            await self.store([chunk], [embedding])
        else:
            # Just update content/metadata
            if self._collection is not None:
                self._collection.update(
                    ids=[chunk_id],
                    documents=[chunk.content],
                    metadatas=[chunk.metadata.to_dict()],
                )

        return True

    async def get_statistics(self) -> VectorStatistics:
        """Get memory statistics.

        Returns:
            Memory statistics.
        """
        from plugins.vector_memory.types import VectorStatistics

        if self._collection is not None:
            count = self._collection.count()
            return VectorStatistics(
                total_documents=0,  # Would need to track separately
                total_chunks=count,
                total_embeddings=count,
            )
        else:
            return VectorStatistics(
                total_documents=len(set(d["chunk"].document_id for d in self._mock_data.values())),
                total_chunks=len(self._mock_data),
                total_embeddings=len(self._mock_data),
            )

    async def health_check(self) -> dict:
        """Check provider health.

        Returns:
            Health status.
        """
        return {
            "healthy": self._initialized,
            "provider": "chromadb",
            "initialized": self._initialized,
        }
