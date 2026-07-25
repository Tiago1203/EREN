"""
PHASE 7 - EPIC 0: HIPAA Risk Assessment

Evaluación de riesgos HIPAA:
- Risk Analysis
- Risk Management
- Risk Assessment Report
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    """Niveles de riesgo."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ThreatSource(str, Enum):
    """Fuentes de amenaza."""
    HACKER = "hacker"
    INSIDER = "insider"
    MALWARE = "malware"
    NATURAL = "natural"
    EQUIPMENT_FAILURE = "equipment_failure"
    HUMAN_ERROR = "human_error"
    DATA_BREACH = "data_breach"


class Vulnerability(str, Enum):
    """Vulnerabilidades."""
    WEAK_AUTH = "weak_authentication"
    UNENCRYPTED_DATA = "unencrypted_data"
    SHARED_ACCOUNTS = "shared_accounts"
    LACK_OF_AUDIT = "lack_of_audit_trails"
    UNPATCHED_SYSTEMS = "unpatched_systems"
    WEAK_ACCESS_CONTROL = "weak_access_control"
    NO_MFA = "no_multi_factor"
    INSECURE_TRANSMISSION = "insecure_transmission"


@dataclass
class RiskFactor:
    """Factor de riesgo."""
    likelihood: float          # 0.0 - 1.0
    impact: float             # 0.0 - 1.0
    controls_effectiveness: float  # 0.0 - 1.0


@dataclass
class Risk:
    """Riesgo identificado."""
    risk_id: str
    title: str
    description: str
    threat_source: ThreatSource
    vulnerabilities: list[Vulnerability]
    risk_level: RiskLevel
    likelihood: float
    impact: float
    residual_risk: float
    affected_systems: list[str] = field(default_factory=list)
    affected_data: list[str] = field(default_factory=list)
    mitigation: str = ""
    mitigation_effectiveness: float = 0.0
    owner: str = ""
    review_date: Optional[datetime] = None


@dataclass
class HIPAAAssessment:
    """Evaluación de riesgos HIPAA."""
    assessment_id: str
    assessment_date: datetime
    assessor: str
    scope: str

    # Risk metrics
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0

    # Coverage
    systems_covered: list[str] = field(default_factory=list)
    phi_flows_analyzed: int = 0

    # Results
    risks: list[Risk] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class HIPAARiskAssessment:
    """Herramienta de evaluación de riesgos HIPAA."""

    def __init__(self):
        self._assessments: list[HIPAAAssessment] = []

    def calculate_risk_score(
        self,
        likelihood: float,
        impact: float,
        controls_effectiveness: float,
    ) -> tuple[float, RiskLevel]:
        """Calcula score de riesgo."""
        residual = likelihood * impact * (1 - controls_effectiveness)
        score = residual * 100

        if score >= 75:
            level = RiskLevel.CRITICAL
        elif score >= 50:
            level = RiskLevel.HIGH
        elif score >= 25:
            level = RiskLevel.MEDIUM
        elif score >= 10:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.MINIMAL

        return score, level

    def identify_phi_risks(self) -> list[Risk]:
        """Identifica riesgos comunes de PHI."""
        risks = []

        # Unencrypted PHI at rest
        risks.append(Risk(
            risk_id="phi-risk-001",
            title="PHI sin encriptación en reposo",
            description="Datos de pacientes sin encriptación AES-256 almacenados",
            threat_source=ThreatSource.DATA_BREACH,
            vulnerabilities=[Vulnerability.UNENCRYPTED_DATA],
            likelihood=0.7,
            impact=0.9,
            risk_level="High",
            residual_risk=0.0,
            affected_data=["patient_records", "diagnoses", "treatments"],
            mitigation="Implementar encriptación AES-256 en base de datos",
        ))

        # Weak authentication
        risks.append(Risk(
            risk_id="phi-risk-002",
            title="Autenticación débil para acceso PHI",
            description="Sistema de autenticación sin MFA para acceso a datos clínicos",
            threat_source=ThreatSource.INSIDER,
            vulnerabilities=[Vulnerability.WEAK_AUTH, Vulnerability.NO_MFA],
            likelihood=0.5,
            impact=0.9,
            risk_level="High",
            residual_risk=0.0,
            affected_data=["patient_records", "lab_results"],
            mitigation="Implementar MFA obligatorio para acceso PHI",
        ))

        # Lack of audit
        risks.append(Risk(
            risk_id="phi-risk-003",
            title="Sin auditoría de acceso PHI",
            description="No se registran logs de acceso a información de pacientes",
            threat_source=ThreatSource.HACKER,
            vulnerabilities=[Vulnerability.LACK_OF_AUDIT],
            likelihood=0.3,
            impact=0.8,
            risk_level="Medium",
            residual_risk=0.0,
            affected_data=["all_phi"],
            mitigation="Implementar logging de auditoría HIPAA-compliant",
        ))

        return risks

    def conduct_assessment(
        self,
        assessor: str,
        scope: str,
        systems: list[str],
    ) -> HIPAAAssessment:
        """Conduce evaluación completa."""
        risks = self.identify_phi_risks()

        for risk in risks:
            score, level = self.calculate_risk_score(
                risk.likelihood, risk.impact, risk.mitigation_effectiveness
            )
            risk.residual_risk = score

        assessment = HIPAAAssessment(
            assessment_id=f"hipaa-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            assessment_date=datetime.utcnow(),
            assessor=assessor,
            scope=scope,
            systems_covered=systems,
            phi_flows_analyzed=len(systems),
            risks=risks,
            recommendations=self._generate_recommendations(risks),
        )

        for risk in risks:
            if risk.risk_level == RiskLevel.CRITICAL:
                assessment.critical_risks += 1
            elif risk.risk_level == RiskLevel.HIGH:
                assessment.high_risks += 1
            elif risk.risk_level == RiskLevel.MEDIUM:
                assessment.medium_risks += 1
            else:
                assessment.low_risks += 1

        self._assessments.append(assessment)
        return assessment

    def _generate_recommendations(self, risks: list[Risk]) -> list[str]:
        """Genera recomendaciones basadas en riesgos."""
        recommendations = []
        if any(r.threat_source == ThreatSource.DATA_BREACH for r in risks):
            recommendations.append("Implementar encriptación de datos en reposo")
        if any(Vulnerability.NO_MFA in r.vulnerabilities for r in risks):
            recommendations.append("Implementar autenticación multifactor")
        if any(Vulnerability.LACK_OF_AUDIT in r.vulnerabilities for r in risks):
            recommendations.append("Implementar sistema de auditoría de accesos")
        if any(Vulnerability.UNENCRYPTED_DATA in r.vulnerabilities for r in risks):
            recommendations.append("Rotar claves de encriptación periódicamente")
        return recommendations

    def get_latest_assessment(self) -> Optional[HIPAAAssessment]:
        """Obtiene última evaluación."""
        return self._assessments[-1] if self._assessments else None

    def get_assessment_trend(self) -> dict:
        """Obtiene tendencias de riesgo."""
        if len(self._assessments) < 2:
            return {"trend": "insufficient_data"}

        latest = self._assessments[-1]
        previous = self._assessments[-2]

        return {
            "latest_date": latest.assessment_date.isoformat(),
            "critical_risks_change": latest.critical_risks - previous.critical_risks,
            "high_risks_change": latest.high_risks - previous.high_risks,
            "total_risks_change": len(latest.risks) - len(previous.risks),
        }
