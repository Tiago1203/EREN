"""Feedback Analyzer for EREN Cognitive Learning Platform.

Analyzes feedback for learning.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.learning.types import Feedback, FeedbackType

if TYPE_CHECKING:
    pass


class FeedbackAnalyzer:
    """Analyzes feedback for learning.

    The Feedback Analyzer does NOT:
    - Record experiences
    - Generate patterns
    - Consolidate knowledge

    It ONLY:
    - Collects feedback
    - Analyzes feedback
    - Categorizes feedback
    """

    def __init__(self):
        """Initialize feedback analyzer."""
        self._feedback: dict[str, Feedback] = {}
        self._by_type: dict[FeedbackType, list[str]] = {ft: [] for ft in FeedbackType}
        self._by_experience: dict[str, list[str]] = {}

    def add(
        self,
        experience_id: str,
        feedback_type: FeedbackType,
        content: str,
        rating: float = 0.5,
        source: str = "user",
    ) -> Feedback:
        """Add feedback.

        Args:
            experience_id: Related experience ID.
            feedback_type: Type of feedback.
            content: Feedback content.
            rating: Rating (0.0 to 1.0).
            source: Feedback source.

        Returns:
            Added feedback.
        """
        feedback_id = f"fb_{uuid.uuid4().hex[:16]}"

        feedback = Feedback(
            feedback_id=feedback_id,
            experience_id=experience_id,
            feedback_type=feedback_type,
            content=content,
            rating=rating,
            source=source,
        )

        self._feedback[feedback_id] = feedback

        # Index by type
        self._by_type[feedback_type].append(feedback_id)

        # Index by experience
        if experience_id not in self._by_experience:
            self._by_experience[experience_id] = []
        self._by_experience[experience_id].append(feedback_id)

        return feedback

    def analyze(self, feedback_id: str) -> dict:
        """Analyze feedback.

        Args:
            feedback_id: Feedback ID.

        Returns:
            Analysis results.
        """
        feedback = self._feedback.get(feedback_id)
        if not feedback:
            return {}

        return {
            "feedback_id": feedback_id,
            "type": feedback.feedback_type.value,
            "rating": feedback.rating,
            "sentiment": self._classify_sentiment(feedback),
            "actionable": self._is_actionable(feedback),
        }

    def _classify_sentiment(self, feedback: Feedback) -> str:
        """Classify sentiment.

        Args:
            feedback: Feedback to analyze.

        Returns:
            Sentiment classification.
        """
        if feedback.feedback_type == FeedbackType.POSITIVE:
            return "positive"
        elif feedback.feedback_type == FeedbackType.NEGATIVE:
            return "negative"
        elif feedback.feedback_type == FeedbackType.CORRECTION:
            return "corrective"
        return "neutral"

    def _is_actionable(self, feedback: Feedback) -> bool:
        """Check if feedback is actionable.

        Args:
            feedback: Feedback to analyze.

        Returns:
            True if actionable.
        """
        return (
            feedback.feedback_type in [FeedbackType.NEGATIVE, FeedbackType.CORRECTION]
            or feedback.rating < 0.3
        )

    def get(self, feedback_id: str) -> Feedback | None:
        """Get feedback by ID."""
        return self._feedback.get(feedback_id)

    def get_by_experience(self, experience_id: str) -> list[Feedback]:
        """Get feedback by experience."""
        fb_ids = self._by_experience.get(experience_id, [])
        return [self._feedback[fid] for fid in fb_ids if fid in self._feedback]

    def get_by_type(self, feedback_type: FeedbackType) -> list[Feedback]:
        """Get feedback by type."""
        fb_ids = self._by_type.get(feedback_type, [])
        return [self._feedback[fid] for fid in fb_ids if fid in self._feedback]

    def get_avg_rating(self) -> float:
        """Get average rating.

        Returns:
            Average rating.
        """
        if not self._feedback:
            return 0.5
        return sum(f.rating for f in self._feedback.values()) / len(self._feedback)


# Global feedback analyzer
_feedback_analyzer: FeedbackAnalyzer | None = None
_analyzer_lock = __import__("threading").Lock()


def get_feedback_analyzer() -> FeedbackAnalyzer:
    """Get the global feedback analyzer."""
    global _feedback_analyzer
    with _analyzer_lock:
        if _feedback_analyzer is None:
            _feedback_analyzer = FeedbackAnalyzer()
        return _feedback_analyzer


def reset_feedback_analyzer() -> None:
    """Reset the global feedback analyzer."""
    global _feedback_analyzer
    with _analyzer_lock:
        _feedback_analyzer = None
