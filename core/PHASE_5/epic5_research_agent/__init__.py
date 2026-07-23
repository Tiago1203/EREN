"""
PHASE 5 - EPIC 5: Research Agent

Agente dedicado a investigación biomédica.
Busca evidencia científica, compara artículos y genera resúmenes técnicos.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_5"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic5_research_agent.domain import (
    # Research Request
    ResearchRequest,
    ResearchType,
    ResearchScope,
    # Research Result
    ResearchResult,
    ResearchFinding,
    EvidenceStrength,
    # Literature Review
    LiteratureReview,
    PaperComparison,
    SummarySection,
)

# Engines
from core.PHASE_5.epic5_research_agent.engines import (
    # Research Planner
    ResearchPlanner,
    ResearchPlan,
    # Evidence Comparator
    EvidenceComparator,
    ComparisonResult,
    # Paper Analyzer
    PaperAnalyzer,
    AnalysisResult,
    # Literature Reviewer
    LiteratureReviewer,
    ReviewOutline,
)

# Agent
from core.PHASE_5.epic5_research_agent.agent import (
    ResearchAgent,
    ResearchAgentConfig,
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
    "ResearchRequest",
    "ResearchType",
    "ResearchScope",
    "ResearchResult",
    "ResearchFinding",
    "EvidenceStrength",
    "LiteratureReview",
    "PaperComparison",
    "SummarySection",
    # Engines
    "ResearchPlanner",
    "ResearchPlan",
    "EvidenceComparator",
    "ComparisonResult",
    "PaperAnalyzer",
    "AnalysisResult",
    "LiteratureReviewer",
    "ReviewOutline",
    # Agent
    "ResearchAgent",
    "ResearchAgentConfig",
]
