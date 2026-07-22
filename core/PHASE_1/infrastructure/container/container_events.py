"""Container Events for the Cognitive Dependency Injection Container.

Defines all container events.

Architecture only -- no implementations.
"""


class ContainerEventType:
    """Types of container events."""

    CONTAINER_CREATED = "ContainerCreated"
    CONTAINER_DISPOSED = "ContainerDisposed"
    SERVICE_REGISTERED = "ServiceRegistered"
    SERVICE_RESOLVED = "ServiceResolved"
    SERVICE_CREATED = "ServiceCreated"
    SCOPE_CREATED = "ScopeCreated"
    SCOPE_DISPOSED = "ScopeDisposed"
    DEPENDENCY_VALIDATED = "DependencyValidated"
    DEPENDENCY_VALIDATION_FAILED = "DependencyValidationFailed"
    CIRCULAR_DEPENDENCY_DETECTED = "CircularDependencyDetected"
    SERVICE_NOT_FOUND = "ServiceNotFound"
    RESOLUTION_FAILED = "ResolutionFailed"


class ContainerEventPublisher:
    """Publishes container events."""

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
