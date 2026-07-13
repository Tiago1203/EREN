"""Type definitions for the Cognitive Decision Engine.

Provides comprehensive type definitions for decision operations.

Architecture only -- no AI, no business logic, no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Decision Types
# =============================================================================


class DecisionType(str, Enum):
    """Types of decisions."""

    # Analysis decisions
    CONTINUE_ANALYSIS = "continue_analysis"  # Continue reasoning
    REQUEST_MORE_EVIDENCE = "request_more_evidence"  # Need more evidence
    
    # Action decisions
    EXECUTE_TOOL = "execute_tool"  # Execute a tool
    CONSULT_KNOWLEDGE = "consult_knowledge"  # Query knowledge base
    CONSULT_MEMORY = "consult_memory"  # Query memory
    
    # Control decisions
    ESCALATE_TO_HUMAN = "escalate_to_human"  # Human intervention
    STOP_ANALYSIS = "stop_analysis"  # End reasoning
    CREATE_WORKFLOW = "create_workflow"  # Create workflow
    
    # State decisions
    WAIT_FOR_EVENT = "wait_for_event"  # Wait for event
    REJECT_HYPOTHESIS = "reject_hypothesis"  # Reject hypothesis


class DecisionPriority(str, Enum):
    """Priority levels for decisions."""

    CRITICAL = "critical"  # Life-threatening, immediate action
    HIGH = "high"  # Important, time-sensitive
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Background action


class DecisionStatus(str, Enum):
    """Status of a decision."""

    PENDING = "pending"  # Awaiting evaluation
    EVALUATED = "evaluated"  # Evaluated
    APPROVED = "approved"  # Approved for execution
    REJECTED = "rejected"  # Rejected
    EXECUTED = "executed"  # Executed
    FAILED = "failed"  # Execution failed


class DecisionCategory(str, Enum):
    """Categories of decisions."""

    ANALYSIS = "analysis"  # Reasoning decisions
    ACTION = "action"  # Action decisions
    CONTROL = "control"  # Control flow decisions
    STATE = "state"  # State management


class RiskLevel(str, Enum):
    """Risk levels."""

    MINIMAL = "minimal"  # Very low risk
    LOW = "low"  # Low risk
    MEDIUM = "medium"  # Medium risk
    HIGH = "high"  # High risk
    CRITICAL = "critical"  # Critical risk


# =============================================================================
# Protocols (Contracts)
# =============================================================================


class RiskEvaluator(Protocol):
    """Protocol for risk evaluation."""

    def evaluate(
        self,
        decision: "DecisionCandidate",
        context: dict,
    ) -> float:
        """Evaluate risk of a decision."""
        ...


class PriorityEvaluator(Protocol):
    """Protocol for priority evaluation."""

    def evaluate(
        self,
        decision: "DecisionCandidate",
        context: dict,
    ) -> int:
        """Evaluate priority of a decision."""
        ...


class DecisionEvaluator(Protocol):
    """Protocol for decision evaluation."""

    def evaluate(
        self,
        candidates: list["DecisionCandidate"],
        context: dict,
    ) -> list["DecisionCandidate"]:
        """Evaluate and rank decision candidates."""
        ...


class ActionSelector(Protocol):
    """Protocol for action selection."""

    def select(
        self,
        candidates: list["DecisionCandidate"],
        context: dict,
    ) -> "Decision | None":
        """Select the best decision."""
        ...


class DecisionPolicy(Protocol):
    """Protocol for decision policies."""

    def should_approve(
        self,
        decision: "DecisionCandidate",
        context: dict,
    ) -> bool:
        """Check if decision should be approved."""
        ...

    def should_escalate(
        self,
        decision: "DecisionCandidate",
        context: dict,
    ) -> bool:
        """Check if decision should escalate to human."""
        ...


# =============================================================================
# Data Classes
# =============================================================================


@dataclass(frozen=True)
class DecisionCandidate:
    """A candidate for decision.

    Created from reasoning results, hypothesis, or context.
    """

    candidate_id: str
    decision_type: DecisionType
    description: str
    category: DecisionCategory
    priority: DecisionPriority = DecisionPriority.MEDIUM
    confidence: float = 0.5  # 0.0 to 1.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    risk_score: float = 0.5  # Calculated risk
    based_on_hypothesis: str = ""  # Hypothesis ID
    based_on_evidence: tuple[str, ...] = field(default_factory=tuple)
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    estimated_duration_ms: int = 0
    preconditions: tuple[str, ...] = field(default_factory=tuple)
    postconditions: tuple[str, ...] = field(default_factory=tuple)
    alternatives: tuple[str, ...] = field(default_factory=tuple)  # Alternative candidate IDs
    metadata: dict = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class Decision:
    """A final decision ready for execution or approval."""

    decision_id: str
    candidate_id: str
    decision_type: DecisionType
    description: str
    category: DecisionCategory
    priority: DecisionPriority
    status: DecisionStatus
    confidence: float
    risk_level: RiskLevel
    risk_score: float
    score: float  # Combined evaluation score
    justification: tuple[str, ...] = field(default_factory=tuple)
    based_on_hypothesis: str = ""
    based_on_evidence: tuple[str, ...] = field(default_factory=tuple)
    alternatives_considered: tuple[str, ...] = field(default_factory=tuple)
    execution_plan: dict = field(default_factory=dict)
    requires_human_approval: bool = False
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    evaluated_at: str = ""
    approved_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class DecisionContext:
    """Context for decision making."""

    session_id: str
    current_stage: str = ""
    available_hypotheses: tuple[str, ...] = field(default_factory=tuple)
    best_hypothesis_id: str = ""
    best_hypothesis_confidence: float = 0.0
    available_evidence: tuple[str, ...] = field(default_factory=tuple)
    device_info: dict = field(default_factory=dict)
    clinical_context: dict = field(default_factory=dict)
    safety_requirements: tuple[str, ...] = field(default_factory=tuple)
    time_constraints: dict = field(default_factory=dict)
    user_preferences: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionTrace:
    """Complete trace of decision process."""

    trace_id: str
    decision_id: str
    candidates_considered: tuple[str, ...]
    candidates_rejected: tuple[str, ...]
    evaluations: tuple[dict, ...]  # Evaluation details
    final_score: float
    selection_reason: str
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(timezone.utc).isoformat())


@dataclass
class DecisionMetrics:
    """Metrics for decision operations."""

    decisions_created: int = 0
    decisions_evaluated: int = 0
    decisions_approved: int = 0
    decisions_rejected: int = 0
    decisions_executed: int = 0
    escalations: int = 0
    average_score: float = 0.0
    average_risk_score: float = 0.0
    by_type: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)


# =============================================================================
# Decision Strategies
# =============================================================================


class DecisionStrategyType(str, Enum):
    """Types of decision strategies."""

    # Conservative
    CONSERVATIVE = "conservative"  # Minimize risk
    SAFETY_FIRST = "safety_first"  # Prioritize safety
    
    # Performance
    EFFICIENCY = "efficiency"  # Maximize efficiency
    SPEED = "speed"  # Prioritize speed
    
    # Balance
    BALANCED = "balanced"  # Balance risk and benefit
    CONFIDENCE_BASED = "confidence_based"  # Follow confidence
    
    # Special
    HUMAN_IN_LOOP = "human_in_loop"  # Always require human approval
    FULLY_AUTOMATED = "fully_automated"  # No human approval needed


# =============================================================================
# Policy Definitions
# =============================================================================


@dataclass(frozen=True)
class DecisionPolicyRule:
    """A rule in a decision policy."""

    rule_id: str
    name: str
    description: str
    condition: str  # Description of condition
    action: str  # Description of action
    priority: int  # Higher = more priority


# =============================================================================
# Constants
# =============================================================================


# Decision type to category mapping
DECISION_CATEGORY_MAP: dict[DecisionType, DecisionCategory] = {
    DecisionType.CONTINUE_ANALYSIS: DecisionCategory.ANALYSIS,
    DecisionType.REQUEST_MORE_EVIDENCE: DecisionCategory.ANALYSIS,
    DecisionType.EXECUTE_TOOL: DecisionCategory.ACTION,
    DecisionType.CONSULT_KNOWLEDGE: DecisionCategory.ACTION,
    DecisionType.CONSULT_MEMORY: DecisionCategory.ACTION,
    DecisionType.ESCALATE_TO_HUMAN: DecisionCategory.CONTROL,
    DecisionType.STOP_ANALYSIS: DecisionCategory.CONTROL,
    DecisionType.CREATE_WORKFLOW: DecisionCategory.STATE,
    DecisionType.WAIT_FOR_EVENT: DecisionCategory.STATE,
    DecisionType.REJECT_HYPOTHESIS: DecisionCategory.ANALYSIS,
}


# Default priorities by decision type
DECISION_PRIORITY_MAP: dict[DecisionType, DecisionPriority] = {
    DecisionType.ESCALATE_TO_HUMAN: DecisionPriority.CRITICAL,
    DecisionType.STOP_ANALYSIS: DecisionPriority.HIGH,
    DecisionType.CONTINUE_ANALYSIS: DecisionPriority.MEDIUM,
    DecisionType.EXECUTE_TOOL: DecisionPriority.HIGH,
    DecisionType.CONSULT_KNOWLEDGE: DecisionPriority.MEDIUM,
    DecisionType.REQUEST_MORE_EVIDENCE: DecisionPriority.MEDIUM,
}


# Risk thresholds by decision type
DECISION_RISK_MAP: dict[DecisionType, RiskLevel] = {
    DecisionType.ESCALATE_TO_HUMAN: RiskLevel.LOW,  # Low risk - human handles it
    DecisionType.CONTINUE_ANALYSIS: RiskLevel.MINIMAL,
    DecisionType.REQUEST_MORE_EVIDENCE: RiskLevel.LOW,
    DecisionType.CONSULT_KNOWLEDGE: RiskLevel.LOW,
    DecisionType.CONSULT_MEMORY: RiskLevel.LOW,
    DecisionType.EXECUTE_TOOL: RiskLevel.MEDIUM,  # Depends on tool
    DecisionType.STOP_ANALYSIS: RiskLevel.HIGH,
    DecisionType.CREATE_WORKFLOW: RiskLevel.MEDIUM,
    DecisionType.WAIT_FOR_EVENT: RiskLevel.LOW,
    DecisionType.REJECT_HYPOTHESIS: RiskLevel.LOW,
}
