"""
PHASE 5 - EPIC 4: Knowledge Domain Objects

Domain objects especializados para gestión de conocimiento:
- KnowledgeQuery
- KnowledgePackage
- CitationBundle
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

class QueryType(str, Enum):
    """Tipos de consulta de conocimiento."""
    FACTUAL = "factual"                   # Consulta factual
    PROCEDURAL = "procedural"             # Procedimientos
    REGULATORY = "regulatory"            # Normativa/regulación
    STANDARDS = "standards"              # Normas y estándares
    TECHNICAL = "technical"               # Técnica
    CLINICAL = "clinical"                # Clínica
    LITERATURE = "literature"            # Literatura científica
    EQUIPMENT = "equipment"              # Equipos
    SAFETY = "safety"                   # Seguridad
    COMPLIANCE = "compliance"            # Cumplimiento


class KnowledgeSource(str, Enum):
    """Fuentes de conocimiento."""
    MANUALS = "manuals"                 # Manuales de equipos
    STANDARDS = "standards"             # Normas (IEC, ISO, AAMI)
    GUIDELINES = "guidelines"           # Guías clínicas
    LITERATURE = "literature"           # Literatura científica
    REGULATIONS = "regulations"         # Regulaciones
    BEST_PRACTICES = "best_practices"   # Mejores prácticas
    HISTORICAL = "historical"           # Datos históricos
    EXPERT = "expert"                  # Conocimiento de expertos


class SourceType(str, Enum):
    """Tipos de fuente para citas."""
    JOURNAL_ARTICLE = "journal_article"
    BOOK = "book"
    STANDARD = "standard"
    REGULATION = "regulation"
    WEBSITE = "website"
    MANUAL = "manual"
    GUIDELINE = "guideline"
    REPORT = "report"
    DATASET = "dataset"
    OTHER = "other"


# =============================================================================
# KNOWLEDGE QUERY - Consulta de conocimiento
# =============================================================================

@dataclass
class KnowledgeQuery:
    """Consulta de conocimiento."""
    query_id: str = ""
    query_type: QueryType = QueryType.TECHNICAL
    
    # Pregunta
    question: str = ""
    context: str = ""
    
    # Scope
    sources: list[KnowledgeSource] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    
    # Constraints
    max_results: int = 10
    min_relevance: float = 0.7
    language: str = "en"
    
    # Filters
    date_from: datetime | None = None
    date_to: datetime | None = None
    equipment_ids: list[str] = field(default_factory=list)
    standard_codes: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.query_id:
            self.query_id = str(uuid.uuid4())


# =============================================================================
# KNOWLEDGE ITEM - Elemento de conocimiento
# =============================================================================

@dataclass
class KnowledgeItem:
    """Elemento de conocimiento retrieved."""
    item_id: str = ""
    
    # Contenido
    title: str = ""
    content: str = ""
    summary: str = ""
    
    # Source
    source_type: SourceType = SourceType.OTHER
    source_name: str = ""
    source_url: str = ""
    
    # Publication (for articles/books)
    publication: str = ""
    standard_code: str = ""
    
    # Metadatos
    relevance_score: float = 0.0
    citation_count: int = 0
    
    # Calidad
    quality_score: float = 0.0
    peer_reviewed: bool = False
    
    # Timestamps
    published_date: datetime | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.item_id:
            self.item_id = str(uuid.uuid4())


# =============================================================================
# KNOWLEDGE PACKAGE - Paquete de conocimiento
# =============================================================================

@dataclass
class KnowledgePackage:
    """Paquete de conocimiento retrieval."""
    package_id: str = ""
    query_id: str = ""
    
    # Items
    items: list[KnowledgeItem] = field(default_factory=list)
    
    # Stats
    total_items: int = 0
    avg_relevance: float = 0.0
    sources_count: int = 0
    
    # Citations
    citations: list[dict] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    retrieval_time_ms: int = 0
    
    def __post_init__(self):
        if not self.package_id:
            self.package_id = str(uuid.uuid4())
        
        # Calcular stats
        self.total_items = len(self.items)
        if self.items:
            self.avg_relevance = sum(i.relevance_score for i in self.items) / len(self.items)
            self.sources_count = len(set(i.source_type for i in self.items))
    
    def add_item(self, item: KnowledgeItem) -> None:
        """Agrega un item al paquete."""
        self.items.append(item)
        self.total_items = len(self.items)
        if self.total_items > 0:
            self.avg_relevance = sum(i.relevance_score for i in self.items) / len(self.items)
    
    def get_top_items(self, n: int = 5) -> list[KnowledgeItem]:
        """Obtiene los N items más relevantes."""
        sorted_items = sorted(self.items, key=lambda x: x.relevance_score, reverse=True)
        return sorted_items[:n]


# =============================================================================
# CITATION - Cita
# =============================================================================

@dataclass
class Citation:
    """Cita de fuente."""
    citation_id: str = ""
    
    # Información de la fuente
    source_type: SourceType = SourceType.OTHER
    title: str = ""
    authors: list[str] = field(default_factory=list)
    
    # Publicación
    publication: str = ""              # Journal, publisher, etc.
    volume: str = ""
    issue: str = ""
    pages: str = ""
    year: int = 0
    
    # Identificadores
    doi: str = ""
    url: str = ""
    isbn: str = ""
    standard_code: str = ""
    
    # Citation text
    citation_text: str = ""
    formatted_citation: str = ""
    
    def __post_init__(self):
        if not self.citation_id:
            self.citation_id = str(uuid.uuid4())
    
    def format_apa(self) -> str:
        """Formatea en estilo APA."""
        authors_str = ", ".join(self.authors) if self.authors else "Unknown"
        year_str = f"({self.year})" if self.year else "(n.d.)"
        title_str = self.title
        
        if self.source_type == SourceType.STANDARD:
            return f"{self.standard_code}. {self.title}. {year_str}."
        
        return f"{authors_str} {year_str}. {title_str}. {self.publication}."
    
    def format_vancouver(self) -> str:
        """Formatea en estilo Vancouver."""
        authors_str = ", ".join(self.authors[:3]) if len(self.authors) > 3 else ", ".join(self.authors)
        if len(self.authors) > 3:
            authors_str += ", et al."
        
        return f"{authors_str}. {self.title}. {self.publication}. {self.year};{self.volume}({self.issue}):{self.pages}."


# =============================================================================
# CITATION BUNDLE - Bundle de citas
# =============================================================================

@dataclass
class CitationBundle:
    """Bundle de citas para un documento."""
    bundle_id: str = ""
    
    # Citas
    citations: list[Citation] = field(default_factory=list)
    
    # Contexto
    topic: str = ""
    references_count: int = 0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.bundle_id:
            self.bundle_id = str(uuid.uuid4())
        self.references_count = len(self.citations)
    
    def add_citation(self, citation: Citation) -> None:
        """Agrega una cita."""
        self.citations.append(citation)
        self.references_count = len(self.citations)
    
    def format_references(self, style: str = "apa") -> str:
        """Formatea todas las referencias."""
        formatted = []
        for i, citation in enumerate(self.citations, 1):
            if style == "apa":
                formatted.append(f"[{i}] {citation.format_apa()}")
            elif style == "vancouver":
                formatted.append(f"{i}. {citation.format_vancouver()}")
            else:
                formatted.append(f"[{i}] {citation.title}")
        
        return "\n".join(formatted)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "QueryType",
    "KnowledgeSource",
    "SourceType",
    # Domain Objects
    "KnowledgeQuery",
    "KnowledgeItem",
    "KnowledgePackage",
    "Citation",
    "CitationBundle",
]
