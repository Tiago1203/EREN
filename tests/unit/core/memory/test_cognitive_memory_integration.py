"""Tests for Cognitive Memory Integration (PR-049).

Tests the integration layer between Cognitive Memory and the pipeline.
"""

import pytest
from core.memory import CognitiveMemoryEngine, MemoryType
from core.memory.cognitive_memory_integration import (
    CognitiveMemoryIntegration,
    MemoryEvent,
    MemoryEventPublisher,
    MemoryEventType,
    MemoryMetrics,
    MemoryTrace,
    MemoryTracer,
    create_cognitive_memory_integration,
)


class TestMemoryEventPublisher:
    """Tests for MemoryEventPublisher."""

    def test_subscribe(self):
        """Test event subscription."""
        publisher = MemoryEventPublisher()
        
        received = []
        publisher.subscribe(lambda e: received.append(e))
        
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
            memory_id="test-1",
        ))
        
        assert len(received) == 1
        assert received[0].memory_id == "test-1"

    def test_unsubscribe(self):
        """Test event unsubscription."""
        publisher = MemoryEventPublisher()
        
        def callback(e):
            pass
        
        publisher.subscribe(callback)
        publisher.unsubscribe(callback)
        
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
        ))
        
        assert len(publisher.get_history()) == 1

    def test_get_history(self):
        """Test getting event history."""
        publisher = MemoryEventPublisher()
        
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
            session_id="s1",
        ))
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_RETRIEVED,
            session_id="s2",
        ))
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
            session_id="s1",
        ))
        
        # Filter by session
        s1_events = publisher.get_history(session_id="s1")
        assert len(s1_events) == 2
        
        # Filter by type
        stored_events = publisher.get_history(event_type=MemoryEventType.MEMORY_STORED)
        assert len(stored_events) == 2

    def test_clear_history(self):
        """Test clearing history."""
        publisher = MemoryEventPublisher()
        
        publisher.publish(MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
        ))
        
        publisher.clear_history()
        
        assert len(publisher.get_history()) == 0


class TestMemoryTracer:
    """Tests for MemoryTracer."""

    def test_begin_and_end_trace(self):
        """Test trace begin/end."""
        tracer = MemoryTracer()
        
        trace_id = tracer.begin_trace("store", memory_id="test-1")
        
        assert trace_id == 0
        assert len(tracer._traces) == 1
        assert tracer._traces[0].operation == "store"
        assert tracer._traces[0].start_time != ""

    def test_end_trace_with_duration(self):
        """Test trace end calculates duration."""
        tracer = MemoryTracer()
        
        trace_id = tracer.begin_trace("search")
        tracer.end_trace(trace_id, success=True)
        
        trace = tracer.get_traces()[0]
        assert trace.success is True
        assert trace.duration_ms >= 0

    def test_end_trace_with_error(self):
        """Test trace with error."""
        tracer = MemoryTracer()
        
        trace_id = tracer.begin_trace("retrieve")
        tracer.end_trace(trace_id, success=False, error="Not found")
        
        trace = tracer.get_traces()[0]
        assert trace.success is False
        assert trace.error == "Not found"


class TestMemoryMetrics:
    """Tests for MemoryMetrics."""

    def test_default_values(self):
        """Test default metric values."""
        metrics = MemoryMetrics()
        
        assert metrics.total_stores == 0
        assert metrics.total_memories == 0
        assert metrics.total_searches == 0
        assert metrics.successful_searches == 0


class TestCognitiveMemoryIntegration:
    """Tests for CognitiveMemoryIntegration."""

    def test_create_integration(self):
        """Test integration creation."""
        integration = create_cognitive_memory_integration()
        
        assert integration.engine is not None
        assert integration.publisher is not None
        assert integration.metrics is not None

    def test_store_with_events(self):
        """Test store publishes events."""
        integration = create_cognitive_memory_integration()
        
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        
        memory_id = integration.store(
            content="Test memory",
            memory_type=MemoryType.SHORT_TERM,
            session_id="test-session",
        )
        
        assert memory_id != ""
        assert len(events) == 1
        assert events[0].event_type == MemoryEventType.MEMORY_STORED
        assert events[0].success is True

    def test_retrieve_with_events(self):
        """Test retrieve publishes events."""
        integration = create_cognitive_memory_integration()
        
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        
        # First store
        memory_id = integration.store(
            content="Test memory",
            memory_type=MemoryType.SHORT_TERM,
        )
        
        # Then retrieve
        memory = integration.retrieve(memory_id)
        
        assert memory is not None
        retrieve_events = [e for e in events if e.event_type == MemoryEventType.MEMORY_RETRIEVED]
        assert len(retrieve_events) == 1

    def test_search_with_events(self):
        """Test search publishes events."""
        from core.memory.memory_models import MemoryQuery
        
        integration = create_cognitive_memory_integration()
        
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        
        # Store some memories
        integration.store(
            content="Python programming",
            memory_type=MemoryType.SEMANTIC,
        )
        integration.store(
            content="JavaScript programming",
            memory_type=MemoryType.SEMANTIC,
        )
        
        # Search
        results = integration.search(
            MemoryQuery(query_text="programming"),
        )
        
        search_events = [e for e in events if e.event_type == MemoryEventType.MEMORY_SEARCHED]
        assert len(search_events) == 1
        assert search_events[0].success is True

    def test_get_all_metrics(self):
        """Test getting all metrics."""
        integration = create_cognitive_memory_integration()
        
        # Perform some operations
        integration.store(
            content="Test",
            memory_type=MemoryType.SHORT_TERM,
        )
        integration.store(
            content="Test 2",
            memory_type=MemoryType.LONG_TERM,
        )
        
        metrics = integration.get_all_metrics()
        
        assert "engine" in metrics
        assert "metrics" in metrics
        assert metrics["metrics"]["total_memories"] == 2

    def test_error_handling(self):
        """Test error handling in store."""
        from core.memory.memory_models import MemoryQuery
        
        integration = create_cognitive_memory_integration()
        
        events = []
        integration.publisher.subscribe(lambda e: events.append(e))
        
        # Search for non-existent memory should not fail
        results = integration.search(MemoryQuery(query_text="nonexistent"))
        
        search_events = [e for e in events if e.event_type == MemoryEventType.MEMORY_SEARCHED]
        assert len(search_events) == 1

    def test_session_isolation(self):
        """Test events are session-isolated."""
        integration = create_cognitive_memory_integration()
        
        integration.store(
            content="Memory 1",
            memory_type=MemoryType.SHORT_TERM,
            session_id="session-1",
        )
        integration.store(
            content="Memory 2",
            memory_type=MemoryType.SHORT_TERM,
            session_id="session-2",
        )
        
        session1_events = integration.publisher.get_history(session_id="session-1")
        session2_events = integration.publisher.get_history(session_id="session-2")
        
        assert len(session1_events) == 1
        assert len(session2_events) == 1
        assert session1_events[0].memory_type == MemoryType.SHORT_TERM.value


class TestMemoryEvent:
    """Tests for MemoryEvent."""

    def test_create_event(self):
        """Test event creation."""
        event = MemoryEvent(
            event_type=MemoryEventType.MEMORY_STORED,
            memory_id="test-123",
            memory_type="short_term",
            session_id="sess-1",
        )
        
        assert event.event_type == MemoryEventType.MEMORY_STORED
        assert event.memory_id == "test-123"
        assert event.memory_type == "short_term"
        assert event.timestamp != ""

    def test_event_defaults(self):
        """Test event default values."""
        event = MemoryEvent(
            event_type=MemoryEventType.MEMORY_RETRIEVED,
        )
        
        assert event.success is True
        assert event.error == ""
        assert event.metadata == {}
