"""EREN Cognitive RAG Pipeline.

The first fully functional RAG pipeline of EREN.
Connects all infrastructure for retrieval-augmented generation.

Architecture:
    User
        │
        ▼
    Execution Coordinator
        │
        ▼
    Reasoning Pipeline
        │
        ▼
    Memory Coordinator
        │
        ▼
    Semantic Retrieval Engine
        │
        ▼
    Knowledge Asset Registry
        │
        ▼
    Vector Memory Plugin
        │
        ▼
    Embedding Layer
        │
        ▼
    Provider Layer
        │
        ▼
    Model Registry
        │
        ▼
    LLM Provider
        │
        ▼
    Response Builder
        │
        ▼
    User

Philosophy:
    The Pipeline NEVER knows about:
    - Vector databases (Chroma, Qdrant)
    - Providers (OpenAI, Anthropic)
    - Embeddings

    All interactions go through contracts.
"""

from __future__ import annotations

from core.PHASE_2.rag.citation_builder import CitationBuilder
from core.PHASE_2.rag.context_builder import ContextBuilder, Deduplicator

# Exceptions
from core.PHASE_2.rag.exceptions import (
    CitationError,
    GenerationError,
    ModelSelectionError,
    NoContextError,
    PromptBuildError,
    ProviderError,
    RAGError,
    RetrievalError,
    TimeoutError,
    TokenBudgetExceededError,
    ValidationError,
)

# Pipeline
from core.PHASE_2.rag.pipeline import CognitiveRAGPipeline

# Components
from core.PHASE_2.rag.planner import RetrievalPlan, RetrievalPlanner
from core.PHASE_2.rag.prompt_builder import PromptBuilder
from core.PHASE_2.rag.response_builder import ResponseBuilder
from core.PHASE_2.rag.token_budget import TokenBudget, get_default_budget, reset_default_budget
from core.PHASE_2.rag.reranker import Reranker
from core.PHASE_2.rag.hybrid_retrieval import HybridRetrieval, BM25Retriever

# Types
from core.PHASE_2.rag.types import (
    Citation,
    ChunkConfig,
    CompressionConfig,
    CompressedChunk,
    ConfidenceLevel,
    DenseRetrievalResult,
    DocumentMetadata,
    DocumentType,
    HallucinationCheck,
    HallucinationReport,
    HybridRetrievalConfig,
    HybridRetrievalResult,
    IngestionResult,
    PipelineStatistics,
    RAGContext,
    RAGPrompt,
    RAGQuery,
    RAGResponse,
    RAGResult,
    RerankStrategy,
    RerankedChunk,
    RerankingConfig,
    RerankingResult,
    ResponseFormat,
    RetrievalResult,
    RetrievalStrategy,
    RetrievedChunk,
    SparseRetrievalResult,
)

__all__ = [
    # Types
    "RetrievalStrategy",
    "ResponseFormat",
    "ConfidenceLevel",
    "RerankStrategy",
    "DocumentType",
    "RAGQuery",
    "RetrievedChunk",
    "RetrievalResult",
    "RAGContext",
    "RAGPrompt",
    "Citation",
    "RAGResponse",
    "RAGResult",
    "PipelineStatistics",
    "HybridRetrievalConfig",
    "HybridRetrievalResult",
    "DenseRetrievalResult",
    "SparseRetrievalResult",
    "RerankingConfig",
    "RerankingResult",
    "RerankedChunk",
    "ChunkConfig",
    "DocumentMetadata",
    "IngestionResult",
    "CompressionConfig",
    "CompressedChunk",
    "HallucinationCheck",
    "HallucinationReport",
    # Exceptions
    "RAGError",
    "RetrievalError",
    "NoContextError",
    "PromptBuildError",
    "TokenBudgetExceededError",
    "ModelSelectionError",
    "GenerationError",
    "CitationError",
    "ValidationError",
    "ProviderError",
    "TimeoutError",
    # Components
    "RetrievalPlanner",
    "RetrievalPlan",
    "ContextBuilder",
    "Deduplicator",
    "PromptBuilder",
    "ResponseBuilder",
    "CitationBuilder",
    "TokenBudget",
    "get_default_budget",
    "reset_default_budget",
    "Reranker",
    "HybridRetrieval",
    "BM25Retriever",
    # Pipeline
    "CognitiveRAGPipeline",
]
