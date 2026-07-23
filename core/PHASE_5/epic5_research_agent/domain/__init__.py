"""
PHASE 5 - EPIC 5: Research Domain Objects

Domain objects especializados para investigación biomédica:
- ResearchRequest
- ResearchResult
- LiteratureReview
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class ResearchType(str, Enum):
    """Tipos de investigación."""
    SYSTEMATIC_REVIEW = "systematic_review"     # Revisión sistemática
    META_ANALYSIS = "meta_analysis"           # Meta-análisis
    CLINICAL_TRIAL = "clinical_trial"         # Ensayo clínico
    CASE_STUDY = "case_study"                 # Caso clínico
    TECHNICAL_REVIEW = "technical_review"      # Revisión técnica
    COMPARATIVE_STUDY = "comparative_study"   # Estudio comparativo
    COHORT_STUDY = "cohort_study"             # Estudio de cohorte
    EXPERIMENTAL = "experimental"             # Experimental


class ResearchScope(str, Enum):
    """Alcance de la investigación."""
    COMPREHENSIVE = "comprehensive"           # Completo (múltiples fuentes)
    FOCUSED = "focused"                     # Enfocado (una pregunta)
    RAPID = "rapid"                         # Rápido (literatura reciente)
    EXHAUSTIVE = "exhaustive"               # Exhaustivo (toda la evidencia)


class EvidenceStrength(str, Enum):
    """Fortaleza de la evidencia."""
    STRONG = "strong"                       # Alta confianza
    MODERATE = "moderate"                   # Confianza moderada
    LIMITED = "limited"                     # Evidencia limitada
    INSUFFICIENT = "insufficient"          # Evidencia insuficiente
    CONFLICTING = "conflicting"            # Evidencia conflictiva


class ComparisonType(str, Enum):
    """Tipos de comparación."""
    METHODOLOGY = "methodology"            # Metodología
    RESULTS = "results"                    # Resultados
    POPULATION = "population"             # Población
    OUTCOMES = "outcomes"                 # Resultados
    QUALITY = "quality"                   # Calidad


# =============================================================================
# RESEARCH REQUEST - Solicitud de investigación
# =============================================================================

@dataclass
class ResearchRequest:
    """Solicitud de investigación."""
    request_id: str = ""
    research_type: ResearchType = ResearchType.SYSTEMATIC_REVIEW
    
    # Tema
    research_question: str = ""
    background: str = ""
    objectives: list[str] = field(default_factory=list)
    
    # Alcance
    scope: ResearchScope = ResearchScope.COMPREHENSIVE
    keywords: list[str] = field(default_factory=list)
    
    # Constraints
    max_articles: int = 50
    date_range_years: int = 5
    include_gray_literature: bool = False
    
    # Criteria
    inclusion_criteria: list[str] = field(default_factory=list)
    exclusion_criteria: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    priority: int = 5
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


# =============================================================================
# RESEARCH FINDING - Hallazgo de investigación
# =============================================================================

@dataclass
class ResearchFinding:
    """Hallazgo de una investigación."""
    finding_id: str = ""
    
    # Descripción
    description: str = ""
    key_points: list[str] = field(default_factory=list)
    
    # Evidencia
    evidence_strength: EvidenceStrength = EvidenceStrength.MODERATE
    supporting_studies: list[str] = field(default_factory=list)
    contradicting_studies: list[str] = field(default_factory=list)
    
    # Metadatos
    confidence_level: float = 0.0
    source_articles: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.finding_id:
            self.finding_id = str(uuid.uuid4())


# =============================================================================
# RESEARCH RESULT - Resultado de investigación
# =============================================================================

@dataclass
class ResearchResult:
    """Resultado de investigación."""
    result_id: str = ""
    request_id: str = ""
    
    # Hallazgos
    findings: list[ResearchFinding] = field(default_factory=list)
    
    # Stats
    articles_reviewed: int = 0
    articles_included: int = 0
    articles_excluded: int = 0
    
    # Conclusión
    conclusion: str = ""
    recommendations: list[str] = field(default_factory=list)
    
    # Calidad
    overall_quality: float = 0.0
    evidence_summary: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    research_time_ms: int = 0
    
    def __post_init__(self):
        if not self.result_id:
            self.result_id = str(uuid.uuid4())
    
    def add_finding(self, finding: ResearchFinding) -> None:
        """Agrega un hallazgo."""
        self.findings.append(finding)


# =============================================================================
# PAPER COMPARISON - Comparación de artículos
# =============================================================================

@dataclass
class PaperComparison:
    """Comparación entre artículos."""
    comparison_id: str = ""
    
    # Artículos comparados
    paper_1_id: str = ""
    paper_2_id: str = ""
    
    # Aspectos comparados
    comparison_type: ComparisonType = ComparisonType.METHODOLOGY
    comparison_details: dict = field(default_factory=dict)
    
    # Resultado
    agreement_level: float = 0.0
    key_differences: list[str] = field(default_factory=list)
    key_similarities: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.comparison_id:
            self.comparison_id = str(uuid.uuid4())


# =============================================================================
# SUMMARY SECTION - Sección de resumen
# =============================================================================

@dataclass
class SummarySection:
    """Sección de un resumen estructurado."""
    section_id: str = ""
    
    # Contenido
    title: str = ""
    content: str = ""
    
    # Type
    section_type: str = "general"  # introduction, methods, results, discussion, etc.
    
    # Metadatos
    order: int = 0
    
    def __post_init__(self):
        if not self.section_id:
            self.section_id = str(uuid.uuid4())


# =============================================================================
# LITERATURE REVIEW - Revisión de literatura
# =============================================================================

@dataclass
class LiteratureReview:
    """Revisión de literatura estructurada."""
    review_id: str = ""
    request_id: str = ""
    
    # Título
    title: str = ""
    
    # Secciones
    sections: list[SummarySection] = field(default_factory=list)
    
    # Comparaciones
    comparisons: list[PaperComparison] = field(default_factory=list)
    
    # Referencias
    references_count: int = 0
    key_references: list[str] = field(default_factory=list)
    
    # Calidad
    quality_score: float = 0.0
    completeness_score: float = 0.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    review_time_ms: int = 0
    
    def __post_init__(self):
        if not self.review_id:
            self.review_id = str(uuid.uuid4())
        self.references_count = len(self.key_references)
    
    def add_section(self, section: SummarySection) -> None:
        """Agrega una sección."""
        self.sections.append(section)
        self.sections.sort(key=lambda s: s.order)
    
    def get_section(self, section_type: str) -> SummarySection | None:
        """Obtiene una sección por tipo."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None
    
    def to_markdown(self) -> str:
        """Convierte a formato markdown."""
        md = f"# {self.title}\n\n"
        
        for section in self.sections:
            md += f"## {section.title}\n\n{section.content}\n\n"
        
        md += "---\n\n## References\n\n"
        for i, ref in enumerate(self.key_references, 1):
            md += f"{i}. {ref}\n"
        
        return md


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "ResearchType",
    "ResearchScope",
    "EvidenceStrength",
    "ComparisonType",
    # Domain Objects
    "ResearchRequest",
    "ResearchFinding",
    "ResearchResult",
    "PaperComparison",
    "SummarySection",
    "LiteratureReview",
]
