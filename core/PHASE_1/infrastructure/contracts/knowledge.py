"""Contract for the knowledge capability."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.PHASE_1.infrastructure.contracts.base import CognitiveEngine


@runtime_checkable
class Knowledge[Item, Query](CognitiveEngine, Protocol):
    """Structures, indexes and serves curated institutional knowledge.

    Generic over the knowledge item and the query used to search it.
    """

    def ingest(self, item: Item) -> None:
        """Index *item* so it becomes retrievable."""
        ...

    def search(self, query: Query, *, limit: int = 10) -> Sequence[Item]:
        """Return up to *limit* knowledge items most relevant to *query*."""
        ...
