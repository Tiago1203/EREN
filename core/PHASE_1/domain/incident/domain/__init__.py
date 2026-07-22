"""Incident domain package."""

from core.PHASE_1.infrastructure.shared import Priority, SafetyLevel

from .entities import (
    Action,
    ConversationMessage,
    EngineeringIncident,
    Evidence,
    Investigation,
)
from .repositories import IncidentRepository
from .value_objects import (
    ActionResult,
    ActionType,
    EvidenceType,
    Feedback,
    IncidentStatus,
    MessageSender,
    Resolution,
    Symptom,
)
from .work_order import (
    WorkOrder,
    WorkOrderAssigned,
    WorkOrderCancelled,
    WorkOrderCompleted,
    WorkOrderCreated,
    WorkOrderOnHold,
    WorkOrderPriority,
    WorkOrderRepository,
    WorkOrderScheduled,
    WorkOrderStarted,
    WorkOrderStatus,
    WorkOrderType,
)

__all__ = [
    # Entities
    "EngineeringIncident",
    "Investigation",
    "Evidence",
    "Action",
    "ConversationMessage",
    # Value Objects
    "IncidentStatus",
    "Symptom",
    "Resolution",
    "ActionType",
    "ActionResult",
    "Feedback",
    "MessageSender",
    "EvidenceType",
    # Shared
    "Priority",
    "SafetyLevel",
    # Repositories
    "IncidentRepository",
    # WorkOrder sub-aggregate
    "WorkOrder",
    "WorkOrderRepository",
    "WorkOrderType",
    "WorkOrderPriority",
    "WorkOrderStatus",
    # WorkOrder Events
    "WorkOrderCreated",
    "WorkOrderAssigned",
    "WorkOrderScheduled",
    "WorkOrderStarted",
    "WorkOrderOnHold",
    "WorkOrderCompleted",
    "WorkOrderCancelled",
]
