"""Orchestrator engine for EREN core — the heart of EREN.

The central nervous system that coordinates all cognitive engines.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .exceptions import OrchestratorError, EngineNotFoundError, PlanExecutionError
from .interfaces import EngineRegistry
from .models import CognitiveContext, EngineResponse, OrchestrationResult, PlanStep


class OrchestrationState(str, Enum):
    IDLE = "idle"
    RECEIVING = "receiving"
    PLANNING = "planning"
    EXECUTING = "executing"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExecutionMetrics:
    """Metrics for an orchestration execution."""
    start_time: datetime
    end_time: datetime | None = None
    step_count: int = 0
    engine_invocations: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> int:
        """Calculate duration in milliseconds."""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return 0


class OrchestratorEngine:
    """
    Coordinates EREN's cognitive engines across a request lifecycle.

    The central nervous system: it **receives a context**, **executes a plan**,
    **invokes engines**, **merges their responses**, and **returns a result**.

    It is the only engine that knows about the others; each other engine stays
    independent and is composed *by* the orchestrator. It delegates — it does
    not plan, reason, or implement domain logic itself.

    Engines are injected as a registry (Dependency Inversion): the orchestrator
    depends only on the ``CognitiveEngine`` abstraction, never on concrete
    engine classes.
    """

    def __init__(self, engines: EngineRegistry | None = None) -> None:
        self._engines: EngineRegistry = engines if engines is not None else {}
        self._state = OrchestrationState.IDLE
        self._current_metrics: ExecutionMetrics | None = None

    @property
    def name(self) -> str:
        """Stable identifier of this engine."""
        return "orchestrator"

    @property
    def state(self) -> OrchestrationState:
        """Current orchestration state."""
        return self._state

    def describe(self) -> str:
        """Human-readable description of the orchestrator capability."""
        return "Coordinates cognitive engines across a request lifecycle."

    def register_engine(self, engine_id: str, engine: Any) -> None:
        """
        Register a cognitive engine.

        Args:
            engine_id: Unique identifier for the engine
            engine: Engine instance implementing CognitiveEngine interface
        """
        self._engines[engine_id] = engine

    def unregister_engine(self, engine_id: str) -> bool:
        """
        Unregister a cognitive engine.

        Args:
            engine_id: Engine identifier

        Returns:
            True if engine was removed, False if not found
        """
        if engine_id in self._engines:
            del self._engines[engine_id]
            return True
        return False

    def list_engines(self) -> list[str]:
        """List all registered engine IDs."""
        return list(self._engines.keys())

    async def orchestrate(self, context: CognitiveContext) -> OrchestrationResult:
        """
        Receive a *context*, run it to completion, and return the result.

        This is the main entry point for orchestration. It:
        1. Validates the context
        2. Creates a plan from the context
        3. Executes the plan
        4. Merges responses into a result

        Args:
            context: The cognitive context to process

        Returns:
            OrchestrationResult with the final output
        """
        self._state = OrchestrationState.RECEIVING
        self._current_metrics = ExecutionMetrics(start_time=datetime.now())

        try:
            # Step 1: Validate context
            self._validate_context(context)

            # Step 2: Create plan
            self._state = OrchestrationState.PLANNING
            plan = self._create_plan(context)

            # Step 3: Execute plan
            self._state = OrchestrationState.EXECUTING
            responses = await self.execute_plan(context, plan)

            # Step 4: Merge responses
            self._state = OrchestrationState.MERGING
            result = await self.merge_responses(context, responses)

            self._state = OrchestrationState.COMPLETED
            self._current_metrics.end_time = datetime.now()

            return result

        except Exception as e:
            self._state = OrchestrationState.FAILED
            if self._current_metrics:
                self._current_metrics.errors.append(str(e))

            raise OrchestratorError(f"Orchestration failed: {e}") from e

    def _validate_context(self, context: CognitiveContext) -> None:
        """Validate the incoming context."""
        if not context.request:
            raise OrchestratorError("Context request cannot be empty")

        if not context.tenant_id:
            raise OrchestratorError("Context tenant_id is required")

    def _create_plan(self, context: CognitiveContext) -> list[PlanStep]:
        """
        Create an execution plan from the context.

        This is a simple rule-based planner. In production, this would
        use a more sophisticated planning algorithm.

        Args:
            context: The cognitive context

        Returns:
            Ordered list of plan steps
        """
        steps = []

        # Always start with reasoning
        steps.append(PlanStep(
            step_id="step-1",
            engine="reasoning",
            action="reason",
            input_data={"question": context.request},
            depends_on=[],
        ))

        # Add RAG if knowledge query detected
        if self._is_knowledge_query(context.request):
            steps.append(PlanStep(
                step_id="step-2",
                engine="rag",
                action="retrieve",
                input_data={"query": context.request},
                depends_on=["step-1"],
            ))

        # Add tools if action detected
        if self._is_action_query(context.request):
            steps.append(PlanStep(
                step_id="step-3",
                engine="tools",
                action="execute",
                input_data={"task": context.request},
                depends_on=["step-1"],
            ))

        # Always end with response synthesis
        steps.append(PlanStep(
            step_id="step-final",
            engine="synthesis",
            action="synthesize",
            input_data={},
            depends_on=[s.step_id for s in steps],
        ))

        return steps

    def _is_knowledge_query(self, request: str) -> bool:
        """Determine if request is a knowledge query."""
        knowledge_keywords = [
            "what", "how", "explain", "describe", "tell me",
            "information", "knowledge", "docs", "documentation",
        ]
        return any(kw in request.lower() for kw in knowledge_keywords)

    def _is_action_query(self, request: str) -> bool:
        """Determine if request requires action."""
        action_keywords = [
            "do", "execute", "run", "start", "stop",
            "create", "update", "delete", "fix", "check",
        ]
        return any(kw in request.lower() for kw in action_keywords)

    async def execute_plan(
        self,
        context: CognitiveContext,
        plan: list[PlanStep],
    ) -> Sequence[EngineResponse]:
        """
        Execute *plan* against *context*.

        Args:
            context: The cognitive context
            plan: Ordered steps to execute

        Returns:
            List of engine responses
        """
        responses = []
        completed_steps: set[str] = set()

        for step in plan:
            # Check dependencies
            if not self._dependencies_met(step, completed_steps):
                raise PlanExecutionError(
                    f"Dependencies not met for step {step.step_id}"
                )

            # Invoke engine
            try:
                response = await self.invoke_engine(step.engine, context, step)
                responses.append(response)
                completed_steps.add(step.step_id)

                if self._current_metrics:
                    self._current_metrics.engine_invocations += 1
                    self._current_metrics.step_count += 1

            except EngineNotFoundError:
                # Skip if engine not found, continue with other steps
                responses.append(EngineResponse(
                    engine=step.engine,
                    success=False,
                    output=None,
                    error=f"Engine {step.engine} not found",
                    confidence=0.0,
                    metadata={},
                ))

        return responses

    def _dependencies_met(self, step: PlanStep, completed: set[str]) -> bool:
        """Check if all dependencies are met."""
        if not step.depends_on:
            return True
        return all(dep in completed for dep in step.depends_on)

    async def invoke_engine(
        self,
        engine_id: str,
        context: CognitiveContext,
        step: PlanStep,
    ) -> EngineResponse:
        """
        Delegate one unit of work to the cognitive engine.

        Args:
            engine_id: Engine identifier
            context: The cognitive context
            step: The plan step to execute

        Returns:
            EngineResponse with the engine's output
        """
        engine = self._engines.get(engine_id)

        if engine is None:
            raise EngineNotFoundError(f"Engine not found: {engine_id}")

        try:
            # Check if engine has async process method
            if hasattr(engine, "process_async"):
                output = await engine.process_async(context, step.action, step.input_data)
            elif hasattr(engine, "process"):
                output = engine.process(context, step.action, step.input_data)
            else:
                # Simple fallback
                output = {"status": "processed", "engine": engine_id}

            return EngineResponse(
                engine=engine_id,
                success=True,
                output=output,
                error=None,
                confidence=0.9,  # Default confidence
                metadata={"step_id": step.step_id, "action": step.action},
            )

        except Exception as e:
            return EngineResponse(
                engine=engine_id,
                success=False,
                output=None,
                error=str(e),
                confidence=0.0,
                metadata={"step_id": step.step_id},
            )

    async def merge_responses(
        self,
        context: CognitiveContext,
        responses: Sequence[EngineResponse],
    ) -> OrchestrationResult:
        """
        Fuse per-engine *responses* into a single explainable result.

        Args:
            context: Original cognitive context
            responses: Engine responses to merge

        Returns:
            Final orchestration result
        """
        # Filter successful responses
        successful = [r for r in responses if r.success]
        failed = [r for r in responses if not r.success]

        # Calculate overall confidence
        if successful:
            confidences = [r.confidence for r in successful]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = 0.0

        # Merge outputs
        merged_output = self._merge_outputs(successful)

        # Build execution summary
        execution_summary = {
            "engines_used": [r.engine for r in successful],
            "engines_failed": [r.engine for r in failed],
            "total_steps": len(responses),
            "successful_steps": len(successful),
            "failed_steps": len(failed),
        }

        if self._current_metrics:
            execution_summary["duration_ms"] = self._current_metrics.duration_ms

        return OrchestrationResult(
            context=context,
            responses=list(responses),
            output=merged_output,
            success=len(failed) == 0,
            confidence=avg_confidence,
            execution_summary=execution_summary,
        )

    def _merge_outputs(self, responses: Sequence[EngineResponse]) -> dict[str, Any]:
        """Merge outputs from multiple engines."""
        merged = {
            "primary": None,
            "supporting": [],
            "errors": [],
        }

        for response in responses:
            if response.output:
                if merged["primary"] is None:
                    merged["primary"] = response.output
                else:
                    merged["supporting"].append(response.output)

            if response.error:
                merged["errors"].append({
                    "engine": response.engine,
                    "error": response.error,
                })

        return merged

    def get_metrics(self) -> ExecutionMetrics | None:
        """Get current execution metrics."""
        return self._current_metrics


# Global instance
_orchestrator: OrchestratorEngine | None = None


def get_orchestrator() -> OrchestratorEngine:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorEngine()
    return _orchestrator
