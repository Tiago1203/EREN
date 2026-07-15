"""RAG Pipeline types for EREN OS.

Types for the Cognitive RAG Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Enums
# =============================================================================


class RetrievalStrategy(str, Enum):
    """Retrieval strategies for RAG."""

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    GRAPH = "graph"
    BM25 = "bm25"
    DENSE = "dense"
    SPARSE = "sparse"
    METADATA = "metadata"
    TEMPORAL = "temporal"


class ResponseFormat(str, Enum):
    """Response formats."""

    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


class ConfidenceLevel(str, Enum):
    """Confidence levels for responses."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class RerankStrategy(str, Enum):
    """Reranking strategies for retrieved chunks."""

    CROSS_ENCODER = "cross_encoder"
    DIVERSITY = "diversity"
    MMR = "mmr"  # Maximal Marginal Relevance
    RRF = "rrf"  # Reciprocal Rank Fusion
    WEIGHTED = "weighted"


class DocumentType(str, Enum):
    """Supported document types for ingestion."""

    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    EXCEL = "excel"
    MARKDOWN = "markdown"
    TXT = "txt"
    HTML = "html"
    FHIR = "fhir"
    HL7 = "hl7"
    DICOM = "dicom"
    JSON = "json"
    CSV = "csv"
    XML = "xml"


# =============================================================================
# RAG Query
# =============================================================================


@dataclass
class RAGQuery:
    """A RAG query from user."""

    query_id: str
    question: str
    context: dict = field(default_factory=dict)
    conversation_id: str = ""
    user_id: str = ""
    session_id: str = ""

    # Retrieval options
    top_k: int = 10
    retrieval_strategy: RetrievalStrategy = RetrievalStrategy.SEMANTIC
    min_relevance_score: float = 0.5

    # Response options
    response_format: ResponseFormat = ResponseFormat.TEXT
    include_citations: bool = True
    include_confidence: bool = True

    # Budget
    max_tokens: int = 4000

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Retrieved Context
# =============================================================================


@dataclass
class RetrievedChunk:
    """A retrieved context chunk."""

    chunk_id: str
    content: str
    document_id: str
    title: str = ""

    # Relevance
    relevance_score: float = 0.0
    rank: int = 0

    # Source info
    source_type: str = ""
    source_uri: str = ""
    author: str = ""
    institution: str = ""
    hospital: str = ""

    # Metadata
    language: str = "en"
    medical_specialty: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    # Provenance
    asset_id: str = ""
    version: str = ""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class RetrievalResult:
    """Result from retrieval engine."""

    query_id: str
    chunks: list[RetrievedChunk]
    total_chunks: int = 0
    retrieval_time_ms: int = 0

    # Deduplication
    unique_chunks: int = 0
    duplicate_count: int = 0

    # Statistics
    avg_relevance: float = 0.0
    max_relevance: float = 0.0
    min_relevance: float = 0.0


# =============================================================================
# RAG Context
# =============================================================================


@dataclass
class RAGContext:
    """Context for RAG pipeline."""

    query: RAGQuery

    # Retrieved content
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)

    # Conversation memory
    conversation_history: list[dict] = field(default_factory=list)

    # Built context
    context_text: str = ""
    context_tokens: int = 0

    # Budget
    available_tokens: int = 0
    used_tokens: int = 0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Prompt
# =============================================================================


@dataclass
class RAGPrompt:
    """Built RAG prompt."""

    system_prompt: str
    user_prompt: str
    context: str

    # Token counts
    system_tokens: int = 0
    user_tokens: int = 0
    context_tokens: int = 0
    total_tokens: int = 0

    # Configuration
    model: str = ""
    max_tokens: int = 4000

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Response
# =============================================================================


@dataclass
class Citation:
    """Citation for a piece of information."""

    citation_id: str
    text: str
    chunk_id: str
    document_id: str
    title: str = ""

    # Location
    start_char: int = 0
    end_char: int = 0

    # Source
    source_type: str = ""
    source_uri: str = ""
    author: str = ""
    institution: str = ""
    published_date: str = ""

    # Metadata
    relevance_score: float = 0.0
    page_number: str = ""
    url: str = ""


@dataclass
class RAGResponse:
    """RAG response to user."""

    query_id: str
    response_id: str

    # Content
    answer: str
    format: ResponseFormat = ResponseFormat.TEXT

    # Quality
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    confidence_score: float = 0.0

    # Citations
    citations: list[Citation] = field(default_factory=list)

    # Sources used
    sources_used: list[str] = field(default_factory=list)

    # Tokens
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Model info
    model_used: str = ""
    provider_used: str = ""

    # Timing
    retrieval_time_ms: int = 0
    generation_time_ms: int = 0
    total_time_ms: int = 0

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# RAG Result
# =============================================================================


@dataclass
class RAGResult:
    """Complete RAG pipeline result."""

    query: RAGQuery
    response: RAGResponse

    # Pipeline stages
    retrieval_result: RetrievalResult | None = None
    context: RAGContext | None = None
    prompt: RAGPrompt | None = None

    # Status
    success: bool = False
    error: str = ""

    # Statistics
    total_time_ms: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Hybrid Retrieval Types
# =============================================================================


@dataclass
class HybridRetrievalConfig:
    """Configuration for hybrid retrieval."""

    dense_weight: float = 0.5
    sparse_weight: float = 0.3
    keyword_weight: float = 0.2
    fusion_method: str = "rrf"  # rrf, weighted, convex
    top_k_dense: int = 20
    top_k_sparse: int = 20
    top_k_keyword: int = 10


@dataclass
class DenseRetrievalResult:
    """Result from dense (semantic) retrieval."""

    chunks: list[RetrievedChunk]
    query_embedding: list[float]
    provider: str = ""
    latency_ms: int = 0


@dataclass
class SparseRetrievalResult:
    """Result from sparse (keyword/BM25) retrieval."""

    chunks: list[RetrievedChunk]
    query_terms: list[str]
    scores: list[float]
    latency_ms: int = 0


@dataclass
class HybridRetrievalResult:
    """Combined result from hybrid retrieval."""

    dense_result: DenseRetrievalResult | None = None
    sparse_result: SparseRetrievalResult | None = None
    fused_chunks: list[RetrievedChunk] = field(default_factory=list)
    fusion_method: str = ""
    total_latency_ms: int = 0


# =============================================================================
# Reranking Types
# =============================================================================


@dataclass
class RerankingConfig:
    """Configuration for reranking."""

    strategy: RerankStrategy = RerankStrategy.CROSS_ENCODER
    top_k: int = 10
    diversity_lambda: float = 0.5  # For MMR
    cross_encoder_model: str = ""


@dataclass
class RerankedChunk:
    """A chunk after reranking."""

    chunk: RetrievedChunk
    original_rank: int
    new_rank: int
    rerank_score: float
    diversity_score: float = 0.0
    final_score: float = 0.0


@dataclass
class RerankingResult:
    """Result from reranking."""

    original_chunks: list[RetrievedChunk]
    reranked_chunks: list[RerankedChunk]
    strategy: RerankStrategy
    latency_ms: int = 0


# =============================================================================
# Document Ingestion Types
# =============================================================================


@dataclass
class DocumentMetadata:
    """Metadata for a document."""

    title: str = ""
    author: str = ""
    institution: str = ""
    hospital: str = ""
    department: str = ""
    document_type: DocumentType = DocumentType.TXT
    language: str = "en"
    specialty: str = ""
    tags: list[str] = field(default_factory=list)
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source_uri: str = ""
    asset_id: str = ""


@dataclass
class ChunkConfig:
    """Configuration for text chunking."""

    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 100
    max_chunk_size: int = 1024
    split_by: str = "token"  # token, sentence, paragraph
    preserve_structure: bool = True


@dataclass
class IngestionResult:
    """Result of document ingestion."""

    document_id: str
    chunks_created: int
    total_tokens: int
    duration_ms: int
    errors: list[str] = field(default_factory=list)
    metadata: DocumentMetadata | None = None


# =============================================================================
# Context Compression Types
# =============================================================================


@dataclass
class CompressionConfig:
    """Configuration for context compression."""

    enabled: bool = True
    max_tokens: int = 4000
    compression_ratio: float = 0.5
    preserve_citations: bool = True
    method: str = "extract"  # extract, abstract, hybrid


@dataclass
class CompressedChunk:
    """A compressed chunk."""

    original_chunk: RetrievedChunk
    compressed_content: str
    compression_ratio: float
    key_points: list[str] = field(default_factory=list)


# =============================================================================
# Hallucination Guard Types
# =============================================================================


@dataclass
class HallucinationCheck:
    """Check for hallucination in response."""

    claim: str
    is_supported: bool
    supporting_sources: list[str] = field(default_factory=list)
    contradicting_sources: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class HallucinationReport:
    """Report on hallucination detection."""

    total_claims: int = 0
    supported_claims: int = 0
    unsupported_claims: int = 0
    hallucination_rate: float = 0.0
    checks: list[HallucinationCheck] = field(default_factory=list)


# =============================================================================
# Pipeline Statistics
# =============================================================================


@dataclass
class PipelineStatistics:
    """Statistics for RAG pipeline."""

    queries_processed: int = 0
    successful_queries: int = 0
    failed_queries: int = 0

    avg_retrieval_time_ms: float = 0.0
    avg_generation_time_ms: float = 0.0
    avg_total_time_ms: float = 0.0

    total_chunks_retrieved: int = 0
    total_citations: int = 0

    avg_chunks_per_query: float = 0.0
    avg_tokens_per_query: float = 0.0

    by_retrieval_strategy: dict[str, int] = field(default_factory=dict)
    by_response_format: dict[str, int] = field(default_factory=dict)
