"""Boot events for the Cognitive Boot Manager.

Defines all boot events.

Architecture only -- no implementations.
"""


class BootEventType:
    """Types of boot events."""

    BOOT_STARTED = "BootStarted"
    BOOT_STEP_STARTED = "BootStepStarted"
    BOOT_STEP_COMPLETED = "BootStepCompleted"
    BOOT_STEP_FAILED = "BootStepFailed"
    BOOT_STEP_SKIPPED = "BootStepSkipped"
    BOOT_COMPLETED = "BootCompleted"
    BOOT_FAILED = "BootFailed"
    BOOT_ROLLBACK_STARTED = "BootRollbackStarted"
    BOOT_ROLLBACK_COMPLETED = "BootRollbackCompleted"
    BOOT_ROLLBACK_FAILED = "BootRollbackFailed"
    CONFIGURATION_LOADED = "ConfigurationLoaded"
    CONTRACT_VALIDATED = "ContractValidated"
    HEALTH_CHECK_PASSED = "HealthCheckPassed"
    HEALTH_CHECK_FAILED = "HealthCheckFailed"


class BootEventPublisher:
    """Publishes boot events."""

    def __init__(self):
        self._enabled = True
        self._events_published = 0

    def publish(self, event_type: str, **data):
        """Publish an event."""
        if self._enabled:
            self._events_published += 1

    def disable(self):
        self._enabled = False

    def enable(self):
        self._enabled = True

    @property
    def events_published(self) -> int:
        return self._events_published
