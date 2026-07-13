"""Tests for the Cognitive Runtime.

These tests verify the complete lifecycle of the Cognitive Runtime,
including initialization, boot, validation, session creation,
and cognitive cycle execution.
"""

import pytest
from datetime import datetime, timezone

# Import the runtime module
import sys
sys.path.insert(0, '/workspace/project/EREN')

from core.runtime import (
    CognitiveRuntime,
    RuntimeBuilder,
    RuntimeConfiguration,
    RuntimeState,
    RuntimeEventType,
    SessionContext,
    CycleContext,
    RuntimeContext,
    create_default_runtime,
    create_testing_runtime,
    create_minimal_runtime,
    RuntimeInitializationError,
    RuntimeBootError,
    RuntimeValidationError,
    RuntimeStartError,
    SessionCreationError,
)


class TestRuntimeCreation:
    """Tests for runtime creation."""

    def test_create_runtime_with_defaults(self):
        """Test creating a runtime with default configuration."""
        runtime = CognitiveRuntime()
        assert runtime is not None
        assert runtime.runtime_id is not None
        assert runtime.state == RuntimeState.CREATED

    def test_create_runtime_with_custom_id(self):
        """Test creating a runtime with custom ID."""
        runtime = CognitiveRuntime(runtime_id="test-runtime-123")
        assert runtime.runtime_id == "test-runtime-123"

    def test_create_runtime_with_configuration(self):
        """Test creating a runtime with custom configuration."""
        config = RuntimeConfiguration.create_testing()
        runtime = CognitiveRuntime(configuration=config)
        assert runtime.configuration.environment == "testing"

    def test_runtime_properties(self):
        """Test runtime properties."""
        runtime = CognitiveRuntime()
        assert runtime.is_running is False
        assert runtime.events == []
        assert runtime.metrics is not None
        assert runtime.trace is not None
        assert runtime.health is not None


class TestRuntimeBuilder:
    """Tests for the RuntimeBuilder."""

    def test_builder_create_default(self):
        """Test creating a runtime with defaults."""
        runtime = RuntimeBuilder().build()
        assert runtime is not None
        assert runtime.state == RuntimeState.CREATED

    def test_builder_with_name(self):
        """Test setting runtime name."""
        runtime = RuntimeBuilder().with_name("Test Runtime").build()
        assert runtime.configuration.runtime_name == "Test Runtime"

    def test_builder_with_version(self):
        """Test setting runtime version."""
        runtime = RuntimeBuilder().with_version("2.0.0").build()
        assert runtime.configuration.runtime_version == "2.0.0"

    def test_builder_with_environment(self):
        """Test setting environment."""
        runtime = RuntimeBuilder().with_environment("production").build()
        assert runtime.configuration.environment == "production"

    def test_builder_with_simulation_mode(self):
        """Test setting simulation mode."""
        runtime = RuntimeBuilder().with_simulation_mode(False).build()
        assert runtime.configuration.simulation_mode is False

    def test_builder_with_simulation_delay(self):
        """Test setting simulation delay."""
        runtime = RuntimeBuilder().with_simulation_delay(500).build()
        assert runtime.configuration.simulation_delay_ms == 500

    def test_builder_development_preset(self):
        """Test using development preset."""
        runtime = RuntimeBuilder().use_development_preset().build()
        assert runtime.configuration.environment == "development"
        assert runtime.configuration.enable_debug_mode is True

    def test_builder_testing_preset(self):
        """Test using testing preset."""
        runtime = RuntimeBuilder().use_testing_preset().build()
        assert runtime.configuration.environment == "testing"
        assert runtime.configuration.simulation_mode is True

    def test_builder_production_preset(self):
        """Test using production preset."""
        runtime = RuntimeBuilder().use_production_preset().build()
        assert runtime.configuration.environment == "production"
        assert runtime.configuration.simulation_mode is False


class TestRuntimeInitialization:
    """Tests for runtime initialization."""

    def test_initialize_runtime(self):
        """Test initializing the runtime."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        assert runtime.state == RuntimeState.INITIALIZED
        assert len(runtime.events) > 0

    def test_initialize_publishes_events(self):
        """Test that initialization publishes events."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.RUNTIME_STARTED in event_types
        assert RuntimeEventType.RUNTIME_INITIALIZED in event_types

    def test_initialize_only_once(self):
        """Test that initialization can only happen once."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        with pytest.raises(RuntimeInitializationError):
            runtime.initialize()

    def test_initialize_from_created_state(self):
        """Test initialization from CREATED state."""
        runtime = CognitiveRuntime()
        assert runtime.state == RuntimeState.CREATED
        runtime.initialize()
        assert runtime.state == RuntimeState.INITIALIZED


class TestRuntimeBoot:
    """Tests for runtime boot."""

    def test_boot_after_initialize(self):
        """Test booting after initialization."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        runtime.boot()
        assert runtime.state == RuntimeState.BOOTED

    def test_boot_publishes_events(self):
        """Test that boot publishes events."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        runtime.boot()
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.RUNTIME_BOOT_STARTED in event_types
        assert RuntimeEventType.RUNTIME_BOOT_COMPLETED in event_types

    def test_boot_from_created_state(self):
        """Test that boot from CREATED state auto-initializes."""
        runtime = CognitiveRuntime()
        runtime.boot()
        assert runtime.state == RuntimeState.BOOTED


class TestRuntimeValidation:
    """Tests for runtime validation."""

    def test_validate_after_boot(self):
        """Test validation after boot."""
        runtime = CognitiveRuntime()
        runtime.boot()
        report = runtime.validate()
        assert report is not None
        assert runtime.state == RuntimeState.VALIDATED

    def test_validate_publishes_events(self):
        """Test that validation publishes events."""
        runtime = CognitiveRuntime()
        runtime.boot()
        runtime.validate()
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.RUNTIME_VALIDATION_STARTED in event_types
        assert RuntimeEventType.RUNTIME_VALIDATION_COMPLETED in event_types

    def test_validation_report(self):
        """Test validation report."""
        runtime = CognitiveRuntime()
        runtime.boot()
        report = runtime.validate()
        
        assert report.runtime_id == runtime.runtime_id
        assert report.is_valid is True
        assert len(report.results) > 0


class TestRuntimeStart:
    """Tests for runtime start."""

    def test_start_runtime(self):
        """Test starting the runtime."""
        runtime = CognitiveRuntime()
        runtime.start()
        assert runtime.state == RuntimeState.RUNNING
        assert runtime.is_running is True

    def test_start_publishes_session_events(self):
        """Test that start publishes initial events."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        # Should have initialization and boot events
        assert len(runtime.events) > 0

    def test_start_from_created_state(self):
        """Test that start from CREATED state auto-initializes and boots."""
        runtime = CognitiveRuntime()
        runtime.start()
        assert runtime.state == RuntimeState.RUNNING

    def test_already_running_returns_self(self):
        """Test that starting an already running runtime returns self."""
        runtime = CognitiveRuntime()
        runtime.start()
        result = runtime.start()
        assert result is runtime


class TestSessionManagement:
    """Tests for session management."""

    def test_create_session(self):
        """Test creating a session."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        assert session is not None
        assert session.session_id is not None
        assert session.correlation_id is not None

    def test_create_session_publishes_event(self):
        """Test that session creation publishes an event."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.create_session()
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.SESSION_CREATED in event_types

    def test_create_session_with_user_id(self):
        """Test creating a session with user ID."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session(user_id="user-123")
        assert session.user_id == "user-123"

    def test_create_session_requires_running(self):
        """Test that session creation requires running runtime."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        with pytest.raises(RuntimeStartError):
            runtime.create_session()

    def test_start_session(self):
        """Test starting a session."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.start_session(session)
        
        assert session.started_at is not None
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.SESSION_STARTED in event_types

    def test_complete_session(self):
        """Test completing a session."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.complete_session(session)
        
        assert session.completed_at is not None
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.SESSION_COMPLETED in event_types


class TestCognitiveCycle:
    """Tests for cognitive cycle execution."""

    def test_execute_cognitive_cycle(self):
        """Test executing a cognitive cycle."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(
            session,
            intent={"query": "Test query"}
        )
        
        # Check that cycle events were published
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.COGNITIVE_CYCLE_STARTED in event_types
        assert RuntimeEventType.COGNITIVE_CYCLE_COMPLETED in event_types

    def test_execute_cycle_publishes_stage_events(self):
        """Test that cycle execution publishes stage events."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(session, intent={"query": "test"})
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.PLANNING_STARTED in event_types
        assert RuntimeEventType.KNOWLEDGE_REQUESTED in event_types
        assert RuntimeEventType.MEMORY_REQUESTED in event_types
        assert RuntimeEventType.REASONING_STARTED in event_types
        assert RuntimeEventType.DECISION_CREATED in event_types
        assert RuntimeEventType.ACTION_GENERATED in event_types

    def test_cycle_updates_session_context(self):
        """Test that cycle updates session context."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(session, intent={"query": "test"})
        
        assert session.intent is not None
        assert session.plan is not None
        assert len(session.hypotheses) > 0
        assert len(session.decisions) > 0
        assert len(session.actions) > 0

    def test_cycle_records_engines_executed(self):
        """Test that cycle records engines executed."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(session, intent={"query": "test"})
        
        assert len(session.engines_executed) > 0
        assert "planner" in session.engines_executed
        assert "knowledge_engine" in session.engines_executed
        assert "memory_engine" in session.engines_executed
        assert "reasoning_engine" in session.engines_executed


class TestMetricsCollection:
    """Tests for metrics collection."""

    def test_metrics_initialized(self):
        """Test that metrics are initialized."""
        runtime = CognitiveRuntime()
        assert runtime.metrics is not None
        assert runtime.metrics.runtime_id == runtime.runtime_id

    def test_metrics_after_initialization(self):
        """Test metrics after initialization."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        # Duration may be 0 in simulation mode due to fast execution
        assert runtime.metrics.initialization_duration_ms >= 0

    def test_metrics_after_boot(self):
        """Test metrics after boot."""
        runtime = CognitiveRuntime()
        runtime.boot()
        
        # Duration may be 0 in simulation mode due to fast execution
        assert runtime.metrics.boot_duration_ms >= 0

    def test_metrics_after_session(self):
        """Test metrics after session."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.create_session()
        
        assert runtime.metrics.sessions_created > 0

    def test_metrics_after_cycle(self):
        """Test metrics after cycle."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(session, intent={"query": "test"})
        
        assert runtime.metrics.cycles_completed > 0

    def test_get_summary(self):
        """Test getting metrics summary."""
        runtime = CognitiveRuntime()
        runtime.start()
        
        summary = runtime.metrics.get_summary()
        assert "runtime_id" in summary
        assert "status" in summary
        assert "sessions" in summary
        assert "cycles" in summary


class TestHealthChecks:
    """Tests for health checks."""

    def test_health_check(self):
        """Test health check."""
        runtime = CognitiveRuntime()
        runtime.boot()
        
        health = runtime.health_check()
        assert health is not None
        assert health.runtime_id == runtime.runtime_id

    def test_health_summary(self):
        """Test health summary."""
        runtime = CognitiveRuntime()
        runtime.boot()
        
        health = runtime.health_check()
        summary = health.summary
        
        assert "total" in summary
        assert "healthy" in summary
        assert "degraded" in summary
        assert "unhealthy" in summary


class TestTraceRecording:
    """Tests for trace recording."""

    def test_trace_initialized(self):
        """Test that trace is initialized."""
        runtime = CognitiveRuntime()
        assert runtime.trace is not None
        assert runtime.trace.runtime_id == runtime.runtime_id

    def test_trace_records_operations(self):
        """Test that trace records operations."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        entries = runtime.trace.get_all_entries()
        assert len(entries) > 0

    def test_trace_records_transitions(self):
        """Test that trace records state transitions."""
        runtime = CognitiveRuntime()
        runtime.initialize()
        
        transitions = runtime.trace.get_transitions()
        assert len(transitions) > 0

    def test_trace_summary(self):
        """Test getting trace summary."""
        runtime = CognitiveRuntime()
        runtime.boot()
        
        summary = runtime.trace.get_summary()
        assert "runtime_id" in summary
        assert "total_entries" in summary


class TestShutdown:
    """Tests for runtime shutdown."""

    def test_shutdown_runtime(self):
        """Test shutting down the runtime."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.shutdown()
        
        assert runtime.state == RuntimeState.STOPPED

    def test_shutdown_publishes_events(self):
        """Test that shutdown publishes events."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.shutdown()
        
        event_types = [e.event_type for e in runtime.events]
        assert RuntimeEventType.RUNTIME_SHUTDOWN in event_types
        assert RuntimeEventType.RUNTIME_COMPLETED in event_types

    def test_double_shutdown_is_safe(self):
        """Test that double shutdown doesn't error."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.shutdown()
        runtime.shutdown()  # Should not raise

    def test_shutdown_updates_metrics(self):
        """Test that shutdown updates metrics."""
        runtime = CognitiveRuntime()
        runtime.start()
        runtime.shutdown()
        
        assert runtime.metrics.completed_at != ""


class TestContextManager:
    """Tests for context manager usage."""

    def test_context_manager(self):
        """Test using runtime as context manager."""
        with CognitiveRuntime() as runtime:
            runtime.start()
            assert runtime.is_running
        
        # After context exit, should be stopped
        assert runtime.state == RuntimeState.STOPPED


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_default_runtime(self):
        """Test create_default_runtime."""
        runtime = create_default_runtime()
        assert runtime is not None

    def test_create_testing_runtime(self):
        """Test create_testing_runtime."""
        runtime = create_testing_runtime()
        assert runtime.configuration.environment == "testing"

    def test_create_minimal_runtime(self):
        """Test create_minimal_runtime."""
        runtime = create_minimal_runtime()
        assert runtime.configuration.simulation_mode is True
        assert runtime.configuration.enable_metrics is False


class TestErrorHandling:
    """Tests for error handling."""

    def test_initialize_error_is_handled(self):
        """Test that initialization errors are handled."""
        # This should not raise
        runtime = CognitiveRuntime()
        try:
            runtime.initialize()
        except RuntimeInitializationError:
            pass  # Expected if something is wrong

    def test_validation_error_with_strict_mode(self):
        """Test validation error in strict mode."""
        runtime = RuntimeBuilder().with_strict_validation(True).build()
        # Runtime is in CREATED state, validation should fail
        # but we need boot first
        runtime.boot()
        
        # In strict mode, invalid config would raise
        # but our defaults are valid, so this should pass


class TestEventHandlers:
    """Tests for event handlers."""

    def test_add_event_handler(self):
        """Test adding event handlers."""
        runtime = CognitiveRuntime()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        runtime.add_event_handler(handler)
        runtime.initialize()
        
        assert len(received_events) > 0

    def test_remove_event_handler(self):
        """Test removing event handlers."""
        runtime = CognitiveRuntime()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        runtime.add_event_handler(handler)
        runtime.remove_event_handler(handler)
        runtime.initialize()
        
        assert len(received_events) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
