"""Tests for the Cognitive Session Manager."""

from __future__ import annotations

from core.session import (
    CognitiveSessionManager,
    SessionState,
    SessionPolicies,
    SessionMetricsCollector,
    PolicyPresets,
)


class TestSessionStates:
    """Tests for session states."""

    def test_all_states_defined(self) -> None:
        """All states should be defined."""
        assert SessionState.CREATED
        assert SessionState.ACTIVE
        assert SessionState.IDLE
        assert SessionState.PAUSED
        assert SessionState.WAITING
        assert SessionState.RECOVERING
        assert SessionState.COMPLETED
        assert SessionState.FAILED
        assert SessionState.CANCELLED
        assert SessionState.ARCHIVED


class TestSessionManager:
    """Tests for SessionManager."""

    def test_manager_creation(self) -> None:
        """Creating manager should work."""
        manager = CognitiveSessionManager()
        assert manager is not None

    def test_create_session(self) -> None:
        """Creating session should work."""
        manager = CognitiveSessionManager()
        session = manager.create_session(
            user_id="user_1",
            hospital_id="hospital_1",
        )

        assert session is not None
        assert session.metadata.session_id.startswith("session_")
        assert session.user_id == "user_1"

    def test_get_session(self) -> None:
        """Getting session should work."""
        manager = CognitiveSessionManager()
        session = manager.create_session(user_id="user_1")

        retrieved = manager.get_session(session.metadata.session_id)
        assert retrieved is not None

    def test_activate_session(self) -> None:
        """Activating session should work."""
        manager = CognitiveSessionManager()
        session = manager.create_session()

        result = manager.activate_session(session.metadata.session_id)
        assert result is True

        activated = manager.get_session(session.metadata.session_id)
        assert activated.state == SessionState.ACTIVE

    def test_pause_session(self) -> None:
        """Pausing session should work."""
        manager = CognitiveSessionManager()
        session = manager.create_session()
        manager.activate_session(session.metadata.session_id)

        result = manager.pause_session(session.metadata.session_id)
        assert result is True

    def test_complete_session(self) -> None:
        """Completing session should work."""
        manager = CognitiveSessionManager()
        session = manager.create_session()
        manager.activate_session(session.metadata.session_id)

        result = manager.complete_session(session.metadata.session_id)
        assert result is True

    def test_find_by_user(self) -> None:
        """Finding by user should work."""
        manager = CognitiveSessionManager()
        manager.create_session(user_id="user_1")
        manager.create_session(user_id="user_1")

        sessions = manager.find_by_user("user_1")
        assert len(sessions) == 2


class TestPolicies:
    """Tests for policies."""

    def test_default_policies(self) -> None:
        """Default policies should work."""
        policies = SessionPolicies()
        assert policies.session_timeout_ms == 300000

    def test_strict_preset(self) -> None:
        """Strict preset should be stricter."""
        policies = PolicyPresets.strict()
        assert policies.session_timeout_ms < 300000


class TestMetrics:
    """Tests for metrics."""

    def test_metrics_collector(self) -> None:
        """Metrics collector should work."""
        collector = SessionMetricsCollector()
        collector.record_session_created()
        collector.record_session_activated()

        assert collector.sessions_created == 1
        assert collector.sessions_activated == 1
