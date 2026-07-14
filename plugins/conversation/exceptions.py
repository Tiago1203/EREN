"""Conversation memory exceptions for EREN Conversation Memory Plugin."""

from __future__ import annotations


class ConversationMemoryError(Exception):
    """Base exception for conversation memory errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class ConversationNotFoundError(ConversationMemoryError):
    """Raised when conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(f"Conversation not found: {conversation_id}")
        self.conversation_id = conversation_id


class EntryNotFoundError(ConversationMemoryError):
    """Raised when entry is not found."""

    def __init__(self, entry_id: str):
        super().__init__(f"Entry not found: {entry_id}")
        self.entry_id = entry_id


class ConversationExistsError(ConversationMemoryError):
    """Raised when conversation already exists."""

    def __init__(self, conversation_id: str):
        super().__init__(f"Conversation already exists: {conversation_id}")
        self.conversation_id = conversation_id


class InvalidConversationError(ConversationMemoryError):
    """Raised when conversation is invalid."""

    def __init__(self, conversation_id: str, reason: str = ""):
        super().__init__(f"Invalid conversation {conversation_id}: {reason}")
        self.conversation_id = conversation_id
        self.reason = reason


class StorageError(ConversationMemoryError):
    """Raised when storage operation fails."""

    def __init__(self, operation: str, reason: str = ""):
        super().__init__(f"Storage error during {operation}: {reason}")
        self.operation = operation
        self.reason = reason


class SerializationError(ConversationMemoryError):
    """Raised when serialization fails."""

    def __init__(self, message: str):
        super().__init__(f"Serialization error: {message}")


class ConfigurationError(ConversationMemoryError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class SearchError(ConversationMemoryError):
    """Raised when search operation fails."""

    def __init__(self, query: str, reason: str = ""):
        super().__init__(f"Search error for '{query}': {reason}")
        self.query = query
        self.reason = reason


class SummarizationError(ConversationMemoryError):
    """Raised when summarization fails."""

    def __init__(self, conversation_id: str, reason: str = ""):
        super().__init__(f"Summarization error for {conversation_id}: {reason}")
        self.conversation_id = conversation_id
        self.reason = reason
