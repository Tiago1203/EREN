"""Event bus abstractions for EREN.

Defines the publish/subscribe **contracts** (`EventPublisher`,
`EventSubscriber`) and the `EventBus` skeleton that mediates between them.

Architecture only. The `EventBus` methods intentionally raise
`NotImplementedError`: this module fixes the *shape* of the eventing mechanism,
not its behavior. No threading, queues, brokers, or delivery guarantees are
implemented here.

Decoupling rationale:

- Producers depend on `EventPublisher`, not on any subscriber.
- Consumers implement `EventSubscriber`; they never reference producers.
- The `EventBus` depends only on these abstractions (Dependency Inversion), so
  it can later be backed by an in-process dispatcher, a queue, or a broker
  without changing producers or consumers.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from core.events.models import Event, EventType

EventHandler = Callable[[Event], None]
"""A callable that reacts to a single event."""


@runtime_checkable
class EventPublisher(Protocol):
    """Something that can emit events onto the bus."""

    def publish(self, event: Event) -> None:
        """Emit ``event`` to all interested subscribers."""
        ...


@runtime_checkable
class EventSubscriber(Protocol):
    """Something that reacts to events it is subscribed to."""

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Event types this subscriber is interested in."""
        ...

    def handle(self, event: Event) -> None:
        """React to a delivered ``event``."""
        ...


class EventBus:
    """Central mediator decoupling event producers from consumers.

    Concrete behavior (registration storage, dispatch strategy, delivery
    guarantees) is added later. This skeleton fixes the interface only and
    implements no logic.
    """

    def subscribe(self, event_type: EventType, subscriber: EventSubscriber) -> None:
        """Register ``subscriber`` to receive events of ``event_type``."""
        raise NotImplementedError

    def unsubscribe(self, event_type: EventType, subscriber: EventSubscriber) -> None:
        """Remove ``subscriber`` from ``event_type``."""
        raise NotImplementedError

    def publish(self, event: Event) -> None:
        """Deliver ``event`` to every subscriber registered for its type."""
        raise NotImplementedError
