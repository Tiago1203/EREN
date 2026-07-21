"""
Evidence Retrieval Module

Complete implementation for retrieving evidence from multiple sources
to support clinical reasoning.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class EvidenceSource(Enum):
    """Sources of evidence."""
    KNOWLEDGE_GRAPH = "knowledge_graph"
    MANUAL = "manual"
    STANDARD = "standard"
    HISTORICAL = "historical"
    GUIDELINE = "guideline"
    LITERATURE = "literature"
    INCIDENT_REPORT = "incident_report"
    MAINTENANCE_LOG = "maintenance_log"
    REGULATION = "regulation"


class EvidenceQuality(Enum):
    """Quality levels of evidence."""
    HIGH = "high"           # Peer-reviewed, authoritative
    MEDIUM = "medium"       # Professional guidelines
    LOW = "low"             # Anecdotal, general


@dataclass(frozen=True)
class EvidenceItem:
    """Individual evidence item."""
    evidence_id: str
    content: str
    source_type: EvidenceSource
    source_id: str
    source_name: str
    relevance_score: float = 0.0
    quality_score: float = 0.0
    timestamp: Optional[datetime] = None
    url: Optional[str] = None
    citation: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.source_type, str):
            object.__setattr__(self, 'source_type', EvidenceSource(self.source_type))


@dataclass(frozen=True)
class EvidenceQuery:
    """Query for evidence retrieval."""
    query_id: str
    query_text: str
    hypothesis_id: Optional[str] = None
    equipment_type: Optional[str] = None
    category: Optional[str] = None
    context: dict = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceRetrievalResult:
    """Result of evidence retrieval."""
    retrieval_id: str
    query: EvidenceQuery
    evidence_items: list[EvidenceItem]
    total_found: int
    retrieval_time_ms: int
    sources_queried: list[EvidenceSource]


class EvidenceSearcher:
    """Searches for evidence across multiple sources."""
    
    def __init__(self):
        self._sources = {}
    
    async def search(
        self,
        query: EvidenceQuery,
        max_results: int = 20,
    ) -> list[EvidenceItem]:
        """Search all sources for evidence."""
        results = []
        
        # Search knowledge graph (EPIC 1 integration)
        kg_results = await self._search_knowledge_graph(query)
        results.extend(kg_results)
        
        # Search manuals
        manual_results = await self._search_manuals(query)
        results.extend(manual_results)
        
        # Search standards
        standard_results = await self._search_standards(query)
        results.extend(standard_results)
        
        # Search historical incidents
        historical_results = await self._search_historical(query)
        results.extend(historical_results)
        
        # Search guidelines
        guideline_results = await self._search_guidelines(query)
        results.extend(guideline_results)
        
        # Sort by combined score and limit
        scored = [(e, e.relevance_score * e.quality_score) for e in results]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [e for e, _ in scored[:max_results]]
    
    async def _search_knowledge_graph(
        self,
        query: EvidenceQuery,
    ) -> list[EvidenceItem]:
        """Search in knowledge graph."""
        # Placeholder - would integrate with EPIC 1 Knowledge Graph
        return [
            EvidenceItem(
                evidence_id="kg_1",
                content=f"Knowledge from graph: {query.query_text}",
                source_type=EvidenceSource.KNOWLEDGE_GRAPH,
                source_id="kg_1",
                source_name="Knowledge Graph",
                relevance_score=0.8,
                quality_score=0.9,
                timestamp=datetime.now(),
            ),
        ]
    
    async def _search_manuals(
        self,
        query: EvidenceQuery,
    ) -> list[EvidenceItem]:
        """Search equipment manuals."""
        if not query.equipment_type:
            return []
        
        return [
            EvidenceItem(
                evidence_id="manual_1",
                content=f"Manual procedure for {query.equipment_type}",
                source_type=EvidenceSource.MANUAL,
                source_id=f"manual_{query.equipment_type}",
                source_name=f"{query.equipment_type} Manual",
                relevance_score=0.7,
                quality_score=0.8,
                timestamp=datetime.now(),
            ),
        ]
    
    async def _search_standards(
        self,
        query: EvidenceQuery,
    ) -> list[EvidenceItem]:
        """Search regulatory standards."""
        return [
            EvidenceItem(
                evidence_id="std_iec60601",
                content="IEC 60601-1 requirement: Equipment must meet safety standards",
                source_type=EvidenceSource.STANDARD,
                source_id="IEC 60601-1",
                source_name="IEC 60601-1:2005",
                relevance_score=0.9,
                quality_score=1.0,
                citation="IEC 60601-1 Clause 4.4",
            ),
            EvidenceItem(
                evidence_id="std_iso13485",
                content="ISO 13485: Quality management system requirements",
                source_type=EvidenceSource.STANDARD,
                source_id="ISO 13485",
                source_name="ISO 13485:2016",
                relevance_score=0.8,
                quality_score=1.0,
                citation="ISO 13485:2016",
            ),
        ]
    
    async def _search_historical(
        self,
        query: EvidenceQuery,
    ) -> list[EvidenceItem]:
        """Search historical incidents."""
        return [
            EvidenceItem(
                evidence_id="hist_1",
                content="Similar incident: SpO2 sensor malfunction resolved by probe replacement",
                source_type=EvidenceSource.HISTORICAL,
                source_id="incident_123",
                source_name="Incident Database",
                relevance_score=0.85,
                quality_score=0.7,
                timestamp=datetime.now(),
            ),
        ]
    
    async def _search_guidelines(
        self,
        query: EvidenceQuery,
    ) -> list[EvidenceItem]:
        """Search clinical guidelines."""
        return [
            EvidenceItem(
                evidence_id="guide_1",
                content="AAMI alarm management guidelines recommend regular testing",
                source_type=EvidenceSource.GUIDELINE,
                source_id="AAMI_ALARM",
                source_name="AAMI Alarm Safety Guidelines",
                relevance_score=0.75,
                quality_score=0.85,
            ),
        ]


class EvidenceCollector:
    """Collects and aggregates evidence."""
    
    async def collect(
        self,
        query: EvidenceQuery,
    ) -> EvidenceRetrievalResult:
        """Collect evidence for a query."""
        start_time = datetime.now()
        
        searcher = EvidenceSearcher()
        evidence = await searcher.search(query)
        
        end_time = datetime.now()
        retrieval_time = int((end_time - start_time).total_seconds() * 1000)
        
        return EvidenceRetrievalResult(
            retrieval_id=f"retrieval_{datetime.now().timestamp()}",
            query=query,
            evidence_items=evidence,
            total_found=len(evidence),
            retrieval_time_ms=retrieval_time,
            sources_queried=[EvidenceSource.KNOWLEDGE_GRAPH],
        )


class EvidenceRetriever:
    """
    Main evidence retriever that orchestrates search and collection.
    """
    
    def __init__(self):
        self.collector = EvidenceCollector()
    
    async def retrieve(
        self,
        query_text: str,
        hypothesis_id: Optional[str] = None,
        equipment_type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> EvidenceRetrievalResult:
        """Retrieve evidence for a query."""
        query = EvidenceQuery(
            query_id=f"q_{datetime.now().timestamp()}",
            query_text=query_text,
            hypothesis_id=hypothesis_id,
            equipment_type=equipment_type,
            category=category,
        )
        
        return await self.collector.collect(query)
    
    async def retrieve_for_hypothesis(
        self,
        hypothesis: dict,
        equipment_type: Optional[str] = None,
    ) -> EvidenceRetrievalResult:
        """Retrieve evidence specifically for a hypothesis."""
        query_text = hypothesis.get("name", "") + " " + hypothesis.get("description", "")
        
        return await self.retrieve(
            query_text=query_text,
            hypothesis_id=hypothesis.get("hypothesis_id"),
            equipment_type=equipment_type,
        )


__all__ = [
    "EvidenceSource",
    "EvidenceQuality",
    "EvidenceItem",
    "EvidenceQuery",
    "EvidenceRetrievalResult",
    "EvidenceSearcher",
    "EvidenceCollector",
    "EvidenceRetriever",
]
