"""Workflow types for EREN Cognitive Workflow Engine.

Type definitions for workflows.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Workflow Types
# =============================================================================


class WorkflowType(str, Enum):
    """Types of workflows."""

    LINEAR = "linear"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    LOOP = "loop"
    SUBWORKFLOW = "subworkflow"
    SAGA = "saga"


class WorkflowStatus(str, Enum):
    """Status of a workflow."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeType(str, Enum):
    """Types of workflow nodes."""

    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    LOOP = "loop"
    MERGE = "merge"
    SUBWORKFLOW = "subworkflow"
    APPROVAL = "approval"
    COMPENSATE = "compensate"


class NodeStatus(str, Enum):
    """Status of a workflow node."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_APPROVAL = "waiting_approval"


class ExecutionStrategy(str, Enum):
    """Execution strategies."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


# =============================================================================
# Workflow Definition
# =============================================================================


@dataclass
class WorkflowNode:
    """A node in a workflow."""

    node_id: str
    name: str
    node_type: NodeType

    # Configuration
    config: dict = field(default_factory=dict)

    # Dependencies
    depends_on: list[str] = field(default_factory=list)

    # Retry configuration
    max_retries: int = 0
    retry_delay_seconds: float = 1.0

    # Timeout
    timeout_seconds: float = 0.0

    # Compensation (for saga)
    compensation_action: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        node_type: NodeType,
        config: dict | None = None,
        depends_on: list[str] | None = None,
        max_retries: int = 0,
        timeout_seconds: float = 0.0,
    ) -> WorkflowNode:
        """Create a new node."""
        return cls(
            node_id=str(uuid.uuid4()),
            name=name,
            node_type=node_type,
            config=config or {},
            depends_on=depends_on or [],
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )


@dataclass
class WorkflowEdge:
    """An edge in a workflow graph."""

    edge_id: str
    source_id: str
    target_id: str

    # Condition for conditional edges
    condition: str = ""

    # Priority
    priority: int = 0

    @classmethod
    def create(
        cls,
        source_id: str,
        target_id: str,
        condition: str = "",
        priority: int = 0,
    ) -> WorkflowEdge:
        """Create a new edge."""
        return cls(
            edge_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            condition=condition,
            priority=priority,
        )


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""

    workflow_id: str
    name: str
    description: str
    workflow_type: WorkflowType

    # Graph
    nodes: list[WorkflowNode] = field(default_factory=list)
    edges: list[WorkflowEdge] = field(default_factory=list)

    # Entry point
    entry_node_id: str = ""

    # Configuration
    config: dict = field(default_factory=dict)

    # Version
    version: int = 1

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def get_node(self, node_id: str) -> WorkflowNode | None:
        """Get a node by ID."""
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_outgoing_edges(self, node_id: str) -> list[WorkflowEdge]:
        """Get outgoing edges from a node."""
        return [e for e in self.edges if e.source_id == node_id]

    def get_incoming_edges(self, node_id: str) -> list[WorkflowEdge]:
        """Get incoming edges to a node."""
        return [e for e in self.edges if e.target_id == node_id]

    def get_entry_node(self) -> WorkflowNode | None:
        """Get the entry node."""
        return self.get_node(self.entry_node_id)


# =============================================================================
# Workflow Execution
# =============================================================================


@dataclass
class NodeExecution:
    """Execution state of a node."""

    node_id: str
    execution_id: str

    # Status
    status: NodeStatus = NodeStatus.PENDING

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Result
    result: Any = None
    error: str = ""

    # Retry info
    retry_count: int = 0
    last_retry_at: datetime | None = None

    # Checkpoint
    checkpoint_id: str = ""

    def duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0


@dataclass
class WorkflowExecution:
    """Execution of a workflow."""

    execution_id: str
    workflow_id: str
    workflow_name: str

    # Status
    status: WorkflowStatus = WorkflowStatus.CREATED

    # Node executions
    node_executions: dict[str, NodeExecution] = field(default_factory=dict)

    # State
    state: dict = field(default_factory=dict)

    # Current position
    current_node_ids: list[str] = field(default_factory=list)
    completed_node_ids: list[str] = field(default_factory=list)
    failed_node_ids: list[str] = field(default_factory=list)

    # Checkpoints
    checkpoint_ids: list[str] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Input/Output
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)

    # Error info
    error_message: str = ""
    error_node_id: str = ""

    # Parent execution (for subworkflows)
    parent_execution_id: str = ""

    def duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        if self.started_at:
            end = self.completed_at or datetime.now(UTC)
            return (end - self.started_at).total_seconds()
        return 0.0

    def progress_percent(self) -> float:
        """Get progress percentage."""
        total = len(self.node_executions)
        if total == 0:
            return 0.0
        completed = len(self.completed_node_ids)
        return (completed / total) * 100


# =============================================================================
# Checkpoint
# =============================================================================


@dataclass
class Checkpoint:
    """A checkpoint of workflow state."""

    checkpoint_id: str
    execution_id: str

    # Snapshot
    state: dict
    node_executions: dict

    # Position
    completed_node_ids: list[str]
    current_node_ids: list[str]

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Saga Compensation
# =============================================================================


@dataclass
class CompensationRecord:
    """Record of a compensation action."""

    record_id: str
    node_id: str
    action: str

    # Status
    executed: bool = False
    error: str = ""

    # Timing
    executed_at: datetime | None = None


# =============================================================================
# Metrics
# =============================================================================


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""

    workflows_created: int = 0
    workflows_completed: int = 0
    workflows_failed: int = 0
    workflows_cancelled: int = 0

    total_executions: int = 0
    total_nodes_executed: int = 0

    avg_duration_seconds: float = 0.0
    avg_progress_percent: float = 0.0

    # By type
    by_type: dict[str, int] = field(default_factory=dict)
