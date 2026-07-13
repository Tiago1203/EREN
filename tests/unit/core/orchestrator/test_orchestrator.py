"""Tests for the Cognitive Orchestrator."""

from __future__ import annotations

from core.orchestrator import (
    CognitiveOrchestrator,
    CognitiveSession,
    OrchestrationPolicies,
    OrchestrationState,
    OrchestrationEventPublisher,
    OrchestrationMetricsCollector,
    OrchestrationPolicies,
    PolicyPresets,
    SessionMetadata,
    SessionMetrics,
    SessionType,
)


class TestOrchestrationStates:
    """Tests for orchestration states."""

    def test_all_states_defined(self) -> None:
        """All states should be defined."""
        assert OrchestrationState.CREATED
        assert OrchestrationState.INITIALIZING
        assert OrchestrationState.PLANNING
        assert OrchestrationState.COLLECTING_EVIDENCE
        assert OrchestrationState.REASONING
        assert OrchestrationState.DECIDING
        assert OrchestrationState.EXECUTING
        assert OrchestrationState.WAITING_EVENTS
        assert OrchestrationState.UPDATING_CONTEXT
        assert OrchestrationState.FINISHED
        assert OrchestrationState.FAILED
        assert OrchestrationState.CANCELLED


class TestCognitiveSession:
    """Tests for CognitiveSession."""

    def test_session_creation(self) -> None:
        """Creating a session should work."""
        metadata = SessionMetadata(
            session_id="session_1",
            correlation_id="corr_1",
            context_id="ctx_1",
        )
        session = CognitiveSession(metadata=metadata)

        assert session.state == OrchestrationState.CREATED
        assert session.metadata.session_id == "session_1"
        assert len(session.state_history) == 0

    def test_session_transition(self) -> None:
        """Transitioning states should work."""
        metadata = SessionMetadata(
            session_id="session_1",
            correlation_id="corr_1",
            context_id="ctx_1",
        )
        session = CognitiveSession(metadata=metadata)

        transition = session.transition_to(
            OrchestrationState.INITIALIZING,
            reason="Test transition",
        )

        assert session.state == OrchestrationState.INITIALIZING
        assert len(session.state_history) == 1
        assert transition.from_state == OrchestrationState.CREATED
        assert transition.to_state == OrchestrationState.INITIALIZING

    def test_session_record_error(self) -> None:
        """Recording errors should work."""
        metadata = SessionMetadata(
            session_id="session_1",
            correlation_id="corr_1",
            context_id="ctx_1",
        )
        session = CognitiveSession(metadata=metadata)

        session.record_error("Test error")

        assert session.last_error == "Test error"
        assert session.error_count == 1
        assert session.metrics.errors_count == 1


class TestCognitiveOrchestrator:
    """Tests for CognitiveOrchestrator."""

    def test_orchestrator_creation(self) -> None:
        """Creating orchestrator should work."""
        orch = CognitiveOrchestrator()

        assert orch is not None
        assert orch._sessions == {}

    def test_create_session(self) -> None:
        """Creating a session should work."""
        orch = CognitiveOrchestrator()

        session = orch.create_session(
            session_type=SessionType.TROUBLESHOOTING,
            user_id="user_1",
        )

        assert session is not None
        assert session.metadata.session_id.startswith("session_")
        assert session.metadata.correlation_id.startswith("corr_")
        assert session.metadata.context_id.startswith("ctx_")
        assert len(orch._sessions) == 1

    def test_start_session(self) -> None:
        """Starting a session should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()

        result = orch.start_session(session.metadata.session_id)

        assert result is True
        assert session.state == OrchestrationState.INITIALIZING

    def test_transition_state(self) -> None:
        """Transitioning state should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()
        orch.start_session(session.metadata.session_id)

        result = orch.transition_to(
            session.metadata.session_id,
            OrchestrationState.PLANNING,
            reason="Start planning",
        )

        assert result is True
        assert session.state == OrchestrationState.PLANNING

    def test_invalid_transition(self) -> None:
        """Invalid transitions should be rejected."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()

        # Can't go directly from CREATED to REASONING
        result = orch.transition_to(
            session.metadata.session_id,
            OrchestrationState.REASONING,
            reason="Invalid",
        )

        assert result is False

    def test_finish_session(self) -> None:
        """Finishing session should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()
        orch.start_session(session.metadata.session_id)

        result = orch.finish_session(session.metadata.session_id)

        assert result is True
        assert session.state == OrchestrationState.FINISHED
        assert session.is_active is False

    def test_fail_session(self) -> None:
        """Failing session should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()
        orch.start_session(session.metadata.session_id)

        result = orch.fail_session(session.metadata.session_id, "Test error")

        assert result is True
        assert session.state == OrchestrationState.FAILED
        assert session.last_error == "Test error"

    def test_cancel_session(self) -> None:
        """Cancelling session should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()

        result = orch.cancel_session(session.metadata.session_id, "User cancelled")

        assert result is True
        assert session.state == OrchestrationState.CANCELLED

    def test_get_session(self) -> None:
        """Getting session should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()

        retrieved = orch.get_session(session.metadata.session_id)

        assert retrieved is not None
        assert retrieved.metadata.session_id == session.metadata.session_id

    def test_set_active_motor(self) -> None:
        """Setting active motor should work."""
        orch = CognitiveOrchestrator()
        session = orch.create_session()

        result = orch.set_active_motor(
            session.metadata.session_id,
            "planner_engine",
        )

        assert result is True
        assert session.active_motor == "planner_engine"


class TestPolicies:
    """Tests for policies."""

    def test_default_policies(self) -> None:
        """Default policies should have correct values."""
        policies = OrchestrationPolicies()

        assert policies.session_timeout_ms == 300000
        assert policies.max_retries == 3
        assert policies.max_iterations == 10

    def test_strict_preset(self) -> None:
        """Strict preset should be stricter."""
        policies = PolicyPresets.strict()

        assert policies.session_timeout_ms < 300000
        assert policies.max_retries <= 3

    def test_critical_preset(self) -> None:
        """Critical preset should be most strict."""
        policies = PolicyPresets.critical()

        assert policies.session_timeout_ms == 120000
        assert policies.max_retries == 1
        assert policies.enable_auto_recovery is False


class TestMetrics:
    """Tests for metrics."""

    def test_metrics_collector(self) -> None:
        """Metrics collector should work."""
        collector = OrchestrationMetricsCollector()

        collector.record_session_created()
        collector.record_session_completed(1000)

        assert collector.sessions_created == 1
        assert collector.sessions_completed == 1
        assert collector.total_duration_ms == 1000

    def test_metrics_to_dict(self) -> None:
        """Metrics to_dict should work."""
        collector = OrchestrationMetricsCollector()
        collector.record_session_created()

        metrics = collector.to_dict()

        assert "sessions_created" in metrics
        assert metrics["sessions_created"] == 1
