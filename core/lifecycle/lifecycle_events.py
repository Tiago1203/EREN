"""Lifecycle events for the Cognitive Lifecycle Manager."""


class LifecycleEventType:
    """Lifecycle event types."""

    LIFECYCLE_STARTED = "LifecycleStarted"
    LIFECYCLE_INITIALIZED = "LifecycleInitialized"
    LIFECYCLE_READY = "LifecycleReady"
    LIFECYCLE_ACTIVATED = "LifecycleActivated"
    LIFECYCLE_PAUSED = "LifecyclePaused"
    LIFECYCLE_RESUMED = "LifecycleResumed"
    LIFECYCLE_RECOVERED = "LifecycleRecovered"
    LIFECYCLE_COMPLETED = "LifecycleCompleted"
    LIFECYCLE_CANCELLED = "LifecycleCancelled"
    LIFECYCLE_ARCHIVED = "LifecycleArchived"
    LIFECYCLE_FAILED = "LifecycleFailed"
    INVALID_TRANSITION_DETECTED = "InvalidTransitionDetected"


class LifecycleEventPublisher:
    """Publishes lifecycle events."""

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
