"""Tests for EPIC 3 — Capacity Context."""

from datetime import date

import pytest

from core.capacity.domain.entities.bed import Bed, BedStatus, BedType
from core.capacity.domain.entities.building import Building, BuildingStatus, BuildingType
from core.capacity.domain.entities.campus import Campus, CampusStatus
from core.capacity.domain.entities.floor import Floor, FloorStatus, FloorType
from core.capacity.domain.entities.room import Room, RoomStatus, RoomType
from core.shared.primitives import BedId, BuildingId, CampusId, FloorId, RoomId, TenantId


@pytest.fixture
def tenant_id() -> TenantId:
    return TenantId(value="tenant_test_001")


@pytest.fixture
def campus_id() -> CampusId:
    return CampusId(value="campus_001")


@pytest.fixture
def building_id() -> BuildingId:
    return BuildingId(value="building_001")


@pytest.fixture
def floor_id() -> FloorId:
    return FloorId(value="floor_001")


@pytest.fixture
def room_id() -> RoomId:
    return RoomId(value="room_001")


class TestCampus:
    def test_create_campus(self, tenant_id: TenantId, campus_id: CampusId) -> None:
        campus = Campus.create(
            tenant_id=tenant_id,
            organization_id=TenantId(value="org_001"),
            campus_code="NYC-01",
            campus_name="New York City Campus",
            address="123 Medical Center Dr",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            timezone="America/New_York",
        )
        assert campus.campus_code == "NYC-01"
        assert campus.campus_name == "New York City Campus"
        assert campus.status == CampusStatus.ACTIVE

    def test_campus_activation_lifecycle(self, tenant_id: TenantId, campus_id: CampusId) -> None:
        campus = Campus.create(
            tenant_id=tenant_id,
            organization_id=TenantId(value="org_001"),
            campus_code="NYC-01",
            campus_name="NYC Campus",
            address="123 Main St",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001",
            timezone="America/New_York",
        )
        campus.deactivate()
        assert campus.status == CampusStatus.INACTIVE
        campus.activate()
        assert campus.status == CampusStatus.ACTIVE


class TestBuilding:
    def test_create_building(self, tenant_id: TenantId, campus_id: CampusId) -> None:
        building = Building.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_code="B-A",
            building_name="Building A",
            building_type=BuildingType.MAIN,
        )
        assert building.building_code == "B-A"
        assert building.status == BuildingStatus.OPERATIONAL


class TestFloor:
    def test_create_floor(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId) -> None:
        floor = Floor.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_number=1,
            floor_type=FloorType.STANDARD,
        )
        assert floor.floor_number == 1
        assert floor.status == FloorStatus.OPERATIONAL

    def test_floor_number_validation(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            Floor.create(
                tenant_id=tenant_id,
                campus_id=campus_id,
                building_id=building_id,
                floor_number=-1,
            )


class TestRoom:
    def test_create_room(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId) -> None:
        room = Room.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_number="101",
            room_type=RoomType.PATIENT,
            bed_count=2,
        )
        assert room.room_number == "101"
        assert room.bed_count == 2


class TestBed:
    def test_create_bed(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-A",
            bed_type=BedType.STANDARD,
        )
        assert bed.bed_number == "101-A"
        assert bed.status == BedStatus.AVAILABLE
        assert bed.is_available()

    def test_isolation_bed_requires_negative_pressure(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        with pytest.raises(ValueError, match="negative_pressure"):
            Bed.create(
                tenant_id=tenant_id,
                campus_id=campus_id,
                building_id=building_id,
                floor_id=floor_id,
                room_id=room_id,
                bed_number="ISO-01",
                bed_type=BedType.ISOLATION,
                negative_pressure=False,  # Invalid
            )

    def test_bed_occupy_vacate_lifecycle(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-A",
            bed_type=BedType.ICU,
        )

        # Occupy bed
        bed.occupy("patient_001")
        assert bed.status == BedStatus.OCCUPIED
        assert bed.patient_id == "patient_001"
        assert not bed.is_available()

        # Vacate bed
        bed.vacate()
        assert bed.status == BedStatus.AVAILABLE
        assert bed.patient_id is None
        assert bed.is_available()

    def test_bed_cannot_occupy_twice(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-B",
        )
        bed.occupy("patient_001")
        with pytest.raises(ValueError, match="Cannot occupy"):
            bed.occupy("patient_002")

    def test_bed_block_unblock(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-C",
        )
        bed.block()
        assert bed.status == BedStatus.BLOCKED

        bed.unblock()
        assert bed.status == BedStatus.AVAILABLE

    def test_bed_cannot_block_occupied(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-D",
        )
        bed.occupy("patient_001")
        with pytest.raises(ValueError, match="Cannot block"):
            bed.block()

    def test_bed_maintenance_workflow(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-E",
        )
        bed.start_maintenance()
        assert bed.status == BedStatus.MAINTENANCE

    def test_bed_close_workflow(self, tenant_id: TenantId, campus_id: CampusId, building_id: BuildingId, floor_id: FloorId, room_id: RoomId) -> None:
        bed = Bed.create(
            tenant_id=tenant_id,
            campus_id=campus_id,
            building_id=building_id,
            floor_id=floor_id,
            room_id=room_id,
            bed_number="101-F",
        )
        bed.close()
        assert bed.status == BedStatus.CLOSED
        # Closed bed cannot be blocked
        with pytest.raises(ValueError, match="Cannot block"):
            bed.block()
