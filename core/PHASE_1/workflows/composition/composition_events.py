"""Composition Events for the Cognitive Composition Root.

Defines all composition events.

Architecture only -- no implementations.
"""


class CompositionEventType:
    """Types of composition events."""

    COMPOSITION_STARTED = "CompositionStarted"
    MODULE_REGISTERED = "ModuleRegistered"
    MODULE_LOADED = "ModuleLoaded"
    MODULE_INITIALIZED = "ModuleInitialized"
    MODULE_VALIDATED = "ModuleValidated"
    MODULE_VALIDATION_FAILED = "ModuleValidationFailed"
    COMPOSITION_VALIDATED = "CompositionValidated"
    COMPOSITION_VALIDATION_FAILED = "CompositionValidationFailed"
    COMPOSITION_COMPLETED = "CompositionCompleted"
    COMPOSITION_FAILED = "CompositionFailed"
    CONTAINER_BUILT = "ContainerBuilt"
    RUNTIME_READY = "RuntimeReady"
    CONTRACT_REGISTERED = "ContractRegistered"


class CompositionEventPublisher:
    """Publishes composition events."""

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
