"""Type definitions for EREN Cognitive Learning Platform.

Provides comprehensive type definitions for learning operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Learning Types
# =============================================================================


class LearningType(str, Enum):
    """Type of learning."""

    SUPERVISED = "supervised"
    REINFORCEMENT = "reinforcement"
    EXPERIENCE_BASED = "experience_based"
    RULE_EXTRACTION = "rule_extraction"
    CASE_BASED = "case_based"
    CONTINUOUS = "continuous_learning"
    HUMAN_FEEDBACK = "human_feedback"
    CLINICAL_VALIDATION = "clinical_validation"
    BIOMEDICAL_OPTIMIZATION = "biomedical_optimization"


class LearningStatus(str, Enum):
    """Status of learning."""

    IDLE = "idle"
    LEARNING = "learning"
    CONSOLIDATING = "consolidating"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Experience Types
# =============================================================================


@dataclass
class Experience:
    """An experience recorded for learning."""

    experience_id: str
    session_id: str

    # Content
    context: dict
    action: str
    result: Any
    outcome: str  # "success", "failure", "partial"

    # Metadata
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Feedback Types
# =============================================================================


class FeedbackType(str, Enum):
    """Type of feedback."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"


@dataclass
class Feedback:
    """Feedback for learning."""

    feedback_id: str
    experience_id: str

    # Content
    feedback_type: FeedbackType
    content: str
    rating: float = 0.5  # 0.0 to 1.0

    # Source
    source: str = "user"  # "user", "system", "clinical"

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Pattern Types
# =============================================================================


@dataclass
class Pattern:
    """A pattern discovered from experience."""

    pattern_id: str

    # Content
    description: str
    pattern_type: str  # "sequence", "correlation", "rule", "anomaly"

    # Evidence
    supporting_experiences: list[str] = field(default_factory=list)
    frequency: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.5

    # Metadata
    discovered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_verified: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Knowledge Types
# =============================================================================


class KnowledgeType(str, Enum):
    """Type of knowledge."""

    FACT = "fact"
    RULE = "rule"
    HEURISTIC = "heuristic"
    CASE = "case"
    METRIC = "metric"


@dataclass
class Knowledge:
    """Consolidated knowledge."""

    knowledge_id: str
    knowledge_type: KnowledgeType

    # Content
    content: str
    description: str

    # Source
    source_experiences: list[str] = field(default_factory=list)
    confidence: float = 0.5

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    usage_count: int = 0


# =============================================================================
# Learning Metrics
# =============================================================================


@dataclass
class LearningMetrics:
    """Metrics for learning process."""

    experiences_recorded: int = 0
    patterns_discovered: int = 0
    knowledge_consolidated: int = 0
    feedback_received: int = 0
    accuracy_improvement: float = 0.0
    avg_outcome_score: float = 0.0
