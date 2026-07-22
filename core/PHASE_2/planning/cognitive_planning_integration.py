"""Cognitive Planning Integration (PR-051).

Integration layer between Planning Engine and the Cognitive Pipeline.
Provides planning-aware stages and event publishing.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.PHASE_2.planning.planner import Planner


# =============================================================================
# Planning Events
# =============================================================================


class PlanningEventType(str, Enum):
    """Types of planning events."""

    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"
    PLANNING_FAILED = "planning_failed"
    GOAL_DECOMPOSED = "goal_decomposed"
    TASK_CREATED = "task_created"
    TASK_SCHEDULED = "task_scheduled"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DEPENDENCY_RESOLVED = "dependency_resolved"


@dataclass
class PlanningEvent:
    """Planning event for the Event Bus."""

    event_type: PlanningEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    correlation_id: str = ""
    plan_id: str = ""
    task_id: str = ""
    duration_ms: float = 0.0
    task_count: int = 0
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Planning Event Publisher
# =============================================================================


class PlanningEventPublisher:
    """Publisher for planning events."""

    def __init__(self):
        """Initialize the publisher."""
        self._subscribers: list[callable] = []
        self._history: list[PlanningEvent] = []

    def subscribe(self, callback: callable) -> None:
        """Subscribe to planning events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from planning events."""
        self._subscribers.remove(callback)

    def publish(self, event: PlanningEvent) -> None:
        """Publish a planning event."""
        self._history.append(event)
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def get_history(
        self,
        session_id: str | None = None,
        event_type: PlanningEventType | None = None,
        limit: int = 100,
    ) -> list[PlanningEvent]:
        """Get event history."""
        history = self._history

        if session_id:
            history = [e for e in history if e.session_id == session_id]
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()


# =============================================================================
# Planning Metrics
# =============================================================================


@dataclass
class PlanningMetrics:
    """Metrics for planning operations."""

    total_plans_created: int = 0
    successful_plans: int = 0
    failed_plans: int = 0
    total_tasks_created: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_plan_duration_ms: float = 0.0
    average_tasks_per_plan: float = 0.0


# =============================================================================
# Planning Integration
# =============================================================================


class CognitivePlanningIntegration:
    """Integration layer for cognitive planning.

    Provides:
    - Event publishing for all planning operations
    - Metrics collection
    - Tracing
    """

    def __init__(self, engine: "CognitivePlanningEngine" = None):
        """Initialize the integration layer.

        Args:
            engine: The underlying planning engine.
        """
        from core.PHASE_2.planning.planner import CognitivePlanningEngine
        
        self._engine = engine or CognitivePlanningEngine()
        self._publisher = PlanningEventPublisher()
        self._metrics = PlanningMetrics()

    @property
    def engine(self) -> "CognitivePlanningEngine":
        """Get the underlying planner."""
        return self._engine

    @property
    def publisher(self) -> PlanningEventPublisher:
        """Get the event publisher."""
        return self._publisher

    @property
    def metrics(self) -> PlanningMetrics:
        """Get current metrics."""
        return self._metrics

    def create_plan(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
        session_id: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Create a plan with full instrumentation.

        Args:
            goal: The goal to plan for
            constraints: Planning constraints
            session_id: Session ID for tracking
            correlation_id: Correlation ID

        Returns:
            Plan result dictionary.
        """
        import time

        start = time.perf_counter()
        self._metrics.total_plans_created += 1

        try:
            # Publish start event
            self._publisher.publish(PlanningEvent(
                event_type=PlanningEventType.PLANNING_STARTED,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
            ))

            # Create plan
            result = self._engine.create_plan(
                goal=goal,
                constraints=constraints or {},
            )

            # Calculate duration
            duration_ms = (time.perf_counter() - start) * 1000
            task_count = len(result.get("tasks", []))

            # Publish completion event
            self._publisher.publish(PlanningEvent(
                event_type=PlanningEventType.PLANNING_COMPLETED,
                session_id=session_id,
                correlation_id=correlation_id,
                plan_id=result.get("plan_id", ""),
                duration_ms=duration_ms,
                task_count=task_count,
                success=True,
            ))

            # Update metrics
            self._metrics.successful_plans += 1
            self._metrics.total_tasks_created += task_count

            return {
                "success": True,
                "plan": result,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000

            # Publish failure event
            self._publisher.publish(PlanningEvent(
                event_type=PlanningEventType.PLANNING_FAILED,
                session_id=session_id,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            ))

            # Update metrics
            self._metrics.failed_plans += 1

            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms,
            }

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all planning metrics."""
        return {
            "metrics": {
                "total_plans_created": self._metrics.total_plans_created,
                "successful_plans": self._metrics.successful_plans,
                "failed_plans": self._metrics.failed_plans,
                "total_tasks_created": self._metrics.total_tasks_created,
                "total_tasks_completed": self._metrics.total_tasks_completed,
                "total_tasks_failed": self._metrics.total_tasks_failed,
                "average_plan_duration_ms": self._metrics.average_plan_duration_ms,
                "average_tasks_per_plan": self._metrics.average_tasks_per_plan,
            },
        }


def create_cognitive_planning_integration(
    engine: "CognitivePlanningEngine" = None,
) -> CognitivePlanningIntegration:
    """Create a cognitive planning integration."""
    return CognitivePlanningIntegration(engine=engine)
