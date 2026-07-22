"""Contract for the workflow capability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.PHASE_1.infrastructure.contracts.base import CognitiveEngine


@runtime_checkable
class Workflow[Definition, Instance, State](CognitiveEngine, Protocol):
    """Drives long-running, stateful, multi-step operational processes.

    Generic over the process definition, a running instance, and its state.
    """

    def start(self, definition: Definition) -> Instance:
        """Instantiate and start a workflow from *definition*."""
        ...

    def advance(self, instance: Instance) -> Instance:
        """Advance *instance* to its next state and return the updated instance."""
        ...

    def state_of(self, instance: Instance) -> State:
        """Return the current state of *instance*."""
        ...
