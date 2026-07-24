"""
Domain objects para EPIC 13: Evidence Lifecycle Model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EvidenceType(Enum):
    """Tipo de evidencia."""
    CLINICAL_TRIAL = "clinical_trial"
    META_ANALYSIS = "meta_analysis"
    CLINICAL_GUIDELINE = "clinical_guideline"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"
    SYSTEMATIC_REVIEW = "systematic_review"


class QualityLevel(Enum):
    """Nivel de calidad (GRADE)."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"


class SourceType(Enum):
    """Tipo de fuente."""
    PUBMED = "pubmed"
    COCHRANE = "cochrane"
    CLINICAL_GUIDELINES = "clinical_guidelines"
    FDA = "fda"
    MANUFACTURER = "manufacturer"
    INSTITUTIONAL = "institutional"


class CitationStyle(Enum):
    """Estilo de citación."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    Vancouver = "vancouver"


@dataclass
class EvidenceSource:
    """Fuente de evidencia."""
    source_type: SourceType
    name: str
    url: Optional[str] = None
    doi: Optional[str] = None
    published_date: Optional[datetime] = None
    authors: list[str] = field(default_factory=list)
    journal: Optional[str] = None
    
    def is_peer_reviewed(self) -> bool:
        """Verifica si es peer-reviewed."""
        return self.source_type in [SourceType.PUBMED, SourceType.COCHRANE]


@dataclass
class EvidenceCitation:
    """Citación de evidencia."""
    citation_text: str
    bibtex: Optional[str] = None
    apa: Optional[str] = None
    links: list[str] = field(default_factory=list)
    
    def format(self, style: CitationStyle) -> str:
        """Formatea citación."""
        if style == CitationStyle.APA:
            return self.apa or self.citation_text
        elif style == CitationStyle.Vancouver:
            return self.citation_text
        return self.citation_text


@dataclass
class EvidenceContent:
    """Contenido de evidencia."""
    title: str
    abstract: str
    findings: str
    conclusions: str


@dataclass
class EvidenceQuality:
    """Calidad de evidencia."""
    quality_level: QualityLevel
    score: float
    methodology_score: float
    sample_size_score: float
    consistency_score: float
    publication_bias_score: float
    
    def is_high_quality(self) -> bool:
        """Verifica si es alta calidad."""
        return self.quality_level == QualityLevel.HIGH
    
    def get_limitations(self) -> list[str]:
        """Obtiene limitaciones."""
        limitations = []
        if self.methodology_score < 0.6:
            limitations.append("Methodology concerns")
        if self.sample_size_score < 0.5:
            limitations.append("Small sample size")
        if self.publication_bias_score > 0.3:
            limitations.append("Potential publication bias")
        return limitations


@dataclass
class RelevanceScore:
    """Score de relevancia."""
    score: float
    relevance_to_query: str
    population_match: float
    outcome_match: float
    
    def is_relevant(self, threshold: float = 0.5) -> bool:
        """Verifica si es relevante."""
        return self.score >= threshold


@dataclass
class ApplicabilityScore:
    """Score de aplicabilidad."""
    score: float
    clinical_setting_match: float
    patient_population_match: float
    resource_availability: float
    
    def is_applicable(self, threshold: float = 0.5) -> bool:
        """Verifica si es aplicable."""
        return self.score >= threshold


@dataclass
class Evidence:
    """Evidencia base."""
    evidence_id: str
    evidence_type: EvidenceType
    source: EvidenceSource
    content: EvidenceContent
    quality: EvidenceQuality
    relevance: RelevanceScore
    applicability: ApplicabilityScore
    citation: EvidenceCitation
    
    def get_confidence_level(self) -> float:
        """Obtiene nivel de confianza basado en calidad."""
        return (self.quality.score + self.relevance.score + self.applicability.score) / 3
    
    def is_strong(self) -> bool:
        """Verifica si es evidencia fuerte."""
        return (
            self.quality.is_high_quality() and
            self.relevance.is_relevant(0.7) and
            self.applicability.is_applicable(0.7)
        )


@dataclass
class EvidenceBundle:
    """Bundle de evidencia."""
    bundle_id: str
    query: str
    evidence_list: list[Evidence] = field(default_factory=list)
    synthesis: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_average_quality(self) -> float:
        """Obtiene calidad promedio."""
        if not self.evidence_list:
            return 0.0
        return sum(e.quality.score for e in self.evidence_list) / len(self.evidence_list)
    
    def get_strongest_evidence(self) -> Optional[Evidence]:
        """Obtiene evidencia más fuerte."""
        if not self.evidence_list:
            return None
        return max(self.evidence_list, key=lambda e: e.get_confidence_level())


@dataclass
class EvidenceQuery:
    """Query de evidencia."""
    query_text: str
    evidence_types: list[EvidenceType] = field(default_factory=list)
    date_range: Optional[tuple] = None
    include_guidelines: bool = True


@dataclass
class EvidenceConfig:
    """Configuración para EvidenceLifecycleAgent."""
    max_evidence: int = 20
    quality_threshold: float = 0.5
    relevance_threshold: float = 0.5
    include_peer_reviewed_only: bool = False
