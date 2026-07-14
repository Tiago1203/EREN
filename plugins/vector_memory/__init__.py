"""EREN Vector Memory Plugin (VMP).

The first REAL vector memory provider for EREN.

Philosophy:
    The Kernel Cognitivo never knows:
    - ChromaDB
    - Qdrant
    - Pinecone
    - Milvus
    - Weaviate
    - pgvector

    It only knows BaseMemoryInterface.

Architecture:
    Document
            │
            ▼
    Chunker
            │
            ▼
    Embedding Layer
            │
            ▼
    Vector Memory Plugin
            │
            ▼
    ChromaDB / Qdrant / pgvector
"""

from __future__ import annotations

from plugins.vector_memory.types import (
    VectorDocument,
    VectorMetadata,
    VectorChunk,
    VectorSearchQuery,
    VectorSearchResult,
    VectorStatistics,
)
from plugins.vector_memory.chunker import (
    BaseChunker,
    SentenceChunker,
    ParagraphChunker,
    SlidingWindowChunker,
    RecursiveChunker,
    ChunkerFactory,
)
from plugins.vector_memory.provider import (
    BaseVectorProvider,
    ChromaVectorProvider,
)
from plugins.vector_memory.plugin import (
    VectorMemoryPlugin,
    VectorMemoryInterface,
)

__all__ = [
    # Types
    "VectorDocument",
    "VectorMetadata",
    "VectorChunk",
    "VectorSearchQuery",
    "VectorSearchResult",
    "VectorStatistics",
    # Chunker
    "BaseChunker",
    "SentenceChunker",
    "ParagraphChunker",
    "SlidingWindowChunker",
    "RecursiveChunker",
    "ChunkerFactory",
    # Provider
    "BaseVectorProvider",
    "ChromaVectorProvider",
    # Plugin
    "VectorMemoryPlugin",
    "VectorMemoryInterface",
]
