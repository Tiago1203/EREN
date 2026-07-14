"""Conversation memory provider for EREN Conversation Memory Plugin.

Implements BaseMemoryInterface for the Memory Coordinator.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.memory.base import BaseMemoryInterface
from core.memory.types import (
    MemoryType,
    MemoryState,
    MemoryQuery,
    MemoryResponse,
    MemoryEntry,
    MemoryMetrics,
)

from plugins.conversation.repository import ConversationRepository
from plugins.conversation.types import (
    ConversationEntry as ConvEntry,
    ConversationMetadata,
    ConversationSearch,
    ConversationConfiguration,
    ConversationRole,
    ConversationType,
)
from plugins.conversation.exceptions import (
    ConversationNotFoundError,
    EntryNotFoundError,
)

if TYPE_CHECKING:
    pass


class ConversationMemoryProvider(BaseMemoryInterface):
    """Provider for conversation memory.

    Implements BaseMemoryInterface for the Memory Coordinator.
    Uses SQLite for storage (replaceable with PostgreSQL in production).
    """

    def __init__(self):
        """Initialize provider."""
        super().__init__()
        self._memory_id = "conversation"
        self._memory_type = MemoryType.CONVERSATION
        self._config: ConversationConfiguration | None = None
        self._repository: ConversationRepository | None = None

    @property
    def memory_id(self) -> str:
        """Get memory identifier."""
        return self._memory_id

    @property
    def memory_type(self) -> MemoryType:
        """Get memory type."""
        return self._memory_type

    def initialize(self, config: dict) -> None:
        """Initialize the memory.

        Args:
            config: Configuration dictionary.

        Raises:
            ConfigurationError: If initialization fails.
        """
        try:
            # Build configuration
            self._config = ConversationConfiguration(
                max_context_entries=config.get("max_context_entries", 20),
                max_tokens_per_entry=config.get("max_tokens_per_entry", 4000),
                summary_threshold_entries=config.get("summary_threshold_entries", 50),
                summary_max_length=config.get("summary_max_length", 500),
                ttl_days=config.get("ttl_days", 30),
                auto_archive_days=config.get("auto_archive_days", 7),
                enable_summarization=config.get("enable_summarization", True),
                enable_full_text_search=config.get("enable_full_text_search", True),
                database_path=config.get("database_path", ":memory:"),
                enable_multi_user=config.get("enable_multi_user", True),
                enable_multi_session=config.get("enable_multi_session", True),
            )

            # Initialize repository
            self._repository = ConversationRepository(self._config)

            self._state = MemoryState.READY

        except Exception as e:
            self._state = MemoryState.UNAVAILABLE
            raise

    def shutdown(self) -> None:
        """Shutdown the memory."""
        self._repository = None
        self._config = None
        self._state = MemoryState.DISABLED

    def read(self, key: str) -> MemoryResponse:
        """Read from memory.

        Args:
            key: Memory key (format: conversation_id:entry_id or just conversation_id).

        Returns:
            Memory response with results.
        """
        start_time = time.time()

        try:
            if not self._repository:
                return MemoryResponse(success=False, error="Not initialized")

            parts = key.split(":")
            conversation_id = parts[0]

            if len(parts) == 2:
                # Read specific entry
                entry = self._repository.get_entry(parts[1])
                return MemoryResponse(
                    results=[self._to_memory_result(entry)],
                    success=True,
                )
            else:
                # Read conversation context
                entries = self._repository.get_entries(
                    conversation_id,
                    limit=self._config.max_context_entries if self._config else 20,
                )
                results = [self._to_memory_result(e) for e in entries]
                return MemoryResponse(results=results, success=True)

        except EntryNotFoundError:
            self._metrics.record_read(int((time.time() - start_time) * 1000), hit=False)
            return MemoryResponse(results=[], success=True)
        except Exception as e:
            self._metrics.record_read(int((time.time() - start_time) * 1000), hit=False)
            return MemoryResponse(success=False, error=str(e))

    def read_batch(self, keys: list[str]) -> MemoryResponse:
        """Read multiple keys from memory.

        Args:
            keys: List of memory keys.

        Returns:
            Memory response with results.
        """
        all_results = []
        errors = []

        for key in keys:
            response = self.read(key)
            all_results.extend(response.results)
            if response.error:
                errors.append(response.error)

        return MemoryResponse(
            results=all_results,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
        )

    def write(self, entry: MemoryEntry) -> MemoryResponse:
        """Write to memory.

        Args:
            entry: Memory entry to write.

        Returns:
            Memory response.
        """
        start_time = time.time()

        try:
            if not self._repository:
                return MemoryResponse(success=False, error="Not initialized")

            # Parse entry metadata
            conversation_id = entry.metadata.get("conversation_id", "default")
            role_str = entry.metadata.get("role", "user")
            role = ConversationRole(role_str)

            # Create conversation if needed
            try:
                self._repository.get_conversation(conversation_id)
            except ConversationNotFoundError:
                metadata = ConversationMetadata(
                    conversation_id=conversation_id,
                    user_id=entry.metadata.get("user_id", ""),
                    session_id=entry.metadata.get("session_id", ""),
                    conversation_type=ConversationType(
                        entry.metadata.get("conversation_type", "general")
                    ),
                )
                self._repository.create_conversation(metadata)

            # Create entry
            conv_entry = ConvEntry(
                entry_id=entry.key or str(uuid.uuid4()),
                conversation_id=conversation_id,
                role=role,
                content=entry.content,
                timestamp=entry.timestamp,
                metadata=entry.metadata,
                tokens=entry.metadata.get("tokens", len(entry.content) // 4),
            )

            self._repository.add_entry(conv_entry)

            self._metrics.record_write(int((time.time() - start_time) * 1000))

            return MemoryResponse(success=True)

        except Exception as e:
            self._metrics.record_write(int((time.time() - start_time) * 1000))
            return MemoryResponse(success=False, error=str(e))

    def write_batch(self, entries: list[MemoryEntry]) -> MemoryResponse:
        """Write multiple entries to memory.

        Args:
            entries: List of memory entries.

        Returns:
            Memory response.
        """
        all_errors = []

        for entry in entries:
            response = self.write(entry)
            if not response.success and response.error:
                all_errors.append(response.error)

        return MemoryResponse(
            success=len(all_errors) == 0,
            error="; ".join(all_errors) if all_errors else "",
        )

    def search(self, query: MemoryQuery) -> MemoryResponse:
        """Search memory.

        Args:
            query: Search query.

        Returns:
            Memory response with search results.
        """
        start_time = time.time()

        try:
            if not self._repository:
                return MemoryResponse(success=False, error="Not initialized")

            # Convert to conversation search
            search = ConversationSearch(
                query=query.query,
                limit=query.limit,
                offset=query.offset,
            )

            entries = self._repository.search(search)
            results = [self._to_memory_result(e) for e in entries]

            self._metrics.record_search(int((time.time() - start_time) * 1000))

            return MemoryResponse(results=results, success=True)

        except Exception as e:
            self._metrics.record_search(int((time.time() - start_time) * 1000))
            return MemoryResponse(success=False, error=str(e))

    def delete(self, key: str) -> MemoryResponse:
        """Delete from memory.

        Args:
            key: Memory key to delete.

        Returns:
            Memory response.
        """
        try:
            if not self._repository:
                return MemoryResponse(success=False, error="Not initialized")

            parts = key.split(":")
            if len(parts) == 2:
                self._repository.delete_entry(parts[1])
            else:
                self._repository.delete_conversation(key)

            return MemoryResponse(success=True)

        except Exception as e:
            return MemoryResponse(success=False, error=str(e))

    def clear(self) -> MemoryResponse:
        """Clear all memory.

        Returns:
            Memory response.
        """
        try:
            if not self._repository:
                return MemoryResponse(success=False, error="Not initialized")

            # Delete all conversations
            conversations = self._repository.list_conversations(limit=1000)
            for conv in conversations:
                self._repository.delete_conversation(conv.conversation_id)

            return MemoryResponse(success=True)

        except Exception as e:
            return MemoryResponse(success=False, error=str(e))

    def _to_memory_result(self, entry: ConvEntry) -> MemoryResult:
        """Convert conversation entry to memory result.

        Args:
            entry: Conversation entry.

        Returns:
            Memory result.
        """
        return MemoryResult(
            content=entry.content,
            memory_type=self._memory_type,
            memory_id=f"{entry.conversation_id}:{entry.entry_id}",
            metadata={
                "role": entry.role.value,
                "conversation_id": entry.conversation_id,
                "entry_id": entry.entry_id,
            },
            timestamp=entry.timestamp,
        )


# Import MemoryResult
from core.memory.types import MemoryResult
