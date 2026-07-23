"""
Risk Assessor Module

Exports for risk assessment.
"""

from enum import Enum


class RiskLevel(Enum):
    """Risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskCategory(Enum):
    """Categories of risk."""
    CLINICAL = "clinical"
    SAFETY = "safety"
    OPERATIONAL = "operational"
    EVIDENCE = "evidence"
    COMPLIANCE = "compliance"


@dataclass
class RiskFactor:
    """Individual risk factor."""
    factor_id: str
    name: str
    description: str
    category: RiskCategory
    probability: float
    severity: float
    detectability: float = 0.5
    
    @property
    def risk_score(self) -> float:
        """Calculate risk score."""
        return self.probability * self.severity * (1 - self.detectability * 0.5)


@dataclass
class RiskAssessment:
    """Complete risk assessment."""
    overall_risk: RiskLevel
    risk_factors: list[RiskFactor]
    recommendations: list[str]
    immediate_actions: list[str]


class RiskAssessor:
    """Assesses risk for clinical recommendations."""
    
    def __init__(self):
        self._safety_keywords = {
            "immediately", "stop", "remove", "discontinue",
            "emergency", "critical", "urgent", "life-threatening"
        }
    
    def assess(
        self,
        hypothesis: dict,
        evidence_bundle: dict,
        recommendation: str,
    ) -> RiskAssessment:
        """Assess risk for a recommendation."""
        
        risk_factors = []
        
        # Clinical risk factors
        severity = hypothesis.get("severity", "medium")
        if severity in ["high", "critical"]:
            risk_factors.append(RiskFactor(
                factor_id="clinical_high_severity",
                name="High Severity Condition",
                description="Recommendation involves high-severity condition",
                category=RiskCategory.CLINICAL,
                probability=0.8,
                severity=0.9,
                detectability=0.7,
            ))
        
        # Safety risk factors
        if self._has_safety_implications(recommendation):
            risk_factors.append(RiskFactor(
                factor_id="safety_implications",
                name="Safety Implications",
                description="Recommendation has safety implications",
                category=RiskCategory.SAFETY,
                probability=0.6,
                severity=0.95,
                detectability=0.8,
            ))
        
        # Evidence quality risk
        confidence = evidence_bundle.get("summary", {}).get("overall_confidence", 1.0)
        if confidence < 0.5:
            risk_factors.append(RiskFactor(
                factor_id="low_evidence_confidence",
                name="Low Evidence Confidence",
                description="Recommendation based on low-confidence evidence",
                category=RiskCategory.EVIDENCE,
                probability=0.7,
                severity=0.7,
                detectability=0.6,
            ))
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, overall_risk)
        
        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            recommendations=recommendations["monitoring"],
            immediate_actions=recommendations["immediate"],
        )
    
    def _calculate_overall_risk(self, factors: list[RiskFactor]) -> RiskLevel:
        """Calculate overall risk level."""
        if not factors:
            return RiskLevel.LOW
        
        max_score = max(f.risk_score for f in factors)
        
        if max_score >= 0.7:
            return RiskLevel.CRITICAL
        elif max_score >= 0.5:
            return RiskLevel.HIGH
        elif max_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _has_safety_implications(self, recommendation: str) -> bool:
        """Check if recommendation has safety implications."""
        return any(
            kw in recommendation.lower() 
            for kw in self._safety_keywords
        )
    
    def _generate_recommendations(
        self,
        factors: list[RiskFactor],
        overall_risk: RiskLevel,
    ) -> dict[str, list[str]]:
        """Generate risk-based recommendations."""
        immediate = []
        monitoring = []
        
        for factor in factors:
            if factor.risk_score >= 0.6:
                immediate.append(
                    f"Address {factor.name}: {factor.description}"
                )
            else:
                monitoring.append(f"Monitor {factor.name}")
        
        if overall_risk == RiskLevel.CRITICAL:
            immediate.append("Escalate to supervisor immediately")
            monitoring.append("Implement continuous monitoring")
        elif overall_risk == RiskLevel.HIGH:
            monitoring.append("Review within 24 hours")
        
        return {
            "immediate": immediate,
            "monitoring": monitoring,
        }


__all__ = [
    "RiskLevel",
    "RiskCategory",
    "RiskFactor",
    "RiskAssessment",
    "RiskAssessor",
]
