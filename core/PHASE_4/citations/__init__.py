"""
Citation and Evidence Attribution Module

Provides citation generation and source attribution for clinical responses.
Integrates evidence tracing from PHASE_3 intelligence engines.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol


class CitationFormat(str, Enum):
    """Citation format styles."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    VANCOUVER = "vancouver"
    NUMERIC = "numeric"


class SourceType(str, Enum):
    """Citation source types."""
    PUBMED = "pubmed"
    CLINICAL_TRIAL = "clinical_trial"
    GUIDELINE = "guideline"
    DEVICE_MANUAL = "device_manual"
    STANDARD = "standard"
    REGULATION = "regulation"
    KNOWLEDGE_ARTICLE = "knowledge_article"
    EXPERT_OPINION = "expert_opinion"


@dataclass
class Citation:
    """Citation for a piece of information."""
    citation_id: str
    source_type: SourceType
    source_id: str
    
    # Content
    title: str
    authors: list[str] = field(default_factory=list)
    publication: str = ""
    year: str = ""
    volume: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    
    # Clinical metadata
    evidence_level: str = ""
    medical_specialty: str = ""
    
    # Attribution
    quoted_text: str = ""
    page_number: str = ""
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EvidenceTrace:
    """Trace of evidence through reasoning."""
    trace_id: str
    claim: str
    supporting_evidence: list[str] = field(default_factory=list)  # Citation IDs
    contradicting_evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning_path: list[str] = field(default_factory=list)


@dataclass
class SourceAttribution:
    """Attribution of a response to sources."""
    response_segment: str
    citation_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence_level: str = ""


class ICitationBuilder(Protocol):
    """Protocol for citation builder."""
    
    def build(self, context) -> list[Citation]:
        """Build citations from context."""
        ...


class CitationBuilder:
    """Builds citations from clinical context."""
    
    def __init__(
        self,
        format_style: CitationFormat = CitationFormat.APA,
    ):
        """Initialize builder."""
        self.format_style = format_style
    
    def build(self, context) -> list[Citation]:
        """Build citations from context."""
        citations = []
        
        # Extract citations from retrieved knowledge
        if hasattr(context, "retrieved_knowledge"):
            for item in context.retrieved_knowledge:
                if "citation_id" in item.get("metadata", {}):
                    citations.append(self._build_from_metadata(item))
        
        return citations
    
    def _build_from_metadata(self, item: dict) -> Citation:
        """Build citation from metadata."""
        metadata = item.get("metadata", {})
        return Citation(
            citation_id=metadata.get("citation_id", ""),
            source_type=SourceType(metadata.get("source_type", "knowledge_article")),
            source_id=metadata.get("source_id", ""),
            title=item.get("title", ""),
            authors=metadata.get("authors", []),
            year=metadata.get("year", ""),
            doi=metadata.get("doi", ""),
            evidence_level=metadata.get("evidence_level", ""),
        )
    
    def format_citation(self, citation: Citation) -> str:
        """Format citation according to style."""
        if self.format_style == CitationFormat.APA:
            return self._format_apa(citation)
        elif self.format_style == CitationFormat.VANCOUVER:
            return self._format_vancouver(citation)
        return str(citation)
    
    def _format_apa(self, citation: Citation) -> str:
        """Format in APA style."""
        authors = ", ".join(citation.authors) if citation.authors else "Unknown"
        year = citation.year or "n.d."
        title = citation.title
        doi = f"doi:{citation.doi}" if citation.doi else citation.url
        
        return f"{authors} ({year}). {title}. {doi}"
    
    def _format_vancouver(self, citation: Citation) -> str:
        """Format in Vancouver style."""
        authors = ", ".join(citation.authors[:3]) + " et al." if len(citation.authors) > 3 else ", ".join(citation.authors)
        year = citation.year
        title = citation.title
        source = citation.publication or citation.url
        
        return f"{authors}. {title}. {source}. {year}."


class SourceAttributor:
    """Attributes response segments to sources."""
    
    def __init__(self, citation_builder: CitationBuilder):
        """Initialize attributor."""
        self.citation_builder = citation_builder
    
    def attribute(
        self,
        response: str,
        citations: list[Citation],
    ) -> list[SourceAttribution]:
        """Attribute response segments to sources."""
        attributions = []
        
        for citation in citations:
            attribution = SourceAttribution(
                response_segment=f"[See {citation.title}]",
                citation_ids=[citation.citation_id],
                confidence=0.8,
                evidence_level=citation.evidence_level,
            )
            attributions.append(attribution)
        
        return attributions


class EvidenceTracer:
    """Traces evidence through reasoning chains."""
    
    def __init__(self):
        """Initialize tracer."""
        self.traces: list[EvidenceTrace] = []
    
    def add_trace(
        self,
        claim: str,
        supporting: list[str] | None = None,
        contradicting: list[str] | None = None,
        confidence: float = 0.0,
    ) -> EvidenceTrace:
        """Add evidence trace."""
        import uuid
        
        trace = EvidenceTrace(
            trace_id=str(uuid.uuid4()),
            claim=claim,
            supporting_evidence=supporting or [],
            contradicting_evidence=contradicting or [],
            confidence=confidence,
        )
        self.traces.append(trace)
        return trace
    
    def get_trace(self, trace_id: str) -> EvidenceTrace | None:
        """Get trace by ID."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None
    
    def build_chain(
        self,
        primary_claim: str,
        supporting_claims: list[str],
    ) -> list[EvidenceTrace]:
        """Build reasoning chain."""
        chain = []
        
        # Add primary claim
        primary_trace = self.add_trace(primary_claim, confidence=0.8)
        chain.append(primary_trace)
        
        # Add supporting claims
        for claim in supporting_claims:
            trace = self.add_trace(claim, confidence=0.6)
            chain.append(trace)
        
        return chain


class ReferenceFormatter:
    """Formats references for display."""
    
    def __init__(self, style: CitationFormat = CitationFormat.APA):
        """Initialize formatter."""
        self.style = style
        self.citation_builder = CitationBuilder(style)
    
    def format_reference_list(
        self,
        citations: list[Citation],
    ) -> str:
        """Format list of references."""
        lines = []
        
        for i, citation in enumerate(citations, 1):
            formatted = self.citation_builder.format_citation(citation)
            lines.append(f"[{i}] {formatted}")
        
        return "\n".join(lines)
    
    def format_inline_citations(
        self,
        text: str,
        citations: list[Citation],
    ) -> str:
        """Format inline citations in text."""
        # Placeholder - would implement actual citation insertion
        return text
