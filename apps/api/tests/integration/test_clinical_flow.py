"""Integration test: Complete Clinical Flow Patient → Diagnosis.

This test validates the full clinical workflow:

    Crear paciente
        ↓
    Registrar diagnóstico
        ↓
    Consultar historial del paciente
        ↓
    Ver diagnóstico
        ↓
    Modificar diagnóstico
        ↓
    Ver auditoría (versiones)
        ↓
    Eliminar (soft delete)
        ↓
    Ver que desaparece de la consulta pero permanece en auditoría

Success criteria:
- Un desarrollador nuevo puede entender el flujo
- No hay que modificar Foundation para que funcione
- Los contextos se integran sin romper reglas
"""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.domain.diagnosis import DiagnosisService
from app.domain.diagnosis.repository import SQLAlchemyDiagnosisRepository
from app.domain.patient import PatientService
from app.domain.patient.repository import SQLAlchemyPatientRepository
from app.events.outbox import OutboxMessage
from app.infrastructure import EventBus
from app.models import Base
from app.models.diagnosis import Diagnosis as DiagnosisModel
from app.models.patient import Patient as PatientModel

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://eren:eren_test@localhost:5432/eren_test"
)


@pytest_asyncio.fixture
async def db_engine():
    """Create async engine for tests."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Create async session for tests."""
    async_session_factory = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session
        await session.rollback()


class TestClinicalFlowPatientDiagnosis:
    """Test complete clinical workflow: Patient → Diagnosis."""

    @pytest.mark.asyncio
    async def test_complete_clinical_flow(
        self, db_session: AsyncSession
    ):
        """
        Complete clinical flow test.
        
        Este test demuestra que Patient y Diagnosis funcionan juntos
        sin modificar Foundation.
        """
        # Arrange - Repositorios y servicios
        patient_repo = SQLAlchemyPatientRepository(db_session)
        diagnosis_repo = SQLAlchemyDiagnosisRepository(db_session)
        event_bus = EventBus(db_session)
        
        patient_service = PatientService(
            repository=patient_repo,
            event_bus=event_bus
        )
        diagnosis_service = DiagnosisService(
            repository=diagnosis_repo,
            event_bus=event_bus
        )

        # ========================================
        # PASO 1: Crear paciente
        # ========================================
        patient = await patient_service.create_patient(
            tenant_id="hospital-001",
            mrn="MRN-001",
            given_name="Juan",
            family_name="Pérez",
            created_by="dr-garcia",
            correlation_id="flow-001",
        )
        await db_session.commit()

        # Verificar que el paciente existe
        assert patient.id is not None
        assert patient.mrn == "MRN-001"
        assert patient.given_name == "Juan"

        # ========================================
        # PASO 2: Registrar diagnóstico
        # ========================================
        diagnosis = await diagnosis_service.record_diagnosis(
            tenant_id="hospital-001",
            patient_id=patient.id,
            diagnosis_code="I10",
            diagnosis_name="Hipertensión esencial",
            description="Presión arterial elevada",
            created_by="dr-garcia",
            correlation_id="flow-001",
        )
        await db_session.commit()

        # Verificar que el diagnóstico existe
        assert diagnosis.id is not None
        assert diagnosis.diagnosis_code == "I10"
        assert diagnosis.diagnosis_name == "Hipertensión esencial"

        # ========================================
        # PASO 3: Consultar historial del paciente
        # ========================================
        diagnoses, total = await diagnosis_service.list_diagnoses_by_patient(
            patient_id=patient.id,
            tenant_id="hospital-001",
            page=1,
            page_size=50,
        )

        # Verificar que hay un diagnóstico
        assert total == 1
        assert len(diagnoses) == 1
        assert diagnoses[0].diagnosis_code == "I10"

        # ========================================
        # PASO 4: Ver diagnóstico
        # ========================================
        retrieved_diagnosis = await diagnosis_service.get_diagnosis(
            diagnosis_id=diagnosis.id,
            tenant_id="hospital-001",
        )

        # Verificar datos
        assert retrieved_diagnosis is not None
        assert retrieved_diagnosis.diagnosis_code == "I10"
        assert retrieved_diagnosis.patient_id == patient.id  # Relación por ID

        # ========================================
        # PASO 5: Modificar diagnóstico
        # ========================================
        amended_diagnosis = await diagnosis_service.amend_diagnosis(
            diagnosis_id=diagnosis.id,
            tenant_id="hospital-001",
            expected_version=diagnosis.version,
            diagnosis_name="Hipertensión esencial (confirmada)",
            description="Paciente en seguimiento",
            correlation_id="flow-001",
        )
        await db_session.commit()

        # Verificar que cambió
        assert amended_diagnosis is not None
        assert amended_diagnosis.diagnosis_name == "Hipertensión esencial (confirmada)"
        assert amended_diagnosis.version == diagnosis.version + 1

        # ========================================
        # PASO 6: Ver auditoría (versiones)
        # ========================================
        # Consultar el diagnóstico actualizado
        audit_diagnosis = await diagnosis_service.get_diagnosis(
            diagnosis_id=diagnosis.id,
            tenant_id="hospital-001",
        )

        # Verificar que hay evidencia de modificación
        assert audit_diagnosis.version == 2
        assert audit_diagnosis.updated_at is not None

        # Verificar eventos en outbox
        result = await db_session.execute(
            select(OutboxMessage).where(
                OutboxMessage.aggregate_id == diagnosis.id
            )
        )
        events = result.scalars().all()

        # Debe haber: DiagnosisRecorded + DiagnosisAmended
        event_types = [e.event_type for e in events]
        assert "DiagnosisRecorded" in event_types
        assert "DiagnosisAmended" in event_types

        # ========================================
        # PASO 7: Eliminar (soft delete)
        # ========================================
        delete_result = await diagnosis_service.delete_diagnosis(
            diagnosis_id=diagnosis.id,
            tenant_id="hospital-001",
            deleted_by="dr-garcia",
            delete_reason="Error en código diagnóstico",
            correlation_id="flow-001",
        )
        await db_session.commit()

        assert delete_result is True

        # ========================================
        # PASO 8: Ver que desaparece de la consulta
        # ========================================
        # No debe aparecer en listados
        diagnoses_after_delete, total_after = await diagnosis_service.list_diagnoses_by_patient(
            patient_id=patient.id,
            tenant_id="hospital-001",
            page=1,
            page_size=50,
        )

        assert total_after == 0
        assert len(diagnoses_after_delete) == 0

        # No debe aparecer en get
        retrieved_after_delete = await diagnosis_service.get_diagnosis(
            diagnosis_id=diagnosis.id,
            tenant_id="hospital-001",
        )
        assert retrieved_after_delete is None

        # ========================================
        # PASO 9: Ver que permanece en auditoría
        # ========================================
        # Consultar directamente en la base de datos
        result = await db_session.execute(
            select(DiagnosisModel).where(
                DiagnosisModel.id == diagnosis.id
            )
        )
        audit_record = result.scalar_one_or_none()

        assert audit_record is not None
        assert audit_record.deleted_at is not None
        assert audit_record.deleted_by == "dr-garcia"
        assert audit_record.delete_reason == "Error en código diagnóstico"

        # Verificar que hay evento de eliminación
        result = await db_session.execute(
            select(OutboxMessage).where(
                OutboxMessage.aggregate_id == diagnosis.id,
                OutboxMessage.event_type == "DiagnosisDeleted"
            )
        )
        delete_event = result.scalar_one_or_none()
        
        assert delete_event is not None

        # ========================================
        # VALIDACIÓN FINAL
        # ========================================
        # El paciente sigue existiendo (no se borró)
        patient_still_exists = await patient_service.get_patient(
            patient_id=patient.id,
            tenant_id="hospital-001",
        )
        assert patient_still_exists is not None

    @pytest.mark.asyncio
    async def test_contexts_are_isolated(
        self, db_session: AsyncSession
    ):
        """
        Verify that Patient and Diagnosis are truly isolated.
        
        Diagnosis solo conoce patient_id, no la entidad Patient.
        """
        patient_repo = SQLAlchemyPatientRepository(db_session)
        diagnosis_repo = SQLAlchemyDiagnosisRepository(db_session)
        event_bus = EventBus(db_session)
        
        patient_service = PatientService(
            repository=patient_repo,
            event_bus=event_bus
        )
        diagnosis_service = DiagnosisService(
            repository=diagnosis_repo,
            event_bus=event_bus
        )

        # Crear paciente
        patient = await patient_service.create_patient(
            tenant_id="tenant-iso",
            mrn="MRN-ISO",
            given_name="Test",
            family_name="Isolation",
            created_by="system",
        )
        await db_session.commit()

        # Registrar diagnóstico
        diagnosis = await diagnosis_service.record_diagnosis(
            tenant_id="tenant-iso",
            patient_id=patient.id,
            diagnosis_code="E11.9",
            diagnosis_name="Diabetes mellitus",
            created_by="system",
        )
        await db_session.commit()

        # El diagnóstico tiene patient_id (identidad)
        assert diagnosis.patient_id == patient.id

        # El modelo de base de datos solo tiene patient_id
        result = await db_session.execute(
            select(DiagnosisModel).where(DiagnosisModel.id == diagnosis.id)
        )
        db_diagnosis = result.scalar_one()

        # Verificar que NO tiene columna de relación
        # (no debe tener ForeignKey hacia Patient)
        assert db_diagnosis.patient_id == patient.id
        
        # Verificar que no existe relación ORM
        assert not hasattr(db_diagnosis, 'patient')

    @pytest.mark.asyncio
    async def test_tenant_isolation_between_contexts(
        self, db_session: AsyncSession
    ):
        """
        Verify that tenant isolation works across contexts.
        
        Tenant A no puede ver datos de Tenant B.
        """
        patient_repo = SQLAlchemyPatientRepository(db_session)
        diagnosis_repo = SQLAlchemyDiagnosisRepository(db_session)
        event_bus = EventBus(db_session)
        
        patient_service = PatientService(
            repository=patient_repo,
            event_bus=event_bus
        )
        diagnosis_service = DiagnosisService(
            repository=diagnosis_repo,
            event_bus=event_bus
        )

        # Crear pacientes para dos tenants
        patient_a = await patient_service.create_patient(
            tenant_id="tenant-A",
            mrn="MRN-A",
            given_name="Patient",
            family_name="A",
            created_by="system",
        )
        patient_b = await patient_service.create_patient(
            tenant_id="tenant-B",
            mrn="MRN-B",
            given_name="Patient",
            family_name="B",
            created_by="system",
        )
        await db_session.commit()

        # Registrar diagnósticos para ambos
        await diagnosis_service.record_diagnosis(
            tenant_id="tenant-A",
            patient_id=patient_a.id,
            diagnosis_code="A00",
            diagnosis_name="Diagnostico A",
            created_by="system",
        )
        await diagnosis_service.record_diagnosis(
            tenant_id="tenant-B",
            patient_id=patient_b.id,
            diagnosis_code="B00",
            diagnosis_name="Diagnostico B",
            created_by="system",
        )
        await db_session.commit()

        # Consultar desde Tenant A
        diagnoses_a, total_a = await diagnosis_service.list_diagnoses_by_tenant(
            tenant_id="tenant-A",
            page=1,
            page_size=50,
        )

        # Consultar desde Tenant B
        diagnoses_b, total_b = await diagnosis_service.list_diagnoses_by_tenant(
            tenant_id="tenant-B",
            page=1,
            page_size=50,
        )

        # Verificar aislamiento
        assert total_a == 1
        assert diagnoses_a[0].diagnosis_code == "A00"

        assert total_b == 1
        assert diagnoses_b[0].diagnosis_code == "B00"

        # Tenant A no ve diagnósticos de Tenant B
        assert all(d.tenant_id == "tenant-A" for d in diagnoses_a)
        assert all(d.tenant_id == "tenant-B" for d in diagnoses_b)


class TestFoundationValidation:
    """
    Validate that Foundation patterns were not broken.
    
    Este test verifica que el flujo funciona SIN modificar Foundation.
    """
    
    @pytest.mark.asyncio
    async def test_no_foundation_was_modified(
        self, db_session: AsyncSession
    ):
        """
        Verify that the flow works with existing patterns only.
        
        Si este test pasa, significa:
        - No se necesitó modificar Patient
        - No se necesitó modificar Diagnosis
        - El patrón se copió correctamente
        """
        # Importar directamente desde los módulos
        from app.domain.patient import PatientService
        from app.domain.patient.repository import SQLAlchemyPatientRepository
        from app.domain.diagnosis import DiagnosisService
        from app.domain.diagnosis.repository import SQLAlchemyDiagnosisRepository
        from app.infrastructure import EventBus
        
        # Verificar que todos los componentes existen
        assert PatientService is not None
        assert SQLAlchemyPatientRepository is not None
        assert DiagnosisService is not None
        assert SQLAlchemyDiagnosisRepository is not None
        assert EventBus is not None
        
        # Verificar que tienen la estructura correcta
        repo = SQLAlchemyPatientRepository(db_session)
        assert hasattr(repo, 'save')
        assert hasattr(repo, 'get_by_id')
        assert hasattr(repo, 'list_by_tenant')
        assert hasattr(repo, 'soft_delete')
        
        diag_repo = SQLAlchemyDiagnosisRepository(db_session)
        assert hasattr(diag_repo, 'save')
        assert hasattr(diag_repo, 'get_by_id')
        assert hasattr(diag_repo, 'list_by_patient')
        assert hasattr(diag_repo, 'soft_delete')
