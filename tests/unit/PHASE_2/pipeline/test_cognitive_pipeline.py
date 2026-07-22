"""Tests for Cognitive Pipeline (PR-048).

Tests the complete cognitive processing pipeline.
"""

import pytest
from core.PHASE_2.pipeline import (
    create_cognitive_pipeline,
    CognitiveEventPublisher,
    CognitiveEventType,
)


class TestCognitivePipeline:
    """Tests for CognitivePipeline."""

    def test_create_pipeline(self):
        """Test pipeline creation."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        assert pipeline is not None
        assert len(pipeline.stages) == 10

    def test_pipeline_execute_success(self):
        """Test successful pipeline execution."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="What is the weather?")
        
        assert result.success is True
        assert len(result.stages) == 10
        assert result.response.get("text") is not None

    def test_pipeline_execute_intent_detection(self):
        """Test intent detection stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="Create a new user")
        
        assert result.success is True
        intent_stage = next(
            s for s in result.stages if s["stage"] == "intent"
        )
        assert intent_stage["success"] is True
        intent_data = intent_stage["data"]
        assert intent_data["intent"] in ["query", "command", "medical", "engineering", "research", "planning"]

    def test_pipeline_execute_context_building(self):
        """Test context building stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="Analyze patient data")
        
        assert result.success is True
        context_stage = next(
            s for s in result.stages if s["stage"] == "context"
        )
        assert context_stage["success"] is True

    def test_pipeline_execute_memory_retrieval(self):
        """Test memory retrieval stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="What did we discuss about X?")
        
        assert result.success is True
        memory_stage = next(
            s for s in result.stages if s["stage"] == "memory"
        )
        assert memory_stage["success"] is True

    def test_pipeline_execute_reasoning(self):
        """Test reasoning stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="Why is the system slow?")
        
        assert result.success is True
        reasoning_stage = next(
            s for s in result.stages if s["stage"] == "reasoning"
        )
        assert reasoning_stage["success"] is True

    def test_pipeline_execute_planning(self):
        """Test planning stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="Schedule a meeting with the team")
        
        assert result.success is True
        planning_stage = next(
            s for s in result.stages if s["stage"] == "planning"
        )
        assert planning_stage["success"] is True
        assert "plan_id" in planning_stage["data"]

    def test_pipeline_execute_decision(self):
        """Test decision stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="What should we do?")
        
        assert result.success is True
        decision_stage = next(
            s for s in result.stages if s["stage"] == "decision"
        )
        assert decision_stage["success"] is True
        assert "decision" in decision_stage["data"]

    def test_pipeline_execute_execution(self):
        """Test execution stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="Run diagnostics")
        
        assert result.success is True
        execution_stage = next(
            s for s in result.stages if s["stage"] == "execution"
        )
        assert execution_stage["success"] is True

    def test_pipeline_execute_learning(self):
        """Test learning stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="How can we improve?")
        
        assert result.success is True
        learning_stage = next(
            s for s in result.stages if s["stage"] == "learning"
        )
        assert learning_stage["success"] is True

    def test_pipeline_execute_response(self):
        """Test response generation stage."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(user_input="What is 2+2?")
        
        assert result.success is True
        response_stage = next(
            s for s in result.stages if s["stage"] == "response"
        )
        assert response_stage["success"] is True
        assert "text" in response_stage["data"]

    def test_pipeline_events_published(self):
        """Test that cognitive events are published."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        pipeline.execute(user_input="Test query")
        
        events = publisher.get_history()
        assert len(events) > 0
        
        event_types = {e.event_type for e in events}
        assert CognitiveEventType.PIPELINE_STARTED in event_types
        assert CognitiveEventType.PIPELINE_COMPLETED in event_types

    def test_pipeline_session_id(self):
        """Test session ID propagation."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result = pipeline.execute(
            user_input="Test",
            session_id="test-session-123"
        )
        
        assert result.session_id == "test-session-123"

    def test_pipeline_multiple_executions(self):
        """Test multiple pipeline executions."""
        publisher = CognitiveEventPublisher()
        pipeline = create_cognitive_pipeline(event_publisher=publisher)
        
        result1 = pipeline.execute(user_input="Query 1")
        result2 = pipeline.execute(user_input="Query 2")
        
        assert result1.success is True
        assert result2.success is True
        assert result1.session_id != result2.session_id


class TestCognitiveEvents:
    """Tests for Cognitive Events."""

    def test_event_publisher_subscribe(self):
        """Test event subscription."""
        publisher = CognitiveEventPublisher()
        
        received = []
        def callback(event):
            received.append(event)
        
        publisher.subscribe(callback)
        publisher.publish(type("Event", (), {"event_type": "test"})())
        
        assert len(received) == 1

    def test_event_publisher_unsubscribe(self):
        """Test event unsubscription."""
        publisher = CognitiveEventPublisher()
        
        def callback(event):
            pass
        
        publisher.subscribe(callback)
        publisher.unsubscribe(callback)
        
        publisher.publish(type("Event", (), {"event_type": "test"})())
        assert len(publisher.get_history()) == 1

    def test_event_history(self):
        """Test event history."""
        publisher = CognitiveEventPublisher()
        
        from core.PHASE_2.pipeline.cognitive_events import CognitiveEvent, CognitiveEventType
        publisher.publish(CognitiveEvent(
            event_type=CognitiveEventType.PIPELINE_STARTED,
            session_id="test-1"
        ))
        publisher.publish(CognitiveEvent(
            event_type=CognitiveEventType.PIPELINE_COMPLETED,
            session_id="test-1"
        ))
        
        history = publisher.get_history(session_id="test-1")
        assert len(history) == 2

    def test_event_clear_history(self):
        """Test clearing event history."""
        publisher = CognitiveEventPublisher()
        
        from core.PHASE_2.pipeline.cognitive_events import CognitiveEvent, CognitiveEventType
        publisher.publish(CognitiveEvent(
            event_type=CognitiveEventType.PIPELINE_STARTED
        ))
        
        publisher.clear_history()
        assert len(publisher.get_history()) == 0


class TestCognitiveStages:
    """Tests for individual cognitive stages."""

    def test_intent_detection_query(self):
        """Test intent detection for queries."""
        from core.PHASE_2.pipeline.stages import IntentDetectionStage
        
        stage = IntentDetectionStage()
        from core.PHASE_2.pipeline.context import PipelineContext
        
        context = PipelineContext(correlation_id="test")
        context["user_input"] = "What is the weather?"
        
        result = stage.execute(context)
        
        assert result.status.value == "completed"
        assert context["intent"] in ["query", "command", "medical", "engineering", "research", "planning"]

    def test_intent_detection_command(self):
        """Test intent detection for commands."""
        from core.PHASE_2.pipeline.stages import IntentDetectionStage
        
        stage = IntentDetectionStage()
        from core.PHASE_2.pipeline.context import PipelineContext
        
        context = PipelineContext(correlation_id="test")
        context["user_input"] = "Create a new file"
        
        result = stage.execute(context)
        
        assert result.status.value == "completed"
        assert context["intent"] == "command"

    def test_context_building(self):
        """Test context building stage."""
        from core.PHASE_2.pipeline.stages import ContextBuildingStage
        
        stage = ContextBuildingStage()
        from core.PHASE_2.pipeline.context import PipelineContext
        
        context = PipelineContext(correlation_id="test")
        context["user_input"] = "Test input"
        context["session_id"] = "session-1"
        context["intent"] = "query"
        
        result = stage.execute(context)
        
        assert result.status.value == "completed"
        assert "context_items" in context
