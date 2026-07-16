"""Unit tests for DiagnosisService.

Tests business logic in isolation (no DB, no external dependencies).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestDiagnosisService:
    """Test DiagnosisService business logic."""

    @pytest.fixture
    def mock_repository(self):
        """Mock DiagnosisRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_event_bus(self):
        """Mock EventBus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository, mock_event_bus):
        """Create service with mocks."""
        from app.domain.diagnosis import DiagnosisService

        return DiagnosisService(repository=mock_repository, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_record_diagnosis_returns_diagnosis(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that record_diagnosis returns a diagnosis."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        result = await service.record_diagnosis(
            tenant_id="tenant-1",
            patient_id="patient-1",
            diagnosis_code="E11.9",
            diagnosis_name="Type 2 diabetes mellitus",
        )

        assert result is not None
        assert hasattr(result, "id")

    @pytest.mark.asyncio
    async def test_record_diagnosis_calls_repository(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that record_diagnosis calls repository.save()."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        await service.record_diagnosis(
            tenant_id="tenant-1",
            patient_id="patient-1",
            diagnosis_code="E11.9",
            diagnosis_name="Type 2 diabetes mellitus",
        )

        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_diagnosis_calls_event_bus(self, service, mock_repository, mock_event_bus):
        """Test that record_diagnosis publishes an event."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        await service.record_diagnosis(
            tenant_id="tenant-1",
            patient_id="patient-1",
            diagnosis_code="E11.9",
            diagnosis_name="Type 2 diabetes mellitus",
        )

        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        assert call_args.kwargs["event_type"] == "DiagnosisRecorded"
        assert call_args.kwargs["aggregate_type"] == "Diagnosis"

    @pytest.mark.asyncio
    async def test_get_diagnosis_returns_diagnosis(self, service, mock_repository):
        """Test that get_diagnosis returns the diagnosis."""
        expected_diagnosis = MagicMock(id="diagnosis-1")
        mock_repository.get_by_id = AsyncMock(return_value=expected_diagnosis)

        result = await service.get_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
        )

        assert result == expected_diagnosis

    @pytest.mark.asyncio
    async def test_get_diagnosis_returns_none_when_not_found(self, service, mock_repository):
        """Test that get_diagnosis returns None when diagnosis doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.get_diagnosis(
            diagnosis_id="non-existent",
            tenant_id="tenant-1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_diagnosis_returns_true_on_success(
        self, service, mock_repository, mock_event_bus
    ):
        """Test that delete_diagnosis returns True on success."""
        mock_repository.get_by_id = AsyncMock(
            return_value=MagicMock(id="diagnosis-1", patient_id="patient-1")
        )
        mock_repository.soft_delete = AsyncMock(return_value=True)

        result = await service.delete_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_diagnosis_returns_false_when_not_found(self, service, mock_repository):
        """Test that delete_diagnosis returns False when diagnosis doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.delete_diagnosis(
            diagnosis_id="non-existent",
            tenant_id="tenant-1",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_diagnosis_publishes_event(self, service, mock_repository, mock_event_bus):
        """Test that delete_diagnosis publishes DiagnosisDeleted event."""
        mock_repository.get_by_id = AsyncMock(
            return_value=MagicMock(id="diagnosis-1", patient_id="patient-1")
        )
        mock_repository.soft_delete = AsyncMock(return_value=True)

        await service.delete_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
        )

        mock_event_bus.publish.assert_called_once()
        call_args = mock_event_bus.publish.call_args
        assert call_args.kwargs["event_type"] == "DiagnosisDeleted"

    @pytest.mark.asyncio
    async def test_list_diagnoses_by_patient_returns_tuple(self, service, mock_repository):
        """Test that list_diagnoses_by_patient returns (diagnoses, total)."""
        mock_diagnoses = [MagicMock(id="d1"), MagicMock(id="d2")]
        mock_repository.list_by_patient = AsyncMock(return_value=(mock_diagnoses, 2))

        result = await service.list_diagnoses_by_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            page=1,
            page_size=50,
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == mock_diagnoses
        assert result[1] == 2

    @pytest.mark.asyncio
    async def test_list_diagnoses_by_tenant_returns_tuple(self, service, mock_repository):
        """Test that list_diagnoses_by_tenant returns (diagnoses, total)."""
        mock_diagnoses = [MagicMock(id="d1"), MagicMock(id="d2")]
        mock_repository.list_by_tenant = AsyncMock(return_value=(mock_diagnoses, 2))

        result = await service.list_diagnoses_by_tenant(
            tenant_id="tenant-1",
            page=1,
            page_size=50,
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == mock_diagnoses
        assert result[1] == 2
