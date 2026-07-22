"""
Conversation Context Provider.

Provides conversation history context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.PHASE_2.ai.conversation import ConversationController


class ConversationContextProvider(BaseContextProvider):
    """
    Provides conversation context for the AI.
    
    Retrieves recent messages and conversation state.
    """
    
    def __init__(
        self,
        conversation_controller: ConversationController | None = None,
    ):
        self._conversation = conversation_controller
    
    @property
    def name(self) -> str:
        return "conversation"
    
    @property
    def priority(self) -> int:
        return 5  # Most critical - executed first
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get conversation context."""
        items = []
        
        # Get recent messages
        messages = await self._get_messages_safe(query.conversation_id)
        
        if messages:
            items.append(self._create_conversation_context(messages))
        
        return items
    
    async def _get_messages_safe(self, conversation_id: str) -> list[dict]:
        """Safely get messages."""
        if self._conversation is None:
            return self._mock_get_messages()
        try:
            results = await self._conversation.list_messages(conversation_id)
            return [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.created_at,
                }
                for m in results[-10:]  # Last 10 messages
            ]
        except Exception:
            return []
    
    def _create_conversation_context(self, messages: list[dict]) -> ContextItem:
        """Create conversation context."""
        lines = ["Recent conversation:"]
        for msg in messages[-5:]:
            lines.append(f"{msg['role'].upper()}: {msg['content'][:100]}")
        
        return self._create_item(
            content="\n".join(lines),
            relevance_score=1.0,  # Always highest relevance
            metadata={"type": "conversation", "message_count": len(messages)},
        )
    
    def _mock_get_messages(self) -> list[dict]:
        """Mock messages for testing."""
        return [
            {"role": "user", "content": "What's the status of the ventilator in ICU?", "timestamp": None},
            {"role": "assistant", "content": "The ventilator is active and working properly.", "timestamp": None},
            {"role": "user", "content": "When is the next maintenance scheduled?", "timestamp": None},
        ]
