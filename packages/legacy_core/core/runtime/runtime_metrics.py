"""Runtime metrics for the Cognitive Operating System.

Collects and tracks all metrics during runtime operation, including
timing, counts, and performance data for the cognitive cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StageMetrics:
    """Metrics for a specific cognitive cycle stage."""

    stage_name: str
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleMetrics:
    """Metrics for a complete cognitive cycle."""

    cycle_id: str
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    stages: list[StageMetrics] = field(default_factory=list)
    events_published: int = 0
    engines_executed: int = 0
    success: bool = True
    error: str | None = None


@dataclass
class SessionMetrics:
    """Metrics for a cognitive session."""

    session_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    cycles_completed: int = 0
    cycles_failed: int = 0
    events_published: int = 0
    total_stages_executed: int = 0
    success: bool = True
    error: str | None = None


@dataclass
class EngineMetrics:
    """Metrics for engine execution."""

    engine_name: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: int = 0
    min_duration_ms: int = 0
    max_duration_ms: int = 0
    avg_duration_ms: int = 0

    def record_execution(self, duration_ms: int, success: bool = True) -> None:
        """Record an engine execution.

        Args:
            duration_ms: Execution duration in milliseconds.
            success: Whether the execution was successful.
        """
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.total_duration_ms += duration_ms

        if self.execution_count == 1:
            self.min_duration_ms = duration_ms
            self.max_duration_ms = duration_ms
        else:
            self.min_duration_ms = min(self.min_duration_ms, duration_ms)
            self.max_duration_ms = max(self.max_duration_ms, duration_ms)

        self.avg_duration_ms = self.total_duration_ms // self.execution_count


@dataclass
class RuntimeMetrics:
    """Complete metrics for the Cognitive Runtime.

    Tracks all operational metrics including initialization, sessions,
    cycles, and engine execution.
    """

    runtime_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    total_duration_ms: int = 0

    # Initialization metrics
    initialization_duration_ms: int = 0
    boot_duration_ms: int = 0
    validation_duration_ms: int = 0

    # Session metrics
    sessions_created: int = 0
    sessions_completed: int = 0
    sessions_failed: int = 0

    # Cycle metrics
    cycles_completed: int = 0
    cycles_failed: int = 0
    total_cycle_duration_ms: int = 0
    avg_cycle_duration_ms: int = 0

    # Engine metrics
    engine_metrics: dict[str, EngineMetrics] = field(default_factory=dict)

    # Event metrics
    events_published: int = 0
    events_failed: int = 0

    # Error metrics
    total_errors: int = 0
    critical_errors: int = 0

    # Internal tracking
    _stage_metrics: list[StageMetrics] = field(default_factory=list, repr=False)
    _cycle_metrics: list[CycleMetrics] = field(default_factory=list, repr=False)
    _session_metrics: list[SessionMetrics] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        """Initialize timestamps."""
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def record_initialization(self, duration_ms: int) -> None:
        """Record initialization completion.

        Args:
            duration_ms: Initialization duration.
        """
        self.initialization_duration_ms = duration_ms

    def record_boot(self, duration_ms: int) -> None:
        """Record boot completion.

        Args:
            duration_ms: Boot duration.
        """
        self.boot_duration_ms = duration_ms

    def record_validation(self, duration_ms: int) -> None:
        """Record validation completion.

        Args:
            duration_ms: Validation duration.
        """
        self.validation_duration_ms = duration_ms

    def record_runtime_start(self) -> None:
        """Record runtime start."""
        self.started_at = datetime.now(UTC).isoformat()

    def record_runtime_completion(
        self,
        completed_at: str = "",
        total_duration_ms: int = 0,
    ) -> None:
        """Record runtime completion.

        Args:
            completed_at: Completion timestamp.
            total_duration_ms: Total runtime duration.
        """
        self.completed_at = completed_at or datetime.now(UTC).isoformat()
        self.total_duration_ms = total_duration_ms

    # -------------------------------------------------------------------------
    # Session Metrics
    # -------------------------------------------------------------------------

    def record_session_created(self, session_id: str) -> None:
        """Record a new session creation.

        Args:
            session_id: The session ID.
        """
        self.sessions_created += 1
        self._session_metrics.append(SessionMetrics(session_id=session_id))

    def record_session_completed(
        self,
        session_id: str,
        duration_ms: int,
        cycles_completed: int,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record session completion.

        Args:
            session_id: The session ID.
            duration_ms: Session duration.
            cycles_completed: Number of cycles completed.
            success: Whether session completed successfully.
            error: Error message if failed.
        """
        if success:
            self.sessions_completed += 1
        else:
            self.sessions_failed += 1

        # Find and update the session metrics
        for session in self._session_metrics:
            if session.session_id == session_id:
                session.completed_at = datetime.now(UTC).isoformat()
                session.duration_ms = duration_ms
                session.cycles_completed = cycles_completed
                session.success = success
                session.error = error
                break

    def record_session_event(self, session_id: str) -> None:
        """Record an event for a session.

        Args:
            session_id: The session ID.
        """
        for session in self._session_metrics:
            if session.session_id == session_id:
                session.events_published += 1
                break

    # -------------------------------------------------------------------------
    # Cycle Metrics
    # -------------------------------------------------------------------------

    def start_cycle(self, cycle_id: str) -> CycleMetrics:
        """Start tracking a new cycle.

        Args:
            cycle_id: The cycle ID.

        Returns:
            The cycle metrics object.
        """
        cycle = CycleMetrics(
            cycle_id=cycle_id,
            started_at=datetime.now(UTC).isoformat(),
        )
        self._cycle_metrics.append(cycle)
        return cycle

    def record_cycle_completed(
        self,
        cycle_id: str,
        duration_ms: int,
        stages_executed: int,
        events_published: int,
        engines_executed: int,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record cycle completion.

        Args:
            cycle_id: The cycle ID.
            duration_ms: Cycle duration.
            stages_executed: Number of stages executed.
            events_published: Events published during cycle.
            engines_executed: Engines executed during cycle.
            success: Whether cycle completed successfully.
            error: Error message if failed.
        """
        if success:
            self.cycles_completed += 1
        else:
            self.cycles_failed += 1

        self.total_cycle_duration_ms += duration_ms
        if self.cycles_completed > 0:
            self.avg_cycle_duration_ms = (
                self.total_cycle_duration_ms // self.cycles_completed
            )

        # Find and update the cycle metrics
        for cycle in self._cycle_metrics:
            if cycle.cycle_id == cycle_id:
                cycle.completed_at = datetime.now(UTC).isoformat()
                cycle.duration_ms = duration_ms
                cycle.success = success
                cycle.error = error
                cycle.events_published = events_published
                cycle.engines_executed = engines_executed
                break

    # -------------------------------------------------------------------------
    # Stage Metrics
    # -------------------------------------------------------------------------

    def start_stage(self, stage_name: str) -> StageMetrics:
        """Start tracking a new stage.

        Args:
            stage_name: The stage name.

        Returns:
            The stage metrics object.
        """
        stage = StageMetrics(
            stage_name=stage_name,
            started_at=datetime.now(UTC).isoformat(),
        )
        self._stage_metrics.append(stage)
        return stage

    def record_stage_completed(
        self,
        stage_name: str,
        duration_ms: int,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record stage completion.

        Args:
            stage_name: The stage name.
            duration_ms: Stage duration.
            success: Whether stage completed successfully.
            error: Error message if failed.
        """
        # Find and update the most recent stage with this name
        for stage in reversed(self._stage_metrics):
            if stage.stage_name == stage_name and not stage.completed_at:
                stage.completed_at = datetime.now(UTC).isoformat()
                stage.duration_ms = duration_ms
                stage.success = success
                stage.error = error
                break

    # -------------------------------------------------------------------------
    # Engine Metrics
    # -------------------------------------------------------------------------

    def record_engine_execution(
        self,
        engine_name: str,
        duration_ms: int,
        success: bool = True,
    ) -> None:
        """Record an engine execution.

        Args:
            engine_name: Name of the engine.
            duration_ms: Execution duration.
            success: Whether execution was successful.
        """
        if engine_name not in self.engine_metrics:
            self.engine_metrics[engine_name] = EngineMetrics(engine_name=engine_name)

        self.engine_metrics[engine_name].record_execution(duration_ms, success)

    # -------------------------------------------------------------------------
    # Event Metrics
    # -------------------------------------------------------------------------

    def record_event_published(self) -> None:
        """Record an event publication."""
        self.events_published += 1

    def record_event_failure(self) -> None:
        """Record an event publication failure."""
        self.events_failed += 1

    # -------------------------------------------------------------------------
    # Error Metrics
    # -------------------------------------------------------------------------

    def record_error(self, critical: bool = False) -> None:
        """Record an error.

        Args:
            critical: Whether the error is critical.
        """
        self.total_errors += 1
        if critical:
            self.critical_errors += 1

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary.

        Returns:
            Metrics as a dictionary.
        """
        return {
            "runtime_id": self.runtime_id,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_ms": self.total_duration_ms,
            "initialization_duration_ms": self.initialization_duration_ms,
            "boot_duration_ms": self.boot_duration_ms,
            "validation_duration_ms": self.validation_duration_ms,
            "sessions_created": self.sessions_created,
            "sessions_completed": self.sessions_completed,
            "sessions_failed": self.sessions_failed,
            "cycles_completed": self.cycles_completed,
            "cycles_failed": self.cycles_failed,
            "total_cycle_duration_ms": self.total_cycle_duration_ms,
            "avg_cycle_duration_ms": self.avg_cycle_duration_ms,
            "engine_metrics": {
                name: {
                    "execution_count": m.execution_count,
                    "success_count": m.success_count,
                    "failure_count": m.failure_count,
                    "total_duration_ms": m.total_duration_ms,
                    "avg_duration_ms": m.avg_duration_ms,
                }
                for name, m in self.engine_metrics.items()
            },
            "events_published": self.events_published,
            "events_failed": self.events_failed,
            "total_errors": self.total_errors,
            "critical_errors": self.critical_errors,
        }

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of key metrics.

        Returns:
            Summary metrics.
        """
        return {
            "runtime_id": self.runtime_id,
            "status": "running" if not self.completed_at else "completed",
            "duration_ms": self.total_duration_ms,
            "sessions": {
                "created": self.sessions_created,
                "completed": self.sessions_completed,
                "failed": self.sessions_failed,
            },
            "cycles": {
                "completed": self.cycles_completed,
                "failed": self.cycles_failed,
                "avg_duration_ms": self.avg_cycle_duration_ms,
            },
            "events": {
                "published": self.events_published,
                "failed": self.events_failed,
            },
            "errors": {
                "total": self.total_errors,
                "critical": self.critical_errors,
            },
        }
