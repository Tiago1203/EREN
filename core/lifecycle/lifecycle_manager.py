"""Cognitive Lifecycle Manager - Core Engine."""

import uuid

from core.lifecycle.lifecycle_events import LifecycleEventPublisher, LifecycleEventType
from core.lifecycle.lifecycle_metrics import LifecycleMetricsCollector
from core.lifecycle.lifecycle_policy import LifecyclePolicy, LifecyclePolicyPresets
from core.lifecycle.lifecycle_state_machine import LifecycleStateMachine
from core.lifecycle.lifecycle_trace import LifecycleTraceCollector
from core.lifecycle.lifecycle_types import VALID_TRANSITIONS


class CognitiveLifecycleManager:
    """The main cognitive lifecycle manager.

    Controls all valid transitions of cognitive sessions.
    """

    def __init__(self, policy: LifecyclePolicy = None):
        self._policy = policy or LifecyclePolicy()
        self._lifecycles = {}
        self._event_publisher = LifecycleEventPublisher()
        self._metrics = LifecycleMetricsCollector()
        self._trace = LifecycleTraceCollector()

    def create_lifecycle(self, session_id: str, correlation_id: str = "") -> LifecycleStateMachine:
        """Create a new lifecycle.

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.

        Returns:
            State machine instance.
        """
        correlation_id = correlation_id or f"corr_{uuid.uuid4().hex[:16]}"
        machine = LifecycleStateMachine()
        self._lifecycles[session_id] = machine

        self._trace.add_entry(
            session_id=session_id,
            correlation_id=correlation_id,
            from_state="",
            to_state="created",
            event="create",
            reason="Lifecycle created",
        )

        self._event_publisher.publish(
            LifecycleEventType.LIFECYCLE_STARTED,
            session_id=session_id,
        )

        return machine

    def get_lifecycle(self, session_id: str) -> LifecycleStateMachine:
        """Get lifecycle state machine.

        Args:
            session_id: Session ID.

        Returns:
            State machine or None.
        """
        return self._lifecycles.get(session_id)

    def trigger_event(
        self,
        session_id: str,
        event: str,
        reason: str = "",
        actor: str = "",
        metadata: dict = None,
    ) -> tuple[bool, str | None, dict | None]:
        """Trigger a lifecycle event.

        Args:
            session_id: Session ID.
            event: Event to trigger.
            reason: Reason for event.
            actor: Actor triggering event.
            metadata: Additional metadata.

        Returns:
            Tuple of (success, new_state, transition_data).
        """
        machine = self._lifecycles.get(session_id)
        if not machine:
            return False, None, {"error": "Lifecycle not found"}

        old_state = machine.current_state
        success, new_state, transition_data = machine.transition(
            event, VALID_TRANSITIONS, reason, metadata
        )

        if success:
            self._metrics.record_transition()
            self._trace.add_entry(
                session_id=session_id,
                correlation_id=metadata.get("correlation_id", "") if metadata else "",
                from_state=old_state,
                to_state=new_state,
                event=event,
                reason=reason,
                actor=actor,
                metadata=metadata,
            )

            self._event_publisher.publish(
                self._get_event_type(event),
                session_id=session_id,
                from_state=old_state,
                to_state=new_state,
            )

            if new_state == "completed":
                self._metrics.record_completed()
            elif new_state == "failed":
                self._metrics.record_failed()
            elif new_state == "cancelled":
                self._metrics.record_cancelled()
            elif new_state == "archived":
                self._metrics.record_archived()
        else:
            self._metrics.record_invalid_transition()
            self._event_publisher.publish(
                LifecycleEventType.INVALID_TRANSITION_DETECTED,
                session_id=session_id,
                current_state=old_state,
                event=event,
            )

        return success, new_state, transition_data

    def _get_event_type(self, event: str) -> str:
        """Get event type for event."""
        mapping = {
            "initialize": LifecycleEventType.LIFECYCLE_INITIALIZED,
            "ready": LifecycleEventType.LIFECYCLE_READY,
            "activate": LifecycleEventType.LIFECYCLE_ACTIVATED,
            "pause": LifecycleEventType.LIFECYCLE_PAUSED,
            "resume": LifecycleEventType.LIFECYCLE_RESUMED,
            "recover": LifecycleEventType.LIFECYCLE_RECOVERED,
            "complete": LifecycleEventType.LIFECYCLE_COMPLETED,
            "fail": LifecycleEventType.LIFECYCLE_FAILED,
            "cancel": LifecycleEventType.LIFECYCLE_CANCELLED,
            "archive": LifecycleEventType.LIFECYCLE_ARCHIVED,
        }
        return mapping.get(event, event)

    def get_trace(self, session_id: str) -> list:
        """Get trace for a session."""
        return self._trace.get_trace(session_id)

    def get_metrics(self) -> dict:
        """Get lifecycle metrics."""
        return self._metrics.to_dict()


class LifecycleManagerFactory:
    """Factory for creating lifecycle managers."""

    @staticmethod
    def create_default():
        return CognitiveLifecycleManager()

    @staticmethod
    def create_strict():
        return CognitiveLifecycleManager(policy=LifecyclePolicyPresets.strict())

    @staticmethod
    def create_permissive():
        return CognitiveLifecycleManager(policy=LifecyclePolicyPresets.permissive())
