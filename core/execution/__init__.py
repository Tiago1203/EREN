"""EREN OS Cognitive Execution Coordinator.

This module implements the Cognitive Execution Coordinator (CEC), the component
responsible for coordinating the complete cognitive execution cycle from
receiving an intent to session completion.

Philosophy:
    The Runtime manages the system.
    The Router selects the Pipeline.
    The Pipeline executes capabilities.
    The Execution Coordinator coordinates the entire cognitive flow.

Key Concepts:
    - Coordinator: Orchestrates the entire execution cycle
    - Session: Tracks execution context
    - Lifecycle: Manages execution phases
    - Validator: Ensures components are available

Example:
    >>> from core.execution import ExecutionCoordinator
    >>> coordinator = ExecutionCoordinator()
    >>> result = coordinator.execute(intent_type="diagnostic")
    >>> print(result.status)
"""

from __future__ import annotations

from core.execution.context import ExecutionContext

# Core Coordinator
from core.execution.coordinator import ExecutionCoordinator

# Observability
from core.execution.events import (
    ExecutionEventPublisher,
    ExecutionEventType,
    get_execution_event_publisher,
)

# Exceptions
from core.execution.exceptions import (
    CancellationRequestedError,
    ComponentNotAvailableError,
    ContextUpdateError,
    ExecutionCancelledError,
    ExecutionException,
    ExecutionInitializationError,
    ExecutionStateError,
    LifecycleError,
    NoPipelineSelectedError,
    PipelineExecutionError,
    PolicyViolationError,
    RoutingError,
    SchedulerError,
    SessionCompletionError,
    SessionCreationError,
    SessionNotFoundError,
    StateTransitionError,
    TimeoutError,
    ValidationError,
)
from core.execution.metrics import (
    ExecutionMetrics,
    get_execution_metrics,
    reset_execution_metrics,
)
from core.execution.result import ExecutionResult
from core.execution.trace import (
    ExecutionTrace,
    get_execution_trace,
    reset_execution_trace,
)

# Types
from core.execution.types import (
    ComponentStatus,
    ExecutionMetadata,
    ExecutionPolicy,
    ExecutionState,
    ValidationResult,
)
from core.execution.validator import ExecutionValidator

# Aliases
ERENCoordinator = ExecutionCoordinator


__all__ = [
    # Core
    "ExecutionCoordinator",
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionValidator",
    # Types
    "ExecutionState",
    "ExecutionPolicy",
    "ExecutionMetadata",
    "ComponentStatus",
    "ValidationResult",
    # Events
    "ExecutionEventPublisher",
    "ExecutionEventType",
    "get_execution_event_publisher",
    # Metrics
    "ExecutionMetrics",
    "get_execution_metrics",
    "reset_execution_metrics",
    # Trace
    "ExecutionTrace",
    "get_execution_trace",
    "reset_execution_trace",
    # Exceptions
    "ExecutionException",
    "ExecutionInitializationError",
    "SessionCreationError",
    "SessionCompletionError",
    "SessionNotFoundError",
    "RoutingError",
    "NoPipelineSelectedError",
    "PipelineExecutionError",
    "ContextUpdateError",
    "LifecycleError",
    "SchedulerError",
    "StateTransitionError",
    "PolicyViolationError",
    "ValidationError",
    "ComponentNotAvailableError",
    "ExecutionCancelledError",
    "TimeoutError",
    "ExecutionStateError",
    "CancellationRequestedError",
    # Aliases
    "ERENCoordinator",
]
