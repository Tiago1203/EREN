"""Contract for the memory capability."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.contracts.base import CognitiveEngine


@runtime_checkable
class Memory[Record, Query](CognitiveEngine, Protocol):
    """Stores and recalls contextual/institutional memory.

    Generic over the stored record and the query used to retrieve it.
    """

    def remember(self, record: Record) -> None:
        """Persist *record* into memory."""
        ...

    def recall(self, query: Query, *, limit: int = 10) -> Sequence[Record]:
        """Return up to *limit* records most relevant to *query*."""
        ...

    def forget(self, query: Query) -> None:
        """Remove records matching *query* from memory."""
        ...
