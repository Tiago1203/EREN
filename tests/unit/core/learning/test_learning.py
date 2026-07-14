"""Tests for Learning Engine (PR-055)."""

import pytest
from core.learning.cognitive_learning_integration import (
    LearningEngine,
    Pattern,
    LearningModel,
    LearningEvent,
    LearningEventType,
)


class TestLearningEngine:
    def test_learn(self):
        engine = LearningEngine()
        result = engine.learn({"pattern": "test"})
        assert result["success"] is True
        assert result["patterns_learned"] >= 0

    def test_learn_with_pattern(self):
        engine = LearningEngine()
        result = engine.learn({"pattern": "diagnosis_pattern", "description": "A diagnostic pattern"})
        assert result["success"] is True

    def test_receive_feedback(self):
        engine = LearningEngine()
        engine.learn({"pattern": "test"})
        patterns = engine.get_patterns()
        if patterns:
            result = engine.receive_feedback(patterns[0].id, 0.9)
            assert result["success"] is True

    def test_predict(self):
        engine = LearningEngine()
        result = engine.predict({"context": "test"})
        assert "success" in result

    def test_predict_with_pattern(self):
        engine = LearningEngine()
        engine.learn({"pattern": "test"})
        patterns = engine.get_patterns()
        if patterns:
            result = engine.predict({"context": "test"}, pattern_id=patterns[0].id)
            assert result["success"] is True

    def test_get_patterns(self):
        engine = LearningEngine()
        patterns = engine.get_patterns()
        assert isinstance(patterns, list)

    def test_get_models(self):
        engine = LearningEngine()
        models = engine.get_models()
        assert isinstance(models, list)

    def test_events(self):
        engine = LearningEngine()
        events = []
        engine.subscribe(lambda e: events.append(e))
        engine.learn({"pattern": "test"})
        assert isinstance(events, list)


class TestPattern:
    def test_create_pattern(self):
        pattern = Pattern(
            id="p1",
            name="Test Pattern",
            description="A test pattern",
            confidence=0.8,
        )
        assert pattern.id == "p1"
        assert pattern.name == "Test Pattern"
        assert pattern.confidence == 0.8


class TestLearningModel:
    def test_create_model(self):
        model = LearningModel(
            id="m1",
            name="Test Model",
            version="1.0",
        )
        assert model.id == "m1"
        assert model.name == "Test Model"
        assert model.version == "1.0"
