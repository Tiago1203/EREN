"""Cognitive Reasoning Integration (PR-050).

Integration layer between Cognitive Reasoning Engine and the Cognitive Pipeline.
Provides reasoning-aware stages and event publishing.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from core.reasoning.reasoning_engine import CognitiveReasoningEngine
    from core.reasoning.reasoning_types import (
        Evidence,
        Hypothesis,
        Decision,
        ReasoningStrategy,
    )


# =============================================================================
# Reasoning Events
# =============================================================================


class ReasoningEventType(str, Enum):
    """Types of reasoning events."""

    REASONING_STARTED = "reasoning_started"
    REASONING_COMPLETED = "reasoning_completed"
    REASONING_FAILED = "reasoning_failed"
    EVIDENCE_COLLECTED = "evidence_collected"
    HYPOTHESIS_GENERATED = "hypothesis_generated"
    HYPOTHESIS_EVALUATED = "hypothesis_evaluated"
    DECISION_MADE = "decision_made"
    CONFIDENCE_CALCULATED = "confidence_calculated"
    EXPLANATION_GENERATED = "explanation_generated"


@dataclass
class ReasoningEvent:
    """Reasoning event for the Event Bus."""

    event_type: ReasoningEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = ""
    correlation_id: str = ""
    strategy: str = ""
    evidence_count: int = 0
    hypothesis_count: int = 0
    confidence: float = 0.0
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Reasoning Event Publisher
# =============================================================================


class ReasoningEventPublisher:
    """Publisher for reasoning events."""

    def __init__(self):
        """Initialize the publisher."""
        self._subscribers: list[callable] = []
        self._history: list[ReasoningEvent] = []

    def subscribe(self, callback: callable) -> None:
        """Subscribe to reasoning events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from reasoning events."""
        self._subscribers.remove(callback)

    def publish(self, event: ReasoningEvent) -> None:
        """Publish a reasoning event."""
        self._history.append(event)
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def get_history(
        self,
        session_id: str | None = None,
        event_type: ReasoningEventType | None = None,
        limit: int = 100,
    ) -> list[ReasoningEvent]:
        """Get event history."""
        history = self._history

        if session_id:
            history = [e for e in history if e.session_id == session_id]
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()


# =============================================================================
# Reasoning Metrics
# =============================================================================


@dataclass
class ReasoningMetrics:
    """Metrics for reasoning operations."""

    total_reasoning_sessions: int = 0
    successful_sessions: int = 0
    failed_sessions: int = 0
    total_evidence_collected: int = 0
    total_hypotheses_generated: int = 0
    total_decisions_made: int = 0
    average_confidence: float = 0.0
    average_reasoning_duration_ms: float = 0.0
    strategy_usage: dict[str, int] = field(default_factory=dict)


# =============================================================================
# Reasoning Tracer
# =============================================================================


@dataclass
class ReasoningTrace:
    """Trace of a reasoning operation."""

    operation: str
    session_id: str = ""
    correlation_id: str = ""
    strategy: str = ""
    start_time: str = ""
    end_time: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    stages_completed: list[str] = field(default_factory=list)
    evidence_used: list[str] = field(default_factory=list)
    hypotheses_generated: list[str] = field(default_factory=list)


class ReasoningTracer:
    """Tracer for reasoning operations."""

    def __init__(self):
        """Initialize the tracer."""
        self._traces: list[ReasoningTrace] = []
        self._active_traces: dict[int, ReasoningTrace] = {}

    def begin_trace(
        self,
        operation: str,
        session_id: str = "",
        correlation_id: str = "",
        strategy: str = "",
    ) -> int:
        """Begin a trace. Returns trace ID."""
        trace_id = len(self._traces)
        trace = ReasoningTrace(
            operation=operation,
            session_id=session_id,
            correlation_id=correlation_id,
            strategy=strategy,
            start_time=datetime.now(UTC).isoformat(),
        )
        self._traces.append(trace)
        self._active_traces[trace_id] = trace
        return trace_id

    def end_trace(
        self,
        trace_id: int,
        success: bool = True,
        error: str = "",
        stages_completed: list[str] | None = None,
    ) -> None:
        """End a trace."""
        if trace_id in self._active_traces:
            trace = self._active_traces[trace_id]
            trace.end_time = datetime.now(UTC).isoformat()
            trace.success = success
            trace.error = error
            if stages_completed:
                trace.stages_completed = stages_completed

            if trace.start_time:
                start = datetime.fromisoformat(trace.start_time)
                end = datetime.fromisoformat(trace.end_time)
                trace.duration_ms = (end - start).total_seconds() * 1000

            del self._active_traces[trace_id]

    def add_evidence(self, trace_id: int, evidence_id: str) -> None:
        """Add evidence to a trace."""
        if trace_id in self._active_traces:
            self._active_traces[trace_id].evidence_used.append(evidence_id)

    def add_hypothesis(self, trace_id: int, hypothesis_id: str) -> None:
        """Add hypothesis to a trace."""
        if trace_id in self._active_traces:
            self._active_traces[trace_id].hypotheses_generated.append(hypothesis_id)

    def get_traces(self, limit: int = 100) -> list[ReasoningTrace]:
        """Get recent traces."""
        return self._traces[-limit:]


# =============================================================================
# Reasoning Integration Wrapper
# =============================================================================


class CognitiveReasoningIntegration:
    """Integration layer for cognitive reasoning.

    Provides:
    - Event publishing for all reasoning operations
    - Metrics collection
    - Tracing
    - Strategy selection
    """

    def __init__(self, engine: "CognitiveReasoningEngine" = None):
        """Initialize the integration layer.

        Args:
            engine: The underlying reasoning engine.
        """
        from core.reasoning.reasoning_engine import CognitiveReasoningEngine
        
        self._engine = engine or CognitiveReasoningEngine()
        self._publisher = ReasoningEventPublisher()
        self._metrics = ReasoningMetrics()
        self._tracer = ReasoningTracer()
        self._default_strategy = "focused"

    @property
    def engine(self) -> "CognitiveReasoningEngine":
        """Get the underlying engine."""
        return self._engine

    @property
    def publisher(self) -> ReasoningEventPublisher:
        """Get the event publisher."""
        return self._publisher

    @property
    def metrics(self) -> ReasoningMetrics:
        """Get current metrics."""
        return self._metrics

    def reason(
        self,
        question: str,
        evidence: list[Any] | None = None,
        strategy: str | None = None,
        session_id: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Perform reasoning with full instrumentation.

        Args:
            question: The question to reason about
            evidence: List of evidence items
            strategy: Reasoning strategy to use
            session_id: Session ID for tracking
            correlation_id: Correlation ID

        Returns:
            Reasoning result dictionary.
        """
        import time

        strategy = strategy or self._default_strategy
        trace_id = self._tracer.begin_trace(
            "reason",
            session_id=session_id,
            correlation_id=correlation_id,
            strategy=strategy,
        )

        start = time.perf_counter()
        self._metrics.total_reasoning_sessions += 1

        try:
            # Publish start event
            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.REASONING_STARTED,
                session_id=session_id,
                correlation_id=correlation_id,
                strategy=strategy,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
            ))

            # Perform reasoning
            result = self._engine.reason(
                question=question,
                evidence=evidence or [],
                strategy=strategy,
            )

            # Calculate duration
            duration_ms = (time.perf_counter() - start) * 1000

            # Extract results
            conclusion = result.get("conclusion", "")
            confidence = result.get("confidence", 0.0)
            justification = result.get("justification", {})
            hypotheses = result.get("hypotheses", [])

            # Publish completion event
            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.REASONING_COMPLETED,
                session_id=session_id,
                correlation_id=correlation_id,
                strategy=strategy,
                evidence_count=len(evidence) if evidence else 0,
                hypothesis_count=len(hypotheses),
                confidence=confidence,
                duration_ms=duration_ms,
                success=True,
                metadata={
                    "conclusion": conclusion,
                    "justification": justification,
                },
            ))

            # Update metrics
            self._metrics.successful_sessions += 1
            self._metrics.total_evidence_collected += len(evidence) if evidence else 0
            self._metrics.total_hypotheses_generated += len(hypotheses)
            self._metrics.strategy_usage[strategy] = (
                self._metrics.strategy_usage.get(strategy, 0) + 1
            )

            # End trace
            self._tracer.end_trace(
                trace_id,
                success=True,
                stages_completed=["evidence", "hypothesis", "evaluation", "decision"],
            )

            return {
                "success": True,
                "conclusion": conclusion,
                "confidence": confidence,
                "justification": justification,
                "hypotheses": hypotheses,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000

            # Publish failure event
            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.REASONING_FAILED,
                session_id=session_id,
                correlation_id=correlation_id,
                strategy=strategy,
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            ))

            # Update metrics
            self._metrics.failed_sessions += 1

            # End trace
            self._tracer.end_trace(trace_id, success=False, error=str(e))

            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms,
            }

    def evaluate_hypothesis(
        self,
        hypothesis: Any,
        evidence: list[Any] | None = None,
        session_id: str = "",
    ) -> dict[str, Any]:
        """Evaluate a hypothesis with instrumentation.

        Args:
            hypothesis: The hypothesis to evaluate
            evidence: Supporting evidence
            session_id: Session ID

        Returns:
            Evaluation result.
        """
        import time

        trace_id = self._tracer.begin_trace(
            "evaluate",
            session_id=session_id,
        )

        start = time.perf_counter()

        try:
            result = self._engine.evaluate_hypothesis(
                hypothesis=hypothesis,
                evidence=evidence or [],
            )

            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.HYPOTHESIS_EVALUATED,
                session_id=session_id,
                confidence=result.get("confidence", 0.0),
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
            ))

            self._tracer.end_trace(trace_id, success=True)

            return {
                "success": True,
                "evaluation": result,
            }

        except Exception as e:
            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.HYPOTHESIS_EVALUATED,
                session_id=session_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(e),
            ))

            self._tracer.end_trace(trace_id, success=False, error=str(e))

            return {
                "success": False,
                "error": str(e),
            }

    def generate_explanation(
        self,
        conclusion: str,
        reasoning_chain: dict[str, Any],
        session_id: str = "",
    ) -> dict[str, Any]:
        """Generate explanation for a conclusion.

        Args:
            conclusion: The conclusion to explain
            reasoning_chain: The reasoning chain
            session_id: Session ID

        Returns:
            Explanation result.
        """
        import time

        trace_id = self._tracer.begin_trace(
            "explain",
            session_id=session_id,
        )

        start = time.perf_counter()

        try:
            result = self._engine.explain(
                conclusion=conclusion,
                reasoning_chain=reasoning_chain,
            )

            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.EXPLANATION_GENERATED,
                session_id=session_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=True,
            ))

            self._tracer.end_trace(trace_id, success=True)

            return {
                "success": True,
                "explanation": result,
            }

        except Exception as e:
            self._publisher.publish(ReasoningEvent(
                event_type=ReasoningEventType.EXPLANATION_GENERATED,
                session_id=session_id,
                duration_ms=(time.perf_counter() - start) * 1000,
                success=False,
                error=str(e),
            ))

            self._tracer.end_trace(trace_id, success=False, error=str(e))

            return {
                "success": False,
                "error": str(e),
            }

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all reasoning metrics.

        Returns:
            Dictionary of metrics.
        """
        return {
            "metrics": {
                "total_reasoning_sessions": self._metrics.total_reasoning_sessions,
                "successful_sessions": self._metrics.successful_sessions,
                "failed_sessions": self._metrics.failed_sessions,
                "total_evidence_collected": self._metrics.total_evidence_collected,
                "total_hypotheses_generated": self._metrics.total_hypotheses_generated,
                "total_decisions_made": self._metrics.total_decisions_made,
                "average_confidence": self._metrics.average_confidence,
                "average_reasoning_duration_ms": self._metrics.average_reasoning_duration_ms,
                "strategy_usage": self._metrics.strategy_usage,
            },
            "traces": len(self._tracer._traces),
        }


# =============================================================================
# Factory Function
# =============================================================================


def create_cognitive_reasoning_integration(
    engine: "CognitiveReasoningEngine" = None,
) -> CognitiveReasoningIntegration:
    """Create a cognitive reasoning integration.

    Args:
        engine: Optional reasoning engine (creates new if not provided)

    Returns:
        CognitiveReasoningIntegration instance.
    """
    return CognitiveReasoningIntegration(engine=engine)
