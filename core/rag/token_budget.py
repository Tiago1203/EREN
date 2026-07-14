"""RAG Token Budget for EREN OS.

Manages token budgets for RAG pipeline.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.rag.types import RetrievedChunk
from core.rag.exceptions import TokenBudgetExceededError

if TYPE_CHECKING:
    pass


class TokenBudget:
    """Manages token budget for RAG context.

    Ensures context fits within token limits.
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        reserved_tokens: int = 500,
    ):
        """Initialize token budget.

        Args:
            max_tokens: Maximum total tokens.
            reserved_tokens: Reserved tokens for response.
        """
        self._max_tokens = max_tokens
        self._reserved_tokens = reserved_tokens
        self._available_tokens = max_tokens - reserved_tokens

    @property
    def available_tokens(self) -> int:
        """Get available tokens for context."""
        return self._available_tokens

    @property
    def max_tokens(self) -> int:
        """Get max tokens."""
        return self._max_tokens

    @property
    def reserved_tokens(self) -> int:
        """Get reserved tokens."""
        return self._reserved_tokens

    def fits_budget(self, tokens: int) -> bool:
        """Check if tokens fit in budget.

        Args:
            tokens: Token count to check.

        Returns:
            True if fits.
        """
        return tokens <= self._available_tokens

    def allocate(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """Allocate chunks within budget.

        Args:
            chunks: Chunks to allocate.

        Returns:
            Chunks that fit budget.

        Raises:
            TokenBudgetExceededError: If budget exceeded.
        """
        allocated = []
        total_tokens = 0

        for chunk in chunks:
            chunk_tokens = self._estimate_tokens(chunk.content)

            if total_tokens + chunk_tokens <= self._available_tokens:
                allocated.append(chunk)
                total_tokens += chunk_tokens
            else:
                # Try to add partial content
                remaining = self._available_tokens - total_tokens
                if remaining >= self._estimate_tokens(chunk.content[:100]):
                    allocated.append(chunk)
                    break
                else:
                    break

        return allocated

    def _estimate_tokens(self, text: str) -> int:
        """Estimate tokens for text."""
        return len(text) // 4


class ChunkPrioritizer:
    """Prioritizes chunks for token budget allocation."""

    def __init__(self):
        """Initialize prioritizer."""
        pass

    def prioritize(
        self,
        chunks: list[RetrievedChunk],
        available_tokens: int,
    ) -> list[RetrievedChunk]:
        """Prioritize chunks for budget.

        Args:
            chunks: Chunks to prioritize.
            available_tokens: Available token budget.

        Returns:
            Prioritized chunks within budget.
        """
        if not chunks:
            return []

        # Sort by relevance score
        sorted_chunks = sorted(
            chunks,
            key=lambda c: c.relevance_score,
            reverse=True,
        )

        # Allocate within budget
        budget = TokenBudget(
            max_tokens=available_tokens + budget.reserved_tokens,
            reserved_tokens=0,
        )

        return budget.allocate(sorted_chunks)


# Module-level budget instance
_default_budget: TokenBudget | None = None


def get_default_budget() -> TokenBudget:
    """Get default token budget.

    Returns:
        Default TokenBudget instance.
    """
    global _default_budget
    if _default_budget is None:
        _default_budget = TokenBudget()
    return _default_budget


def reset_default_budget() -> None:
    """Reset default budget."""
    global _default_budget
    _default_budget = None
