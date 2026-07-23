"""
PHASE 4 - EPIC 0: Configuration Module

Configuración para la plataforma de conocimiento.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import os


class Environment(str, Enum):
    """Entornos de deployment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


@dataclass
class EmbeddingConfig:
    """Configuración de embeddings."""
    model: str = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    dimension: int = 768
    batch_size: int = 32
    max_sequence_length: int = 512
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    timeout_seconds: int = 60
    
    # Provider específico
    provider: str = "openai"  # openai, anthropic, ollama, transformers
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class VectorStoreConfig:
    """Configuración del vector store."""
    type: str = "qdrant"  # qdrant, weaviate, pinecone, milvus
    
    # Qdrant config
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_timeout: int = 30
    
    # Collection defaults
    default_vector_size: int = 768
    default_distance: str = "Cosine"
    hnsw_m: int = 16
    hnsw_ef_construct: int = 200
    hnsw_ef_search: int = 128
    
    # Sharding
    shard_number: int = 1
    replication_factor: int = 1


@dataclass
class DocumentProcessingConfig:
    """Configuración de procesamiento de documentos."""
    max_document_size_mb: int = 50
    max_pages: int = 1000
    enable_ocr: bool = True
    ocr_language: str = "eng"
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50
    chunking_strategy: str = "recursive"  # recursive, semantic, fixed
    
    # Extraction
    extract_tables: bool = True
    extract_figures: bool = True
    extract_metadata: bool = True
    extract_sections: bool = True
    
    # Supported formats
    supported_formats: list[str] = field(default_factory=lambda: [
        "pdf", "docx", "html", "markdown", "txt", "xml", "json"
    ])


@dataclass
class KnowledgeExtractionConfig:
    """Configuración de extracción de conocimiento."""
    # Model
    model_type: str = "transformers"  # spacy, transformers, hybrid
    model_name: str = "dmis-lab/biobert-base-cased-v1.2"
    
    # Thresholds
    min_entity_confidence: float = 0.5
    min_relation_confidence: float = 0.5
    
    # Limits
    max_entities_per_doc: int = 500
    max_concepts_per_doc: int = 200
    max_relations_per_doc: int = 100
    
    # Code linking
    link_icd10: bool = True
    link_snomed: bool = True
    link_loinc: bool = False


@dataclass
class RetrievalConfig:
    """Configuración de retrieval."""
    # Strategy
    strategy: str = "hybrid"  # vector_only, keyword_only, hybrid, rrf
    
    # Vector search
    vector_weight: float = 0.7
    top_k_vector: int = 10
    min_vector_score: float = 0.5
    
    # Keyword search (BM25)
    keyword_weight: float = 0.3
    top_k_keyword: int = 10
    min_keyword_score: float = 0.3
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    
    # RRF
    rrf_k: int = 60
    
    # Query expansion
    enable_query_expansion: bool = True
    expansion_synonyms: int = 3


@dataclass
class RAGConfig:
    """Configuración del pipeline RAG."""
    # Prompt
    max_context_tokens: int = 4000
    min_citations: int = 3
    max_citations: int = 20
    
    # Generation
    default_temperature: float = 0.3
    max_generation_length: int = 2000
    enable_streaming: bool = False
    
    # Safety
    enable_safety_check: bool = True
    safety_threshold: float = 0.8
    
    # Confidence
    confidence_high_threshold: float = 0.8
    confidence_medium_threshold: float = 0.5


@dataclass
class CitationConfig:
    """Configuración de citación."""
    # Style
    default_style: str = "apa"  # apa, vancouver, mla, chicago
    
    # Resolution
    enable_doi_resolution: bool = True
    enable_pubmed_resolution: bool = True
    resolve_timeout_seconds: int = 10
    
    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400
    
    # Sources
    prefer_peer_reviewed: bool = True
    min_evidence_level: str = "4"  # 1a, 1b, 2a, 2b, 3, 4, 5


@dataclass
class QualityConfig:
    """Configuración de calidad."""
    # Thresholds
    quality_high_threshold: float = 0.8
    quality_medium_threshold: float = 0.6
    quality_low_threshold: float = 0.4
    
    # Bias detection
    enable_bias_detection: bool = True
    bias_severity_threshold: float = 0.6
    
    # Duplicate detection
    enable_duplicate_detection: bool = True
    duplicate_similarity_threshold: float = 0.9
    
    # Evidence ranking
    evidence_relevance_weight: float = 0.4
    evidence_quality_weight: float = 0.4
    evidence_level_weight: float = 0.2


@dataclass
class GovernanceConfig:
    """Configuración de gobernanza."""
    # Retention
    default_retention_years: int = 7
    short_term_retention_years: int = 2
    review_interval_months: int = 12
    
    # Audit
    enable_audit_logging: bool = True
    audit_retention_days: int = 2555  # 7 years
    log_access: bool = True
    
    # Approval
    require_approval_for_publish: bool = True
    approver_roles: list[str] = field(default_factory=lambda: [
        "clinical_engineer", "biomedical_engineer", "admin"
    ])


@dataclass
class SyncConfig:
    """Configuración de sincronización."""
    # Schedule
    enable_sync: bool = True
    sync_interval_seconds: int = 3600  # 1 hour
    sync_on_startup: bool = True
    
    # Batch
    batch_size: int = 100
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    
    # Sources
    sync_pubmed: bool = True
    sync_fda: bool = True
    sync_ema: bool = True
    sync_guidelines: bool = True
    
    # API keys
    pubmed_api_key: Optional[str] = None
    fda_api_key: Optional[str] = None


@dataclass
class LoggingConfig:
    """Configuración de logging."""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    format: str = "json"  # json, text
    enable_request_logging: bool = True
    enable_event_logging: bool = True
    log_file: Optional[str] = None


@dataclass
class ObservabilityConfig:
    """Configuración de observabilidad."""
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_health_check: bool = True
    
    # Metrics
    metrics_port: int = 9090
    metrics_prefix: str = "eren_phase4"
    
    # Tracing
    tracing_endpoint: Optional[str] = None
    tracing_sample_rate: float = 0.1


@dataclass
class PHASE4Config:
    """Configuración principal de PHASE 4."""
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Service
    service_name: str = "eren-phase4"
    service_version: str = "2.0.0"
    
    # Components
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    document_processing: DocumentProcessingConfig = field(default_factory=DocumentProcessingConfig)
    knowledge_extraction: KnowledgeExtractionConfig = field(default_factory=KnowledgeExtractionConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    citation: CitationConfig = field(default_factory=CitationConfig)
    quality: QualityConfig = field(default_factory=QualityConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    sync: SyncConfig = field(default_factory=SyncConfig)
    
    # Observability
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    
    @classmethod
    def from_env(cls) -> "PHASE4Config":
        """Crea configuración desde variables de entorno."""
        env = os.getenv("ENVIRONMENT", "development")
        
        config = cls(
            environment=Environment(env),
            debug=env in ["development", "test"],
        )
        
        # Override with env vars
        if api_key := os.getenv("EMBEDDING_API_KEY"):
            config.embedding.api_key = api_key
        
        if qdrant_url := os.getenv("QDRANT_URL"):
            config.vector_store.qdrant_url = qdrant_url
        
        if qdrant_key := os.getenv("QDRANT_API_KEY"):
            config.vector_store.qdrant_api_key = qdrant_key
        
        return config
    
    @classmethod
    def production(cls) -> "PHASE4Config":
        """Crea configuración de producción."""
        config = cls(
            environment=Environment.PRODUCTION,
            debug=False,
        )
        config.logging.level = "WARNING"
        config.observability.enable_tracing = True
        return config
    
    @classmethod
    def development(cls) -> "PHASE4Config":
        """Crea configuración de desarrollo."""
        config = cls(
            environment=Environment.DEVELOPMENT,
            debug=True,
        )
        config.logging.level = "DEBUG"
        return config
    
    @classmethod
    def test(cls) -> "PHASE4Config":
        """Crea configuración de testing."""
        return cls(
            environment=Environment.TEST,
            debug=True,
        )


__all__ = [
    "Environment",
    "EmbeddingConfig",
    "VectorStoreConfig",
    "DocumentProcessingConfig",
    "KnowledgeExtractionConfig",
    "RetrievalConfig",
    "RAGConfig",
    "CitationConfig",
    "QualityConfig",
    "GovernanceConfig",
    "SyncConfig",
    "LoggingConfig",
    "ObservabilityConfig",
    "PHASE4Config",
]
