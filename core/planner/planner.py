"""Planner — the cognitive planning capability of EREN.

Architecture scaffolding only. This module defines the **Planner** class: the
primary entry point for the planning capability. It coordinates the four
responsibilities (receive intention, create plan, select engines, order
execution) but contains no business logic, AI, or agents.

The class is structured so that each responsibility can be **injected** via
strategy protocols (see ``types.py``), enabling future evolution without
touching the pipeline skeleton.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from core.contracts.base import CognitiveEngine

from .exceptions import (
    EngineSelectionError,
    InvalidIntentionError,
    PlanCreationError,
    PlannerError,
    StepOrderingError,
)
from .models import CognitiveEngineId, EngineSelection, Intention, Plan, PlanStep
from .types import (
    EngineSelector,
    ExecutionContext,
    PlannerCallback,
    PlannerResult,
    PlanningStrategy,
    ReplanReason,
    StepOrderer,
    StepValidator,
    TaskPriority,
)

if TYPE_CHECKING:
    pass


class Planner(CognitiveEngine):
    """The primary planning capability of EREN.

    The Planner receives a **raw request** from the Orchestrator, normalizes it
    into an ``Intention``, decomposes it into ordered steps with engines
    assigned, and returns a ``PlannerResult`` wrapping the final ``Plan``.

    **Four responsibilities (no more, no less):**

    1. ``receive_intention`` — normalize a raw request into a structured
       ``Intention``.
    2. ``create_plan`` — decompose the intention into candidate ``PlanStep``.
    3. ``select_engines`` — assign a cognitive engine to each step.
    4. ``order_execution`` — resolve dependencies into a topologically-sorted
       ``Plan``.

    The Planner **does not**:

    - execute steps (that is the Orchestrator / Workflow Engine);
    - perform reasoning within a step (that is the Reasoning Engine);
    - interact with any delivery surface (``apps/*``);
    - call external services, databases, or LLM providers.

    Parameters
    ----------
    strategy : PlanningStrategy
        Pluggable decomposition strategy. Defaults to a basic rule-based
        implementation if not provided.
    selector : EngineSelector
        Pluggable engine selection strategy. Defaults to a static mapping if
        not provided.
    orderer : StepOrderer
        Pluggable dependency resolver. Defaults to Kahn's algorithm if not
        provided.
    validators : list[StepValidator]
        Ordered list of validators applied to each step before it is added
        to the plan.
    callbacks : list[PlannerCallback]
        Async callbacks invoked at pipeline milestones.
    """

    def __init__(
        self,
        strategy: PlanningStrategy | None = None,
        selector: EngineSelector | None = None,
        orderer: StepOrderer | None = None,
        validators: list[StepValidator] | None = None,
        callbacks: list[PlannerCallback] | None = None,
    ) -> None:
        self._strategy = strategy or _DefaultPlanningStrategy()
        self._selector = selector or _DefaultEngineSelector()
        self._orderer = orderer or _DefaultStepOrderer()
        self._validators = validators or []
        self._callbacks = callbacks or []

    # --------------------------------------------------------------------------
    # CognitiveEngine identity
    # --------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Stable identifier of this engine."""
        return "planner"

    def describe(self) -> str:
        """Human-readable description of the planner capability."""
        return (
            "Decomposes a clinical request into an ordered, engine-assigned plan "
            "with full traceability."
        )

    # --------------------------------------------------------------------------
    # Main entry point
    # --------------------------------------------------------------------------

    async def plan(
        self,
        raw_request: object,
        context: ExecutionContext | None = None,
    ) -> PlannerResult:
        """Transform a raw request into an executable ``PlannerResult``.

        This is the **single public entry point** for the planning capability.
        All four responsibilities are invoked in order; failures at any stage
        raise a typed ``PlannerError``.

        Parameters
        ----------
        raw_request
            The unstructured request from the Orchestrator. Can be a string,
            a dict, or any object the configured ``strategy`` can parse.
        context
            Ambient execution context. A default (empty) context is created
            if not provided.

        Returns
        -------
        PlannerResult
            Wraps the final ``Plan`` together with priority, metadata, and
            warnings.

        Raises
        ------
        InvalidIntentionError
            If the raw request cannot be normalized into an ``Intention``.
        PlanCreationError
            If the strategy fails to decompose the intention.
        EngineSelectionError
            If the selector cannot assign an engine to every step.
        StepOrderingError
            If the orderer cannot resolve step dependencies.
        """
        ctx = context or ExecutionContext()

        # 1. Receive intention
        await self._emit("intention_received", {"raw": str(raw_request)[:200]})
        intention = self._receive_intention(raw_request)

        # 2. Create plan
        await self._emit("plan_creation_started", {"goal": intention.goal})
        steps = self._create_plan(intention, ctx)

        # 3. Select engines
        await self._emit("engine_selection_started", {"step_count": len(steps)})
        steps = self._select_engines(steps, ctx)

        # 4. Order execution
        await self._emit("step_ordering_started", {"step_count": len(steps)})
        plan = self._order_execution(steps, intention)

        # Build result
        priority = self._infer_priority(intention, ctx)
        warnings = self._collect_warnings(steps, ctx)
        requires_confirmation = self._requires_confirmation(steps, priority)

        result = PlannerResult(
            plan=plan,
            priority=priority,
            estimated_steps=len(steps),
            requires_confirmation=requires_confirmation,
            warnings=warnings,
            metadata={"strategy": self._strategy.__class__.__name__},
        )

        await self._emit("plan_completed", {
            "plan_id": id(plan),
            "steps": len(steps),
            "priority": priority.name,
        })

        return result

    async def replan(
        self,
        previous_plan: Plan,
        reason: ReplanReason,
        context: ExecutionContext,
    ) -> PlannerResult:
        """Revise *previous_plan* after a failure or significant change.

        The default implementation discards the failed plan and replans from
        the current context. Subclasses may implement more sophisticated
        recovery strategies (e.g., retry the failed step, skip it, substitute
        an alternative engine).

        Parameters
        ----------
        previous_plan
            The plan that failed or needs revision.
        reason
            Why replanning is needed (see ``ReplanReason``).
        context
            Updated execution context (may contain new information).

        Returns
        -------
        PlannerResult
            A new plan addressing the same intention.
        """
        await self._emit("replan_started", {
            "reason": reason,
            "original_steps": len(previous_plan.steps),
        })

        # Default strategy: full replan from the original intention
        return await self.plan(previous_plan.intention.goal, context)

    # --------------------------------------------------------------------------
    # Responsibility 1: Receive intention
    # --------------------------------------------------------------------------

    def _receive_intention(self, raw: object) -> Intention:
        """Normalize a raw request into a structured ``Intention``.

        The default implementation accepts strings and dicts. Override to
        support additional input shapes or to extract structured fields
        (goal_type, entities, constraints) from the raw input.
        """
        if isinstance(raw, str):
            goal = raw.strip()
        elif isinstance(raw, dict):
            goal = str(raw.get("goal", ""))
        else:
            raise InvalidIntentionError(
                f"Cannot normalize {type(raw).__name__} into Intention. "
                "Expected str or dict with 'goal' key."
            )

        if not goal:
            raise InvalidIntentionError("Intention goal cannot be empty.")

        return Intention(goal=goal)

    # --------------------------------------------------------------------------
    # Responsibility 2: Create plan
    # --------------------------------------------------------------------------

    def _create_plan(self, intention: Intention, context: ExecutionContext) -> list[PlanStep]:
        """Decompose *intention* into candidate ``PlanStep``.

        Delegates to the injected ``PlanningStrategy``. Steps are returned in
        discovery order; the orderer may reorder them.

        Each step is validated by every configured ``StepValidator`` before
        being added to the list.
        """
        raw_steps = self._strategy.decompose(intention, context)
        validated: list[PlanStep] = []

        for i, step in enumerate(raw_steps):
            step = replace(step, order=i)
            if all(v(step, context) for v in self._validators):
                validated.append(step)
            else:
                # Log but continue — a single bad step does not abort planning
                # pylint: disable-next=broad-except
                pass

        return validated

    # --------------------------------------------------------------------------
    # Responsibility 3: Select engines
    # --------------------------------------------------------------------------

    def _select_engines(
        self,
        steps: list[PlanStep],
        context: ExecutionContext,
    ) -> list[PlanStep]:
        """Assign a cognitive engine to each step.

        Delegates to the injected ``EngineSelector``. Returns the same steps
        with their ``selection`` field populated.
        """
        return self._selector.select(steps, context)

    # --------------------------------------------------------------------------
    # Responsibility 4: Order execution
    # --------------------------------------------------------------------------

    def _order_execution(self, steps: list[PlanStep], intention: Intention) -> Plan:
        """Resolve dependencies into a topologically-sorted ``Plan``.

        Delegates to the injected ``StepOrderer``.
        """
        ordered = self._orderer.order(steps)

        # Re-assign order after sorting
        ordered = [replace(s, order=i) for i, s in enumerate(ordered)]

        return Plan(intention=intention, steps=tuple(ordered))

    # --------------------------------------------------------------------------
    # Helper methods
    # --------------------------------------------------------------------------

    def _infer_priority(self, intention: Intention, context: ExecutionContext) -> TaskPriority:
        """Infer task priority from intention and context."""
        if context.urgency != TaskPriority.NORMAL:
            return context.urgency

        goal_lower = intention.goal.lower()
        if any(kw in goal_lower for kw in ("emergency", "crítico", "urgente", "critical")):
            return TaskPriority.CRITICAL
        if any(kw in goal_lower for kw in ("mantenimiento", "revisión", "calibración")):
            return TaskPriority.HIGH

        return TaskPriority.NORMAL

    def _requires_confirmation(self, steps: list[PlanStep], priority: TaskPriority) -> bool:
        """Determine whether the plan requires user confirmation before execution."""
        if priority == TaskPriority.CRITICAL:
            return True
        if any(s.selection.engine == CognitiveEngineId.TOOLS for s in steps):
            return True
        return False

    def _collect_warnings(self, steps: list[PlanStep], context: ExecutionContext) -> tuple[str, ...]:
        """Collect advisory warnings from steps and context."""
        warnings: list[str] = []

        if not steps:
            warnings.append("No steps generated — plan may be incomplete.")

        if context.urgency == TaskPriority.CRITICAL and len(steps) > 5:
            warnings.append("Critical plan with many steps — verify all are essential.")

        return tuple(warnings)

    async def _emit(self, event: str, data: dict[str, Any]) -> None:
        """Invoke all registered callbacks."""
        for cb in self._callbacks:
            await cb(event, data)


# ==============================================================================
# Default strategy implementations (scaffolded)
# ==============================================================================


class _DefaultPlanningStrategy:
    """Basic rule-based planning strategy.

    Architecture scaffolding. Produces a generic sequence of steps based on
    keyword matching. Replace with a more sophisticated strategy (LLM-assisted,
    tree-search, etc.) when ready.
    """

    def decompose(self, intention: Intention, context: ExecutionContext) -> list[PlanStep]:
        """Decompose *intention* into a fixed generic sequence.

        This is intentionally naive. The real implementation will use the
        Clinical Reasoning Framework (§3) to guide decomposition.
        """
        goal = intention.goal.lower()
        steps: list[PlanStep] = []
        order = 0

        # Step 1: Identify context
        if context.hospital_id:
            steps.append(PlanStep(order=order, selection=EngineSelection(
                engine=CognitiveEngineId.MEMORY,
                rationale="Hospital context identified in session.",
            ), description="Retrieve hospital context"))
            order += 1

        # Step 2: Search knowledge base
        steps.append(PlanStep(order=order, selection=EngineSelection(
            engine=CognitiveEngineId.KNOWLEDGE,
            rationale="Device/service manual lookup.",
        ), description="Search technical knowledge"))
        order += 1

        # Step 3: Query memory
        if context.device_id:
            steps.append(PlanStep(order=order, selection=EngineSelection(
                engine=CognitiveEngineId.MEMORY,
                rationale="Device history retrieval.",
            ), description="Retrieve device maintenance history"))
            order += 1

        # Step 4: Diagnostic reasoning
        if any(kw in goal for kw in ("diagnostic", "error", "falla", "problem", "issue")):
            steps.append(PlanStep(order=order, selection=EngineSelection(
                engine=CognitiveEngineId.REASONING,
                rationale="Hypothesis generation and evaluation.",
            ), description="Generate diagnostic hypotheses"))
            order += 1

        # Step 5: Risk assessment
        if any(kw in goal for kw in ("safety", "riesgo", "critical", "paciente")):
            steps.append(PlanStep(order=order, selection=EngineSelection(
                engine=CognitiveEngineId.DIAGNOSTIC,
                rationale="Clinical risk evaluation.",
            ), description="Assess clinical risk"))
            order += 1

        # Step 6: Build response
        steps.append(PlanStep(order=order, selection=EngineSelection(
            engine=CognitiveEngineId.REASONING,
            rationale="Construct evidence-based response.",
        ), description="Construct response"))

        return steps


class _DefaultEngineSelector:
    """Basic static engine selector.

    Architecture scaffolding. Uses a static mapping from step description
    keywords to engines. Replace with a learned or LLM-assisted selector
    when ready.
    """

    def select(self, steps: list[PlanStep], context: ExecutionContext) -> list[PlanStep]:
        """Assign engines based on static keyword rules."""
        updated: list[PlanStep] = []

        for step in steps:
            if step.selection.rationale:
                # Already assigned (e.g., by _DefaultPlanningStrategy)
                updated.append(step)
                continue

            # Default assignment
            selection = EngineSelection(
                engine=CognitiveEngineId.REASONING,
                rationale="Default engine assignment (fallback).",
            )

            updated.append(replace(step, selection=selection))

        return updated


class _DefaultStepOrderer:
    """Basic topological sort using Kahn's algorithm.

    Architecture scaffolding. Resolves ``depends_on`` dependencies into a
    linear order. Handles cycles by returning the original order.
    """

    def order(self, steps: list[PlanStep]) -> list[PlanStep]:
        """Return steps in topologically-sorted order."""
        if not steps:
            return []

        # Build adjacency list and in-degree map
        n = len(steps)
        in_degree = dict.fromkeys(range(n), 0)
        dependents: dict[int, list[int]] = {i: [] for i in range(n)}

        for i, step in enumerate(steps):
            for dep in step.depends_on:
                if 0 <= dep < n:
                    in_degree[i] += 1
                    dependents[dep].append(i)

        # Kahn's algorithm
        queue = [i for i in range(n) if in_degree[i] == 0]
        sorted_indices: list[int] = []

        while queue:
            current = queue.pop(0)
            sorted_indices.append(current)
            for nxt in dependents[current]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        # If not all nodes are sorted, there is a cycle — return original order
        if len(sorted_indices) != n:
            return steps

        return [steps[i] for i in sorted_indices]


__all__ = [
    "EngineSelectionError",
    "InvalidIntentionError",
    "PlanCreationError",
    "Planner",
    "PlannerError",
    "StepOrderingError",
]
