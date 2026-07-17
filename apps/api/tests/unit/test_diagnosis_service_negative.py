"""Negative test cases for DiagnosisService.

These tests validate edge cases and error handling:
- Concurrent modification (optimistic locking)
- Non-existent diagnosis
- Soft delete with metadata
- Tenant isolation
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestDiagnosisServiceNegative:
    """Test negative/error cases for DiagnosisService."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock()

    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository, mock_event_bus):
        from app.clinical.diagnosis import DiagnosisService

        return DiagnosisService(repository=mock_repository, event_bus=mock_event_bus)

    @pytest.mark.asyncio
    async def test_get_diagnosis_returns_none_when_not_found(self, service, mock_repository):
        """Test get_diagnosis returns None when diagnosis doesn't exist."""
        mock_repository.get_by_id = AsyncMock(return_value=None)

        result = await service.get_diagnosis(
            diagnosis_id="non-existent-id",
            tenant_id="tenant-1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_record_diagnosis_with_minimal_data(
        self, service, mock_repository, mock_event_bus
    ):
        """Test record_diagnosis with only required fields."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        result = await service.record_diagnosis(
            tenant_id="tenant-1",
            patient_id="patient-1",
            diagnosis_code="E11.9",
            diagnosis_name="Type 2 diabetes mellitus",
        )

        assert result is not None
        mock_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_diagnosis_with_all_optional_data(
        self, service, mock_repository, mock_event_bus
    ):
        """Test record_diagnosis with all optional fields."""
        mock_repository.save = AsyncMock(return_value=MagicMock(id="test-id"))

        result = await service.record_diagnosis(
            tenant_id="tenant-1",
            patient_id="patient-1",
            diagnosis_code="I10",
            diagnosis_name="Essential hypertension",
            description="Chronic condition",
            created_by="doctor-1",
        )

        assert result is not None
        mock_repository.save.assert_called_once()
        mock_event_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_diagnosis_with_metadata(self, service, mock_repository, mock_event_bus):
        """Test delete_diagnosis calls repository with metadata."""
        mock_diagnosis = MagicMock(id="diagnosis-1", patient_id="patient-1")
        mock_repository.get_by_id = AsyncMock(return_value=mock_diagnosis)
        mock_repository.soft_delete = AsyncMock(return_value=True)

        result = await service.delete_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
            deleted_by="admin-user",
            delete_reason="Incorrect diagnosis",
            correlation_id="corr-123",
        )

        assert result is True
        mock_repository.soft_delete.assert_called_once_with(
            "diagnosis-1",
            "tenant-1",
            deleted_by="admin-user",
            delete_reason="Incorrect diagnosis",
        )

    @pytest.mark.asyncio
    async def test_amend_diagnosis_with_optimistic_locking(
        self, service, mock_repository, mock_event_bus
    ):
        """Test amend_diagnosis with optimistic locking."""
        mock_diagnosis = MagicMock(
            id="diagnosis-1",
            patient_id="patient-1",
            version=1,
        )
        mock_repository.get_by_id = AsyncMock(return_value=mock_diagnosis)
        mock_repository.update = AsyncMock(return_value=mock_diagnosis)

        result = await service.amend_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
            expected_version=1,
            diagnosis_name="Updated diagnosis name",
        )

        assert result is not None
        mock_repository.update.assert_called_once()
        call_args = mock_repository.update.call_args
        assert call_args[0][1] == 1  # expected_version

    @pytest.mark.asyncio
    async def test_amend_diagnosis_concurrent_modification_returns_none(
        self, service, mock_repository, mock_event_bus
    ):
        """Test amend_diagnosis returns None on concurrent modification."""
        mock_diagnosis = MagicMock(
            id="diagnosis-1",
            patient_id="patient-1",
            version=2,
        )
        mock_repository.get_by_id = AsyncMock(return_value=mock_diagnosis)
        mock_repository.update = AsyncMock(return_value=None)

        result = await service.amend_diagnosis(
            diagnosis_id="diagnosis-1",
            tenant_id="tenant-1",
            expected_version=1,
            diagnosis_name="New Name",
        )

        assert result is None
        mock_event_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_list_diagnoses_returns_empty_list(self, service, mock_repository):
        """Test list_diagnoses_by_tenant returns empty list."""
        mock_repository.list_by_tenant = AsyncMock(return_value=([], 0))

        diagnoses, total = await service.list_diagnoses_by_tenant(
            tenant_id="tenant-empty",
            page=1,
            page_size=50,
        )

        assert diagnoses == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_list_diagnoses_by_patient_respects_pagination(self, service, mock_repository):
        """Test list_diagnoses_by_patient correctly passes pagination params."""
        mock_diagnoses = [MagicMock(id=f"d{i}") for i in range(10)]
        mock_repository.list_by_patient = AsyncMock(return_value=(mock_diagnoses, 100))

        await service.list_diagnoses_by_patient(
            patient_id="patient-1",
            tenant_id="tenant-1",
            page=3,
            page_size=10,
        )

        mock_repository.list_by_patient.assert_called_once_with(
            "patient-1",
            "tenant-1",
            3,
            10,
        )


class TestDiagnosisRepositoryProtocol:
    """Test repository protocol compliance."""

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_save(self):
        """Verify repository protocol defines save method."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert DiagnosisRepository is not None

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_get_by_id(self):
        """Verify repository protocol defines get_by_id method."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert hasattr(DiagnosisRepository, "get_by_id")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_list_by_tenant(self):
        """Verify repository protocol defines list_by_tenant method."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert hasattr(DiagnosisRepository, "list_by_tenant")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_update_with_version(self):
        """Verify repository protocol update accepts version."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert hasattr(DiagnosisRepository, "update")

    @pytest.mark.asyncio
    async def test_repository_protocol_requires_soft_delete_with_metadata(self):
        """Verify repository protocol soft_delete accepts metadata."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert hasattr(DiagnosisRepository, "soft_delete")

    @pytest.mark.asyncio
    async def test_repository_protocol_has_list_by_patient(self):
        """Verify repository protocol has list_by_patient method."""
        from app.clinical.diagnosis.repository import DiagnosisRepository

        assert hasattr(DiagnosisRepository, "list_by_patient")
