"""Knowledge Consolidation for EREN Cognitive Learning Platform.

Consolidates learned knowledge.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.learning.types import Knowledge, KnowledgeType, Pattern, Experience

if TYPE_CHECKING:
    pass


class KnowledgeConsolidator:
    """Consolidates learned knowledge.

    The Knowledge Consolidator does NOT:
    - Record experiences
    - Discover patterns
    - Analyze feedback

    It ONLY:
    - Consolidates patterns into knowledge
    - Updates existing knowledge
    - Manages knowledge lifecycle
    """

    def __init__(self):
        """Initialize knowledge consolidator."""
        self._knowledge: dict[str, Knowledge] = {}

    def consolidate(
        self,
        patterns: list[Pattern],
        experiences: list[Experience],
    ) -> list[Knowledge]:
        """Consolidate patterns into knowledge.

        Args:
            patterns: Patterns to consolidate.
            experiences: Related experiences.

        Returns:
            Consolidated knowledge.
        """
        knowledge_items = []

        for pattern in patterns:
            if pattern.confidence < 0.5:
                continue

            knowledge = self._pattern_to_knowledge(pattern, experiences)
            knowledge_items.append(knowledge)
            self._knowledge[knowledge.knowledge_id] = knowledge

        return knowledge_items

    def _pattern_to_knowledge(
        self,
        pattern: Pattern,
        experiences: list[Experience],
    ) -> Knowledge:
        """Convert pattern to knowledge.

        Args:
            pattern: Pattern to convert.
            experiences: Related experiences.

        Returns:
            Knowledge item.
        """
        # Determine knowledge type
        if pattern.pattern_type == "sequence":
            knowledge_type = KnowledgeType.RULE
        elif pattern.pattern_type == "correlation":
            knowledge_type = KnowledgeType.HEURISTIC
        else:
            knowledge_type = KnowledgeType.FACT

        # Get supporting experience IDs
        supporting_ids = []
        for exp in experiences:
            if exp.action in pattern.description or any(k in str(exp.context) for k in pattern.description.split()):
                supporting_ids.append(exp.experience_id)

        knowledge = Knowledge(
            knowledge_id=f"kn_{uuid.uuid4().hex[:16]}",
            knowledge_type=knowledge_type,
            content=pattern.description,
            description=f"Discovered {pattern.pattern_type}: {pattern.description}",
            source_experiences=supporting_ids[:10],  # Limit to 10
            confidence=pattern.confidence,
        )

        return knowledge

    def get(self, knowledge_id: str) -> Knowledge | None:
        """Get knowledge by ID."""
        return self._knowledge.get(knowledge_id)

    def get_all(self) -> list[Knowledge]:
        """Get all knowledge."""
        return list(self._knowledge.values())

    def get_by_type(self, knowledge_type: KnowledgeType) -> list[Knowledge]:
        """Get knowledge by type."""
        return [k for k in self._knowledge.values() if k.knowledge_type == knowledge_type]

    def update(self, knowledge_id: str, **updates) -> bool:
        """Update knowledge.

        Args:
            knowledge_id: Knowledge ID.
            updates: Fields to update.

        Returns:
            True if updated.
        """
        knowledge = self._knowledge.get(knowledge_id)
        if not knowledge:
            return False

        if "content" in updates:
            knowledge.content = updates["content"]
        if "confidence" in updates:
            knowledge.confidence = updates["confidence"]
        if "description" in updates:
            knowledge.description = updates["description"]

        knowledge.updated_at = datetime.now(timezone.utc)
        knowledge.usage_count += 1

        return True

    def increment_usage(self, knowledge_id: str) -> bool:
        """Increment knowledge usage count.

        Args:
            knowledge_id: Knowledge ID.

        Returns:
            True if incremented.
        """
        knowledge = self._knowledge.get(knowledge_id)
        if not knowledge:
            return False

        knowledge.usage_count += 1
        return True


# Global knowledge consolidator
_knowledge_consolidator: KnowledgeConsolidator | None = None
_consolidator_lock = __import__("threading").Lock()


def get_knowledge_consolidator() -> KnowledgeConsolidator:
    """Get the global knowledge consolidator."""
    global _knowledge_consolidator
    with _consolidator_lock:
        if _knowledge_consolidator is None:
            _knowledge_consolidator = KnowledgeConsolidator()
        return _knowledge_consolidator


def reset_knowledge_consolidator() -> None:
    """Reset the global knowledge consolidator."""
    global _knowledge_consolidator
    with _consolidator_lock:
        _knowledge_consolidator = None
