"""Policies for the Cognitive Orchestrator.

Defines orchestration policies.

Architecture only -- no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Timeout Policies
# =============================================================================


@dataclass(frozen=True)
class TimeoutPolicy:
    """Policy for timeouts."""

    session_timeout_ms: int = 300000  # 5 minutes
    phase_timeout_ms: int = 60000  # 1 minute
    event_timeout_ms: int = 30000  # 30 seconds
    motor_timeout_ms: int = 120000  # 2 minutes


# =============================================================================
# Retry Policies
# =============================================================================


@dataclass(frozen=True)
class RetryPolicy:
    """Policy for retries."""

    max_retries: int = 3
    retry_delay_ms: int = 1000
    exponential_backoff: bool = False
    max_retry_delay_ms: int = 10000


# =============================================================================
# Cancellation Policies
# =============================================================================


@dataclass(frozen=True)
class CancellationPolicy:
    """Policy for session cancellation."""

    allow_user_cancellation: bool = True
    allow_system_cancellation: bool = True
    cancellation_delay_ms: int = 0
    graceful_shutdown_timeout_ms: int = 5000


# =============================================================================
# Recovery Policies
# =============================================================================


@dataclass(frozen=True)
class RecoveryPolicy:
    """Policy for error recovery."""

    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_strategy: str = "retry"  # retry, fallback, escalate
    fallback_motor: str = ""


# =============================================================================
# Iteration Policies
# =============================================================================


@dataclass(frozen=True)
class IterationPolicy:
    """Policy for iteration limits."""

    max_iterations: int = 10
    max_reasoning_iterations: int = 5
    max_evidence_iterations: int = 3
    max_context_updates: int = 100


# =============================================================================
# Orchestration Policies
# =============================================================================


@dataclass(frozen=True)
class OrchestrationPolicies:
    """Complete orchestration policies.

    Bundles all policy configurations for the orchestrator.
    """

    # Timeout policies
    session_timeout_ms: int = 300000
    phase_timeout_ms: int = 60000
    event_timeout_ms: int = 30000
    motor_timeout_ms: int = 120000

    # Retry policies
    max_retries: int = 3
    retry_delay_ms: int = 1000
    exponential_backoff: bool = False

    # Cancellation policies
    allow_user_cancellation: bool = True
    allow_system_cancellation: bool = True
    graceful_shutdown_timeout_ms: int = 5000

    # Recovery policies
    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_strategy: str = "retry"

    # Iteration policies
    max_iterations: int = 10
    max_reasoning_iterations: int = 5
    max_evidence_iterations: int = 3
    max_context_updates: int = 100

    # Feature flags
    enable_parallel_execution: bool = False
    enable_context_caching: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = True

    def get_timeout_policy(self) -> TimeoutPolicy:
        """Get timeout policy.

        Returns:
            Timeout policy.
        """
        return TimeoutPolicy(
            session_timeout_ms=self.session_timeout_ms,
            phase_timeout_ms=self.phase_timeout_ms,
            event_timeout_ms=self.event_timeout_ms,
            motor_timeout_ms=self.motor_timeout_ms,
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
        )

    def get_cancellation_policy(self) -> CancellationPolicy:
        """Get cancellation policy.

        Returns:
            Cancellation policy.
        """
        return CancellationPolicy(
            allow_user_cancellation=self.allow_user_cancellation,
            allow_system_cancellation=self.allow_system_cancellation,
            graceful_shutdown_timeout_ms=self.graceful_shutdown_timeout_ms,
        )

    def get_recovery_policy(self) -> RecoveryPolicy:
        """Get recovery policy.

        Returns:
            Recovery policy.
        """
        return RecoveryPolicy(
            enable_auto_recovery=self.enable_auto_recovery,
            max_recovery_attempts=self.max_recovery_attempts,
            recovery_strategy=self.recovery_strategy,
        )

    def get_iteration_policy(self) -> IterationPolicy:
        """Get iteration policy.

        Returns:
            Iteration policy.
        """
        return IterationPolicy(
            max_iterations=self.max_iterations,
            max_reasoning_iterations=self.max_reasoning_iterations,
            max_evidence_iterations=self.max_evidence_iterations,
            max_context_updates=self.max_context_updates,
        )


# =============================================================================
# Policy Presets
# =============================================================================


class PolicyPresets:
    """Presets for common policy configurations."""

    @staticmethod
    def strict() -> OrchestrationPolicies:
        """Get strict policies for production.

        Returns:
            Strict policies.
        """
        return OrchestrationPolicies(
            session_timeout_ms=180000,  # 3 minutes
            phase_timeout_ms=30000,  # 30 seconds
            max_retries=2,
            max_iterations=5,
            enable_auto_recovery=True,
        )

    @staticmethod
    def permissive() -> OrchestrationPolicies:
        """Get permissive policies for development.

        Returns:
            Permissive policies.
        """
        return OrchestrationPolicies(
            session_timeout_ms=600000,  # 10 minutes
            phase_timeout_ms=120000,  # 2 minutes
            max_retries=5,
            max_iterations=20,
            enable_auto_recovery=True,
        )

    @staticmethod
    def critical() -> OrchestrationPolicies:
        """Get policies for critical environments.

        Returns:
            Critical policies.
        """
        return OrchestrationPolicies(
            session_timeout_ms=120000,  # 2 minutes
            phase_timeout_ms=15000,  # 15 seconds
            max_retries=1,
            max_iterations=3,
            enable_auto_recovery=False,
        )
