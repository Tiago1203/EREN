"""Dynamic registry of EREN cognitive engines.

`EngineRegistry` lets engines be registered and resolved **by name at runtime**,
so consumers (e.g. the orchestrator) discover engines through dependency
injection instead of importing and instantiating concrete classes.

Design principles:

- **Dependency Injection:** engines are *injected* into the registry (via the
  constructor or `register`); the registry never constructs engines itself and
  depends only on the `CognitiveEngine` abstraction.
- **No conditional dispatch:** resolution is an O(1) dictionary lookup keyed by
  `engine.name` — there are no ``if/elif`` chains selecting engines by type.

This is thin infrastructure, not business logic: it stores and hands back
objects. It contains no AI, no domain logic, and no cognition.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from core.contracts import CognitiveEngine
from core.registry.exceptions import (
    EngineAlreadyRegisteredError,
    EngineNotFoundError,
)


class EngineRegistry:
    """In-memory registry of cognitive engines keyed by ``engine.name``.

    Engines are provided from the outside (constructor or :meth:`register`),
    keeping construction and wiring a caller concern (Dependency Injection).
    """

    def __init__(self, engines: Iterable[CognitiveEngine] | None = None) -> None:
        self._engines: dict[str, CognitiveEngine] = {}
        for engine in engines or ():
            self.register(engine)

    def register(self, engine: CognitiveEngine, *, replace: bool = False) -> None:
        """Register ``engine`` under its ``name``.

        Raises :class:`EngineAlreadyRegisteredError` if the name is taken and
        ``replace`` is ``False``.
        """
        name = engine.name
        if name in self._engines and not replace:
            raise EngineAlreadyRegisteredError(name)
        self._engines[name] = engine

    def unregister(self, name: str) -> None:
        """Remove the engine registered under ``name``.

        Raises :class:`EngineNotFoundError` if no such engine exists.
        """
        try:
            del self._engines[name]
        except KeyError as exc:
            raise EngineNotFoundError(name) from exc

    def get(self, name: str) -> CognitiveEngine:
        """Return the engine registered under ``name`` (O(1) lookup).

        Raises :class:`EngineNotFoundError` if no such engine exists.
        """
        try:
            return self._engines[name]
        except KeyError as exc:
            raise EngineNotFoundError(name) from exc

    def list(self) -> Sequence[CognitiveEngine]:
        """Return all registered engines."""
        return tuple(self._engines.values())

    def __contains__(self, name: object) -> bool:
        return name in self._engines

    def __len__(self) -> int:
        return len(self._engines)
