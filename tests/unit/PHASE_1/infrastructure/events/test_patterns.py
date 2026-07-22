"""Tests for subscriber and publisher patterns."""

from __future__ import annotations

import pytest

from core.PHASE_1.infrastructure.events.bus import EventBus
from core.PHASE_1.infrastructure.events.models import (
    Event,
    EventType,
    PlanCreated,
    KnowledgeRetrieved,
    ReasoningStarted,
)
from core.PHASE_1.infrastructure.events.subscriber import (
    BaseSubscriber,
    FunctionSubscriber,
    MultiHandlerSubscriber,
    LoggingSubscriber,
    AuditSubscriber,
    MetricSubscriber,
)
from core.PHASE_1.infrastructure.events.publisher import (
    EventPublisherMixin,
    EventContext,
    EventAggregator,
)


class TestFunctionSubscriber:
    """Tests for FunctionSubscriber."""

    def test_function_subscriber_receives_events(self) -> None:
        """Function subscriber should receive matching events."""
        bus = EventBus()
        received: list[Event] = []

        def handler(event: Event) -> None:
            received.append(event)

        subscriber = FunctionSubscriber(
            event_types=(EventType.PLAN_CREATED,),
            handler=handler,
        )

        bus.subscribe(EventType.PLAN_CREATED, subscriber)
        bus.publish(PlanCreated(source="planner"))

        assert len(received) == 1
        bus.close()

    def test_function_subscriber_with_predicate(self) -> None:
        """Function subscriber with predicate should filter events."""
        bus = EventBus()
        received: list[Event] = []

        def handler(event: Event) -> None:
            received.append(event)

        subscriber = FunctionSubscriber(
            event_types=(EventType.PLAN_CREATED,),
            handler=handler,
            predicate=lambda e: e.payload.get("priority") == "high",
        )

        bus.subscribe(EventType.PLAN_CREATED, subscriber)

        bus.publish(PlanCreated(source="planner", payload={"priority": "low"}))
        bus.publish(PlanCreated(source="planner", payload={"priority": "high"}))

        assert len(received) == 1
        bus.close()


class TestMultiHandlerSubscriber:
    """Tests for MultiHandlerSubscriber."""

    def test_routes_to_correct_handler(self) -> None:
        """MultiHandlerSubscriber should route to correct handler."""
        bus = EventBus()
        plan_events: list[Event] = []
        knowledge_events: list[Event] = []

        subscriber = MultiHandlerSubscriber()
        subscriber.register(EventType.PLAN_CREATED, lambda e: plan_events.append(e))
        subscriber.register(EventType.KNOWLEDGE_RETRIEVED, lambda e: knowledge_events.append(e))

        bus.subscribe(EventType.PLAN_CREATED, subscriber)
        bus.subscribe(EventType.KNOWLEDGE_RETRIEVED, subscriber)

        bus.publish(PlanCreated(source="planner"))
        bus.publish(KnowledgeRetrieved(source="knowledge"))

        assert len(plan_events) == 1
        assert len(knowledge_events) == 1
        bus.close()

    def test_fallback_handler(self) -> None:
        """MultiHandlerSubscriber should call fallback for unmatched events."""
        bus = EventBus()
        fallback_events: list[Event] = []

        subscriber = MultiHandlerSubscriber()
        subscriber.register(EventType.PLAN_CREATED, lambda e: None)
        subscriber.register_fallback(lambda e: fallback_events.append(e))

        bus.subscribe_wildcard(subscriber)

        bus.publish(PlanCreated(source="planner"))
        bus.publish(ReasoningStarted(source="reasoning"))

        assert len(fallback_events) == 1
        bus.close()


class TestLoggingSubscriber:
    """Tests for LoggingSubscriber."""

    def test_logs_events(self) -> None:
        """LoggingSubscriber should be a valid subscriber."""
        subscriber = LoggingSubscriber(
            event_types=(EventType.PLAN_CREATED,),
            log_level=20,  # INFO
        )

        event = PlanCreated(source="planner")
        subscriber.handle(event)  # Should not raise

        assert EventType.PLAN_CREATED in subscriber.subscribed_types


class TestAuditSubscriber:
    """Tests for AuditSubscriber."""

    def test_creates_audit_records(self) -> None:
        """AuditSubscriber should create audit records."""
        bus = EventBus()
        subscriber = AuditSubscriber()

        bus.subscribe_wildcard(subscriber)

        event = PlanCreated(
            source="planner",
            correlation_id="req-123",
            payload={"step_count": 5},
        )
        bus.publish(event)

        records = subscriber.get_records()
        assert len(records) == 1
        assert records[0]["event_type"] == "plan_created"
        assert records[0]["correlation_id"] == "req-123"
        assert records[0]["payload_keys"] == ["step_count"]
        bus.close()

    def test_filter_by_event_type(self) -> None:
        """get_records should filter by event type."""
        bus = EventBus()
        subscriber = AuditSubscriber()

        bus.subscribe_wildcard(subscriber)

        bus.publish(PlanCreated(source="planner"))
        bus.publish(KnowledgeRetrieved(source="knowledge"))
        bus.publish(ReasoningStarted(source="reasoning"))

        plan_records = subscriber.get_records(event_type=EventType.PLAN_CREATED)
        assert len(plan_records) == 1
        bus.close()


class TestMetricSubscriber:
    """Tests for MetricSubscriber."""

    def test_collects_metrics(self) -> None:
        """MetricSubscriber should collect event counts."""
        bus = EventBus()
        subscriber = MetricSubscriber()

        bus.subscribe_wildcard(subscriber)

        bus.publish(PlanCreated(source="planner"))
        bus.publish(PlanCreated(source="planner"))
        bus.publish(KnowledgeRetrieved(source="knowledge"))

        counts = subscriber.get_counts()
        assert counts["plan_created"] == 2
        assert counts["knowledge_retrieved"] == 1
        assert subscriber.get_total_count() == 3
        bus.close()


class TestEventContext:
    """Tests for EventContext."""

    def test_event_context_publishes(self) -> None:
        """EventContext should publish events."""
        bus = EventBus()
        received: list[Event] = []

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return ()

            def handle(self, event: Event) -> None:
                received.append(event)

        bus.subscribe_wildcard(Subscriber())

        with EventContext(
            correlation_id="req-123",
            source="test",
            event_bus=bus,
        ) as ctx:
            ctx.publish(EventType.PLAN_CREATED, step_count=5)

        assert len(received) == 1
        assert received[0].correlation_id == "req-123"
        assert received[0].source == "test"
        bus.close()


class TestEventAggregator:
    """Tests for EventAggregator."""

    def test_aggregates_and_publishes(self) -> None:
        """EventAggregator should publish all events at once."""
        bus = EventBus()
        received: list[Event] = []

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return ()

            def handle(self, event: Event) -> None:
                received.append(event)

        bus.subscribe_wildcard(Subscriber())

        aggregator = EventAggregator(
            source="test",
            correlation_id="req-123",
            event_bus=bus,
        )

        aggregator.add(EventType.PLAN_CREATED, step_count=5)
        aggregator.add(EventType.KNOWLEDGE_RETRIEVED, count=10)
        assert len(aggregator) == 2

        aggregator.publish_all()
        assert len(aggregator) == 0
        assert len(received) == 2
        bus.close()


class TestEventPublisherMixin:
    """Tests for EventPublisherMixin."""

    def test_publishes_events(self) -> None:
        """EventPublisherMixin should publish events."""
        bus = EventBus()
        received: list[Event] = []

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return ()

            def handle(self, event: Event) -> None:
                received.append(event)

        bus.subscribe_wildcard(Subscriber())

        class MyPublisher(EventPublisherMixin):
            pass

        publisher = MyPublisher(event_bus=bus, source="my-engine")
        publisher.publish(EventType.PLAN_CREATED, step_count=5)

        assert len(received) == 1
        assert received[0].source == "my-engine"
        bus.close()

    def test_context_manager(self) -> None:
        """EventPublisherMixin context manager should work."""
        bus = EventBus()
        received: list[Event] = []

        class Subscriber:
            @property
            def subscribed_types(self) -> tuple[EventType, ...]:
                return ()

            def handle(self, event: Event) -> None:
                received.append(event)

        bus.subscribe_wildcard(Subscriber())

        class MyPublisher(EventPublisherMixin):
            pass

        publisher = MyPublisher(event_bus=bus, source="my-engine")

        with publisher.context(correlation_id="ctx-123"):
            publisher.publish(EventType.PLAN_CREATED)

        assert len(received) == 1
        assert received[0].correlation_id == "ctx-123"
        bus.close()
