"""Lifecycle policies for the Cognitive Lifecycle Manager."""


class LifecyclePolicy:
    """Policies for lifecycle management."""

    def __init__(
        self,
        auto_recovery: bool = True,
        max_recovery_attempts: int = 3,
        timeout_ms: int = 300000,
        auto_archive: bool = True,
        archive_delay_ms: int = 3600000,
        cleanup_enabled: bool = True,
        retention_days: int = 90,
    ):
        self.auto_recovery = auto_recovery
        self.max_recovery_attempts = max_recovery_attempts
        self.timeout_ms = timeout_ms
        self.auto_archive = auto_archive
        self.archive_delay_ms = archive_delay_ms
        self.cleanup_enabled = cleanup_enabled
        self.retention_days = retention_days


class LifecyclePolicyPresets:
    """Presets for lifecycle policies."""

    @staticmethod
    def default():
        return LifecyclePolicy()

    @staticmethod
    def strict():
        return LifecyclePolicy(
            auto_recovery=True,
            max_recovery_attempts=2,
            timeout_ms=180000,
            auto_archive=True,
            retention_days=30,
        )

    @staticmethod
    def permissive():
        return LifecyclePolicy(
            auto_recovery=True,
            max_recovery_attempts=5,
            timeout_ms=600000,
            auto_archive=False,
            retention_days=365,
        )
