"""
Clinical Intelligence Policies

Business policies for clinical decision support.
"""

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "ClinicalPolicy",
    "PolicyType",
    "PolicyScope",
]


class PolicyType(Enum):
    """Tipos de políticas clínicas."""
    SAFETY = "safety"
    EVIDENCE = "evidence"
    CONFIDENCE = "confidence"
    ESCALATION = "escalation"
    DOCUMENTATION = "documentation"
    CONSENT = "consent"


class PolicyScope(Enum):
    """Alcance de políticas."""
    GLOBAL = "global"
    INSTITUTION = "institution"
    DEPARTMENT = "department"
    SPECIALTY = "specialty"
    INDIVIDUAL = "individual"


@dataclass(frozen=True)
class PolicyCondition:
    """Condición para aplicación de política."""
    condition_type: str
    parameters: dict
    logic_operator: str = "AND"  # AND, OR


@dataclass(frozen=True)
class PolicyAction:
    """Acción definida por política."""
    action_type: str
    parameters: dict
    requires_acknowledgment: bool = False


@dataclass(frozen=True)
class ClinicalPolicy:
    """
    Política clínica.
    
    Define reglas y acciones para decisiones clínicas.
    """
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    scope: PolicyScope
    conditions: list[PolicyCondition]
    actions: list[PolicyAction]
    severity_threshold: float = 0.0
    enabled: bool = True
    version: str = "1.0"
    
    def is_applicable(self, context: dict) -> bool:
        """Determina si la política aplica al contexto dado."""
        # Placeholder - implementar lógica específica
        return True
