"""Cognitive Orchestrator (CKO).

The orchestration component of EREN. Coordinates all cognitive engines
through the complete cognitive processing cycle.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from core.PHASE_2.orchestrator.exceptions import (
    InvalidStateTransitionError,
    OrchestrationError,
    SessionCancelledError,
    SessionNotFoundError,
    SessionTimeoutError,
)
from core.PHASE_2.orchestrator.orchestration_events import (
    OrchestrationEventPublisher,
    OrchestrationEventType,
)
from core.PHASE_2.orchestrator.orchestration_metrics import (
    OrchestrationHealthCheck,
    OrchestrationMetricsCollector,
)
from core.PHASE_2.orchestrator.orchestration_policies import (
    CancellationPolicy,
    IterationPolicy,
    OrchestrationPolicies,
    PolicyPresets,
    RecoveryPolicy,
    RetryPolicy,
    TimeoutPolicy,
)
from core.PHASE_2.orchestrator.orchestration_trace import (
    OrchestrationTraceCollector,
    OrchestrationTraceEntry,
    TraceAnalyzer,
)
from core.PHASE_2.orchestrator.orchestration_types import (
    VALID_TRANSITIONS,
    CognitiveSession,
    OrchestrationPolicy,
    OrchestrationState,
    SessionMetadata,
    SessionMetrics,
    SessionType,
    StateTransition,
    TraceEntry,
)
from core.PHASE_2.orchestrator.orchestrator import (
    CognitiveOrchestrator,
    OrchestratorFactory,
)

__all__ = [
    # Core Engine
    "CognitiveOrchestrator",
    "OrchestratorFactory",
    # Types
    "CognitiveSession",
    "SessionMetadata",
    "SessionMetrics",
    "StateTransition",
    "TraceEntry",
    "OrchestrationState",
    "SessionType",
    "OrchestrationPolicy",
    "VALID_TRANSITIONS",
    # Events
    "OrchestrationEventPublisher",
    "OrchestrationEventType",
    # Metrics
    "OrchestrationMetricsCollector",
    "OrchestrationHealthCheck",
    # Policies
    "OrchestrationPolicies",
    "TimeoutPolicy",
    "RetryPolicy",
    "CancellationPolicy",
    "RecoveryPolicy",
    "IterationPolicy",
    "PolicyPresets",
    # Trace
    "OrchestrationTraceCollector",
    "OrchestrationTraceEntry",
    "TraceAnalyzer",
    # Exceptions
    "OrchestrationError",
    "SessionNotFoundError",
    "InvalidStateTransitionError",
    "SessionTimeoutError",
    "SessionCancelledError",
]
