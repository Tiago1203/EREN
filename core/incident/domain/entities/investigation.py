"""Investigation sub-aggregate for Engineering Incident."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from core.shared import EngineerId

from ..value_objects import ActionResult, ActionType, EvidenceType, Feedback, MessageSender, Symptom

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class InvestigationId:
    """Unique identifier for an investigation."""

    value: str

    @classmethod
    def generate(cls) -> InvestigationId:
        return cls(value=f"inv_{uuid4()}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ActionId:
    """Unique identifier for an action."""

    value: str

    @classmethod
    def generate(cls) -> ActionId:
        return cls(value=f"act_{uuid4()}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EvidenceId:
    """Unique identifier for evidence."""

    value: str

    @classmethod
    def generate(cls) -> EvidenceId:
        return cls(value=f"ev_{uuid4()}")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MessageId:
    """Unique identifier for a message."""

    value: str

    @classmethod
    def generate(cls) -> MessageId:
        return cls(value=f"msg_{uuid4()}")

    def __str__(self) -> str:
        return self.value


@dataclass
class Evidence:
    """Evidence recorded during investigation.

    Evidence represents data collected during the investigation process,
    such as measurements, observations, or test results.
    """

    __slots__ = (
        "id",
        "investigation_id",
        "type",
        "description",
        "recorded_at",
        "recorded_by",
        "data",
    )

    def __init__(
        self,
        investigation_id: InvestigationId,
        evidence_type: EvidenceType,
        description: str,
        recorded_by: EngineerId,
        data: dict | None = None,
    ) -> None:
        self.id = EvidenceId.generate()
        self.investigation_id = investigation_id
        self.type = evidence_type
        self.description = description
        self.recorded_at = datetime.now(UTC)
        self.recorded_by = recorded_by
        self.data = data or {}

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "investigation_id": str(self.investigation_id),
            "type": str(self.type),
            "description": self.description,
            "recorded_at": self.recorded_at.isoformat(),
            "recorded_by": str(self.recorded_by),
            "data": self.data,
        }


@dataclass
class Action:
    """Action taken during investigation.

    Actions represent concrete steps taken by the engineer
    to diagnose or resolve the incident.
    """

    __slots__ = (
        "id",
        "investigation_id",
        "description",
        "type",
        "performed_at",
        "performed_by",
        "result",
        "notes",
    )

    def __init__(
        self,
        investigation_id: InvestigationId,
        description: str,
        action_type: ActionType,
        performed_by: EngineerId,
        result: ActionResult,
        notes: str | None = None,
    ) -> None:
        self.id = ActionId.generate()
        self.investigation_id = investigation_id
        self.description = description
        self.type = action_type
        self.performed_at = datetime.now(UTC)
        self.performed_by = performed_by
        self.result = result
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "investigation_id": str(self.investigation_id),
            "description": self.description,
            "type": str(self.type),
            "performed_at": self.performed_at.isoformat(),
            "performed_by": str(self.performed_by),
            "result": str(self.result),
            "notes": self.notes,
        }


@dataclass
class ConversationMessage:
    """Message in the incident conversation.

    Conversation messages represent the dialogue between the engineer
    and the AI system during the investigation.
    """

    __slots__ = (
        "id",
        "investigation_id",
        "sender",
        "content",
        "timestamp",
        "ai_recommendation_id",
        "feedback",
    )

    def __init__(
        self,
        investigation_id: InvestigationId,
        sender: MessageSender,
        content: str,
        ai_recommendation_id: str | None = None,
        feedback: Feedback | None = None,
    ) -> None:
        self.id = MessageId.generate()
        self.investigation_id = investigation_id
        self.sender = sender
        self.content = content
        self.timestamp = datetime.now(UTC)
        self.ai_recommendation_id = ai_recommendation_id
        self.feedback = feedback

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "investigation_id": str(self.investigation_id),
            "sender": str(self.sender),
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "ai_recommendation_id": self.ai_recommendation_id,
            "feedback_type": self.feedback.feedback_type if self.feedback else None,
            "feedback_content": self.feedback.content if self.feedback else None,
        }


@dataclass
class Investigation:
    """Investigation aggregate.

    Investigation tracks the process of diagnosing and resolving
    an engineering incident. It contains evidence, actions,
    and conversation messages.
    """

    __slots__ = (
        "id",
        "incident_id",
        "status",
        "created_at",
        "completed_at",
        "evidence_list",
        "actions_list",
        "messages_list",
    )

    def __init__(self, incident_id: InvestigationId) -> None:
        self.id = InvestigationId.generate()
        self.incident_id = incident_id
        self.status = "active"
        self.created_at = datetime.now(UTC)
        self.completed_at: datetime | None = None
        self.evidence_list: list[Evidence] = []
        self.actions_list: list[Action] = []
        self.messages_list: list[ConversationMessage] = []

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the investigation."""
        if self.completed_at:
            msg = "Cannot add evidence to completed investigation"
            raise ValueError(msg)
        self.evidence_list.append(evidence)

    def add_action(self, action: Action) -> None:
        """Add an action to the investigation."""
        if self.completed_at:
            msg = "Cannot add action to completed investigation"
            raise ValueError(msg)
        self.actions_list.append(action)

    def add_message(self, message: ConversationMessage) -> None:
        """Add a message to the conversation."""
        if self.completed_at:
            msg = "Cannot add message to completed investigation"
            raise ValueError(msg)
        self.messages_list.append(message)

    def complete(self) -> None:
        """Mark the investigation as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(UTC)

    def is_completed(self) -> bool:
        """Check if investigation is completed."""
        return self.completed_at is not None

    def get_actions_count(self) -> int:
        """Get the number of actions taken."""
        return len(self.actions_list)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "incident_id": str(self.incident_id),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "evidence": [e.to_dict() for e in self.evidence_list],
            "actions": [a.to_dict() for a in self.actions_list],
            "messages": [m.to_dict() for m in self.messages_list],
        }
