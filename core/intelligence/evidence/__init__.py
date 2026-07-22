"""
Evidence Retrieval Module

Complete implementation of EPIC 3 for EREN PHASE 3.

This module provides evidence retrieval and evaluation capabilities:
- Evidence Retrieval Engine
- Evidence Bundle
- Evidence Scoring
- Evidence Ranking
- Biomedical Rules Engine (Drools-style)
"""

# Version
__version__ = "1.0.0"

# Evidence Retrieval
from core.intelligence.evidence.retrieval import (
    EvidenceSource,
    EvidenceQuality,
    EvidenceItem,
    EvidenceQuery,
    EvidenceRetrievalResult,
    EvidenceSearcher,
    EvidenceCollector,
    EvidenceRetriever,
)

# Evidence Bundle
from core.intelligence.evidence.bundle import (
    ComplianceStatus,
    EvidencePriority,
    RuleMatch,
    EvidenceSummary,
    EvidenceBundle,
    EvidenceBundleGenerator,
    EvidenceBundleManager,
)

# Evidence Scoring
from core.intelligence.evidence.scoring import (
    ScoringMethod,
    EvidenceScore,
    EvidenceScorer,
    EvidenceRanker,
)

# Evidence Ranking
from core.intelligence.evidence.ranking import (
    EvidenceRanking,
    EvidenceRankingAlgorithm,
    TFIDFRanking,
    SemanticRanking,
    HybridRanking,
)

# Rules Engine
from core.intelligence.evidence.rules import (
    RuleCategory,
    ConditionOperator,
    ConditionConnector,
    ActionType,
    Condition,
    RuleAction,
    Rule,
    RuleMatch,
    ConditionEvaluator,
    RulesEngine,
    get_standard_rules,
)

__all__ = [
    # Version
    "__version__",
    # Evidence Retrieval
    "EvidenceSource",
    "EvidenceQuality",
    "EvidenceItem",
    "EvidenceQuery",
    "EvidenceRetrievalResult",
    "EvidenceSearcher",
    "EvidenceCollector",
    "EvidenceRetriever",
    # Evidence Bundle
    "ComplianceStatus",
    "EvidencePriority",
    "RuleMatch",
    "EvidenceSummary",
    "EvidenceBundle",
    "EvidenceBundleGenerator",
    "EvidenceBundleManager",
    # Evidence Scoring
    "ScoringMethod",
    "EvidenceScore",
    "EvidenceScorer",
    "EvidenceRanker",
    # Evidence Ranking
    "EvidenceRanking",
    "EvidenceRankingAlgorithm",
    "TFIDFRanking",
    "SemanticRanking",
    "HybridRanking",
    # Rules Engine
    "RuleCategory",
    "ConditionOperator",
    "ConditionConnector",
    "ActionType",
    "Condition",
    "RuleAction",
    "Rule",
    "RuleMatch",
    "ConditionEvaluator",
    "RulesEngine",
    "get_standard_rules",
]
