"""Abstract interfaces (ports) for the Planner engine.

Defines the contract the planner exposes to the rest of EREN core. Pure
``typing.Protocol`` — method signatures only, no logic, AI, or agents.

The port declares the planner's four responsibilities as an explicit pipeline:

1. **receive intention** — normalize a raw request into an ``Intention``.
2. **create plan** — decompose the intention into ordered ``PlanStep`` s.
3. **select engines** — decide which cognitive engine handles each step.
4. **order execution** — resolve dependencies into a final ordered ``Plan``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from .models import EngineSelection, Intention, Plan, PlanStep


@runtime_checkable
class PlannerPort(Protocol):
    """Contract the Planner engine exposes to callers (e.g. the orchestrator).

    Consumers depend on this abstraction rather than on ``PlannerEngine`` so the
    planner is substitutable (Dependency Inversion / Liskov). Complements the
    generic ``core.contracts.Planner`` contract with the planner-local pipeline.
    """

    def receive_intention(self, raw_intention: object) -> Intention:
        """Normalize a raw caller request into a structured ``Intention``."""
        ...

    def create_plan(self, intention: Intention) -> Plan:
        """Decompose *intention* into an ordered, executable ``Plan``."""
        ...

    def select_engines(self, intention: Intention) -> Sequence[EngineSelection]:
        """Choose which cognitive engine should handle each part of the work."""
        ...

    def order_execution(self, steps: Sequence[PlanStep]) -> Plan:
        """Resolve dependencies among *steps* into a final ordered ``Plan``."""
        ...
