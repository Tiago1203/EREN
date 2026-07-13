"""Scheduling strategies.

Defines different scheduling strategies for task selection.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

from .scheduling_types import CognitiveTask, TaskPriority

if TYPE_CHECKING:
    pass


# =============================================================================
# Scheduling Strategy Interface
# =============================================================================


class SchedulingStrategy(ABC):
    """Base class for scheduling strategies."""

    @abstractmethod
    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select tasks for execution.

        Args:
            tasks: Available tasks.

        Returns:
            Ordered list of tasks.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Get strategy name."""
        ...


# =============================================================================
# FIFO Strategy
# =============================================================================


class FIFOStrategy(SchedulingStrategy):
    """First-In-First-Out strategy.

    Tasks are executed in the order they were enqueued.
    """

    def name(self) -> str:
        """Get strategy name."""
        return "FIFO"

    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select tasks in FIFO order.

        Args:
            tasks: Available tasks.

        Returns:
            Tasks in FIFO order.
        """
        return sorted(tasks, key=lambda t: t.metadata.created_at)


# =============================================================================
# Priority Strategy
# =============================================================================


class PriorityStrategy(SchedulingStrategy):
    """Priority-based strategy.

    Higher priority tasks are executed first.
    """

    def name(self) -> str:
        """Get strategy name."""
        return "Priority"

    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select tasks by priority.

        Args:
            tasks: Available tasks.

        Returns:
            Tasks ordered by priority.
        """
        return sorted(
            tasks,
            key=lambda t: (t.priority.value, t.metadata.created_at)
        )


# =============================================================================
# Deadline First Strategy
# =============================================================================


class DeadlineFirstStrategy(SchedulingStrategy):
    """Deadline-based strategy.

    Tasks with earlier deadlines are executed first.
    """

    def name(self) -> str:
        """Get strategy name."""
        return "DeadlineFirst"

    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select tasks by deadline.

        Args:
            tasks: Available tasks.

        Returns:
            Tasks ordered by deadline.
        """
        def deadline_sort_key(task: CognitiveTask) -> tuple:
            if task.deadline:
                try:
                    dt = datetime.fromisoformat(task.deadline)
                    return (0, dt)
                except ValueError:
                    pass
            return (1, datetime.max)

        return sorted(tasks, key=deadline_sort_key)


# =============================================================================
# Critical First Strategy
# =============================================================================


class CriticalFirstStrategy(SchedulingStrategy):
    """Critical task strategy.

    Critical and high priority tasks are executed first,
    with deadline awareness.
    """

    def name(self) -> str:
        """Get strategy name."""
        return "CriticalFirst"

    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select critical tasks first.

        Args:
            tasks: Available tasks.

        Returns:
            Critical tasks prioritized.
        """
        def critical_sort_key(task: CognitiveTask) -> tuple:
            # Priority first
            priority_score = task.priority.value

            # Deadline urgency
            deadline_score = 0
            if task.deadline:
                try:
                    deadline = datetime.fromisoformat(task.deadline)
                    now = datetime.now(timezone.utc)
                    time_remaining = (deadline - now).total_seconds()
                    if time_remaining < 0:
                        deadline_score = -1  # Overdue
                    elif time_remaining < 60:
                        deadline_score = 0  # Urgent
                    else:
                        deadline_score = 1  # Normal
                except ValueError:
                    deadline_score = 1

            return (priority_score, deadline_score, task.metadata.created_at)

        return sorted(tasks, key=critical_sort_key)


# =============================================================================
# Fair Scheduling Strategy
# =============================================================================


class FairSchedulingStrategy(SchedulingStrategy):
    """Fair scheduling strategy.

    Distributes work evenly across sessions/capabilities.
    """

    def __init__(self) -> None:
        """Initialize fair strategy."""
        self._session_counts: dict[str, int] = {}

    def name(self) -> str:
        """Get strategy name."""
        return "FairScheduling"

    def select(
        self,
        tasks: list[CognitiveTask],
    ) -> list[CognitiveTask]:
        """Select tasks fairly.

        Args:
            tasks: Available tasks.

        Returns:
            Tasks with fair distribution.
        """
        def fair_sort_key(task: CognitiveTask) -> tuple:
            session_id = task.metadata.session_id
            count = self._session_counts.get(session_id, 0)
            return (count, task.priority.value, task.metadata.created_at)

        result = sorted(tasks, key=fair_sort_key)

        # Update counts
        for task in result:
            session_id = task.metadata.session_id
            self._session_counts[session_id] = self._session_counts.get(session_id, 0) + 1

        return result


# =============================================================================
# Strategy Factory
# =============================================================================


class StrategyFactory:
    """Factory for creating scheduling strategies."""

    STRATEGIES: dict[str, type[SchedulingStrategy]] = {
        "FIFO": FIFOStrategy,
        "Priority": PriorityStrategy,
        "DeadlineFirst": DeadlineFirstStrategy,
        "CriticalFirst": CriticalFirstStrategy,
        "FairScheduling": FairSchedulingStrategy,
    }

    @classmethod
    def create(cls, name: str) -> SchedulingStrategy:
        """Create a strategy by name.

        Args:
            name: Strategy name.

        Returns:
            Strategy instance.
        """
        strategy_class = cls.STRATEGIES.get(name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {name}")
        return strategy_class()

    @classmethod
    def list_strategies(cls) -> list[str]:
        """List available strategies.

        Returns:
            List of strategy names.
        """
        return list(cls.STRATEGIES.keys())
