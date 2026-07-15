"""Tests for Value Objects."""

from __future__ import annotations

import pytest

from core.shared import (
    Confidence,
    Priority,
    SafetyLevel,
    ValueObject,
)


class TestValueObject:
    """Tests for ValueObject base class."""

    def test_value_objects_are_immutable(self) -> None:
        """Value objects should be frozen and immutable."""
        from dataclasses import dataclass

        @dataclass(frozen=True, slots=True)
        class Point(ValueObject):
            x: int
            y: int

        point = Point(x=1, y=2)

        with pytest.raises(AttributeError):
            point.x = 3  # type: ignore

    def test_value_objects_equal_by_attributes(self) -> None:
        """Value objects with same attributes should be equal."""
        from dataclasses import dataclass

        @dataclass(frozen=True, slots=True)
        class Point(ValueObject):
            x: int
            y: int

        point1 = Point(x=1, y=2)
        point2 = Point(x=1, y=2)

        assert point1 == point2
        assert hash(point1) == hash(point2)

    def test_value_objects_different_by_attributes(self) -> None:
        """Value objects with different attributes should not be equal."""
        from dataclasses import dataclass

        @dataclass(frozen=True, slots=True)
        class Point(ValueObject):
            x: int
            y: int

        point1 = Point(x=1, y=2)
        point2 = Point(x=1, y=3)

        assert point1 != point2


class TestPriority:
    """Tests for Priority value object."""

    def test_priority_creation(self) -> None:
        """Priority should be creatable with valid values."""
        p = Priority(value="high")
        assert p.value == "high"

    def test_priority_factory_methods(self) -> None:
        """Priority should have factory methods."""
        assert Priority.critical().value == "critical"
        assert Priority.high().value == "high"
        assert Priority.medium().value == "medium"
        assert Priority.low().value == "low"

    def test_priority_invalid_value(self) -> None:
        """Priority should raise for invalid values."""
        with pytest.raises(ValueError, match="Invalid priority"):
            Priority(value="invalid")

    def test_priority_case_insensitive(self) -> None:
        """Priority should be case insensitive (validated but stored as lowercase)."""
        p = Priority(value="HIGH")
        # Priority validates and stores lowercase
        assert p.value == "high"

    def test_priority_to_int(self) -> None:
        """Priority should convert to integer order."""
        assert int(Priority.critical()) == 4
        assert int(Priority.high()) == 3
        assert int(Priority.medium()) == 2
        assert int(Priority.low()) == 1


class TestSafetyLevel:
    """Tests for SafetyLevel value object."""

    def test_safety_level_creation(self) -> None:
        """SafetyLevel should be creatable with valid values."""
        sl = SafetyLevel(value="warning")
        assert sl.value == "warning"

    def test_safety_level_factory_methods(self) -> None:
        """SafetyLevel should have factory methods."""
        assert SafetyLevel.informational().value == "informational"
        assert SafetyLevel.recommendation().value == "recommendation"
        assert SafetyLevel.warning().value == "warning"
        assert SafetyLevel.critical().value == "critical"
        assert SafetyLevel.never_automate().value == "never_automate"

    def test_safety_level_requires_approval(self) -> None:
        """Critical and never_automate should require human approval."""
        assert SafetyLevel.informational().requires_human_approval() is False
        assert SafetyLevel.recommendation().requires_human_approval() is False
        assert SafetyLevel.warning().requires_human_approval() is False
        assert SafetyLevel.critical().requires_human_approval() is True
        assert SafetyLevel.never_automate().requires_human_approval() is True

    def test_safety_level_invalid_value(self) -> None:
        """SafetyLevel should raise for invalid values."""
        with pytest.raises(ValueError, match="Invalid safety level"):
            SafetyLevel(value="invalid")


class TestConfidence:
    """Tests for Confidence value object."""

    def test_confidence_creation(self) -> None:
        """Confidence should be creatable with all parameters."""
        c = Confidence(
            score=0.85,
            evidence_count=10,
            consensus=0.8,
            freshness=0.9,
        )
        assert c.score == 0.85
        assert c.evidence_count == 10
        assert c.consensus == 0.8
        assert c.freshness == 0.9

    def test_confidence_from_score(self) -> None:
        """Confidence should be creatable from just score."""
        c = Confidence.from_score(0.75)
        assert c.score == 0.75
        assert c.evidence_count == 0
        assert c.consensus == 0.0
        assert c.freshness == 1.0

    def test_confidence_factory_methods(self) -> None:
        """Confidence should have factory methods for levels."""
        assert Confidence.low().score == 0.3
        assert Confidence.medium().score == 0.6
        assert Confidence.high().score == 0.85

    def test_confidence_invalid_score(self) -> None:
        """Confidence should raise for invalid score."""
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            Confidence(score=1.5, evidence_count=1, consensus=0.5, freshness=0.5)

        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            Confidence(score=-0.1, evidence_count=1, consensus=0.5, freshness=0.5)

    def test_confidence_is_high(self) -> None:
        """Confidence should correctly identify high confidence."""
        assert Confidence.high().is_high() is True
        assert Confidence(score=0.7, evidence_count=5, consensus=0.6, freshness=0.8).is_high() is True
        assert Confidence.medium().is_high() is False
        assert Confidence.low().is_high() is False

    def test_confidence_is_low(self) -> None:
        """Confidence should correctly identify low confidence."""
        assert Confidence.low().is_low() is True
        assert Confidence(score=0.4, evidence_count=2, consensus=0.3, freshness=0.5).is_low() is True
        assert Confidence.medium().is_low() is False
        assert Confidence.high().is_low() is False
