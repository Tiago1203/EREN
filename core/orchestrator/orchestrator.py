"""Cognitive Orchestrator - Core Engine.

The orchestrator coordinates all cognitive engines through the
complete cognitive processing cycle.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .orchestration_events import OrchestrationEventPublisher
from .orchestration_metrics import OrchestrationMetricsCollector
from .orchestration_policies import OrchestrationPolicies
from .orchestration_trace import OrchestrationTraceCollector
from .orchestration_types import (
    CognitiveSession,
    OrchestrationPolicy,
    OrchestrationState,
    SessionMetadata,
    SessionMetrics,
    SessionType,
    VALID_TRANSITIONS,
)

# EventBus integration (optional)
try:
    from core.events import get_global_bus, Event
    _HAS_EVENT_BUS = True
except ImportError:
    _HAS_EVENT_BUS = False

if TYPE_CHECKING:
    pass


# =============================================================================
# Cognitive Orchestrator
# =============================================================================


class CognitiveOrchestrator:
    """The main cognitive orchestrator.

    Responsibilities:
    - Coordinate the complete cognitive processing cycle
    - Manage session lifecycle
    - Handle state transitions
    - Publish orchestration events
    - Collect metrics and traces
    - Enforce orchestration policies

    The orchestrator does NOT:
    - Call motors directly
    - Execute tools
    - Access memory
    - Access knowledge
    - Perform reasoning
    - Make decisions
    """

    def __init__(
        self,
        policies: OrchestrationPolicies | None = None,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            policies: Orchestration policies.
        """
        # Policies
        self._policies = policies or OrchestrationPolicies()

        # Session management
        self._sessions: dict[str, CognitiveSession] = {}
        self._active_session: CognitiveSession | None = None
        self._lock = threading.RLock()

        # Event publisher
        self._event_publisher = OrchestrationEventPublisher()

        # Metrics
        self._metrics = OrchestrationMetricsCollector()

        # Trace
        self._trace = OrchestrationTraceCollector()

    # =========================================================================
    # Session Management
    # =========================================================================

    def create_session(
        self,
        session_type: SessionType = SessionType.TROUBLESHOOTING,
        user_id: str = "",
        metadata: dict | None = None,
    ) -> CognitiveSession:
        """Create a new cognitive session.

        Args:
            session_type: Type of session.
            user_id: User ID.
            metadata: Additional metadata.

        Returns:
            The created session.
        """
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        correlation_id = f"corr_{uuid.uuid4().hex[:16]}"
        context_id = f"ctx_{uuid.uuid4().hex[:16]}"

        session_metadata = SessionMetadata(
            session_id=session_id,
            correlation_id=correlation_id,
            context_id=context_id,
            session_type=session_type,
            user_id=user_id,
            metadata=metadata or {},
        )

        session = CognitiveSession(
            metadata=session_metadata,
            state=OrchestrationState.CREATED,
        )

        with self._lock:
            self._sessions[session_id] = session
            self._active_session = session

        self._publish_event("SessionStarted", session)

        return session

    def start_session(self, session_id: str) -> bool:
        """Start a session.

        Args:
            session_id: Session ID.

        Returns:
            True if started successfully.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            if session.state != OrchestrationState.CREATED:
                return False

            # Transition to INITIALIZING
            session.transition_to(
                OrchestrationState.INITIALIZING,
                reason="Session starting",
            )
            session.add_trace_entry(
                OrchestrationState.INITIALIZING,
                "Session starting",
                session.metadata.correlation_id,
            )
            session.record_event("SessionStarted")
            session.is_active = True

        self._publish_event("StateChanged", session)

        return True

    def transition_to(
        self,
        session_id: str,
        new_state: OrchestrationState,
        reason: str = "",
    ) -> bool:
        """Transition session to a new state.

        Args:
            session_id: Session ID.
            new_state: Target state.
            reason: Reason for transition.

        Returns:
            True if transition was valid.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Validate transition
            valid_next = VALID_TRANSITIONS.get(session.state, ())
            if new_state not in valid_next:
                return False

            # Perform transition
            session.transition_to(new_state, reason)
            session.add_trace_entry(
                new_state,
                reason,
                session.metadata.correlation_id,
            )
            session.record_event(f"StateChanged:{new_state.value}")

        self._publish_event("StateChanged", session)

        return True

    def finish_session(self, session_id: str) -> bool:
        """Finish a session successfully.

        Args:
            session_id: Session ID.

        Returns:
            True if finished.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.transition_to(
                OrchestrationState.FINISHED,
                reason="Session completed",
            )
            session.finish()
            session.add_trace_entry(
                OrchestrationState.FINISHED,
                "Session completed",
                session.metadata.correlation_id,
            )

        self._publish_event("SessionCompleted", session)

        return True

    def fail_session(self, session_id: str, reason: str) -> bool:
        """Mark session as failed.

        Args:
            session_id: Session ID.
            reason: Failure reason.

        Returns:
            True if failed.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.record_error(reason)
            session.fail(reason)
            session.add_trace_entry(
                OrchestrationState.FAILED,
                f"Session failed: {reason}",
                session.metadata.correlation_id,
            )

        self._publish_event("SessionFailed", session)

        return True

    def cancel_session(self, session_id: str, reason: str) -> bool:
        """Cancel a session.

        Args:
            session_id: Session ID.
            reason: Cancellation reason.

        Returns:
            True if cancelled.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.record_error(reason)
            session.cancel(reason)
            session.add_trace_entry(
                OrchestrationState.CANCELLED,
                f"Session cancelled: {reason}",
                session.metadata.correlation_id,
            )

        self._publish_event("SessionCancelled", session)

        return True

    def get_session(self, session_id: str) -> CognitiveSession | None:
        """Get a session by ID.

        Args:
            session_id: Session ID.

        Returns:
            The session or None.
        """
        return self._sessions.get(session_id)

    def get_active_session(self) -> CognitiveSession | None:
        """Get the currently active session.

        Returns:
            The active session or None.
        """
        return self._active_session

    def get_all_sessions(self) -> list[CognitiveSession]:
        """Get all sessions.

        Returns:
            List of all sessions.
        """
        return list(self._sessions.values())

    # =========================================================================
    # Motor Coordination
    # =========================================================================

    def set_active_motor(self, session_id: str, motor_id: str) -> bool:
        """Set the active motor for a session.

        Args:
            session_id: Session ID.
            motor_id: Motor ID.

        Returns:
            True if set.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.active_motor = motor_id
            return True

    def set_active_phase(self, session_id: str, phase: str) -> bool:
        """Set the active phase for a session.

        Args:
            session_id: Session ID.
            phase: Phase name.

        Returns:
            True if set.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.active_phase = phase
            return True

    # =========================================================================
    # Metrics and Trace
    # =========================================================================

    def record_metric(
        self,
        session_id: str,
        metric_type: str,
        value: int | float,
    ) -> None:
        """Record a metric for a session.

        Args:
            session_id: Session ID.
            metric_type: Type of metric.
            value: Metric value.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return

            if metric_type == "duration_ms":
                session.metrics.duration_ms = int(value)
            elif metric_type == "decisions":
                session.metrics.decisions_taken = int(value)
            elif metric_type == "tools":
                session.metrics.tools_executed = int(value)
            elif metric_type == "iterations":
                session.metrics.cognitive_iterations = int(value)

    def get_trace(self, session_id: str) -> list:
        """Get trace for a session.

        Args:
            session_id: Session ID.

        Returns:
            Trace entries.
        """
        session = self._sessions.get(session_id)
        if not session:
            return []

        return list(session.trace_history)

    def get_metrics(self, session_id: str) -> dict | None:
        """Get metrics for a session.

        Args:
            session_id: Session ID.

        Returns:
            Metrics dictionary.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None

        return session.metrics.to_dict()

    # =========================================================================
    # Policies
    # =========================================================================

    def get_policies(self) -> OrchestrationPolicies:
        """Get orchestration policies.

        Returns:
            Policies.
        """
        return self._policies

    def check_timeout(self, session_id: str) -> bool:
        """Check if session has timed out.

        Args:
            session_id: Session ID.

        Returns:
            True if timed out.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        if not session.metadata.started_at:
            return False

        started = datetime.fromisoformat(session.metadata.started_at)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds() * 1000

        return elapsed > self._policies.session_timeout_ms

    # =========================================================================
    # Event Publishing
    # =========================================================================

    def _publish_event(self, event_type: str, session: CognitiveSession) -> None:
        """Publish an orchestration event.

        Args:
            event_type: Type of event.
            session: The session.
        """
        self._event_publisher.publish(
            event_type=event_type,
            session_id=session.metadata.session_id,
            correlation_id=session.metadata.correlation_id,
            state=session.state.value,
            metrics=session.metrics.to_dict(),
        )

    def publish_custom_event(
        self,
        session_id: str,
        event_type: str,
        data: dict | None = None,
    ) -> bool:
        """Publish a custom event for a session.

        Args:
            session_id: Session ID.
            event_type: Type of event.
            data: Event data.

        Returns:
            True if published.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.record_event(event_type)

            self._event_publisher.publish(
                event_type=event_type,
                session_id=session_id,
                correlation_id=session.metadata.correlation_id,
                state=session.state.value,
                data=data or {},
            )

            return True


# =============================================================================
# Factory
# =============================================================================


class OrchestratorFactory:
    """Factory for creating orchestrators."""

    @staticmethod
    def create_default() -> CognitiveOrchestrator:
        """Create an orchestrator with default policies.

        Returns:
            New orchestrator.
        """
        return CognitiveOrchestrator()

    @staticmethod
    def create_with_policies(policies: OrchestrationPolicies) -> CognitiveOrchestrator:
        """Create an orchestrator with custom policies.

        Args:
            policies: Custom policies.

        Returns:
            New orchestrator.
        """
        return CognitiveOrchestrator(policies=policies)
