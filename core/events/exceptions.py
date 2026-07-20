"""Exceptions for EREN's event system.

Provides typed exception hierarchy for the event system, making it easy
to handle specific error conditions in calling code.
"""

from __future__ import annotations


class EventError(Exception):
    """Base class for all event-system errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class PublishError(EventError):
    """Raised when an event cannot be published.

    This includes:
    - Bus not available
    - Serialization failures
    - Circuit breaker open
    - Broker connection failures
    """

    def __init__(self, message: str = "", event_type: str | None = None) -> None:
        super().__init__(message)
        self.event_type = event_type


class SubscriptionError(EventError):
    """Raised when a subscription/unsubscription cannot be completed.

    This includes:
    - Invalid subscriber
    - Subscriber already subscribed
    - Subscription not found (on unsubscribe)
    """

    def __init__(self, message: str = "", event_type: str | None = None) -> None:
        super().__init__(message)
        self.event_type = event_type


class EventValidationError(EventError):
    """Raised when an event fails validation.

    This includes:
    - Invalid event type
    - Missing required payload fields
    - Payload type mismatch
    """

    def __init__(self, message: str = "", event_id: str | None = None) -> None:
        super().__init__(message)
        self.event_id = event_id


class EventBusClosedError(EventError):
    """Raised when operations are attempted on a closed EventBus."""


class CircuitBreakerOpenError(EventError):
    """Raised when publishing is blocked due to circuit breaker."""

    def __init__(self, message: str = "", reset_timeout: float | None = None) -> None:
        super().__init__(message)
        self.reset_timeout = reset_timeout


class SubscriberError(EventError):
    """Raised when a subscriber's handler fails.

    This exception wraps the original error and includes
    information about which subscriber and event caused it.
    """

    def __init__(
        self,
        message: str = "",
        subscriber: str | None = None,
        event_type: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.subscriber = subscriber
        self.event_type = event_type
        self.original_error = original_error
