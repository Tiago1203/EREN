"""
Evidence Retrieval Module

Provides evidence storage and retrieval from multiple sources:
- Literature (PubMed, ClinicalTrials)
- Standards (ISO, IEC)
- Regulatory (FDA, ECRI)
- Guidelines (WHO, NICE)
- Real-world evidence
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


class EvidenceSourceType(Enum):
    """Types of evidence sources."""
    PUBMED = "pubmed"
    CLINICAL_TRIALS = "clinical_trials"
    COCHRANE = "cochrane"
    ISO_STANDARD = "iso_standard"
    IEC_STANDARD = "iec_standard"
    AAMI_GUIDELINE = "aami_guideline"
    FDA_MAUDE = "fda_maude"
    FDA_RECALL = "fda_recall"
    ECRI_REPORT = "ecri_report"
    EU_MDR = "eu_mdr"
    WHO_GUIDELINE = "who_guideline"
    NICE_GUIDELINE = "nice_guideline"
    INSTITUTIONAL_GUIDELINE = "institutional_guideline"
    INCIDENT_REPORT = "incident_report"
    MAINTENANCE_LOG = "maintenance_log"
    DEVICE_TELEMETRY = "device_telemetry"
    REAL_WORLD_EVIDENCE = "real_world_evidence"


class EvidenceLevel(Enum):
    """Evidence quality levels."""
    LEVEL_1_SYSTEMATIC = "level_1_systematic"
    LEVEL_1_RCT = "level_1_rct"
    LEVEL_2_COHORT = "level_2_cohort"
    LEVEL_3_CASE_CONTROL = "level_3_case_control"
    LEVEL_4_CASE_SERIES = "level_4_case_series"
    LEVEL_5_EXPERT = "level_5_expert"
    LEVEL_6_MECHANISTIC = "level_6_mechanistic"
    LEVEL_7_REAL_WORLD = "level_7_real_world"


class QueryType(Enum):
    """Evidence query types."""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    VECTOR = "vector"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class Evidence:
    """Stored evidence."""
    evidence_id: str
    source_type: EvidenceSourceType
    source_id: str
    title: str
    abstract: str | None = None
    url: str | None = None
    authors: list[str] = field(default_factory=list)
    publication_date: date | None = None
    evidence_level: EvidenceLevel = EvidenceLevel.LEVEL_5_EXPERT
    content_hash: str | None = None
    indexed_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceQuery:
    """Evidence search query."""
    query_text: str
    query_type: QueryType = QueryType.HYBRID
    context: dict | None = None


@dataclass(frozen=True)
class EvidenceFilters:
    """Filters for evidence search."""
    source_types: list[EvidenceSourceType] | None = None
    evidence_levels: list[EvidenceLevel] | None = None
    date_from: date | None = None
    date_to: date | None = None
    relevance_threshold: float | None = None


@dataclass(frozen=True)
class EvidenceRetrieval:
    """Evidence retrieval result."""
    retrieval_id: str
    query: str
    evidence_found: list[Evidence]
    relevance_scores: dict[str, float] = field(default_factory=dict)
    retrieval_time_ms: int = 0
    total_available: int = 0


class EvidenceStore:
    """
    Evidence store for storing and retrieving biomedical evidence.
    """
    
    def __init__(self):
        self._evidence: dict[str, Evidence] = {}
        self._cache: dict[str, EvidenceRetrieval] = {}
    
    async def add_evidence(self, evidence: Evidence) -> str:
        """Add evidence to the store."""
        self._evidence[evidence.evidence_id] = evidence
        return evidence.evidence_id
    
    async def retrieve_evidence(
        self,
        query: EvidenceQuery,
        filters: EvidenceFilters | None = None,
        limit: int = 20,
    ) -> EvidenceRetrieval:
        """Retrieve relevant evidence."""
        results = []
        query_lower = query.query_text.lower()
        
        for ev in self._evidence.values():
            if query_lower in ev.title.lower() or (ev.abstract and query_lower in ev.abstract.lower()):
                results.append(ev)
                if len(results) >= limit:
                    break
        
        return EvidenceRetrieval(
            retrieval_id=f"retrieval_{datetime.now().timestamp()}",
            query=query.query_text,
            evidence_found=results,
            total_available=len(results),
        )
    
    async def get_evidence(
        self,
        evidence_id: str,
    ) -> Evidence | None:
        """Get evidence by ID."""
        return self._evidence.get(evidence_id)


__all__ = [
    "EvidenceSourceType",
    "EvidenceLevel",
    "QueryType",
    "Evidence",
    "EvidenceQuery",
    "EvidenceFilters",
    "EvidenceRetrieval",
    "EvidenceStore",
]
