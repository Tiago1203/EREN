"""
Evidence Retrieval Module

Provides evidence storage and retrieval from multiple sources:
- Literature (PubMed, ClinicalTrials)
- Standards (ISO, IEC)
- Regulatory (FDA, ECRI)
- Guidelines (WHO, NICE)
- Real-world evidence
"""

from core.PHASE_3.intelligence.knowledge.retrieval.evidence_store import (
    EvidenceSourceType,
    EvidenceLevel,
    QueryType,
    Evidence,
    EvidenceQuery,
    EvidenceFilters,
    EvidenceRetrieval,
    EvidenceWithRelevance,
    EvidenceChain,
    EvidenceStore,
    InMemoryEvidenceStore,
    create_evidence_store,
)

__all__ = [
    "EvidenceSourceType",
    "EvidenceLevel",
    "QueryType",
    "Evidence",
    "EvidenceQuery",
    "EvidenceFilters",
    "EvidenceRetrieval",
    "EvidenceWithRelevance",
    "EvidenceChain",
    "EvidenceStore",
    "InMemoryEvidenceStore",
    "create_evidence_store",
]
