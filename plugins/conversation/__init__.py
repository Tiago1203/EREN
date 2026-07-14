"""EREN Conversation Memory Plugin.

Provides conversation memory capability for EREN OS.
Implements BaseMemoryInterface for Memory Coordinator.
Registers with Plugin Framework.
"""

from __future__ import annotations

from plugins.conversation.plugin import ConversationMemoryPlugin, create_plugin
from plugins.conversation.provider import ConversationMemoryProvider
from plugins.conversation.repository import ConversationRepository
from plugins.conversation.contracts import (
    ConversationRepositoryContract,
    DefaultConversationRepository,
)
from plugins.conversation.search_service import ConversationSearchService
from plugins.conversation.summary_service import ConversationSummaryService
from plugins.conversation.indexer import ConversationIndexer
from plugins.conversation.types import (
    ConversationEntry,
    ConversationMetadata,
    ConversationSummary,
    ConversationSearch,
    ConversationMetrics,
    ConversationConfiguration,
    ConversationRole,
    ConversationType,
    ConversationState,
    ConversationChunk,
    ConversationAttachment,
    ConversationReference,
    ConversationStatistics,
    ConversationSearchResult,
)
from plugins.conversation.exceptions import (
    ConversationMemoryError,
    ConversationNotFoundError,
    EntryNotFoundError,
    ConversationExistsError,
    InvalidConversationError,
    StorageError,
    SerializationError,
    ConfigurationError,
    SearchError,
    SummarizationError,
)

__all__ = [
    # Plugin
    "ConversationMemoryPlugin",
    "create_plugin",
    # Provider
    "ConversationMemoryProvider",
    # Repository
    "ConversationRepository",
    # Contracts
    "ConversationRepositoryContract",
    "DefaultConversationRepository",
    # Services
    "ConversationSearchService",
    "ConversationSummaryService",
    "ConversationIndexer",
    # Types
    "ConversationEntry",
    "ConversationMetadata",
    "ConversationSummary",
    "ConversationSearch",
    "ConversationMetrics",
    "ConversationConfiguration",
    "ConversationRole",
    "ConversationType",
    "ConversationState",
    "ConversationChunk",
    "ConversationAttachment",
    "ConversationReference",
    "ConversationStatistics",
    "ConversationSearchResult",
    # Exceptions
    "ConversationMemoryError",
    "ConversationNotFoundError",
    "EntryNotFoundError",
    "ConversationExistsError",
    "InvalidConversationError",
    "StorageError",
    "SerializationError",
    "ConfigurationError",
    "SearchError",
    "SummarizationError",
]
