"""
PHASE 7 - EPIC 0: IEC 62304 Software Classification

Clasificación de software médico IEC 62304:
- Safety Classification (Class A, B, C)
- Risk Management
- Software Requirements
- Architecture
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SoftwareClass(str, Enum):
    """Clasificación de software IEC 62304."""
    CLASS_A = "A"    # No injury possible
    CLASS_B = "B"    # Non-serious injury possible
    CLASS_C = "C"   # Death or serious injury possible


class HazardSeverity(str, Enum):
    """Severidad de hazard."""
    NEGLIGIBLE = "negligible"        # Minor injury, no permanent impairment
    CRITICAL = "critical"            # Serious injury, permanent impairment
    CATASTROPHIC = "catastrophic"    # Death or permanent severe impairment


class Probability(str, Enum):
    """Probabilidad de ocurrencia."""
    FREQUENT = "frequent"
    PROBABLE = "probable"
    OCCASIONAL = "occasional"
    RARE = "rare"
    IMPROBABLE = "improbable"
    NONE = "none"


@dataclass
class SoftwareRequirement:
    """Requisito de software."""
    requirement_id: str
    title: str
    description: str
    software_class: SoftwareClass
    safety_classification: bool       # Si es un safety requirement
    priority: int = 1
    source: str = ""


@dataclass
class Hazard:
    """Hazard identificado."""
    hazard_id: str
    title: str
    description: str
    severity: HazardSeverity
    probability: Probability
    risk_level: str = ""            # Calculado
    mitigation: str = ""
    software_requirement_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SoftwareItem:
    """Item de software."""
    item_id: str
    name: str
    software_class: SoftwareClass
    parent_id: Optional[str] = None
    child_ids: list[str] = field(default_factory=list)


class IEC62304Classifier:
    """Clasificador de software IEC 62304."""

    RISK_LEVELS = {
        (HazardSeverity.NEGLIGIBLE, Probability.FREQUENT): "Medium",
        (HazardSeverity.NEGLIGIBLE, Probability.PROBABLE): "Medium",
        (HazardSeverity.NEGLIGIBLE, Probability.OCCASIONAL): "Low",
        (HazardSeverity.NEGLIGIBLE, Probability.RARE): "Low",
        (HazardSeverity.NEGLIGIBLE, Probability.IMPROBABLE): "Low",
        (HazardSeverity.CRITICAL, Probability.FREQUENT): "High",
        (HazardSeverity.CRITICAL, Probability.PROBABLE): "High",
        (HazardSeverity.CRITICAL, Probability.OCCASIONAL): "Medium",
        (HazardSeverity.CRITICAL, Probability.RARE): "Medium",
        (HazardSeverity.CRITICAL, Probability.IMPROBABLE): "Low",
        (HazardSeverity.CATASTROPHIC, Probability.FREQUENT): "Critical",
        (HazardSeverity.CATASTROPHIC, Probability.PROBABLE): "Critical",
        (HazardSeverity.CATASTROPHIC, Probability.OCCASIONAL): "High",
        (HazardSeverity.CATASTROPHIC, Probability.RARE): "Medium",
        (HazardSeverity.CATASTROPHIC, Probability.IMPROBABLE): "Medium",
    }

    def classify_software(
        self,
        hazards: list[Hazard],
    ) -> SoftwareClass:
        """Clasifica software basándose en hazards."""
        if not hazards:
            return SoftwareClass.CLASS_A

        max_risk = "Low"
        for hazard in hazards:
            risk = self.RISK_LEVELS.get((hazard.severity, hazard.probability), "Low")
            if risk == "Critical":
                return SoftwareClass.CLASS_C
            elif risk == "High" and max_risk != "Critical":
                max_risk = "High"
            elif risk == "Medium" and max_risk not in ["Critical", "High"]:
                max_risk = "Medium"

        if max_risk in ["Critical", "High"]:
            return SoftwareClass.CLASS_C
        elif max_risk == "Medium":
            return SoftwareClass.CLASS_B
        return SoftwareClass.CLASS_A

    def calculate_risk_level(self, severity: HazardSeverity, probability: Probability) -> str:
        """Calcula nivel de riesgo."""
        return self.RISK_LEVELS.get((severity, probability), "Low")

    def create_software_item(
        self,
        name: str,
        software_class: SoftwareClass,
        parent_id: Optional[str] = None,
    ) -> SoftwareItem:
        """Crea item de software."""
        item = SoftwareItem(
            item_id=f"sw-item-{name.lower().replace(' ', '-')}",
            name=name,
            software_class=software_class,
            parent_id=parent_id,
        )
        return item

    def get_development_process(self, software_class: SoftwareClass) -> dict:
        """Obtiene proceso de desarrollo requerido."""
        processes = {
            SoftwareClass.CLASS_A: {
                "process_required": True,
                "software_planning": True,
                "software_requirements": True,
                "software_architecture": False,
                "software_detailed_design": False,
                "software_unit_implementation": False,
                "software_unit_verification": False,
                "software_integration": True,
                "software_system_testing": True,
            },
            SoftwareClass.CLASS_B: {
                "process_required": True,
                "software_planning": True,
                "software_requirements": True,
                "software_architecture": True,
                "software_detailed_design": False,
                "software_unit_implementation": True,
                "software_unit_verification": True,
                "software_integration": True,
                "software_system_testing": True,
            },
            SoftwareClass.CLASS_C: {
                "process_required": True,
                "software_planning": True,
                "software_requirements": True,
                "software_architecture": True,
                "software_detailed_design": True,
                "software_unit_implementation": True,
                "software_unit_verification": True,
                "software_integration": True,
                "software_system_testing": True,
            },
        }
        return processes.get(software_class, processes[SoftwareClass.CLASS_A])
