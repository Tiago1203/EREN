"""Tests for the Cognitive Lifecycle Manager."""

from core.lifecycle import (
    CognitiveLifecycleManager,
    LifecycleManagerFactory,
    LifecycleState,
    LifecycleStateMachine,
    LifecyclePolicy,
    VALID_TRANSITIONS,
)


class TestLifecycleStates:
    """Tests for lifecycle states."""

    def test_all_states_defined(self):
        """All states should be defined."""
        assert LifecycleState.CREATED
        assert LifecycleState.INITIALIZING
        assert LifecycleState.READY
        assert LifecycleState.ACTIVE
        assert LifecycleState.PAUSED
        assert LifecycleState.WAITING
        assert LifecycleState.COMPLETED
        assert LifecycleState.FAILED
        assert LifecycleState.CANCELLED
        assert LifecycleState.ARCHIVED


class TestStateMachine:
    """Tests for state machine."""

    def test_initial_state(self):
        """Initial state should be created."""
        sm = LifecycleStateMachine()
        assert sm.current_state == "created"

    def test_valid_transition(self):
        """Valid transition should succeed."""
        sm = LifecycleStateMachine()
        success, new_state, data = sm.transition("initialize", VALID_TRANSITIONS)
        assert success is True
        assert new_state == "initializing"

    def test_invalid_transition(self):
        """Invalid transition should fail."""
        sm = LifecycleStateMachine()
        success, new_state, data = sm.transition("complete", VALID_TRANSITIONS)
        assert success is False

    def test_history(self):
        """History should be recorded."""
        sm = LifecycleStateMachine()
        sm.transition("initialize", VALID_TRANSITIONS)
        sm.transition("ready", VALID_TRANSITIONS)
        assert len(sm.history) == 2


class TestLifecycleManager:
    """Tests for LifecycleManager."""

    def test_manager_creation(self):
        """Creating manager should work."""
        manager = CognitiveLifecycleManager()
        assert manager is not None

    def test_create_lifecycle(self):
        """Creating lifecycle should work."""
        manager = CognitiveLifecycleManager()
        machine = manager.create_lifecycle("session_1")
        assert machine is not None
        assert machine.current_state == "created"

    def test_trigger_event(self):
        """Triggering event should work."""
        manager = CognitiveLifecycleManager()
        manager.create_lifecycle("session_1")

        success, new_state, data = manager.trigger_event(
            "session_1", "initialize"
        )
        assert success is True
        assert new_state == "initializing"

    def test_full_transition_path(self):
        """Full transition path should work."""
        manager = CognitiveLifecycleManager()
        manager.create_lifecycle("session_1")

        manager.trigger_event("session_1", "initialize")
        manager.trigger_event("session_1", "ready")
        manager.trigger_event("session_1", "activate")
        manager.trigger_event("session_1", "complete")
        manager.trigger_event("session_1", "ready")

        machine = manager.get_lifecycle("session_1")
        assert machine.current_state == "completed"

    def test_invalid_transition_rejected(self):
        """Invalid transition should be rejected."""
        manager = CognitiveLifecycleManager()
        manager.create_lifecycle("session_1")

        success, new_state, data = manager.trigger_event(
            "session_1", "complete"
        )
        assert success is False

    def test_get_metrics(self):
        """Getting metrics should work."""
        manager = CognitiveLifecycleManager()
        metrics = manager.get_metrics()
        assert "transitions" in metrics


class TestPolicies:
    """Tests for policies."""

    def test_default_policy(self):
        """Default policy should work."""
        policy = LifecyclePolicy()
        assert policy.auto_recovery is True
        assert policy.max_recovery_attempts == 3

    def test_strict_preset(self):
        """Strict preset should be stricter."""
        from core.lifecycle import LifecyclePolicyPresets
        policy = LifecyclePolicyPresets.strict()
        assert policy.max_recovery_attempts == 2
