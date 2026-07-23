"""
PHASE 4 - EPIC 7: Citation & Traceability Engine

Sistema de citación y trazabilidad:
- Generación de referencias
- DOI linking
- Source tracking
- Auditoría completa
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import uuid

from core.PHASE_4.foundation import (
    Citation,
    SourceReference,
    TracedCitation,
    EvidenceTrace,
    EvidenceLevel,
)


class CitationStyle(str, Enum):
    """Estilos de citación."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    VANCOUVER = "vancouver"
    AMA = "ama"
    NUMERIC = "numeric"


class SourceType(str, Enum):
    """Tipos de fuente."""
    PUBMED = "pubmed"
    CLINICAL_TRIAL = "clinical_trial"
    GUIDELINE = "guideline"
    DEVICE_MANUAL = "device_manual"
    STANDARD = "standard"
    REGULATION = "regulation"
    TEXTBOOK = "textbook"
    WEBSITE = "website"
    KNOWLEDGE_ARTICLE = "knowledge_article"


@dataclass
class FormattedCitation:
    """Citación formateada."""
    citation: Citation
    inline_format: str
    reference_format: str
    bibtex: str = ""


@dataclass
class CitationChain:
    """Cadena de citaciones."""
    chain_id: str
    primary_claim: str
    citations: list[Citation]
    reasoning_steps: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SourceTrace:
    """Traza de fuente para auditoría."""
    trace_id: str
    source_id: str
    source_type: SourceType
    action: str  # accessed, cited, extracted, verified
    timestamp: datetime
    user_id: str = ""
    ip_address: str = ""
    metadata: dict = field(default_factory=dict)


class ICitationFormatter(Protocol):
    """Protocolo para formateador de citaciones."""
    
    def format(self, citation: Citation) -> FormattedCitation:
        """Formatea citación."""
        ...


class APAFormatter:
    """Formateador APA."""
    
    def format(self, citation: Citation) -> FormattedCitation:
        """Formatea en estilo APA."""
        authors = self._format_authors(citation.reference.authors)
        year = citation.reference.year or "n.d."
        title = citation.reference.title
        
        # Build reference
        if citation.reference.doi:
            url = f"https://doi.org/{citation.reference.doi}"
        else:
            url = citation.reference.url
        
        reference = f"{authors} ({year}). {title}. {url}"
        
        # Inline format
        inline = f"({authors}, {year})"
        
        return FormattedCitation(
            citation=citation,
            inline_format=inline,
            reference_format=reference,
        )
    
    def _format_authors(self, authors: list[str]) -> str:
        """Formatea lista de autores."""
        if not authors:
            return "Unknown"
        if len(authors) == 1:
            return authors[0]
        if len(authors) <= 6:
            return ", ".join(authors[:-1]) + ", & " + authors[-1]
        return ", ".join(authors[:6]) + ", et al."


class VancouverFormatter:
    """Formateador Vancouver."""
    
    def format(self, citation: Citation) -> FormattedCitation:
        """Formatea en estilo Vancouver."""
        authors = self._format_authors(citation.reference.authors)
        title = citation.reference.title
        journal = citation.reference.journal
        year = citation.reference.year
        volume = citation.reference.volume
        pages = citation.reference.pages
        
        # Build reference
        parts = [authors, f"{title}.", journal]
        
        if year:
            parts.append(year)
        if volume:
            parts.append(f"{volume}")
        if pages:
            parts.append(f":{pages}")
        
        reference = ". ".join(filter(None, parts))
        
        # Inline
        inline = f"{authors}. {title}. {journal}. {year}"
        
        return FormattedCitation(
            citation=citation,
            inline_format=inline,
            reference_format=reference,
        )
    
    def _format_authors(self, authors: list[str]) -> str:
        """Formatea lista de autores."""
        if not authors:
            return "Unknown"
        if len(authors) == 1:
            return authors[0]
        if len(authors) <= 6:
            return ", ".join(authors[:-1]) + ", " + authors[-1]
        return f"{authors[0]} et al"


class DOIResolver:
    """Resuelve DOIs para obtener metadata."""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    async def resolve(self, doi: str) -> dict:
        """Resuelve DOI y retorna metadata."""
        if doi in self._cache:
            return self._cache[doi]
        
        # Placeholder - would call CrossRef API
        # https://api.crossref.org/works/{doi}
        
        result = {
            "doi": doi,
            "title": "Unknown",
            "authors": [],
            "journal": "",
            "year": "",
            "volume": "",
            "pages": "",
        }
        
        self._cache[doi] = result
        return result


class PubMedLinker:
    """Linker para PubMed."""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    async def get_metadata(self, pmid: str) -> dict:
        """Obtiene metadata de PubMed."""
        if pmid in self._cache:
            return self._cache[pmid]
        
        # Placeholder - would call PubMed API
        
        result = {
            "pmid": pmid,
            "title": "Unknown",
            "authors": [],
            "journal": "",
            "year": "",
        }
        
        self._cache[pmid] = result
        return result


class CitationEngine:
    """Motor de citación."""
    
    def __init__(
        self,
        formatter: ICitationFormatter | None = None,
    ):
        self.formatter = formatter or APAFormatter()
        self.doi_resolver = DOIResolver()
        self.pubmed_linker = PubMedLinker()
    
    async def cite(
        self,
        claim: str,
        source_id: str,
        source_type: SourceType,
        source_data: dict,
    ) -> Citation:
        """Crea citación para una fuente."""
        # Build source reference
        reference = SourceReference(
            source_id=source_id,
            source_type=source_type.value,
            title=source_data.get("title", "Unknown"),
            authors=source_data.get("authors", []),
            year=source_data.get("year", ""),
            doi=source_data.get("doi", ""),
            url=source_data.get("url", ""),
            journal=source_data.get("journal", ""),
            volume=source_data.get("volume", ""),
            pages=source_data.get("pages", ""),
        )
        
        # Determine evidence level
        evidence_level = self._determine_evidence_level(source_type)
        
        citation = Citation(
            citation_id=str(uuid.uuid4()),
            reference=reference,
            evidence_level=evidence_level,
            quality_score=source_data.get("quality_score", 0.5),
        )
        
        return citation
    
    async def cite_from_doi(self, doi: str, claim: str) -> Citation:
        """Crea citación desde DOI."""
        metadata = await self.doi_resolver.resolve(doi)
        
        return await self.cite(
            claim=claim,
            source_id=doi,
            source_type=SourceType.PUBMED,
            source_data=metadata,
        )
    
    def format_citation(
        self,
        citation: Citation,
        style: CitationStyle = CitationStyle.APA,
    ) -> FormattedCitation:
        """Formatea citación según estilo."""
        # Select formatter
        if style == CitationStyle.VANCOUVER:
            formatter = VancouverFormatter()
        else:
            formatter = APAFormatter()
        
        return formatter.format(citation)
    
    def format_reference_list(
        self,
        citations: list[Citation],
        style: CitationStyle = CitationStyle.APA,
    ) -> str:
        """Formatea lista de referencias."""
        formatted = []
        
        for i, citation in enumerate(citations, 1):
            fc = self.format_citation(citation, style)
            formatted.append(f"[{i}] {fc.reference_format}")
        
        return "\n".join(formatted)
    
    def _determine_evidence_level(self, source_type: SourceType) -> EvidenceLevel:
        """Determina nivel de evidencia según tipo de fuente."""
        levels = {
            SourceType.PUBMED: EvidenceLevel.LEVEL_2B,
            SourceType.CLINICAL_TRIAL: EvidenceLevel.LEVEL_1B,
            SourceType.GUIDELINE: EvidenceLevel.LEVEL_1A,
            SourceType.DEVICE_MANUAL: EvidenceLevel.LEVEL_5,
            SourceType.STANDARD: EvidenceLevel.LEVEL_5,
            SourceType.REGULATION: EvidenceLevel.LEVEL_5,
            SourceType.TEXTBOOK: EvidenceLevel.LEVEL_4,
            SourceType.WEBSITE: EvidenceLevel.LEVEL_5,
            SourceType.KNOWLEDGE_ARTICLE: EvidenceLevel.LEVEL_4,
        }
        return levels.get(source_type, EvidenceLevel.LEVEL_5)


class TraceabilityEngine:
    """Motor de trazabilidad."""
    
    def __init__(self):
        self._traces: dict[str, TracedCitation] = {}
        self._audit_log: list[SourceTrace] = []
    
    async def trace(
        self,
        claim: str,
        citations: list[Citation],
        reasoning_chain: list[str] | None = None,
    ) -> TracedCitation:
        """Crea trace de citación para claim."""
        trace_id = str(uuid.uuid4())
        
        # Build supporting/contradicting evidence
        supporting = [c.citation_id for c in citations]
        
        # Calculate confidence
        confidence = self._calculate_confidence(citations)
        
        traced = TracedCitation(
            trace_id=trace_id,
            citation=citations[0] if citations else None,
            claim=claim,
            reasoning_path=reasoning_chain or [],
            supporting_evidence=supporting,
            confidence=confidence,
        )
        
        self._traces[trace_id] = traced
        
        return traced
    
    async def get_trace(self, trace_id: str) -> Optional[TracedCitation]:
        """Obtiene trace por ID."""
        return self._traces.get(trace_id)
    
    async def link_claim_to_sources(
        self,
        claim: str,
        source_ids: list[str],
    ) -> EvidenceTrace:
        """Vincula claim a fuentes."""
        trace_id = str(uuid.uuid4())
        
        trace = EvidenceTrace(
            trace_id=trace_id,
            claim=claim,
            citations=[],  # Would load citations
            evidence_chain=source_ids,
        )
        
        return trace
    
    def log_access(
        self,
        source_id: str,
        source_type: SourceType,
        action: str,
        user_id: str = "",
    ) -> SourceTrace:
        """Registra acceso a fuente."""
        trace = SourceTrace(
            trace_id=str(uuid.uuid4()),
            source_id=source_id,
            source_type=source_type,
            action=action,
            timestamp=datetime.now(UTC),
            user_id=user_id,
        )
        
        self._audit_log.append(trace)
        
        return trace
    
    def get_audit_log(
        self,
        source_id: str | None = None,
        user_id: str | None = None,
    ) -> list[SourceTrace]:
        """Obtiene log de auditoría."""
        log = self._audit_log
        
        if source_id:
            log = [t for t in log if t.source_id == source_id]
        
        if user_id:
            log = [t for t in log if t.user_id == user_id]
        
        return log
    
    def _calculate_confidence(self, citations: list[Citation]) -> float:
        """Calcula confianza basada en citaciones."""
        if not citations:
            return 0.0
        
        # Weight by evidence level
        level_weights = {
            EvidenceLevel.LEVEL_1A: 1.0,
            EvidenceLevel.LEVEL_1B: 0.9,
            EvidenceLevel.LEVEL_2A: 0.8,
            EvidenceLevel.LEVEL_2B: 0.7,
            EvidenceLevel.LEVEL_3: 0.5,
            EvidenceLevel.LEVEL_4: 0.3,
            EvidenceLevel.LEVEL_5: 0.2,
        }
        
        total = 0.0
        for citation in citations:
            weight = level_weights.get(citation.evidence_level, 0.3)
            total += weight * citation.quality_score
        
        return total / len(citations)


class CitationChainBuilder:
    """Constructor de cadenas de citación."""
    
    def __init__(self, citation_engine: CitationEngine):
        self.citation_engine = citation_engine
    
    async def build_chain(
        self,
        primary_claim: str,
        supporting_claims: list[dict],  # {claim, source_id, source_type, source_data}
    ) -> CitationChain:
        """Construye cadena de citación."""
        chain_id = str(uuid.uuid4())
        
        citations = []
        reasoning_steps = [f"Primary claim: {primary_claim}"]
        
        for i, claim_data in enumerate(supporting_claims, 1):
            citation = await self.citation_engine.cite(
                claim=claim_data["claim"],
                source_id=claim_data["source_id"],
                source_type=claim_data["source_type"],
                source_data=claim_data["source_data"],
            )
            citations.append(citation)
            
            reasoning_steps.append(
                f"{i}. {claim_data['claim']} "
                f"[Evidence: {citation.reference.title}]"
            )
        
        # Calculate overall confidence
        confidence = sum(c.quality_score for c in citations) / len(citations) if citations else 0
        
        return CitationChain(
            chain_id=chain_id,
            primary_claim=primary_claim,
            citations=citations,
            reasoning_steps=reasoning_steps,
            confidence=confidence,
        )


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Citations (import as aliases to avoid override)
from core.PHASE_4.epic7_citation_traceability.citations import (
    CitationStyle,
    Citation as _Citation,
    BaseCitationBuilder,
    ClinicalCitationBuilder,
    CitationValidator,
)

# References
from core.PHASE_4.epic7_citation_traceability.references import (
    ReferenceStatus,
    Reference,
    BaseReferenceManager,
    InMemoryReferenceManager,
    DOIResolver,
    PubMedResolver,
    ReferenceIndexer,
)

# Sources (import as aliases to avoid override)
from core.PHASE_4.epic7_citation_traceability.sources import (
    SourceType as _SourceType,
    SourceStatus as _SourceStatus,
    EvidenceLevel as _EvidenceLevel,
    SourceEvidence,
    BaseSourceVerifier,
    ClinicalSourceVerifier,
    SourceTracker,
    AuditEntry,
    AuditTrail,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    # Enums
    "CitationStyle",
    "SourceType",
    "SourceStatus",
    "ReferenceStatus",
    "EvidenceLevel",
    # Data Classes
    "FormattedCitation",
    "CitationChain",
    "SourceTrace",
    "Citation",
    "Reference",
    "SourceEvidence",
    "AuditEntry",
    # Protocols
    "ICitationFormatter",
    "BaseCitationBuilder",
    "BaseReferenceManager",
    "BaseSourceVerifier",
    # Formatters
    "APAFormatter",
    "VancouverFormatter",
    "ClinicalCitationBuilder",
    "CitationValidator",
    # Resolvers
    "DOIResolver",
    "PubMedLinker",
    "PubMedResolver",
    "ReferenceIndexer",
    # Engines
    "CitationEngine",
    "TraceabilityEngine",
    "CitationChainBuilder",
    # New from submodules
    "InMemoryReferenceManager",
    "ClinicalSourceVerifier",
    "SourceTracker",
    "AuditTrail",
]
