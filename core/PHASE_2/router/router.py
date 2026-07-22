"""Capability Router for EREN OS Cognitive Capability Router.

Main router engine that selects appropriate pipelines.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.router.context import RouterContext
from core.PHASE_2.router.matcher import PipelineMatcher
from core.PHASE_2.router.policy import RoutingPolicy
from core.PHASE_2.router.registry import RoutingRegistry, get_routing_registry
from core.PHASE_2.router.result import RoutingResult
from core.PHASE_2.router.selector import PipelineSelector
from core.PHASE_2.router.types import (
    CandidatePipeline,
    RouterState,
)

if TYPE_CHECKING:
    pass


class CapabilityRouter:
    """Main cognitive capability router.

    Responsible for:
    - Receiving routing requests
    - Matching intents to pipelines
    - Selecting best pipeline using policies
    - Publishing events
    - Recording metrics
    - Recording traces

    Features:
    - Thread-safe execution
    - Multiple routing policies
    - Fallback support
    - Complete observability
    """

    def __init__(
        self,
        registry: RoutingRegistry | None = None,
        default_policy: RoutingPolicy = RoutingPolicy.FIRST_MATCH,
        fallback_enabled: bool = True,
    ):
        """Initialize the router.

        Args:
            registry: Routing registry.
            default_policy: Default routing policy.
            fallback_enabled: Whether to use fallback.
        """
        self._registry = registry or get_routing_registry()
        self._default_policy = default_policy
        self._fallback_enabled = fallback_enabled

        # Components
        self._matcher = PipelineMatcher()
        self._selector = PipelineSelector(
            policy=default_policy,
            fallback_enabled=fallback_enabled,
        )

        # State
        self._state = RouterState.CREATED
        self._lock = threading.RLock()

        # Statistics
        self._routing_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._total_duration_ms = 0

        # Observability
        self._event_publisher = None
        self._metrics = None
        self._trace = None

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def state(self) -> RouterState:
        """Get current state."""
        with self._lock:
            return self._state

    @property
    def routing_count(self) -> int:
        """Get total routing count."""
        return self._routing_count

    @property
    def success_count(self) -> int:
        """Get success count."""
        return self._success_count

    @property
    def failure_count(self) -> int:
        """Get failure count."""
        return self._failure_count

    @property
    def average_duration_ms(self) -> float:
        """Get average routing duration."""
        if self._routing_count == 0:
            return 0.0
        return self._total_duration_ms / self._routing_count

    # =========================================================================
    # Observability
    # =========================================================================

    def set_event_publisher(self, publisher) -> None:
        """Set event publisher.

        Args:
            publisher: Event publisher instance.
        """
        self._event_publisher = publisher

    def set_metrics(self, metrics) -> None:
        """Set metrics collector.

        Args:
            metrics: Metrics collector.
        """
        self._metrics = metrics

    def set_trace(self, trace) -> None:
        """Set trace collector.

        Args:
            trace: Trace collector.
        """
        self._trace = trace

    # =========================================================================
    # Routing
    # =========================================================================

    def route(
        self,
        intent_type: str,
        intent_data: dict | None = None,
        session_id: str = "",
        correlation_id: str = "",
        user_id: str = "",
        tenant_id: str = "",
        hospital_id: str = "",
        priority: int = 0,
        available_capabilities: list[str] | None = None,
        required_capabilities: list[str] | None = None,
        context_data: dict | None = None,
        **kwargs: Any,
    ) -> RoutingResult:
        """Route an intent to the appropriate pipeline.

        Args:
            intent_type: Type of intent.
            intent_data: Intent data.
            session_id: Session ID.
            correlation_id: Correlation ID.
            user_id: User ID.
            tenant_id: Tenant ID.
            hospital_id: Hospital ID.
            priority: Routing priority.
            available_capabilities: Available capabilities.
            required_capabilities: Required capabilities.
            context_data: Additional context data.
            **kwargs: Additional routing parameters.

        Returns:
            RoutingResult with selected pipeline.

        Raises:
            RouterException: If routing fails.
        """
        result = RoutingResult()
        start_time = datetime.now(UTC)

        try:
            result.start()

            # Create context
            context = RouterContext(
                intent_type=intent_type,
                intent_data=intent_data or {},
                session_id=session_id or f"sess_{uuid.uuid4().hex[:16]}",
                correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:16]}",
                user_id=user_id,
                tenant_id=tenant_id,
                hospital_id=hospital_id,
                priority=priority,
                available_capabilities=available_capabilities or [],
                required_capabilities=required_capabilities or [],
                context_data=context_data or {},
                metadata=kwargs,
            )

            result.add_trace_entry("context_created", context.to_dict())
            result.add_event("RoutingStarted", {"intent_type": intent_type})

            # Update state
            with self._lock:
                self._state = RouterState.MATCHING

            # Match pipelines
            candidates = self._match_pipelines(context, result)

            # Update state
            with self._lock:
                self._state = RouterState.SELECTING

            # Select pipeline
            selected = self._selector.select(context, candidates, result)

            if selected:
                result.set_selected_pipeline(
                    selected,
                    reason=f"Selected by {self._selector.policy.value} policy",
                )
                result.add_event("PipelineSelected", {
                    "pipeline_name": selected.pipeline_name,
                    "policy": self._selector.policy.value,
                })

            # Complete
            result.complete()

            # Update statistics
            with self._lock:
                self._routing_count += 1
                duration = (datetime.now(UTC) - start_time).total_seconds() * 1000
                self._total_duration_ms += duration

                if result.is_success:
                    self._success_count += 1
                    self._state = RouterState.READY
                else:
                    self._failure_count += 1
                    self._state = RouterState.FAILED

            result.add_event("RoutingCompleted", {
                "success": result.is_success,
                "duration_ms": result.duration_ms,
            })

            return result

        except Exception as e:
            result.fail(str(e))
            with self._lock:
                self._failure_count += 1
                self._state = RouterState.FAILED
            result.add_event("RoutingFailed", {"error": str(e)})
            return result

    def route_with_context(
        self,
        context: RouterContext,
    ) -> RoutingResult:
        """Route using an existing context.

        Args:
            context: Routing context.

        Returns:
            RoutingResult with selected pipeline.
        """
        return self.route(
            intent_type=context.intent_type,
            intent_data=context.intent_data,
            session_id=context.session_id,
            correlation_id=context.correlation_id,
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            hospital_id=context.hospital_id,
            priority=context.priority,
            available_capabilities=context.available_capabilities,
            required_capabilities=context.required_capabilities,
            context_data=context.context_data,
            **context.metadata,
        )

    # =========================================================================
    # Matching
    # =========================================================================

    def _match_pipelines(
        self,
        context: RouterContext,
        result: RoutingResult,
    ) -> list[CandidatePipeline]:
        """Match pipelines to context.

        Args:
            context: Routing context.
            result: Routing result.

        Returns:
            List of candidate pipelines.
        """
        candidates: list[CandidatePipeline] = []

        # Get all registered pipelines
        pipelines = self._registry.list_pipelines()

        result.add_trace_entry("matching_start", {
            "pipeline_count": len(pipelines),
            "intent_type": context.intent_type,
        })

        for metadata in pipelines:
            candidate = self._matcher.match(context, metadata)
            candidates.append(candidate)

            if candidate.score > 0:
                result.add_trace_entry("pipeline_matched", {
                    "pipeline": metadata.pipeline_name,
                    "score": candidate.score,
                    "match_result": candidate.match_result.value,
                })

        # Sort by score
        candidates.sort(key=lambda c: c.score, reverse=True)

        result.add_trace_entry("matching_complete", {
            "candidate_count": len(candidates),
        })

        return candidates

    # =========================================================================
    # Utility
    # =========================================================================

    def get_statistics(self) -> dict:
        """Get router statistics.

        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            return {
                "routing_count": self._routing_count,
                "success_count": self._success_count,
                "failure_count": self._failure_count,
                "success_rate": (
                    self._success_count / self._routing_count * 100
                    if self._routing_count > 0 else 0
                ),
                "average_duration_ms": self.average_duration_ms,
            }

    def reset_statistics(self) -> None:
        """Reset router statistics."""
        with self._lock:
            self._routing_count = 0
            self._success_count = 0
            self._failure_count = 0
            self._total_duration_ms = 0

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "state": self._state.value,
            "default_policy": self._default_policy.value,
            "fallback_enabled": self._fallback_enabled,
            "pipeline_count": self._registry.get_pipeline_count(),
            "rule_count": self._registry.get_rule_count(),
            "statistics": self.get_statistics(),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CapabilityRouter("
            f"state={self._state.value}, "
            f"policy={self._default_policy.value}, "
            f"routings={self._routing_count})"
        )
