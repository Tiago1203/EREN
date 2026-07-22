"""EREN OS Cognitive Capability Router.

This module implements the Cognitive Capability Router (CCR), the component
responsible for dynamically selecting which Cognitive Pipeline should execute
based on context, intent, available capabilities, and system policies.

Philosophy:
    The Runtime does not select pipelines.
    The Pipeline does not decide when to execute.
    The Capability Router decides which Cognitive Pipeline to use.

Key Concepts:
    - Router: Orchestrates pipeline selection
    - Matcher: Evaluates intent-to-pipeline compatibility
    - Selector: Selects best pipeline using policies
    - Registry: Manages pipeline metadata and rules
    - Policy: Determines selection strategy

Example:
    >>> from core.PHASE_2.router import CapabilityRouter
    >>> router = CapabilityRouter()
    >>> result = router.route(intent_type="diagnostic")
    >>> print(result.selected_pipeline)
"""

from __future__ import annotations

from core.PHASE_2.router.context import RouterContext

# Observability
from core.PHASE_2.router.events import (
    RouterEventPublisher,
    RouterEventType,
    get_router_event_publisher,
    publish_router_event,
)

# Exceptions
from core.PHASE_2.router.exceptions import (
    ContextError,
    FallbackError,
    InvalidTransitionError,
    MatcherError,
    MetadataError,
    MultipleMatchingPipelinesError,
    NoMatchingPipelineError,
    PipelineNotEligibleError,
    PolicyViolationError,
    RegistryError,
    RouterException,
    RouterInitializationError,
    RouterStateError,
    RoutingError,
    RuleAlreadyRegisteredError,
    RuleNotFoundError,
    RuleValidationError,
    SelectorError,
    StrictPolicyError,
)
from core.PHASE_2.router.matcher import PipelineMatcher
from core.PHASE_2.router.metrics import (
    RouterMetrics,
    get_router_metrics,
    reset_router_metrics,
)

# Policy
from core.PHASE_2.router.policy import (
    FallbackPolicy,
    FirstMatchPolicy,
    HighestScorePolicy,
    PolicyFactory,
    PriorityPolicy,
    RoutingPolicy,
    RoutingPolicyHandler,
    StrictPolicy,
    WeightedPolicy,
)

# Registry
from core.PHASE_2.router.registry import (
    RoutingRegistry,
    get_routing_registry,
)
from core.PHASE_2.router.result import RoutingResult

# Core Router
from core.PHASE_2.router.router import CapabilityRouter
from core.PHASE_2.router.selector import PipelineSelector
from core.PHASE_2.router.trace import (
    RouterTrace,
    get_router_trace,
    reset_router_trace,
)

# Types
from core.PHASE_2.router.types import (
    CandidatePipeline,
    MatchResult,
    PipelineMetadata,
    RouterState,
    RoutingRule,
)
from core.PHASE_2.router.types import (
    RoutingPolicy as RoutingPolicyType,
)

# Aliases
ERENRouter = CapabilityRouter


__all__ = [
    # Core
    "CapabilityRouter",
    "RouterContext",
    "RoutingResult",
    "PipelineMatcher",
    "PipelineSelector",
    # Registry
    "RoutingRegistry",
    "get_routing_registry",
    # Policy
    "RoutingPolicy",
    "RoutingPolicyHandler",
    "FirstMatchPolicy",
    "HighestScorePolicy",
    "PriorityPolicy",
    "StrictPolicy",
    "WeightedPolicy",
    "FallbackPolicy",
    "PolicyFactory",
    # Types
    "RouterState",
    "RoutingPolicyType",
    "MatchResult",
    "PipelineMetadata",
    "CandidatePipeline",
    "RoutingRule",
    # Events
    "RouterEventPublisher",
    "RouterEventType",
    "get_router_event_publisher",
    "publish_router_event",
    # Metrics
    "RouterMetrics",
    "get_router_metrics",
    "reset_router_metrics",
    # Trace
    "RouterTrace",
    "get_router_trace",
    "reset_router_trace",
    # Exceptions
    "RouterException",
    "RouterInitializationError",
    "RoutingError",
    "NoMatchingPipelineError",
    "MultipleMatchingPipelinesError",
    "PipelineNotEligibleError",
    "PolicyViolationError",
    "StrictPolicyError",
    "FallbackError",
    "RouterStateError",
    "InvalidTransitionError",
    "RuleValidationError",
    "RegistryError",
    "RuleNotFoundError",
    "RuleAlreadyRegisteredError",
    "SelectorError",
    "MatcherError",
    "ContextError",
    "MetadataError",
    # Aliases
    "ERENRouter",
]
