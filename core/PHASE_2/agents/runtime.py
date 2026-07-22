"""Cognitive Agent Runtime (CAR) for EREN OS.

Main runtime for coordinating multi-agent execution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.agents.capabilities import get_capability_registry
from core.PHASE_2.agents.communicator import get_communicator
from core.PHASE_2.agents.context import get_context_manager
from core.PHASE_2.agents.events import AgentEvent, AgentEventType, get_event_bus
from core.PHASE_2.agents.health import get_health_manager
from core.PHASE_2.agents.lifecycle import get_lifecycle_manager
from core.PHASE_2.agents.metrics import get_metrics_collector
from core.PHASE_2.agents.registry import get_registry
from core.PHASE_2.agents.scheduler import get_scheduler
from core.PHASE_2.agents.types import (
    AgentManifest,
    AgentStatus,
    AgentTask,
    RuntimeState,
)

if TYPE_CHECKING:
    pass


class CognitiveAgentRuntime:
    """Cognitive Agent Runtime.

    The Runtime does NOT:
    - Execute tasks itself
    - Know about OpenAI
    - Know about models
    - Know about retrieval
    - Know about databases

    It ONLY:
    - Registers agents
    - Schedules tasks
    - Coordinates communication
    - Manages lifecycle
    - Tracks health
    - Collects metrics

    Philosophy:
        Decision Engine decides.
        Agents execute.
        Runtime coordinates.
    """

    def __init__(self):
        """Initialize agent runtime."""
        # Core components
        self._registry = get_registry()
        self._scheduler = get_scheduler()
        self._communicator = get_communicator()
        self._lifecycle = get_lifecycle_manager()
        self._health = get_health_manager()
        self._context = get_context_manager()
        self._capabilities = get_capability_registry()
        self._events = get_event_bus()
        self._metrics = get_metrics_collector()

        # State
        self._state = RuntimeState()
        self._is_running = False

    def start(self) -> None:
        """Start the agent runtime."""
        self._is_running = True
        self._state.is_running = True
        self._state.started_at = datetime.now(UTC)

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.RUNTIME_STARTED,
            agent_id="runtime",
        ))

    def stop(self) -> None:
        """Stop the agent runtime."""
        self._is_running = False
        self._state.is_running = False

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.RUNTIME_STOPPED,
            agent_id="runtime",
        ))

    def register_agent(
        self,
        manifest: AgentManifest,
    ) -> AgentManifest:
        """Register an agent.

        Args:
            manifest: Agent manifest.

        Returns:
            Registered manifest.
        """
        # Register with registry
        self._registry.register(manifest)

        # Initialize lifecycle
        self._lifecycle.initialize(manifest.agent_id, manifest)

        # Register with health manager
        self._health.register_agent(manifest.agent_id)

        # Register capabilities
        cap_names = [cap.name for cap in manifest.capabilities]
        self._capabilities.register_agent_capabilities(manifest.agent_id, cap_names)

        # Update state
        self._state.total_agents += 1
        self._state.active_agents += 1

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.AGENT_REGISTERED,
            agent_id=manifest.agent_id,
            metadata={"agent_type": manifest.agent_type.value},
        ))

        return manifest

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            True if unregistered.
        """
        if self._registry.unregister(agent_id):
            self._health.unregister_agent(agent_id)
            self._state.active_agents -= 1

            # Publish event
            self._events.publish(AgentEvent(
                event_type=AgentEventType.AGENT_UNREGISTERED,
                agent_id=agent_id,
            ))

            return True

        return False

    def submit_task(
        self,
        capability: str,
        description: str,
        input_data: dict | None = None,
        priority: int = 5,
        depends_on: list[str] | None = None,
        correlation_id: str = "",
    ) -> AgentTask | None:
        """Submit a task for execution.

        Args:
            capability: Required capability.
            description: Task description.
            input_data: Task input.
            priority: Task priority (1-10).
            depends_on: Task dependencies.
            correlation_id: Correlation ID.

        Returns:
            Submitted task or None.
        """
        # Find available agent
        agent = self._registry.find_best_agent(capability)
        if not agent:
            return None

        # Submit task
        task = self._scheduler.submit_task(
            agent_id=agent.agent_id,
            capability=capability,
            description=description,
            input_data=input_data,
            priority=priority,
            depends_on=depends_on,
            max_retries=agent.retry_limit,
        )

        task.correlation_id = correlation_id

        # Update state
        self._state.pending_tasks += 1

        # Record metrics
        self._metrics.record_task_submitted(
            task_id=task.task_id,
            agent_id=agent.agent_id,
            capability=capability,
        )

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.TASK_SUBMITTED,
            agent_id=agent.agent_id,
            task_id=task.task_id,
            capability=capability,
        ))

        return task

    def start_task(
        self,
        task_id: str,
        agent_id: str,
    ) -> AgentTask | None:
        """Start a task.

        Args:
            task_id: Task ID.
            agent_id: Agent ID.

        Returns:
            Started task or None.
        """
        task = self._scheduler.start_task(task_id, agent_id)
        if not task:
            return None

        # Update agent status
        self._registry.set_status(agent_id, AgentStatus.BUSY)
        self._health.record_task_start(agent_id)

        # Update state
        self._state.pending_tasks -= 1
        self._state.running_tasks += 1

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.TASK_STARTED,
            agent_id=agent_id,
            task_id=task_id,
        ))

        return task

    def complete_task(
        self,
        task_id: str,
        output_data: Any,
    ) -> AgentTask | None:
        """Complete a task.

        Args:
            task_id: Task ID.
            output_data: Task output.

        Returns:
            Completed task or None.
        """
        task = self._scheduler.complete_task(task_id, output_data)
        if not task:
            return None

        # Update agent status
        self._registry.set_status(task.agent_id, AgentStatus.IDLE)
        duration_ms = task.duration_seconds * 1000
        self._health.record_task_success(task.agent_id, duration_ms)

        # Update state
        self._state.running_tasks -= 1
        self._state.completed_tasks += 1

        # Record metrics
        self._metrics.record_task_completed(
            task_id=task_id,
            agent_id=task.agent_id,
            duration_ms=duration_ms,
        )

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.TASK_COMPLETED,
            agent_id=task.agent_id,
            task_id=task_id,
        ))

        return task

    def fail_task(
        self,
        task_id: str,
        error: str,
    ) -> AgentTask | None:
        """Fail a task.

        Args:
            task_id: Task ID.
            error: Error message.

        Returns:
            Failed task or None.
        """
        task = self._scheduler.fail_task(task_id, error)
        if not task:
            return None

        # Update agent status
        self._registry.set_status(task.agent_id, AgentStatus.IDLE)
        duration_ms = task.duration_seconds * 1000
        self._health.record_task_failure(task.agent_id, duration_ms)

        # Update state
        self._state.running_tasks -= 1
        if task.status.value == "failed":
            self._state.failed_tasks += 1

        # Record metrics
        self._metrics.record_task_failed(
            task_id=task_id,
            agent_id=task.agent_id,
            duration_ms=duration_ms,
            error=error,
        )

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.TASK_FAILED,
            agent_id=task.agent_id,
            task_id=task_id,
            error=error,
        ))

        return task

    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        content: Any,
        message_type: str = "request",
    ) -> None:
        """Send message between agents.

        Args:
            sender_id: Sender agent ID.
            receiver_id: Receiver agent ID.
            content: Message content.
            message_type: Message type.
        """
        self._communicator.send(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
        )

        # Record metrics
        self._metrics.record_message_sent(sender_id, receiver_id)

        # Publish event
        self._events.publish(AgentEvent(
            event_type=AgentEventType.MESSAGE_SENT,
            agent_id=sender_id,
            metadata={
                "receiver_id": receiver_id,
                "message_type": message_type,
            },
        ))

    def get_state(self) -> RuntimeState:
        """Get runtime state.

        Returns:
            Current runtime state.
        """
        self._state.active_agents = len(self._registry.get_all())
        self._state.last_updated = datetime.now(UTC)
        return self._state

    def get_agent(self, agent_id: str) -> AgentManifest | None:
        """Get agent manifest.

        Args:
            agent_id: Agent ID.

        Returns:
            Agent manifest or None.
        """
        return self._registry.get(agent_id)

    def get_all_agents(self) -> list[AgentManifest]:
        """Get all registered agents.

        Returns:
            List of agents.
        """
        return self._registry.get_all()

    def get_task(self, task_id: str) -> AgentTask | None:
        """Get task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Task or None.
        """
        return self._scheduler.get_task(task_id)

    def get_ready_tasks(self) -> list[AgentTask]:
        """Get tasks ready for execution.

        Returns:
            List of ready tasks.
        """
        # Get completed tasks
        completed = {
            t.task_id: t.output_data
            for t in self._scheduler.get_all_tasks()
            if t.status.value == "completed"
        }

        return self._scheduler.get_ready_tasks(completed)


# Global runtime
_global_runtime: CognitiveAgentRuntime | None = None
_runtime_lock = __import__("threading").Lock()


def get_agent_runtime() -> CognitiveAgentRuntime:
    """Get the global agent runtime.

    Returns:
        Global CognitiveAgentRuntime instance.
    """
    global _global_runtime
    with _runtime_lock:
        if _global_runtime is None:
            _global_runtime = CognitiveAgentRuntime()
        return _global_runtime


def reset_agent_runtime() -> None:
    """Reset the global agent runtime."""
    global _global_runtime
    with _runtime_lock:
        _global_runtime = None
