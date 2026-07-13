"""Cognitive Lifecycle Manager (CLM)."""

from core.lifecycle.lifecycle_manager import (
    CognitiveLifecycleManager,
    LifecycleManagerFactory,
)
from core.lifecycle.lifecycle_state_machine import LifecycleStateMachine
from core.lifecycle.lifecycle_types import LifecycleState, LifecycleEvent, VALID_TRANSITIONS
from core.lifecycle.lifecycle_policy import LifecyclePolicy, LifecyclePolicyPresets
from core.lifecycle.lifecycle_events import LifecycleEventPublisher, LifecycleEventType
from core.lifecycle.lifecycle_metrics import LifecycleMetricsCollector
from core.lifecycle.lifecycle_trace import LifecycleTraceCollector, LifecycleTraceEntry
from core.lifecycle.lifecycle_transition import LifecycleTransition
from core.lifecycle.exceptions import (
    LifecycleError,
    InvalidTransitionError,
    TerminalStateError,
    LifecycleNotFoundError,
)

__all__ = [
    "CognitiveLifecycleManager",
    "LifecycleManagerFactory",
    "LifecycleStateMachine",
    "LifecycleState",
    "LifecycleEvent",
    "VALID_TRANSITIONS",
    "LifecyclePolicy",
    "LifecyclePolicyPresets",
    "LifecycleEventPublisher",
    "LifecycleEventType",
    "LifecycleMetricsCollector",
    "LifecycleTraceCollector",
    "LifecycleTraceEntry",
    "LifecycleTransition",
    "LifecycleError",
    "InvalidTransitionError",
    "TerminalStateError",
    "LifecycleNotFoundError",
]
