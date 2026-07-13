"""Cognitive Reasoning Engine (CRE).

The logical brain of EREN. Transforms evidence into hypotheses
and then into justified decisions.

EREN NO uses AI. EREN NO generates text. EREN NO calls LLM.
EREN only organizes reasoning.

Architecture only -- no AI, no implementations.
"""

from __future__ import annotations

from core.reasoning.adapters import (
    ReasoningContextAdapter,
    ReasoningMemoryAdapter,
)
from core.reasoning.capabilities import get_reasoning_capabilities
from core.reasoning.confidence_model import (
    BayesianConfidenceCalculator,
    ConfidenceCalculator,
    ConfidenceCalculatorFactory,
    DefaultConfidenceCalculator,
    DempsterShaferCalculator,
    probability_to_level,
)
from core.reasoning.evidence_manager import EvidenceManager
from core.reasoning.exceptions import (
    ChainNotFoundError,
    ChainValidationError,
    DecisionNotFoundError,
    EvidenceNotFoundError,
    HypothesisLimitExceededError,
    HypothesisNotFoundError,
    InsufficientEvidenceError,
    InvalidConfidenceError,
    ReasoningError,
    ReasoningStageError,
    SessionAlreadyActiveError,
    SessionNotFoundError,
    StrategyNotSupportedError,
)
from core.reasoning.hypothesis_manager import HypothesisManager
from core.reasoning.reasoning_chain import ReasoningChain, ReasoningChainBuilder, ReasoningChainManager
from core.reasoning.reasoning_engine import (
    CognitiveReasoningEngine,
    ReasoningCapabilityRegistrar,
    ReasoningEventPublisher,
    ReasoningSession,
)
from core.reasoning.reasoning_events import ReasoningEvent, ReasoningEventPublisher as LegacyEventPublisher
from core.reasoning.reasoning_metrics import ReasoningHealthCheck, ReasoningMetrics, ReasoningMetricsCollector
from core.reasoning.reasoning_strategy import (
    EvidenceFirstStrategyExecutor,
    ExhaustiveStrategyExecutor,
    FocusedStrategyExecutor,
    HypothesisFirstStrategyExecutor,
    ReasoningStrategyExecutor,
)
from core.reasoning.reasoning_trace import ReasoningTrace, ReasoningTraceBuilder
from core.reasoning.reasoning_types import (
    ConfidenceLevel,
    ConfidenceScore,
    Decision,
    DecisionStatus,
    DecisionType,
    Evidence,
    EvidenceRelation,
    EvidenceSource,
    EvidenceType,
    Hypothesis,
    HypothesisPriority,
    HypothesisStatus,
    InferenceType,
    ReasoningStage,
    ReasoningState,
    ReasoningStrategy,
    StrategyConfig,
)

__all__ = [
    # Core Engine
    "CognitiveReasoningEngine",
    "ReasoningSession",
    "ReasoningCapabilityRegistrar",
    "ReasoningEventPublisher",
    # Legacy (for backwards compatibility)
    "LegacyEventPublisher",
    # Adapters
    "ReasoningContextAdapter",
    "ReasoningMemoryAdapter",
    # Capabilities
    "get_reasoning_capabilities",
    # Hypothesis Management
    "HypothesisManager",
    "Hypothesis",
    "HypothesisStatus",
    "HypothesisPriority",
    # Evidence Management
    "EvidenceManager",
    "Evidence",
    "EvidenceType",
    "EvidenceSource",
    "EvidenceRelation",
    # Confidence
    "ConfidenceScore",
    "ConfidenceLevel",
    "ConfidenceCalculator",
    "ConfidenceCalculatorFactory",
    "DefaultConfidenceCalculator",
    "BayesianConfidenceCalculator",
    "DempsterShaferCalculator",
    "probability_to_level",
    # Decision
    "Decision",
    "DecisionType",
    "DecisionStatus",
    # Reasoning Chain
    "ReasoningChain",
    "ReasoningChainBuilder",
    "ReasoningChainManager",
    "ReasoningStep",
    "InferenceType",
    # Trace
    "ReasoningTrace",
    "ReasoningTraceBuilder",
    "ReasoningEvent",
    # Metrics
    "ReasoningMetrics",
    "ReasoningMetricsCollector",
    "ReasoningHealthCheck",
    # Strategy
    "ReasoningStrategy",
    "ReasoningStrategyExecutor",
    "StrategyConfig",
    "ExhaustiveStrategyExecutor",
    "FocusedStrategyExecutor",
    "EvidenceFirstStrategyExecutor",
    "HypothesisFirstStrategyExecutor",
    # State
    "ReasoningState",
    "ReasoningStage",
    # Exceptions
    "ReasoningError",
    "SessionNotFoundError",
    "SessionAlreadyActiveError",
    "HypothesisNotFoundError",
    "EvidenceNotFoundError",
    "DecisionNotFoundError",
    "ChainNotFoundError",
    "InvalidConfidenceError",
    "HypothesisLimitExceededError",
    "ChainValidationError",
    "StrategyNotSupportedError",
    "InsufficientEvidenceError",
    "ReasoningStageError",
]
