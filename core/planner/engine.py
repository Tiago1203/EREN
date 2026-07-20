"""Planner engine for EREN core.

Architecture scaffolding only. The class fixes the **shape** of the planner
capability — method signatures for its four responsibilities — but contains no
logic, AI, or agents. Method bodies raise ``NotImplementedError`` until behavior
is designed.
"""

from __future__ import annotations

from collections.abc import Sequence

from .exceptions import PlannerError
from .models import EngineSelection, Intention, Plan, PlanStep


class PlannerEngine:
    """Turns a caller's intention into an ordered, executable plan.

    Responsibilities (and nothing else):

    1. **receive intention** — :meth:`receive_intention`
    2. **create plan** — :meth:`create_plan`
    3. **select engines** — :meth:`select_engines`
    4. **order execution** — :meth:`order_execution`

    It decides *what should happen and in what order*; it does not execute steps
    (orchestrator/workflow) nor reason within a step (reasoning engine).
    Satisfies :class:`~core.contracts.base.CognitiveEngine` and, structurally,
    :class:`core.planner.interfaces.PlannerPort`.
    """

    @property
    def name(self) -> str:
        """Stable identifier of this engine."""
        return "planner"

    def describe(self) -> str:
        """Human-readable description of the planner capability."""
        return "Decomposes an intention into an ordered, engine-assigned plan."

    def receive_intention(self, raw_intention: object) -> Intention:
        """Normalize a raw caller request into a structured ``Intention``."""
        raise NotImplementedError

    def create_plan(self, intention: Intention) -> Plan:
        """Decompose *intention* into an ordered, executable ``Plan``."""
        raise NotImplementedError

    def select_engines(self, intention: Intention) -> Sequence[EngineSelection]:
        """Choose which cognitive engine should handle each part of the work."""
        raise NotImplementedError

    def order_execution(self, steps: Sequence[PlanStep]) -> Plan:
        """Resolve dependencies among *steps* into a final ordered ``Plan``."""
        raise NotImplementedError


__all__ = ["PlannerEngine", "PlannerError"]
