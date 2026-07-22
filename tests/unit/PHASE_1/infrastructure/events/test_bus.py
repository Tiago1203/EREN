"""Tests for the EventBus."""

from __future__ import annotations

import pytest

from core.PHASE_1.infrastructure.events.bus import (
    EventBus,
    EventSubscriber,
)
from core.PHASE_1.infrastructure.events.models import (
    Event,
    EventType,
    PlanCreated,
    KnowledgeRetrieved,
    ReasoningStarted,
)


class TestEventBus:
    """Tests for the EventBus class."""

    def test_subscribe_and_publish(self) -> None:
        """Subscribed subscriber should receive events."""
        bus = EventBus()
        received: list[Event] = []

        class TestSubscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received.append(event)

        subscriber = TestSubscriber()
        bus.subscribe(EventType.PLAN_CREATED, subscriber)

        event = PlanCreated(source="planner", payload={"step_count": 5})
        bus.publish(event)

        assert len(received) == 1
        assert received[0].type == EventType.PLAN_CREATED
        bus.close()

    def test_unsubscribe(self) -> None:
        """Unsubscribed subscriber should not receive events."""
        bus = EventBus()
        received: list[Event] = []

        class TestSubscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received.append(event)

        subscriber = TestSubscriber()
        bus.subscribe(EventType.PLAN_CREATED, subscriber)
        bus.unsubscribe(EventType.PLAN_CREATED, subscriber)

        event = PlanCreated(source="planner")
        bus.publish(event)

        assert len(received) == 0
        bus.close()

    def test_multiple_subscribers(self) -> None:
        """Multiple subscribers should all receive events."""
        bus = EventBus()
        received1: list[Event] = []
        received2: list[Event] = []

        class Subscriber1:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received1.append(event)

        class Subscriber2:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received2.append(event)

        bus.subscribe(EventType.PLAN_CREATED, Subscriber1())
        bus.subscribe(EventType.PLAN_CREATED, Subscriber2())

        event = PlanCreated(source="planner")
        bus.publish(event)

        assert len(received1) == 1
        assert len(received2) == 1
        bus.close()

    def test_wildcard_subscriber(self) -> None:
        """Wildcard subscribers should receive all events."""
        bus = EventBus()
        received: list[Event] = []

        class WildcardSubscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return ()  # Empty means wildcard

            def handle(self, event: Event) -> None:
                received.append(event)

        subscriber = WildcardSubscriber()
        bus.subscribe_wildcard(subscriber)

        bus.publish(PlanCreated(source="planner"))
        bus.publish(KnowledgeRetrieved(source="knowledge"))
        bus.publish(ReasoningStarted(source="reasoning"))

        assert len(received) == 3
        bus.close()

    def test_unsubscribe_all(self) -> None:
        """unsubscribe_all should remove from all event types."""
        bus = EventBus()
        received: list[Event] = []

        class MultiSubscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED, EventType.KNOWLEDGE_RETRIEVED)

            def handle(self, event: Event) -> None:
                received.append(event)

        subscriber = MultiSubscriber()
        bus.subscribe(EventType.PLAN_CREATED, subscriber)
        bus.subscribe(EventType.KNOWLEDGE_RETRIEVED, subscriber)

        removed = bus.unsubscribe_all(subscriber)
        assert removed == 2

        bus.publish(PlanCreated(source="planner"))
        assert len(received) == 0
        bus.close()

    def test_get_subscriber_count(self) -> None:
        """get_subscriber_count should return correct count."""
        bus = EventBus()

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                pass

        subscriber = Subscriber()
        bus.subscribe(EventType.PLAN_CREATED, subscriber)

        assert bus.get_subscriber_count(EventType.PLAN_CREATED) == 1
        assert bus.get_subscriber_count(EventType.KNOWLEDGE_RETRIEVED) == 0
        assert bus.get_subscriber_count() == 1
        bus.close()

    def test_get_subscribed_types(self) -> None:
        """get_subscribed_types should return all subscribed types."""
        bus = EventBus()

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED, EventType.KNOWLEDGE_RETRIEVED)

            def handle(self, event: Event) -> None:
                pass

        bus.subscribe(EventType.PLAN_CREATED, Subscriber())
        bus.subscribe(EventType.KNOWLEDGE_RETRIEVED, Subscriber())

        types = bus.get_subscribed_types()
        assert EventType.PLAN_CREATED in types
        assert EventType.KNOWLEDGE_RETRIEVED in types
        bus.close()

    def test_priority_ordering(self) -> None:
        """Higher priority subscribers should receive events first."""
        bus = EventBus()
        received: list[str] = []

        class LowPriority:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received.append("low")

        class HighPriority:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received.append("high")

        bus.subscribe(EventType.PLAN_CREATED, LowPriority(), priority=0)
        bus.subscribe(EventType.PLAN_CREATED, HighPriority(), priority=10)

        event = PlanCreated(source="planner")
        bus.publish(event)

        assert received == ["high", "low"]
        bus.close()

    def test_context_manager(self) -> None:
        """EventBus should work as a context manager."""
        with EventBus() as bus:
            assert bus is not None

    def test_duplicate_subscription_ignored(self) -> None:
        """Duplicate subscriptions should be ignored."""
        bus = EventBus()
        received: list[Event] = []

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return (EventType.PLAN_CREATED,)

            def handle(self, event: Event) -> None:
                received.append(event)

        subscriber = Subscriber()
        bus.subscribe(EventType.PLAN_CREATED, subscriber)
        bus.subscribe(EventType.PLAN_CREATED, subscriber)  # Duplicate
        bus.subscribe(EventType.PLAN_CREATED, subscriber)  # Duplicate

        bus.publish(PlanCreated(source="planner"))

        assert len(received) == 1
        bus.close()


class TestGlobalBus:
    """Tests for global bus functions."""

    def test_get_global_bus(self) -> None:
        """get_global_bus should return a bus instance."""
        from core.PHASE_1.infrastructure.events.bus import get_global_bus, reset_global_bus

        reset_global_bus()
        bus = get_global_bus()
        assert isinstance(bus, EventBus)
        reset_global_bus()

    def test_set_global_bus(self) -> None:
        """set_global_bus should change the global bus."""
        from core.PHASE_1.infrastructure.events.bus import get_global_bus, set_global_bus, reset_global_bus

        reset_global_bus()
        custom_bus = EventBus()
        set_global_bus(custom_bus)

        assert get_global_bus() is custom_bus
        reset_global_bus()

    def test_reset_global_bus(self) -> None:
        """reset_global_bus should reset to new instance."""
        from core.PHASE_1.infrastructure.events.bus import get_global_bus, reset_global_bus

        reset_global_bus()
        bus1 = get_global_bus()
        reset_global_bus()
        bus2 = get_global_bus()

        assert bus1 is not bus2
        reset_global_bus()
