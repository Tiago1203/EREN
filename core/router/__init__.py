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
    >>> from core.router import CapabilityRouter
    >>> router = CapabilityRouter()
    >>> result = router.route(intent_type="diagnostic")
    >>> print(result.selected_pipeline)
"""

from __future__ import annotations

from core.router.context import RouterContext

# Observability
from core.router.events import (
    RouterEventPublisher,
    RouterEventType,
    get_router_event_publisher,
    publish_router_event,
)

# Exceptions
from core.router.exceptions import (
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
from core.router.matcher import PipelineMatcher
from core.router.metrics import (
    RouterMetrics,
    get_router_metrics,
    reset_router_metrics,
)

# Policy
from core.router.policy import (
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
from core.router.registry import (
    RoutingRegistry,
    get_routing_registry,
)
from core.router.result import RoutingResult

# Core Router
from core.router.router import CapabilityRouter
from core.router.selector import PipelineSelector
from core.router.trace import (
    RouterTrace,
    get_router_trace,
    reset_router_trace,
)

# Types
from core.router.types import (
    CandidatePipeline,
    MatchResult,
    PipelineMetadata,
    RouterState,
    RoutingRule,
)
from core.router.types import (
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
