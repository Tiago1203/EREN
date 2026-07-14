"""Conversation repository contract for EREN Conversation Memory Plugin.

Abstract contract for conversation storage implementations.
SQLite, PostgreSQL, MongoDB, etc. all implement this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from plugins.conversation.types import (
    ConversationEntry,
    ConversationMetadata,
    ConversationSummary,
    ConversationSearch,
    ConversationMetrics,
    ConversationConfiguration,
    ConversationState,
)

if TYPE_CHECKING:
    pass


class ConversationRepositoryContract(ABC):
    """Abstract contract for conversation storage.

    All storage implementations (SQLite, PostgreSQL, MongoDB, etc.)
    must implement this contract.
    """

    @abstractmethod
    def create_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        """Create a new conversation.

        Args:
            metadata: Conversation metadata.

        Returns:
            Created conversation metadata.
        """
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> ConversationMetadata:
        """Get conversation metadata.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Conversation metadata.
        """
        pass

    @abstractmethod
    def update_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        """Update conversation metadata.

        Args:
            metadata: Updated metadata.

        Returns:
            Updated metadata.
        """
        pass

    @abstractmethod
    def list_conversations(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        state: ConversationState | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ConversationMetadata]:
        """List conversations.

        Args:
            user_id: Filter by user.
            session_id: Filter by session.
            state: Filter by state.
            limit: Maximum results.
            offset: Result offset.

        Returns:
            List of conversations.
        """
        pass

    @abstractmethod
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation and all entries.

        Args:
            conversation_id: Conversation ID.

        Returns:
            True if deleted.
        """
        pass

    @abstractmethod
    def add_entry(self, entry: ConversationEntry) -> ConversationEntry:
        """Add entry to conversation.

        Args:
            entry: Entry to add.

        Returns:
            Added entry.
        """
        pass

    @abstractmethod
    def get_entries(
        self,
        conversation_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ConversationEntry]:
        """Get entries for conversation.

        Args:
            conversation_id: Conversation ID.
            limit: Maximum entries.
            offset: Entry offset.

        Returns:
            List of entries.
        """
        pass

    @abstractmethod
    def get_entry(self, entry_id: str) -> ConversationEntry:
        """Get entry by ID.

        Args:
            entry_id: Entry ID.

        Returns:
            Entry.
        """
        pass

    @abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        """Delete entry.

        Args:
            entry_id: Entry ID.

        Returns:
            True if deleted.
        """
        pass

    @abstractmethod
    def save_summary(self, summary: ConversationSummary) -> ConversationSummary:
        """Save conversation summary.

        Args:
            summary: Summary to save.

        Returns:
            Saved summary.
        """
        pass

    @abstractmethod
    def get_summary(self, conversation_id: str) -> ConversationSummary | None:
        """Get conversation summary.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Summary or None.
        """
        pass

    @abstractmethod
    def search(self, search: ConversationSearch) -> list[ConversationEntry]:
        """Search entries.

        Args:
            search: Search parameters.

        Returns:
            Matching entries.
        """
        pass

    @abstractmethod
    def get_metrics(self) -> ConversationMetrics:
        """Get metrics.

        Returns:
            Metrics.
        """
        pass


# Import actual repository for default implementation
from plugins.conversation.repository import ConversationRepository


class DefaultConversationRepository(ConversationRepositoryContract):
    """Default implementation using SQLite.

    This is the default implementation. For production,
    use PostgreSQL, MongoDB, or other implementations.
    """

    def __init__(self, config: ConversationConfiguration):
        """Initialize repository.

        Args:
            config: Configuration.
        """
        self._repository = ConversationRepository(config)

    def create_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        return self._repository.create_conversation(metadata)

    def get_conversation(self, conversation_id: str) -> ConversationMetadata:
        return self._repository.get_conversation(conversation_id)

    def update_conversation(self, metadata: ConversationMetadata) -> ConversationMetadata:
        return self._repository.update_conversation(metadata)

    def list_conversations(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        state: ConversationState | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ConversationMetadata]:
        return self._repository.list_conversations(user_id, session_id, state, limit, offset)

    def delete_conversation(self, conversation_id: str) -> bool:
        return self._repository.delete_conversation(conversation_id)

    def add_entry(self, entry: ConversationEntry) -> ConversationEntry:
        return self._repository.add_entry(entry)

    def get_entries(
        self,
        conversation_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ConversationEntry]:
        return self._repository.get_entries(conversation_id, limit, offset)

    def get_entry(self, entry_id: str) -> ConversationEntry:
        return self._repository.get_entry(entry_id)

    def delete_entry(self, entry_id: str) -> bool:
        return self._repository.delete_entry(entry_id)

    def save_summary(self, summary: ConversationSummary) -> ConversationSummary:
        return self._repository.save_summary(summary)

    def get_summary(self, conversation_id: str) -> ConversationSummary | None:
        return self._repository.get_summary(conversation_id)

    def search(self, search: ConversationSearch) -> list[ConversationEntry]:
        return self._repository.search(search)

    def get_metrics(self) -> ConversationMetrics:
        return self._repository.get_metrics()
