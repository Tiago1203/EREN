"""Foundational contracts shared by every EREN cognitive engine.

Pure interfaces — no logic, AI, or agents. Uses ``typing.Protocol`` so engines
depend on abstractions, not concrete classes (Dependency Inversion). Interfaces
are kept small and single-purpose (Interface Segregation): the common capability
every engine shares lives in :class:`CognitiveEngine`, while optional concerns
(such as a start/stop lifecycle) are separate protocols an engine *may* also
satisfy.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CognitiveEngine(Protocol):
    """Common contract implemented by every cognitive engine.

    Consumers (e.g. the orchestrator) depend on this abstraction rather than on
    any concrete engine, so engines are interchangeable behind it (Liskov
    Substitution). Deliberately minimal — engine-specific behavior belongs in
    the specialized sub-protocols in this package.
    """

    @property
    def name(self) -> str:
        """Stable, unique identifier of the engine (e.g. ``"planner"``)."""
        ...

    def describe(self) -> str:
        """Return a short, human-readable description of the engine's capability."""
        ...


@runtime_checkable
class SupportsLifecycle(Protocol):
    """Optional start/stop lifecycle for engines that manage resources.

    Segregated from :class:`CognitiveEngine` so stateless engines are not forced
    to implement lifecycle methods they do not need.
    """

    async def startup(self) -> None:
        """Acquire resources and become ready to serve requests."""
        ...

    async def shutdown(self) -> None:
        """Release resources acquired during :meth:`startup`."""
        ...
