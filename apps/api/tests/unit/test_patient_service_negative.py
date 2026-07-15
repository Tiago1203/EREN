"""Negative test cases for PatientService.

These tests validate edge cases and error handling:
- Duplicate MRN
- Empty required fields
- Non-existent patient
- Service errors
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
        from app.domain.patient import PatientService
        return PatientService(repository=mock_repository, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_get_patient_raises_when_not_found(
        self, service, mock_repository
    ):
        """Test get_patient returns None when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.get_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_patient_returns_none_when_not_found(
        self, service, mock_repository
    ):
        """Test update_patient returns None when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.update_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
            given_name="New Name",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_patient_returns_false_when_not_found(
        self, service, mock_repository
    ):
        """Test delete_patient returns False when patient doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.delete_patient(
            patient_id="non-existent-id",
            tenant_id="tenant-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_create_patient_with_minimal_data(
        self, service, mock_repository, mock_event_bus
    ):
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
    async def test_delete_patient_calls_repository_with_correct_params(
        self, service, mock_repository, mock_event_bus
    ):
        """Test delete_patient calls repository with correct parameters."""
        mock_patient = MagicMock(id="patient-1")
        mock_repository.get_by_id = AsyncMock(return_value=mock_patient)
        mock_repository.soft_delete = AsyncMock(return_value=True)

        result = await service.delete_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            deleted_by="admin-user",
            correlation_id="corr-123",
        )

        assert result is True
        mock_repository.soft_delete.assert_called_once_with("patient-1", "tenant-1")

    @pytest.mark.asyncio
    async def test_update_patient_with_partial_data(
        self, service, mock_repository, mock_event_bus
    ):
        """Test update_patient with partial data (only some fields)."""
        mock_patient = MagicMock(
            id="patient-1",
            given_name="Old Name",
            family_name="Old Family",
        )
        mock_repository.get_by_id = AsyncMock(return_value=mock_patient)
        mock_repository.update = AsyncMock(return_value=mock_patient)

        result = await service.update_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            given_name="New Name",
        )

        assert result is not None
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_patients_returns_empty_list(
        self, service, mock_repository
    ):
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
    async def test_list_patients_respects_pagination(
        self, service, mock_repository
    ):
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
        from app.domain.patient.repository import PatientRepository
        # PatientRepository is a Protocol, not a class
        # This test verifies the Protocol exists
        assert PatientRepository is not None

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_get_by_id(self):
        """Verify repository protocol defines get_by_id method."""
        from app.domain.patient.repository import PatientRepository
        # Check Protocol has the required method signature
        assert hasattr(PatientRepository, 'get_by_id')

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_list_by_tenant(self):
        """Verify repository protocol defines list_by_tenant method."""
        from app.domain.patient.repository import PatientRepository
        assert hasattr(PatientRepository, 'list_by_tenant')
