"""Clinical Decision Support System Engine."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from core.clinical.cdss import CDSSResult, EvidenceLevel, Recommendation, RecommendationPriority


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EvidenceLevel(str, Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"


@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    priority: RecommendationPriority
    evidence_level: EvidenceLevel
    confidence: float
    actions: list[str]


@dataclass
class CDSSResult:
    recommendations: list[Recommendation]
    confidence: float
    summary: str


class CDSSEngine:
    """
    Clinical Decision Support System Engine.
    
    Provides evidence-based recommendations for biomedical engineering decisions.
    """

    def __init__(self):
        self._knowledge_base: dict[str, list[dict[str, Any]]] = {}
        self._confidence_threshold = 0.6

    def add_knowledge(
        self,
        condition: str,
        recommendation: dict[str, Any],
        evidence_level: EvidenceLevel = EvidenceLevel.C,
    ) -> None:
        """Add a recommendation to the knowledge base."""
        if condition not in self._knowledge_base:
            self._knowledge_base[condition] = []
        recommendation["evidence_level"] = evidence_level
        self._knowledge_base[condition].append(recommendation)

    def get_recommendations(
        self,
        device_type: str,
        symptoms: list[str],
        device_context: dict[str, Any] | None = None,
    ) -> CDSSResult:
        """
        Generate clinical recommendations based on device type and symptoms.
        
        Args:
            device_type: Type of medical device
            symptoms: List of observed symptoms
            device_context: Additional device context (age, usage hours, etc.)
            
        Returns:
            CDSSResult with recommendations and confidence score
        """
        recommendations = []
        confidence_scores = []

        # Search knowledge base for matching conditions
        for symptom in symptoms:
            if symptom in self._knowledge_base:
                for kb_entry in self._knowledge_base[symptom]:
                    rec = self._create_recommendation(symptom, kb_entry, device_context)
                    if rec:
                        recommendations.append(rec)
                        confidence_scores.append(rec.confidence)

        # Apply rule-based reasoning for common patterns
        rule_recommendations = self._apply_rules(device_type, symptoms, device_context)
        recommendations.extend(rule_recommendations)
        
        for rec in rule_recommendations:
            confidence_scores.append(rec.confidence)

        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        # Generate summary
        summary = self._generate_summary(device_type, symptoms, recommendations)

        return CDSSResult(
            recommendations=recommendations,
            confidence=avg_confidence,
            summary=summary,
        )

    def _create_recommendation(
        self,
        condition: str,
        kb_entry: dict[str, Any],
        device_context: dict[str, Any] | None,
    ) -> Recommendation | None:
        """Create a recommendation from knowledge base entry."""
        confidence = kb_entry.get("confidence", 0.7)
        evidence_level = kb_entry.get("evidence_level", EvidenceLevel.C)

        # Adjust confidence based on device context
        if device_context:
            usage_hours = device_context.get("usage_hours", 0)
            if usage_hours > 10000:
                confidence *= 0.9
            age_years = device_context.get("age_years", 0)
            if age_years > 10:
                confidence *= 0.85

        if confidence < self._confidence_threshold:
            return None

        priority = self._determine_priority(
            kb_entry.get("severity", "medium"),
            evidence_level,
        )

        return Recommendation(
            id=f"rec-{condition}-{hash(kb_entry.get('title', ''))}",
            title=kb_entry.get("title", "Recommendation"),
            description=kb_entry.get("description", ""),
            priority=priority,
            evidence_level=evidence_level,
            confidence=confidence,
            actions=kb_entry.get("actions", []),
        )

    def _apply_rules(
        self,
        device_type: str,
        symptoms: list[str],
        device_context: dict[str, Any] | None,
    ) -> list[Recommendation]:
        """Apply rule-based reasoning for common patterns."""
        recommendations = []

        # Rule: Age-based maintenance
        if device_context:
            age_years = device_context.get("age_years", 0)
            if age_years > 7:
                recommendations.append(Recommendation(
                    id=f"rule-age-{device_type}",
                    title=f"Consider Lifecycle Replacement",
                    description=f"Device is {age_years} years old and may be approaching end of lifecycle.",
                    priority=RecommendationPriority.MEDIUM,
                    evidence_level=EvidenceLevel.B,
                    confidence=0.75,
                    actions=[
                        "Evaluate device against current technology standards",
                        "Review manufacturer support status",
                        "Prepare capital planning budget",
                    ],
                ))

            # Rule: Usage hour threshold
            usage_hours = device_context.get("usage_hours", 0)
            if usage_hours > 15000:
                recommendations.append(Recommendation(
                    id=f"rule-usage-{device_type}",
                    title="High Usage Inspection Required",
                    description=f"Device has exceeded 15,000 usage hours.",
                    priority=RecommendationPriority.HIGH,
                    evidence_level=EvidenceLevel.B,
                    confidence=0.85,
                    actions=[
                        "Schedule comprehensive preventive maintenance",
                        "Inspect wear-prone components",
                        "Review maintenance history",
                    ],
                ))

        # Rule: Critical device types
        critical_types = ["ventilator", "defibrillator", "infusion_pump", "monitor"]
        if any(ct in device_type.lower() for ct in critical_types):
            if symptoms:
                recommendations.append(Recommendation(
                    id=f"rule-critical-{device_type}",
                    title="Critical Device - Prioritized Attention",
                    description="This is a critical care device requiring immediate attention.",
                    priority=RecommendationPriority.HIGH,
                    evidence_level=EvidenceLevel.A,
                    confidence=0.95,
                    actions=[
                        "Escalate to senior biomedical engineer",
                        "Review manufacturer safety notices",
                        "Check for recalls",
                    ],
                ))

        return recommendations

    def _determine_priority(
        self,
        severity: str,
        evidence_level: EvidenceLevel,
    ) -> RecommendationPriority:
        """Determine recommendation priority based on severity and evidence."""
        severity_map = {
            "critical": RecommendationPriority.CRITICAL,
            "high": RecommendationPriority.HIGH,
            "medium": RecommendationPriority.MEDIUM,
            "low": RecommendationPriority.LOW,
        }
        base_priority = severity_map.get(severity.lower(), RecommendationPriority.MEDIUM)

        # Elevate priority for strong evidence
        if evidence_level == EvidenceLevel.A:
            if base_priority == RecommendationPriority.MEDIUM:
                return RecommendationPriority.HIGH
            elif base_priority == RecommendationPriority.LOW:
                return RecommendationPriority.MEDIUM

        return base_priority

    def _generate_summary(
        self,
        device_type: str,
        symptoms: list[str],
        recommendations: list[Recommendation],
    ) -> str:
        """Generate human-readable summary of recommendations."""
        if not recommendations:
            return f"No specific recommendations for {device_type} with symptoms: {', '.join(symptoms)}"

        critical = [r for r in recommendations if r.priority == RecommendationPriority.CRITICAL]
        high = [r for r in recommendations if r.priority == RecommendationPriority.HIGH]

        summary_parts = []
        if critical:
            summary_parts.append(f"{len(critical)} critical recommendation(s)")
        if high:
            summary_parts.append(f"{len(high)} high priority recommendation(s)")

        total = len(recommendations)
        avg_confidence = sum(r.confidence for r in recommendations) / total if total else 0

        return (
            f"Generated {total} recommendation(s) for {device_type}. "
            f"{', '.join(summary_parts) if summary_parts else 'All are medium or low priority.'} "
            f"Overall confidence: {avg_confidence:.0%}."
        )


# Global instance for convenience
_engine: CDSSEngine | None = None


def get_cdss_engine() -> CDSSEngine:
    """Get or create the global CDSS engine instance."""
    global _engine
    if _engine is None:
        _engine = CDSSEngine()
        _initialize_knowledge_base(_engine)
    return _engine


def _initialize_knowledge_base(engine: CDSSEngine) -> None:
    """Initialize the CDSS engine with default knowledge."""
    # Preventive maintenance rules
    engine.add_knowledge(
        condition="power_instability",
        recommendation={
            "title": "Power Supply Inspection",
            "description": "Device shows power instability symptoms.",
            "confidence": 0.85,
            "actions": [
                "Check power cable integrity",
                "Verify grounding",
                "Test UPS functionality",
                "Measure voltage fluctuations",
            ],
        },
        evidence_level=EvidenceLevel.A,
    )

    # Calibration drift
    engine.add_knowledge(
        condition="calibration_drift",
        recommendation={
            "title": "Full Calibration Required",
            "description": "Device calibration has drifted beyond acceptable limits.",
            "confidence": 0.90,
            "actions": [
                "Perform complete calibration procedure",
                "Document calibration results",
                "Verify against reference standards",
                "Update maintenance records",
            ],
        },
        evidence_level=EvidenceLevel.A,
    )

    # Temperature issues
    engine.add_knowledge(
        condition="overheating",
        recommendation={
            "title": "Cooling System Check",
            "description": "Device is experiencing thermal issues.",
            "confidence": 0.80,
            "actions": [
                "Clean air filters and vents",
                "Check cooling fans",
                "Verify ambient temperature",
                "Inspect thermal paste",
            ],
        },
        evidence_level=EvidenceLevel.B,
    )
