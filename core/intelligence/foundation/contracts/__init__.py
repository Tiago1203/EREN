"""
Clinical Intelligence Contracts

Protocols (interfaces) for clinical reasoning components.
"""

from typing import Protocol, Optional
from dataclasses import dataclass

__all__ = [
    "IClinicalReasoner",
    "IEvidenceEvaluator",
    "IClinicalValidator",
    "ClinicalExplanation",
]


@dataclass(frozen=True)
class ClinicalExplanation:
    """Explicación clínica de un diagnóstico o recomendación."""
    explanation_id: str
    content: str
    evidence_references: list[str]
    reasoning_steps: list[str]
    confidence_factors: list[str]
    alternative_considerations: list[str]


class IClinicalReasoner(Protocol):
    """
    Interface para razonadores clínicos.
    
    Responsabilidades:
    - Generar candidatos de diagnóstico
    - Proporcionar explicaciones
    - Manejar incertidumbre
    """
    
    async def reason(
        self,
        patient_context: "PatientSummary",
        findings: list["ClinicalFinding"],
        clinical_question: str,
    ) -> list["DiagnosisCandidate"]:
        """Genera candidatos de diagnóstico."""
        ...
    
    async def explain(
        self,
        diagnosis_id: str,
    ) -> ClinicalExplanation:
        """Genera explicación de un diagnóstico."""
        ...
    
    async def rank_candidates(
        self,
        candidates: list["DiagnosisCandidate"],
    ) -> list["DiagnosisCandidate"]:
        """Ranking de candidatos por probabilidad."""
        ...


class IEvidenceEvaluator(Protocol):
    """
    Interface para evaluadores de evidencia.
    
    Responsabilidades:
    - Evaluar calidad de evidencia
    - Construir cadenas de evidencia
    - Asignar pesos
    """
    
    async def evaluate_evidence(
        self,
        evidence: "Evidence",
        context: dict,
    ) -> tuple[float, list[str]]:
        """
        Evalúa la calidad de la evidencia.
        
        Returns:
            Tuple de (score 0.0-1.0, lista de razones)
        """
        ...
    
    async def build_evidence_chain(
        self,
        findings: list["ClinicalFinding"],
    ) -> "EvidenceChain":
        """Construye cadena de evidencia para hallazgos."""
        ...
    
    async def assess_consistency(
        self,
        evidence_chain: "EvidenceChain",
    ) -> float:
        """
        Evalúa consistencia de la cadena de evidencia.
        
        Returns:
            Score de consistencia 0.0-1.0
        """
        ...


class IClinicalValidator(Protocol):
    """
    Interface para validadores clínicos.
    
    Responsabilidades:
    - Ejecutar validaciones de seguridad
    - Verificar contraindicaciones
    - Generar alertas
    """
    
    async def validate_recommendation(
        self,
        recommendation: "TreatmentRecommendation",
        patient_context: dict,
    ) -> "ValidationReport":
        """Valida una recomendación de tratamiento."""
        ...
    
    async def check_safety(
        self,
        recommendation: "TreatmentRecommendation",
        patient_context: dict,
    ) -> list["SafetyCheck"]:
        """Ejecuta checks de seguridad."""
        ...
    
    async def generate_alerts(
        self,
        safety_issues: list["SafetyCheck"],
    ) -> list["ClinicalWarning"]:
        """Genera alertas clínicas."""
        ...
