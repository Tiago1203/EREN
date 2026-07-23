"""
EREN PHASE 4 — Knowledge Infrastructure

Comprehensive Knowledge Infrastructure with 12 EPICs:

EPIC 0: Foundation - Shared kernel, contracts, gateways
EPIC 1: Document Processing - PDF, DOCX, HTML, OCR
EPIC 2: Knowledge Extraction - NER, concepts, relations, ontologies
EPIC 3: Clinical Embeddings - BioBERT, PubMedBERT, ClinicalBERT
EPIC 4: Vector Indexing - Qdrant collections, payloads, indices
EPIC 5: Hybrid Retrieval - Vector + BM25 + RRF fusion
EPIC 6: Clinical RAG - Query processor, context, evidence
EPIC 7: Citation & Traceability - DOI, PubMed, source tracking
EPIC 8: Knowledge Quality - Evidence ranking, bias detection
EPIC 9: Knowledge Repository - Versions, collections, governance
EPIC 10: Sync Engine - PubMed, FDA, EMA synchronization
EPIC 11: Governance - Audit, retention, rollback, compliance

Dependencies:
- PHASE_1: Consumes Device, Incident, Knowledge, Asset contexts
- PHASE_2: Extends embeddings, retrieval, RAG
- PHASE_3: Integrates reasoning, evidence, decision engines
"""

__version__ = "2.0.0"
__phase__ = "PHASE_4"

# EPIC 0: Foundation
from core.PHASE_4.foundation import (
    DocumentFormat, KnowledgeDomain, ProcessingStatus, QualityLevel,
    EvidenceLevel, GovernanceStatus, KnowledgeEvent,
    ProcessedDocument, ExtractedKnowledge, ExtractedEntity, ExtractedConcept,
    ExtractedRelation, IndexedVector, SearchResult, KnowledgeQuery,
    RetrievalResult, KnowledgeAsset, KnowledgeVersion, TracedCitation,
    EvidenceTrace, KnowledgePackage, KnowledgeAssetFactory,
    PHASE1Gateway, PHASE2Gateway, PHASE3Gateway, PHASE5Contract,
)

# EPIC 1: Document Processing
from core.PHASE_4.epic1_document_processing import (
    TextExtractionMethod, TableExtractionStrategy, DocumentMetadata,
    PageContent, Section, ExtractedTable, FigureReference,
    ProcessingOptions, DocumentProcessingPipeline, TextNormalizer,
)

# EPIC 2: Knowledge Extraction
from core.PHASE_4.epic2_knowledge_extraction import (
    EntityType, ConceptCategory, RelationType, ExtractionModel,
    EntityCandidate, ConceptCandidate, RelationCandidate, ExtractionResult,
    OntologyMapping, BiomedicalNerRecognizer, ClinicalConceptExtractor,
    RuleBasedRelationExtractor, MedicalCodeLinker, KnowledgeExtractionPipeline,
)

# EPIC 3: Clinical Embeddings
from core.PHASE_4.epic3_clinical_embeddings import (
    EmbeddingModel, EmbeddingDimension, NormalizationMethod, EmbeddingConfig,
    CachedEmbedding, EmbeddingVersion, EmbeddingBatch, InMemoryEmbeddingCache,
    PubMedBERTProvider, ClinicalEmbeddingEngine, EmbeddingOptimizer,
)

# EPIC 4: Vector Indexing
from core.PHASE_4.epic4_vector_indexing import (
    DistanceMetric, IndexType, CollectionType, CollectionConfig,
    IndexPayload, IndexingResult, CollectionStats, InMemoryQdrantClient,
    CollectionManager, VectorIndexer, VectorSearchEngine,
)

# EPIC 5: Hybrid Retrieval
from core.PHASE_4.epic5_hybrid_retrieval import (
    RetrievalStrategy, BM25Variant, RetrievalFilters, VectorSearchParams,
    KeywordSearchParams, HybridSearchConfig, ScoredResult, FusionResult,
    BM25Searcher, HybridRetrievalEngine, QueryExpander,
)

# EPIC 6: Clinical RAG
from core.PHASE_4.epic6_clinical_rag import (
    ClinicalQueryType, QueryIntent, ProcessedQuery, ClinicalContext,
    PromptContext, ClinicalRAGResponse, ClinicalQueryProcessor,
    ClinicalContextBuilder, PromptContextBuilder, ClinicalRAGPipeline,
)

# EPIC 7: Citation & Traceability
from core.PHASE_4.epic7_citation_traceability import (
    CitationStyle, SourceType, FormattedCitation, CitationChain,
    SourceTrace, APAFormatter, VancouverFormatter, DOIResolver,
    PubMedLinker, CitationEngine, TraceabilityEngine, CitationChainBuilder,
)

# EPIC 8: Knowledge Quality
from core.PHASE_4.epic8_knowledge_quality import (
    BiasType, QualityDimension, QualityScore, BiasReport,
    DuplicateGroup, DuplicateCandidate, EvidenceRanking, RankedEvidence,
    EvidenceRanker, QualityAssessor, BiasDetector, DuplicateDetector,
)

# EPIC 9: Knowledge Repository
from core.PHASE_4.epic9_knowledge_repository import (
    RepositoryType, RepositoryStats, KnowledgeRepository,
)

# EPIC 10: Sync Engine
from core.PHASE_4.epic10_sync_engine import (
    SyncSource, SyncStatus, SyncEvent, SyncConfig, SyncJob,
    PubMedSyncSource, FDASyncSource, SyncScheduler, SyncMonitor,
)

# EPIC 11: Governance
from core.PHASE_4.epic11_governance import (
    AuditAction, RetentionPolicy, AuditEntry, ComplianceReport,
    RollbackPlan, AuditLogger, RetentionManager, RollbackManager,
    GovernanceEngine,
)
