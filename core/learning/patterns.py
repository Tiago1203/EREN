"""Pattern Discovery for EREN Cognitive Learning Platform.

Discovers patterns from experiences.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.learning.types import Experience, Pattern

if TYPE_CHECKING:
    pass


class PatternDiscovery:
    """Discovers patterns from experiences.

    The Pattern Discovery does NOT:
    - Record experiences
    - Analyze feedback
    - Consolidate knowledge

    It ONLY:
    - Discovers patterns
    - Analyzes sequences
    - Finds correlations
    """

    def __init__(self):
        """Initialize pattern discovery."""
        self._patterns: dict[str, Pattern] = {}

    def discover(
        self,
        experiences: list[Experience],
        min_frequency: float = 0.1,
    ) -> list[Pattern]:
        """Discover patterns from experiences.

        Args:
            experiences: Experiences to analyze.
            min_frequency: Minimum frequency threshold.

        Returns:
            Discovered patterns.
        """
        patterns = []

        # Discover sequence patterns
        sequence_patterns = self._discover_sequences(experiences)
        patterns.extend(sequence_patterns)

        # Discover correlation patterns
        correlation_patterns = self._discover_correlations(experiences)
        patterns.extend(correlation_patterns)

        # Filter by frequency
        patterns = [p for p in patterns if p.frequency >= min_frequency]

        return patterns

    def _discover_sequences(self, experiences: list[Experience]) -> list[Pattern]:
        """Discover sequence patterns."""
        patterns = []

        # Group by session
        session_experiences: dict[str, list[Experience]] = {}
        for exp in experiences:
            if exp.session_id not in session_experiences:
                session_experiences[exp.session_id] = []
            session_experiences[exp.session_id].append(exp)

        # Find common action sequences
        action_sequences: dict[str, int] = {}
        for session_id, exps in session_experiences.items():
            sorted_exps = sorted(exps, key=lambda e: e.created_at)
            actions = tuple(exp.action for exp in sorted_exps[:3])

            if len(actions) >= 2:
                key = " -> ".join(actions)
                action_sequences[key] = action_sequences.get(key, 0) + 1

        # Create patterns
        for seq, count in action_sequences.items():
            if count >= 2:
                frequency = count / len(session_experiences)
                pattern = Pattern(
                    pattern_id=f"pat_{uuid.uuid4().hex[:16]}",
                    description=f"Action sequence: {seq}",
                    pattern_type="sequence",
                    frequency=frequency,
                    confidence=min(1.0, count * 0.3),
                )
                patterns.append(pattern)
                self._patterns[pattern.pattern_id] = pattern

        return patterns

    def _discover_correlations(self, experiences: list[Experience]) -> list[Pattern]:
        """Discover correlation patterns."""
        patterns = []

        # Group by outcome
        outcomes: dict[str, list[Experience]] = {}
        for exp in experiences:
            if exp.outcome not in outcomes:
                outcomes[exp.outcome] = []
            outcomes[exp.outcome].append(exp)

        # Find context correlations
        for outcome, exps in outcomes.items():
            if len(exps) < 2:
                continue

            context_keys: dict[str, int] = {}
            for exp in exps:
                for key in exp.context.keys():
                    context_keys[key] = context_keys.get(key, 0) + 1

            for key, count in context_keys.items():
                if count >= len(exps) * 0.5:
                    pattern = Pattern(
                        pattern_id=f"pat_{uuid.uuid4().hex[:16]}",
                        description=f"Context '{key}' correlates with {outcome}",
                        pattern_type="correlation",
                        frequency=count / len(exps),
                        confidence=min(1.0, count * 0.2),
                    )
                    patterns.append(pattern)
                    self._patterns[pattern.pattern_id] = pattern

        return patterns

    def get(self, pattern_id: str) -> Pattern | None:
        """Get pattern by ID."""
        return self._patterns.get(pattern_id)

    def get_all(self) -> list[Pattern]:
        """Get all patterns."""
        return list(self._patterns.values())

    def verify_pattern(self, pattern_id: str, new_experiences: list[Experience]) -> float:
        """Verify a pattern with new experiences."""
        pattern = self._patterns.get(pattern_id)
        if not pattern:
            return 0.0

        matches = 0
        for exp in new_experiences:
            if pattern.pattern_type == "sequence":
                if exp.action in pattern.description:
                    matches += 1
            elif pattern.pattern_type == "correlation":
                if any(k in exp.context for k in pattern.description.split()):
                    matches += 1

        if not new_experiences:
            return 0.0

        return matches / len(new_experiences)


# Global pattern discovery
_pattern_discovery: PatternDiscovery | None = None
_pattern_lock = __import__("threading").Lock()


def get_pattern_discovery() -> PatternDiscovery:
    """Get the global pattern discovery."""
    global _pattern_discovery
    with _pattern_lock:
        if _pattern_discovery is None:
            _pattern_discovery = PatternDiscovery()
        return _pattern_discovery


def reset_pattern_discovery() -> None:
    """Reset the global pattern discovery."""
    global _pattern_discovery
    with _pattern_lock:
        _pattern_discovery = None
