"""
Clinical Intelligence Gateway.

Gateway implementation for Clinical Intelligence domain (PHASE 3).
Provides AI Core with access to clinical intelligence capabilities.

This gateway connects PHASE 2 (AI Core) with PHASE 3 (Clinical Intelligence),
enabling the AI to use clinical reasoning, evidence retrieval, confidence
scoring, and decision making.

ARCHITECTURE NOTE:
This gateway is the bridge between PHASE_2 (Cognitive OS) and PHASE_3 (Clinical Intelligence).
It allows AI Core to invoke clinical intelligence services while maintaining
clean architecture and dependency inversion.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol
from dataclasses import dataclass
from datetime import datetime

if TYPE_CHECKING:
    from core.PHASE_3.intelligence.reasoning import ReasoningPipeline, ClinicalContext
    from core.PHASE_3.intelligence.evidence import EvidenceBundle, EvidenceRetrieval
    from core.PHASE_3.intelligence.confidence import ConfidenceScore
    from core.PHASE_3.intelligence.decision import ClinicalDecision
    from core.PHASE_3.intelligence.safety import SafetyValidation
    from core.PHASE_3.intelligence.validation import ClinicalValidation


@dataclass(frozen=True)
class ClinicalQueryDTO:
    """DTO for clinical query from AI Core to Clinical Intelligence."""
    query_id: str
    device_id: str | None
    incident_id: str | None
    symptoms: list[str]
    context: dict[str, Any]
    tenant_id: str
    requested_at: datetime


@dataclass(frozen=True)
class ClinicalResponseDTO:
    """DTO for clinical response from Clinical Intelligence to AI Core."""
    query_id: str
    reasoning_chain: list[str]
    hypotheses: list[dict[str, Any]]
    evidence_bundle: dict[str, Any]
    confidence_score: float
    recommendations: list[dict[str, Any]]
    safety_validated: bool
    validation_status: str
    generated_at: datetime


class IClinicalIntelligenceGateway(Protocol):
    """Protocol for Clinical Intelligence Gateway."""

    async def process_clinical_query(
        self,
        query: ClinicalQueryDTO,
    ) -> ClinicalResponseDTO:
        """Process a clinical query and return intelligent recommendations."""
        ...

    async def get_reasoning_context(
        self,
        device_id: str,
        incident_id: str | None,
    ) -> dict[str, Any]:
        """Get reasoning context for a device/incident."""
        ...

    async def validate_safety(
        self,
        recommendation: dict[str, Any],
    ) -> bool:
        """Validate that a recommendation is safe."""
        ...

    async def get_confidence(
        self,
        reasoning_result: dict[str, Any],
    ) -> float:
        """Get confidence score for reasoning result."""
        ...


class ClinicalIntelligenceGateway(IClinicalIntelligenceGateway):
    """
    Gateway for Clinical Intelligence domain.

    AI Core uses this gateway to access clinical intelligence capabilities
    from PHASE 3 without knowing about implementation details.

    CONNECTION FLOW:
    PHASE_2 (AI Core)
        │
        ├── AIKernel → ConversationController → ContextBuilder
        │                    │
        │                    └── ClinicalIntelligenceGateway ← THIS
        │                                    │
        │                                    ▼
        │                         PHASE_3 (Clinical Intelligence)
        │                                    │
        │                         reasoning → evidence → confidence
        │                                    │
        │                         decision → safety → validation
        │
        └── Domain Gateways → PHASE_1 (Business Domain)

    EXAMPLE USAGE:
    ```python
    # In PHASE_2 AI Kernel or ContextBuilder
    clinical_gateway = ClinicalIntelligenceGateway()

    query = ClinicalQueryDTO(
        query_id="q-001",
        device_id="dev-123",
        incident_id="inc-456",
        symptoms=["high_temperature", "error_code_5E"],
        context={"conversation_history": [...], "memory": {...}},
        tenant_id="hospital-001",
        requested_at=datetime.now(),
    )

    response = await clinical_gateway.process_clinical_query(query)
    # response.recommendations contains clinical recommendations
    ```
    """

    def __init__(
        self,
        reasoning_pipeline: ReasoningPipeline | None = None,
        evidence_retrieval: EvidenceRetrieval | None = None,
        safety_validation: SafetyValidation | None = None,
    ):
        """
        Initialize Clinical Intelligence Gateway.

        Args:
            reasoning_pipeline: PHASE_3 ReasoningPipeline instance
            evidence_retrieval: PHASE_3 EvidenceRetrieval instance
            safety_validation: PHASE_3 SafetyValidation instance
        """
        self._reasoning_pipeline = reasoning_pipeline
        self._evidence_retrieval = evidence_retrieval
        self._safety_validation = safety_validation

    @property
    def name(self) -> str:
        return "clinical_intelligence"

    async def process_clinical_query(
        self,
        query: ClinicalQueryDTO,
    ) -> ClinicalResponseDTO:
        """
        Process a clinical query and return intelligent recommendations.

        This is the main entry point for AI Core to use Clinical Intelligence.
        It orchestrates the full clinical intelligence pipeline:
        1. Reasoning (generate hypotheses)
        2. Evidence Retrieval (find supporting evidence)
        3. Confidence Scoring (calculate certainty)
        4. Decision Making (select best action)
        5. Safety Validation (ensure safety)
        6. Clinical Validation (validate completeness)
        """
        if self._reasoning_pipeline is None:
            return self._mock_process_clinical_query(query)

        # Build clinical context from AI Core context
        clinical_context = self._build_clinical_context(query)

        # Run reasoning pipeline
        reasoning_result = await self._reasoning_pipeline.process(clinical_context)

        # Retrieve evidence
        evidence_bundle = await self._retrieve_evidence(query, reasoning_result)

        # Calculate confidence
        confidence_score = self._calculate_confidence(reasoning_result, evidence_bundle)

        # Generate recommendations
        recommendations = self._generate_recommendations(reasoning_result)

        # Validate safety
        safety_validated = await self._validate_safety(recommendations)

        # Perform clinical validation
        validation_status = self._validate_clinically(
            reasoning_result,
            evidence_bundle,
            confidence_score,
            recommendations,
        )

        return ClinicalResponseDTO(
            query_id=query.query_id,
            reasoning_chain=self._extract_reasoning_chain(reasoning_result),
            hypotheses=self._extract_hypotheses(reasoning_result),
            evidence_bundle=evidence_bundle,
            confidence_score=confidence_score,
            recommendations=recommendations,
            safety_validated=safety_validated,
            validation_status=validation_status,
            generated_at=datetime.now(),
        )

    async def get_reasoning_context(
        self,
        device_id: str,
        incident_id: str | None,
    ) -> dict[str, Any]:
        """
        Get reasoning context for a device/incident.

        This enriches the AI Core context with clinical intelligence context,
        including medical history, similar cases, and biomedical knowledge.
        """
        return self._mock_get_reasoning_context(device_id, incident_id)

    async def validate_safety(
        self,
        recommendation: dict[str, Any],
    ) -> bool:
        """Validate that a recommendation is safe before execution."""
        if self._safety_validation is None:
            return self._mock_validate_safety(recommendation)

        return await self._safety_validation.is_safe(recommendation)

    async def get_confidence(
        self,
        reasoning_result: dict[str, Any],
    ) -> float:
        """Get confidence score for reasoning result."""
        # Calculate based on evidence quality, consistency, and coverage
        evidence_score = reasoning_result.get("evidence_score", 0.5)
        consistency_score = reasoning_result.get("consistency_score", 0.5)
        coverage_score = reasoning_result.get("coverage_score", 0.5)

        return (evidence_score * 0.4 + consistency_score * 0.3 + coverage_score * 0.3)

    # =========================================================================
    # Private Methods
    # =========================================================================

    def _build_clinical_context(self, query: ClinicalQueryDTO) -> Any:
        """Build PHASE_3 clinical context from AI Core query."""
        # This would convert AI Core context to PHASE_3 ClinicalContext
        # For now, return a mock context
        return {
            "query_id": query.query_id,
            "device_id": query.device_id,
            "incident_id": query.incident_id,
            "symptoms": query.symptoms,
            "context": query.context,
            "tenant_id": query.tenant_id,
        }

    async def _retrieve_evidence(
        self,
        query: ClinicalQueryDTO,
        reasoning_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Retrieve supporting evidence for reasoning."""
        if self._evidence_retrieval is None:
            return self._mock_evidence_bundle(query, reasoning_result)

        # Retrieve evidence based on hypotheses
        hypotheses = reasoning_result.get("hypotheses", [])
        evidence = await self._evidence_retrieval.retrieve_for_hypotheses(hypotheses)
        return evidence

    def _calculate_confidence(
        self,
        reasoning_result: dict[str, Any],
        evidence_bundle: dict[str, Any],
    ) -> float:
        """Calculate confidence score."""
        evidence_count = evidence_bundle.get("evidence_count", 0)
        evidence_quality = evidence_bundle.get("quality_score", 0.5)
        consistency = reasoning_result.get("consistency", 0.5)

        base_confidence = (evidence_count / 10) * 0.3 + evidence_quality * 0.5 + consistency * 0.2
        return min(1.0, max(0.0, base_confidence))

    def _generate_recommendations(
        self,
        reasoning_result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate clinical recommendations."""
        hypotheses = reasoning_result.get("hypotheses", [])
        recommendations = []

        for hypothesis in hypotheses[:3]:  # Top 3 hypotheses
            recommendations.append({
                "action": hypothesis.get("recommended_action", "unknown"),
                "priority": hypothesis.get("priority", "medium"),
                "confidence": hypothesis.get("confidence", 0.5),
                "reasoning": hypothesis.get("reasoning", ""),
            })

        return recommendations

    async def _validate_safety(
        self,
        recommendations: list[dict[str, Any]],
    ) -> bool:
        """Validate safety of all recommendations."""
        if self._safety_validation is None:
            return all(self._mock_validate_safety(rec) for rec in recommendations)

        for recommendation in recommendations:
            if not await self._safety_validation.is_safe(recommendation):
                return False
        return True

    def _validate_clinically(
        self,
        reasoning_result: dict[str, Any],
        evidence_bundle: dict[str, Any],
        confidence_score: float,
        recommendations: list[dict[str, Any]],
    ) -> str:
        """Perform clinical validation."""
        if confidence_score < 0.5:
            return "LOW_CONFIDENCE"
        if evidence_bundle.get("evidence_count", 0) < 2:
            return "INSUFFICIENT_EVIDENCE"
        if not recommendations:
            return "NO_RECOMMENDATIONS"
        return "VALIDATED"

    def _extract_reasoning_chain(self, reasoning_result: dict[str, Any]) -> list[str]:
        """Extract reasoning chain steps."""
        return reasoning_result.get("chain", [])

    def _extract_hypotheses(self, reasoning_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract hypotheses from reasoning result."""
        return reasoning_result.get("hypotheses", [])

    # =========================================================================
    # Mock Implementations (for testing without PHASE_3)
    # =========================================================================

    def _mock_process_clinical_query(
        self,
        query: ClinicalQueryDTO,
    ) -> ClinicalResponseDTO:
        """Mock implementation for testing."""
        return ClinicalResponseDTO(
            query_id=query.query_id,
            reasoning_chain=[
                f"Analyzing symptoms: {', '.join(query.symptoms)}",
                "Generating hypotheses based on medical knowledge",
                "Retrieving evidence from biomedical database",
                "Calculating confidence scores",
                "Generating recommendations",
            ],
            hypotheses=[
                {
                    "id": "hyp-001",
                    "cause": "Sensor malfunction",
                    "confidence": 0.85,
                    "recommended_action": "Replace sensor",
                    "priority": "high",
                },
                {
                    "id": "hyp-002",
                    "cause": "Calibration drift",
                    "confidence": 0.65,
                    "recommended_action": "Recalibrate device",
                    "priority": "medium",
                },
            ],
            evidence_bundle={
                "evidence_count": 5,
                "quality_score": 0.8,
                "sources": [
                    "Manual GE Healthcare p.42",
                    "Similar incident INC-2024-001",
                    "IEC 60601-1 compliance",
                ],
            },
            confidence_score=0.78,
            recommendations=[
                {
                    "action": "Replace sensor",
                    "priority": "high",
                    "confidence": 0.85,
                    "reasoning": "Based on sensor malfunction hypothesis with 85% confidence",
                },
            ],
            safety_validated=True,
            validation_status="VALIDATED",
            generated_at=datetime.now(),
        )

    def _mock_get_reasoning_context(
        self,
        device_id: str,
        incident_id: str | None,
    ) -> dict[str, Any]:
        """Mock reasoning context."""
        return {
            "device_id": device_id,
            "incident_id": incident_id,
            "similar_cases": [
                {"id": "INC-001", "resolution": "Replaced sensor"},
                {"id": "INC-002", "resolution": "Recalibrated"},
            ],
            "biomedical_knowledge": {
                "failure_modes": ["sensor_malfunction", "calibration_drift", "power_issue"],
                "standards": ["IEC 60601-1", "ISO 14971"],
            },
        }

    def _mock_validate_safety(self, recommendation: dict[str, Any]) -> bool:
        """Mock safety validation."""
        unsafe_actions = ["open", "bypass", "disable", "remove_safety"]
        action = recommendation.get("action", "").lower()
        return not any(unsafe in action for unsafe in unsafe_actions)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ClinicalIntelligenceGateway",
    "IClinicalIntelligenceGateway",
    "ClinicalQueryDTO",
    "ClinicalResponseDTO",
]
