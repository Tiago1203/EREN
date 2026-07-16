"""Integration tests for Device lifecycle with real database.

Tests the full CRUD + lifecycle operations with the real SQLAlchemy repository
and PostgreSQL database.

Uses fixtures from conftest.py (db_engine, db_session).
"""

from __future__ import annotations

from datetime import UTC
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.device import DeviceService, SQLAlchemyDeviceRepository
from app.infrastructure.messaging.outbox import TransactionalOutbox

# Import models to register them with Base.metadata
from app.infrastructure.models.device import DeviceModel  # noqa: F401


# ─── Repository Tests ──────────────────────────────────────────────────────


class TestDeviceRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        device_id = str(uuid4())

        device = await repository.save(
            tenant_id="tenant-1",
            device_id=device_id,
            serial_number="SN-DB-001",
            name="Test Device",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            manufacturer_country="USA",
            building="Main",
            floor="1",
            room="101",
            department="Radiology",
            description=None,
            is_critical=False,
            calibration_last=None,
            calibration_next=None,
            calibration_interval_days=None,
            maintenance_interval_days=None,
            registered_by="engineer-1",
            status="registered",
        )
        await db_session.commit()

        saved = await repository.get_by_id(device_id, "tenant-1")
        assert saved is not None
        assert saved.serial_number == "SN-DB-001"
        assert saved.name == "Test Device"
        assert saved.status == "registered"
        assert saved.version == 1

    @pytest.mark.asyncio
    async def test_duplicate_serial_raises(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        device_id_1 = str(uuid4())
        device_id_2 = str(uuid4())

        await repository.save(
            tenant_id="tenant-1",
            device_id=device_id_1,
            serial_number="SN-UNIQUE",
            name="Device 1",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            manufacturer_country=None,
            building="Main",
            floor="1",
            room="101",
            department="Radiology",
            description=None,
            is_critical=False,
            calibration_last=None,
            calibration_next=None,
            calibration_interval_days=None,
            maintenance_interval_days=None,
            registered_by="engineer-1",
            status="registered",
        )
        await db_session.commit()

        saved = await repository.get_by_serial("SN-UNIQUE", "tenant-1")
        assert saved is not None
        assert str(saved.id) == device_id_1

    @pytest.mark.asyncio
    async def test_update_with_optimistic_locking(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        device_id = str(uuid4())

        device = await repository.save(
            tenant_id="tenant-1",
            device_id=device_id,
            serial_number="SN-LOCK-001",
            name="Lock Test",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            manufacturer_country=None,
            building="Main",
            floor="1",
            room="101",
            department="Radiology",
            description=None,
            is_critical=False,
            calibration_last=None,
            calibration_next=None,
            calibration_interval_days=None,
            maintenance_interval_days=None,
            registered_by="engineer-1",
            status="registered",
        )
        await db_session.commit()

        # Correct version
        updated = await repository.update(device, expected_version=1, name="Updated Name")
        assert updated is not None
        assert updated.version == 2

        # Wrong version - concurrent modification
        stale = await repository.get_by_id(device_id, "tenant-1")
        result = await repository.update(stale, expected_version=1, name="Stale Update")
        assert result is None

    @pytest.mark.asyncio
    async def test_tenant_isolation(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        device_id = str(uuid4())

        await repository.save(
            tenant_id="tenant-A",
            device_id=device_id,
            serial_number="SN-ISO-001",
            name="Isolated Device",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            manufacturer_country=None,
            building="Main",
            floor="1",
            room="101",
            department="Radiology",
            description=None,
            is_critical=False,
            calibration_last=None,
            calibration_next=None,
            calibration_interval_days=None,
            maintenance_interval_days=None,
            registered_by="engineer-1",
            status="registered",
        )
        await db_session.commit()

        # Same serial number for different tenant should be allowed
        other = await repository.get_by_serial("SN-ISO-001", "tenant-B")
        assert other is None  # tenant-B can't see tenant-A's device

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)

        for i in range(10):
            await repository.save(
                tenant_id="tenant-list",
                device_id=str(uuid4()),
                serial_number=f"SN-LIST-{i:03d}",
                name=f"Device {i}",
                device_type="diagnostic",
                manufacturer_name="Acme",
                manufacturer_model="X-100",
                manufacturer_country=None,
                building="Main",
                floor="1",
                room=f"10{i}",
                department="Radiology",
                description=None,
                is_critical=False,
                calibration_last=None,
                calibration_next=None,
                calibration_interval_days=None,
                maintenance_interval_days=None,
                registered_by="engineer-1",
                status="registered",
            )
        await db_session.commit()

        devices, total = await repository.list_by_tenant("tenant-list", page=1, page_size=3)
        assert len(devices) == 3
        assert total == 10

        devices_page2, _ = await repository.list_by_tenant("tenant-list", page=2, page_size=3)
        assert len(devices_page2) == 3

    @pytest.mark.asyncio
    async def test_list_with_filters(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)

        for i, (status, device_type) in enumerate([
            ("active", "diagnostic"),
            ("active", "imaging"),
            ("in_maintenance", "diagnostic"),
            ("active", "diagnostic"),
        ]):
            await repository.save(
                tenant_id="tenant-filter",
                device_id=str(uuid4()),
                serial_number=f"SN-FILT-{i:02d}",
                name=f"Filter Device {i}",
                device_type=device_type,
                manufacturer_name="Acme",
                manufacturer_model="X-100",
                manufacturer_country=None,
                building="Main",
                floor="1",
                room=f"20{i}",
                department="Radiology",
                description=None,
                is_critical=False,
                calibration_last=None,
                calibration_next=None,
                calibration_interval_days=None,
                maintenance_interval_days=None,
                registered_by="engineer-1",
                status=status,
            )
        await db_session.commit()

        active, total = await repository.list_by_tenant(
            "tenant-filter", status_filter="active"
        )
        assert all(d.status == "active" for d in active)

        critical, total2 = await repository.list_by_tenant(
            "tenant-filter", is_critical=True
        )
        assert len(critical) == 0  # None marked as critical


# ─── Service + Outbox Integration Tests ─────────────────────────────────────


class TestDeviceServiceIntegration:
    @pytest.mark.asyncio
    async def test_register_device_with_outbox_event(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        outbox = TransactionalOutbox(db_session)
        service = DeviceService(repository=repository, outbox=outbox)

        device = await service.register_device(
            tenant_id="tenant-svc-1",
            serial_number="SN-SVC-001",
            name="Service Test Device",
            device_type="imaging",
            manufacturer_name="GE",
            manufacturer_model="Revolution",
            building="Main",
            floor="2",
            room="201",
            department="Radiology",
            registered_by="engineer-1",
            correlation_id="corr-svc-1",
        )
        await db_session.commit()

        assert device is not None
        # Verify outbox has the event
        result = await db_session.execute(
            select(DeviceModel).where(DeviceModel.id == device.id)
        )
        saved = result.scalar_one_or_none()
        assert saved is not None

    @pytest.mark.asyncio
    async def test_update_device_with_version_check(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        outbox = TransactionalOutbox(db_session)
        service = DeviceService(repository=repository, outbox=outbox)

        device = await service.register_device(
            tenant_id="tenant-upd",
            serial_number="SN-UPD-001",
            name="Update Test",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            building="Main",
        )
        await db_session.commit()

        updated = await service.update_device(
            device_id=str(device.id),
            tenant_id="tenant-upd",
            expected_version=device.version,
            name="Updated Name",
        )
        await db_session.commit()

        assert updated is not None
        assert updated.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_lifecycle_full_flow(self, db_session: AsyncSession):
        """Test the full device lifecycle: register -> calibrate -> maintenance -> decommission."""
        repository = SQLAlchemyDeviceRepository(db_session)
        outbox = TransactionalOutbox(db_session)
        service = DeviceService(repository=repository, outbox=outbox)

        # 1. Register
        device = await service.register_device(
            tenant_id="tenant-lifecycle",
            serial_number="SN-LIFECYCLE-001",
            name="Lifecycle Device",
            device_type="therapeutic",
            manufacturer_name="MedTech",
            manufacturer_model="TheraPro",
            building="Main",
            floor="1",
            department="ICU",
        )
        await db_session.commit()
        v1 = device.version

        # 2. Start maintenance
        device = await service.start_maintenance(
            device_id=str(device.id),
            tenant_id="tenant-lifecycle",
            expected_version=v1,
            maintenance_type="preventive",
            technician_id="tech-1",
        )
        await db_session.commit()
        v2 = device.version

        # 3. Finish maintenance
        from datetime import datetime
        next_cal = datetime(2027, 7, 16, tzinfo=UTC)

        device = await service.finish_maintenance(
            device_id=str(device.id),
            tenant_id="tenant-lifecycle",
            expected_version=v2,
            completed_by="tech-1",
            next_calibration_date=next_cal,
        )
        await db_session.commit()
        v3 = device.version

        # Verify status is active
        assert device.status == "active"

        # 4. Take out of service
        device = await service.take_out_of_service(
            device_id=str(device.id),
            tenant_id="tenant-lifecycle",
            expected_version=v3,
            reason="Scheduled inspection",
            taken_by="manager-1",
        )
        await db_session.commit()
        v4 = device.version

        assert device.status == "out_of_service"

        # 5. Return to service
        device = await service.return_to_service(
            device_id=str(device.id),
            tenant_id="tenant-lifecycle",
            expected_version=v4,
            returned_by="manager-1",
        )
        await db_session.commit()
        v5 = device.version

        assert device.status == "active"

        # 6. Decommission
        device = await service.decommission_device(
            device_id=str(device.id),
            tenant_id="tenant-lifecycle",
            expected_version=v5,
            reason="End of useful life",
            decommissioned_by="manager-1",
        )
        await db_session.commit()

        assert device.status == "decommissioned"

    @pytest.mark.asyncio
    async def test_transfer_device(self, db_session: AsyncSession):
        repository = SQLAlchemyDeviceRepository(db_session)
        outbox = TransactionalOutbox(db_session)
        service = DeviceService(repository=repository, outbox=outbox)

        device = await service.register_device(
            tenant_id="tenant-transfer",
            serial_number="SN-TRANSFER-001",
            name="Transfer Device",
            device_type="diagnostic",
            manufacturer_name="Acme",
            manufacturer_model="X-100",
            building="Building A",
            department="Radiology",
        )
        await db_session.commit()

        device = await service.transfer_device(
            device_id=str(device.id),
            tenant_id="tenant-transfer",
            expected_version=device.version,
            new_building="Building B",
            new_floor="3",
            new_room="301",
            new_department="ICU",
            transfer_reason="Relocation",
            transferred_by="manager-1",
        )
        await db_session.commit()

        assert device.location_building == "Building B"
        assert device.location_floor == "3"
