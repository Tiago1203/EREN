"""Tests for the Cognitive Scheduler."""

from __future__ import annotations

from core.PHASE_2.scheduler import (
    CognitiveScheduler,
    SchedulerFactory,
    TaskState,
    TaskPriority,
    TaskType,
    SchedulingPolicy,
    PolicyPresets,
    FIFOStrategy,
    PriorityStrategy,
    DeadlineFirstStrategy,
    CriticalFirstStrategy,
    StrategyFactory,
    SchedulingQueue,
    SchedulingMetricsCollector,
)


class TestTaskStates:
    """Tests for task states."""

    def test_all_states_defined(self) -> None:
        """All states should be defined."""
        assert TaskState.PENDING
        assert TaskState.READY
        assert TaskState.RUNNING
        assert TaskState.WAITING
        assert TaskState.BLOCKED
        assert TaskState.COMPLETED
        assert TaskState.FAILED
        assert TaskState.CANCELLED


class TestTaskPriorities:
    """Tests for task priorities."""

    def test_all_priorities_defined(self) -> None:
        """All priorities should be defined."""
        assert TaskPriority.CRITICAL
        assert TaskPriority.HIGH
        assert TaskPriority.NORMAL
        assert TaskPriority.LOW
        assert TaskPriority.BACKGROUND


class TestSchedulingQueue:
    """Tests for scheduling queue."""

    def test_queue_creation(self) -> None:
        """Creating queue should work."""
        queue = SchedulingQueue(name="test")
        assert queue.name == "test"
        assert queue.size == 0

    def test_enqueue(self) -> None:
        """Enqueueing task should work."""
        queue = SchedulingQueue(name="test")
        from core.PHASE_2.scheduler import CognitiveTask, TaskMetadata

        metadata = TaskMetadata(
            task_id="task_1",
            session_id="session_1",
            correlation_id="corr_1",
        )
        task = CognitiveTask(
            metadata=metadata,
            task_type=TaskType.PLANNING,
            capability="planner.execute",
        )

        queue.enqueue(task)
        assert queue.size == 1

    def test_dequeue(self) -> None:
        """Dequeuing task should work."""
        queue = SchedulingQueue(name="test")
        from core.PHASE_2.scheduler import CognitiveTask, TaskMetadata

        metadata = TaskMetadata(
            task_id="task_1",
            session_id="session_1",
            correlation_id="corr_1",
        )
        task = CognitiveTask(
            metadata=metadata,
            task_type=TaskType.PLANNING,
            capability="planner.execute",
        )

        queue.enqueue(task)
        dequeued = queue.dequeue()

        assert dequeued is not None
        assert dequeued.metadata.task_id == "task_1"
        assert queue.size == 0


class TestStrategies:
    """Tests for scheduling strategies."""

    def test_fifo_strategy(self) -> None:
        """FIFO strategy should work."""
        strategy = FIFOStrategy()
        assert strategy.name() == "FIFO"

    def test_priority_strategy(self) -> None:
        """Priority strategy should work."""
        strategy = PriorityStrategy()
        assert strategy.name() == "Priority"

    def test_deadline_strategy(self) -> None:
        """Deadline strategy should work."""
        strategy = DeadlineFirstStrategy()
        assert strategy.name() == "DeadlineFirst"

    def test_critical_strategy(self) -> None:
        """Critical strategy should work."""
        strategy = CriticalFirstStrategy()
        assert strategy.name() == "CriticalFirst"

    def test_strategy_factory(self) -> None:
        """Strategy factory should work."""
        strategies = StrategyFactory.list_strategies()
        assert "FIFO" in strategies
        assert "Priority" in strategies
        assert "DeadlineFirst" in strategies
        assert "CriticalFirst" in strategies


class TestCognitiveScheduler:
    """Tests for CognitiveScheduler."""

    def test_scheduler_creation(self) -> None:
        """Creating scheduler should work."""
        scheduler = CognitiveScheduler()
        assert scheduler is not None

    def test_submit_task(self) -> None:
        """Submitting task should work."""
        scheduler = CognitiveScheduler()
        task = scheduler.submit_task(
            task_type=TaskType.PLANNING,
            capability="planner.execute",
            session_id="session_1",
            correlation_id="corr_1",
            priority=TaskPriority.HIGH,
        )

        assert task is not None
        assert task.metadata.task_id.startswith("task_")
        assert task.task_type == TaskType.PLANNING
        assert task.capability == "planner.execute"

    def test_schedule_next(self) -> None:
        """Scheduling next task should work."""
        scheduler = CognitiveScheduler()
        scheduler.submit_task(
            task_type=TaskType.PLANNING,
            capability="planner.execute",
            session_id="session_1",
            correlation_id="corr_1",
        )

        next_task = scheduler.schedule_next()
        assert next_task is not None

    def test_complete_task(self) -> None:
        """Completing task should work."""
        scheduler = CognitiveScheduler()
        task = scheduler.submit_task(
            task_type=TaskType.PLANNING,
            capability="planner.execute",
            session_id="session_1",
            correlation_id="corr_1",
        )

        result = scheduler.complete_task(task.metadata.task_id, {"status": "ok"})
        assert result is True

        completed_task = scheduler.get_task(task.metadata.task_id)
        assert completed_task is not None
        assert completed_task.state == TaskState.COMPLETED


class TestPolicies:
    """Tests for policies."""

    def test_default_policy(self) -> None:
        """Default policy should work."""
        policy = SchedulingPolicy()
        assert policy.strategy == "Priority"
        assert policy.max_retries == 3

    def test_low_latency_preset(self) -> None:
        """Low latency preset should work."""
        policy = PolicyPresets.low_latency()
        assert policy.task_timeout_ms == 10000

    def test_critical_preset(self) -> None:
        """Critical preset should work."""
        policy = PolicyPresets.critical()
        assert policy.strategy == "CriticalFirst"
        assert policy.max_retries == 1


class TestMetrics:
    """Tests for metrics."""

    def test_metrics_collector(self) -> None:
        """Metrics collector should work."""
        collector = SchedulingMetricsCollector()
        collector.record_task_submitted()
        collector.record_task_scheduled()

        assert collector.tasks_submitted == 1
        assert collector.tasks_scheduled == 1
