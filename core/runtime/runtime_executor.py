"""Runtime executor for the Cognitive Operating System.

Executes the complete cognitive cycle through all engines,
coordinating the flow from planning through reasoning to action.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .runtime_context import CycleContext, RuntimeContext, SessionContext
from .runtime_events import (
    ActionExecuted,
    ActionGenerated,
    CognitiveCycleCompleted,
    CognitiveCycleFailed,
    CognitiveCycleStarted,
    ContextUpdated,
    DecisionCreated,
    KnowledgeRetrieved,
    MemoryRetrieved,
    PlanningCompleted,
    PlanningStarted,
    ReasoningCompleted,
    RuntimeEvent,
    RuntimeEventType,
    SessionCompleted,
    SessionCreated,
    SessionFailed,
    SessionStarted,
)
from .runtime_metrics import CycleMetrics, RuntimeMetrics
from .runtime_trace import RuntimeTraceCollector


@dataclass
class ExecutionResult:
    """Result of an engine execution."""

    engine_name: str
    success: bool
    duration_ms: int
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = None


class CognitiveCycleExecutor:
    """Executes the complete cognitive cycle.

    Coordinates the flow through all cognitive engines:
    1. Planning - Create a plan based on intent
    2. Knowledge - Retrieve relevant knowledge
    3. Memory - Retrieve relevant memories
    4. Reasoning - Generate hypotheses from evidence
    5. Decision - Make decisions based on hypotheses
    6. Action - Generate and execute actions
    7. Context Update - Update the cognitive context
    """

    def __init__(
        self,
        context: RuntimeContext,
        trace: RuntimeTraceCollector,
        metrics: RuntimeMetrics,
        simulation_mode: bool = True,
        simulation_delay_ms: int = 100,
    ):
        """Initialize the executor.

        Args:
            context: Runtime context.
            trace: Trace collector.
            metrics: Runtime metrics.
            simulation_mode: Whether to use simulation (no real AI).
            simulation_delay_ms: Delay between simulated steps.
        """
        self._context = context
        self._trace = trace
        self._metrics = metrics
        self._simulation_mode = simulation_mode
        self._simulation_delay_ms = simulation_delay_ms
        self._event_handlers: list[callable] = []

    def add_event_handler(self, handler: callable) -> None:
        """Add an event handler.

        Args:
            handler: Function to call with events.
        """
        self._event_handlers.append(handler)

    def execute_cycle(
        self,
        session: SessionContext,
        intent: dict[str, Any],
    ) -> CycleContext:
        """Execute a complete cognitive cycle.

        Args:
            session: The session context.
            intent: The initial intent.

        Returns:
            The cycle context with results.
        """
        # Create cycle context
        cycle = self._context.create_cycle()
        cycle.start()

        # Store intent
        session.intent = intent

        # Emit cycle started event
        self._publish_event(CognitiveCycleStarted(
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            payload={
                "cycle_id": cycle.cycle_id,
                "intent": intent,
            },
        ))

        self._trace.add_entry(
            operation="cycle_started",
            category="cognitive_cycle",
            component="executor",
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            cycle_id=cycle.cycle_id,
        )

        try:
            # Execute each stage of the cognitive cycle
            self._execute_planning(session, cycle, intent)
            self._execute_knowledge_retrieval(session, cycle)
            self._execute_memory_retrieval(session, cycle)
            self._execute_reasoning(session, cycle)
            self._execute_decision(session, cycle)
            self._execute_action(session, cycle)
            self._execute_context_update(session, cycle)

            # Complete cycle successfully
            cycle.complete(success=True)
            session.complete_cycle()

            # Emit completion events
            self._publish_event(CognitiveCycleCompleted(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "cycle_id": cycle.cycle_id,
                    "duration_ms": cycle.duration_ms,
                    "stages_completed": len(cycle.stages),
                },
            ))

            self._trace.add_entry(
                operation="cycle_completed",
                category="cognitive_cycle",
                component="executor",
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                cycle_id=cycle.cycle_id,
                duration_ms=cycle.duration_ms,
            )

            # Update metrics
            self._metrics.record_cycle_completed(
                cycle_id=cycle.cycle_id,
                duration_ms=cycle.duration_ms,
                stages_executed=len(cycle.stages),
                events_published=len(session.events_published),
                engines_executed=len(session.engines_executed),
                success=True,
            )

        except Exception as e:
            # Complete cycle with failure
            cycle.complete(success=False, error=str(e))
            session.complete_cycle()
            session.add_error(str(e))

            self._publish_event(CognitiveCycleFailed(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "cycle_id": cycle.cycle_id,
                    "error": str(e),
                },
            ))

            self._trace.add_entry(
                operation="cycle_failed",
                category="cognitive_cycle",
                component="executor",
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                cycle_id=cycle.cycle_id,
                success=False,
                error=str(e),
            )

            self._metrics.record_cycle_completed(
                cycle_id=cycle.cycle_id,
                duration_ms=cycle.duration_ms,
                stages_executed=len(cycle.stages),
                events_published=len(session.events_published),
                engines_executed=len(session.engines_executed),
                success=False,
                error=str(e),
            )

        return cycle

    def _execute_planning(
        self,
        session: SessionContext,
        cycle: CycleContext,
        intent: dict[str, Any],
    ) -> None:
        """Execute the planning stage.

        Args:
            session: Session context.
            cycle: Cycle context.
            intent: Intent data.
        """
        stage_name = "planning"
        session.set_stage(stage_name)

        self._publish_event(PlanningStarted(
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            payload={"intent": intent},
        ))

        start_time = datetime.now(timezone.utc)
        engine_name = "planner"
        session.add_engine_executed(engine_name)

        try:
            # Simulate planning execution
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Create simulated plan result
            plan_result = {
                "plan_id": f"plan_{uuid4().hex[:16]}",
                "steps": [
                    {"step_id": 1, "description": "Analyze intent", "engine": "planner"},
                    {"step_id": 2, "description": "Retrieve knowledge", "engine": "knowledge"},
                    {"step_id": 3, "description": "Retrieve memory", "engine": "memory"},
                    {"step_id": 4, "description": "Generate hypotheses", "engine": "reasoning"},
                    {"step_id": 5, "description": "Make decision", "engine": "decision"},
                    {"step_id": 6, "description": "Execute action", "engine": "tools"},
                ],
                "estimated_duration_ms": 5000,
            }

            session.plan = plan_result
            cycle.plan_result = plan_result

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(PlanningCompleted(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "plan_id": plan_result["plan_id"],
                    "steps": len(plan_result["steps"]),
                    "duration_ms": duration_ms,
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_knowledge_retrieval(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute knowledge retrieval.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "knowledge_retrieval"
        session.set_stage(stage_name)

        self._publish_event(RuntimeEvent(
            event_type=RuntimeEventType.KNOWLEDGE_REQUESTED,
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            payload={"query": session.intent.get("query", "")},
        ))

        start_time = datetime.now(timezone.utc)
        engine_name = "knowledge_engine"
        session.add_engine_executed(engine_name)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Simulated knowledge results
            knowledge_result = {
                "knowledge_ids": [f"kn_{uuid4().hex[:16]}" for _ in range(3)],
                "results": [
                    {"id": f"kn_{uuid4().hex[:16]}", "relevance": 0.9, "content": "Simulated knowledge"},
                    {"id": f"kn_{uuid4().hex[:16]}", "relevance": 0.7, "content": "Simulated knowledge"},
                ],
            }

            session.knowledge_results = knowledge_result["results"]
            cycle.knowledge_result = knowledge_result

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(KnowledgeRetrieved(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "results_count": len(knowledge_result["results"]),
                    "duration_ms": duration_ms,
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_memory_retrieval(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute memory retrieval.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "memory_retrieval"
        session.set_stage(stage_name)

        self._publish_event(RuntimeEvent(
            event_type=RuntimeEventType.MEMORY_REQUESTED,
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            payload={"query": session.intent.get("query", "")},
        ))

        start_time = datetime.now(timezone.utc)
        engine_name = "memory_engine"
        session.add_engine_executed(engine_name)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Simulated memory results
            memory_result = {
                "memory_ids": [f"mem_{uuid4().hex[:16]}" for _ in range(2)],
                "results": [
                    {"id": f"mem_{uuid4().hex[:16]}", "relevance": 0.8, "content": "Simulated memory"},
                ],
            }

            session.memory_results = memory_result["results"]
            cycle.memory_result = memory_result

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(MemoryRetrieved(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "results_count": len(memory_result["results"]),
                    "duration_ms": duration_ms,
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_reasoning(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute reasoning.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "reasoning"
        session.set_stage(stage_name)

        self._publish_event(RuntimeEvent(
            event_type=RuntimeEventType.REASONING_STARTED,
            session_id=session.session_id,
            correlation_id=session.correlation_id,
            payload={
                "evidence_count": len(session.knowledge_results) + len(session.memory_results),
            },
        ))

        start_time = datetime.now(timezone.utc)
        engine_name = "reasoning_engine"
        session.add_engine_executed(engine_name)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Simulated reasoning results - generate hypotheses
            hypotheses = []
            for i in range(3):
                hyp_id = f"hyp_{uuid4().hex[:16]}"
                hypotheses.append({
                    "id": hyp_id,
                    "description": f"Simulated hypothesis {i + 1}",
                    "probability": 0.7 - (i * 0.15),
                    "confidence": 0.8 - (i * 0.1),
                })
                session.hypotheses.append({
                    "hypothesis_id": hyp_id,
                    "description": f"Simulated hypothesis {i + 1}",
                    "probability": 0.7 - (i * 0.15),
                })

            reasoning_result = {
                "hypotheses": hypotheses,
                "best_hypothesis": hypotheses[0]["id"] if hypotheses else None,
                "evidence_used": len(session.evidence),
            }

            cycle.reasoning_result = reasoning_result

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(ReasoningCompleted(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "hypotheses_count": len(hypotheses),
                    "best_hypothesis": reasoning_result["best_hypothesis"],
                    "duration_ms": duration_ms,
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_decision(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute decision making.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "decision"
        session.set_stage(stage_name)

        start_time = datetime.now(timezone.utc)
        engine_name = "decision_engine"
        session.add_engine_executed(engine_name)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Get best hypothesis
            best_hypothesis = session.hypotheses[0] if session.hypotheses else None

            # Create decision
            decision_id = f"dec_{uuid4().hex[:16]}"
            decision = {
                "decision_id": decision_id,
                "type": "action_decision",
                "based_on_hypothesis": best_hypothesis.get("hypothesis_id") if best_hypothesis else None,
                "confidence": best_hypothesis.get("probability", 0.5) if best_hypothesis else 0.5,
                "action": "Simulated diagnostic action",
            }

            session.decisions.append(decision)
            cycle.decision_result = decision

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(DecisionCreated(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "decision_id": decision_id,
                    "based_on_hypothesis": decision["based_on_hypothesis"],
                    "confidence": decision["confidence"],
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_action(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute action.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "action"
        session.set_stage(stage_name)

        start_time = datetime.now(timezone.utc)
        engine_name = "tool_engine"
        session.add_engine_executed(engine_name)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Get latest decision
            decision = session.decisions[-1] if session.decisions else {}

            # Generate action
            action_id = f"act_{uuid4().hex[:16]}"
            action = {
                "action_id": action_id,
                "type": "diagnostic_action",
                "parameters": decision,
                "status": "executed",
                "result": "Simulated action execution completed successfully",
            }

            session.actions.append(action)
            cycle.action_result = action

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=True)

            self._publish_event(ActionGenerated(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "action_id": action_id,
                    "action_type": action["type"],
                },
            ))

            self._publish_event(ActionExecuted(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "action_id": action_id,
                    "duration_ms": duration_ms,
                },
            ))

            self._metrics.record_engine_execution(engine_name, duration_ms, True)

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, engine_name, duration_ms, success=False, error=str(e))
            self._metrics.record_engine_execution(engine_name, duration_ms, False)
            raise

    def _execute_context_update(
        self,
        session: SessionContext,
        cycle: CycleContext,
    ) -> None:
        """Execute context update.

        Args:
            session: Session context.
            cycle: Cycle context.
        """
        stage_name = "context_update"
        session.set_stage(stage_name)

        start_time = datetime.now(timezone.utc)

        try:
            if self._simulation_mode:
                self._simulate_execution(stage_name)

            # Simulate context update
            updated_context = {
                "context_id": session.context_id,
                "version": len(session.stages_completed) + 1,
                "updated_fields": ["plan", "knowledge_results", "memory_results", "hypotheses", "decisions", "actions"],
            }

            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, "cognitive_context", duration_ms, success=True)

            self._publish_event(ContextUpdated(
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "context_id": session.context_id,
                    "updated_fields": updated_context["updated_fields"],
                    "version": updated_context["version"],
                },
            ))

        except Exception as e:
            duration_ms = self._get_duration_ms(start_time)
            cycle.add_stage(stage_name, "cognitive_context", duration_ms, success=False, error=str(e))
            raise

    def _publish_event(self, event: RuntimeEvent) -> None:
        """Publish an event.

        Args:
            event: The event to publish.
        """
        # Update session event count
        if self._context.current_session:
            self._context.current_session.add_event(event.event_type.value)

        # Record in trace
        self._trace.record_event_publication(
            event_type=event.event_type.value,
            session_id=event.session_id,
            correlation_id=event.correlation_id,
        )

        # Record in metrics
        self._metrics.record_event_published()

        # Call event handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass  # Don't let handler errors break execution

    def _simulate_execution(self, stage_name: str) -> None:
        """Simulate execution delay.

        Args:
            stage_name: Name of the stage being simulated.
        """
        if self._simulation_delay_ms > 0:
            import time
            time.sleep(self._simulation_delay_ms / 1000.0)

    def _get_duration_ms(self, start_time: datetime) -> int:
        """Calculate duration from start time.

        Args:
            start_time: Start timestamp.

        Returns:
            Duration in milliseconds.
        """
        return int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
