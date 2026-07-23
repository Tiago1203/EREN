# EPIC 2: Biomedical Agent

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Especializar un agente experto en Ingeniería Clínica.

---

## Responsabilidad

**Resolver preguntas relacionadas con Ingeniería Clínica.**

EPIC 2 es responsable de:

- Analizar equipos médicos
- Generar recomendaciones de mantenimiento
- Verificar cumplimiento de normas (IEC, ISO, AAMI)
- Proporcionar información de fabricantes
- Gestionar calibraciones
- Evaluar riesgos de dispositivos

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Reasoning, Evidence, Decision)
- **FASE 4**: Knowledge Platform (RAG, Embeddings, Citations)

### EPICs
- **EPIC 0**: Base Agent, AgentRegistry
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 2: Biomedical Agent                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    BIOMEDICAL AGENT                                │   │
│  │  ├── EquipmentExpert ──────────── Análisis de equipos             │   │
│  │  ├── MaintenanceExpert ────────── Recomendaciones de mantenimiento │   │
│  │  ├── ManufacturerExpert ───────── Información de fabricantes       │   │
│  │  ├── StandardsExpert ──────────── Normas IEC/ISO/AAMI              │   │
│  │  └── CalibrationExpert ────────── Calibraciones                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       TASK PROCESSORS                              │   │
│  │  ├── Device Analysis ──────────── Análisis técnico                │   │
│  │  ├── Maintenance Planning ──────── Planificación PM/CM/PdM         │   │
│  │  ├── Calibration Check ─────────── Estado de calibración          │   │
│  │  ├── Compliance Audit ───────────── Cumplimiento de normas         │   │
│  │  └── Risk Assessment ───────────── Evaluación de riesgos           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN OBJECTS                               │   │
│  │  ├── BiomedicalTask ────────────── Tarea especializada            │   │
│  │  ├── DeviceAssessment ──────────── Evaluación de dispositivo      │   │
│  │  └── MaintenanceRecommendation ── Recomendación de mantenimiento  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic2_biomedical_agent/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # BiomedicalTask, DeviceAssessment, etc.
├── experts/
│   └── __init__.py              # Equipment, Maintenance, Manufacturer, Standards, Calibration
└── agent/
    └── __init__.py              # BiomedicalAgent
```

---

## Componentes

### 1. BiomedicalAgent

Agente principal especializado en ingeniería clínica.

```python
class BiomedicalAgent(BaseAgent):
    """Agente especializado en Ingeniería Clínica."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea biomédica."""
```

**Tipos de tarea:**
- `DEVICE_ANALYSIS`: Análisis técnico de equipo
- `MAINTENANCE_PLANNING`: Planificación de mantenimiento
- `CALIBRATION_CHECK`: Verificación de calibración
- `COMPLIANCE_AUDIT`: Auditoría de cumplimiento
- `RISK_ASSESSMENT`: Evaluación de riesgos
- `INCIDENT_INVESTIGATION`: Investigación de incidentes
- `MANUAL_REVIEW`: Revisión de manuales
- `SPECIFICATION_ANALYSIS`: Análisis de especificaciones

### 2. EquipmentExpert

Analiza equipos médicos.

```python
class EquipmentExpert:
    """Experto en análisis de equipos médicos."""
    
    async def analyze_device(self, device_id: str, context: dict) -> EquipmentAnalysis:
        """Analiza un dispositivo médico."""
    
    async def predict_failures(self, device_id: str, usage_hours: int, age_years: float) -> list[dict]:
        """Predice fallas potenciales."""
```

### 3. MaintenanceExpert

Genera recomendaciones de mantenimiento.

```python
class MaintenanceExpert:
    """Experto en asesoría de mantenimiento."""
    
    async def generate_recommendations(
        self,
        device_id: str,
        device_type: str,
        age_years: float,
        usage_hours: int,
    ) -> list[MaintenanceRecommendation]:
        """Genera recomendaciones de mantenimiento."""
```

**Tipos de mantenimiento:**
- `PREVENTIVE`: Preventivo
- `CORRECTIVE`: Correctivo
- `PREDICTIVE`: Predictivo
- `CALIBRATION`: Calibración
- `SAFETY`: Seguridad
- `EMERGENCY`: Emergencia
- `INSPECTION`: Inspección

### 4. StandardsExpert

Expertos en normas técnicas.

```python
class StandardsExpert:
    """Experto en normas y estándares técnicos."""
    
    async def find_applicable_standards(
        self,
        device_type: str,
        device_class: str,
    ) -> list[StandardReference]:
        """Encuentra estándares aplicables."""
    
    async def check_compliance(
        self,
        standard_id: str,
        device_requirements: dict,
    ) -> dict:
        """Verifica cumplimiento de un estándar."""
```

**Estándares soportados:**
- IEC 60601-1: Requisitos generales
- IEC 60601-1-2: Compatibilidad electromagnética
- IEC 60601-1-6: Usabilidad
- IEC 60601-1-8: Sistemas de alarma
- IEC 62353: Pruebas recurrentes
- ISO 14971: Gestión de riesgos
- AAMI HE75: Factores humanos

### 5. CalibrationExpert

Gestiona calibraciones.

```python
class CalibrationExpert:
    """Experto en calibraciones."""
    
    async def get_calibration_status(self, device_id: str) -> dict:
        """Obtiene estado de calibración."""
    
    async def calculate_interval(
        self,
        device_type: str,
        usage_hours: int,
        accuracy_required: float,
    ) -> int:
        """Calcula intervalo de calibración."""
```

### 6. ManufacturerExpert

Información de fabricantes.

```python
class ManufacturerExpert:
    """Experto en información de fabricantes."""
    
    async def get_manufacturer_info(self, manufacturer_name: str) -> ManufacturerInfo | None:
        """Obtiene información de un fabricante."""
    
    async def get_device_manual(self, manufacturer: str, model: str) -> dict | None:
        """Obtiene manual de dispositivo."""
```

---

## Domain Objects

### BiomedicalTask

```python
@dataclass
class BiomedicalTask:
    """Tarea especializada en Ingeniería Clínica."""
    task_id: str
    task_type: BiomedicalTaskType
    device_id: str | None
    device_name: str
    device_type: str
    manufacturer: str
    model: str
    description: str
    priority: MaintenancePriority
    context: dict
```

### DeviceAssessment

```python
@dataclass
class DeviceAssessment:
    """Evaluación de un dispositivo médico."""
    assessment_id: str
    device_id: str
    severity: AssessmentSeverity
    findings: list[dict]
    recommendations: list[str]
    compliance_status: dict
    violations: list[dict]
```

### MaintenanceRecommendation

```python
@dataclass
class MaintenanceRecommendation:
    """Recomendación de mantenimiento."""
    recommendation_id: str
    device_id: str
    maintenance_type: MaintenanceType
    priority: MaintenancePriority
    title: str
    description: str
    estimated_duration_minutes: int
    frequency_days: int | None
    estimated_cost: float
    standards: list[str]
```

---

## Uso

### Uso básico

```python
from core.PHASE_5.epic2_biomedical_agent import (
    BiomedicalAgent,
    BiomedicalAgentConfig,
)

# Crear agente
config = BiomedicalAgentConfig(
    enable_equipment_expert=True,
    enable_maintenance_expert=True,
    enable_standards_expert=True,
)
agent = BiomedicalAgent(
    agent_id="biomedical_1",
    config=config,
)

# Analizar dispositivo
result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="biomedical_1",
    task_type="device_analysis",
    input_data={
        "device_id": "DEV-123",
        "device_name": "Infusion Pump",
        "device_type": "therapeutic_equipment",
        "manufacturer": "Medtronic",
        "model": "Symbia T",
        "age_years": 3,
        "usage_hours": 5000,
    },
))
```

### Planificación de mantenimiento

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="biomedical_1",
    task_type="maintenance_planning",
    input_data={
        "device_id": "DEV-456",
        "device_type": "monitoring_equipment",
        "age_years": 5,
        "usage_hours": 15000,
    },
))

for rec in result.output["recommendations"]:
    print(f"{rec['priority']}: {rec['title']}")
```

### Auditoría de cumplimiento

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="biomedical_1",
    task_type="compliance_audit",
    input_data={
        "device_id": "DEV-789",
        "device_type": "diagnostic_equipment",
        "device_class": "Class II",
    },
))

for std in result.output["standards"]:
    status = "✅" if std["compliant"] else "❌"
    print(f"{status} {std['id']}: {std['title']}")
```

---

## Estándares Técnicos Soportados

| Estándar | Descripción | Obligatorio |
|----------|-------------|-------------|
| IEC 60601-1 | Requisitos generales para equipos médicos eléctricos | ✅ |
| IEC 60601-1-2 | Compatibilidad electromagnética | ✅ |
| IEC 60601-1-6 | Usabilidad | ✅ |
| IEC 60601-1-8 | Sistemas de alarma | ⚠️ |
| IEC 62353 | Pruebas recurrentes | ✅ |
| ISO 14971 | Gestión de riesgos | ✅ |
| AAMI HE75 | Factores humanos | ⚠️ |

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `DEVICE_ANALYZED` | Dispositivo analizado |
| `MAINTENANCE_RECOMMENDED` | Mantenimiento recomendado |
| `CALIBRATION_CHECKED` | Calibración verificada |
| `COMPLIANCE_AUDITED` | Cumplimiento auditado |
| `RISK_ASSESSED` | Riesgo evaluado |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `DeviceNotFoundError` | Dispositivo no encontrado |
| `ManufacturerUnknownError` | Fabricante desconocido |
| `StandardNotFoundError` | Estándar no encontrado |
| `CalibrationExpiredError` | Calibración vencida |

---

## Concatenación

```
EPIC 1 ──► EPIC 2 (orquesta BiomedicalAgent)
FASE 3 ──► EPIC 2 (consume Reasoning, Evidence)
FASE 4 ──► EPIC 2 (consume RAG, Knowledge)
EPIC 2 ──► EPIC 3 (provee contexto a DiagnosticAgent)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 3: Diagnostic Agent
- EPIC 4: Knowledge Agent

---

*EREN PHASE 5 - EPIC 2*
*Architecture Board - 2026-07-23*
