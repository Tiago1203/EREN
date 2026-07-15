"""Unit tests for PatientService.

Tests business logic in isolation (no DB, no external dependencies).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestPatientService:
    """Test PatientService business logic."""

    @pytest.fixture
    def mock_repository(self):
        """Mock PatientRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_event_bus(self):
        """Mock EventBus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository, mock_event_bus):
        """Create service with mocks."""
        from app.domain.patient import PatientService
        return PatientService(repository=mock_repository, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_create_patient_returns_patient(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that create_patient returns a patient."""
        # Arrange
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        # Act
        result = await service.create_patient(
            tenant_id="tenant-1",
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
        )

        # Assert
        assert result is not None
        assert hasattr(result, 'id')

    @pytest.mark.asyncio
    async def test_create_patient_calls_repository(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that create_patient calls repository.save()."""
        # Arrange
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        # Act
        await service.create_patient(
            tenant_id="tenant-1",
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
        )

        # Assert
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_patient_calls_event_bus(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that create_patient publishes an event."""
        # Arrange
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        # Act
        await service.create_patient(
            tenant_id="tenant-1",
            mrn="MRN001",
            given_name="John",
            family_name="Doe",
        )

        # Assert
        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        assert call_args.kwargs["event_type"] == "PatientCreated"
        assert call_args.kwargs["aggregate_type"] == "Patient"

    @pytest.mark.asyncio
    async def test_get_patient_returns_patient(
        self, service, mock_repository
    ):
        """Test that get_patient returns the patient."""
        # Arrange
        expected_patient = MagicMock(id="patient-1")
        mock_repository.get_by_id = AsyncMock(return_value=expected_patient)

        # Act
        result = await service.get_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
        )

        # Assert
        assert result == expected_patient

    @pytest.mark.asyncio
    async def test_get_patient_returns_none_when_not_found(
        self, service, mock_repository
    ):
        """Test that get_patient returns None when patient doesn't exist."""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)

        # Act
        result = await service.get_patient(
            patient_id="non-existent",
            tenant_id="tenant-1",
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_patient_returns_true_on_success(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that delete_patient returns True on success."""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=MagicMock(id="patient-1"))
        mock_repository.soft_delete = AsyncMock(return_value=True)

        # Act
        result = await service.delete_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
        )

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_patient_returns_false_when_not_found(
        self, service, mock_repository
    ):
        """Test that delete_patient returns False when patient doesn't exist."""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=None)

        # Act
        result = await service.delete_patient(
            patient_id="non-existent",
            tenant_id="tenant-1",
        )

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_patient_publishes_event(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that delete_patient publishes PatientDeleted event."""
        # Arrange
        mock_repository.get_by_id = AsyncMock(return_value=MagicMock(id="patient-1"))
        mock_repository.soft_delete = AsyncMock(return_value=True)

        # Act
        await service.delete_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
        )

        # Assert
        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        assert call_args.kwargs["event_type"] == "PatientDeleted"

    @pytest.mark.asyncio
    async def test_list_patients_returns_tuple(
        self, service, mock_repository
    ):
        """Test that list_patients returns (patients, total)."""
        # Arrange
        mock_patients = [MagicMock(id="p1"), MagicMock(id="p2")]
        mock_repository.list_by_tenant = AsyncMock(return_value=(mock_patients, 2))

        # Act
        result = await service.list_patients(
            tenant_id="tenant-1",
            page=1,
            page_size=50,
        )

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == mock_patients
        assert result[1] == 2
