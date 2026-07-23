"""
Evidence Store Module

Provides evidence storage and retrieval for clinical intelligence.
Supports multiple evidence sources: literature, standards, regulatory, guidelines, and real-world evidence.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Evidence Source Types
# =============================================================================


class EvidenceSourceType(str, Enum):
    """Types of evidence sources."""
    
    PUBMED = "pubmed"
    CLINICAL_TRIALS = "clinical_trials"
    COCHRANE = "cochrane"
    IEEE = "ieee"
    ISO = "iso"
    IEC = "iec"
    FDA = "fda"
    ECRI = "ecri"
    WHO = "who"
    NICE = "nice"
    AHRQ = "ahrq"
    REAL_WORLD = "real_world"
    INTERNAL = "internal"
    MANUAL = "manual"
    KNOWLEDGE_ARTICLE = "knowledge_article"
    DEVICE_MANUAL = "device_manual"
    REGULATORY = "regulatory"


class EvidenceLevel(str, Enum):
    """Evidence quality levels (Oxford Hierarchy)."""
    
    LEVEL_1A = "1a"  # Systematic review of RCTs
    LEVEL_1B = "1b"  # Individual RCT (with narrow confidence interval)
    LEVEL_2A = "2a"  # Systematic review of cohort studies
    LEVEL_2B = "2b"  # Individual cohort study (including low quality RCT)
    LEVEL_3A = "3a"  # Systematic review of case-control studies
    LEVEL_3B = "3b"  # Individual case-control study
    LEVEL_4 = "4"    # Case series
    LEVEL_5 = "5"    # Expert opinion, bench research
    
    # Custom for clinical engineering
    DEVICE_SPEC = "device_spec"  # Device specifications
    MANUFACTURER_DATA = "manufacturer_data"
    REGULATORY_CLEARANCE = "regulatory_clearance"
    CLINICAL_EXPERTISE = "clinical_expertise"
    INTERNAL_STANDARD = "internal_standard"


class QueryType(str, Enum):
    """Evidence query types."""
    
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    BOOLEAN = "boolean"
    FILTERED = "filtered"
    TEMPORAL = "temporal"
    RELATIONAL = "relational"


# =============================================================================
# Evidence Models
# =============================================================================


@dataclass(frozen=True)
class Evidence:
    """Clinical evidence from a source."""
    
    evidence_id: str
    source_type: EvidenceSourceType
    source_id: str
    
    # Content
    title: str
    abstract: str = ""
    content: str = ""
    
    # Quality
    evidence_level: EvidenceLevel = EvidenceLevel.LEVEL_5
    quality_score: float = 0.0
    
    # Metadata
    authors: list[str] = field(default_factory=list)
    publication_date: str = ""
    journal: str = ""
    volume: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    
    # Clinical metadata
    medical_specialty: str = ""
    icd_codes: list[str] = field(default_factory=list)
    snomed_codes: list[str] = field(default_factory=list)
    loinc_codes: list[str] = field(default_factory=list)
    
    # Engineering metadata
    device_categories: list[str] = field(default_factory=list)
    manufacturers: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    
    # Relevance
    relevance_score: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Additional metadata
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate evidence."""
        if not self.title:
            raise ValueError("Evidence title is required")
        if not self.source_id:
            raise ValueError("Evidence source_id is required")
    
    @classmethod
    def create(
        cls,
        source_type: EvidenceSourceType,
        source_id: str,
        title: str,
        **kwargs,
    ) -> Evidence:
        """Factory method to create evidence with auto-generated ID."""
        return cls(
            evidence_id=str(uuid.uuid4()),
            source_type=source_type,
            source_id=source_id,
            title=title,
            **kwargs,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "evidence_id": self.evidence_id,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "title": self.title,
            "abstract": self.abstract,
            "content": self.content,
            "evidence_level": self.evidence_level.value,
            "quality_score": self.quality_score,
            "authors": self.authors,
            "publication_date": self.publication_date,
            "journal": self.journal,
            "doi": self.doi,
            "url": self.url,
            "medical_specialty": self.medical_specialty,
            "icd_codes": self.icd_codes,
            "snomed_codes": self.snomed_codes,
            "loinc_codes": self.loinc_codes,
            "device_categories": self.device_categories,
            "manufacturers": self.manufacturers,
            "standards": self.standards,
            "relevance_score": self.relevance_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class EvidenceQuery:
    """Query for evidence retrieval."""
    
    query_id: str
    query_text: str
    query_type: QueryType = QueryType.HYBRID
    
    # Filters
    source_types: list[EvidenceSourceType] | None = None
    evidence_levels: list[EvidenceLevel] | None = None
    
    # Date range
    date_from: str | None = None
    date_to: str | None = None
    
    # Medical filters
    medical_specialties: list[str] | None = None
    icd_codes: list[str] | None = None
    snomed_codes: list[str] | None = None
    
    # Engineering filters
    device_categories: list[str] | None = None
    manufacturers: list[str] | None = None
    standards: list[str] | None = None
    
    # Results
    max_results: int = 10
    min_relevance: float = 0.5
    
    # Context
    tenant_id: str = ""
    user_id: str = ""
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    @classmethod
    def create(
        cls,
        query_text: str,
        query_type: QueryType = QueryType.HYBRID,
        **kwargs,
    ) -> EvidenceQuery:
        """Factory method to create query with auto-generated ID."""
        return cls(
            query_id=str(uuid.uuid4()),
            query_text=query_text,
            query_type=query_type,
            **kwargs,
        )


@dataclass(frozen=True)
class EvidenceFilters:
    """Filters for evidence queries."""
    
    # Source filters
    include_sources: list[EvidenceSourceType] | None = None
    exclude_sources: list[EvidenceSourceType] | None = None
    
    # Level filters
    min_level: EvidenceLevel | None = None
    max_level: EvidenceLevel | None = None
    
    # Date filters
    published_after: str | None = None
    published_before: str | None = None
    
    # Specialty filters
    specialties: list[str] | None = None
    
    # Code filters
    icd_codes: list[str] | None = None
    snomed_codes: list[str] | None = None
    loinc_codes: list[str] | None = None
    
    # Engineering filters
    device_categories: list[str] | None = None
    manufacturers: list[str] | None = None
    standards: list[str] | None = None
    
    # Quality filters
    min_quality_score: float = 0.0
    
    def matches(self, evidence: Evidence) -> bool:
        """Check if evidence matches filters."""
        # Source filter
        if self.include_sources and evidence.source_type not in self.include_sources:
            return False
        if self.exclude_sources and evidence.source_type in self.exclude_sources:
            return False
        
        # Level filter
        if self.min_level:
            level_order = [e.value for e in EvidenceLevel]
            if evidence.evidence_level.value not in level_order[:level_order.index(self.min_level.value) + 1]:
                return False
        
        # Quality filter
        if evidence.quality_score < self.min_quality_score:
            return False
        
        # Date filter
        if self.published_after and evidence.publication_date < self.published_after:
            return False
        if self.published_before and evidence.publication_date > self.published_before:
            return False
        
        # Specialty filter
        if self.specialties and evidence.medical_specialty not in self.specialties:
            return False
        
        # Code filters
        if self.icd_codes and not any(c in evidence.icd_codes for c in self.icd_codes):
            return False
        if self.snomed_codes and not any(c in evidence.snomed_codes for c in self.snomed_codes):
            return False
        
        # Engineering filters
        if self.device_categories and not any(c in evidence.device_categories for c in self.device_categories):
            return False
        if self.manufacturers and evidence.manufacturers and not any(m in evidence.manufacturers for m in self.manufacturers):
            return False
        if self.standards and not any(s in evidence.standards for s in self.standards):
            return False
        
        return True


@dataclass
class EvidenceRetrieval:
    """Result of evidence retrieval operation."""
    
    query: EvidenceQuery
    results: list[Evidence]
    
    # Statistics
    total_found: int = 0
    total_returned: int = 0
    retrieval_time_ms: int = 0
    
    # Quality metrics
    avg_quality_score: float = 0.0
    level_distribution: dict[str, int] = field(default_factory=dict)
    source_distribution: dict[str, int] = field(default_factory=dict)
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        """Calculate statistics."""
        self.total_found = self.total_returned = len(self.results)
        
        if self.results:
            self.avg_quality_score = sum(e.quality_score for e in self.results) / len(self.results)
            
            for e in self.results:
                level_key = e.evidence_level.value
                self.level_distribution[level_key] = self.level_distribution.get(level_key, 0) + 1
                
                source_key = e.source_type.value
                self.source_distribution[source_key] = self.source_distribution.get(source_key, 0) + 1
    
    def filter_by_level(self, min_level: EvidenceLevel) -> EvidenceRetrieval:
        """Filter results by minimum evidence level."""
        filtered = [e for e in self.results if e.evidence_level.value <= min_level.value]
        return EvidenceRetrieval(
            query=self.query,
            results=filtered,
            total_found=self.total_found,
            retrieval_time_ms=self.retrieval_time_ms,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_id": self.query.query_id,
            "query_text": self.query.query_text,
            "total_found": self.total_found,
            "total_returned": self.total_returned,
            "retrieval_time_ms": self.retrieval_time_ms,
            "avg_quality_score": self.avg_quality_score,
            "level_distribution": self.level_distribution,
            "source_distribution": self.source_distribution,
            "results": [e.to_dict() for e in self.results],
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class EvidenceWithRelevance:
    """Evidence with calculated relevance score."""
    
    evidence: Evidence
    relevance_score: float
    relevance_factors: dict[str, float] = field(default_factory=dict)
    
    # Why this evidence was retrieved
    matched_terms: list[str] = field(default_factory=list)
    matched_codes: list[str] = field(default_factory=list)
    matched_categories: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "evidence": self.evidence.to_dict(),
            "relevance_score": self.relevance_score,
            "relevance_factors": self.relevance_factors,
            "matched_terms": self.matched_terms,
            "matched_codes": self.matched_codes,
            "matched_categories": self.matched_categories,
        }


@dataclass
class EvidenceChain:
    """Chain of evidence for clinical reasoning."""
    
    chain_id: str
    primary_evidence: Evidence
    
    # Supporting evidence
    supporting_evidence: list[Evidence] = field(default_factory=list)
    contradicting_evidence: list[Evidence] = field(default_factory=list)
    
    # Chain metadata
    chain_strength: float = 0.0  # 0.0-1.0
    consistency_score: float = 0.0  # 0.0-1.0
    
    # Clinical context
    clinical_question: str = ""
    clinical_context: str = ""
    
    # Reasoning
    reasoning_steps: list[str] = field(default_factory=list)
    conclusion: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    @classmethod
    def create(
        cls,
        primary_evidence: Evidence,
        clinical_question: str = "",
    ) -> EvidenceChain:
        """Factory method to create evidence chain."""
        return cls(
            chain_id=str(uuid.uuid4()),
            primary_evidence=primary_evidence,
            clinical_question=clinical_question,
        )
    
    def add_supporting(self, evidence: Evidence) -> None:
        """Add supporting evidence."""
        self.supporting_evidence.append(evidence)
        self._recalculate_strength()
    
    def add_contradicting(self, evidence: Evidence) -> None:
        """Add contradicting evidence."""
        self.contradicting_evidence.append(evidence)
        self._recalculate_strength()
    
    def _recalculate_strength(self) -> None:
        """Recalculate chain strength based on evidence."""
        if not self.supporting_evidence and not self.contradicting_evidence:
            self.chain_strength = self.primary_evidence.quality_score
            return
        
        supporting_avg = sum(e.quality_score for e in self.supporting_evidence) / len(self.supporting_evidence) if self.supporting_evidence else 0
        contradicting_avg = sum(e.quality_score for e in self.contradicting_evidence) / len(self.contradicting_evidence) if self.contradicting_evidence else 0
        
        # Strength decreases with contradicting evidence
        self.chain_strength = (supporting_avg - contradicting_avg * 0.5) / 1.5
        self.chain_strength = max(0.0, min(1.0, self.chain_strength))
        
        # Consistency: how many supporting vs contradicting
        total = len(self.supporting_evidence) + len(self.contradicting_evidence)
        if total > 0:
            self.consistency_score = len(self.supporting_evidence) / total
        else:
            self.consistency_score = 1.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chain_id": self.chain_id,
            "primary_evidence": self.primary_evidence.to_dict(),
            "supporting_evidence": [e.to_dict() for e in self.supporting_evidence],
            "contradicting_evidence": [e.to_dict() for e in self.contradicting_evidence],
            "chain_strength": self.chain_strength,
            "consistency_score": self.consistency_score,
            "clinical_question": self.clinical_question,
            "clinical_context": self.clinical_context,
            "reasoning_steps": self.reasoning_steps,
            "conclusion": self.conclusion,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# Evidence Store Protocol
# =============================================================================


class EvidenceStore(Protocol):
    """Protocol for evidence storage implementations."""
    
    async def store(self, evidence: Evidence) -> str:
        """Store evidence and return ID."""
        ...
    
    async def retrieve(
        self,
        query: EvidenceQuery,
    ) -> EvidenceRetrieval:
        """Retrieve evidence matching query."""
        ...
    
    async def get(self, evidence_id: str) -> Evidence | None:
        """Get evidence by ID."""
        ...
    
    async def update(self, evidence: Evidence) -> bool:
        """Update existing evidence."""
        ...
    
    async def delete(self, evidence_id: str) -> bool:
        """Delete evidence by ID."""
        ...
    
    async def search_by_code(
        self,
        code_type: str,
        codes: list[str],
    ) -> list[Evidence]:
        """Search evidence by medical codes."""
        ...
    
    async def search_by_category(
        self,
        category: str,
        subcategories: list[str] | None = None,
    ) -> list[Evidence]:
        """Search evidence by category."""
        ...
    
    async def get_related(
        self,
        evidence_id: str,
        max_results: int = 5,
    ) -> list[Evidence]:
        """Get related evidence."""
        ...
    
    async def build_chain(
        self,
        evidence_id: str,
        include_supporting: bool = True,
        include_contradicting: bool = True,
    ) -> EvidenceChain:
        """Build evidence chain for an evidence item."""
        ...


# =============================================================================
# In-Memory Evidence Store Implementation
# =============================================================================


class InMemoryEvidenceStore:
    """In-memory implementation of EvidenceStore for testing and development."""
    
    def __init__(self):
        """Initialize in-memory store."""
        self._store: dict[str, Evidence] = {}
        self._code_index: dict[str, dict[str, list[str]]] = {}  # code_type -> code -> [evidence_ids]
        self._category_index: dict[str, set[str]] = {}  # category -> evidence_ids
    
    async def store(self, evidence: Evidence) -> str:
        """Store evidence."""
        self._store[evidence.evidence_id] = evidence
        self._index_evidence(evidence)
        return evidence.evidence_id
    
    async def retrieve(self, query: EvidenceQuery) -> EvidenceRetrieval:
        """Retrieve evidence matching query."""
        import time
        start = time.time()
        
        results = []
        for evidence in self._store.values():
            # Check relevance
            if self._matches_query(evidence, query):
                if evidence.relevance_score >= query.min_relevance:
                    results.append(evidence)
        
        # Sort by relevance
        results.sort(key=lambda e: e.relevance_score, reverse=True)
        
        # Limit results
        results = results[:query.max_results]
        
        retrieval_time_ms = int((time.time() - start) * 1000)
        
        return EvidenceRetrieval(
            query=query,
            results=results,
            retrieval_time_ms=retrieval_time_ms,
        )
    
    async def get(self, evidence_id: str) -> Evidence | None:
        """Get evidence by ID."""
        return self._store.get(evidence_id)
    
    async def update(self, evidence: Evidence) -> bool:
        """Update existing evidence."""
        if evidence.evidence_id in self._store:
            self._store[evidence.evidence_id] = evidence
            return True
        return False
    
    async def delete(self, evidence_id: str) -> bool:
        """Delete evidence by ID."""
        if evidence_id in self._store:
            del self._store[evidence_id]
            return True
        return False
    
    async def search_by_code(
        self,
        code_type: str,
        codes: list[str],
    ) -> list[Evidence]:
        """Search evidence by medical codes."""
        evidence_ids: set[str] | None = None
        
        for code in codes:
            if code_type in self._code_index and code in self._code_index[code_type]:
                ids = set(self._code_index[code_type][code])
                if evidence_ids is None:
                    evidence_ids = ids
                else:
                    evidence_ids &= ids
        
        if evidence_ids is None:
            return []
        
        return [self._store[eid] for eid in evidence_ids if eid in self._store]
    
    async def search_by_category(
        self,
        category: str,
        subcategories: list[str] | None = None,
    ) -> list[Evidence]:
        """Search evidence by category."""
        if category not in self._category_index:
            return []
        
        evidence_ids = self._category_index[category]
        results = [self._store[eid] for eid in evidence_ids if eid in self._store]
        
        if subcategories:
            results = [
                e for e in results
                if e.medical_specialty in subcategories or e.device_categories
                if any(c in subcategories for c in e.device_categories)
            ]
        
        return results
    
    async def get_related(
        self,
        evidence_id: str,
        max_results: int = 5,
    ) -> list[Evidence]:
        """Get related evidence."""
        evidence = self._store.get(evidence_id)
        if not evidence:
            return []
        
        # Simple relevance-based related search
        related = []
        for other in self._store.values():
            if other.evidence_id == evidence_id:
                continue
            
            # Check shared codes
            shared_icd = set(evidence.icd_codes) & set(other.icd_codes)
            shared_snomed = set(evidence.snomed_codes) & set(other.snomed_codes)
            
            if shared_icd or shared_snomed:
                related.append((other, len(shared_icd) + len(shared_snomed)))
        
        related.sort(key=lambda x: x[1], reverse=True)
        return [e for e, _ in related[:max_results]]
    
    async def build_chain(
        self,
        evidence_id: str,
        include_supporting: bool = True,
        include_contradicting: bool = True,
    ) -> EvidenceChain:
        """Build evidence chain."""
        evidence = self._store.get(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        chain = EvidenceChain.create(evidence)
        
        # Find supporting evidence (same codes, higher level)
        if include_supporting:
            for other in self._store.values():
                if other.evidence_id == evidence_id:
                    continue
                if set(evidence.icd_codes) & set(other.icd_codes):
                    if other.evidence_level.value < evidence.evidence_level.value:
                        chain.add_supporting(other)
        
        chain._recalculate_strength()
        return chain
    
    def _index_evidence(self, evidence: Evidence) -> None:
        """Index evidence for fast search."""
        # ICD codes
        if evidence.icd_codes:
            self._code_index.setdefault("icd", {})
            for code in evidence.icd_codes:
                self._code_index["icd"].setdefault(code, []).append(evidence.evidence_id)
        
        # SNOMED codes
        if evidence.snomed_codes:
            self._code_index.setdefault("snomed", {})
            for code in evidence.snomed_codes:
                self._code_index["snomed"].setdefault(code, []).append(evidence.evidence_id)
        
        # LOINC codes
        if evidence.loinc_codes:
            self._code_index.setdefault("loinc", {})
            for code in evidence.loinc_codes:
                self._code_index["loinc"].setdefault(code, []).append(evidence.evidence_id)
        
        # Medical specialty
        if evidence.medical_specialty:
            self._category_index.setdefault(evidence.medical_specialty, set()).add(evidence.evidence_id)
    
    def _matches_query(self, evidence: Evidence, query: EvidenceQuery) -> bool:
        """Check if evidence matches query."""
        # Source filter
        if query.source_types and evidence.source_type not in query.source_types:
            return False
        
        # Level filter
        if query.evidence_levels and evidence.evidence_level not in query.evidence_levels:
            return False
        
        # Medical specialty filter
        if query.medical_specialties and evidence.medical_specialty not in query.medical_specialties:
            return False
        
        # ICD code filter
        if query.icd_codes and not any(c in evidence.icd_codes for c in query.icd_codes):
            return False
        
        # SNOMED code filter
        if query.snomed_codes and not any(c in evidence.snomed_codes for c in query.snomed_codes):
            return False
        
        # Device category filter
        if query.device_categories and not any(c in evidence.device_categories for c in query.device_categories):
            return False
        
        # Manufacturer filter
        if query.manufacturers and evidence.manufacturers and not any(m in evidence.manufacturers for m in query.manufacturers):
            return False
        
        return True


# =============================================================================
# Factory Function
# =============================================================================


def create_evidence_store(store_type: str = "memory") -> EvidenceStore:
    """Create evidence store instance.
    
    Args:
        store_type: Type of store ("memory", "qdrant", "postgres")
    
    Returns:
        EvidenceStore implementation
    """
    if store_type == "memory":
        return InMemoryEvidenceStore()
    
    # Future implementations
    # elif store_type == "qdrant":
    #     return QdrantEvidenceStore(...)
    # elif store_type == "postgres":
    #     return PostgresEvidenceStore(...)
    
    raise ValueError(f"Unknown store type: {store_type}")
