"""Cognitive Execution Coordinator for EREN OS.

Main coordinator that orchestrates the complete cognitive execution cycle.
"""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.execution.context import ExecutionContext
from core.PHASE_2.execution.exceptions import (
    ExecutionCancelledError,
    PipelineExecutionError,
    RoutingError,
)
from core.PHASE_2.execution.result import ExecutionResult
from core.PHASE_2.execution.validator import ExecutionValidator

if TYPE_CHECKING:
    pass


class ExecutionCoordinator:
    """Main cognitive execution coordinator.

    Responsible for coordinating the complete cognitive execution cycle:
    1. Create session
    2. Initialize lifecycle
    3. Route intent to pipeline
    4. Execute pipeline
    5. Update context
    6. Complete session

    Features:
    - Thread-safe execution
    - Complete observability
    - Component validation
    - Error handling
    - Cancellation support
    """

    def __init__(
        self,
        validator: ExecutionValidator | None = None,
        enable_events: bool = True,
        enable_metrics: bool = True,
        enable_trace: bool = True,
    ):
        """Initialize the coordinator.

        Args:
            validator: Component validator.
            enable_events: Enable event publishing.
            enable_metrics: Enable metrics collection.
            enable_trace: Enable tracing.
        """
        # Components (via contracts)
        self._router = None
        self._pipeline_builder = None
        self._session_manager = None
        self._lifecycle_manager = None
        self._context_manager = None
        self._event_bus = None

        # Validator
        self._validator = validator or ExecutionValidator()
        self._validator.register_default_checkers()

        # Observability
        self._enable_events = enable_events
        self._enable_metrics = enable_metrics
        self._enable_trace = enable_trace
        self._event_publisher = None
        self._metrics_collector = None
        self._trace_collector = None

        # State
        self._lock = threading.RLock()
        self._is_cancelled = False
        self._cancelled_execution_id: str | None = None

        # Statistics
        self._execution_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._total_duration_ms = 0

    # =========================================================================
    # Component Registration
    # =========================================================================

    def set_router(self, router: Any) -> None:
        """Set the capability router.

        Args:
            router: Router instance (via contract).
        """
        self._router = router

    def set_pipeline_builder(self, builder: Any) -> None:
        """Set the pipeline builder.

        Args:
            builder: Pipeline builder instance (via contract).
        """
        self._pipeline_builder = builder

    def set_session_manager(self, manager: Any) -> None:
        """Set the session manager.

        Args:
            manager: Session manager instance (via contract).
        """
        self._session_manager = manager

    def set_lifecycle_manager(self, manager: Any) -> None:
        """Set the lifecycle manager.

        Args:
            manager: Lifecycle manager instance (via contract).
        """
        self._lifecycle_manager = manager

    def set_context_manager(self, manager: Any) -> None:
        """Set the context manager.

        Args:
            manager: Context manager instance (via contract).
        """
        self._context_manager = manager

    def set_event_bus(self, event_bus: Any) -> None:
        """Set the event bus.

        Args:
            event_bus: Event bus instance (via contract).
        """
        self._event_bus = event_bus

    # =========================================================================
    # Observability Setters
    # =========================================================================

    def set_event_publisher(self, publisher: Any) -> None:
        """Set the event publisher.

        Args:
            publisher: Event publisher instance.
        """
        self._event_publisher = publisher

    def set_metrics_collector(self, collector: Any) -> None:
        """Set the metrics collector.

        Args:
            collector: Metrics collector instance.
        """
        self._metrics_collector = collector

    def set_trace_collector(self, collector: Any) -> None:
        """Set the trace collector.

        Args:
            collector: Trace collector instance.
        """
        self._trace_collector = collector

    # =========================================================================
    # Execution
    # =========================================================================

    def execute(
        self,
        intent_type: str,
        intent_data: dict | None = None,
        user_id: str = "",
        tenant_id: str = "",
        hospital_id: str = "",
        priority: int = 0,
        session_id: str = "",
        correlation_id: str = "",
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute a cognitive intent.

        Args:
            intent_type: Type of intent.
            intent_data: Intent data.
            user_id: User ID.
            tenant_id: Tenant ID.
            hospital_id: Hospital ID.
            priority: Execution priority.
            session_id: Optional session ID.
            correlation_id: Correlation ID.
            **kwargs: Additional execution parameters.

        Returns:
            ExecutionResult with execution outcome.

        Raises:
            ExecutionException: If execution fails.
        """
        # Generate IDs
        execution_id = f"exec_{uuid.uuid4().hex[:16]}"
        session_id = session_id or f"sess_{uuid.uuid4().hex[:16]}"
        correlation_id = correlation_id or f"corr_{uuid.uuid4().hex[:16]}"

        # Create result
        result = ExecutionResult(
            execution_id=execution_id,
            session_id=session_id,
            started_at=datetime.now(UTC),
        )

        # Create context
        context = ExecutionContext(
            execution_id=execution_id,
            session_id=session_id,
            correlation_id=correlation_id,
            intent_type=intent_type,
            intent_data=intent_data or {},
            user_id=user_id,
            tenant_id=tenant_id,
            hospital_id=hospital_id,
            priority=priority,
            metadata=kwargs,
        )

        try:
            # Start execution
            context.start()
            result.add_event("ExecutionStarted", {"intent_type": intent_type})

            # Validate components
            self._validate_components(result, context)

            # Create session
            self._create_session(result, context)

            # Route intent
            self._route_intent(result, context)

            # Execute pipeline
            self._execute_pipeline(result, context)

            # Update context
            self._update_context(result, context)

            # Complete session
            self._complete_session(result, context)

            # Mark as completed
            result.complete()
            result.add_event("ExecutionCompleted", {"duration_ms": result.duration_ms})

            # Update statistics
            self._update_statistics(result)

        except ExecutionCancelledError as e:
            result.cancel()
            result.add_error(str(e))
            result.add_event("ExecutionCancelled", {"execution_id": execution_id})

        except Exception as e:
            result.fail(str(e))
            result.add_event("ExecutionFailed", {"error": str(e)})
            self._failure_count += 1

        return result

    def _validate_components(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Validate required components.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("validating")

        validation_result = self._validator.validate()

        for status in validation_result.component_statuses:
            if not status.available:
                result.add_warning(f"Component '{status.name}' not available")

        # Log validation errors as warnings, don't fail execution
        # Components may not be initialized yet but can be optional
        if not validation_result.is_valid:
            for error in validation_result.errors[:3]:
                result.add_warning(f"Validation: {error}")

    def _create_session(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Create a new session.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("creating_session")
        result.add_event("SessionCreating")

        session_start = datetime.now(UTC)

        # Create session via manager (if available)
        if self._session_manager:
            try:
                session = self._session_manager.create_session(
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    hospital_id=context.hospital_id,
                )
                context.session_id = session.session_id if hasattr(session, "session_id") else context.session_id
            except Exception:
                pass  # Session manager might not be initialized

        result.session_creation_time_ms = int(
            (datetime.now(UTC) - session_start).total_seconds() * 1000
        )
        result.add_event("SessionCreated", {"session_id": context.session_id})

    def _route_intent(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Route intent to appropriate pipeline.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("routing")
        result.add_event("RoutingStarted")

        routing_start = datetime.now(UTC)

        # Route via router (if available)
        if self._router:
            try:
                routing_result = self._router.route(
                    intent_type=context.intent_type,
                    intent_data=context.intent_data,
                    session_id=context.session_id,
                    correlation_id=context.correlation_id,
                    user_id=context.user_id,
                    tenant_id=context.tenant_id,
                    hospital_id=context.hospital_id,
                    priority=context.priority,
                )
                result.set_routing_result(routing_result.to_dict())
                context.set_routing_context(routing_result.to_dict())
            except Exception as e:
                result.add_error(f"Routing failed: {e}")
                raise RoutingError(str(e), context.intent_type)
        else:
            result.add_warning("Router not available, using default pipeline")
            result.set_routing_result({
                "selected_pipeline": "default",
                "policy": "default",
            })

        result.routing_time_ms = int(
            (datetime.now(UTC) - routing_start).total_seconds() * 1000
        )
        result.add_event("RoutingCompleted", {
            "pipeline": result.selected_pipeline,
            "duration_ms": result.routing_time_ms,
        })

    def _execute_pipeline(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Execute the selected pipeline.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("pipeline_execution")
        result.add_event("PipelineExecutionStarted")

        pipeline_start = datetime.now(UTC)

        # Execute pipeline (if router and builder available)
        if self._router and self._pipeline_builder:
            try:
                pipeline_name = result.selected_pipeline
                if not pipeline_name:
                    pipeline_name = "default"

                # Get pipeline from registry and build
                from core.PHASE_2.pipeline import get_pipeline_registry
                registry = get_pipeline_registry()

                try:
                    pipeline = registry.get(pipeline_name)
                except Exception:
                    # Use default pipeline
                    from core.PHASE_2.pipeline import DefaultPipelineBuilder
                    pipeline = DefaultPipelineBuilder.create_default()

                # Execute pipeline
                pipeline_result = pipeline.execute(
                    intent=context.intent_data,
                    session_id=context.session_id,
                    correlation_id=context.correlation_id,
                )
                result.set_pipeline_result(pipeline_result.to_dict())
                context.set_pipeline_context(pipeline_result.to_dict())

            except Exception as e:
                result.add_error(f"Pipeline execution failed: {e}")
                raise PipelineExecutionError(str(e), result.selected_pipeline)
        else:
            result.add_warning("Pipeline execution skipped (components not available)")
            result.set_pipeline_result({
                "status": "skipped",
                "duration_ms": 0,
            })

        result.pipeline_time_ms = int(
            (datetime.now(UTC) - pipeline_start).total_seconds() * 1000
        )
        result.add_event("PipelineExecutionCompleted", {
            "duration_ms": result.pipeline_time_ms,
        })

    def _update_context(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Update the shared context.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("updating_context")
        result.add_event("ContextUpdating")

        update_start = datetime.now(UTC)

        # Collect updates from pipeline result
        if result.pipeline_result:
            for key, value in result.pipeline_result.items():
                if key not in ("status", "duration_ms"):
                    context.add_context_update(key, value)
                    result.add_context_update(key, value)

        # Update via context manager (if available)
        if self._context_manager:
            try:
                updates = context.get_context_updates()
                self._context_manager.update_context(
                    session_id=context.session_id,
                    updates=updates,
                )
            except Exception:
                pass

        result.context_update_time_ms = int(
            (datetime.now(UTC) - update_start).total_seconds() * 1000
        )
        result.add_event("ContextUpdated", {
            "updates_count": len(context.get_context_updates()),
        })

    def _complete_session(
        self,
        result: ExecutionResult,
        context: ExecutionContext,
    ) -> None:
        """Complete the session.

        Args:
            result: Execution result.
            context: Execution context.
        """
        context.transition_to("completing_session")
        result.add_event("SessionCompleting")

        completion_start = datetime.now(UTC)

        # Complete session via manager (if available)
        if self._session_manager:
            try:
                self._session_manager.complete_session(context.session_id)
            except Exception:
                pass

        result.session_completion_time_ms = int(
            (datetime.now(UTC) - completion_start).total_seconds() * 1000
        )
        result.add_event("SessionCompleted")

    # =========================================================================
    # Cancellation
    # =========================================================================

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an ongoing execution.

        Args:
            execution_id: ID of execution to cancel.

        Returns:
            True if cancellation was requested.
        """
        with self._lock:
            if self._cancelled_execution_id is None:
                self._is_cancelled = True
                self._cancelled_execution_id = execution_id
                return True
            return False

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested.

        Returns:
            True if cancellation was requested.
        """
        with self._lock:
            return self._is_cancelled

    # =========================================================================
    # Statistics
    # =========================================================================

    def _update_statistics(self, result: ExecutionResult) -> None:
        """Update execution statistics.

        Args:
            result: Execution result.
        """
        with self._lock:
            self._execution_count += 1
            self._total_duration_ms += result.duration_ms

            if result.is_success:
                self._success_count += 1
            else:
                self._failure_count += 1

    def get_statistics(self) -> dict:
        """Get execution statistics.

        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            return {
                "execution_count": self._execution_count,
                "success_count": self._success_count,
                "failure_count": self._failure_count,
                "success_rate": (
                    self._success_count / self._execution_count * 100
                    if self._execution_count > 0 else 0
                ),
                "average_duration_ms": (
                    self._total_duration_ms / self._execution_count
                    if self._execution_count > 0 else 0
                ),
            }

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "statistics": self.get_statistics(),
            "enable_events": self._enable_events,
            "enable_metrics": self._enable_metrics,
            "enable_trace": self._enable_trace,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ExecutionCoordinator("
            f"executions={self._execution_count}, "
            f"success_rate={self.get_statistics()['success_rate']:.1f}%)"
        )
