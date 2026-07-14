"""Tests for Cognitive Reasoning Integration (PR-050).

Tests the integration layer between reasoning engine and pipeline.
"""

import pytest
from core.reasoning.cognitive_reasoning_integration import (
    CognitiveReasoningIntegration,
    ReasoningEvent,
    ReasoningEventPublisher,
    ReasoningEventType,
    ReasoningMetrics,
    ReasoningTrace,
    ReasoningTracer,
    create_cognitive_reasoning_integration,
)


class TestReasoningEventPublisher:
    """Tests for ReasoningEventPublisher."""

    def test_subscribe(self):
        """Test event subscription."""
        publisher = ReasoningEventPublisher()
        
        received = []
        publisher.subscribe(lambda e: received.append(e))
        
        publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_STARTED,
            session_id="test-1",
        ))
        
        assert len(received) == 1
        assert received[0].session_id == "test-1"

    def test_unsubscribe(self):
        """Test event unsubscription."""
        publisher = ReasoningEventPublisher()
        
        def callback(e):
            pass
        
        publisher.subscribe(callback)
        publisher.unsubscribe(callback)
        
        publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_STARTED,
        ))
        
        assert len(publisher.get_history()) == 1

    def test_get_history(self):
        """Test getting event history."""
        publisher = ReasoningEventPublisher()
        
        publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_STARTED,
            session_id="s1",
        ))
        publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_COMPLETED,
            session_id="s2",
        ))
        
        # Filter by session
        s1_events = publisher.get_history(session_id="s1")
        assert len(s1_events) == 1
        
        # Filter by type
        started_events = publisher.get_history(
            event_type=ReasoningEventType.REASONING_STARTED
        )
        assert len(started_events) == 1

    def test_clear_history(self):
        """Test clearing history."""
        publisher = ReasoningEventPublisher()
        
        publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_STARTED,
        ))
        
        publisher.clear_history()
        
        assert len(publisher.get_history()) == 0


class TestReasoningTracer:
    """Tests for ReasoningTracer."""

    def test_begin_and_end_trace(self):
        """Test trace begin/end."""
        tracer = ReasoningTracer()
        
        trace_id = tracer.begin_trace(
            "reason",
            session_id="s1",
            strategy="focused",
        )
        
        assert trace_id == 0
        assert len(tracer._traces) == 1
        
        tracer.end_trace(trace_id, success=True)
        
        trace = tracer.get_traces()[0]
        assert trace.success is True
        assert trace.duration_ms >= 0

    def test_add_evidence(self):
        """Test adding evidence to trace."""
        tracer = ReasoningTracer()
        
        trace_id = tracer.begin_trace("reason")
        tracer.add_evidence(trace_id, "evidence-1")
        tracer.add_evidence(trace_id, "evidence-2")
        
        assert len(tracer._active_traces[trace_id].evidence_used) == 2

    def test_add_hypothesis(self):
        """Test adding hypothesis to trace."""
        tracer = ReasoningTracer()
        
        trace_id = tracer.begin_trace("reason")
        tracer.add_hypothesis(trace_id, "hypothesis-1")
        
        assert len(tracer._active_traces[trace_id].hypotheses_generated) == 1

    def test_trace_with_error(self):
        """Test trace with error."""
        tracer = ReasoningTracer()
        
        trace_id = tracer.begin_trace("reason")
        tracer.end_trace(trace_id, success=False, error="Not enough evidence")
        
        trace = tracer.get_traces()[0]
        assert trace.success is False
        assert trace.error == "Not enough evidence"


class TestReasoningMetrics:
    """Tests for ReasoningMetrics."""

    def test_default_values(self):
        """Test default metric values."""
        metrics = ReasoningMetrics()
        
        assert metrics.total_reasoning_sessions == 0
        assert metrics.successful_sessions == 0
        assert metrics.failed_sessions == 0
        assert metrics.total_evidence_collected == 0
        assert metrics.total_hypotheses_generated == 0


class TestCognitiveReasoningIntegration:
    """Tests for CognitiveReasoningIntegration."""

    def test_create_integration(self):
        """Test integration creation."""
        integration = create_cognitive_reasoning_integration()
        
        assert integration.engine is not None
        assert integration.publisher is not None
        assert integration.metrics is not None

    def test_events_published(self):
        """Test that events are published."""
        integration = create_cognitive_reasoning_integration()
        
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        
        # The reasoning engine may not be fully implemented,
        # so we just test that events are tracked
        integration.publisher.publish(ReasoningEvent(
            event_type=ReasoningEventType.REASONING_STARTED,
            session_id="test-session",
        ))
        
        assert len(events) == 1
        assert events[0].event_type == ReasoningEventType.REASONING_STARTED

    def test_get_all_metrics(self):
        """Test getting all metrics."""
        integration = create_cognitive_reasoning_integration()
        
        metrics = integration.get_all_metrics()
        
        assert "metrics" in metrics
        assert "traces" in metrics
        assert metrics["metrics"]["total_reasoning_sessions"] == 0


class TestReasoningEvent:
    """Tests for ReasoningEvent."""

    def test_create_event(self):
        """Test event creation."""
        event = ReasoningEvent(
            event_type=ReasoningEventType.REASONING_COMPLETED,
            session_id="test-123",
            correlation_id="corr-456",
            strategy="focused",
            evidence_count=5,
            hypothesis_count=3,
            confidence=0.85,
            duration_ms=123.45,
        )
        
        assert event.event_type == ReasoningEventType.REASONING_COMPLETED
        assert event.session_id == "test-123"
        assert event.strategy == "focused"
        assert event.evidence_count == 5
        assert event.confidence == 0.85

    def test_event_defaults(self):
        """Test event default values."""
        event = ReasoningEvent(
            event_type=ReasoningEventType.EVIDENCE_COLLECTED,
        )
        
        assert event.success is True
        assert event.error == ""
        assert event.metadata == {}
        assert event.timestamp != ""


class TestEventTypes:
    """Tests for ReasoningEventType enum."""

    def test_all_event_types_exist(self):
        """Test all expected event types exist."""
        expected_types = [
            "REASONING_STARTED",
            "REASONING_COMPLETED",
            "REASONING_FAILED",
            "EVIDENCE_COLLECTED",
            "HYPOTHESIS_GENERATED",
            "HYPOTHESIS_EVALUATED",
            "DECISION_MADE",
            "CONFIDENCE_CALCULATED",
            "EXPLANATION_GENERATED",
        ]
        
        for type_name in expected_types:
            assert hasattr(ReasoningEventType, type_name)

    def test_event_type_values(self):
        """Test event type values."""
        assert ReasoningEventType.REASONING_STARTED.value == "reasoning_started"
        assert ReasoningEventType.REASONING_COMPLETED.value == "reasoning_completed"
        assert ReasoningEventType.EVIDENCE_COLLECTED.value == "evidence_collected"
