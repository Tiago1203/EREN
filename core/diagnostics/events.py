"""Diagnostics Events for EREN OS Diagnostics.

Publishes diagnostic events to the Event Bus:
- DiagnosticsStarted
- HealthCheckStarted
- HealthCheckCompleted
- ValidationStarted
- ValidationCompleted
- IntegrationCheckCompleted
- PerformanceMeasured
- ReportGenerated
- DiagnosticsCompleted
- DiagnosticsFailed

Philosophy:
    Diagnostics should be observable. Every diagnostic action is an event.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class DiagnosticsEventType(str, Enum):
    """Event types for diagnostics operations."""

    DIAGNOSTICS_STARTED = "diagnostics_started"
    DIAGNOSTICS_COMPLETED = "diagnostics_completed"
    DIAGNOSTICS_FAILED = "diagnostics_failed"
    HEALTH_CHECK_STARTED = "health_check_started"
    HEALTH_CHECK_COMPLETED = "health_check_completed"
    READINESS_CHECK_STARTED = "readiness_check_started"
    READINESS_CHECK_COMPLETED = "readiness_check_completed"
    LIVENESS_CHECK_STARTED = "liveness_check_started"
    LIVENESS_CHECK_COMPLETED = "liveness_check_completed"
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    ARCHITECTURE_VALIDATION_STARTED = "architecture_validation_started"
    ARCHITECTURE_VALIDATION_COMPLETED = "architecture_validation_completed"
    CONTRACT_VALIDATION_STARTED = "contract_validation_started"
    CONTRACT_VALIDATION_COMPLETED = "contract_validation_completed"
    DEPENDENCY_VALIDATION_STARTED = "dependency_validation_started"
    DEPENDENCY_VALIDATION_COMPLETED = "dependency_validation_completed"
    INTEGRATION_CHECK_STARTED = "integration_check_started"
    INTEGRATION_CHECK_COMPLETED = "integration_check_completed"
    RUNTIME_VALIDATION_STARTED = "runtime_validation_started"
    RUNTIME_VALIDATION_COMPLETED = "runtime_validation_completed"
    PERFORMANCE_MEASURED = "performance_measured"
    REPORT_GENERATED = "report_generated"
    SCORE_CALCULATED = "score_calculated"
    COMPONENT_HEALTH_CHANGED = "component_health_changed"
    ISSUE_DETECTED = "issue_detected"
    CRITICAL_ISSUE_DETECTED = "critical_issue_detected"


class DiagnosticsEventPublisher:
    """Publishes diagnostics events to the Event Bus.

    Integrates with EREN's Event Bus to publish all diagnostic events.
    """

    def __init__(self, event_bus=None):
        """Initialize the event publisher.

        Args:
            event_bus: Optional Event Bus instance. If None, events are logged.
        """
        self._event_bus = event_bus
        self._event_history: list[dict] = []
        self._lock = threading.RLock()
        self._subscribers: list[callable] = []

    def set_event_bus(self, event_bus) -> None:
        """Set the Event Bus instance.

        Args:
            event_bus: Event Bus to use for publishing.
        """
        self._event_bus = event_bus

    def publish(
        self,
        event_type: DiagnosticsEventType,
        source: str = "diagnostics",
        correlation_id: str = "",
        session_id: str = "",
        payload: dict | None = None,
    ) -> None:
        """Publish a diagnostics event.

        Args:
            event_type: Type of event to publish.
            source: Source component.
            correlation_id: Correlation ID for tracking.
            session_id: Session ID if applicable.
            payload: Additional event payload.
        """
        import uuid

        event = {
            "event_type": event_type.value if isinstance(event_type, Enum) else event_type,
            "source": source,
            "correlation_id": correlation_id or f"diag_{uuid.uuid4().hex[:16]}",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload or {},
        }

        with self._lock:
            self._event_history.append(event)

        # Publish to Event Bus if available
        if self._event_bus:
            try:
                from core.events.models import Event, EventType
                self._event_bus.publish(Event(
                    type=self._map_to_core_event_type(event_type),
                    source=source,
                    correlation_id=correlation_id,
                    session_id=session_id,
                    payload=payload or {},
                ))
            except Exception:
                # Fall back to logging if Event Bus fails
                self._log_event(event)
        else:
            self._log_event(event)

        # Notify local subscribers
        self._notify_subscribers(event)

    def _map_to_core_event_type(self, diag_type: DiagnosticsEventType) -> "EventType":
        """Map diagnostics event type to core event type.

        Args:
            diag_type: Diagnostics event type.

        Returns:
            Mapped core EventType.
        """
        from core.events.models import EventType

        mapping = {
            DiagnosticsEventType.DIAGNOSTICS_STARTED: EventType.DIAGNOSTIC_STARTED,
            DiagnosticsEventType.DIAGNOSTICS_COMPLETED: EventType.DIAGNOSTIC_COMPLETED,
        }

        return mapping.get(diag_type, EventType.DIAGNOSTIC_STARTED)

    def _log_event(self, event: dict) -> None:
        """Log an event (fallback when no Event Bus).

        Args:
            event: Event dictionary.
        """
        import logging
        logging.debug(f"Diagnostics Event: {event['event_type']} - {event.get('payload', {})}")

    def _notify_subscribers(self, event: dict) -> None:
        """Notify local subscribers of an event.

        Args:
            event: Event dictionary.
        """
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def subscribe(self, callback: callable) -> None:
        """Subscribe to diagnostics events.

        Args:
            callback: Function to call with each event.
        """
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from diagnostics events.

        Args:
            callback: Function to remove.
        """
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def get_event_history(self) -> list[dict]:
        """Get history of published events.

        Returns:
            List of event dictionaries.
        """
        with self._lock:
            return list(self._event_history)

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()


# Convenience functions for publishing events
_publisher: DiagnosticsEventPublisher | None = None
_publisher_lock = threading.Lock()


def get_publisher() -> DiagnosticsEventPublisher:
    """Get the global diagnostics event publisher.

    Returns:
        Global DiagnosticsEventPublisher instance.
    """
    global _publisher
    with _publisher_lock:
        if _publisher is None:
            _publisher = DiagnosticsEventPublisher()
        return _publisher


def set_publisher(publisher: DiagnosticsEventPublisher) -> None:
    """Set the global diagnostics event publisher.

    Args:
        publisher: Publisher instance to use globally.
    """
    global _publisher
    with _publisher_lock:
        _publisher = publisher


def publish_diagnostics_started(correlation_id: str = "") -> None:
    """Publish DiagnosticsStarted event.

    Args:
        correlation_id: Correlation ID for tracking.
    """
    get_publisher().publish(
        DiagnosticsEventType.DIAGNOSTICS_STARTED,
        correlation_id=correlation_id,
    )


def publish_diagnostics_completed(
    correlation_id: str = "",
    duration_ms: int = 0,
    score: float = 0.0,
) -> None:
    """Publish DiagnosticsCompleted event.

    Args:
        correlation_id: Correlation ID for tracking.
        duration_ms: Total duration in milliseconds.
        score: Final diagnostic score.
    """
    get_publisher().publish(
        DiagnosticsEventType.DIAGNOSTICS_COMPLETED,
        correlation_id=correlation_id,
        payload={
            "duration_ms": duration_ms,
            "score": score,
        },
    )


def publish_diagnostics_failed(
    correlation_id: str = "",
    error: str = "",
) -> None:
    """Publish DiagnosticsFailed event.

    Args:
        correlation_id: Correlation ID for tracking.
        error: Error message.
    """
    get_publisher().publish(
        DiagnosticsEventType.DIAGNOSTICS_FAILED,
        correlation_id=correlation_id,
        payload={
            "error": error,
        },
    )


def publish_validation_started(
    validation_type: str,
    correlation_id: str = "",
) -> None:
    """Publish ValidationStarted event.

    Args:
        validation_type: Type of validation starting.
        correlation_id: Correlation ID for tracking.
    """
    get_publisher().publish(
        DiagnosticsEventType.VALIDATION_STARTED,
        correlation_id=correlation_id,
        payload={
            "validation_type": validation_type,
        },
    )


def publish_validation_completed(
    validation_type: str,
    correlation_id: str = "",
    score: float = 0.0,
    passed: bool = True,
) -> None:
    """Publish ValidationCompleted event.

    Args:
        validation_type: Type of validation completed.
        correlation_id: Correlation ID for tracking.
        score: Validation score.
        passed: Whether validation passed.
    """
    get_publisher().publish(
        DiagnosticsEventType.VALIDATION_COMPLETED,
        correlation_id=correlation_id,
        payload={
            "validation_type": validation_type,
            "score": score,
            "passed": passed,
        },
    )


def publish_report_generated(
    correlation_id: str = "",
    score: float = 0.0,
    production_ready: bool = False,
) -> None:
    """Publish ReportGenerated event.

    Args:
        correlation_id: Correlation ID for tracking.
        score: Final score.
        production_ready: Whether system is production ready.
    """
    get_publisher().publish(
        DiagnosticsEventType.REPORT_GENERATED,
        correlation_id=correlation_id,
        payload={
            "score": score,
            "production_ready": production_ready,
        },
    )


def publish_issue_detected(
    issue_type: str,
    severity: str,
    description: str,
    correlation_id: str = "",
) -> None:
    """Publish IssueDetected event.

    Args:
        issue_type: Type of issue detected.
        severity: Issue severity.
        description: Issue description.
        correlation_id: Correlation ID for tracking.
    """
    event_type = (
        DiagnosticsEventType.CRITICAL_ISSUE_DETECTED
        if severity == "critical"
        else DiagnosticsEventType.ISSUE_DETECTED
    )

    get_publisher().publish(
        event_type,
        correlation_id=correlation_id,
        payload={
            "issue_type": issue_type,
            "severity": severity,
            "description": description,
        },
    )
