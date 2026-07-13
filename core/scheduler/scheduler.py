"""Cognitive Scheduler - Core Engine.

The scheduler coordinates task execution timing for cognitive engines.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .scheduling_events import SchedulingEventPublisher
from .scheduling_metrics import SchedulingMetricsCollector
from .scheduling_policy import PolicyPresets, SchedulingPolicy
from .scheduling_queue import MultiQueueManager, SchedulingQueue
from .scheduling_strategy import (
    FIFOStrategy,
    PriorityStrategy,
    SchedulingStrategy,
    StrategyFactory,
)
from .scheduling_trace import SchedulingTraceCollector
from .scheduling_types import (
    CognitiveTask,
    QueueStatistics,
    SchedulingDecision,
    TaskMetadata,
    TaskPriority,
    TaskState,
    TaskType,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Cognitive Scheduler
# =============================================================================


class CognitiveScheduler:
    """The main cognitive scheduler.

    Responsibilities:
    - Manage cognitive task queues
    - Select tasks for execution based on strategy
    - Coordinate with Capability Registry for task execution
    - Enforce scheduling policies
    - Collect metrics and traces

    The scheduler does NOT:
    - Execute tasks directly
    - Know implementation details of capabilities
    - Make business decisions
    - Access memory or knowledge
    """

    def __init__(
        self,
        policy: SchedulingPolicy | None = None,
    ) -> None:
        """Initialize the scheduler.

        Args:
            policy: Scheduling policy.
        """
        # Policy
        self._policy = policy or SchedulingPolicy()

        # Queue management
        self._queue_manager = MultiQueueManager()
        self._default_queue = self._queue_manager.create_queue("default")

        # Strategy
        self._strategy: SchedulingStrategy = StrategyFactory.create(self._policy.strategy)

        # Event publisher
        self._event_publisher = SchedulingEventPublisher()

        # Metrics
        self._metrics = SchedulingMetricsCollector()

        # Trace
        self._trace = SchedulingTraceCollector()

        # Thread safety
        self._lock = threading.RLock()

    # =========================================================================
    # Task Management
    # =========================================================================

    def submit_task(
        self,
        task_type: TaskType,
        capability: str,
        session_id: str,
        correlation_id: str,
        parameters: dict | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: str = "",
        dependencies: tuple[str, ...] = (),
        max_retries: int = 3,
        timeout_ms: int = 30000,
    ) -> CognitiveTask:
        """Submit a new cognitive task.

        Args:
            task_type: Type of task.
            capability: Required capability.
            session_id: Session ID.
            correlation_id: Correlation ID.
            parameters: Task parameters.
            priority: Task priority.
            deadline: Deadline ISO timestamp.
            dependencies: Task dependencies.
            max_retries: Maximum retries.
            timeout_ms: Task timeout.

        Returns:
            The created task.
        """
        task_id = f"task_{uuid.uuid4().hex[:16]}"

        metadata = TaskMetadata(
            task_id=task_id,
            session_id=session_id,
            correlation_id=correlation_id,
        )

        from .scheduling_types import TaskDependencies

        task = CognitiveTask(
            metadata=metadata,
            task_type=task_type,
            capability=capability,
            parameters=parameters or {},
            priority=priority,
            deadline=deadline,
            dependencies=TaskDependencies(depends_on=dependencies),
            max_retries=max_retries,
            timeout_ms=timeout_ms,
        )

        with self._lock:
            self._default_queue.enqueue(task)
            self._metrics.record_task_submitted()

            self._trace.add_entry(
                task_id=task_id,
                session_id=session_id,
                correlation_id=correlation_id,
                action="SUBMITTED",
                task_state=task.state.value,
                capability=capability,
                strategy_used=self._strategy.name(),
            )

        self._event_publisher.publish(
            event_type="TaskSubmitted",
            task_id=task_id,
            session_id=session_id,
            capability=capability,
        )

        return task

    def schedule_next(self) -> CognitiveTask | None:
        """Schedule the next task for execution.

        Returns:
            Next task to execute or None.
        """
        with self._lock:
            # Get ready tasks
            ready_tasks = self._default_queue.get_ready()

            # If no ready tasks, check pending
            if not ready_tasks:
                ready_tasks = self._default_queue.get_pending()

            if not ready_tasks:
                return None

            # Apply strategy
            selected_tasks = self._strategy.select(ready_tasks)

            if not selected_tasks:
                return None

            task = selected_tasks[0]

            # Make scheduling decision
            decision = SchedulingDecision(
                decision_id=f"dec_{uuid.uuid4().hex[:16]}",
                task_id=task.metadata.task_id,
                selected_capability=task.capability,
                reason=f"Selected by {self._strategy.name()} strategy",
                queue_position=0,
                estimated_wait_ms=0,
            )

            # Mark as scheduled
            self._metrics.record_task_scheduled()
            self._metrics.record_scheduling_decision()

            self._trace.add_entry(
                task_id=task.metadata.task_id,
                session_id=task.metadata.session_id,
                correlation_id=task.metadata.correlation_id,
                action="SCHEDULED",
                task_state=TaskState.READY.value,
                capability=task.capability,
                strategy_used=self._strategy.name(),
                metadata={"decision_id": decision.decision_id},
            )

            self._event_publisher.publish(
                event_type="TaskScheduled",
                task_id=task.metadata.task_id,
                capability=task.capability,
                decision_id=decision.decision_id,
            )

            return task

    def start_task(self, task_id: str, assigned_to: str) -> bool:
        """Mark a task as started.

        Args:
            task_id: Task ID.
            assigned_to: Capability assigned to.

        Returns:
            True if task was started.
        """
        task = self._default_queue.get(task_id)
        if not task:
            return False

        task.mark_running(assigned_to)

        self._trace.add_entry(
            task_id=task_id,
            session_id=task.metadata.session_id,
            correlation_id=task.metadata.correlation_id,
            action="STARTED",
            task_state=TaskState.RUNNING.value,
            capability=task.capability,
            strategy_used=self._strategy.name(),
        )

        self._event_publisher.publish(
            event_type="TaskStarted",
            task_id=task_id,
            assigned_to=assigned_to,
        )

        return True

    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed.

        Args:
            task_id: Task ID.
            result: Task result.

        Returns:
            True if task was completed.
        """
        task = self._default_queue.get(task_id)
        if not task:
            return False

        task.mark_completed(result)

        self._metrics.record_task_completed(task.execution_time_ms)

        self._trace.add_entry(
            task_id=task_id,
            session_id=task.metadata.session_id,
            correlation_id=task.metadata.correlation_id,
            action="COMPLETED",
            task_state=TaskState.COMPLETED.value,
            capability=task.capability,
            strategy_used=self._strategy.name(),
        )

        self._event_publisher.publish(
            event_type="TaskCompleted",
            task_id=task_id,
            execution_time_ms=task.execution_time_ms,
        )

        return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed.

        Args:
            task_id: Task ID.
            error: Error message.

        Returns:
            True if task was marked as failed.
        """
        task = self._default_queue.get(task_id)
        if not task:
            return False

        task.mark_failed(error)

        if task.can_retry:
            self._metrics.record_task_retry()
            self._event_publisher.publish(
                event_type="TaskRetry",
                task_id=task_id,
                retries=task.retries,
                error=error,
            )
        else:
            self._metrics.record_task_failed()
            self._event_publisher.publish(
                event_type="TaskFailed",
                task_id=task_id,
                retries=task.retries,
                error=error,
            )

        self._trace.add_entry(
            task_id=task_id,
            session_id=task.metadata.session_id,
            correlation_id=task.metadata.correlation_id,
            action="FAILED",
            task_state=TaskState.FAILED.value,
            capability=task.capability,
            strategy_used=self._strategy.name(),
            metadata={"error": error, "retries": task.retries},
        )

        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID.

        Returns:
            True if task was cancelled.
        """
        task = self._default_queue.get(task_id)
        if not task:
            return False

        task.mark_cancelled()
        self._default_queue.remove(task_id)
        self._metrics.record_task_cancelled()

        self._trace.add_entry(
            task_id=task_id,
            session_id=task.metadata.session_id,
            correlation_id=task.metadata.correlation_id,
            action="CANCELLED",
            task_state=TaskState.CANCELLED.value,
            capability=task.capability,
            strategy_used=self._strategy.name(),
        )

        self._event_publisher.publish(
            event_type="TaskCancelled",
            task_id=task_id,
        )

        return True

    def get_task(self, task_id: str) -> CognitiveTask | None:
        """Get a task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Task or None.
        """
        return self._default_queue.get(task_id)

    def get_queue_stats(self) -> QueueStatistics:
        """Get queue statistics.

        Returns:
            Queue statistics.
        """
        return self._default_queue.get_statistics()

    def get_metrics(self) -> dict:
        """Get scheduler metrics.

        Returns:
            Metrics dictionary.
        """
        return self._metrics.to_dict()

    # =========================================================================
    # Strategy Management
    # =========================================================================

    def set_strategy(self, strategy_name: str) -> None:
        """Set the scheduling strategy.

        Args:
            strategy_name: Strategy name.
        """
        self._strategy = StrategyFactory.create(strategy_name)
        self._metrics.record_strategy_change()

        self._event_publisher.publish(
            event_type="SchedulingStrategyChanged",
            old_strategy=self._policy.strategy,
            new_strategy=strategy_name,
        )

    def get_strategy(self) -> str:
        """Get current strategy name.

        Returns:
            Strategy name.
        """
        return self._strategy.name()


# =============================================================================
# Factory
# =============================================================================


class SchedulerFactory:
    """Factory for creating schedulers."""

    @staticmethod
    def create_default() -> CognitiveScheduler:
        """Create a scheduler with default policy.

        Returns:
            New scheduler.
        """
        return CognitiveScheduler()

    @staticmethod
    def create_with_policy(policy: SchedulingPolicy) -> CognitiveScheduler:
        """Create a scheduler with custom policy.

        Args:
            policy: Custom policy.

        Returns:
            New scheduler.
        """
        return CognitiveScheduler(policy=policy)

    @staticmethod
    def create_low_latency() -> CognitiveScheduler:
        """Create a low latency scheduler.

        Returns:
            New scheduler.
        """
        return CognitiveScheduler(policy=PolicyPresets.low_latency())

    @staticmethod
    def create_high_throughput() -> CognitiveScheduler:
        """Create a high throughput scheduler.

        Returns:
            New scheduler.
        """
        return CognitiveScheduler(policy=PolicyPresets.high_throughput())

    @staticmethod
    def create_critical() -> CognitiveScheduler:
        """Create a critical environment scheduler.

        Returns:
            New scheduler.
        """
        return CognitiveScheduler(policy=PolicyPresets.critical())
