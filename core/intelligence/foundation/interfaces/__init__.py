"""
Clinical Intelligence Interfaces

Additional interfaces for knowledge management and confidence calculation.
"""

from typing import Protocol, Optional
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "IConfidenceCalculator",
    "IKnowledgeBase",
    "IMedicalOntology",
    "IGuidelineRepository",
    "CodeSystem",
    "MedicalConcept",
]


class CodeSystem(Enum):
    """Sistemas de codificación médica."""
    SNOMED_CT = "snomed_ct"
    ICD_10 = "icd_10"
    ICD_11 = "icd_11"
    LOINC = "loinc"
    RXNORM = "rxnorm"
    UMLS = "umls"
    ATC = "atc"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ConceptRelationship:
    """Relación entre conceptos médicos."""
    relationship_type: str
    target_concept_id: str
    is_hierarchical: bool


@dataclass(frozen=True)
class MedicalConcept:
    """Concepto médico."""
    concept_id: str
    code_system: CodeSystem
    code: str
    display_name: str
    synonyms: list[str]
    definitions: list[str]
    semantic_type: str
    hierarchy_path: list[str]
    relationships: list[ConceptRelationship]


@dataclass(frozen=True)
class ConceptHierarchy:
    """Jerarquía de un concepto médico."""
    root: MedicalConcept
    parents: list[MedicalConcept]
    children: list[MedicalConcept]
    siblings: list[MedicalConcept]


@dataclass(frozen=True)
class ConfidenceExplanation:
    """Explicación de un score de confianza."""
    explanation_id: str
    score: float
    factor_breakdown: dict
    recommendations: list[str]


@dataclass(frozen=True)
class GuidelineContext:
    """Contexto para búsqueda de guías."""
    clinical_context: str
    patient_characteristics: dict
    available_resources: list[str]


@dataclass(frozen=True)
class ClinicalGuideline:
    """Guía clínica."""
    guideline_id: str
    title: str
    organization: str
    version: str
    effective_date: str
    url: Optional[str]
    recommendations: list["GuidelineRecommendation"]


@dataclass(frozen=True)
class GuidelineRecommendation:
    """Recomendación de una guía."""
    recommendation_id: str
    strength: str  # Strong, Weak
    text: str
    evidence_level: str
    notes: Optional[str]


class IConfidenceCalculator(Protocol):
    """
    Interface para calculadores de confianza.
    
    Responsabilidades:
    - Calcular scores de confianza
    - Explicar scores
    - Calibrar modelos
    """
    
    async def calculate_confidence(
        self,
        finding: "ClinicalFinding",
        evidence: list["Evidence"],
        patient_context: dict,
    ) -> "ConfidenceScore":
        """Calcula confianza para un hallazgo."""
        ...
    
    async def explain_confidence(
        self,
        score: "ConfidenceScore",
    ) -> ConfidenceExplanation:
        """Genera explicación del score."""
        ...
    
    async def update_calibration(
        self,
        predictions: list[float],
        outcomes: list[float],
    ) -> "CalibrationData":
        """Actualiza calibración del modelo."""
        ...


class IKnowledgeBase(Protocol):
    """
    Interface para base de conocimiento.
    
    Responsabilidades:
    - Buscar conceptos médicos
    - Obtener detalles de conceptos
    - Proporcionar relaciones
    """
    
    async def search_concepts(
        self,
        query: str,
        semantic_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[MedicalConcept]:
        """Busca conceptos médicos."""
        ...
    
    async def get_concept(
        self,
        concept_id: str,
    ) -> Optional[MedicalConcept]:
        """Obtiene concepto por ID."""
        ...
    
    async def get_related_concepts(
        self,
        concept_id: str,
        relation_type: Optional[str] = None,
    ) -> list[MedicalConcept]:
        """Obtiene conceptos relacionados."""
        ...


class IMedicalOntology(Protocol):
    """
    Interface para ontología médica.
    
    Responsabilidades:
    - Navegar jerarquías de conceptos
    - Encontrar relaciones
    - Inferir conocimiento
    """
    
    async def get_hierarchy(
        self,
        concept_id: str,
    ) -> ConceptHierarchy:
        """Obtiene jerarquía del concepto."""
        ...
    
    async def find_narrower_concepts(
        self,
        concept_id: str,
    ) -> list[MedicalConcept]:
        """Encuentra conceptos más específicos."""
        ...
    
    async def find_broader_concepts(
        self,
        concept_id: str,
    ) -> list[MedicalConcept]:
        """Encuentra conceptos más generales."""
        ...


class IGuidelineRepository(Protocol):
    """
    Interface para repositorio de guías clínicas.
    
    Responsabilidades:
    - Buscar guías por condición
    - Obtener recomendaciones
    - Verificar compliance
    """
    
    async def search_guidelines(
        self,
        query: str,
        specialty: Optional[str] = None,
    ) -> list[ClinicalGuideline]:
        """Busca guías clínicas."""
        ...
    
    async def get_guideline(
        self,
        guideline_id: str,
    ) -> Optional[ClinicalGuideline]:
        """Obtiene guía por ID."""
        ...
    
    async def get_recommendations_for(
        self,
        condition: str,
        context: GuidelineContext,
    ) -> list[GuidelineRecommendation]:
        """Obtiene recomendaciones para una condición."""
        ...
