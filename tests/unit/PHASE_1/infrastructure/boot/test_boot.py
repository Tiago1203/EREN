"""Tests for the Cognitive Boot Manager."""

from core.PHASE_1.infrastructure.boot import (
    CognitiveBootManager,
    BootManagerFactory,
    BootState,
    BootStatus,
    BootPolicy,
    BootPolicyPresets,
    BootConfiguration,
    BootMetricsCollector,
    BOOT_SEQUENCE,
)


class TestBootStates:
    """Tests for boot states."""

    def test_all_states_defined(self):
        """All states should be defined."""
        assert BootState.CREATED
        assert BootState.LOAD_CONFIGURATION
        assert BootState.CREATE_EVENT_BUS
        assert BootState.CREATE_CAPABILITY_REGISTRY
        assert BootState.READY
        assert BootState.FAILED
        assert BootState.ROLLED_BACK


class TestBootSequence:
    """Tests for boot sequence."""

    def test_boot_sequence_length(self):
        """Boot sequence should have 12 steps."""
        assert len(BOOT_SEQUENCE) == 12

    def test_boot_sequence_order(self):
        """Boot sequence should be in correct order."""
        states = [step[2] for step in BOOT_SEQUENCE]
        assert states[0] == BootState.LOAD_CONFIGURATION
        assert states[-1] == BootState.CREATE_ORCHESTRATOR


class TestBootManager:
    """Tests for BootManager."""

    def test_manager_creation(self):
        """Creating manager should work."""
        manager = CognitiveBootManager()
        assert manager is not None
        assert manager.state == BootState.CREATED

    def test_initial_state(self):
        """Initial state should be CREATED."""
        manager = CognitiveBootManager()
        assert manager.state == "created"

    def test_boot_success(self):
        """Boot should succeed."""
        manager = CognitiveBootManager()
        result = manager.boot()

        assert result.success is True
        assert result.state == "ready"
        assert len(result.steps) == 12

    def test_boot_steps_completed(self):
        """All steps should be completed."""
        manager = CognitiveBootManager()
        result = manager.boot()

        completed_steps = [s for s in result.steps if s.status == "completed"]
        assert len(completed_steps) == 12

    def test_components_initialized(self):
        """Components should be initialized."""
        manager = CognitiveBootManager()
        result = manager.boot()

        assert "load_configuration" in result.components
        assert "create_event_bus" in result.components
        assert "create_orchestrator" in result.components

    def test_trace_recorded(self):
        """Trace should be recorded."""
        manager = CognitiveBootManager()
        manager.boot()

        trace = manager.get_trace()
        assert len(trace) > 0

    def test_metrics_recorded(self):
        """Metrics should be recorded."""
        manager = CognitiveBootManager()
        manager.boot()

        metrics = manager.get_metrics()
        assert metrics["boot_successes"] == 1
        assert metrics["steps_completed"] == 12


class TestBootPolicies:
    """Tests for boot policies."""

    def test_default_policy(self):
        """Default policy should work."""
        policy = BootPolicy()
        assert policy.strict_mode is True
        assert policy.stop_on_error is True
        assert policy.enable_rollback is True

    def test_production_preset(self):
        """Production preset should be strict."""
        policy = BootPolicyPresets.production()
        assert policy.strict_mode is True
        assert policy.stop_on_error is True

    def test_development_preset(self):
        """Development preset should be lenient."""
        policy = BootPolicyPresets.development()
        assert policy.strict_mode is False
        assert policy.stop_on_error is False


class TestBootMetrics:
    """Tests for boot metrics."""

    def test_metrics_collector(self):
        """Metrics collector should work."""
        collector = BootMetricsCollector()
        collector.record_boot_started()
        collector.record_boot_success(1000)

        assert collector.boot_attempts == 1
        assert collector.boot_successes == 1

    def test_success_rate(self):
        """Success rate should be calculated."""
        collector = BootMetricsCollector()
        collector.record_boot_started()
        collector.record_boot_success(1000)
        collector.record_boot_started()
        collector.record_boot_failure(500)

        assert collector.success_rate == 0.5
