"""EREN Engineering Incident Context.

This package contains the Engineering Incident bounded context,
which is the heart of the EREN Clinical Engineering Copilot.

Architecture:
- domain/entities: EngineeringIncident aggregate, Investigation sub-aggregate
- domain/value_objects: IncidentStatus, Symptom, Resolution, etc.
- domain/repositories: Repository interfaces
- domain/work_order: WorkOrder sub-aggregate
- application: Commands, queries, and handlers
- infrastructure: Repository implementations, messaging
"""

from .domain import (
    Action,
    ActionResult,
    ActionType,
    ConversationMessage,
    EngineeringIncident,
    Evidence,
    IncidentRepository,
    IncidentStatus,
    Investigation,
    MessageSender,
    Priority,
    Resolution,
    SafetyLevel,
    Symptom,
    # WorkOrder sub-aggregate
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
    "Priority",
    "SafetyLevel",
    "ActionType",
    "ActionResult",
    "MessageSender",
    # Repositories
    "IncidentRepository",
    # WorkOrder sub-aggregate
    "WorkOrder",
    "WorkOrderRepository",
    "WorkOrderType",
    "WorkOrderPriority",
    "WorkOrderStatus",
    "WorkOrderCreated",
    "WorkOrderAssigned",
    "WorkOrderScheduled",
    "WorkOrderStarted",
    "WorkOrderOnHold",
    "WorkOrderCompleted",
    "WorkOrderCancelled",
]
