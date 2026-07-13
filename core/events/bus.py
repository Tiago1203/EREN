"""Event bus implementations for EREN.

Provides the publish/subscribe **contracts** (`EventPublisher`, `EventSubscriber`)
and the `EventBus` implementation that mediates between them.

Architecture:
- Producers depend on `EventPublisher`, not on any subscriber.
- Consumers implement `EventSubscriber`; they never reference producers.
- The `EventBus` depends only on these abstractions (Dependency Inversion), so
  it can be backed by an in-process dispatcher, a queue, or a broker.

This module provides a functional in-process EventBus implementation suitable for
single-process deployments. For distributed scenarios, wrap with a broker adapter.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.events.models import Event, EventType

EventHandler = Callable[["Event"], None]
"""A callable that reacts to a single event."""

AsyncEventHandler = Callable[["Event"], Any]
"""An async callable that reacts to a single event."""


class EventPublisher:
    """Protocol for components that can emit events onto the bus.

    Any class that wants to publish events should accept this interface
    (or the concrete EventBus) via dependency injection.
    """

    def publish(self, event: "Event") -> None:
        """Emit ``event`` to all interested subscribers.

        Args:
            event: The event to publish.

        Raises:
            PublishError: If publishing fails.
        """
        ...


class EventSubscriber:
    """Protocol for components that react to events.

    Subscribers declare which event types they care about via
    ``subscribed_types`` and implement ``handle`` to react.
    """

    @property
    def subscribed_types(self) -> tuple["EventType", ...]:
        """Event types this subscriber is interested in."""
        return ()

    def handle(self, event: "Event") -> None:
        """React to a delivered ``event``.

        Args:
            event: The event to handle.

        Raises:
            Exception: Any exception will be logged but not propagated
                to prevent one subscriber from breaking others.
        """
        ...


class EventBus:
    """Central mediator decoupling event producers from consumers.

    This is a thread-safe, in-process implementation suitable for single-process
    deployments. For distributed scenarios, wrap with a broker adapter.

    Features:
    - Thread-safe subscription management
    - Synchronous and async event dispatch
    - Wildcard subscriptions (subscribe to all events)
    - Event filtering
    - Subscriber priority
    - Error isolation between subscribers

    Example::

        bus = EventBus()

        # Subscribe
        bus.subscribe(EventType.PLAN_CREATED, my_handler)

        # Publish
        bus.publish(PlanCreated(
            source="planner",
            correlation_id="req-123",
            payload={"step_count": 5}
        ))
    """

    def __init__(
        self,
        max_workers: int | None = None,
        async_mode: bool = False,
    ) -> None:
        """Initialize the EventBus.

        Args:
            max_workers: Maximum number of worker threads for async dispatch.
                        Defaults to min(32, cpu_count + 4).
            async_mode: If True, use async event dispatch.
        """
        self._subscriptions: dict["EventType", list[tuple[int, EventSubscriber]]] = (
            defaultdict(list)
        )
        self._wildcard_subscribers: list[tuple[int, EventSubscriber]] = []
        self._lock = threading.RLock()
        self._async_mode = async_mode
        self._executor: ThreadPoolExecutor | None = None

        if max_workers is not None:
            self._executor = ThreadPoolExecutor(max_workers=max_workers)

    # --------------------------------------------------------------------------
    # Subscription management
    # --------------------------------------------------------------------------

    def subscribe(
        self,
        event_type: "EventType",
        subscriber: EventSubscriber,
        priority: int = 0,
    ) -> None:
        """Register ``subscriber`` to receive events of ``event_type``.

        Args:
            event_type: The type of event to subscribe to.
            subscriber: The subscriber that will handle events.
            priority: Higher priority subscribers receive events first.
                      Default is 0. Use negative for low priority.
        """
        with self._lock:
            # Check if already subscribed
            for existing_priority, existing_sub in self._subscriptions[event_type]:
                if existing_sub is subscriber:
                    return  # Already subscribed

            self._subscriptions[event_type].append((priority, subscriber))
            # Sort by priority (highest first)
            self._subscriptions[event_type].sort(key=lambda x: -x[0])

    def subscribe_wildcard(
        self,
        subscriber: EventSubscriber,
        priority: int = 0,
    ) -> None:
        """Register ``subscriber`` to receive ALL events.

        Args:
            subscriber: The subscriber that will handle events.
            priority: Higher priority subscribers receive events first.
        """
        with self._lock:
            self._wildcard_subscribers.append((priority, subscriber))
            self._wildcard_subscribers.sort(key=lambda x: -x[0])

    def unsubscribe(
        self,
        event_type: "EventType",
        subscriber: EventSubscriber,
    ) -> bool:
        """Remove ``subscriber`` from ``event_type``.

        Args:
            event_type: The event type to unsubscribe from.
            subscriber: The subscriber to remove.

        Returns:
            True if the subscriber was found and removed, False otherwise.
        """
        with self._lock:
            if event_type not in self._subscriptions:
                return False

            original_length = len(self._subscriptions[event_type])
            self._subscriptions[event_type] = [
                (p, s) for p, s in self._subscriptions[event_type]
                if s is not subscriber
            ]
            return len(self._subscriptions[event_type]) < original_length

    def unsubscribe_wildcard(self, subscriber: EventSubscriber) -> bool:
        """Remove ``subscriber`` from wildcard subscriptions.

        Args:
            subscriber: The subscriber to remove.

        Returns:
            True if the subscriber was found and removed, False otherwise.
        """
        with self._lock:
            original_length = len(self._wildcard_subscribers)
            self._wildcard_subscribers = [
                (p, s) for p, s in self._wildcard_subscribers
                if s is not subscriber
            ]
            return len(self._wildcard_subscribers) < original_length

    def unsubscribe_all(self, subscriber: EventSubscriber) -> int:
        """Remove ``subscriber`` from all event types.

        Args:
            subscriber: The subscriber to remove.

        Returns:
            The number of subscriptions removed.
        """
        count = 0
        with self._lock:
            # Remove from specific subscriptions
            for event_type in list(self._subscriptions.keys()):
                if self.unsubscribe(event_type, subscriber):
                    count += 1

            # Remove from wildcard subscriptions
            if self.unsubscribe_wildcard(subscriber):
                count += 1

        return count

    # --------------------------------------------------------------------------
    # Event publishing
    # --------------------------------------------------------------------------

    def publish(self, event: "Event") -> None:
        """Deliver ``event`` to every subscriber registered for its type.

        This is a synchronous operation: all subscribers are called in the
        calling thread. For async dispatch, use ``publish_async``.

        Args:
            event: The event to publish.

        Note:
            If a subscriber raises an exception, it's logged but doesn't
            prevent other subscribers from receiving the event.
        """
        self._dispatch(event, sync=True)

    def publish_async(self, event: "Event") -> None:
        """Deliver ``event`` asynchronously to subscribers.

        Uses a thread pool to dispatch events without blocking the caller.

        Args:
            event: The event to publish.
        """
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=4)

        self._executor.submit(self._dispatch, event, sync=True)

    def _dispatch(self, event: "Event", *, sync: bool = True) -> None:
        """Internal dispatch method.

        Args:
            event: The event to dispatch.
            sync: Whether to call subscribers synchronously.
        """
        # Collect all subscribers to notify
        with self._lock:
            subscribers_to_notify: list[EventSubscriber] = []

            # Get subscribers for this specific event type
            if event.type in self._subscriptions:
                subscribers_to_notify.extend(
                    sub for _, sub in self._subscriptions[event.type]
                )

            # Get wildcard subscribers
            subscribers_to_notify.extend(
                sub for _, sub in self._wildcard_subscribers
            )

        # Call subscribers (outside lock to prevent deadlocks)
        for subscriber in subscribers_to_notify:
            try:
                subscriber.handle(event)
            except Exception:
                # Log but don't propagate exceptions
                import logging
                logging.exception(
                    "Error in event subscriber %s handling %s",
                    subscriber,
                    event.type,
                )

    # --------------------------------------------------------------------------
    # Query methods
    # --------------------------------------------------------------------------

    def get_subscriber_count(self, event_type: "EventType | None" = None) -> int:
        """Get the number of subscribers.

        Args:
            event_type: If provided, count subscribers for this type only.
                       If None, count all subscribers including wildcards.

        Returns:
            Number of subscribers.
        """
        with self._lock:
            if event_type is None:
                count = len(self._wildcard_subscribers)
                for subs in self._subscriptions.values():
                    count += len(subs)
                return count

            if event_type in self._subscriptions:
                return len(self._subscriptions[event_type])
            return 0

    def get_subscribed_types(self) -> set["EventType"]:
        """Get all event types with active subscriptions.

        Returns:
            Set of event types with at least one subscriber.
        """
        with self._lock:
            return set(self._subscriptions.keys())

    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------

    def close(self) -> None:
        """Clean up resources used by the EventBus.

        Call this when shutting down the application.
        """
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None

    def __enter__(self) -> "EventBus":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


# =============================================================================
# Global event bus singleton
# =============================================================================


_global_bus: EventBus | None = None
_global_bus_lock = threading.Lock()


def get_global_bus() -> EventBus:
    """Get the global EventBus singleton.

    Returns:
        The global EventBus instance.
    """
    global _global_bus
    with _global_bus_lock:
        if _global_bus is None:
            _global_bus = EventBus()
        return _global_bus


def set_global_bus(bus: EventBus) -> None:
    """Set the global EventBus singleton.

    Args:
        bus: The EventBus instance to use as the global bus.
    """
    global _global_bus
    with _global_bus_lock:
        _global_bus = bus


def reset_global_bus() -> None:
    """Reset the global EventBus singleton.

    Useful for testing.
    """
    global _global_bus
    with _global_bus_lock:
        if _global_bus is not None:
            _global_bus.close()
        _global_bus = None
