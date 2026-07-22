"""Tests for EPIC 3 — Staffing Context."""

from datetime import UTC, datetime

import pytest

from core.PHASE_1.domain.staffing.domain.entities.role import Role, RoleType
from core.PHASE_1.domain.staffing.domain.entities.shift import Shift, ShiftStatus, ShiftType
from core.PHASE_1.domain.staffing.domain.entities.staff import EmploymentStatus, Staff, StaffType
from core.PHASE_1.domain.staffing.domain.entities.team import Team, TeamType


@pytest.fixture
def tenant_id() -> str:
    return "tenant_test_001"


class TestStaff:
    def test_create_staff(self, tenant_id: str) -> None:
        staff = Staff.create(
            tenant_id=tenant_id,
            employee_id="EMP-001",
            first_name="John",
            last_name="Doe",
            email="john.doe@hospital.com",
            staff_type=StaffType.NURSE,
        )
        assert staff.full_name == "John Doe"
        assert staff.employment_status == EmploymentStatus.ACTIVE
        assert staff.is_active()

    def test_staff_assign_to_team(self, tenant_id: str) -> None:
        staff = Staff.create(
            tenant_id=tenant_id,
            employee_id="EMP-002",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@hospital.com",
            staff_type=StaffType.ENGINEER,
        )
        team_id = "team_biomedical_01"
        staff.assign_to_team(team_id)
        assert team_id in staff.team_ids

    def test_staff_termination(self, tenant_id: str) -> None:
        staff = Staff.create(
            tenant_id=tenant_id,
            employee_id="EMP-003",
            first_name="Bob",
            last_name="Wilson",
            email="bob.wilson@hospital.com",
            staff_type=StaffType.TECHNICIAN,
        )
        staff.terminate()
        assert staff.employment_status == EmploymentStatus.TERMINATED
        assert not staff.is_active()

    def test_staff_cannot_terminate_twice(self, tenant_id: str) -> None:
        staff = Staff.create(
            tenant_id=tenant_id,
            employee_id="EMP-004",
            first_name="Alice",
            last_name="Brown",
            email="alice.brown@hospital.com",
            staff_type=StaffType.ADMIN,
        )
        staff.terminate()
        with pytest.raises(ValueError, match="already terminated"):
            staff.terminate()


class TestShift:
    def test_create_shift(self, tenant_id: str) -> None:
        staff_id = "staff_001"
        start = datetime.now(UTC)
        end = datetime(2026, 7, 20, 22, 0, tzinfo=UTC)

        shift = Shift.create(
            tenant_id=tenant_id,
            staff_id=staff_id,
            shift_type=ShiftType.NIGHT,
            start_time=start,
            end_time=end,
        )
        assert shift.shift_type == ShiftType.NIGHT
        assert shift.status == ShiftStatus.SCHEDULED

    def test_shift_time_validation(self, tenant_id: str) -> None:
        start = datetime(2026, 7, 20, 22, 0, tzinfo=UTC)
        end = datetime(2026, 7, 20, 14, 0, tzinfo=UTC)  # End before start

        with pytest.raises(ValueError, match="end_time must be after start_time"):
            Shift.create(
                tenant_id=tenant_id,
                staff_id="staff_001",
                shift_type=ShiftType.NIGHT,
                start_time=start,
                end_time=end,
            )

    def test_shift_lifecycle(self, tenant_id: str) -> None:
        staff_id = "staff_002"
        shift = Shift.create(
            tenant_id=tenant_id,
            staff_id=staff_id,
            shift_type=ShiftType.DAY,
            start_time=datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
            end_time=datetime(2026, 7, 20, 16, 0, tzinfo=UTC),
        )
        shift.start()
        assert shift.status == ShiftStatus.IN_PROGRESS

        shift.complete()
        assert shift.status == ShiftStatus.COMPLETED

    def test_shift_cannot_start_twice(self, tenant_id: str) -> None:
        shift = Shift.create(
            tenant_id=tenant_id,
            staff_id="staff_003",
            shift_type=ShiftType.EVENING,
            start_time=datetime(2026, 7, 20, 14, 0, tzinfo=UTC),
            end_time=datetime(2026, 7, 20, 22, 0, tzinfo=UTC),
        )
        shift.start()
        with pytest.raises(ValueError, match="Cannot start"):
            shift.start()


class TestRole:
    def test_create_role(self, tenant_id: str) -> None:
        role = Role.create(
            tenant_id=tenant_id,
            role_name="ICU Nurse",
            role_type=RoleType.CLINICAL,
        )
        assert role.role_name == "ICU Nurse"
        assert role.role_type == RoleType.CLINICAL


class TestTeam:
    def test_create_team(self, tenant_id: str) -> None:
        team = Team.create(
            tenant_id=tenant_id,
            team_name="Biomedical Engineering",
            team_type=TeamType.BIOMEDICAL,
        )
        assert team.team_name == "Biomedical Engineering"
        assert team.team_type == TeamType.BIOMEDICAL
