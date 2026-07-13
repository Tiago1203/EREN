"""Registry abstraction for EREN.

Defines the :class:`EngineRegistryPort` contract so consumers depend on the
*abstraction* of a registry, not on the concrete :class:`EngineRegistry`
(Dependency Inversion).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.contracts import CognitiveEngine


@runtime_checkable
class EngineRegistryPort(Protocol):
    """Contract for a dynamic registry of cognitive engines."""

    def register(self, engine: CognitiveEngine, *, replace: bool = False) -> None:
        """Register ``engine`` under its ``name``."""
        ...

    def unregister(self, name: str) -> None:
        """Remove the engine registered under ``name``."""
        ...

    def get(self, name: str) -> CognitiveEngine:
        """Return the engine registered under ``name``."""
        ...

    def list(self) -> Sequence[CognitiveEngine]:
        """Return all registered engines."""
        ...
