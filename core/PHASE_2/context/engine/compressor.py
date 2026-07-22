"""Context compressor for EREN Cognitive Context Engine.

Compresses context to fit token budget.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.context.engine.types import ContextItem

if TYPE_CHECKING:
    pass


class ContextCompressor:
    """Compresses context to fit within token budget.

    Ensures context fits in available tokens.
    """

    def __init__(self):
        """Initialize compressor."""
        pass

    def compress(
        self,
        items: list[ContextItem],
        max_tokens: int,
    ) -> list[ContextItem]:
        """Compress context items.

        Args:
            items: Items to compress.
            max_tokens: Maximum tokens available.

        Returns:
            Compressed items.
        """
        if not items:
            return []

        # Sort by relevance
        sorted_items = sorted(
            items,
            key=lambda i: (i.relevance_score, i.priority.value),
            reverse=True,
        )

        compressed = []
        total_tokens = 0

        for item in sorted_items:
            if total_tokens + item.tokens <= max_tokens:
                compressed.append(item)
                total_tokens += item.tokens
            else:
                # Try to truncate
                truncated = self._truncate(item, max_tokens - total_tokens)
                if truncated and truncated.tokens > 0:
                    compressed.append(truncated)

        return compressed

    def _truncate(
        self,
        item: ContextItem,
        max_tokens: int,
    ) -> ContextItem | None:
        """Truncate an item to fit budget.

        Args:
            item: Item to truncate.
            max_tokens: Max tokens available.

        Returns:
            Truncated item or None.
        """
        # Estimate chars from tokens
        max_chars = max_tokens * 4

        if len(item.content) <= max_chars:
            return item

        truncated_content = item.content[:max_chars]

        return ContextItem(
            item_id=item.item_id,
            source=item.source,
            content=truncated_content,
            relevance_score=item.relevance_score,
            priority=item.priority,
            metadata=item.metadata,
            document_id=item.document_id,
            chunk_id=item.chunk_id,
            title=item.title,
            author=item.author,
            timestamp=item.timestamp,
            tokens=max_tokens,
        )

    def compress_to_ratio(
        self,
        items: list[ContextItem],
        target_ratio: float = 0.8,
    ) -> list[ContextItem]:
        """Compress items to target ratio.

        Args:
            items: Items to compress.
            target_ratio: Target compression ratio.

        Returns:
            Compressed items.
        """
        if not items:
            return []

        total_tokens = sum(item.tokens for item in items)
        target_tokens = int(total_tokens * target_ratio)

        return self.compress(items, target_tokens)
