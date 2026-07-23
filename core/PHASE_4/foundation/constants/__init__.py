"""
PHASE 4 - EPIC 0: Constants Module

Constantes globales para la plataforma de conocimiento.
"""

from __future__ import annotations


# =============================================================================
# VERSION CONSTANTS
# =============================================================================

VERSION = "2.0.0"
PHASE = "PHASE_4"
EPIC = "EPIC_0"


# =============================================================================
# EMBEDDING CONSTANTS
# =============================================================================

DEFAULT_EMBEDDING_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
DEFAULT_EMBEDDING_DIMENSION = 768
MAX_EMBEDDING_BATCH_SIZE = 100
EMBEDDING_CACHE_TTL_SECONDS = 3600


# =============================================================================
# VECTOR INDEX CONSTANTS
# =============================================================================

DEFAULT_VECTOR_SIZE = 768
DEFAULT_TOP_K = 10
DEFAULT_MIN_SCORE = 0.5
MAX_RESULTS = 100
HNSW_M_PARAM = 16
HNSW_EF_CONSTRUCT = 200
HNSW_EF_SEARCH = 128


# =============================================================================
# RETRIEVAL CONSTANTS
# =============================================================================

BM25_K1 = 1.5
BM25_B = 0.75
RRF_K_PARAM = 60
HYBRID_VECTOR_WEIGHT = 0.7
HYBRID_KEYWORD_WEIGHT = 0.3


# =============================================================================
# DOCUMENT PROCESSING CONSTANTS
# =============================================================================

MAX_DOCUMENT_SIZE_MB = 50
MAX_PAGES = 1000
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "pt", "zh", "ja"]


# =============================================================================
# KNOWLEDGE EXTRACTION CONSTANTS
# =============================================================================

MIN_CONFIDENCE_THRESHOLD = 0.5
MAX_ENTITIES_PER_DOCUMENT = 500
MAX_CONCEPTS_PER_DOCUMENT = 200
MAX_RELATIONS_PER_DOCUMENT = 100


# =============================================================================
# QUALITY CONSTANTS
# =============================================================================

QUALITY_THRESHOLD_HIGH = 0.8
QUALITY_THRESHOLD_MEDIUM = 0.6
QUALITY_THRESHOLD_LOW = 0.4
BIAS_SEVERITY_THRESHOLD = 0.6
DUPLICATE_SIMILARITY_THRESHOLD = 0.9


# =============================================================================
# GOVERNANCE CONSTANTS
# =============================================================================

RETENTION_STANDARD_YEARS = 7
RETENTION_SHORT_YEARS = 2
RETENTION_REVIEW_MONTHS = 12
AUDIT_LOG_RETENTION_DAYS = 2555  # 7 years


# =============================================================================
# SYNC CONSTANTS
# =============================================================================

SYNC_INTERVAL_SECONDS = 3600  # 1 hour
SYNC_BATCH_SIZE = 100
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 60


# =============================================================================
# RAG PIPELINE CONSTANTS
# =============================================================================

MAX_CONTEXT_TOKENS = 4000
MIN_CITATIONS = 3
DEFAULT_TEMPERATURE = 0.3
MAX_GENERATION_LENGTH = 2000


# =============================================================================
# CITATION CONSTANTS
# =============================================================================

MAX_CITATIONS_PER_RESPONSE = 20
CITATION_CACHE_TTL_SECONDS = 86400  # 24 hours
DOI_RESOLVER_TIMEOUT_SECONDS = 10
PUBMED_RESOLVER_TIMEOUT_SECONDS = 10


# =============================================================================
# PAGINATION CONSTANTS
# =============================================================================

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_PAGINATION_PAGES = 50


# =============================================================================
# CACHE CONSTANTS
# =============================================================================

CACHE_MAX_SIZE = 10000
CACHE_TTL_SECONDS = 3600
CACHE_PREFIX = "eren:phase4:"


# =============================================================================
# TIMEOUT CONSTANTS
# =============================================================================

DEFAULT_TIMEOUT_SECONDS = 30
LONG_OPERATION_TIMEOUT_SECONDS = 300
EMBEDDING_TIMEOUT_SECONDS = 60
INDEXING_TIMEOUT_SECONDS = 120


# =============================================================================
# ERROR CONSTANTS
# =============================================================================

ERROR_CODE_PREFIX = "P4"
ERROR_KNOWLEDGE_NOT_FOUND = f"{ERROR_CODE_PREFIX}001"
ERROR_DOCUMENT_PARSE_FAILED = f"{ERROR_CODE_PREFIX}002"
ERROR_EMBEDDING_FAILED = f"{ERROR_CODE_PREFIX}003"
ERROR_INDEX_FAILED = f"{ERROR_CODE_PREFIX}004"
ERROR_RETRIEVAL_FAILED = f"{ERROR_CODE_PREFIX}005"
ERROR_CITATION_FAILED = f"{ERROR_CODE_PREFIX}006"
ERROR_QUALITY_ASSESSMENT_FAILED = f"{ERROR_CODE_PREFIX}007"
ERROR_SYNC_FAILED = f"{ERROR_CODE_PREFIX}008"
ERROR_GOVERNANCE_FAILED = f"{ERROR_CODE_PREFIX}009"


__all__ = [
    "VERSION",
    "PHASE",
    "EPIC",
    # Embedding
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_EMBEDDING_DIMENSION",
    "MAX_EMBEDDING_BATCH_SIZE",
    "EMBEDDING_CACHE_TTL_SECONDS",
    # Vector Index
    "DEFAULT_VECTOR_SIZE",
    "DEFAULT_TOP_K",
    "DEFAULT_MIN_SCORE",
    "MAX_RESULTS",
    # Retrieval
    "BM25_K1",
    "BM25_B",
    "RRF_K_PARAM",
    "HYBRID_VECTOR_WEIGHT",
    "HYBRID_KEYWORD_WEIGHT",
    # Document
    "MAX_DOCUMENT_SIZE_MB",
    "MAX_PAGES",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
    # Quality
    "QUALITY_THRESHOLD_HIGH",
    "QUALITY_THRESHOLD_MEDIUM",
    "QUALITY_THRESHOLD_LOW",
    # Governance
    "RETENTION_STANDARD_YEARS",
    "RETENTION_SHORT_YEARS",
    "AUDIT_LOG_RETENTION_DAYS",
    # Sync
    "SYNC_INTERVAL_SECONDS",
    "SYNC_BATCH_SIZE",
    # RAG
    "MAX_CONTEXT_TOKENS",
    "MIN_CITATIONS",
    # Citation
    "MAX_CITATIONS_PER_RESPONSE",
    # Cache
    "CACHE_MAX_SIZE",
    "CACHE_PREFIX",
]
