"""WorkOrder-specific value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.shared import ValueObject

if TYPE_CHECKING:
    pass


# SLA deadlines in hours by priority
_SLA_HOURS = {
    "low": 720,       # 30 days
    "medium": 168,    # 7 days
    "high": 72,       # 3 days
    "urgent": 24,     # 1 day
    "emergency": 4,   # 4 hours
}


@dataclass(frozen=True)
class WorkOrderType(ValueObject):
    """Type of work order."""

    value: str  # corrective | preventive | inspection | calibration

    def __post_init__(self) -> None:
        valid = {"corrective", "preventive", "inspection", "calibration"}
        if self.value.lower() not in valid:
            msg = f"Invalid work order type: {self.value}. Must be one of {valid}"
            raise ValueError(msg)

    @classmethod
    def corrective(cls) -> WorkOrderType:
        return cls(value="corrective")

    @classmethod
    def preventive(cls) -> WorkOrderType:
        return cls(value="preventive")

    @classmethod
    def inspection(cls) -> WorkOrderType:
        return cls(value="inspection")

    @classmethod
    def calibration(cls) -> WorkOrderType:
        return cls(value="calibration")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class WorkOrderPriority(ValueObject):
    """Priority level for work order."""

    value: str  # low | medium | high | urgent | emergency

    def __post_init__(self) -> None:
        valid = {"low", "medium", "high", "urgent", "emergency"}
        if self.value.lower() not in valid:
            msg = f"Invalid priority: {self.value}. Must be one of {valid}"
            raise ValueError(msg)

    @classmethod
    def low(cls) -> WorkOrderPriority:
        return cls(value="low")

    @classmethod
    def medium(cls) -> WorkOrderPriority:
        return cls(value="medium")

    @classmethod
    def high(cls) -> WorkOrderPriority:
        return cls(value="high")

    @classmethod
    def urgent(cls) -> WorkOrderPriority:
        return cls(value="urgent")

    @classmethod
    def emergency(cls) -> WorkOrderPriority:
        return cls(value="emergency")

    def sla_deadline_hours(self) -> int:
        """Return SLA deadline in hours for this priority."""
        return _SLA_HOURS.get(self.value, 168)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class WorkOrderStatus(ValueObject):
    """Status of a work order.

    Lifecycle:
    draft → scheduled → in_progress → completed
                ↘ cancelled ←── in_progress / scheduled / on_hold
                    ↘ on_hold ←── in_progress
                        ↘ pending_parts ←── in_progress
    """

    value: str

    VALID = {
        "draft",
        "scheduled",
        "in_progress",
        "pending_parts",
        "on_hold",
        "completed",
        "cancelled",
    }

    # Class-level constants (not dataclass fields)
    _ALLOWED_TRANSITIONS: classmethod = classmethod(
        lambda cls: {
            "draft": {"scheduled", "cancelled"},
            "scheduled": {"in_progress", "cancelled", "on_hold"},
            "in_progress": {"pending_parts", "completed", "cancelled", "on_hold"},
            "pending_parts": {"in_progress", "cancelled", "on_hold"},
            "on_hold": {"scheduled", "in_progress", "cancelled"},
            "completed": set(),
            "cancelled": set(),
        }
    )

    def __post_init__(self) -> None:
        if self.value.lower() not in self.VALID:
            msg = f"Invalid work order status: {self.value}. Must be one of {self.VALID}"
            raise ValueError(msg)

    @classmethod
    def draft(cls) -> WorkOrderStatus:
        return cls(value="draft")

    @classmethod
    def scheduled(cls) -> WorkOrderStatus:
        return cls(value="scheduled")

    @classmethod
    def in_progress(cls) -> WorkOrderStatus:
        return cls(value="in_progress")

    @classmethod
    def pending_parts(cls) -> WorkOrderStatus:
        return cls(value="pending_parts")

    @classmethod
    def on_hold(cls) -> WorkOrderStatus:
        return cls(value="on_hold")

    @classmethod
    def completed(cls) -> WorkOrderStatus:
        return cls(value="completed")

    @classmethod
    def cancelled(cls) -> WorkOrderStatus:
        return cls(value="cancelled")

    def _allowed_transitions(self) -> dict[str, set[str]]:
        return {
            "draft": {"scheduled", "cancelled"},
            "scheduled": {"in_progress", "cancelled", "on_hold"},
            "in_progress": {"pending_parts", "completed", "cancelled", "on_hold"},
            "pending_parts": {"in_progress", "cancelled", "on_hold"},
            "on_hold": {"scheduled", "in_progress", "cancelled"},
            "completed": set(),
            "cancelled": set(),
        }

    def can_transition_to(self, target: WorkOrderStatus) -> bool:
        """Check if transition to target status is allowed."""
        return target.value in self._allowed_transitions().get(self.value, set())

    def is_terminal(self) -> bool:
        """Terminal states cannot transition further."""
        return self.value in {"completed", "cancelled"}

    def __str__(self) -> str:
        return self.value
