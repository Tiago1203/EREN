# EREN - Cognitive Operating System for Clinical Engineering

## Prompt para Documentación y Contexto

---

## 📌 ¿Qué es EREN?

**EREN** (Enterprise Reasoning Engine Network) es un **Cognitive Operating System (COS)** especializado en **Ingeniería Clínica**. 

No es una aplicación tradicional, ni un chatbot, ni un asistente simple. Es un **sistema operativo cognitivo** que:
- Orchestra procesos de pensamiento complejo
- Gestiona conocimiento institucional
- Amplifica la capacidad humana en entornos clínicos
- Proporciona razonamiento contextual para mantenimiento de equipos médicos

---

## 🏗️ Arquitectura

EREN está construido con los siguientes principios arquitectónicos:

### Domain-Driven Design (DDD)
- **Bounded Contexts** separados para cada dominio de negocio
- **Shared Kernel** para lógica común
- **Ubiquitous Language** compartida

### Clean Architecture
```
┌─────────────────────────────────────────────────┐
│                  PRESENTATION                      │
│              (API REST, Web UI)                   │
├─────────────────────────────────────────────────┤
│                   APPLICATION                     │
│              (Use Cases, Services)                │
├─────────────────────────────────────────────────┤
│                     DOMAIN                        │
│           (Entities, Value Objects,               │
│            Domain Events, Aggregates)              │
├─────────────────────────────────────────────────┤
│                 INFRASTRUCTURE                    │
│     (Repositories, External Services, DB)         │
└─────────────────────────────────────────────────┘
```

### Event-Driven Architecture
- **RabbitMQ** como message broker
- **Outbox Pattern** para consistencia eventual
- Domain Events para comunicación entre contextos

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **API Backend** | FastAPI + Pydantic v2 |
| **Base de Datos** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Cache** | Redis |
| **Message Broker** | RabbitMQ |
| **Frontend** | Next.js 14 (App Router) |
| **Mobile** | React Native (futuro) |
| **Containerización** | Docker + Docker Compose |
| **Orquestación** | Kubernetes + Helm |
| **CI/CD** | GitHub Actions |
| **Monitoreo** | OpenTelemetry |

---

## 📂 Estructura del Proyecto

```
EREN/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/       # API endpoints
│   │   │   ├── schemas/       # Pydantic DTOs
│   │   │   ├── models/        # SQLAlchemy ORM
│   │   │   ├── services/      # Business logic
│   │   │   ├── infrastructure/# Repos, Events
│   │   │   └── integrations/  # FHIR, HL7, MQTT
│   │   └── tests/
│   │
│   └── web/                    # Next.js frontend
│       ├── app/               # App Router pages
│       ├── components/        # React components
│       └── lib/               # Utilities
│
├── core/                       # Domain logic (DDD)
│   ├── device/                # Device Context
│   ├── incident/              # Incident Context
│   ├── knowledge/             # Knowledge Context
│   ├── recommendation/        # Recommendation Context
│   ├── capacity/              # Hospital Capacity
│   ├── staffing/              # Staffing Management
│   ├── organization/          # Organization
│   ├── department/            # Department
│   ├── inventory/             # Inventory Management
│   ├── asset/                 # Asset Management
│   └── shared/                # Shared Kernel
│       ├── primitives/        # Value Objects
│       ├── events/            # Base events
│       └── exceptions/        # Shared exceptions
│
├── infra/                      # Infrastructure as Code
│   ├── k8s/                  # Kubernetes manifests
│   ├── helm/                 # Helm charts
│   ├── scripts/              # Deployment scripts
│   └── production/            # Production configs
│
├── docs/                      # Documentación
│   ├── phases/               # Fases del proyecto
│   │   └── PHASE_1/          # ✅ COMPLETO
│   │       ├── epics/        # epic0-10
│   │       └── adr/          # Architecture Decisions
│   ├── architecture/          # Docs de arquitectura
│   └── guides/               # Guías técnicas
│
├── tests/                     # Tests
│   ├── test_epic3_*.py      # Tests de dominios
│   ├── integration/          # Tests de integración
│   └── unit/                # Tests unitarios
│
├── docker-compose.yml        # Desarrollo local
├── pyproject.toml            # Dependencias Python
└── package.json              # Dependencias Node
```

---

## 📋 Dominios Implementados (Bounded Contexts)

### 1. Device Context (`core/device/`)
- **Entidades:** Device, Location, Manufacturer, Model
- **Comportamiento:** Registro, transferencia, mantenimiento, calibración, descomisionamiento
- **Eventos:** DeviceRegistered, DeviceTransferred, MaintenanceScheduled

### 2. Incident Context (`core/incident/`)
- **Entidades:** EngineeringIncident, Alert, IncidentType
- **Comportamiento:** Creación, escalamiento, resolución de incidentes
- **Eventos:** IncidentCreated, IncidentEscalated, IncidentResolved

### 3. Knowledge Context (`core/knowledge/`)
- **Entidades:** KnowledgeArticle, Category, Tag
- **Comportamiento:** CRUD de artículos, búsqueda, versionado
- **Eventos:** ArticlePublished, ArticleUpdated

### 4. Recommendation Context (`core/recommendation/`)
- **Entidades:** AIRecommendation, RecommendationType
- **Comportamiento:** Generación de recomendaciones basadas en contexto
- **Eventos:** RecommendationGenerated

### 5. Capacity Context (`core/capacity/`)
- **Entidades:** Campus, Building, Floor, Room, Bed
- **Comportamiento:** Gestión de capacidad hospitalaria
- **Eventos:** CapacityUpdated, BedOccupied, BedVacated

### 6. Staffing Context (`core/staffing/`)
- **Entidades:** Staff, Role, Shift, Team
- **Comportamiento:** Gestión de personal, turnos, equipos
- **Eventos:** StaffAssigned, ShiftCreated

### 7. Organization Context (`core/organization/`)
- **Entidades:** Organization, Hospital
- **Comportamiento:** Estructura organizacional
- **Eventos:** OrganizationCreated

### 8. Department Context (`core/department/`)
- **Entidades:** Department, Unit, Budget
- **Comportamiento:** Gestión de departamentos
- **Eventos:** DepartmentCreated

### 9. Inventory Context (`core/inventory/`)
- **Entidades:** InventoryItem, Warehouse, Supplier, PurchaseOrder
- **Comportamiento:** Control de inventario, órdenes de compra
- **Eventos:** ItemRestocked, OrderPlaced

### 10. Asset Context (`core/asset/`)
- **Entidades:** Asset, Contract, Warranty
- **Comportamiento:** Gestión de activos, contratos
- **Eventos:** AssetAcquired, ContractExpiring

---

## 🎯 Fases del Proyecto

### FASE 1: Foundation & Platform ✅ COMPLETO
**Épicas: EPIC 0-10**

| Épica | Descripción |
|-------|-------------|
| EPIC 0 | Arquitectura, ADRs, DDD, Roadmap |
| EPIC 1 | Infraestructura, Docker, CI/CD |
| EPIC 2 | Shared Kernel |
| EPIC 3 | Device Context |
| EPIC 4 | Incident Context |
| EPIC 5 | Recommendation Context |
| EPIC 6 | Knowledge Context |
| EPIC 7 | APIs base, Contratos |
| EPIC 8 | Seguridad, Persistencia |
| EPIC 9 | Consolidación, Documentación |
| EPIC 10 | Enterprise Release |

### Resultado de FASE 1
- ✅ Arquitectura empresarial
- ✅ 10 Bounded Contexts implementados
- ✅ PostgreSQL + Redis + RabbitMQ
- ✅ Docker + Kubernetes
- ✅ CI/CD con GitHub Actions
- ✅ 29+ API endpoints
- ✅ Unit of Work & Outbox Pattern
- ✅ Health Checks
- ✅ Multi-tenant support

---

## 🔌 Integraciones

### FHIR (HL7 FHIR R4)
```python
# apps/api/app/integrations/fhir_client.py
class FHIRClient:
    async def get_patient(self, patient_id: str) -> Patient
    async def search_resources(self, resource_type: str, params: dict)
```

### HL7 v2
```python
# apps/api/app/integrations/hl7_listener.py
class HL7Listener:
    async def process_message(self, message: HL7Message)
```

### MQTT (IoT)
```python
# apps/api/app/integrations/mqtt_client.py
class MQTTClient:
    async def publish_telemetry(self, device_id: str, data: dict)
```

### DICOM
```python
# apps/api/app/integrations/dicom_client.py
class DICOMClient:
    async def query_studies(self, query: DICOMQuery)
```

---

## 📡 API Endpoints (29+ endpoints)

### Devices
- `POST /api/v1/devices` - Registrar dispositivo
- `GET /api/v1/devices` - Listar dispositivos
- `GET /api/v1/devices/{id}` - Obtener dispositivo
- `PUT /api/v1/devices/{id}` - Actualizar dispositivo
- `DELETE /api/v1/devices/{id}` - Eliminar dispositivo
- `POST /api/v1/devices/{id}/transfer` - Transferir
- `POST /api/v1/devices/{id}/maintenance` - Programar mantenimiento
- `POST /api/v1/devices/{id}/calibrate` - Calibrar
- `POST /api/v1/devices/{id}/decommission` - Descomisionar

### Incidents
- `POST /api/v1/incidents` - Crear incidente
- `GET /api/v1/incidents` - Listar incidentes
- `GET /api/v1/incidents/{id}` - Obtener incidente
- `PUT /api/v1/incidents/{id}` - Actualizar incidente
- `POST /api/v1/incidents/{id}/escalate` - Escalar

### Knowledge
- `POST /api/v1/knowledge` - Crear artículo
- `GET /api/v1/knowledge` - Buscar artículos
- `GET /api/v1/knowledge/{id}` - Obtener artículo
- `PUT /api/v1/knowledge/{id}` - Actualizar artículo

### Capacity
- `POST /api/v1/capacity/campus` - Crear campus
- `GET /api/v1/capacity/campus/{id}` - Obtener campus
- `GET /api/v1/capacity/beds` - Listar camas

### Staffing
- `POST /api/v1/staffing/staff` - Crear staff
- `GET /api/v1/staffing/staff` - Listar staff
- `POST /api/v1/staffing/shifts` - Crear turno

---

## 🔐 Seguridad

### Autenticación
- JWT tokens
- Supabase Auth integration

### Autorización
- RBAC (Role-Based Access Control)
- Tenant isolation con RLS (Row-Level Security)

### Auditoría
- Event logging para todas las operaciones
- Audit trails con timestamps

---

## 📊 Patrones de Diseño

### Unit of Work
```python
class UnitOfWork:
    async def __aenter__(self) -> UnitOfWork
    async def __aexit__(self, exc_type, exc_val, exc_tb)
    async def commit(self)
    async def rollback(self)
```

### Repository Pattern
```python
class DeviceRepository(Protocol):
    async def save(self, device: Device) -> Device
    async def get_by_id(self, id: DeviceId) -> Device | None
    async def list(self, filters: DeviceFilters) -> list[Device]
```

### Outbox Pattern
```python
# Garantiza consistencia eventual
# Outbox table → Message Broker → Event handlers
```

---

## 🚀 Cómo Iniciar

```bash
# 1. Clonar
git clone https://github.com/Tiago1203/EREN.git
cd EREN

# 2. Variables de entorno
cp apps/api/.env.example apps/api/.env

# 3. Levantar con Docker
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/health
```

---

## 📈 Métricas y Monitoreo

- **OpenTelemetry** para tracing distribuido
- **Health Checks** en `/health`, `/ready`, `/live`
- **Prometheus metrics** en `/metrics`
- **Structured logging** con correlación de request IDs

---

## 🎓 Glosario (Ubiquitous Language)

| Término | Definición |
|---------|------------|
| **Device** | Equipo médico o de soporte vital |
| **Incident** | Evento que requiere atención de ingeniería |
| **Work Order** | Orden de trabajo programada |
| **Tenant** | Organización/hospital cliente |
| **Bounded Context** | Límite de dominio con responsabilidad clara |
| **Aggregate** | Grupo de entidades tratadas como unidad |
| **Value Object** | Objeto inmutable definido por sus atributos |
| **Domain Event** | Evento que representa un cambio de negocio |
| **Outbox Pattern** | Patrón para consistencia eventual |

---

## 📚 Recursos

- [docs/phases/PHASE_1/README.md](./docs/phases/PHASE_1/README.md) - Documentación de FASE 1
- [docs/architecture/](./docs/architecture/) - Documentos de arquitectura
- [docs/phases/PHASE_1/adr/](./docs/phases/PHASE_1/adr/) - Architecture Decision Records

---

*Última actualización: 2026-07-20*
