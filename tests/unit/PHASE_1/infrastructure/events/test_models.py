"""Tests for event models."""

from __future__ import annotations

import pytest

from core.PHASE_1.infrastructure.events.models import (
    Event,
    EventType,
    create_event,
    EVENT_TYPE_TO_CLASS,
    PlanCreated,
    KnowledgeRetrieved,
    ReasoningStarted,
)


class TestEventType:
    """Tests for the EventType enum."""

    def test_all_event_types_exist(self) -> None:
        """All expected event types should exist."""
        expected_types = {
            "voice_input_received",
            "voice_output_generated",
            "intent_received",
            "intent_detected",
            "plan_created",
            "knowledge_requested",
            "knowledge_retrieved",
            "memory_requested",
            "memory_retrieved",
            "reasoning_started",
            "reasoning_finished",
            "diagnostic_started",
            "diagnostic_completed",
            "workflow_started",
            "workflow_completed",
            "tool_executed",
            "response_generated",
            "engine_error",
        }
        actual_types = {e.value for e in EventType}
        assert expected_types.issubset(actual_types)

    def test_event_types_are_unique(self) -> None:
        """All event type values should be unique."""
        values = [e.value for e in EventType]
        assert len(values) == len(set(values))


class TestEvent:
    """Tests for the Event base model."""

    def test_event_has_id(self) -> None:
        """Event should have a unique ID."""
        event = Event(type=EventType.PLAN_CREATED)
        assert event.event_id is not None
        assert len(event.event_id) > 0

    def test_event_has_timestamp(self) -> None:
        """Event should have a timestamp."""
        event = Event(type=EventType.PLAN_CREATED)
        assert event.timestamp is not None

    def test_event_can_set_context(self) -> None:
        """Event should allow setting context fields."""
        event = Event(
            type=EventType.PLAN_CREATED,
            source="planner",
            correlation_id="req-123",
            session_id="sess-456",
        )
        assert event.source == "planner"
        assert event.correlation_id == "req-123"
        assert event.session_id == "sess-456"

    def test_event_can_have_payload(self) -> None:
        """Event should allow a payload."""
        event = Event(
            type=EventType.PLAN_CREATED,
            payload={"step_count": 5, "priority": "high"},
        )
        assert event.payload["step_count"] == 5
        assert event.payload["priority"] == "high"

    def test_event_is_frozen(self) -> None:
        """Event should be immutable."""
        event = Event(type=EventType.PLAN_CREATED)
        with pytest.raises(Exception):
            event.event_id = "modified"  # type: ignore

    def test_event_with_context_method(self) -> None:
        """Event.with_context should return a copy with updated context."""
        event = Event(
            type=EventType.PLAN_CREATED,
            source="original",
            correlation_id="old",
        )
        updated = event.with_context(
            source="new",
            correlation_id="new-correlation",
        )
        assert updated.source == "new"
        assert updated.correlation_id == "new-correlation"
        # Original should be unchanged
        assert event.source == "original"
        assert event.correlation_id == "old"


class TestEventSubclasses:
    """Tests for specific event subclasses."""

    def test_plan_created_event(self) -> None:
        """PlanCreated should have correct type."""
        event = PlanCreated(
            source="planner",
            payload={"step_count": 5},
        )
        assert event.type == EventType.PLAN_CREATED
        assert event.payload["step_count"] == 5

    def test_knowledge_retrieved_event(self) -> None:
        """KnowledgeRetrieved should have correct type."""
        event = KnowledgeRetrieved(
            source="knowledge",
            payload={"document_count": 10},
        )
        assert event.type == EventType.KNOWLEDGE_RETRIEVED
        assert event.payload["document_count"] == 10

    def test_reasoning_started_event(self) -> None:
        """ReasoningStarted should have correct type."""
        event = ReasoningStarted(
            source="reasoning",
            payload={"question": "Why is the device failing?"},
        )
        assert event.type == EventType.REASONING_STARTED
        assert event.payload["question"] == "Why is the device failing?"


class TestCreateEvent:
    """Tests for the create_event factory function."""

    def test_create_event_by_type(self) -> None:
        """create_event should create the correct event type."""
        event = create_event(
            event_type=EventType.PLAN_CREATED,
            source="planner",
            correlation_id="req-123",
            step_count=5,
        )
        assert isinstance(event, PlanCreated)
        assert event.source == "planner"
        assert event.correlation_id == "req-123"
        assert event.payload["step_count"] == 5

    def test_create_event_unknown_type_raises(self) -> None:
        """create_event should raise for unknown event types."""
        with pytest.raises(ValueError):
            create_event(
                event_type="unknown"  # type: ignore
            )

    def test_create_all_event_types(self) -> None:
        """All event types should be createable."""
        for event_type in EventType:
            event = create_event(event_type=event_type, source="test")
            assert isinstance(event, Event)
            assert event.type == event_type


class TestEventTypeRegistry:
    """Tests for the EVENT_TYPE_TO_CLASS registry."""

    def test_registry_has_all_types(self) -> None:
        """Registry should have an entry for every EventType."""
        for event_type in EventType:
            assert event_type in EVENT_TYPE_TO_CLASS

    def test_registry_maps_to_correct_classes(self) -> None:
        """Registry should map to the correct classes."""
        assert EVENT_TYPE_TO_CLASS[EventType.PLAN_CREATED] == PlanCreated
        assert EVENT_TYPE_TO_CLASS[EventType.KNOWLEDGE_RETRIEVED] == KnowledgeRetrieved
