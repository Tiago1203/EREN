"""Conversation indexer for EREN Conversation Memory Plugin.

Handles indexing for future vector search integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from plugins.conversation.types import (
    ConversationEntry,
    ConversationChunk,
)

if TYPE_CHECKING:
    pass


class ConversationIndexer:
    """Service for conversation indexing.

    Responsibilities:
    - Prepare information for indexing
    - Send information to Vector Memory Plugin
    - Update indices
    - Delete obsolete indices

    Note:
        This component prepares data for future vector search.
        Actual embedding generation is handled by the Vector Memory Plugin.
    """

    def __init__(self):
        """Initialize indexer."""
        self._vector_plugin = None
        self._embedding_callback: Callable | None = None

    def register_vector_plugin(self, plugin) -> None:
        """Register vector memory plugin.

        Args:
            plugin: Vector memory plugin.
        """
        self._vector_plugin = plugin

    def register_embedding_callback(self, callback: Callable) -> None:
        """Register embedding generation callback.

        Args:
            callback: Function to generate embeddings.
        """
        self._embedding_callback = callback

    def index_entry(self, entry: ConversationEntry) -> bool:
        """Index a conversation entry.

        Args:
            entry: Entry to index.

        Returns:
            True if indexed successfully.
        """
        try:
            # Create chunks from entry
            chunks = self._create_chunks(entry)

            # Index each chunk
            for chunk in chunks:
                self._index_chunk(chunk)

            return True
        except Exception:
            return False

    def index_conversation(self, conversation_id: str, entries: list[ConversationEntry]) -> bool:
        """Index all entries in a conversation.

        Args:
            conversation_id: Conversation ID.
            entries: Entries to index.

        Returns:
            True if indexed successfully.
        """
        try:
            for entry in entries:
                self.index_entry(entry)
            return True
        except Exception:
            return False

    def delete_index(self, entry_id: str) -> bool:
        """Delete entry index.

        Args:
            entry_id: Entry ID.

        Returns:
            True if deleted.
        """
        try:
            if self._vector_plugin:
                # Delete from vector plugin
                self._vector_plugin.delete(f"conversation:{entry_id}")
            return True
        except Exception:
            return False

    def delete_conversation_index(self, conversation_id: str) -> bool:
        """Delete all indices for a conversation.

        Args:
            conversation_id: Conversation ID.

        Returns:
            True if deleted.
        """
        try:
            if self._vector_plugin:
                # Delete all conversation entries
                self._vector_plugin.delete(f"conversation:{conversation_id}:*")
            return True
        except Exception:
            return False

    def _create_chunks(self, entry: ConversationEntry) -> list[ConversationChunk]:
        """Create chunks from entry for indexing.

        Args:
            entry: Entry to chunk.

        Returns:
            List of chunks.
        """
        # Simple chunking: one chunk per entry
        # Future: smarter chunking with overlap
        chunk = ConversationChunk(
            chunk_id=f"{entry.conversation_id}:{entry.entry_id}",
            conversation_id=entry.conversation_id,
            entry_id=entry.entry_id,
            content=entry.content,
            role=entry.role.value,
            sequence=0,
            metadata={
                "timestamp": entry.timestamp.isoformat(),
                "tokens": entry.tokens,
            },
        )
        return [chunk]

    def _index_chunk(self, chunk: ConversationChunk) -> bool:
        """Index a chunk.

        Args:
            chunk: Chunk to index.

        Returns:
            True if indexed.
        """
        if self._vector_plugin:
            # Generate embedding if callback provided
            if self._embedding_callback:
                embedding = self._embedding_callback(chunk.content)
                chunk.metadata["embedding"] = embedding

            # Store in vector plugin
            self._vector_plugin.write(
                key=chunk.chunk_id,
                content=chunk.content,
                metadata=chunk.metadata,
            )
        return True

    def reindex_all(self, conversations: list[tuple[str, list[ConversationEntry]]]) -> int:
        """Reindex all conversations.

        Args:
            conversations: List of (conversation_id, entries) tuples.

        Returns:
            Number of entries indexed.
        """
        count = 0
        for conversation_id, entries in conversations:
            if self.index_conversation(conversation_id, entries):
                count += len(entries)
        return count
