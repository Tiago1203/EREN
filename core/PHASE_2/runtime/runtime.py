"""Cognitive Runtime — the core of EREN's Cognitive Operating System.

The Runtime is responsible for:
- Initializing the Composition Root and Container
- Executing the Boot Manager
- Creating and managing Cognitive Sessions
- Coordinating the complete Cognitive Cycle
- Publishing all lifecycle events
- Collecting metrics and traces

The Runtime does NOT:
- Think (that's the Reasoning Engine)
- Decide (that's the Decision Engine)
- Use AI (it's architecture only)
- Implement business logic

It ONLY coordinates the flow through existing contracts.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from .exceptions import (
    RuntimeBootError,
    RuntimeExecutionError,
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStartError,
    RuntimeValidationError,
    SessionCreationError,
)
from .runtime_configuration import RuntimeConfiguration, SessionConfiguration
from .runtime_context import ComponentReferences, RuntimeContext, SessionContext
from .runtime_events import (
    RuntimeBootCompleted,
    RuntimeBootStarted,
    RuntimeCompleted,
    RuntimeEvent,
    RuntimeInitialized,
    RuntimeShutdown,
    RuntimeStarted,
    RuntimeValidationCompleted,
    RuntimeValidationStarted,
    SessionCompleted,
    SessionCreated,
    SessionFailed,
    SessionStarted,
)
from .runtime_executor import CognitiveCycleExecutor
from .runtime_health import RuntimeHealth, RuntimeHealthChecker
from .runtime_metrics import RuntimeMetrics
from .runtime_state import RuntimeState, RuntimeStateMachine
from .runtime_trace import RuntimeTraceCollector
from .runtime_validator import RuntimeValidator, ValidationReport


class CognitiveRuntime:
    """The main Cognitive Runtime.

    This is the central coordinator for the EREN Cognitive Operating System.
    It initializes all components and coordinates the execution of the
    complete cognitive cycle.

    Usage:
        runtime = CognitiveRuntime()
        runtime.initialize()
        runtime.validate()
        runtime.start()

        # Create and execute a session
        session = runtime.create_session()
        runtime.execute_cognitive_cycle(session, intent={"query": "test"})

        # Shutdown when done
        runtime.shutdown()
    """

    def __init__(
        self,
        configuration: RuntimeConfiguration | None = None,
        runtime_id: str | None = None,
    ):
        """Initialize the Cognitive Runtime.

        Args:
            configuration: Runtime configuration. Uses default if None.
            runtime_id: Optional runtime ID. Generated if None.
        """
        self._runtime_id = runtime_id or f"runtime_{uuid.uuid4().hex[:16]}"
        self._configuration = configuration or RuntimeConfiguration.create_default()

        # State machine
        self._state_machine = RuntimeStateMachine()

        # Context and components
        self._context = RuntimeContext(runtime_id=self._runtime_id)
        self._components = ComponentReferences()

        # Observability
        self._trace = RuntimeTraceCollector(runtime_id=self._runtime_id)
        self._metrics = RuntimeMetrics(runtime_id=self._runtime_id)

        # Sub-systems
        self._validator = RuntimeValidator(runtime_id=self._runtime_id)
        self._health_checker = RuntimeHealthChecker(runtime_id=self._runtime_id)
        self._executor: CognitiveCycleExecutor | None = None

        # Event handlers
        self._event_handlers: list[callable] = []
        self._events: list[RuntimeEvent] = []

        # Thread safety
        self._lock = threading.RLock()

        # Store configuration
        self._context.configuration = self._configuration

        # Record creation
        self._trace.add_entry(
            operation="runtime_created",
            category="lifecycle",
            component="runtime",
        )

    # =============================================================================
    # Properties
    # =============================================================================

    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id

    @property
    def state(self) -> RuntimeState:
        """Get the current runtime state."""
        return self._state_machine.current_state

    @property
    def is_running(self) -> bool:
        """Check if runtime is running."""
        return self.state == RuntimeState.RUNNING

    @property
    def configuration(self) -> RuntimeConfiguration:
        """Get the runtime configuration."""
        return self._configuration

    @property
    def context(self) -> RuntimeContext:
        """Get the runtime context."""
        return self._context

    @property
    def components(self) -> ComponentReferences:
        """Get component references."""
        return self._components

    @property
    def metrics(self) -> RuntimeMetrics:
        """Get runtime metrics."""
        return self._metrics

    @property
    def trace(self) -> RuntimeTraceCollector:
        """Get the trace collector."""
        return self._trace

    @property
    def health(self) -> RuntimeHealth:
        """Get current health status."""
        return self._health_checker.health

    @property
    def events(self) -> list[RuntimeEvent]:
        """Get all published events."""
        return self._events.copy()

    # =============================================================================
    # Event Handling
    # =============================================================================

    def add_event_handler(self, handler: callable) -> None:
        """Add an event handler.

        Args:
            handler: Function to call with events.
        """
        self._event_handlers.append(handler)

    def remove_event_handler(self, handler: callable) -> None:
        """Remove an event handler.

        Args:
            handler: Handler to remove.
        """
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    def _publish_event(self, event: RuntimeEvent) -> None:
        """Publish an event.

        Args:
            event: The event to publish.
        """
        event = event.model_copy(update={"runtime_id": self._runtime_id})

        with self._lock:
            self._events.append(event)

        # Record in trace
        self._trace.record_event_publication(
            event_type=event.event_type.value,
            session_id=event.session_id,
            correlation_id=event.correlation_id,
        )

        # Record in metrics
        self._metrics.record_event_published()

        # Call handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass

    # =============================================================================
    # Initialization
    # =============================================================================

    def initialize(self) -> CognitiveRuntime:
        """Initialize the runtime.

        Initializes the Composition Root, builds the Container,
        and prepares all components.

        Returns:
            Self for chaining.

        Raises:
            RuntimeInitializationError: If initialization fails.
        """
        if self.state != RuntimeState.CREATED:
            raise RuntimeInitializationError(
                f"Cannot initialize from state: {self.state.value}"
            )

        try:
            self._transition_to(RuntimeState.INITIALIZING)

            start_time = datetime.now(UTC)

            self._publish_event(RuntimeStarted(
                runtime_id=self._runtime_id,
                payload={
                    "version": self._configuration.runtime_version,
                    "environment": self._configuration.environment,
                },
            ))

            # Initialize Composition Root
            self._initialize_composition_root()

            # Initialize Container
            self._initialize_container()

            # Initialize Event Bus
            self._initialize_event_bus()

            # Initialize Capability Registry
            self._initialize_capability_registry()

            # Initialize Managers
            self._initialize_managers()

            # Initialize Engines
            self._initialize_engines()

            # Calculate duration
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            self._metrics.record_initialization(duration_ms)

            self._transition_to(RuntimeState.INITIALIZED)

            self._publish_event(RuntimeInitialized(
                runtime_id=self._runtime_id,
                payload={
                    "initialization_time_ms": duration_ms,
                    "modules_loaded": len(self._configuration.custom_config.get("modules", [])),
                },
            ))

            self._trace.add_entry(
                operation="initialized",
                category="lifecycle",
                component="runtime",
                duration_ms=duration_ms,
            )

            return self

        except Exception as e:
            self._handle_error("initialization", e)
            raise RuntimeInitializationError(str(e))

    def _initialize_composition_root(self) -> None:
        """Initialize the Composition Root."""
        from core.composition.composition_root import CognitiveCompositionRoot

        root = CognitiveCompositionRoot().with_default_modules()
        runtime = root.build()

        self._components.composition_root = root
        self._context.configuration = runtime

        self._trace.add_entry(
            operation="composition_root_initialized",
            category="initialization",
            component="composition_root",
        )

    def _initialize_container(self) -> None:
        """Initialize the DI Container."""
        from core.PHASE_1.infrastructure.container.container import CognitiveContainer

        container = CognitiveContainer()
        self._components.container = container

        self._trace.add_entry(
            operation="container_initialized",
            category="initialization",
            component="container",
        )

    def _initialize_event_bus(self) -> None:
        """Initialize the Event Bus."""
        from core.PHASE_1.infrastructure.events.bus import EventBus

        event_bus = EventBus()
        self._components.event_bus = event_bus

        self._trace.add_entry(
            operation="event_bus_initialized",
            category="initialization",
            component="event_bus",
        )

    def _initialize_capability_registry(self) -> None:
        """Initialize the Capability Registry."""
        from core.PHASE_2.capabilities.capability_registry import CapabilityRegistry

        registry = CapabilityRegistry()
        self._components.capability_registry = registry

        self._trace.add_entry(
            operation="capability_registry_initialized",
            category="initialization",
            component="capability_registry",
        )

    def _initialize_managers(self) -> None:
        """Initialize all managers."""
        from core.PHASE_1.infrastructure.boot.boot_manager import CognitiveBootManager
        from core.PHASE_1.infrastructure.lifecycle.lifecycle_manager import CognitiveLifecycleManager
        from core.PHASE_2.orchestrator.orchestrator import CognitiveOrchestrator
        from core.PHASE_2.scheduler.scheduler import CognitiveScheduler
        from core.PHASE_2.session.session_manager import CognitiveSessionManager

        self._components.boot_manager = CognitiveBootManager()
        self._components.session_manager = CognitiveSessionManager()
        self._components.lifecycle_manager = CognitiveLifecycleManager()
        self._components.orchestrator = CognitiveOrchestrator()
        self._components.scheduler = CognitiveScheduler()

        self._trace.add_entry(
            operation="managers_initialized",
            category="initialization",
            component="managers",
        )

    def _initialize_engines(self) -> None:
        """Initialize all cognitive engines."""
        from core.PHASE_2.decision.decision_engine import CognitiveDecisionEngine

        from core.PHASE_1.domain.knowledge.knowledge_engine import CognitiveKnowledgeEngine
        from core.PHASE_2.memory.memory_engine import CognitiveMemoryEngine
        from core.PHASE_2.planner.planner_engine import PlannerEngine
        from core.PHASE_2.reasoning.reasoning_engine import CognitiveReasoningEngine

        # Note: Some engines may be None in simulation mode
        if self._configuration.enable_planner:
            self._components.planner = PlannerEngine()

        if self._configuration.enable_knowledge:
            self._components.knowledge_engine = CognitiveKnowledgeEngine()

        if self._configuration.enable_memory:
            self._components.memory_engine = CognitiveMemoryEngine()

        if self._configuration.enable_reasoning:
            self._components.reasoning_engine = CognitiveReasoningEngine()

        if self._configuration.enable_decision:
            self._components.decision_engine = CognitiveDecisionEngine()

        # Tool engine placeholder
        if self._configuration.enable_tools:
            self._components.tool_engine = None  # Placeholder for simulation

        self._trace.add_entry(
            operation="engines_initialized",
            category="initialization",
            component="engines",
        )

    # =============================================================================
    # Boot
    # =============================================================================

    def boot(self) -> CognitiveRuntime:
        """Execute the boot process.

        Runs the Boot Manager to prepare all components.

        Returns:
            Self for chaining.

        Raises:
            RuntimeBootError: If boot fails.
        """
        if self.state != RuntimeState.INITIALIZED:
            if self.state == RuntimeState.CREATED:
                self.initialize()
            else:
                raise RuntimeBootError(
                    f"Cannot boot from state: {self.state.value}"
                )

        try:
            self._transition_to(RuntimeState.BOOTING)

            start_time = datetime.now(UTC)

            self._publish_event(RuntimeBootStarted(
                runtime_id=self._runtime_id,
            ))

            # Execute boot manager
            boot_manager = self._components.boot_manager
            if boot_manager:
                result = boot_manager.boot()
                if not result.success:
                    raise RuntimeBootError(f"Boot failed: {result.error}")

            # Calculate duration
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            self._metrics.record_boot(duration_ms)

            self._transition_to(RuntimeState.BOOTED)

            self._publish_event(RuntimeBootCompleted(
                runtime_id=self._runtime_id,
                payload={
                    "boot_time_ms": duration_ms,
                    "components_ready": len(boot_manager.components) if boot_manager else 0,
                },
            ))

            self._trace.add_entry(
                operation="booted",
                category="lifecycle",
                component="runtime",
                duration_ms=duration_ms,
            )

            return self

        except Exception as e:
            self._handle_error("boot", e)
            raise RuntimeBootError(str(e))

    # =============================================================================
    # Validation
    # =============================================================================

    def validate(self) -> ValidationReport:
        """Validate the runtime.

        Runs comprehensive validation checks on all components.

        Returns:
            Validation report.

        Raises:
            RuntimeValidationError: If validation fails in strict mode.
        """
        if self.state not in (RuntimeState.INITIALIZED, RuntimeState.BOOTED):
            if self.state == RuntimeState.CREATED:
                self.initialize().boot()
            else:
                raise RuntimeValidationError(
                    f"Cannot validate from state: {self.state.value}"
                )

        self._transition_to(RuntimeState.VALIDATING)

        self._publish_event(RuntimeValidationStarted(
            runtime_id=self._runtime_id,
        ))

        start_time = datetime.now(UTC)

        # Set validator strict mode
        self._validator.set_strict_mode(self._configuration.strict_validation)

        # Run validation
        report = self._validator.validate(
            configuration=self._configuration,
            container=self._components.container,
            composition_root=self._components.composition_root,
            event_bus=self._components.event_bus,
            capability_registry=self._components.capability_registry,
            boot_manager=self._components.boot_manager,
            session_manager=self._components.session_manager,
            lifecycle_manager=self._components.lifecycle_manager,
            orchestrator=self._components.orchestrator,
            scheduler=self._components.scheduler,
            planner=self._components.planner,
            knowledge_engine=self._components.knowledge_engine,
            memory_engine=self._components.memory_engine,
            reasoning_engine=self._components.reasoning_engine,
            decision_engine=self._components.decision_engine,
            tool_engine=self._components.tool_engine,
        )

        duration_ms = int(
            (datetime.now(UTC) - start_time).total_seconds() * 1000
        )
        self._metrics.record_validation(duration_ms)

        if report.is_valid:
            self._transition_to(RuntimeState.VALIDATED)
        else:
            self._transition_to(RuntimeState.VALIDATION_FAILED)
            if self._configuration.strict_validation:
                raise RuntimeValidationError(
                    f"Validation failed: {report.critical_failures}"
                )

        self._publish_event(RuntimeValidationCompleted(
            runtime_id=self._runtime_id,
            payload={
                "validation_time_ms": duration_ms,
                "valid": report.is_valid,
                "errors": report.errors,
            },
        ))

        self._trace.add_entry(
            operation="validated",
            category="lifecycle",
            component="runtime",
            duration_ms=duration_ms,
            success=report.is_valid,
        )

        return report

    def health_check(self) -> RuntimeHealth:
        """Perform a health check.

        Returns:
            Health status.
        """
        return self._health_checker.check_all(
            container=self._components.container,
            event_bus=self._components.event_bus,
            capability_registry=self._components.capability_registry,
            boot_manager=self._components.boot_manager,
            session_manager=self._components.session_manager,
            lifecycle_manager=self._components.lifecycle_manager,
            orchestrator=self._components.orchestrator,
            scheduler=self._components.scheduler,
            planner=self._components.planner,
            knowledge_engine=self._components.knowledge_engine,
            memory_engine=self._components.memory_engine,
            reasoning_engine=self._components.reasoning_engine,
            decision_engine=self._components.decision_engine,
            tool_engine=self._components.tool_engine,
        )

    # =============================================================================
    # Start
    # =============================================================================

    def start(self) -> CognitiveRuntime:
        """Start the runtime.

        Performs final validation (if configured) and starts the runtime.

        Returns:
            Self for chaining.

        Raises:
            RuntimeStartError: If start fails.
        """
        if self.state == RuntimeState.RUNNING:
            return self

        try:
            # Ensure proper state
            if self.state == RuntimeState.CREATED:
                self.initialize()

            if self.state == RuntimeState.INITIALIZED:
                self.boot()

            if self.state == RuntimeState.BOOTED:
                # Auto-validate if configured
                if self._configuration.validate_before_start:
                    report = self.validate()
                    if not report.is_valid:
                        raise RuntimeStartError(
                            f"Pre-start validation failed: {report.critical_failures}"
                        )

            if self.state != RuntimeState.VALIDATED and self.state != RuntimeState.RUNNING:
                raise RuntimeStartError(
                    f"Cannot start from state: {self.state.value}"
                )

            self._transition_to(RuntimeState.RUNNING)

            self._metrics.record_runtime_start()

            # Create executor
            self._executor = CognitiveCycleExecutor(
                context=self._context,
                trace=self._trace,
                metrics=self._metrics,
                simulation_mode=self._configuration.simulation_mode,
                simulation_delay_ms=self._configuration.simulation_delay_ms,
            )

            # Add event handler to executor
            self._executor.add_event_handler(self._publish_event)

            self._trace.add_entry(
                operation="started",
                category="lifecycle",
                component="runtime",
            )

            return self

        except Exception as e:
            self._handle_error("start", e)
            raise RuntimeStartError(str(e))

    # =============================================================================
    # Session Management
    # =============================================================================

    def create_session(
        self,
        configuration: SessionConfiguration | None = None,
        user_id: str = "",
        hospital_id: str = "",
    ) -> SessionContext:
        """Create a new cognitive session.

        Args:
            configuration: Optional session configuration.
            user_id: User ID.
            hospital_id: Hospital ID.

        Returns:
            The new session context.

        Raises:
            SessionCreationError: If session creation fails.
            RuntimeStartError: If runtime is not running.
        """
        if not self.is_running:
            raise RuntimeStartError("Runtime must be running to create sessions")

        try:
            config = configuration or SessionConfiguration()
            session_type = config.session_type

            # Create session context
            session = self._context.create_session(
                user_id=user_id or config.user_id,
                hospital_id=hospital_id or config.hospital_id,
                session_type=session_type,
            )

            # Record in metrics
            self._metrics.record_session_created(session.session_id)

            self._publish_event(SessionCreated(
                runtime_id=self._runtime_id,
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "session_type": session_type,
                    "user_id": session.user_id,
                    "hospital_id": session.hospital_id,
                },
            ))

            self._trace.add_entry(
                operation="session_created",
                category="session",
                component="runtime",
                session_id=session.session_id,
                correlation_id=session.correlation_id,
            )

            return session

        except Exception as e:
            self._handle_error("session_creation", e)
            raise SessionCreationError(str(e))

    def start_session(self, session: SessionContext) -> SessionContext:
        """Start a cognitive session.

        Args:
            session: The session to start.

        Returns:
            The started session.

        Raises:
            RuntimeExecutionError: If session start fails.
        """
        if not self.is_running:
            raise RuntimeStartError("Runtime must be running")

        try:
            session.started_at = datetime.now(UTC).isoformat()

            self._publish_event(SessionStarted(
                runtime_id=self._runtime_id,
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                payload={
                    "started_at": session.started_at,
                },
            ))

            self._trace.add_entry(
                operation="session_started",
                category="session",
                component="runtime",
                session_id=session.session_id,
                correlation_id=session.correlation_id,
            )

            return session

        except Exception as e:
            self._handle_error("session_start", e)
            raise RuntimeExecutionError(str(e))

    def complete_session(
        self,
        session: SessionContext,
        success: bool = True,
        error: str | None = None,
    ) -> SessionContext:
        """Complete a cognitive session.

        Args:
            session: The session to complete.
            success: Whether session completed successfully.
            error: Error message if failed.

        Returns:
            The completed session.
        """
        try:
            session.completed_at = datetime.now(UTC).isoformat()
            duration_ms = 0
            if session.started_at:
                started = datetime.fromisoformat(session.started_at)
                completed = datetime.fromisoformat(session.completed_at)
                duration_ms = int((completed - started).total_seconds() * 1000)

            if success:
                self._publish_event(SessionCompleted(
                    runtime_id=self._runtime_id,
                    session_id=session.session_id,
                    correlation_id=session.correlation_id,
                    payload={
                        "completed_at": session.completed_at,
                        "duration_ms": duration_ms,
                        "cycles_completed": len(self._context.completed_cycles),
                    },
                ))
            else:
                self._publish_event(SessionFailed(
                    runtime_id=self._runtime_id,
                    session_id=session.session_id,
                    correlation_id=session.correlation_id,
                    payload={
                        "error": error or "Unknown error",
                        "failed_at": session.completed_at,
                    },
                ))

            # Record metrics
            self._metrics.record_session_completed(
                session_id=session.session_id,
                duration_ms=duration_ms,
                cycles_completed=len(self._context.completed_cycles),
                success=success,
                error=error,
            )

            self._context.complete_session()

            self._trace.add_entry(
                operation="session_completed",
                category="session",
                component="runtime",
                session_id=session.session_id,
                correlation_id=session.correlation_id,
                duration_ms=duration_ms,
                success=success,
                error=error,
            )

            return session

        except Exception as e:
            session.add_error(str(e))
            raise RuntimeExecutionError(str(e))

    # =============================================================================
    # Cognitive Cycle Execution
    # =============================================================================

    def execute_cognitive_cycle(
        self,
        session: SessionContext,
        intent: dict[str, Any],
    ) -> SessionContext:
        """Execute a complete cognitive cycle.

        This is the main entry point for processing a user request.
        It coordinates the flow through all engines.

        Args:
            session: The session context.
            intent: The intent/input data.

        Returns:
            The updated session context.

        Raises:
            RuntimeExecutionError: If cycle execution fails.
        """
        if not self.is_running:
            raise RuntimeStartError("Runtime must be running")
        if not self._executor:
            raise RuntimeExecutionError("Runtime executor not initialized")

        try:
            # Start session if not started
            if not session.started_at:
                self.start_session(session)

            # Execute the cycle
            cycle = self._executor.execute_cycle(session, intent)

            return session

        except Exception as e:
            self._handle_error("cognitive_cycle", e)
            raise RuntimeExecutionError(str(e))

    # =============================================================================
    # Shutdown
    # =============================================================================

    def shutdown(self, reason: str = "normal_shutdown") -> None:
        """Shutdown the runtime.

        Args:
            reason: Reason for shutdown.
        """
        if self.state == RuntimeState.STOPPED:
            return

        try:
            self._transition_to(RuntimeState.SHUTTING_DOWN)

            self._publish_event(RuntimeShutdown(
                runtime_id=self._runtime_id,
                payload={
                    "reason": reason,
                },
            ))

            # Cleanup
            if self._configuration.cleanup_on_shutdown:
                self._cleanup()

            # Calculate total duration
            total_duration_ms = 0
            if self._metrics.started_at:
                started = datetime.fromisoformat(self._metrics.started_at)
                total_duration_ms = int(
                    (datetime.now(UTC) - started).total_seconds() * 1000
                )

            self._metrics.record_runtime_completion(
                completed_at=datetime.now(UTC).isoformat(),
                total_duration_ms=total_duration_ms,
            )

            self._transition_to(RuntimeState.STOPPED)

            self._publish_event(RuntimeCompleted(
                runtime_id=self._runtime_id,
                payload={
                    "completed_at": datetime.now(UTC).isoformat(),
                    "total_duration_ms": total_duration_ms,
                    "cycles_completed": self._metrics.cycles_completed,
                    "sessions_completed": self._metrics.sessions_completed,
                    "metrics": self._metrics.to_dict(),
                },
            ))

            self._trace.add_entry(
                operation="shutdown",
                category="lifecycle",
                component="runtime",
                metadata={"reason": reason},
            )

        except Exception as e:
            self._handle_error("shutdown", e)
            raise RuntimeShutdownError(str(e))

    def _cleanup(self) -> None:
        """Clean up runtime resources."""
        # Dispose container
        container = self._components.container
        if container and hasattr(container, 'dispose'):
            try:
                container.dispose()
            except Exception:
                pass

        # Close event bus
        event_bus = self._components.event_bus
        if event_bus and hasattr(event_bus, 'close'):
            try:
                event_bus.close()
            except Exception:
                pass

    # =============================================================================
    # State Management
    # =============================================================================

    def _transition_to(self, target_state: RuntimeState) -> None:
        """Transition to a new state.

        Args:
            target_state: The target state.

        Raises:
            ValueError: If transition is not valid.
        """
        previous_state = self.state
        self._state_machine.transition(target_state)

        self._trace.record_transition(
            entity_type="runtime",
            entity_id=self._runtime_id,
            from_state=previous_state.value,
            to_state=target_state.value,
            reason=f"Transition from {previous_state.value}",
        )

    def _handle_error(self, operation: str, error: Exception) -> None:
        """Handle an error.

        Args:
            operation: The operation that failed.
            error: The error that occurred.
        """
        self._metrics.record_error(critical=True)
        self._trace.add_entry(
            operation=f"{operation}_failed",
            category="error",
            component="runtime",
            success=False,
            error=str(error),
        )

    # =============================================================================
    # Context Manager
    # =============================================================================

    def __enter__(self) -> CognitiveRuntime:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit."""
        self.shutdown(reason="context_exit")
        return False
