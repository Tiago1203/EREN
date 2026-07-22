"""Contract for the planning capability."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.PHASE_1.infrastructure.contracts.base import CognitiveEngine


@runtime_checkable
class Planner[Goal, Plan](CognitiveEngine, Protocol):
    """Decomposes a goal into an ordered, executable plan.

    Generic over the goal and plan representations so the contract is reusable
    across domains without modification (Open/Closed).
    """

    def plan(self, goal: Goal) -> Plan:
        """Produce an executable plan that achieves *goal*."""
        ...

    def replan(self, goal: Goal, previous: Plan, reason: str) -> Plan:
        """Revise *previous* plan for *goal* after a failure or new information."""
        ...
