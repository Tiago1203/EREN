# Arquitectura Objetivo (TO-BE) — EREN

**Versión:** 1.0
**Fecha:** 2026-08-03
**Basado en:** `docs/architecture-validation.md`

---

## 1. PRINCIPIOS RECTORES

La arquitectura objetivo se fundamenta en 5 principios innegociables:

1. **Dependency Rule unilateral:** Código externo puede depender de código interno, nunca al revés. Todo `core/` es interno. Todo `apps/` es externo. `apps/` puede importar `core/`, nunca `core/` importa `apps/`.
2. **Un Composition Root por proceso:** Una sola ubicación donde se construyen todas las dependencias. En EREN: `apps/api/app/main.py`.
3. **Un tipo de puerto por bounded context:** Cada PHASE define SUS propios puertos. `apps/api` consume esos puertos a través de adapters. No hay puertos duplicados.
4. **Infraestructura en la capa más externa:** Container, bootstrap, lifecycle, observability, messaging son responsabilidad de `apps/api`, no de `core/`.
5. **Infraestructura de PHASE_1 movida a apps/api:** `core/PHASE_1/` contiene dominio puro. Su infraestructura (container, boot, lifecycle, events) pertenece a `apps/api/infrastructure/`.

---

## 2. ESTRUCTURA OBJETIVO

### 2.1 Vista de directorios

```
/workspace/project/EREN/
├── apps/
│   ├── api/
│   │   └── app/
│   │       ├── main.py                    # Composition Root
│   │       ├── config/                    # Configuración
│   │       ├── domain/                    # Ports (interfaces)
│   │       │   ├── device/repository.py   # Puerto: DeviceRepository (ABC)
│   │       │   ├── incident/repository.py
│   │       │   ├── work_order/repository.py
│   │       │   └── recommendation/repository.py
│   │       ├── application/               # Casos de uso
│   │       │   ├── device/
│   │       │   ├── incident/
│   │       │   └── work_order/
│   │       ├── infrastructure/            # Adapters
│   │       │   ├── repositories/         # Implementaciones SQLAlchemy
│   │       │   │   ├── device.py
│   │       │   │   ├── incident.py
│   │       │   │   └── work_order.py
│   │       │   ├── messaging/            # RabbitMQ, Outbox
│   │       │   ├── observability/        # Logging, Tracing
│   │       │   ├── container/            # DI Container
│   │       │   └── bootstrap/            # Bootstrap
│   │       ├── presentation/            # Routers
│   │       └── __init__.py
│   └── web/                             # Siguiente fase
│
├── core/                                # Dominio puro — NO infraestructura
│   ├── PHASE_1/
│   │   ├── domain/                      # ✅ Dominio puro
│   │   │   ├── device/                 # AggregateRoot + VOs + Puerto (ABC)
│   │   │   ├── incident/
│   │   │   └── knowledge/
│   │   └── infrastructure/              # ⚠️ ELIMINAR — moverse a apps/api/infrastructure/
│   │       ├── container/              # ❌ Eliminar (ir a apps/api/infrastructure/container/)
│   │       ├── boot/                   # ❌ Eliminar (ir a apps/api/infrastructure/bootstrap/)
│   │       ├── lifecycle/              # ❌ Eliminar (ir a apps/api/infrastructure/)
│   │       ├── diagnostics/            # ❌ Eliminar
│   │       ├── events/                # ❌ Eliminar
│   │       └── contracts/              # ✅ MANTENER — son PUERTOS (contracts = interfaces)
│   │
│   ├── PHASE_2/                        # Dominio AI
│   │   └── domain/                    # ✅ Dominio puro (mover todo aquí)
│   │       ├── kernel/
│   │       ├── memory/
│   │       ├── rag/
│   │       └── contracts/             # Puertos de IA
│   │
│   ├── PHASE_3/                        # Dominio clínico
│   │   ├── domain/
│   │   │   ├── recommendation/        # AggregateRoot + Puerto
│   │   │   ├── reasoning/
│   │   │   └── evidence/
│   │   └── infrastructure/            # ❌ Eliminar
│   │
│   ├── PHASE_4/                        # Dominio Knowledge Infrastructure
│   │   ├── domain/
│   │   └── infrastructure/            # ❌ Eliminar
│   │
│   ├── PHASE_5/                        # Dominio Multi-Agent
│   │   ├── domain/
│   │   └── infrastructure/            # ❌ Eliminar
│   │
│   └── PHASE_7/                        # Dominio Enterprise
│       ├── domain/
│       │   ├── audit/
│       │   ├── compliance/
│       │   └── tenant/
│       └── infrastructure/            # ❌ Eliminar
│
├── packages/
│   ├── sdk/                           # Cliente API tipado para web/mobile
│   └── shared/                        # Tipos compartidos (Published Language)
│
└── tests/
    ├── unit/
    ├── integration/
    └── contract/                      # ✅ NUEVO — contract tests
```

---

## 3. COMPOSITION ROOT — DISEÑO

### 3.1 Arquitectura del Container

```python
# apps/api/app/main.py (Composition Root)

from app.infrastructure.container import Container, DependencyGraph
from app.infrastructure.bootstrap import Bootstrap
from app.infrastructure.lifecycle import LifecycleManager
from app.infrastructure.observability import configure_logging, setup_instrumentation
from app.infrastructure.messaging import start_outbox_worker
from app.presentation.routers import api_router


def create_container() -> Container:
    """Composition Root — construye todo el grafo de dependencias."""
    graph = DependencyGraph()

    # Infrastructure
    graph.register_factory(AsyncEngine, lambda c: create_async_engine())
    graph.register_factory(AsyncSession, lambda c: create_session_factory(c.get(AsyncEngine)))
    graph.register_factory(RabbitMQConnection, lambda c: connect_rabbitmq())
    graph.register_factory(EventBus, lambda c: RabbitMQEventBus(c.get(RabbitMQConnection)))
    graph.register_factory(OutboxProcessor, lambda c: TransactionalOutbox(c.get(AsyncSession)))

    # Repositories (adapters)
    graph.register_factory(
        DeviceRepository,
        lambda c: SQLAlchemyDeviceRepository(c.get(AsyncSession)),
        lifetime=Lifetime.SCOPED,
    )
    graph.register_factory(
        IncidentRepository,
        lambda c: SQLAlchemyIncidentRepository(c.get(AsyncSession)),
        lifetime=Lifetime.SCOPED,
    )
    graph.register_factory(
        KnowledgeRepository,
        lambda c: SQLAlchemyKnowledgeRepository(c.get(AsyncSession)),
        lifetime=Lifetime.SCOPED,
    )
    graph.register_factory(
        RecommendationRepository,
        lambda c: SQLAlchemyRecommendationRepository(c.get(AsyncSession)),
        lifetime=Lifetime.SCOPED,
    )

    # Application Services
    graph.register_factory(
        DeviceService,
        lambda c: DeviceService(
            repository=c.get(DeviceRepository),
            event_bus=c.get(EventBus),
            outbox=c.get(OutboxProcessor),
        ),
        lifetime=Lifetime.SCOPED,
    )

    # PHASE_2 (AI Kernel) — si se activa
    if settings.ai_enabled:
        graph.register_singleton(CognitiveKernel, lambda c: create_cognitive_kernel(c))

    return Container(graph)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    container = create_container()

    # Bootstrap
    bootstrap = Bootstrap(container)
    await bootstrap.initialize()

    # Observability
    configure_logging()
    if settings.otel_endpoint:
        setup_instrumentation(app)

    # Start background workers
    outbox_task = asyncio.create_task(container.get(OutboxProcessor).run())

    yield

    # Shutdown
    await container.get(LifecycleManager).shutdown()
    outbox_task.cancel()
    await container.dispose()
```

### 3.2 Beneficios del Composition Root centralizado

| Aspecto | Antes | Después |
|---|---|---|
| Resolución de dependencias | Manual en cada `Depends()` | Un lugar |
| testing | Mock en cada test | Reemplazar container |
| Agregar nueva dependencia | Modificar N routers | Modificar `create_container()` |
| Ciclo de vida | Desconocido | Configurado por lifetime |
| Lazy initialization | No | Solo lo que se usa se construye |

---

## 4. CLEAN ARCHITECTURE — DISEÑO OBJETIVO

### 4.1 Dependency Rule

```
apps/web
    ↓ (HTTP)
apps/api
    ↓ (injects)
domain/ports/           ← contracts/interfaces (PUERTOS)
    ↑ (implemented by)
infrastructure/adapters/ ← implementaciones concretas (ADAPTADORES)
    ↑ (uses)
core/PHASE_1/           ← dominio puro (ENTIDADES, VOs, SERVICES)
    ↑ (imports from)
core/PHASE_2/           ← dominio puro AI
    ↑ (imports from)
core/PHASE_3/           ← dominio puro clínico
```

**Regla:** Toda flecha apunta hacia `core/`. Nunca de `core/` hacia `apps/`.

### 4.2 Capa de dominio vs aplicación

| Capa | Contenido | Ubicación |
|---|---|---|
| **Dominio** (core/) | Entities, VOs, AggregateRoots, Domain Services, Repository Interfaces | `core/PHASE_*/domain/` |
| **Aplicación** (apps/api/) | Casos de uso, Commands, Queries, Application Services | `apps/api/app/application/` |
| **Infraestructura** (apps/api/) | Repositories, EventBus, Cache, External APIs, DI Container | `apps/api/app/infrastructure/` |
| **Presentación** (apps/api/) | Routers, Schemas, Middleware | `apps/api/app/presentation/` |

---

## 5. DDD — BOUNDED CONTEXTS

### 5.1 Contextos identificados

| BC | PHASE | Subdominios | Agregados | Integración |
|---|---|---|---|---|
| Device Management | PHASE_1 | Device, Incident | Device, EngineeringIncident | apps/api → PHASE_1 |
| Knowledge | PHASE_1 | Knowledge, Article | KnowledgeArticle | apps/api → PHASE_1 |
| Clinical Intelligence | PHASE_3 | Recommendation, Reasoning, Evidence | AIRecommendation | apps/api → PHASE_3 |
| AI Kernel | PHASE_2 | Kernel, Memory, RAG, Reasoning | CognitiveSession | PHASE_2 → PHASE_1 (downstream) |
| Knowledge Infrastructure | PHASE_4 | Vector Indexing, RAG, Quality | — | PHASE_4 → PHASE_2, 3 (downstream) |
| Multi-Agent | PHASE_5 | Agent, Consensus | AgentTask | PHASE_5 → PHASE_2, 3, 4 (downstream) |
| Enterprise | PHASE_7 | Audit, Compliance, Tenant | AuditEntry | apps/api → PHASE_7 |
| Organization | PHASE_1 | Organization, Department, Staff | Organization, Department | apps/api → PHASE_1 |

### 5.2 Context Mapping

```
PHASE_7 (Enterprise)
    └── PHASE_1 (Device Management)
        └── PHASE_3 (Clinical Intelligence)
            └── PHASE_2 (AI Kernel)
                └── PHASE_4 (Knowledge Infrastructure)
                    └── PHASE_5 (Multi-Agent)

apps/api ←→ PHASE_1 (device, knowledge, organization)
apps/api ←→ PHASE_3 (recommendation)
apps/api ←→ PHASE_7 (audit, compliance)
```

**Relaciones:**
- **Conformista** entre PHASE_2, 4, 5 y PHASE_1: PHASE_1 define los puertos, las demás los consumen
- **下游 (Downstream)** de PHASE_2, 4, 5 respecto a PHASE_1:usan el dominio de PHASE_1 pero no lo modifican

---

## 6. HEXAGONAL ARCHITECTURE — PUERTOS Y ADAPTADORES

### 6.1 Puertos de entrada (Driving Ports)

Definidos como interfaces en `core/`:

```python
# core/PHASE_1/domain/device/domain/repositories/device_repository.py
class DeviceRepository(ABC):
    """Puerto — Persistence para Device."""

    @abstractmethod
    async def save(self, device: Device) -> Result[Device, str]: ...

    @abstractmethod
    async def get_by_id(self, device_id: DeviceId) -> Result[Device | None, str]: ...
```

### 6.2 Puertos de salida (Driven Ports)

```python
# core/PHASE_1/infrastructure/contracts/security/authentication.py
class AuthenticationProvider(ABC):
    """Puerto — Authentication."""

    @abstractmethod
    async def authenticate(self, credentials: Credentials) -> Result[Principal, str]: ...


# core/PHASE_1/infrastructure/contracts/security/audit.py
class AuditProvider(ABC):
    """Puerto — Audit."""

    @abstractmethod
    async def log(self, entry: AuditEntry) -> Result[None, str]: ...
```

### 6.3 Adaptadores primarios (Driving Adapters)

```python
# apps/api/presentation/routers/device.py
@router.post("/devices")
async def create_device(
    service: DeviceService = Depends(get_device_service),
    body: DeviceCreate,
) -> DeviceResponse:
    result = await service.register_device(...)
    return result.unwrap()
```

### 6.4 Adaptadores secundarios (Driven Adapters)

```python
# apps/api/infrastructure/repositories/device.py
class SQLAlchemyDeviceRepository(DeviceRepository):
    """Adaptador — SQLAlchemy para Device."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, device: Device) -> Result[Device, str]:
        model = DeviceModel.from_domain(device)
        self._session.add(model)
        await self._session.flush()
        return Ok(model.to_domain())
```

### 6.5 Contract Tests (NUEVO)

```python
# tests/contract/test_device_repository_contract.py
import pytest
from core.PHASE_1.domain.device.domain.repositories import DeviceRepository


class TestDeviceRepositoryContract:
    """Contract test — verifica que todo adapter cumple el contrato."""

    @pytest.fixture
    @abstractmethod
    def repository(self) -> DeviceRepository:
        """Implementado por cada adapter test subclass."""
        ...

    async def test_save_returns_result(self, repository: DeviceRepository):
        device = Device.create(...)
        result = await repository.save(device)
        assert result.is_ok()

    async def test_get_by_id_returns_none_for_missing(
        self, repository: DeviceRepository
    ):
        result = await repository.get_by_id(DeviceId.generate())
        assert result.unwrap() is None
```

---

## 7. EVENT-DRIVEN ARCHITECTURE — DISEÑO OBJETIVO

### 7.1 Event Bus con Transactional Outbox

```
Domain Service
    ↓ DomainEvent
TransactionalOutbox
    ↓ (commit transaction)
Outbox Table (DB)
    ↓ (async polling)
Outbox Worker
    ↓ publish_event()
RabbitMQ Exchange
    ↓ (fanout)
Queue: domain-events    ← Consumer 1
Queue: analytics        ← Consumer 2
```

### 7.2 Schema Registry

```python
# apps/api/infrastructure/messaging/schemas/
events/
    ├── device_registered.py    # Schema para DeviceRegistered
    ├── incident_created.py    # Schema para IncidentCreated
    └── recommendation_ready.py  # Schema para RecommendationReady
```

```python
# apps/api/infrastructure/messaging/schemas/device_registered.py
from pydantic import BaseModel


class DeviceRegisteredEvent(BaseModel):
    """Schema para DeviceRegistered — publicado en RabbitMQ."""
    event_type: Literal["device.registered"] = "device.registered"
    device_id: str
    tenant_id: str
    timestamp: datetime
    version: Literal["1.0"] = "1.0"

    class Config:
        frozen = True
```

### 7.3 Consumer ejemplo

```python
# apps/api/infrastructure/messaging/consumers/device_consumer.py
class DeviceEventConsumer:
    """Consume eventos de dispositivo desde RabbitMQ."""

    async def handle(self, message: bytes) -> None:
        event = DeviceRegisteredEvent.model_validate_json(message)
        # Reaccionar al evento
        await self._send_notification(event)
        await self._update_analytics(event)
```

---

## 8. FRONTEND — ARQUITECTURA OBJETIVO

### 8.1 Eliminación de acceso directo a Supabase

```
ANTES:
    Web → Supabase (directo)

DESPUÉS:
    Web → packages/sdk → apps/api (REST/GraphQL) → apps/api SDK
```

### 8.2 SDK Cliente

```typescript
// packages/sdk/src/client.ts
export class ErenClient {
  constructor(private baseUrl: string) {}

  async getDevices(params: DeviceQueryParams): Promise<Device[]> {
    const res = await fetch(`${this.baseUrl}/v1/devices?${params}`);
    return res.json();
  }
}

// packages/sdk/src/services/device.service.ts
export class DeviceService {
  constructor(private client: ErenClient) {}

  async list(params: DeviceQueryParams): Promise<Device[]> {
    return this.client.getDevices(params);
  }

  async create(data: CreateDeviceDTO): Promise<Device> {
    return this.client.postDevices(data);
  }
}
```

### 8.3 Migración de frontend

| Fase | Locaciones | Riesgo |
|---|---|---|
| 1 | `lib/queries.ts` → SDK calls | Bajo |
| 2 | `modules/equipos/` → SDK calls | Medio |
| 3 | `AuthProvider.tsx` → SDK calls | Alto |
| 4 | `lib/storage.ts` → API signed URLs | Alto |

---

## 9. VENTAJAS Y DESVENTAJAS POR DECISIÓN

### 9.1 Mover infraestructura de core/ a apps/api/

| Aspecto | Ventaja | Desventaja |
|---|---|---|
| Clean Architecture | Cumple Dependency Rule estrictamente | Requiere migrar 50+ archivos |
| Testing | Dominio puro testable sin infraestructura | Necesita mock del container |
| Microservicios | Si un PHASE se convierte en servicio, su infraestructura va con él | PHASE_2, 4, 5 también necesitan mover infraestructura |
| Tiempo | — | 2-3 semanas de trabajo |

### 9.2 Unificar puertos (eliminar duplicación)

| Aspecto | Ventaja | Desventaja |
|---|---|---|
| Consistencia | Un solo contrato por BC | Requiere reescribir 4 repositorios de apps/api |
| Type safety | ABC con Result[T] es más robusto | Protocol con primitivos es más flexible |
| Compatibilidad PHASE_4, 5 | Usan los mismos puertos | Requiere coordinar cambios en PHASE_4, 5 |
| Tiempo | — | 1-2 semanas |

### 9.3 Composition Root centralizado

| Aspecto | Ventaja | Desventaja |
|---|---|---|
| Mantenibilidad | Una ubicación para todas las dependencias | Requiere aprender el container |
| Testing | Reemplazar container por test container | Puede ser overkill para proyecto pequeño |
| Performance | Lazy loading por defecto | — |
| Tiempo | — | 3-5 días |

---

## 10. PRINCIPIOS MEJORADOS POR CADA CAMBIO

| Cambio | Principios mejorados |
|---|---|
| Mover infraestructura de core/ → apps/api/ | **Dependency Rule**, **Architecture Boundaries**, **Independent Deployability** |
| Unificar puertos (ABC en core/) | **Interface Segregation**, **Liskov Substitution**, **Single Responsibility** |
| Composition Root centralizado | **Dependency Inversion**, **Hollywood Principle**, **IoC** |
| Contract tests | **Verification**, **Boundary Compliance**, **Contract Testing** |
| SDK cliente | **Coupling Reduction**, **Encapsulation**, **API as a Product** |
| Transactional Outbox + RabbitMQ | **Eventual Consistency**, **Reliability**, **Event Sourcing Readiness** |

---

## 11. MÓDULOS ELIMINADOS EN TO-BE

| Módulo | Ubicación actual | Razón de eliminación |
|---|---|---|
| DI Container dead | `core/PHASE_1/infrastructure/container/` | Nunca usado; redundante |
| PHASE_2 Runtime dead | `core/PHASE_2/runtime/` | Nunca usado |
| PHASE_2/ai/di vacío | `core/PHASE_2/ai/di/` | Solo `__init__.py` |
| LEGACY | `core/LEGACY/` | Completamente aislado |
| PHASE_1/diagnostic vacío | `core/PHASE_1/infrastructure/diagnostic/` | Carpeta vacía |
| PHASE_1/diagnostics/ | `core/PHASE_1/infrastructure/diagnostics/` | Mover funcionalidad a apps/api |
| RepositoryImpl dead | `apps/api/app/infrastructure/repositories/*Impl` | Nunca instanciados |
| UnitOfWork dead | `apps/api/app/infrastructure/unit_of_work.py` | Nunca usado |
| CircuitBreaker dead | `apps/api/app/providers/circuit_breaker.py` | Nunca usado |
| Events duplicados | `apps/api/app/events/` | Mover a infrastructure/messaging/ |

---

*Documento de arquitectura objetivo. No modifica código. Solo describe el estado deseado.*
