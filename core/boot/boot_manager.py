"""Cognitive Boot Manager - Core Engine.

The official component for starting EREN in an orderly and reproducible manner.

Architecture only -- no implementations, no business logic.

This component does NOT:
- Create concrete implementations
- Break existing contracts
- Modify existing motors
- Create circular dependencies

It ONLY prepares infrastructure so that the Dependency Injection Container
can create real instances later.
"""

import threading
from datetime import datetime, timezone

from .boot_events import BootEventPublisher, BootEventType
from .boot_metrics import BootMetricsCollector
from .boot_policy import BootPolicy, BootPolicyPresets
from .boot_trace import BootTraceCollector
from .boot_types import (
    BOOT_SEQUENCE,
    BootConfiguration,
    BootResult,
    BootState,
    BootStatus,
    BootStep,
)


class CognitiveBootManager:
    """The main cognitive boot manager.

    This is the ONLY authorized component for starting EREN.

    Responsibilities:
    - Coordinate the boot sequence
    - Manage boot state transitions
    - Validate contracts before boot
    - Publish boot events
    - Collect boot metrics and traces
    - Support rollback on failure

    The Boot Manager does NOT:
    - Create concrete implementations
    - Break existing contracts
    - Modify existing motors
    - Create circular dependencies
    """

    def __init__(
        self,
        policy: BootPolicy = None,
        configuration: BootConfiguration = None,
    ):
        """Initialize the boot manager.

        Args:
            policy: Boot policy.
            configuration: Boot configuration.
        """
        self._policy = policy or BootPolicy()
        self._configuration = configuration or BootConfiguration()

        self._event_publisher = BootEventPublisher()
        self._metrics = BootMetricsCollector()
        self._trace = BootTraceCollector()

        self._state = BootState.CREATED
        self._steps = []
        self._components = {}

        # P0.1: Thread-safety for concurrent access
        self._lock = threading.RLock()

    @property
    def state(self) -> str:
        """Get current boot state."""
        with self._lock:
            return self._state

    @property
    def steps(self) -> list:
        """Get boot steps."""
        with self._lock:
            return self._steps.copy()

    @property
    def components(self) -> dict:
        """Get initialized components."""
        with self._lock:
            return self._components.copy()

    def get_trace(self) -> list:
        """Get boot trace."""
        with self._lock:
            return self._trace.get_all_entries()

    def get_metrics(self) -> dict:
        """Get boot metrics."""
        with self._lock:
            return self._metrics.to_dict()

    def boot(self) -> BootResult:
        """Execute the complete boot sequence.

        Returns:
            BootResult with success status and details.
        """
        start_time = datetime.now(timezone.utc)

        with self._lock:
            self._metrics.record_boot_started()

            self._event_publisher.publish(
                BootEventType.BOOT_STARTED,
                state=self._state,
            )

            self._trace.add_entry(
                step_name="boot",
                state=self._state,
                status="started",
            )

            try:
                # Execute boot sequence
                for step_key, step_name, target_state in BOOT_SEQUENCE:
                    step = self._execute_step(step_key, step_name, target_state)
                    self._steps.append(step)

                    if step.status == BootStatus.FAILED:
                        if self._policy.stop_on_error:
                            break

                # Check if boot was successful
                failed_steps = [s for s in self._steps if s.status == BootStatus.FAILED]

                if failed_steps:
                    self._state = BootState.FAILED
                    duration_ms = int(
                        (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    )
                    self._metrics.record_boot_failure(duration_ms)

                    self._event_publisher.publish(
                        BootEventType.BOOT_FAILED,
                        state=self._state,
                        failed_steps=len(failed_steps),
                    )

                    return BootResult(
                        success=False,
                        state=self._state,
                        steps=self._steps.copy(),
                        error=failed_steps[0].error,
                        duration_ms=duration_ms,
                        components=self._components.copy(),
                    )

                # Boot successful
                self._state = BootState.READY
                duration_ms = int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )
                self._metrics.record_boot_success(duration_ms)

                self._event_publisher.publish(
                    BootEventType.BOOT_COMPLETED,
                    state=self._state,
                )

                self._trace.add_entry(
                    step_name="boot",
                    state=self._state,
                    status="completed",
                    duration_ms=duration_ms,
                )

                return BootResult(
                    success=True,
                    state=self._state,
                    steps=self._steps.copy(),
                    duration_ms=duration_ms,
                    components=self._components.copy(),
                )

            except Exception as e:
                duration_ms = int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )
                self._state = BootState.FAILED
                self._metrics.record_boot_failure(duration_ms)

                self._event_publisher.publish(
                    BootEventType.BOOT_FAILED,
                    state=self._state,
                    error=str(e),
                )

                return BootResult(
                    success=False,
                    state=self._state,
                    steps=self._steps.copy(),
                    error=str(e),
                    duration_ms=duration_ms,
                    components=self._components.copy(),
                )

    def _execute_step(self, step_key: str, step_name: str, target_state: str) -> BootStep:
        """Execute a single boot step.

        Args:
            step_key: Key of the step.
            step_name: Display name of the step.
            target_state: Target state after step.

        Returns:
            BootStep with execution result.
        """
        step = BootStep(name=step_name, state=target_state)
        step.status = BootStatus.IN_PROGRESS

        start_time = datetime.now(timezone.utc)

        self._event_publisher.publish(
            BootEventType.BOOT_STEP_STARTED,
            step_name=step_name,
            state=target_state,
        )

        self._trace.add_entry(
            step_name=step_name,
            state=target_state,
            status="started",
        )

        try:
            # Execute step via handler
            component = self._execute_step_handler(step_key)

            if component is not None:
                with self._lock:
                    self._components[step_key] = component

            step.status = BootStatus.COMPLETED
            step.duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            self._metrics.record_step_completed()

            self._event_publisher.publish(
                BootEventType.BOOT_STEP_COMPLETED,
                step_name=step_name,
                duration_ms=step.duration_ms,
            )

            self._trace.add_entry(
                step_name=step_name,
                state=target_state,
                status="completed",
                duration_ms=step.duration_ms,
            )

        except Exception as e:
            step.status = BootStatus.FAILED
            step.error = str(e)
            step.duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            self._metrics.record_step_failed()

            self._event_publisher.publish(
                BootEventType.BOOT_STEP_FAILED,
                step_name=step_name,
                error=str(e),
            )

            self._trace.add_entry(
                step_name=step_name,
                state=target_state,
                status="failed",
                error=str(e),
                duration_ms=step.duration_ms,
            )

        return step

    def _execute_step_handler(self, step_key: str):
        """Execute step handler.

        This method prepares the infrastructure for each component.
        It does NOT create concrete implementations.

        Args:
            step_key: Key of the step.

        Returns:
            Prepared infrastructure (contracts/placeholders).
        """
        handlers = {
            "load_configuration": self._load_configuration,
            "create_event_bus": self._create_event_bus,
            "create_capability_registry": self._create_capability_registry,
            "create_context_manager": self._create_context_manager,
            "create_memory_engine": self._create_memory_engine,
            "create_knowledge_engine": self._create_knowledge_engine,
            "create_tool_engine": self._create_tool_engine,
            "create_planner": self._create_planner,
            "create_reasoning": self._create_reasoning,
            "create_decision": self._create_decision,
            "create_scheduler": self._create_scheduler,
            "create_orchestrator": self._create_orchestrator,
        }

        handler = handlers.get(step_key)
        if handler:
            return handler()

        return None

    def _load_configuration(self):
        """Load configuration.

        Returns:
            Configuration placeholder.
        """
        return {"config": self._configuration}

    def _create_event_bus(self):
        """Prepare Event Bus infrastructure.

        Returns:
            Event Bus contract placeholder.
        """
        return {"type": "event_bus", "interface": "EventPublisher"}

    def _create_capability_registry(self):
        """Prepare Capability Registry infrastructure.

        Returns:
            Capability Registry contract placeholder.
        """
        return {"type": "capability_registry", "interface": "CapabilityRegistry"}

    def _create_context_manager(self):
        """Prepare Context Manager infrastructure.

        Returns:
            Context Manager contract placeholder.
        """
        return {"type": "context_manager", "interface": "ContextManager"}

    def _create_memory_engine(self):
        """Prepare Memory Engine infrastructure.

        Returns:
            Memory Engine contract placeholder.
        """
        return {"type": "memory_engine", "interface": "MemoryContract"}

    def _create_knowledge_engine(self):
        """Prepare Knowledge Engine infrastructure.

        Returns:
            Knowledge Engine contract placeholder.
        """
        return {"type": "knowledge_engine", "interface": "KnowledgeContract"}

    def _create_tool_engine(self):
        """Prepare Tool Engine infrastructure.

        Returns:
            Tool Engine contract placeholder.
        """
        return {"type": "tool_engine", "interface": "ToolContract"}

    def _create_planner(self):
        """Prepare Planner infrastructure.

        Returns:
            Planner contract placeholder.
        """
        return {"type": "planner", "interface": "PlannerContract"}

    def _create_reasoning(self):
        """Prepare Reasoning Engine infrastructure.

        Returns:
            Reasoning Engine contract placeholder.
        """
        return {"type": "reasoning_engine", "interface": "ReasoningContract"}

    def _create_decision(self):
        """Prepare Decision Engine infrastructure.

        Returns:
            Decision Engine contract placeholder.
        """
        return {"type": "decision_engine", "interface": "DecisionContract"}

    def _create_scheduler(self):
        """Prepare Scheduler infrastructure.

        Returns:
            Scheduler contract placeholder.
        """
        return {"type": "scheduler", "interface": "SchedulingContract"}

    def _create_orchestrator(self):
        """Prepare Orchestrator infrastructure.

        Returns:
            Orchestrator contract placeholder.
        """
        return {"type": "orchestrator", "interface": "OrchestratorContract"}


class BootManagerFactory:
    """Factory for creating boot managers."""

    @staticmethod
    def create_default():
        """Create a boot manager with default settings."""
        return CognitiveBootManager()

    @staticmethod
    def create_development():
        """Create a boot manager for development."""
        return CognitiveBootManager(
            policy=BootPolicyPresets.development(),
        )

    @staticmethod
    def create_production():
        """Create a boot manager for production."""
        return CognitiveBootManager(
            policy=BootPolicyPresets.production(),
        )

    @staticmethod
    def create_testing():
        """Create a boot manager for testing."""
        return CognitiveBootManager(
            policy=BootPolicyPresets.testing(),
        )
