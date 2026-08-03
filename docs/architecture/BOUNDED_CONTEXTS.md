# BOUNDED CONTEXTS — Definición y Contratos

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** Auditoría `docs/audit/PHASE_REPORT.md` + `docs/audit/PROJECT_INVENTORY.md`

---

## PRINCIPIO FUNDADOR

> "Un Bounded Context define un submundo coherente del dominio. Tiene sus propios modelos, su propia lógica, y es independiente de los otros Contexts."

Cada Context responde a: "¿De qué es responsable este equipo?"

---

## CONTEXT 1 — device

### Propósito

Gestionar el ciclo de vida de dispositivos médicos: registro, mantenimiento, incidentes y órdenes de trabajo.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_1/domain/device/` — AggregateRoot Device con serial, ubicación, estado
- **Evidencia:** `core/PHASE_1/domain/incident/` — AggregateRoot EngineeringIncident
- **Evidencia:** `core/PHASE_1/domain/knowledge/` — AggregateRoot KnowledgeArticle
- **Evidencia:** `apps/api/app/domain/device/service.py` — DeviceService implementado
- **Evidencia:** `apps/api/app/routers/devices.py` — 22 endpoints funcionales

### Responsabilidades

1. Registrar dispositivos con metadata y ubicación
2. Programar y ejecutar mantenimientos preventivos y correctivos
3. Gestionar incidentes generados por dispositivos
4. Crear y asignar órdenes de trabajo
5. Mantener documentación técnica (knowledge articles)

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `Device` | AggregateRoot | Dispositivo médico con identidad, estado, ubicación |
| `EngineeringIncident` | AggregateRoot | Incidente asociado a un dispositivo |
| `WorkOrder` | AggregateRoot | Orden de trabajo con asignaciones |
| `KnowledgeArticle` | AggregateRoot | Artículo técnico de referencia |

### Value Objects

`DeviceId`, `DeviceStatus`, `LocationInfo`, `SerialNumber`, `CalibrationInfo`, `IncidentSeverity`, `WorkOrderPriority`

### Eventos de dominio

| Evento | Cuándo se publica | Consumido por |
|---|---|---|
| `DeviceRegistered` | Nuevo dispositivo creado | clinical, audit, ai |
| `MaintenanceScheduled` | Mantenimiento programado | audit |
| `IncidentCreated` | Incidente abierto | clinical, audit, ai |
| `WorkOrderCompleted` | Orden completada | audit, clinical |
| `DeviceStatusChanged` | Cambio de estado | audit |

### Contratos públicos (Puertos)

```python
# device/contracts/device_repository.py
class DeviceRepository(ABC):
    async def save(self, device: Device) -> Result[Device, str]: ...
    async def get_by_id(self, device_id: DeviceId) -> Result[Device | None, str]: ...
    async def list(self, tenant_id: TenantId, filters: DeviceFilters) -> Result[list[Device], str]: ...

# device/contracts/incident_repository.py
class IncidentRepository(ABC):
    async def save(self, incident: EngineeringIncident) -> Result[EngineeringIncident, str]: ...
    async def get_by_device(self, device_id: DeviceId) -> Result[list[EngineeringIncident], str]: ...
```

### Dependencias permitidas

- ✅ `ai/contracts/EmbeddingPort` — para buscar knowledge articles
- ✅ `shared/` — primitives y result types
- ❌ `clinical/domain/` — prohibido
- ❌ `audit/domain/` — prohibido

### Estado en auditoría

**IMPLEMENTADO** — Dominio real funcionando en producción. Device, Incident, WorkOrder, Knowledge implementados. Algunos submódulos (department, inventory, staffing, capacity, asset) son PARCIAL.

---

## CONTEXT 2 — clinical

### Propósito

Generar recomendaciones clínicas basadas en evidencia, validarlas con reasoning, y entregarlas al profesional de salud.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_3/recommendation/` — AIRecommendation aggregate
- **Evidencia:** `core/PHASE_3/intelligence/` — reasoning, evidence, safety, confidence
- **Evidencia:** `core/PHASE_3/intelligence/foundation/enums.py` — EvidenceLevel usado por PHASE_4
- **Evidencia:** `apps/api/app/domain/recommendation/repository.py` — RecommendationRepository implementado
- **Evidencia:** PHASE_4 importa `EvidenceLevel`, `ReasoningPipeline`, `EvidenceStore` de PHASE_3

### Responsabilidades

1. Generar recomendaciones clínicas basadas en contexto de dispositivo
2. Validar evidencia con pipelines de razonamiento clínico
3. Calcular nivel de confianza de cada recomendación
4. Filtrar recomendaciones por seguridad del paciente
5. Explicar el razonamiento detrás de cada recomendación

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `AIRecommendation` | AggregateRoot | Recomendación con confianza, evidencia, explicación |
| `Evidence` | Entity | Pieza de evidencia que soporta una recomendación |
| `ReasoningResult` | Value Object | Resultado de un pipeline de razonamiento |
| `ConfidenceLevel` | Value Object | Nivel de confianza (HIGH, MEDIUM, LOW) |

### Eventos de dominio

| Evento | Cuándo se publica | Consumido por |
|---|---|---|
| `RecommendationGenerated` | Nueva recomendación creada | audit, device |
| `EvidenceValidated` | Evidencia validada contra reglas clínicas | audit |
| `ReasoningCompleted` | Pipeline de razonamiento terminado | ai |

### Contratos públicos

```python
# clinical/contracts/recommendation_repository.py
class RecommendationRepository(ABC):
    async def save(self, recommendation: AIRecommendation) -> Result[AIRecommendation, str]: ...
    async def get_by_device(self, device_id: DeviceId) -> Result[list[AIRecommendation], str]: ...
    async def get_pending(self, tenant_id: TenantId) -> Result[list[AIRecommendation], str]: ...
```

### Dependencias permitidas

- ✅ `device/contracts/` — para subscribirse a DeviceRegistered, IncidentCreated
- ✅ `ai/contracts/EmbeddingPort` — para generar embeddings clínicos
- ✅ `ai/contracts/ReasoningPort` — para pipelines de razonamiento
- ✅ `ai/contracts/RetrievalPort` — para búsqueda de evidencia
- ❌ `device/domain/` — prohibido

### Estado en auditoría

**IMPLEMENTADO (parcial)** — AIRecommendation aggregate implementado y usado por apps/api. Los submódulos de intelligence (reasoning, evidence, safety, confidence) son PARCIAL.

---

## CONTEXT 3 — ai

### Propósito

Proveer las capacidades de inteligencia artificial del sistema: embeddings, razonamiento, memoria, planificación, y ejecución de agentes.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_2/` — ~600 archivos de kernel, memory, rag, reasoning, embeddings, planner
- **Evidencia:** PHASE_4 importa `EmbeddingManager` y `SemanticRetrievalEngine` de PHASE_2
- **Evidencia:** PHASE_5 define gateway contracts hacia PHASE_2 (comentados, pendientes de implementar)

### Decisión arquitectónica (pendiente de validación)

**Pregunta:** ¿PHASE_2 contiene múltiples Bounded Contexts?

**Análisis de auditoría:**
- PHASE_2 tiene duplicación: `ai/rag` vs `cognitive/rag`, `ai/memory` vs `cognitive/memory`
- No hay evidencia de que se hayan diseñado como BCs separados
- La regla de arquitectura dice: "la estructura crece con el código"

**Hipótesis:** PHASE_2 es un único Bounded Context de AI que puede dividirse en el futuro si crece lo suficiente.

**Recomendación:** Mantener como un BC hasta que los submódulos requieran evolucionar independientemente. Monitorear el crecimiento.

### Responsabilidades

1. Generar embeddings vectoriales para textos y documentos
2. Ejecutar pipelines de razonamiento clínico
3. Mantener memoria de sesión para interacciones
4. Planificar secuencias de acciones para agentes
5. Recuperar información relevante (RAG)

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `CognitiveSession` | AggregateRoot | Sesión de interacción con contexto |
| `AgentTask` | AggregateRoot | Tarea asignada a un agente |
| `EmbeddingVector` | Value Object | Vector de embedding |
| `PlanStep` | Value Object | Paso de un plan generado |
| `RetrievalResult` | Value Object | Resultado de búsqueda semántica |

### Contratos públicos (Puertos de AI)

```python
# ai/contracts/embedding_port.py
class EmbeddingPort(ABC):
    async def get_embeddings(self, texts: list[str]) -> Result[list[list[float]], str]: ...
    async def get_embedding_for_query(self, query: str) -> Result[list[float], str]: ...

# ai/contracts/reasoning_port.py
class ReasoningPort(ABC):
    async def validate_claim(
        self, claim: str, evidence: list[Evidence]
    ) -> Result[ReasoningResult, str]: ...
    async def generate_explanation(
        self, recommendation: AIRecommendation
    ) -> Result[str, str]: ...

# ai/contracts/memory_port.py
class MemoryPort(ABC):
    async def store(self, session_id: SessionId, data: MemoryData) -> Result[None, str]: ...
    async def retrieve(self, session_id: SessionId, query: str) -> Result[list[MemoryEntry], str]: ...

# ai/contracts/retrieval_port.py
class RetrievalPort(ABC):
    async def search(
        self, query: str, top_k: int = 10, filters: dict | None = None
    ) -> Result[list[RetrievalResult], str]: ...
```

### Dependencias permitidas

- ✅ `device/contracts/` — subscribirse a DeviceRegistered, IncidentCreated
- ✅ `clinical/contracts/` — subscribirse a RecommendationGenerated
- ✅ `shared/` — transversales
- ❌ `device/domain/` — prohibido
- ❌ `clinical/domain/` — prohibido

### Estado en auditoría

**PARCIAL** — Mucho scaffolding (~600 archivos) con implementación parcial. El concepto de embeddings, reasoning, retrieval existe pero no está conectado como sistema unificado. **Decision pending: ¿es un BC o múltiples?**

---

## CONTEXT 4 — audit

### Propósito

Registrar todas las acciones del sistema para cumplimiento regulatorio (HIPAA, FDA, ISO 13485) y auditoría interna.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_7/audit/` — logger, repository, dashboard, compliance
- **Evidencia:** `apps/api/app/middleware/audit.py` — middleware de auditoría implementado
- **Evidencia:** `core/PHASE_1/infrastructure/contracts/security/audit.py` — AuditProvider contract

### Responsabilidades

1. Registrar cada acción del sistema con actor, timestamp, acción, recurso
2. Consultar trail de auditoría por tenant, usuario, rango de fechas
3. Generar reportes de auditoría para inspecciones regulatorias
4. Mantener inmutabilidad de los registros

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `AuditEntry` | AggregateRoot | Entrada inmutable de auditoría |
| `AuditQuery` | Value Object | Parámetros de búsqueda |

### Eventos de dominio

| Evento | Cuándo se publica | Consumido por |
|---|---|---|
| `ActionLogged` | Cualquier acción en el sistema | nadie (es el subscriber final) |

### Contratos públicos

```python
# audit/contracts/audit_port.py
class AuditPort(ABC):
    async def log(self, entry: AuditEntry) -> Result[None, str]: ...
    async def query(
        self, tenant_id: TenantId, filters: AuditFilters
    ) -> Result[list[AuditEntry], str]: ...
```

### Dependencias permitidas

- ✅ `shared/` — transversales
- ❌ Todos los otros domains — audit es subscriber pasivo

### Estado en auditoría

**PARCIAL** — Concepto definido, middleware implementado, pero el aggregate `AuditEntry` y su repository no están completamente implementados en la infraestructura.

---

## CONTEXT 5 — tenant

### Propósito

Aislar tenants y gestionar cuotas de recursos.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_7/tenant/` — manager, isolation, quotas, migrations
- **Evidencia:** `apps/api/app/api/v1/tenants/` — routers de tenant

### Responsabilidades

1. Crear y configurar tenants
2. Aislar datos entre tenants (RLS en PostgreSQL)
3. Gestionar cuotas de dispositivos, usuarios, almacenamiento
4. Aplicar límites de API por tier

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `Tenant` | AggregateRoot | Tenant con configuración y tier |
| `Quota` | Value Object | Límite de recurso |
| `TenantConfig` | Value Object | Configuración específica del tenant |

### Dependencias permitidas

- ✅ `shared/` — transversales
- ❌ Otros domains — tenant no consume dominios

### Estado en auditoría

**PARCIAL** — Estructura existe pero no está completamente integrada con el sistema de permisos y RLS.

---

## CONTEXT 6 — enterprise

### Propósito

Gestionar cumplimiento regulatorio (FDA, HIPAA, ISO 13485, IEC 62304), licenciamiento y soporte.

### Evidencia de existencia

- **Evidencia:** `core/PHASE_7/compliance/` — fda, hipaa, iec_62304, iso_13485, security
- **Evidencia:** `apps/api/app/enterprise/` — licensing, versioning, support (stubs dead code)

### Responsabilidades

1. Validar operaciones contra reglas de cumplimiento regulatorio
2. Gestionar licenciamiento y versiones del sistema
3. Gestionar tickets de soporte

### Entidades principales

| Entidad | Tipo | Descripción |
|---|---|---|
| `ComplianceRule` | Entity | Regla de cumplimiento activo |
| `License` | AggregateRoot | Licencia activa del sistema |
| `SupportTicket` | AggregateRoot | Ticket de soporte |

### Dependencias permitidas

- ✅ `audit/contracts/` — para registrar cumplimiento
- ✅ `device/contracts/` — para validar operaciones de dispositivos
- ✅ `shared/` — transversales

### Estado en auditoría

**PARCIAL** — Conceptos definidos pero no integrados en producción. Los stubs en `apps/api/app/enterprise/` son dead code.

---

## CONTEXT 7 — platform (no es un Bounded Context)

**Platform no es un Bounded Context.** Es infraestructura operativa.

El Domain Layer y Application Layer están en `core/`. Platform está fuera de core/.

```
platform/
├── deployment/    → Scripts de deploy (no dominio)
├── monitoring/    → Prometheus + Grafana (no dominio)
├── logging/      → ELK stack (no dominio)
├── observability/ → OpenTelemetry (no dominio)
├── recovery/     → Backup + restore (no dominio)
└── scaling/     → Autoscaling configs (no dominio)
```

Si desaparece, el negocio puede seguir operando. Los Bounded Contexts no dependen de platform.

---

## RESUMEN

| Context | Propósito | Implementado | Eventos | Contracts |
|---|---|---|---|---|
| device | Dispositivos médicos | ✅ Full | 5 | DeviceRepository, IncidentRepository |
| clinical | Recomendaciones clínicas | ⚠️ Parcial | 3 | RecommendationRepository |
| ai | Inteligencia AI | ⚠️ Parcial | 3 | EmbeddingPort, ReasoningPort, MemoryPort, RetrievalPort |
| audit | Auditoría regulatoria | ⚠️ Parcial | 1 | AuditPort |
| tenant | Multi-tenancy | ⚠️ Parcial | 1 | TenantPort |
| enterprise | Compliance + licensing | ⚠️ Parcial | 0 | CompliancePort |

---

*Los Contexts se implementan incrementalmente. Cada uno evoluciona a su propio ritmo.*
