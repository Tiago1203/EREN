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

# Types
from core.rag.types import (
    RetrievalStrategy,
    ResponseFormat,
    ConfidenceLevel,
    RAGQuery,
    RetrievedChunk,
    RetrievalResult,
    RAGContext,
    RAGPrompt,
    Citation,
    RAGResponse,
    RAGResult,
    PipelineStatistics,
)

# Exceptions
from core.rag.exceptions import (
    RAGError,
    RetrievalError,
    NoContextError,
    PromptBuildError,
    TokenBudgetExceededError,
    ModelSelectionError,
    GenerationError,
    CitationError,
    ValidationError,
    ProviderError,
    TimeoutError,
)

# Components
from core.rag.planner import RetrievalPlanner, RetrievalPlan
from core.rag.context_builder import ContextBuilder, Deduplicator
from core.rag.prompt_builder import PromptBuilder
from core.rag.response_builder import ResponseBuilder
from core.rag.citation_builder import CitationBuilder
from core.rag.token_budget import TokenBudget, get_default_budget, reset_default_budget

# Pipeline
from core.rag.pipeline import CognitiveRAGPipeline

__all__ = [
    # Types
    "RetrievalStrategy",
    "ResponseFormat",
    "ConfidenceLevel",
    "RAGQuery",
    "RetrievedChunk",
    "RetrievalResult",
    "RAGContext",
    "RAGPrompt",
    "Citation",
    "RAGResponse",
    "RAGResult",
    "PipelineStatistics",
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
    # Pipeline
    "CognitiveRAGPipeline",
]
