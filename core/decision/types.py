"""Decision Engine types for EREN OS.

Types for the Cognitive Decision Engine (CDE).
Refactored from Planning Engine to be a complete decision-making system.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Decision Strategy Types
# =============================================================================


class DecisionStrategy(str, Enum):
    """Strategies for decision-making."""

    SEQUENTIAL = "sequential"  # Execute tasks one at a time
    PARALLEL = "parallel"  # Execute independent tasks in parallel
    HYBRID = "hybrid"  # Mix of sequential and parallel
    CONDITIONAL = "conditional"  # Based on conditions
    EXPLORATORY = "exploratory"  # Explore multiple paths
    CONSERVATIVE = "conservative"  # Minimize risk
    AGGRESSIVE = "aggressive"  # Maximize speed


class ExecutionPolicy(str, Enum):
    """Policies for execution."""

    STRICT = "strict"  # Follow plan exactly
    ADAPTIVE = "adaptive"  # Adapt to conditions
    CONSERVATIVE = "conservative"  # Minimize changes
    AGGRESSIVE = "aggressive"  # Allow more changes
    FAILFAST = "failfast"  # Stop on first failure
    GRACEFUL = "graceful"  # Handle failures gracefully


class RiskLevel(str, Enum):
    """Risk levels for decisions."""

    MINIMAL = "minimal"  # Very low risk
    LOW = "low"  # Low risk
    MEDIUM = "medium"  # Medium risk
    HIGH = "high"  # High risk
    CRITICAL = "critical"  # Critical risk


# =============================================================================
# Re-export from Planning (with new names)
# =============================================================================


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(str, Enum):
    """Priority levels for tasks."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DependencyType(str, Enum):
    """Types of task dependencies."""

    BLOCKS = "blocks"
    REQUIRES = "requires"
    ENABLES = "enables"
    OPTIONAL = "optional"


class GoalType(str, Enum):
    """Types of goals."""

    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    TROUBLESHOOTING = "troubleshooting"
    CONSULTATION = "consultation"
    REPORT = "report"
    CUSTOM = "custom"


class DecisionStatus(str, Enum):
    """Status of a decision plan."""

    CREATED = "created"
    EVALUATED = "evaluated"
    APPROVED = "approved"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REPLANNING = "replanning"


# =============================================================================
# Decision Plan (renamed from ExecutionPlan)
# =============================================================================


@dataclass
class DecisionTask:
    """A decision task in a plan."""

    task_id: str
    name: str
    description: str

    # Task type
    task_type: str = ""
    capability: str = ""

    # Status
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.REQUIRES

    # Context
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)

    # Estimates
    estimated_time_seconds: float = 0.0
    estimated_cost: float = 0.0
    estimated_tokens: int = 0

    # Execution
    assigned_to: str = ""
    retries: int = 0
    max_retries: int = 3

    # Risk
    risk_level: RiskLevel = RiskLevel.MEDIUM

    # Results
    result: Any = None
    error: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_seconds(self) -> float:
        """Calculate task duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0

    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        return len(self.depends_on) > 0 and self.status == TaskStatus.PENDING


@dataclass
class Goal:
    """A goal to be achieved."""

    goal_id: str
    goal_type: GoalType
    description: str

    # Context
    user_intent: str = ""
    context: dict = field(default_factory=dict)

    # Requirements
    required_capabilities: list[str] = field(default_factory=list)
    required_outputs: list[str] = field(default_factory=list)
    constraints: dict = field(default_factory=dict)

    # Estimates
    complexity: int = 1
    estimated_tasks: int = 0
    estimated_time_seconds: float = 0.0

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GoalAnalysis:
    """Analysis of a goal."""

    goal: Goal
    intent: str

    # Analysis results
    goal_type: GoalType = GoalType.CUSTOM
    primary_objective: str = ""
    sub_objectives: list[str] = field(default_factory=list)

    # Identified capabilities
    required_capabilities: list[str] = field(default_factory=list)
    potential_dependencies: list[str] = field(default_factory=list)

    # Estimates
    estimated_complexity: int = 1
    estimated_tasks: int = 1
    estimated_time_seconds: float = 0.0

    # Constraints
    constraints: dict = field(default_factory=dict)

    # Strategy
    recommended_strategy: DecisionStrategy = DecisionStrategy.HYBRID
    risk_tolerance: RiskLevel = RiskLevel.MEDIUM

    # Metadata
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class DecisionPlan:
    """Complete decision plan (renamed from ExecutionPlan).

    Represents the complete decision for achieving a goal.
    """

    plan_id: str
    goal: Goal

    # Tasks
    tasks: list[DecisionTask] = field(default_factory=list)

    # Strategy
    strategy: DecisionStrategy = DecisionStrategy.HYBRID
    policy: ExecutionPolicy = ExecutionPolicy.ADAPTIVE

    # Status
    status: DecisionStatus = DecisionStatus.CREATED

    # Risk assessment
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    risk_factors: list[str] = field(default_factory=list)

    # Estimates
    total_estimated_time_seconds: float = 0.0
    total_estimated_cost: float = 0.0
    total_estimated_tokens: int = 0

    # Actual
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_retries: int = 0

    # Execution
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Replanning
    replan_count: int = 0
    original_plan_id: str = ""

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if not self.tasks:
            return 0.0
        return self.completed_tasks / len(self.tasks)

    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return self.status == DecisionStatus.COMPLETED

    @property
    def has_failed(self) -> bool:
        """Check if any task failed."""
        return self.failed_tasks > 0

    @property
    def total_duration_seconds(self) -> float:
        """Calculate total duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now(timezone.utc) - self.started_at).total_seconds()
        return 0.0

    def get_task(self, task_id: str) -> DecisionTask | None:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> list[DecisionTask]:
        """Get tasks that are ready to execute."""
        ready = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            deps_complete = all(
                self.get_task(dep_id) and
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.depends_on
            )

            if deps_complete:
                ready.append(task)

        return ready


# =============================================================================
# Decision Components
# =============================================================================


@dataclass
class StrategySelection:
    """Selection of decision strategy."""

    selected_strategy: DecisionStrategy
    alternatives: list[DecisionStrategy]
    reasoning: str
    confidence: float
    estimated_outcome: dict


@dataclass
class RiskAssessment:
    """Assessment of risk for a decision."""

    overall_risk: RiskLevel
    risk_score: float  # 0.0 to 1.0
    risk_factors: list[dict]
    mitigation_strategies: list[str]
    requires_escalation: bool
    escalation_reason: str = ""


@dataclass
class ExecutionDecision:
    """Decision about how to execute tasks."""

    policy: ExecutionPolicy
    parallelism_allowed: bool
    max_parallel_tasks: int
    allow_replanning: bool
    failfast_enabled: bool
    retry_strategy: str
    timeout_seconds: float


@dataclass
class ReplanningReason:
    """Reason for replanning."""

    reason: str
    affected_tasks: list[str]
    original_plan_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Metrics
# =============================================================================


@dataclass
class DecisionMetrics:
    """Metrics for decision operations."""

    # Counts
    decisions_made: int = 0
    decisions_completed: int = 0
    decisions_failed: int = 0
    replans_triggered: int = 0
    total_tasks: int = 0

    # Timing
    avg_decision_time_ms: float = 0.0
    avg_tasks_per_decision: float = 0.0

    # Success rates
    success_rate: float = 0.0
    replan_rate: float = 0.0

    # By type
    by_strategy: dict[str, int] = field(default_factory=dict)
    by_goal_type: dict[str, int] = field(default_factory=dict)
