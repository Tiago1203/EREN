"""Conversation summary service for EREN Conversation Memory Plugin.

Handles conversation summarization logic.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from plugins.conversation.types import (
    ConversationSummary,
    ConversationEntry,
    ConversationMetadata,
)

if TYPE_CHECKING:
    from plugins.conversation.contracts import ConversationRepositoryContract


class ConversationSummaryService:
    """Service for conversation summarization.

    Responsibilities:
    - Summarize long conversations
    - Update summaries
    - Detect when to summarize
    - Maintain compact context
    """

    def __init__(
        self,
        repository: "ConversationRepositoryContract",
        threshold_entries: int = 50,
        max_summary_length: int = 500,
    ):
        """Initialize summary service.

        Args:
            repository: Conversation repository contract.
            threshold_entries: Entries before summarization.
            max_summary_length: Maximum summary length.
        """
        self._repository = repository
        self._threshold_entries = threshold_entries
        self._max_summary_length = max_summary_length

    def should_summarize(self, conversation_id: str) -> bool:
        """Check if conversation should be summarized.

        Args:
            conversation_id: Conversation ID.

        Returns:
            True if should summarize.
        """
        try:
            metadata = self._repository.get_conversation(conversation_id)
            return metadata.entries_count >= self._threshold_entries
        except Exception:
            return False

    def summarize(
        self,
        conversation_id: str,
        entries: list[ConversationEntry] | None = None,
    ) -> ConversationSummary | None:
        """Summarize a conversation.

        Args:
            conversation_id: Conversation ID.
            entries: Optional pre-fetched entries.

        Returns:
            Summary or None.
        """
        try:
            # Get conversation metadata
            metadata = self._repository.get_conversation(conversation_id)

            # Get entries if not provided
            if entries is None:
                entries = self._repository.get_entries(conversation_id, limit=1000)

            if not entries:
                return None

            # Generate summary text
            summary_text = self._generate_summary(entries)

            # Extract key points
            key_points = self._extract_key_points(entries)

            # Calculate tokens saved
            original_tokens = sum(e.tokens for e in entries)
            summary_tokens = len(summary_text) // 4  # Rough estimate
            tokens_saved = original_tokens - summary_tokens

            # Create summary
            summary = ConversationSummary(
                conversation_id=conversation_id,
                summary=summary_text,
                key_points=key_points,
                created_at=datetime.now(timezone.utc),
                entries_count=len(entries),
                tokens_saved=tokens_saved,
            )

            # Save summary
            return self._repository.save_summary(summary)

        except Exception:
            return None

    def get_summary(self, conversation_id: str) -> ConversationSummary | None:
        """Get existing summary.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Summary or None.
        """
        return self._repository.get_summary(conversation_id)

    def update_summary(self, conversation_id: str) -> ConversationSummary | None:
        """Update summary for conversation.

        Args:
            conversation_id: Conversation ID.

        Returns:
            Updated summary or None.
        """
        return self.summarize(conversation_id)

    def _generate_summary(self, entries: list[ConversationEntry]) -> str:
        """Generate summary text from entries.

        Args:
            entries: Conversation entries.

        Returns:
            Summary text.
        """
        if not entries:
            return ""

        # Build summary from first and last few entries
        summary_parts = []

        # First entry (topic)
        if entries:
            summary_parts.append(f"Started: {entries[0].content[:100]}")

        # Last entry (conclusion)
        if len(entries) > 1:
            summary_parts.append(f"Last: {entries[-1].content[:100]}")

        # Entry count
        summary_parts.append(f"Total exchanges: {len(entries)}")

        # Combine
        summary = " | ".join(summary_parts)

        # Truncate if needed
        if len(summary) > self._max_summary_length:
            summary = summary[:self._max_summary_length - 3] + "..."

        return summary

    def _extract_key_points(self, entries: list[ConversationEntry]) -> list[str]:
        """Extract key points from entries.

        Args:
            entries: Conversation entries.

        Returns:
            List of key points.
        """
        key_points = []

        # Simple extraction: first meaningful content from each speaker
        speakers_seen = set()
        for entry in entries:
            if entry.role.value not in speakers_seen and len(key_points) < 5:
                content = entry.content.strip()
                if len(content) > 10:
                    key_points.append(content[:100])
                    speakers_seen.add(entry.role.value)

        return key_points

    def get_compact_context(
        self,
        conversation_id: str,
        max_entries: int = 5,
    ) -> list[ConversationEntry]:
        """Get compact context for conversation.

        Args:
            conversation_id: Conversation ID.
            max_entries: Maximum entries to return.

        Returns:
            List of entries for context.
        """
        entries = self._repository.get_entries(conversation_id, limit=1000)

        if len(entries) <= max_entries:
            return entries

        # Return last N entries for recent context
        return entries[-max_entries:]
