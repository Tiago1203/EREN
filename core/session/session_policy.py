"""Session policies for the Cognitive Session Manager.

Provides policy definitions for session management.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeoutPolicy:
    """Policy for session timeouts."""

    session_timeout_ms: int = 300000  # 5 minutes
    idle_timeout_ms: int = 60000  # 1 minute
    active_timeout_ms: int = 600000  # 10 minutes
    pause_timeout_ms: int = 300000  # 5 minutes


@dataclass(frozen=True)
class ExpirationPolicy:
    """Policy for session expiration."""

    max_session_duration_ms: int = 3600000  # 1 hour
    max_idle_duration_ms: int = 1800000  # 30 minutes
    force_expire_after_ms: int = 86400000  # 24 hours


@dataclass(frozen=True)
class RecoveryPolicy:
    """Policy for session recovery."""

    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_timeout_ms: int = 60000  # 1 minute
    recovery_strategy: str = "retry"  # retry, reset, escalate


@dataclass(frozen=True)
class ArchivalPolicy:
    """Policy for session archival."""

    auto_archive: bool = True
    archive_after_completion_ms: int = 3600000  # 1 hour
    archive_completed_sessions: bool = True
    archive_failed_sessions: bool = True


@dataclass(frozen=True)
class CleanupPolicy:
    """Policy for session cleanup."""

    auto_cleanup: bool = True
    cleanup_interval_ms: int = 300000  # 5 minutes
    cleanup_expired_sessions: bool = True
    cleanup_archived_sessions: bool = True
    max_archived_sessions: int = 10000
    cleanup_threshold_hours: int = 24


@dataclass(frozen=True)
class RetentionPolicy:
    """Policy for session retention."""

    retention_days: int = 90
    retention_audit_days: int = 365
    enable_compliance_retention: bool = False
    compliance_retention_days: int = 2555  # 7 years for medical


@dataclass(frozen=True)
class SessionPolicies:
    """Complete session policies.

    Bundles all policy configurations for session management.
    """

    # Timeout
    session_timeout_ms: int = 300000
    idle_timeout_ms: int = 60000
    active_timeout_ms: int = 600000
    pause_timeout_ms: int = 300000

    # Expiration
    max_session_duration_ms: int = 3600000
    max_idle_duration_ms: int = 1800000
    force_expire_after_ms: int = 86400000

    # Recovery
    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    recovery_timeout_ms: int = 60000
    recovery_strategy: str = "retry"

    # Archival
    auto_archive: bool = True
    archive_after_completion_ms: int = 3600000
    archive_completed_sessions: bool = True
    archive_failed_sessions: bool = True

    # Cleanup
    auto_cleanup: bool = True
    cleanup_interval_ms: int = 300000
    cleanup_expired_sessions: bool = True
    cleanup_archived_sessions: bool = True
    max_archived_sessions: int = 10000
    cleanup_threshold_hours: int = 24

    # Retention
    retention_days: int = 90
    retention_audit_days: int = 365
    enable_compliance_retention: bool = False
    compliance_retention_days: int = 2555

    # Limits
    max_sessions_per_user: int = 10
    max_sessions_per_hospital: int = 1000
    max_sessions_per_tenant: int = 10000

    def get_timeout_policy(self) -> TimeoutPolicy:
        """Get timeout policy."""
        return TimeoutPolicy(
            session_timeout_ms=self.session_timeout_ms,
            idle_timeout_ms=self.idle_timeout_ms,
            active_timeout_ms=self.active_timeout_ms,
            pause_timeout_ms=self.pause_timeout_ms,
        )

    def get_expiration_policy(self) -> ExpirationPolicy:
        """Get expiration policy."""
        return ExpirationPolicy(
            max_session_duration_ms=self.max_session_duration_ms,
            max_idle_duration_ms=self.max_idle_duration_ms,
            force_expire_after_ms=self.force_expire_after_ms,
        )

    def get_recovery_policy(self) -> RecoveryPolicy:
        """Get recovery policy."""
        return RecoveryPolicy(
            enable_auto_recovery=self.enable_auto_recovery,
            max_recovery_attempts=self.max_recovery_attempts,
            recovery_timeout_ms=self.recovery_timeout_ms,
            recovery_strategy=self.recovery_strategy,
        )

    def get_archival_policy(self) -> ArchivalPolicy:
        """Get archival policy."""
        return ArchivalPolicy(
            auto_archive=self.auto_archive,
            archive_after_completion_ms=self.archive_after_completion_ms,
            archive_completed_sessions=self.archive_completed_sessions,
            archive_failed_sessions=self.archive_failed_sessions,
        )

    def get_cleanup_policy(self) -> CleanupPolicy:
        """Get cleanup policy."""
        return CleanupPolicy(
            auto_cleanup=self.auto_cleanup,
            cleanup_interval_ms=self.cleanup_interval_ms,
            cleanup_expired_sessions=self.cleanup_expired_sessions,
            cleanup_archived_sessions=self.cleanup_archived_sessions,
            max_archived_sessions=self.max_archived_sessions,
            cleanup_threshold_hours=self.cleanup_threshold_hours,
        )

    def get_retention_policy(self) -> RetentionPolicy:
        """Get retention policy."""
        return RetentionPolicy(
            retention_days=self.retention_days,
            retention_audit_days=self.retention_audit_days,
            enable_compliance_retention=self.enable_compliance_retention,
            compliance_retention_days=self.compliance_retention_days,
        )


class PolicyPresets:
    """Presets for common policy configurations."""

    @staticmethod
    def default() -> SessionPolicies:
        """Get default policies."""
        return SessionPolicies()

    @staticmethod
    def strict() -> SessionPolicies:
        """Get strict policies for production."""
        return SessionPolicies(
            session_timeout_ms=180000,  # 3 minutes
            idle_timeout_ms=30000,  # 30 seconds
            max_recovery_attempts=2,
            retention_days=30,
        )

    @staticmethod
    def permissive() -> SessionPolicies:
        """Get permissive policies for development."""
        return SessionPolicies(
            session_timeout_ms=600000,  # 10 minutes
            idle_timeout_ms=300000,  # 5 minutes
            max_recovery_attempts=5,
            retention_days=365,
        )

    @staticmethod
    def compliance() -> SessionPolicies:
        """Get policies for compliance environments."""
        return SessionPolicies(
            session_timeout_ms=180000,
            idle_timeout_ms=60000,
            enable_compliance_retention=True,
            compliance_retention_days=2555,  # 7 years
            retention_audit_days=2555,
            auto_archive=True,
        )
