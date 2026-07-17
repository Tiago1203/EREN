"""WorkOrder sub-aggregate — part of Incident bounded context.

Note: WorkOrder is a sub-aggregate of the Incident bounded context.
It lives here (core/incident/domain/work_order/) but is referenced
by the Incident aggregate root.

Architecture:
- Pending ADR-0204: WorkOrder must be implemented in core/
- Current state: orchestration exists in apps/api/app/domain/work_order/
- Target: refactor apps/api/app/domain/work_order/service.py to call core/incident/domain/work_order/
"""

from .work_order import (
    WorkOrder,
    WorkOrderAssigned,
    WorkOrderCancelled,
    WorkOrderCompleted,
    WorkOrderCreated,
    WorkOrderOnHold,
    WorkOrderScheduled,
    WorkOrderStarted,
)
from .repository import WorkOrderRepository
from .value_objects import (
    WorkOrderPriority,
    WorkOrderStatus,
    WorkOrderType,
)

__all__ = [
    # Aggregate
    "WorkOrder",
    # Value Objects
    "WorkOrderType",
    "WorkOrderPriority",
    "WorkOrderStatus",
    # Repository
    "WorkOrderRepository",
    # Events
    "WorkOrderCreated",
    "WorkOrderAssigned",
    "WorkOrderScheduled",
    "WorkOrderStarted",
    "WorkOrderOnHold",
    "WorkOrderCompleted",
    "WorkOrderCancelled",
]
