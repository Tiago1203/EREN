"""
PHASE 5 - EPIC 4: Knowledge Agent

Agente especializado en búsqueda y gestión de conocimiento biomédico.
Consulta toda la plataforma de conocimiento construida en FASE 4.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_4"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic4_knowledge_agent.domain import (
    # Knowledge Query
    KnowledgeQuery,
    QueryType,
    KnowledgeSource,
    # Knowledge Package
    KnowledgePackage,
    KnowledgeItem,
    # Citation Bundle
    CitationBundle,
    Citation,
    SourceType,
)

# Engines
from core.PHASE_5.epic4_knowledge_agent.engines import (
    # Knowledge Retriever
    KnowledgeRetriever,
    RetrievalResult,
    # Citation Collector
    CitationCollector,
    CitationResult,
    # Search Engines
    KnowledgeSearchEngine,
    LiteratureSearchEngine,
    StandardsSearchEngine,
)

# Agent
from core.PHASE_5.epic4_knowledge_agent.agent import (
    KnowledgeAgent,
    KnowledgeAgentConfig,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain
    "KnowledgeQuery",
    "QueryType",
    "KnowledgeSource",
    "KnowledgePackage",
    "KnowledgeItem",
    "CitationBundle",
    "Citation",
    "SourceType",
    # Engines
    "KnowledgeRetriever",
    "RetrievalResult",
    "CitationCollector",
    "CitationResult",
    "KnowledgeSearchEngine",
    "LiteratureSearchEngine",
    "StandardsSearchEngine",
    # Agent
    "KnowledgeAgent",
    "KnowledgeAgentConfig",
]
