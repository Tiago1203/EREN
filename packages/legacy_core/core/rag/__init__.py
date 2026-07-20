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

from core.rag.citation_builder import CitationBuilder
from core.rag.context_builder import ContextBuilder, Deduplicator

# Exceptions
from core.rag.exceptions import (
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
from core.rag.pipeline import CognitiveRAGPipeline

# Components
from core.rag.planner import RetrievalPlan, RetrievalPlanner
from core.rag.prompt_builder import PromptBuilder
from core.rag.response_builder import ResponseBuilder
from core.rag.token_budget import TokenBudget, get_default_budget, reset_default_budget
from core.rag.reranker import Reranker
from core.rag.hybrid_retrieval import HybridRetrieval, BM25Retriever

# Types
from core.rag.types import (
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
