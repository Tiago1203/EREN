"""
EREN PHASE 4 — Knowledge Infrastructure

Knowledge Infrastructure layer that orchestrates:
- Clinical embeddings specialized for biomedical knowledge
- Qdrant vector database integration
- Clinical knowledge retrieval
- Clinical RAG pipeline
- Citation and evidence attribution

Dependencies:
- PHASE_1: Consumes business domain knowledge (10 Bounded Contexts)
- PHASE_2: Extends AI Core (embeddings, retrieval, RAG)
- PHASE_3: Integrates with Clinical Intelligence engines
"""

__version__ = "1.0.0"
__phase__ = "PHASE_4"

from core.PHASE_4.embeddings import (
    MedicalEmbeddingProvider,
    ClinicalChunker,
    EmbeddingManager,
)
from core.PHASE_4.qdrant import (
    QdrantClient,
    CollectionManager,
    VectorStore,
    HybridSearch,
)
from core.PHASE_4.knowledge import (
    KnowledgeRetriever,
    EvidenceSearcher,
    ArticleRetriever,
)
from core.PHASE_4.rag import (
    ClinicalRAGPipeline,
    RAGOrchestrator,
    QueryProcessor,
)
from core.PHASE_4.citations import (
    CitationBuilder,
    SourceAttributor,
    EvidenceTracer,
)

__all__ = [
    # Version
    "__version__",
    "__phase__",
    # Embeddings
    "MedicalEmbeddingProvider",
    "ClinicalChunker",
    "EmbeddingManager",
    # Qdrant
    "QdrantClient",
    "CollectionManager",
    "VectorStore",
    "HybridSearch",
    # Knowledge
    "KnowledgeRetriever",
    "EvidenceSearcher",
    "ArticleRetriever",
    # RAG
    "ClinicalRAGPipeline",
    "RAGOrchestrator",
    "QueryProcessor",
    # Citations
    "CitationBuilder",
    "SourceAttributor",
    "EvidenceTracer",
]
