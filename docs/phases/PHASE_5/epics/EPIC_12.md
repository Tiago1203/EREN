# EPIC 12: Clinical Context Builder

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Construir el modelo de contexto clínico unificado que alimenta todo el sistema cognitivo.**

EPIC 12 es responsable de:
- Consolidar contexto del paciente
- Consolidar contexto del dispositivo
- Consolidar contexto hospitalario
- Unificar contextos para razonamiento clínico
- Gestionar ciclo de vida del contexto clínico

---

## Dependencias

### Fases
- **FASE 1**: Business Domain (Device, Incident, Knowledge, Asset, Hospital)
- **FASE 2**: Cognitive Operating System (Memory, Context)
- **FASE 3**: Clinical Intelligence (Reasoning, Evidence, Decision)
- **FASE 4**: Knowledge Platform (RAG, Embeddings)

### EPICs
- **EPIC 0**: Foundation (provee BaseAgent, AgentContext)
- **EPIC 1**: Agent Orchestrator (lo invoca para construir contexto)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 12: Clinical Context Builder                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  CLINICAL CONTEXT MODULES                            │   │
│  │  ├── PatientContextBuilder ──────────── Construye contexto paciente │   │
│  │  ├── DeviceContextBuilder ──────────── Construye contexto dispositivo│   │
│  │  ├── HospitalContextBuilder ─────────── Construye contexto hosp.   │   │
│  │  ├── ClinicalContextAggregator ─────── Agrega todos los contextos│   │
│  │  └── ContextLifecycleManager ────────── Gestiona ciclo de contexto │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── ClinicalContext ─────────────────── Contexto clínico unificado│   │
│  │  ├── PatientContext ───────────────────── Contexto de paciente     │   │
│  │  ├── DeviceContext ────────────────────── Contexto de dispositivo  │   │
│  │  ├── HospitalContext ──────────────────── Contexto hospitalario     │   │
│  │  └── ContextSnapshot ─────────────────── Snapshot de contexto       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    CONTEXT COMPONENTS                               │   │
│  │  ├── MedicalHistory ───────────────────── Historia médica          │   │
│  │  ├── DeviceHistory ────────────────────── Historia de dispositivo  │   │
│  │  ├── ClinicalTimeline ─────────────────── Línea de tiempo clínica  │   │
│  │  ├── RiskFactors ──────────────────────── Factores de riesgo      │   │
│  │  └── ActiveConditions ─────────────────── Condiciones activas     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic12_clinical_context/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # ClinicalContext, PatientContext, etc.
├── builders/
│   ├── __init__.py              # Builders de contexto
│   ├── patient_builder.py       # PatientContextBuilder
│   ├── device_builder.py        # DeviceContextBuilder
│   ├── hospital_builder.py      # HospitalContextBuilder
│   └── context_aggregator.py    # ClinicalContextAggregator
├── lifecycle/
│   ├── __init__.py              # ContextLifecycleManager
│   └── context_manager.py       # Gestión de ciclo de vida
└── agent/
    └── __init__.py              # ClinicalContextAgent
```

---

## Componentes

### 1. ClinicalContextAgent

Agente principal de contexto clínico.

```python
class ClinicalContextAgent(BaseAgent):
    """Agente de construcción de contexto clínico."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta construcción de contexto."""
```

**Acciones:**
- `build`: Construir contexto clínico
- `patient`: Construir contexto de paciente
- `device`: Construir contexto de dispositivo
- `hospital`: Construir contexto hospitalario
- `aggregate`: Agregar contextos
- `snapshot`: Guardar snapshot

### 2. PatientContextBuilder

Construye contexto de paciente.

```python
class PatientContextBuilder:
    """Constructor de contexto de paciente."""
    
    async def build(
        self,
        patient_id: str,
        include_history: bool = True,
        include_conditions: bool = True,
    ) -> PatientContext:
        """Construye contexto de paciente."""
    
    async def get_medical_history(
        self,
        patient_id: str,
    ) -> MedicalHistory:
        """Obtiene historial médico."""
    
    async def get_active_conditions(
        self,
        patient_id: str,
    ) -> list[ActiveCondition]:
        """Obtiene condiciones activas."""
```

### 3. DeviceContextBuilder

Construye contexto de dispositivo.

```python
class DeviceContextBuilder:
    """Constructor de contexto de dispositivo."""
    
    async def build(
        self,
        device_id: str,
        include_maintenance: bool = True,
        include_incidents: bool = True,
    ) -> DeviceContext:
        """Construye contexto de dispositivo."""
    
    async def get_device_history(
        self,
        device_id: str,
    ) -> DeviceHistory:
        """Obtiene historial de dispositivo."""
    
    async def get_incident_history(
        self,
        device_id: str,
    ) -> list[Incident]:
        """Obtiene historial de incidentes."""
```

### 4. HospitalContextBuilder

Construye contexto hospitalario.

```python
class HospitalContextBuilder:
    """Constructor de contexto hospitalario."""
    
    async def build(
        self,
        hospital_id: str,
        include_departments: bool = True,
        include_capacity: bool = True,
    ) -> HospitalContext:
        """Construye contexto hospitalario."""
    
    async def get_department_context(
        self,
        department_id: str,
    ) -> DepartmentContext:
        """Obtiene contexto de departamento."""
    
    async def get_resource_availability(
        self,
        hospital_id: str,
    ) -> ResourceAvailability:
        """Obtiene disponibilidad de recursos."""
```

### 5. ClinicalContextAggregator

Agrega todos los contextos en un contexto clínico unificado.

```python
class ClinicalContextAggregator:
    """Agregador de contexto clínico."""
    
    async def aggregate(
        self,
        patient_context: PatientContext,
        device_context: DeviceContext,
        hospital_context: HospitalContext,
    ) -> ClinicalContext:
        """Agrega contextos en contexto clínico."""
    
    async def enrich_with_timeline(
        self,
        context: ClinicalContext,
    ) -> ClinicalContext:
        """Enriquece con línea de tiempo."""
    
    async def identify_risk_factors(
        self,
        context: ClinicalContext,
    ) -> list[RiskFactor]:
        """Identifica factores de riesgo."""
```

### 6. ContextLifecycleManager

Gestiona ciclo de vida del contexto.

```python
class ContextLifecycleManager:
    """Gestor de ciclo de vida de contexto."""
    
    async def create_context(
        self,
        session_id: str,
        patient_id: str,
        device_id: str,
    ) -> ClinicalContext:
        """Crea nuevo contexto."""
    
    async def update_context(
        self,
        context_id: str,
        updates: dict,
    ) -> ClinicalContext:
        """Actualiza contexto existente."""
    
    async def snapshot(
        self,
        context_id: str,
    ) -> ContextSnapshot:
        """Guarda snapshot de contexto."""
    
    async def restore(
        self,
        snapshot_id: str,
    ) -> ClinicalContext:
        """Restaura desde snapshot."""
```

---

## Domain Objects

### ClinicalContext

```python
@dataclass
class ClinicalContext:
    """Contexto clínico unificado."""
    context_id: str
    patient_context: PatientContext
    device_context: DeviceContext
    hospital_context: HospitalContext
    timeline: ClinicalTimeline
    risk_factors: list[RiskFactor]
    metadata: ContextMetadata
    
    def get_patient_id(self) -> str:
        """Obtiene ID de paciente."""
    
    def get_device_id(self) -> str:
        """Obtiene ID de dispositivo."""
    
    def get_active_conditions(self) -> list[str]:
        """Obtiene condiciones activas."""
    
    def get_risk_level(self) -> RiskLevel:
        """Obtiene nivel de riesgo."""
```

### PatientContext

```python
@dataclass
class PatientContext:
    """Contexto de paciente."""
    patient_id: str
    medical_history: MedicalHistory
    active_conditions: list[ActiveCondition]
    allergies: list[str]
    medications: list[Medication]
    demographics: PatientDemographics
    
    def get_critical_conditions(self) -> list[str]:
        """Obtiene condiciones críticas."""
```

### DeviceContext

```python
@dataclass
class DeviceContext:
    """Contexto de dispositivo."""
    device_id: str
    device_type: str
    manufacturer: str
    model: str
    maintenance_history: list[MaintenanceRecord]
    incident_history: list[Incident]
    calibration_status: CalibrationStatus
    risk_classification: DeviceRiskClass
    
    def needs_maintenance(self) -> bool:
        """Verifica si necesita mantenimiento."""
    
    def get_incident_trend(self) -> IncidentTrend:
        """Obtiene tendencia de incidentes."""
```

### HospitalContext

```python
@dataclass
class HospitalContext:
    """Contexto hospitalario."""
    hospital_id: str
    department: DepartmentContext
    unit: UnitContext
    bed_availability: BedAvailability
    staff_availability: StaffAvailability
    resource_capacity: ResourceCapacity
    
    def get_resource_constraints(self) -> list[str]:
        """Obtiene restricciones de recursos."""
```

---

## ContextMetadata

```python
@dataclass
class ContextMetadata:
    """Metadatos de contexto."""
    created_at: datetime
    updated_at: datetime
    created_by: str
    session_id: str
    version: int
    
    def is_stale(self, threshold_hours: int = 24) -> bool:
        """Verifica si está obsoleto."""
```

---

## Uso

### Construir contexto clínico completo

```python
from core.PHASE_5.epic12_clinical_context import (
    ClinicalContextAgent,
    ClinicalContextConfig,
)

agent = ClinicalContextAgent(
    agent_id="context_builder_1",
    config=ClinicalContextConfig(),
)

result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="context_builder_1",
    task_type="clinical_context",
    input_data={
        "action": "build",
        "patient_id": "patient_123",
        "device_id": "device_456",
        "hospital_id": "hospital_789",
    },
))
```

### Construir solo contexto de paciente

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="context_builder_1",
    task_type="clinical_context",
    input_data={
        "action": "patient",
        "patient_id": "patient_123",
        "include_history": True,
        "include_conditions": True,
    },
))
```

### Guardar snapshot de contexto

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="context_builder_1",
    task_type="clinical_context",
    input_data={
        "action": "snapshot",
        "context_id": "context_123",
    },
))
```

---

## Integración con FASE 1-4

```
FASE 1 (Device/Incident/Knowledge) ──► ClinicalContextAgent
                                          │
FASE 2 (Memory/Context) ──────────────────┼──► PatientContextBuilder
                                          │              │
FASE 3 (Reasoning/Evidence/Decision) ─────┼──► DeviceContextBuilder
                                          │              │
FASE 4 (Knowledge/RAG) ────────────────────┴──► HospitalContextBuilder
                                                      │
                                                      ▼
                                              ClinicalContext
```

---

## Concatenación

```
EPIC 0 (Foundation) ──► EPIC 12 (Clinical Context)
EPIC 1 (Orchestrator) ──► EPIC 12 (construye contexto)
EPIC 12 ──► EPIC 2-6 (provee contexto a agentes)
EPIC 12 ──► EPIC 3 (Diagnosis necesita contexto)
```

---

## Estado

**✅ IMPLEMENTADO**

Este EPIC cierra el gap de Clinical Context (10/100 → 90/100).

---

## Próximos Pasos

- EPIC 13: Evidence Lifecycle Model
- EPIC 14: Uncertainty Quantification

---

*EREN PHASE 5 - EPIC 12*
*Architecture Board - 2026-07-24*
