"""Conversation memory plugin for EREN.

Registers with the Plugin Framework and provides conversation memory capability.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.memory.base import BaseMemoryInterface
from core.memory.types import MemoryType

from plugins.conversation.provider import ConversationMemoryProvider
from plugins.conversation.types import (
    ConversationConfiguration,
    ConversationMetrics,
)

if TYPE_CHECKING:
    pass


class ConversationMemoryPlugin:
    """Plugin for conversation memory.

    Registers with Plugin Framework and provides conversation memory capability.
    """

    def __init__(self):
        """Initialize plugin."""
        self._provider: ConversationMemoryProvider | None = None
        self._initialized = False

    @property
    def plugin_id(self) -> str:
        """Get plugin identifier."""
        return "conversation-memory"

    @property
    def name(self) -> str:
        """Get plugin name."""
        return "Conversation Memory"

    @property
    def version(self) -> str:
        """Get plugin version."""
        return "1.0.0"

    @property
    def description(self) -> str:
        """Get plugin description."""
        return "Conversation memory for EREN OS"

    def get_capabilities(self) -> list[dict]:
        """Get plugin capabilities."""
        return [
            {
                "capability_id": "conversation-memory",
                "name": "Conversation Memory",
                "type": "memory",
                "memory_type": MemoryType.CONVERSATION.value,
                "description": "Stores and retrieves conversation history",
            },
        ]

    def initialize(self, config: dict) -> None:
        """Initialize the plugin.

        Args:
            config: Plugin configuration.
        """
        self._provider = ConversationMemoryProvider()
        self._provider.initialize(config)
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        if self._provider:
            self._provider.shutdown()
            self._provider = None
        self._initialized = False

    @property
    def memory_provider(self) -> BaseMemoryInterface | None:
        """Get memory provider.

        Returns:
            Memory provider for registration with Memory Coordinator.
        """
        return self._provider

    def get_metrics(self) -> ConversationMetrics | None:
        """Get conversation metrics.

        Returns:
            Metrics or None if not initialized.
        """
        if not self._provider or not self._provider._repository:
            return None

        return self._provider._repository.get_metrics()


# Plugin factory function
def create_plugin() -> ConversationMemoryPlugin:
    """Create conversation memory plugin instance.

    Returns:
        ConversationMemoryPlugin instance.
    """
    return ConversationMemoryPlugin()
