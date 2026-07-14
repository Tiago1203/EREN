"""Scheduling policies.

Defines policies for the cognitive scheduler.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Timeout Policy
# =============================================================================


@dataclass(frozen=True)
class TimeoutPolicy:
    """Policy for task timeouts."""

    task_timeout_ms: int = 30000  # 30 seconds
    session_timeout_ms: int = 300000  # 5 minutes
    global_timeout_ms: int = 600000  # 10 minutes
    enable_timeout: bool = True


# =============================================================================
# Retry Policy
# =============================================================================


@dataclass(frozen=True)
class RetryPolicy:
    """Policy for task retries."""

    max_retries: int = 3
    retry_delay_ms: int = 1000
    exponential_backoff: bool = False
    max_retry_delay_ms: int = 30000
    retry_on_failure: bool = True
    retry_on_timeout: bool = True


# =============================================================================
# Queue Policy
# =============================================================================


@dataclass(frozen=True)
class QueuePolicy:
    """Policy for queue management."""

    max_queue_size: int = 1000
    max_tasks_per_session: int = 100
    queue_timeout_ms: int = 60000  # 1 minute
    enable_priority_inheritance: bool = True
    enable_deadline_extension: bool = False


# =============================================================================
# Capacity Policy
# =============================================================================


@dataclass(frozen=True)
class CapacityPolicy:
    """Policy for capacity management."""

    max_concurrent_tasks: int = 10
    max_tasks_per_capability: int = 5
    enable_capacity_reservation: bool = True
    capacity_release_delay_ms: int = 1000


# =============================================================================
# Scheduling Policy
# =============================================================================


@dataclass(frozen=True)
class SchedulingPolicy:
    """Complete scheduling policy.

    Bundles all policy configurations for the scheduler.
    """

    # Strategy
    strategy: str = "Priority"  # FIFO, Priority, DeadlineFirst, CriticalFirst, FairScheduling

    # Timeout
    task_timeout_ms: int = 30000
    session_timeout_ms: int = 300000
    global_timeout_ms: int = 600000
    enable_timeout: bool = True

    # Retry
    max_retries: int = 3
    retry_delay_ms: int = 1000
    exponential_backoff: bool = False
    retry_on_failure: bool = True
    retry_on_timeout: bool = True

    # Queue
    max_queue_size: int = 1000
    max_tasks_per_session: int = 100
    queue_timeout_ms: int = 60000
    enable_priority_inheritance: bool = True

    # Capacity
    max_concurrent_tasks: int = 10
    max_tasks_per_capability: int = 5
    enable_capacity_reservation: bool = True

    # Feature flags
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_adaptive_scheduling: bool = False

    def get_timeout_policy(self) -> TimeoutPolicy:
        """Get timeout policy.

        Returns:
            Timeout policy.
        """
        return TimeoutPolicy(
            task_timeout_ms=self.task_timeout_ms,
            session_timeout_ms=self.session_timeout_ms,
            global_timeout_ms=self.global_timeout_ms,
            enable_timeout=self.enable_timeout,
        )

    def get_retry_policy(self) -> RetryPolicy:
        """Get retry policy.

        Returns:
            Retry policy.
        """
        return RetryPolicy(
            max_retries=self.max_retries,
            retry_delay_ms=self.retry_delay_ms,
            exponential_backoff=self.exponential_backoff,
            retry_on_failure=self.retry_on_failure,
            retry_on_timeout=self.retry_on_timeout,
        )

    def get_queue_policy(self) -> QueuePolicy:
        """Get queue policy.

        Returns:
            Queue policy.
        """
        return QueuePolicy(
            max_queue_size=self.max_queue_size,
            max_tasks_per_session=self.max_tasks_per_session,
            queue_timeout_ms=self.queue_timeout_ms,
            enable_priority_inheritance=self.enable_priority_inheritance,
        )

    def get_capacity_policy(self) -> CapacityPolicy:
        """Get capacity policy.

        Returns:
            Capacity policy.
        """
        return CapacityPolicy(
            max_concurrent_tasks=self.max_concurrent_tasks,
            max_tasks_per_capability=self.max_tasks_per_capability,
            enable_capacity_reservation=self.enable_capacity_reservation,
        )


# =============================================================================
# Policy Presets
# =============================================================================


class PolicyPresets:
    """Presets for common policy configurations."""

    @staticmethod
    def low_latency() -> SchedulingPolicy:
        """Get low latency policies.

        Returns:
            Low latency policies.
        """
        return SchedulingPolicy(
            strategy="Priority",
            task_timeout_ms=10000,
            max_retries=2,
            max_concurrent_tasks=20,
            enable_adaptive_scheduling=True,
        )

    @staticmethod
    def high_throughput() -> SchedulingPolicy:
        """Get high throughput policies.

        Returns:
            High throughput policies.
        """
        return SchedulingPolicy(
            strategy="FairScheduling",
            task_timeout_ms=60000,
            max_retries=3,
            max_concurrent_tasks=50,
            enable_adaptive_scheduling=True,
        )

    @staticmethod
    def critical() -> SchedulingPolicy:
        """Get critical environment policies.

        Returns:
            Critical policies.
        """
        return SchedulingPolicy(
            strategy="CriticalFirst",
            task_timeout_ms=5000,
            max_retries=1,
            max_concurrent_tasks=5,
            enable_adaptive_scheduling=False,
        )
