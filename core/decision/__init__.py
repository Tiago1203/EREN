"""Cognitive Decision Engine (CDE).

The decision component of EREN. Transforms hypotheses and evidence
into structured decisions.

Philosophy:
- Reasoning = Think
- Decision = Decide

EREN NO uses AI. EREN NO calls LLMs. EREN NO executes tools.
EREN only organizes decision infrastructure.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

from core.decision.decision_engine import (
    CognitiveDecisionEngine,
    DecisionCapabilityRegistrar,
    DecisionEventPublisher,
)
from core.decision.decision_evaluator import (
    ActionSelectorComponent,
    DecisionEvaluatorComponent,
    PriorityEvaluatorComponent,
    RiskEvaluatorComponent,
)
from core.decision.decision_metrics import DecisionHealthCheck, DecisionMetricsCollector
from core.decision.decision_policies import (
    BalancedPolicy,
    ConservativePolicy,
    DecisionPolicyComponent,
    PermissivePolicy,
)
from core.decision.decision_strategy import (
    BalancedStrategy,
    ConfidenceBasedStrategy,
    ConservativeStrategy,
    DecisionStrategy,
    DecisionStrategyFactory,
    DecisionStrategyType,
    SpeedStrategy,
)
from core.decision.decision_trace import DecisionTraceBuilder, DecisionTraceEvent
from core.decision.decision_types import (
    ActionSelector,
    Decision,
    DecisionCandidate,
    DecisionCategory,
    DECISION_CATEGORY_MAP,
    DECISION_PRIORITY_MAP,
    DECISION_RISK_MAP,
    DecisionContext,
    DecisionMetrics,
    DecisionPolicy,
    DecisionPolicyRule,
    DecisionPriority,
    DecisionStatus,
    DecisionTrace,
    DecisionType,
    PriorityEvaluator,
    RiskEvaluator,
    RiskLevel,
)

__all__ = [
    # Core Engine
    "CognitiveDecisionEngine",
    "DecisionCapabilityRegistrar",
    "DecisionEventPublisher",
    # Evaluators
    "RiskEvaluatorComponent",
    "PriorityEvaluatorComponent",
    "DecisionEvaluatorComponent",
    "ActionSelectorComponent",
    # Policies
    "DecisionPolicyComponent",
    "ConservativePolicy",
    "BalancedPolicy",
    "PermissivePolicy",
    # Strategies
    "DecisionStrategy",
    "DecisionStrategyType",
    "DecisionStrategyFactory",
    "ConservativeStrategy",
    "BalancedStrategy",
    "SpeedStrategy",
    "ConfidenceBasedStrategy",
    # Trace
    "DecisionTraceBuilder",
    "DecisionTraceEvent",
    # Types
    "Decision",
    "DecisionCandidate",
    "DecisionContext",
    "DecisionTrace",
    "DecisionPolicyRule",
    "DecisionMetrics",
    # Enums
    "DecisionType",
    "DecisionPriority",
    "DecisionStatus",
    "DecisionCategory",
    "DecisionStrategyType",
    "RiskLevel",
    # protocols
    "RiskEvaluator",
    "PriorityEvaluator",
    "DecisionEvaluator",
    "ActionSelector",
    "DecisionPolicy",
    # Constants
    "DECISION_CATEGORY_MAP",
    "DECISION_PRIORITY_MAP",
    "DECISION_RISK_MAP",
    # Metrics
    "DecisionMetricsCollector",
    "DecisionHealthCheck",
]
