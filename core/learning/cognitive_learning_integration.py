"""Cognitive Learning Engine (PR-055).

Provides learning and adaptation capabilities for EREN OS.
Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


# =============================================================================
# Learning Events
# =============================================================================


class LearningEventType(str, Enum):
    """Types of learning events."""
    LEARNING_STARTED = "learning_started"
    LEARNING_COMPLETED = "learning_completed"
    LEARNING_FAILED = "learning_failed"
    PATTERN_DETECTED = "pattern_detected"
    PATTERN_LEARNED = "pattern_learned"
    MODEL_UPDATED = "model_updated"
    FEEDBACK_RECEIVED = "feedback_received"


@dataclass
class LearningEvent:
    """Learning event."""
    event_type: LearningEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    pattern_id: str = ""
    model_id: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Learning Types
# =============================================================================


@dataclass
class Pattern:
    """A learned pattern."""
    id: str
    name: str
    description: str = ""
    confidence: float = 0.0
    occurrences: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningModel:
    """A learning model."""
    id: str
    name: str
    version: str = "1.0"
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Learning Engine
# =============================================================================


class LearningEngine:
    """Engine for learning and adaptation."""

    def __init__(self):
        self._patterns: dict[str, Pattern] = {}
        self._models: dict[str, LearningModel] = {}
        self._subscribers: list[Callable] = []

    def learn(
        self,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Learn from data."""
        import time
        
        self._publish(LearningEvent(
            event_type=LearningEventType.LEARNING_STARTED,
            session_id=session_id,
        ))

        start = time.perf_counter()

        try:
            # Detect patterns (simplified)
            patterns = self._detect_patterns(data)

            # Update models
            self._update_models(data, patterns)

            duration_ms = (time.perf_counter() - start) * 1000

            self._publish(LearningEvent(
                event_type=LearningEventType.LEARNING_COMPLETED,
                session_id=session_id,
                pattern_id=patterns[0].id if patterns else "",
                duration_ms=duration_ms,
                success=True,
            ))

            return {
                "success": True,
                "patterns_learned": len(patterns),
                "duration_ms": duration_ms,
            }

        except Exception as e:
            self._publish(LearningEvent(
                event_type=LearningEventType.LEARNING_FAILED,
                session_id=session_id,
                error=str(e),
                success=False,
            ))

            return {
                "success": False,
                "error": str(e),
            }

    def _detect_patterns(self, data: dict[str, Any]) -> list[Pattern]:
        """Detect patterns in data."""
        patterns = []
        
        # Simple pattern detection (placeholder)
        if "pattern" in data:
            pattern = Pattern(
                id=f"pattern_{len(self._patterns)}",
                name=data.get("pattern", "Unnamed"),
                description=data.get("description", ""),
                confidence=0.8,
                occurrences=1,
            )
            self._patterns[pattern.id] = pattern
            patterns.append(pattern)

            self._publish(LearningEvent(
                event_type=LearningEventType.PATTERN_DETECTED,
                pattern_id=pattern.id,
            ))

            self._publish(LearningEvent(
                event_type=LearningEventType.PATTERN_LEARNED,
                pattern_id=pattern.id,
            ))

        return patterns

    def _update_models(self, data: dict[str, Any], patterns: list[Pattern]) -> None:
        """Update learning models."""
        for pattern in patterns:
            model = LearningModel(
                id=f"model_{pattern.id}",
                name=f"Model for {pattern.name}",
                version="1.0",
                parameters={"pattern_id": pattern.id},
            )
            self._models[model.id] = model

            self._publish(LearningEvent(
                event_type=LearningEventType.MODEL_UPDATED,
                model_id=model.id,
            ))

    def receive_feedback(
        self,
        pattern_id: str,
        feedback: float,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Receive feedback on learned pattern."""
        pattern = self._patterns.get(pattern_id)
        if not pattern:
            return {"success": False, "error": "Pattern not found"}

        # Update confidence based on feedback
        pattern.confidence = (pattern.confidence + feedback) / 2
        pattern.occurrences += 1

        self._publish(LearningEvent(
            event_type=LearningEventType.FEEDBACK_RECEIVED,
            pattern_id=pattern_id,
            session_id=session_id,
        ))

        return {
            "success": True,
            "pattern_id": pattern_id,
            "new_confidence": pattern.confidence,
        }

    def predict(
        self,
        context: dict[str, Any],
        pattern_id: str | None = None,
    ) -> dict[str, Any]:
        """Predict based on learned patterns."""
        if pattern_id:
            pattern = self._patterns.get(pattern_id)
            if pattern:
                return {
                    "success": True,
                    "prediction": {
                        "pattern": pattern.name,
                        "confidence": pattern.confidence,
                    },
                }

        # Find best matching pattern
        best_pattern = max(
            self._patterns.values(),
            key=lambda p: p.confidence,
            default=None,
        )

        if best_pattern:
            return {
                "success": True,
                "prediction": {
                    "pattern": best_pattern.name,
                    "confidence": best_pattern.confidence,
                },
            }

        return {
            "success": False,
            "error": "No patterns available",
        }

    def get_patterns(self) -> list[Pattern]:
        """Get all learned patterns."""
        return list(self._patterns.values())

    def get_models(self) -> list[LearningModel]:
        """Get all learning models."""
        return list(self._models.values())

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to learning events."""
        self._subscribers.append(callback)

    def _publish(self, event: LearningEvent) -> None:
        """Publish an event."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass
