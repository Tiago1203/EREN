"""Tests for Cognitive Planning Integration (PR-051)."""

import pytest
from core.PHASE_2.planning.cognitive_planning_integration import (
    PlanningEvent,
    PlanningEventPublisher,
    PlanningEventType,
    PlanningMetrics,
    CognitivePlanningIntegration,
    create_cognitive_planning_integration,
)


class TestPlanningEventPublisher:
    def test_subscribe(self):
        publisher = PlanningEventPublisher()
        received = []
        publisher.subscribe(lambda e: received.append(e))
        publisher.publish(PlanningEvent(
            event_type=PlanningEventType.PLANNING_STARTED,
            session_id="test-1",
        ))
        assert len(received) == 1

    def test_get_history(self):
        publisher = PlanningEventPublisher()
        publisher.publish(PlanningEvent(
            event_type=PlanningEventType.PLANNING_STARTED,
            session_id="s1",
        ))
        publisher.publish(PlanningEvent(
            event_type=PlanningEventType.PLANNING_COMPLETED,
            session_id="s1",
        ))
        s1_events = publisher.get_history(session_id="s1")
        assert len(s1_events) == 2


class TestCognitivePlanningIntegration:
    def test_create_integration(self):
        integration = create_cognitive_planning_integration()
        assert integration.engine is not None
        assert integration.publisher is not None
        assert integration.metrics is not None

    def test_events_published(self):
        integration = create_cognitive_planning_integration()
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        integration.publisher.publish(PlanningEvent(
            event_type=PlanningEventType.PLANNING_STARTED,
        ))
        assert len(events) == 1

    def test_get_all_metrics(self):
        integration = create_cognitive_planning_integration()
        metrics = integration.get_all_metrics()
        assert "metrics" in metrics
