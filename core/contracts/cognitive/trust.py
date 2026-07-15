"""
Trust Capability Contract.

Philosophy: EREN expresses trust in sources.
Not all sources are equal - EREN must evaluate and communicate trust.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Types
# =============================================================================


class TrustLevel(Enum):
    """Trust level scale.

    Based on evidence quality and source reliability.
    """

    HIGH = "high"  # 80-100% - Well-established, validated
    MODERATE = "moderate"  # 50-79% - Reasonable, some evidence
    LOW = "low"  # 20-49% - Limited evidence, uncertain
    UNCERTAIN = "uncertain"  # <20% - Insufficient evidence


class TrustSourceType(Enum):
    """Types of trust sources."""

    PEER_REVIEWED = "peer_reviewed"  # Published research
    CLINICAL_GUIDELINE = "clinical_guideline"  # AHA, ESC, etc.
    MANUFACTURER = "manufacturer"  # Device/system documentation
    INSTITUTIONAL = "institutional"  # Hospital protocols
    EXPERT_CONSENSUS = "expert_consensus"  # Clinical experts
    EMERGING = "emerging"  # New evidence, not validated
    UNVERIFIED = "unverified"  # Not validated
    UNKNOWN = "unknown"


class EvidenceType(Enum):
    """Types of evidence for trust evaluation."""

    RESEARCH_STUDY = "research_study"
    CLINICAL_GUIDELINE = "clinical_guideline"
    MANUFACTURER_SPEC = "manufacturer_spec"
    INSTITUTIONAL_PROTOCOL = "institutional_protocol"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"
    DEVICE_READING = "device_reading"
    SENSOR_DATA = "sensor_data"
    PATIENT_HISTORY = "patient_history"
    SIMILAR_CASE = "similar_case"
    REASONING_INFERENCE = "reasoning_inference"


@dataclass(frozen=True)
class TrustScore:
    """Trust evaluation result.

    EREN Philosophy: EREN measures and expresses uncertainty.
    Every trust evaluation includes confidence and factors.
    """

    # Trust level (categorical)
    level: TrustLevel

    # Trust score (numeric, 0.0 to 1.0)
    score: float  # 0.0 = no trust, 1.0 = full trust

    # Confidence in this evaluation (0.0 to 1.0)
    confidence: float

    # Factors that contributed to this evaluation
    factors: tuple[str, ...]

    # Evidence supporting this evaluation
    supporting_evidence: tuple[str, ...]

    # Contradicting evidence (if any)
    contradicting_evidence: tuple[str, ...]

    # Trust dimensions
    dimensions: tuple[tuple[str, float], ...] = field(
        default_factory=tuple
    )  # (dimension_name, score)

    # Validity
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    source_id: str | None = None

    @property
    def is_high_trust(self) -> bool:
        """Check if this is high trust."""
        return self.level == TrustLevel.HIGH

    @property
    def is_expired(self) -> bool:
        """Check if this trust score has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    @property
    def reliability(self) -> float:
        """Calculate reliability (score * confidence).

        This combines trust level with confidence in the evaluation.
        """
        return self.score * self.confidence


@dataclass(frozen=True)
class TrustContext:
    """Context for trust evaluation.

    Provides additional information for trust assessment.
    """

    # Source identification
    source_id: str
    source_type: TrustSourceType

    # Temporal factors
    publication_date: datetime | None = None
    last_updated: datetime | None = None
    review_date: datetime | None = None

    # Validation factors
    validation_count: int = 0  # Times this has been validated
    conflict_count: int = 0  # Times conflicts were found
    usage_count: int = 0  # Times successfully used

    # Relevance
    relevance_score: float | None = None  # 0.0 to 1.0
    specialty_match: float | None = None  # 0.0 to 1.0

    # External factors
    jurisdiction: str | None = None  # Geographic validity
    institutional_endorsement: bool = False

    metadata: tuple[tuple[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TrustEvaluation:
    """Complete trust evaluation with reasoning."""

    evaluation_id: str
    source_id: str
    source_type: TrustSourceType

    # Results
    trust_score: TrustScore
    primary_factors: tuple[str, ...]  # Top factors for trust

    # Method
    evaluation_method: str  # How trust was determined
    models_used: tuple[str, ...] = field(default_factory=tuple)

    # Temporal
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None

    # Comparisons
    similar_sources: tuple[str, ...] = field(default_factory=tuple)  # Similar high-trust sources
    conflicting_sources: tuple[str, ...] = field(default_factory=tuple)  # Known conflicts


@dataclass(frozen=True)
class TrustHistory:
    """Historical trust evaluation for a source."""

    source_id: str
    evaluations: tuple[TrustEvaluation, ...]
    average_score: float
    trend: str  # "increasing", "stable", "decreasing"
    last_evaluation: datetime


# =============================================================================
# Provider Interface
# =============================================================================


class TrustProvider(Protocol):
    """Contract for trust evaluation services.

    Philosophy: EREN expresses trust in sources.
    Every evidence, source, and device must have trust evaluation.

    Trust affects:
    - Which evidence is weighted heavily in reasoning
    - How confident EREN is in conclusions
    - How to present recommendations to users
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def evaluate_source_trust(
        self,
        source_id: str,
        source_type: TrustSourceType,
        context: TrustContext | None = None,
    ) -> TrustScore:
        """Evaluate trust in a source.

        Args:
            source_id: Identifier of the source
            source_type: Type of source
            context: Additional context for evaluation

        Returns:
            TrustScore with level and confidence
        """
        ...

    async def evaluate_evidence_trust(
        self,
        evidence_id: str,
        evidence_type: EvidenceType,
        context: TrustContext | None = None,
    ) -> TrustScore:
        """Evaluate trust in evidence.

        Args:
            evidence_id: Identifier of the evidence
            evidence_type: Type of evidence
            context: Additional context

        Returns:
            TrustScore for the evidence
        """
        ...

    async def evaluate_device_trust(
        self,
        device_id: str,
        last_calibration: datetime | None = None,
        maintenance_status: str | None = None,
    ) -> TrustScore:
        """Evaluate trust in a medical device.

        Args:
            device_id: Device identifier
            last_calibration: Last calibration date
            maintenance_status: Current maintenance status

        Returns:
            TrustScore for the device
        """
        ...

    async def evaluate_clinical_guideline_trust(
        self,
        guideline_id: str,
        issuing_body: str,
        version: str,
    ) -> TrustScore:
        """Evaluate trust in a clinical guideline.

        Args:
            guideline_id: Guideline identifier
            issuing_body: Organization that issued it
            version: Guideline version

        Returns:
            TrustScore for the guideline
        """
        ...

    async def get_trust_context(
        self,
        source_id: str,
    ) -> TrustContext | None:
        """Get trust context for a source.

        Args:
            source_id: Source identifier

        Returns:
            TrustContext if available, None otherwise
        """
        ...

    async def update_trust_context(
        self,
        source_id: str,
        validation_result: bool,
        usage_success: bool,
    ) -> bool:
        """Update trust context based on real-world usage.

        EREN Philosophy: EREN learns without compromising safety.
        Trust can evolve based on outcomes.

        Args:
            source_id: Source that was used
            validation_result: Did validation confirm trust?
            usage_success: Did usage result in good outcomes?

        Returns:
            True if context was updated
        """
        ...

    async def compare_sources(
        self,
        source_ids: list[str],
    ) -> tuple[TrustScore, ...]:
        """Compare trust levels of multiple sources.

        Args:
            source_ids: Sources to compare

        Returns:
            TrustScores ordered by trust level
        """
        ...

    async def get_trust_history(
        self,
        source_id: str,
        limit: int = 10,
    ) -> TrustHistory | None:
        """Get trust history for a source.

        Args:
            source_id: Source identifier
            limit: Maximum evaluations to return

        Returns:
            TrustHistory if available, None otherwise
        """
        ...

    async def reconcile_conflicts(
        self,
        evidence_ids: list[str],
    ) -> tuple[str, list[str]]:
        """Reconcile conflicting trust assessments.

        When multiple sources disagree, determine which to trust.

        Args:
            evidence_ids: Conflicting evidence IDs

        Returns:
            Tuple of (preferred_source_id, alternative_source_ids)
        """
        ...

    async def get_trusted_sources(
        self,
        source_type: TrustSourceType | None = None,
        min_trust_level: TrustLevel = TrustLevel.MODERATE,
        limit: int = 10,
    ) -> tuple[str, ...]:
        """Get list of trusted sources.

        Args:
            source_type: Filter by source type
            min_trust_level: Minimum trust level
            limit: Maximum sources to return

        Returns:
            Tuple of trusted source IDs
        """
        ...


# =============================================================================
# Trust Evaluation Factors
# =============================================================================


@dataclass(frozen=True)
class TrustFactor:
    """A factor that contributes to trust evaluation."""

    factor_id: str
    name: str
    description: str
    weight: float  # Importance in evaluation (0.0 to 1.0)
    direction: str  # "positive" or "negative"


@dataclass(frozen=True)
class TrustFactors:
    """Standard trust evaluation factors."""

    # Positive factors (increase trust)
    PUBLICATION_IN_PRESSED_REVIEWED = TrustFactor(
        factor_id="peer_reviewed",
        name="Peer Reviewed",
        description="Published in peer-reviewed journal",
        weight=0.3,
        direction="positive",
    )

    CLINICAL_GUIDELINE_ENDORSED = TrustFactor(
        factor_id="guideline_endorsed",
        name="Guideline Endorsed",
        description="Endorsed by major clinical organization",
        weight=0.25,
        direction="positive",
    )

    RECENT_UPDATE = TrustFactor(
        factor_id="recent_update",
        name="Recently Updated",
        description="Evidence has been updated recently",
        weight=0.15,
        direction="positive",
    )

    MULTIPLE_VALIDATIONS = TrustFactor(
        factor_id="multi_validated",
        name="Multiple Validations",
        description="Validated by multiple independent sources",
        weight=0.2,
        direction="positive",
    )

    INSTITUTIONAL_USE = TrustFactor(
        factor_id="institutional_use",
        name="Institutional Use",
        description="In use at multiple institutions",
        weight=0.1,
        direction="positive",
    )

    # Negative factors (decrease trust)
    OUTDATED = TrustFactor(
        factor_id="outdated",
        name="Outdated",
        description="Evidence has not been updated in extended period",
        weight=-0.2,
        direction="negative",
    )

    CONFLICTING_EVIDENCE = TrustFactor(
        factor_id="conflicting_evidence",
        name="Conflicting Evidence",
        description="Contradicted by other high-quality sources",
        weight=-0.3,
        direction="negative",
    )

    SINGLE_SOURCE = TrustFactor(
        factor_id="single_source",
        name="Single Source",
        description="Only one source, not independently verified",
        weight=-0.15,
        direction="negative",
    )

    UNVERIFIED = TrustFactor(
        factor_id="unverified",
        name="Unverified",
        description="Source has not been independently verified",
        weight=-0.25,
        direction="negative",
    )


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class TrustEvent:
    """Base class for trust events."""

    event_id: str
    source_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class TrustEvaluated(TrustEvent):
    """Fired when trust is evaluated."""

    trust_score: TrustScore
    evaluation_method: str


@dataclass(frozen=True)
class TrustUpdated(TrustEvent):
    """Fired when trust is updated based on outcomes."""

    previous_score: float
    new_score: float
    reason: str


@dataclass(frozen=True)
class TrustConflictDetected(TrustEvent):
    """Fired when conflicting trust assessments are detected."""

    conflicting_sources: tuple[str, ...]
    resolution: str | None
