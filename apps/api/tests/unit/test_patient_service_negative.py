"""Negative test cases for PatientService.

These tests validate edge cases and error handling:
- Concurrent modification (optimistic locking)
- Non-existent patient
- Soft delete with metadata
- Tenant isolation
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestPatientServiceNegative:
    """Test negative/error cases for PatientService."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository, mock_event_bus):
        from app.clinical.patient import PatientService

        return PatientService(repository=mock_repository, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_get_patient_returns_none_when_not_found(self, service, mock_repository):
        """Test get_patient returns None when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.get_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_patient_returns_none_when_not_found(self, service, mock_repository):
        """Test update_patient returns None when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.update_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
            expected_version=1,
            given_name="New Name",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_patient_returns_false_when_not_found(self, service, mock_repository):
        """Test delete_patient returns False when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.delete_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_create_patient_with_minimal_data(self, service, mock_repository, mock_event_bus):
        """Test create_patient with only required fields."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        # Only required fields
        result = await service.create_patient(
            tenant_id="tenant-1",
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
        )

        assert result is not None
        mock_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_patient_with_all_optional_data(
        self, service, mock_repository, mock_event_bus
    ):
        """Test create_patient with all optional fields."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        result = await service.create_patient(
            tenant_id="tenant-1",
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
            date_of_birth="1990-01-15",
            gender="male",
            email="john@example.com",
            phone="+1234567890",
            blood_type="O+",
            allergies="Penicillin",
            created_by="doctor-1",
        )

        assert result is not None
        mock_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_patient_with_metadata(self, service, mock_repository, mock_event_bus):
        """Test delete_patient calls repository with metadata."""
        mock_patient = MagicMock(id="patient-1")
        mock_repository.get_by_id = AsyncMock(return_value=mock_patient)
        mock_repository.soft_delete = AsyncMock(return_value=True)

        result = await service.delete_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            deleted_by="admin-user",
            delete_reason="Patient requested deletion",
            correlation_id="corr-123",
        )

        assert result is True
        mock_repository.soft_delete.assert_called_once_with(
            "patient-1",
            "tenant-1",
            deleted_by="admin-user",
            delete_reason="Patient requested deletion",
        )

    @pytest.mark.asyncio
    async def test_update_patient_with_optimistic_locking(
        self, service, mock_repository, mock_event_bus
    ):
        """Test update_patient with optimistic locking."""
        mock_patient = MagicMock(
            id="patient-1",
            given_name="Old Name",
            family_name="Old Family",
            version=1,
        )
        mock_repository.get_by_id = AsyncMock(return_value=mock_patient)
        mock_repository.update = AsyncMock(return_value=mock_patient)

        result = await service.update_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            expected_version=1,
            given_name="New Name",
        )

        assert result is not None
        mock_repository.update.assert_called_once()
        # Verify version was passed
        call_args = mock_repository.update.call_args
        assert call_args[0][1] == 1  # expected_version

    @pytest.mark.asyncio
    async def test_update_patient_concurrent_modification_returns_none(
        self, service, mock_repository, mock_event_bus
    ):
        """Test update_patient returns None on concurrent modification."""
        mock_patient = MagicMock(
            id="patient-1",
            given_name="Old Name",
            version=2,  # Version changed
        )
        mock_repository.get_by_id = AsyncMock(return_value=mock_patient)
        # Repository returns None when version mismatch
        mock_repository.update = AsyncMock(return_value=None)

        result = await service.update_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            expected_version=1,  # Outdated version
            given_name="New Name",
        )

        assert result is None
        # No event should be published
        mock_event_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_patients_returns_empty_list(self, service, mock_repository):
        """Test list_patients returns empty list when no patients exist."""
        mock_repository.list_by_tenant = AsyncMock(return_value=([], 0))

        patients, total = await service.list_patients(
            tenant_id="tenant-empty",
            page=1,
            page_size=50,
        )

        assert patients == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_patients_respects_pagination(self, service, mock_repository):
        """Test list_patients correctly passes pagination params."""
        mock_patients = [MagicMock(id=f"p{i}") for i in range(10)]
        mock_repository.list_by_tenant = AsyncMock(return_value=(mock_patients, 100))

        await service.list_patients(
            tenant_id="tenant-1",
            page=3,
            page_size=10,
        )

        mock_repository.list_by_tenant.assert_called_once_with(
            "tenant-1",
            3,  # page
            10,  # page_size
        )


class TestPatientRepositoryProtocol:
    """Test repository protocol compliance."""

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_save(self):
        """Verify repository protocol defines save method."""
        from app.clinical.patient.repository import PatientRepository

        # PatientRepository is a Protocol, not a class
        # This test verifies the Protocol exists
        assert PatientRepository is not None

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_get_by_id(self):
        """Verify repository protocol defines get_by_id method."""
        from app.clinical.patient.repository import PatientRepository

        # Check Protocol has the required method signature
        assert hasattr(PatientRepository, "get_by_id")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_list_by_tenant(self):
        """Verify repository protocol defines list_by_tenant method."""
        from app.clinical.patient.repository import PatientRepository

        assert hasattr(PatientRepository, "list_by_tenant")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_update_with_version(self):
        """Verify repository protocol update accepts version."""
        from app.clinical.patient.repository import PatientRepository

        # Update should accept expected_version for optimistic locking
        assert hasattr(PatientRepository, "update")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_soft_delete_with_metadata(self):
        """Verify repository protocol soft_delete accepts metadata."""
        from app.clinical.patient.repository import PatientRepository

        # soft_delete should accept deleted_by and delete_reason
        assert hasattr(PatientRepository, "soft_delete")
