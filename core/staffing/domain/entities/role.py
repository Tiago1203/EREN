"""Role entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from core.shared import AggregateRoot, RoleId, TenantId

if TYPE_CHECKING:
    pass


class RoleType(str, Enum):
    CLINICAL = "clinical"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"


@dataclass(eq=False)
class Role(AggregateRoot):
    """Role entity.

    A role defines a job function (e.g., "ICU Nurse", "Biomedical Engineer").
    Roles are assigned to staff members.
    """

    tenant_id: TenantId
    role_id: RoleId
    role_name: str
    role_type: RoleType

    @classmethod
    def create(
        cls,
        tenant_id: TenantId,
        role_name: str,
        role_type: RoleType,
    ) -> Role:
        role_id = RoleId.generate()
        role = cls(
            id=role_id,
            tenant_id=tenant_id,
            role_id=role_id,
            role_name=role_name,
            role_type=role_type,
        )
        role._mark_created()
        return role
