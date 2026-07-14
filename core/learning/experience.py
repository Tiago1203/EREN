"""Experience Collector for EREN Cognitive Learning Platform.

Records experiences for learning.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.learning.types import Experience

if TYPE_CHECKING:
    pass


class ExperienceCollector:
    """Collects experiences for learning.

    The Experience Collector does NOT:
    - Analyze experiences
    - Generate patterns
    - Consolidate knowledge

    It ONLY:
    - Records experiences
    - Stores experiences
    - Retrieves experiences
    """

    def __init__(self):
        """Initialize experience collector."""
        self._experiences: dict[str, Experience] = {}
        self._by_session: dict[str, list[str]] = {}
        self._by_outcome: dict[str, list[str]] = {}

    def record(
        self,
        session_id: str,
        context: dict,
        action: str,
        result: Any,
        outcome: str,
        confidence: float = 0.5,
        tags: list[str] | None = None,
    ) -> Experience:
        """Record an experience.

        Args:
            session_id: Session ID.
            context: Context data.
            action: Action taken.
            result: Result of action.
            outcome: Outcome ("success", "failure", "partial").
            confidence: Confidence in the experience.
            tags: Optional tags.

        Returns:
            Recorded experience.
        """
        experience_id = f"exp_{uuid.uuid4().hex[:16]}"

        experience = Experience(
            experience_id=experience_id,
            session_id=session_id,
            context=context,
            action=action,
            result=result,
            outcome=outcome,
            confidence=confidence,
            tags=tags or [],
        )

        self._experiences[experience_id] = experience

        # Index by session
        if session_id not in self._by_session:
            self._by_session[session_id] = []
        self._by_session[session_id].append(experience_id)

        # Index by outcome
        if outcome not in self._by_outcome:
            self._by_outcome[outcome] = []
        self._by_outcome[outcome].append(experience_id)

        return experience

    def get(self, experience_id: str) -> Experience | None:
        """Get experience by ID.

        Args:
            experience_id: Experience ID.

        Returns:
            Experience or None.
        """
        return self._experiences.get(experience_id)

    def get_by_session(self, session_id: str) -> list[Experience]:
        """Get experiences by session.

        Args:
            session_id: Session ID.

        Returns:
            List of experiences.
        """
        exp_ids = self._by_session.get(session_id, [])
        return [self._experiences[eid] for eid in exp_ids if eid in self._experiences]

    def get_by_outcome(self, outcome: str) -> list[Experience]:
        """Get experiences by outcome.

        Args:
            outcome: Outcome type.

        Returns:
            List of experiences.
        """
        exp_ids = self._by_outcome.get(outcome, [])
        return [self._experiences[eid] for eid in exp_ids if eid in self._experiences]

    def get_all(self) -> list[Experience]:
        """Get all experiences.

        Returns:
            List of all experiences.
        """
        return list(self._experiences.values())

    def get_count(self) -> int:
        """Get total experience count.

        Returns:
            Number of experiences.
        """
        return len(self._experiences)


# Global experience collector
_experience_collector: ExperienceCollector | None = None
_collector_lock = __import__("threading").Lock()


def get_experience_collector() -> ExperienceCollector:
    """Get the global experience collector."""
    global _experience_collector
    with _collector_lock:
        if _experience_collector is None:
            _experience_collector = ExperienceCollector()
        return _experience_collector


def reset_experience_collector() -> None:
    """Reset the global experience collector."""
    global _experience_collector
    with _collector_lock:
        _experience_collector = None
