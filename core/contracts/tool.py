"""Contract for tools — controlled, invokable capabilities.

A tool is a *leaf* capability (a database call, an external service, a
calculator). It is intentionally **not** a :class:`CognitiveEngine`: engines
reason and coordinate, tools just execute. Keeping them separate honors
Interface Segregation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Tool[TInput, TOutput](Protocol):
    """A single, controlled capability an engine may invoke.

    Generic over its input and output types so concrete tools stay strongly
    typed without this contract knowing any domain detail (Open/Closed).
    """

    @property
    def name(self) -> str:
        """Stable, unique identifier of the tool."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        ...

    def invoke(self, payload: TInput) -> TOutput:
        """Execute the tool with *payload* and return its result."""
        ...
