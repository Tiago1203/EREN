"""Planning Engine types for EREN OS.

Types for the Cognitive Planning Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Enums
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

    BLOCKS = "blocks"  # Must complete before dependent
    REQUIRES = "requires"  # Needs output from dependent
    ENABLES = "enables"  # Enables dependent to run
    OPTIONAL = "optional"  # Can run in parallel


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


class PlanStatus(str, Enum):
    """Status of an execution plan."""

    CREATED = "created"
    VALIDATED = "validated"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Task Definition
# =============================================================================


@dataclass
class Task:
    """A single task in an execution plan."""

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
    depends_on: list[str] = field(default_factory=list)  # Task IDs
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

    # Results
    result: Any = None
    error: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

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

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "capability": self.capability,
            "status": self.status.value,
            "priority": self.priority.value,
            "depends_on": self.depends_on,
            "estimated_time_seconds": self.estimated_time_seconds,
            "estimated_cost": self.estimated_cost,
            "duration_seconds": self.duration_seconds,
            "retries": self.retries,
        }


# =============================================================================
# Goal Analysis
# =============================================================================


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

    # Analysis
    complexity: int = 1  # 1-5 scale
    estimated_tasks: int = 0
    estimated_time_seconds: float = 0.0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


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

    # Metadata
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


# =============================================================================
# Execution Plan
# =============================================================================


@dataclass
class ExecutionPlan:
    """Complete execution plan."""

    plan_id: str
    goal: Goal

    # Tasks
    tasks: list[Task] = field(default_factory=list)

    # Status
    status: PlanStatus = PlanStatus.CREATED

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

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if not self.tasks:
            return 0.0
        return self.completed_tasks / len(self.tasks)

    @property
    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return self.status == PlanStatus.COMPLETED

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
            return (datetime.now(UTC) - self.started_at).total_seconds()
        return 0.0

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> list[Task]:
        """Get tasks that are ready to execute."""
        ready = []
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are complete
            deps_complete = all(
                self.get_task(dep_id) and
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.depends_on
            )

            if deps_complete:
                ready.append(task)

        return ready

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "goal_type": self.goal.goal_type.value,
            "status": self.status.value,
            "total_tasks": len(self.tasks),
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "progress": self.progress,
            "estimated_time": self.total_estimated_time_seconds,
            "total_duration": self.total_duration_seconds,
        }


# =============================================================================
# Planning Metrics
# =============================================================================


@dataclass
class PlanningMetrics:
    """Metrics for planning operations."""

    # Counts
    plans_created: int = 0
    plans_completed: int = 0
    plans_failed: int = 0
    total_tasks: int = 0

    # Timing
    avg_planning_time_ms: float = 0.0
    avg_tasks_per_plan: float = 0.0

    # Success rates
    success_rate: float = 0.0

    # By goal type
    by_goal_type: dict[str, int] = field(default_factory=dict)
