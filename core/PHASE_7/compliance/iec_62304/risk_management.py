"""
PHASE 7 - EPIC 0: IEC 62304 Risk Management

Gestión de riesgos de software médico:
- FMEA/FMEA integration
- Risk Acceptability Criteria
- Software Risk Control Measures
- Risk Management File
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskAcceptability(str, Enum):
    """Criterios de aceptabilidad de riesgo."""
    UNACCEPTABLE = "unacceptable"
    ALARA = "alara"                 # As Low As Reasonably Achievable
    ACCEPTABLE = "acceptable"


class RiskControlMeasure(str, Enum):
    """Medidas de control de riesgo."""
    ARCHITECTURAL = "architectural"     # Cambios en arquitectura
    DETAILED_DESIGN = "detailed_design" # Cambios en diseño detallado
    CODE = "code"                        # Cambios en código
    TESTING = "testing"                  # Pruebas adicionales
    DOCUMENTATION = "documentation"      # Documentación/advertencias
    MONITORING = "monitoring"            # Monitoreo post-release


@dataclass
class SoftwareRisk:
    """Riesgo de software."""
    risk_id: str
    hazard_id: str
    title: str
    description: str
    severity: str
    probability: str
    initial_risk: str
    control_measures: list[RiskControlMeasure] = field(default_factory=list)
    residual_severity: str = ""
    residual_probability: str = ""
    residual_risk: str = ""
    acceptability: RiskAcceptability = RiskAcceptability.ALARA
    responsible: str = ""
    review_date: Optional[datetime] = None


@dataclass
class RiskManagementFile:
    """Archivo de gestión de riesgos."""
    file_id: str
    software_name: str
    software_class: str
    created_at: datetime
    risks: list[SoftwareRisk] = field(default_factory=list)
    acceptable_risk_criteria: str = "ALARA"
    authority: str = ""


class IEC62304RiskManager:
    """Gestor de riesgos IEC 62304."""

    def __init__(self):
        self._files: dict[str, RiskManagementFile] = {}
        self._risks: dict[str, list[SoftwareRisk]] = {}

    def create_rmf(
        self,
        software_name: str,
        software_class: str,
        authority: str,
    ) -> RiskManagementFile:
        """Crea Risk Management File."""
        file_id = f"rmf-{software_name.lower().replace(' ', '-')}"
        rmf = RiskManagementFile(
            file_id=file_id,
            software_name=software_name,
            software_class=software_class,
            created_at=datetime.utcnow(),
            authority=authority,
        )
        self._files[file_id] = rmf
        self._risks[file_id] = []
        return rmf

    def add_risk(
        self,
        file_id: str,
        hazard_id: str,
        title: str,
        description: str,
        severity: str,
        probability: str,
        responsible: str,
    ) -> SoftwareRisk:
        """Agrega riesgo al archivo."""
        if file_id not in self._risks:
            self._risks[file_id] = []

        risk = SoftwareRisk(
            risk_id=f"risk-{len(self._risks[file_id]) + 1:04d}",
            hazard_id=hazard_id,
            title=title,
            description=description,
            severity=severity,
            probability=probability,
            initial_risk=self._calculate_risk(severity, probability),
            responsible=responsible,
        )
        self._risks[file_id].append(risk)
        return risk

    def apply_control_measure(
        self,
        file_id: str,
        risk_id: str,
        measure: RiskControlMeasure,
        residual_severity: str,
        residual_probability: str,
    ) -> bool:
        """Aplica medida de control."""
        for risk in self._risks.get(file_id, []):
            if risk.risk_id == risk_id:
                risk.control_measures.append(measure)
                risk.residual_severity = residual_severity
                risk.residual_probability = residual_probability
                risk.residual_risk = self._calculate_risk(
                    residual_severity, residual_probability
                )
                return True
        return False

    def evaluate_acceptability(
        self,
        file_id: str,
        risk_id: str,
    ) -> RiskAcceptability:
        """Evalúa aceptabilidad de riesgo residual."""
        for risk in self._risks.get(file_id, []):
            if risk.risk_id == risk_id:
                return risk.acceptability
        return RiskAcceptability.UNACCEPTABLE

    def _calculate_risk(self, severity: str, probability: str) -> str:
        """Calcula nivel de riesgo."""
        severity_map = {"Negligible": 1, "Critical": 3, "Catastrophic": 5}
        probability_map = {"Frequent": 5, "Probable": 4, "Occasional": 3, "Rare": 2, "Improbable": 1}

        s = severity_map.get(severity, 1)
        p = probability_map.get(probability, 1)
        score = s * p

        if score >= 15:
            return "Critical"
        elif score >= 8:
            return "High"
        elif score >= 4:
            return "Medium"
        return "Low"

    def get_risk_summary(self, file_id: str) -> dict:
        """Obtiene resumen de riesgos."""
        risks = self._risks.get(file_id, [])
        by_level = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        unacceptable = 0

        for risk in risks:
            by_level[risk.initial_risk] += 1
            if risk.acceptability == RiskAcceptability.UNACCEPTABLE:
                unacceptable += 1

        return {
            "file_id": file_id,
            "total_risks": len(risks),
            "risks_by_level": by_level,
            "unacceptable_risks": unacceptable,
        }
