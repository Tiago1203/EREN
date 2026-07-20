# AUDITORÍA ARQUITECTÓNICA - FASE 1: DOMAIN AI INTEGRATION

*Versión 1.0 - 2026-07-20*

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Análisis de Módulos](#2-análisis-de-módulos)
3. [Problemas de Acoplamiento](#3-problemas-de-acoplamiento)
4. [Diseño de Nueva Capa](#4-diseño-de-nueva-capa)
5. [Eventos Públicos para IA](#5-eventos-públicos-para-ia)
6. [DTOs para Desacoplamiento](#6-dtos-para-desacoplamiento)
7. [Interfaces a Mover a Shared](#7-interfaces-a-mover-a-shared)
8. [Componentes No Accesibles por AI](#8-componentes-no-accesibles-por-ai)
9. [Dependencias Circulares](#9-dependencias-circulares)
10. [Arquitectura Propuesta](#10-arquitectura-propuesta)
11. [Riesgos Identificados](#11-riesgos-identificados)
12. [ADRs Necesarios](#12-adrs-necesarios)
13. [Plan de Migración](#13-plan-de-migración)

---

## 1. RESUMEN EJECUTIVO

### Estado Actual

| Aspecto | Estado | Observación |
|---------|--------|-------------|
| **Repositorios** | ✅ Buenos | Interfaces ABC bien definidas |
| **Servicios de Query** | ❌ No existen | Solo repositorios |
| **Servicios de Comando** | ❌ No existen | Solo dominio |
| **DTOs para AI** | ❌ No existen | Entidades directamente expuestas |
| **Eventos para AI** | ⚠️ Parcial | Algunos eventos definidos |
| **Contratos compartidos** | ⚠️ Parcial | Solo BaseEntity y DomainEvent |

### Problemas Críticos Identificados

1. **AI Core accede directamente a repositorios** - Viola DDD
2. **No hay Query Services** - CQRS no implementado
3. **Entidades expuestas directamente** - Acoplamiento fuerte
4. **Eventos no disponibles para suscripción** - Sin pub/sub para AI
5. **No hay DTOs de dominio** - Estructuras de dominio filtran a AI

---

## 2. ANÁLISIS DE MÓDULOS

### 2.1 Device Context

#### Estructura Actual

```
core/device/
├── domain/
│   ├── entities/
│   │   └── device.py           # Device aggregate
│   ├── repositories/
│   │   └── device_repository.py # ABC interface
│   ├── services/
│   │   └── __init__.py        # Vacío
│   └── value_objects/
│       ├── device_status.py
│       └── __init__.py
└── infrastructure/
    └── repositories/
        └── device_repository_impl.py
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Repository Interface | ✅ | Bien definida con ABC |
| Entity | ✅ | AgregateRoot bien diseñado |
| Value Objects | ✅ | Completos |
| Domain Services | ❌ | No existen |
| Query Methods | ✅ | get_by_status, get_critical, get_needing_maintenance |
| **Acceso para AI** | ❌ | Repositorio directamente expuesto |

#### Problemas

1. No hay servicio de aplicación
2. Métodos de query dispersos en repositorio
3. Entidad Device expuesta directamente

---

### 2.2 Incident Context

#### Estructura Actual

```
core/incident/
├── domain/
│   ├── entities/
│   │   ├── incident.py          # EngineeringIncident aggregate
│   │   └── investigation.py    # Investigation entity
│   ├── repositories/
│   │   └── incident_repository.py
│   ├── work_order/
│   │   ├── work_order.py
│   │   └── repository.py
│   └── value_objects/
│       └── incident_status.py
└── __init__.py
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Repository Interface | ✅ | Completa con 8 métodos |
| WorkOrder Repository | ✅ | Interface separada |
| Entity | ✅ | Estado machine implementado |
| **Acceso para AI** | ❌ | Repositorio directamente expuesto |

#### Problemas

1. No hay InvestigationQueryService
2. WorkOrderRepository aislada
3. Incident incluye lógica de negocio en entidad

---

### 2.3 Knowledge Context

#### Estructura Actual

```
core/knowledge/
├── domain/
│   ├── entities/
│   │   └── knowledge_article.py
│   ├── repositories/
│   │   └── knowledge_repository.py
│   └── services/
│       └── knowledge_service.py
├── engine.py
├── knowledge_engine.py
├── registry.py
├── router.py
├── types.py
└── models.py
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Repository Interface | ✅ | 12 métodos de query |
| KnowledgeService | ⚠️ | Existe pero no es fachada |
| Search Methods | ✅ | search_by_keywords, get_related_articles |
| **Para AI** | ⚠️ | Repository expuesto, no hay fachada |

#### Problemas

1. Múltiples módulos de nivel superior (engine, router, registry)
2. KnowledgeService no es fachada estándar
3. No hay DTOs de búsqueda

---

### 2.4 Recommendation Context

#### Estructura Actual

```
core/recommendation/
├── domain/
│   ├── entities/
│   │   └── recommendation.py  # AIRecommendation
│   ├── repositories/
│   │   └── recommendation_repository.py
│   ├── services/
│   │   └── recommendation_service.py
│   └── value_objects/
│       └── recommendation_status.py
└── __init__.py
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Repository Interface | ✅ | 8 métodos |
| Domain Service | ⚠️ | recommendation_service.py existe |
| **Para AI** | ⚠️ | No hay fachada clara |

#### Problemas

1. Domain Service mezclado con lógica
2. No hay separación CQRS
3. AIRecommendation expuesta directamente

---

### 2.5 Clinical Context (CDSS)

#### Estructura Actual

```
core/clinical/
├── cdss/
│   └── engine.py              # CDSSEngine
├── diagnosis/
├── predictive/
└── troubleshooting/
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| CDSSEngine | ✅ | Motor bien diseñado |
| Diagnosis | ✅ | Implementado |
| Predictive | ✅ | Implementado |
| Troubleshooting | ✅ | Implementado |
| **Interfaz AI** | ❌ | Solo engine, sin fachada |

#### Problemas

1. CDSSEngine no tiene interfaz abstracta
2. No hay clínica como QueryService
3. Resultados son objetos internos, no DTOs

---

### 2.6 Shared Kernel

#### Estructura Actual

```
core/shared/
├── entities/
│   └── base.py               # BaseEntity, AggregateRoot
├── errors/
├── events/
│   └── domain.py            # DomainEvent
├── primitives/
│   └── entity_id.py         # EntityId types
└── value_objects/
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| BaseEntity | ✅ | Bien diseñado |
| AggregateRoot | ✅ | Hereda de BaseEntity |
| DomainEvent | ✅ | Base para eventos |
| EntityId Types | ✅ | Typed IDs |

#### Problemas

1. No hay interfaces de Repository en Shared
2. No hay interfaces de QueryService
3. FASE 2 no reutiliza BaseEntity

---

### 2.7 Events Module

#### Estructura Actual

```
core/events/
├── bus.py                   # EventBus, EventPublisher, EventSubscriber
├── publisher.py
├── subscriber.py
├── models.py
└── exceptions.py
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| EventBus | ✅ | Bien implementado |
| EventPublisher | ✅ | Interfaz para productores |
| EventSubscriber | ✅ | Interfaz para consumidores |
| **Para AI** | ⚠️ | No hay suscriptor pre-configurado |

#### Problemas

1. AI no puede suscribirse fácilmente
2. No hay EventQueryService
3. Eventos de dominio dispersos en contextos

---

### 2.8 Context Module (Blackboard)

#### Estructura Actual

```
core/context/
├── blackboard.py
├── cognitive_context.py
├── context_history.py
├── context_manager.py
├── context_snapshot.py
├── context_types.py
└── engine/
```

#### Evaluación

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Blackboard | ✅ | Sistema completo |
| CognitiveContext | ✅ | Implementado |
| **Para AI** | ⚠️ | FASE 2 tiene su propio context_builder |

#### Problemas

1. FASE 2 no usa este módulo
2. Dos sistemas de contexto
3. No hay puente entre ellos

---

### 2.9 Repositorios - Evaluación Centralizada

| Módulo | Repository | Query Methods | Command Methods | AI Accessible |
|--------|------------|---------------|-----------------|---------------|
| Device | ✅ | 7 | 1 | ❌ Direct |
| Incident | ✅ | 6 | 2 | ❌ Direct |
| Knowledge | ✅ | 12 | 4 | ❌ Direct |
| Recommendation | ✅ | 8 | 3 | ❌ Direct |
| WorkOrder | ✅ | 5 | 3 | ❌ Direct |
| Capacity | ✅ | 6 | 2 | ❌ Direct |
| Staffing | ✅ | 4 | 2 | ❌ Direct |
| Organization | ✅ | 3 | 2 | ❌ Direct |
| Department | ✅ | 3 | 2 | ❌ Direct |
| Inventory | ✅ | 5 | 3 | ❌ Direct |
| Asset | ✅ | 4 | 2 | ❌ Direct |

---

## 3. PROBLEMAS DE ACOPLAMIENTO

### 3.1 Repositorios Accesibles Externamente

| Repositorio | Problema | Impacto |
|-------------|----------|---------|
| DeviceRepository | Expuesto directamente | AI puede modificar estado |
| IncidentRepository | Sin fachada | AI viola encapsulamiento |
| KnowledgeRepository | Sin QueryService | Queries en dominio |
| RecommendationRepository | Mezclado con servicio | CQRS violado |

### 3.2 Servicios que Deberían ser Query Services

| Servicio Actual | Debería Ser | Razón |
|-----------------|-------------|-------|
| DeviceRepository.get_by_status() | DeviceQueryService | Read-only |
| IncidentRepository.get_open_incidents() | IncidentQueryService | Read-only |
| KnowledgeRepository.search_by_keywords() | KnowledgeQueryService | Read-only |
| RecommendationRepository.get_high_confidence() | RecommendationQueryService | Read-only |

### 3.3 Acoplamientos Circulares Detectados

```
core/knowledge/
    │
    ├──▶ knowledge_engine.py
    │         │
    │         ▼
    │    knowledge_router.py
    │         │
    │         ▼
    │    registry.py ◀──┘
    │
    └──▶ models.py
              │
              ▼
         interfaces.py
              │
              ▼
         permissions.py
```

### 3.4 Componentes Muy Acoplados

| Componente | Acoplado a | Problema |
|------------|------------|----------|
| CDSSEngine | Ninguno | Aislado pero sin fachada |
| KnowledgeEngine | KnowledgeRouter | Dependencia interna fuerte |
| KnowledgeRegistry | KnowledgeService | Acoplamiento bidireccional |

---

## 4. DISEÑO DE NUEVA CAPA

### 4.1 Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AI CORE (FASE 2)                                          │
│                                                                                      │
│  AICoreController                                                                   │
│       │                                                                              │
│       ▼                                                                              │
│  ToolOrchestrator                                                                   │
│       │                                                                              │
│       ▼                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │              DOMAIN TOOLS (Herramientas AI que acceden al dominio)          │    │
│  │                                                                              │    │
│  │  - get_device(id) ──────────▶ DeviceQueryService                           │    │
│  │  - search_knowledge(q) ─────▶ KnowledgeQueryService                       │    │
│  │  - get_incident(id) ────────▶ IncidentQueryService                        │    │
│  │  - get_cdss_recommendations──▶ CDSSService                                 │    │
│  │                                                                              │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                              │
│                                        ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │           CORE/APPLICATION/SERVICES (EPIC 11)                               │    │
│  │                                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │    │
│  │  │                      QUERY SERVICES (CQRS Read)                       │  │    │
│  │  │                                                                     │  │    │
│  │  │  DeviceQueryService          IncidentQueryService                    │  │    │
│  │  │  KnowledgeQueryService       RecommendationQueryService              │  │    │
│  │  │  WorkOrderQueryService      HospitalQueryService                     │  │    │
│  │  │  StaffQueryService          AssetQueryService                        │  │    │
│  │  │  InventoryQueryService                                             │  │    │
│  │  │                                                                     │  │    │
│  │  └─────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │    │
│  │  │                      COMMAND SERVICES (CQRS Write)                    │  │    │
│  │  │                                                                     │  │    │
│  │  │  DeviceCommandService        IncidentCommandService                  │  │    │
│  │  │  KnowledgeCommandService     RecommendationCommandService            │  │    │
│  │  │  WorkOrderCommandService     ClinicalCommandService                  │  │    │
│  │  │                                                                     │  │    │
│  │  └─────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │    │
│  │  │                      DOMAIN SERVICES (AI-Ready)                       │  │    │
│  │  │                                                                     │  │    │
│  │  │  CDSSService                    RCAAnalysisService                  │  │    │
│  │  │  DiagnosisService              TroubleshootingService              │  │    │
│  │  │  PredictionService                                                  │  │    │
│  │  │                                                                     │  │    │
│  │  └─────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                              │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │    │
│  │  │                      EVENT SERVICES                                 │  │    │
│  │  │                                                                     │  │    │
│  │  │  EventQueryService              EventSubscriptionService            │  │    │
│  │  │                                                                     │  │    │
│  │  └─────────────────────────────────────────────────────────────────────┘  │    │
│  │                                                                              │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                              │
│                                        ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                        DOMAIN LAYER (Sin cambios)                          │    │
│  │                                                                              │    │
│  │  Entities │ Value Objects │ Domain Services │ Repository Interfaces         │    │
│  │                                                                              │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Query Services - Firma de Interfaces

```python
# core/application/services/query/device_query_service.py

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from core.shared import DeviceId, TenantId, Result

if TYPE_CHECKING:
    from core.application.dto import DeviceDTO, DeviceSummaryDTO

class IDeviceQueryService(ABC):
    """Interface for Device query operations (read-only)."""
    
    @abstractmethod
    async def get_device(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
    ) -> Result["DeviceDTO | None", str]:
        """Get device by ID."""
        ...
    
    @abstractmethod
    async def list_devices(
        self,
        tenant_id: TenantId,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list["DeviceDTO"], str]:
        """List all devices for tenant."""
        ...
    
    @abstractmethod
    async def get_by_status(
        self,
        tenant_id: TenantId,
        status: str,
        limit: int = 50,
    ) -> Result[list["DeviceDTO"], str]:
        """Get devices by status."""
        ...
    
    @abstractmethod
    async def get_critical_devices(
        self,
        tenant_id: TenantId,
    ) -> Result[list["DeviceDTO"], str]:
        """Get all critical devices."""
        ...
    
    @abstractmethod
    async def get_needing_maintenance(
        self,
        tenant_id: TenantId,
    ) -> Result[list["DeviceDTO"], str]:
        """Get devices that need maintenance."""
        ...
    
    @abstractmethod
    async def get_device_history(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
    ) -> Result[list[dict], str]:
        """Get device maintenance/incident history."""
        ...
```

### 4.3 Command Services - Firma de Interfaces

```python
# core/application/services/command/device_command_service.py

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from core.shared import DeviceId, TenantId, Result

if TYPE_CHECKING:
    from core.application.dto import DeviceDTO

@dataclass
class RegisterDeviceCommand:
    tenant_id: TenantId
    serial_number: str
    name: str
    device_type: str
    manufacturer_name: str
    manufacturer_model: str
    is_critical: bool = False

@dataclass
class TransferDeviceCommand:
    device_id: DeviceId
    tenant_id: TenantId
    new_location: dict

class IDeviceCommandService(ABC):
    """Interface for Device command operations (write)."""
    
    @abstractmethod
    async def register_device(
        self,
        command: RegisterDeviceCommand,
    ) -> Result["DeviceDTO", str]:
        """Register a new device."""
        ...
    
    @abstractmethod
    async def transfer_device(
        self,
        command: TransferDeviceCommand,
    ) -> Result["DeviceDTO", str]:
        """Transfer device to new location."""
        ...
    
    @abstractmethod
    async def schedule_maintenance(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        maintenance_date: datetime,
        description: str,
    ) -> Result["DeviceDTO", str]:
        """Schedule maintenance for device."""
        ...
```

### 4.4 Domain Services - Firma de Interfaces

```python
# core/application/services/domain/cdss_service.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.application.dto import CDSSRecommendationDTO, DeviceContextDTO

@dataclass
class CDSSQuery:
    device_type: str
    symptoms: list[str]
    device_context: "DeviceContextDTO | None" = None

@dataclass
class CDSSResultDTO:
    recommendations: list["CDSSRecommendationDTO"]
    confidence: float
    summary: str

class ICDSSService(ABC):
    """Interface for Clinical Decision Support System."""
    
    @abstractmethod
    async def get_recommendations(
        self,
        query: CDSSQuery,
    ) -> CDSSResultDTO:
        """Get clinical recommendations for a device/symptoms."""
        ...
    
    @abstractmethod
    async def analyze_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> CDSSResultDTO:
        """Analyze device and provide recommendations."""
        ...
```

---

## 5. EVENTOS PÚBLICOS PARA IA

### 5.1 Catálogo de Eventos

| Evento | Tipo | Para AI | Descripción |
|--------|------|---------|-------------|
| `DeviceRegistered` | Device | ✅ | Nuevo dispositivo registrado |
| `DeviceStatusChanged` | Device | ✅ | Cambio de estado |
| `DeviceLocationChanged` | Device | ✅ | Transferencia de ubicación |
| `DeviceMaintenanceScheduled` | Device | ✅ | Mantenimiento programado |
| `IncidentReported` | Incident | ✅ | Nuevo incidente reportado |
| `IncidentTriaged` | Incident | ✅ | Incidente triagiado |
| `IncidentEscalated` | Incident | ✅ | Incidente escalado |
| `IncidentResolved` | Incident | ✅ | Incidente resuelto |
| `WorkOrderCreated` | WorkOrder | ✅ | Nueva orden creada |
| `WorkOrderAssigned` | WorkOrder | ✅ | Orden asignada |
| `WorkOrderCompleted` | WorkOrder | ✅ | Orden completada |
| `RecommendationGenerated` | Recommendation | ✅ | Nueva recomendación |
| `RecommendationAccepted` | Recommendation | ✅ | Recomendación aceptada |
| `BedOccupied` | Capacity | ✅ | Cama ocupada |
| `BedAvailable` | Capacity | ✅ | Cama disponible |

### 5.2 Eventos No Accesibles para AI

| Evento | Tipo | Razón |
|--------|------|-------|
| `InternalErrorOccurred` | System | Solo para auditoría interna |
| `DatabaseConnectionFailed` | Infrastructure | Solo para DevOps |
| `SecurityBreachDetected` | Security | Solo para equipo de seguridad |
| `BackupCompleted` | Infrastructure | Solo para DevOps |

### 5.3 Interfaz de Eventos para AI

```python
# core/application/services/events/event_subscription_service.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Awaitable, Any

@dataclass
class AIEventSubscription:
    event_type: str
    callback: Callable[[dict], Awaitable[None]]
    filter: dict | None = None

class IEventSubscriptionService(ABC):
    """Interface for AI to subscribe to domain events."""
    
    @abstractmethod
    async def subscribe(
        self,
        subscription: AIEventSubscription,
    ) -> str:
        """Subscribe to events. Returns subscription ID."""
        ...
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        ...
    
    @abstractmethod
    async def get_subscriptions(
        self,
        tenant_id: str,
    ) -> list[AIEventSubscription]:
        """Get all active subscriptions for tenant."""
        ...
```

---

## 6. DTOs PARA DESACOPLAMIENTO

### 6.1 DTOs Necesarios

| DTO | Entidad Source | Propósito |
|-----|---------------|-----------|
| `DeviceDTO` | Device | Respuesta completa de dispositivo |
| `DeviceSummaryDTO` | Device | Lista resumida |
| `DeviceHistoryDTO` | Device | Historial para AI |
| `IncidentDTO` | EngineeringIncident | Respuesta completa |
| `IncidentSummaryDTO` | EngineeringIncident | Lista resumida |
| `IncidentTimelineDTO` | EngineeringIncident | Timeline para AI |
| `KnowledgeArticleDTO` | KnowledgeArticle | Artículo completo |
| `KnowledgeSearchResultDTO` | KnowledgeArticle | Resultado de búsqueda |
| `RecommendationDTO` | AIRecommendation | Recomendación completa |
| `WorkOrderDTO` | WorkOrder | Orden completa |
| `HospitalContextDTO` | Capacity | Contexto hospitalario |
| `CDSSRecommendationDTO` | Recommendation | Recomendación clínica |
| `RCAAnalysisDTO` | Analysis | Análisis de causa raíz |
| `DiagnosisDTO` | Diagnosis | Diagnóstico diferencial |

### 6.2 Ejemplo de DTO

```python
# core/application/dto/device_dtos.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class DeviceDTO:
    """DTO for Device - exposed to AI."""
    
    id: str
    serial_number: str
    name: str
    device_type: str
    status: str
    manufacturer: str
    model: str
    is_critical: bool
    location: dict
    last_maintenance: datetime | None
    next_maintenance: datetime | None
    created_at: datetime
    
    @classmethod
    def from_entity(cls, device: "Device") -> "DeviceDTO":
        """Create DTO from Device entity."""
        return cls(
            id=str(device.id),
            serial_number=str(device.serial_number),
            name=device.name,
            device_type=str(device.device_type),
            status=str(device.status),
            manufacturer=device.manufacturer.name,
            model=device.manufacturer.model,
            is_critical=device.is_critical,
            location=device.location.to_dict(),
            last_maintenance=device.last_maintenance,
            next_maintenance=device.next_maintenance,
            created_at=device.created_at,
        )

@dataclass(frozen=True)
class DeviceSummaryDTO:
    """Lightweight DTO for device lists."""
    
    id: str
    name: str
    device_type: str
    status: str
    is_critical: bool
```

### 6.3 DTOs de Dominio Clínico

```python
# core/application/dto/clinical_dtos.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class CDSSRecommendationDTO:
    """DTO for CDSS recommendations."""
    
    id: str
    title: str
    description: str
    priority: str
    evidence_level: str
    confidence: float
    actions: list[str]
    device_id: str | None = None
    symptoms: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class RCAAnalysisDTO:
    """DTO for Root Cause Analysis."""
    
    root_cause: str
    contributing_factors: list[str]
    confidence: float
    evidence: list[dict]
    recommended_actions: list[str]
    similar_incidents: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class DiagnosisDTO:
    """DTO for differential diagnosis."""
    
    diagnosis: str
    probability: float
    supporting_evidence: list[str]
    conflicting_evidence: list[str] = field(default_factory=list)
    recommended_tests: list[str] = field(default_factory=list)
```

---

## 7. INTERFACES A MOVER A SHARED

### 7.1 Interfaces de Servicio

```
core/shared/services/
├── __init__.py
├── query/
│   ├── __init__.py
│   └── interfaces.py           # IQueryService<T>
└── command/
    ├── __init__.py
    └── interfaces.py           # ICommandService<T>
```

### 7.2 Interfaces a Definir

```python
# core/shared/services/query/interfaces.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Result

T = TypeVar("T")

class IQueryService(ABC, Generic[T]):
    """Base interface for all Query Services."""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Result[T | None, str]:
        """Get entity by ID."""
        ...
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> Result[list[T], str]:
        """List all entities."""
        ...
```

```python
# core/shared/services/command/interfaces.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Result

T = TypeVar("T")
C = TypeVar("C")

class ICommandService(ABC, Generic[T, C]):
    """Base interface for all Command Services."""
    
    @abstractmethod
    async def execute(self, command: C) -> Result[T, str]:
        """Execute a command and return result."""
        ...
```

### 7.3 Interfaz de Repositorio Estandarizada

```python
# core/shared/repositories/interfaces.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Result

Entity = TypeVar("Entity")
EntityId = TypeVar("EntityId")

class IRepository(ABC, Generic[Entity, EntityId]):
    """Base interface for all repositories."""
    
    @abstractmethod
    async def save(self, entity: Entity) -> Result[Entity, str]:
        ...
    
    @abstractmethod
    async def get_by_id(self, id: EntityId) -> Result[Entity | None, str]:
        ...
    
    @abstractmethod
    async def delete(self, id: EntityId) -> Result[bool, str]:
        ...
```

---

## 8. COMPONENTES NO ACCESIBLES POR AI

### 8.1 Never Access Directamente

| Componente | Razón |
|------------|-------|
| `BaseEntity._pending_events` | Interno del agregado |
| `AggregateRoot.mark_created()` | Solo para factory interno |
| `ConcurrencyError` | Manejo interno de concurrencia |
| `DomainEvent._internal_metadata` | Solo para audit trail |
| `UnitOfWork` | Infraestructura, no dominio |

### 8.2 Solo Accesibles Via Command Service

| Componente | Servicio |
|------------|----------|
| `DeviceRepository.save()` | DeviceCommandService |
| `IncidentRepository.save()` | IncidentCommandService |
| `WorkOrderRepository.save()` | WorkOrderCommandService |
| `RecommendationRepository.save()` | RecommendationCommandService |

### 8.3 Solo Accesibles Via Query Service

| Componente | Servicio |
|------------|----------|
| `DeviceRepository.get_critical_devices()` | DeviceQueryService |
| `IncidentRepository.get_open_incidents()` | IncidentQueryService |
| `KnowledgeRepository.search_by_keywords()` | KnowledgeQueryService |
| `CapacityRepository.get_available_beds()` | HospitalQueryService |

---

## 9. DEPENDENCIAS CIRCULARES

### 9.1 Detectadas

| Ciclo | Módulos | Solución |
|-------|---------|----------|
| Knowledge → Engine → Router → Registry → Knowledge | knowledge/* | Extraer interfaces |
| Clinical → Diagnosis → CDSS → Clinical | clinical/* | Interfaz ICDSS en Shared |

### 9.2 Diagrama de Dependencias Actual

```
┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE MODULE                             │
│                                                                 │
│  ┌─────────────┐                                               │
│  │   engine    │ ◀──────┐                                      │
│  └─────────────┘       │                                      │
│         │              │                                      │
│         ▼              │                                      │
│  ┌─────────────┐       │                                      │
│  │   router    │───────┼──────────────────────────────────────┘
│  └─────────────┘       │
│         │              │
│         ▼              │
│  ┌─────────────┐       │
│  │  registry   │───────┘
│  └─────────────┘
│         │              │
│         ▼              │
│  ┌─────────────┐       │
│  │  service    │───────┘
│  └─────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Solución - Interfaces Abstractas

```
┌─────────────────────────────────────────────────────────────────┐
│                     KNOWLEDGE MODULE (REFACTORED)                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    INTERFACES (core/shared)              │   │
│  │                                                         │   │
│  │  IKnowledgeEngine                                        │   │
│  │  IKnowledgeRouter                                       │   │
│  │  IKnowledgeRegistry                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    IMPLEMENTATIONS                       │   │
│  │                                                         │   │
│  │  KnowledgeEngine ──▶ uses IKnowledgeRouter              │   │
│  │  KnowledgeRouter ──▶ uses IKnowledgeRegistry           │   │
│  │  KnowledgeRegistry                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. ARQUITECTURA PROPUEStA

### 10.1 Diagrama Completo

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI CORE (FASE 2)                                              │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                              TOOL ORCHESTRATOR                                     │   │
│  │                                                                                  │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                   │   │
│  │  │ DomainTool:   │  │ DomainTool:   │  │ DomainTool:   │                   │   │
│  │  │ get_device    │  │ search_knowledge│ │ get_incident │                   │   │
│  │  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                   │   │
│  │          │                    │                    │                            │   │
│  └──────────┼────────────────────┼────────────────────┼────────────────────────────┘   │
│             │                    │                    │                                │
└─────────────┼────────────────────┼────────────────────┼────────────────────────────────┘
              │                    │                    │
              ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                     CORE/APPLICATION/SERVICES (EPIC 11)                                      │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           QUERY SERVICES                                           │   │
│  │                                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │   │
│  │  │ DeviceQuerySvc │  │ KnowledgeQuerySvc│ │IncidentQuerySvc│                 │   │
│  │  │ get_device()   │  │ search()       │  │ get_incident() │                 │   │
│  │  │ list_devices() │  │ get_article()  │  │ get_open()     │                 │   │
│  │  │ get_critical() │  │ get_related() │  │ get_by_device()│                 │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │   │
│  │                                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │   │
│  │  │RecommendationSvc│ │ WorkOrderQuerySvc│ │ HospitalQuerySvc│                 │   │
│  │  │ get_pending()   │  │ get_pending()  │  │ get_capacity() │                 │   │
│  │  │ get_by_conf()  │  │ get_sla_breach()│ │ get_available()│                 │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          COMMAND SERVICES                                         │   │
│  │                                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │   │
│  │  │ DeviceCommandSvc│ │IncidentCommandSvc│ │ KnowledgeCommandSvc│               │   │
│  │  │ register()     │  │ create()       │  │ create()       │                 │   │
│  │  │ transfer()     │  │ escalate()     │  │ publish()      │                 │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                          DOMAIN SERVICES                                          │   │
│  │                                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │   │
│  │  │ CDSSService    │  │ RCAAnalysisSvc │  │ DiagnosisSvc    │                 │   │
│  │  │ get_recomm()   │  │ analyze()      │  │ get_diff_diag() │                 │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │   │
│  │                                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                                     │   │
│  │  │ TroubleshootingSvc│ │ PredictionSvc  │                                     │   │
│  │  │ get_steps()     │  │ predict()      │                                     │   │
│  │  └─────────────────┘  └─────────────────┘                                     │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                             EVENT SERVICES                                        │   │
│  │                                                                                  │   │
│  │  ┌─────────────────────────┐  ┌─────────────────────────────┐                   │   │
│  │  │ EventQueryService      │  │ EventSubscriptionService   │                   │   │
│  │  │ get_events()          │  │ subscribe()                │                   │   │
│  │  │ get_by_type()         │  │ unsubscribe()              │                   │   │
│  │  └─────────────────────────┘  └─────────────────────────────┘                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Repository Interfaces
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              DOMAIN LAYER                                                    │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         ENTITIES (Aggregate Roots)                                 │   │
│  │                                                                                  │   │
│  │  Device ──▶ DeviceRepository (ABC)    Incident ──▶ IncidentRepository (ABC)    │   │
│  │  Knowledge ──▶ KnowledgeRepository  Recommendation ──▶ RecommendationRepository│   │
│  │  WorkOrder ──▶ WorkOrderRepository  Bed ──▶ BedRepository (ABC)              │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         VALUE OBJECTS                                              │   │
│  │                                                                                  │   │
│  │  DeviceStatus  IncidentStatus  RecommendationStatus  WorkOrderStatus           │   │
│  │  DeviceType    Severity        EvidenceLevel          Priority                  │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                         DOMAIN EVENTS                                              │   │
│  │                                                                                  │   │
│  │  DeviceRegistered  IncidentReported  WorkOrderCreated  RecommendationGenerated  │   │
│  │  DeviceStatusChanged IncidentResolved WorkOrderCompleted                          │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQLAlchemy Implementations
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           INFRASTRUCTURE LAYER                                            │
│                                                                                          │
│  DeviceRepositoryImpl  IncidentRepositoryImpl  KnowledgeRepositoryImpl                  │
│  RecommendationRepositoryImpl  WorkOrderRepositoryImpl  BedRepositoryImpl                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Flujo de Datos

```
AI: "Show me devices needing maintenance"
    │
    ▼
ToolOrchestrator.route("maintenance")
    │
    ▼
DomainTool: get_needing_maintenance()
    │
    ▼
DeviceQueryService.get_needing_maintenance(tenant_id)
    │
    ├──▶ Validates tenant_id
    ├──▶ Calls DeviceRepository.get_needing_maintenance()
    ├──▶ Maps Device entity to DeviceDTO
    └──▶ Returns list[DeviceDTO]
    │
    ▼
Tool returns DeviceDTO list to AI
    │
    ▼
AI processes DTOs, not entities
```

---

## 11. RIESGOS IDENTIFICADOS

### 11.1 Alto Riesgo

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper API existente | Alta | Crítico | No modificar interfaces de repositorio |
| Introducir regresiones | Alta | Alto | Tests de regresión obligatorios |
| Ciclos de dependencia | Media | Alto | Análisis de dependencias automatizado |

### 11.2 Medio Riesgo

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Performance degradado | Media | Medio | Lazy loading, caching |
| Tests insuficientes | Alta | Medio | 80% coverage mínimo |
| Documentación desactualizada | Alta | Bajo | Actualizar con cada PR |

### 11.3 Bajo Riesgo

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Naming inconsistente | Baja | Bajo | Style guide |
| DTOs incompletos | Baja | Bajo | Code review |

---

## 12. ADRs NECESARIOS

### 12.1 ADRs a Crear

| ADR | Título | Decisión |
|-----|--------|----------|
| ADR-11000 | Domain AI Integration Architecture | Arquitectura de la nueva capa |
| ADR-11001 | Query Services Design | Patrones CQRS para query |
| ADR-11002 | Command Services Design | Patrones CQRS para command |
| ADR-11003 | DTO Design for AI | Estructura de DTOs |
| ADR-11004 | Event Exposure Strategy | Qué eventos exponer a AI |
| ADR-11005 | Dependency Inversion | Uso de interfaces abstractas |
| ADR-11006 | Repository Access Control | Solo via servicios, no directo |
| ADR-11007 | Shared Interfaces Location | Dónde definir interfaces compartidas |
| ADR-11008 | Tool Service Mapping | Cómo mapear tools a servicios |

### 12.2 ADRs Existentes a Actualizar

| ADR | Actualización |
|-----|---------------|
| ADR-0001 | Agregar referencia a EPIC 11 |
| ADR-0007 | Agregar restricción de acceso a repositorios |
| ADR-0012 | Actualizar con nueva arquitectura |

---

## 13. PLAN DE MIGRACIÓN

### 13.1 Fases de Implementación

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PLAN DE MIGRACIÓN                                              │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 1: Shared Interfaces (Semana 1)                                             │   │
│  │  - Crear core/shared/services/                                                   │   │
│  │  - Definir IQueryService, ICommandService                                        │   │
│  │  - Definir IRepository genérica                                                 │   │
│  │  - Actualizar ADR-11000 a 11008                                                 │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 2: DTOs (Semana 2)                                                         │   │
│  │  - Crear core/application/dto/                                                  │   │
│  │  - Implementar DeviceDTO, IncidentDTO, etc.                                      │   │
│  │  - Implementar from_entity() para cada DTO                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 3: Query Services (Semana 3-4)                                            │   │
│  │  - DeviceQueryService                                                           │   │
│  │  - IncidentQueryService                                                         │   │
│  │  - KnowledgeQueryService                                                        │   │
│  │  - RecommendationQueryService                                                    │   │
│  │  - WorkOrderQueryService                                                        │   │
│  │  - HospitalQueryService                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 4: Command Services (Semana 5-6)                                          │   │
│  │  - DeviceCommandService                                                         │   │
│  │  - IncidentCommandService                                                       │   │
│  │  - KnowledgeCommandService                                                      │   │
│  │  - RecommendationCommandService                                                 │   │
│  │  - WorkOrderCommandService                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 5: Domain Services (Semana 7-8)                                            │   │
│  │  - CDSSService (fachada para CDSSEngine)                                        │   │
│  │  - RCAAnalysisService                                                          │   │
│  │  - DiagnosisService                                                             │   │
│  │  - TroubleshootingService                                                        │   │
│  │  - PredictionService                                                             │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 6: Event Services (Semana 9)                                              │   │
│  │  - EventQueryService                                                            │   │
│  │  - EventSubscriptionService                                                     │   │
│  │  - Registrar eventos públicos                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 7: Integración con AI Core (Semana 10-11)                                │   │
│  │  - Crear DomainTools                                                            │   │
│  │  - Registrar en ToolOrchestrator                                                │   │
│  │  - Tests de integración                                                        │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                        │                                                 │
│                                        ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │  FASE 8: Validación y Documentación (Semana 12)                                │   │
│  │  - Tests de regresión                                                          │   │
│  │  - Actualizar documentación                                                     │   │
│  │  - Code review final                                                            │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 13.2 Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `core/device/domain/repositories/device_repository.py` | Agregar marker interface |
| `core/incident/domain/repositories/incident_repository.py` | Agregar marker interface |
| `core/knowledge/domain/repositories/knowledge_repository.py` | Agregar marker interface |
| `core/shared/entities/base.py` | Agregar métodos de conversión a DTO |
| `docs/phases/PHASE_1/README.md` | Actualizar estado de EPIC 11 |
| `docs/phases/README.md` | Actualizar roadmap |

### 13.3 Archivos a Crear

| Archivo | Propósito |
|---------|-----------|
| `core/application/__init__.py` | Módulo de aplicación |
| `core/application/services/__init__.py` | Servicios |
| `core/application/services/query/*.py` | 9 Query Services |
| `core/application/services/command/*.py` | 6 Command Services |
| `core/application/services/domain/*.py` | 5 Domain Services |
| `core/application/services/events/*.py` | 2 Event Services |
| `core/application/dto/*.py` | 14 DTOs |
| `core/shared/services/__init__.py` | Interfaces compartidas |
| `core/shared/services/query/interfaces.py` | IQueryService |
| `core/shared/services/command/interfaces.py` | ICommandService |
| `docs/phases/PHASE_1/epics/epic11/*.md` | Documentación EPIC 11 |
| `docs/phases/PHASE_1/adr/epic11/*.md` | ADRs EPIC 11 |

### 13.4 Compatibilidad

| Aspecto | Estrategia |
|---------|-----------|
| APIs REST existentes | Sin cambios |
| Repositorios | Solo añadir interfaces, no modificar |
| Entidades | Solo añadir from_entity(), no modificar lógica |
| FASE 2 actual | Wrapper de compatibilidad |

### 13.5 Criterios de Éxito

- ✅ Todos los repositorios tienen servicios wrapper
- ✅ AI Core accede solo via servicios
- ✅ DTOs separan dominio de AI
- ✅ Tests de regresión pasan 100%
- ✅ Documentación actualizada
- ✅ ADRs creados y aceptados

---

## ANEXO: CHECKLIST DE AUDITORÍA

### Entidades
- [x] Device - Analizado
- [x] Incident - Analizado
- [x] KnowledgeArticle - Analizado
- [x] AIRecommendation - Analizado
- [x] WorkOrder - Analizado
- [x] Bed/Capacity - Analizado
- [x] Staff - Analizado
- [x] Asset - Analizado
- [x] Inventory - Analizado

### Repositorios
- [x] DeviceRepository - Analizado
- [x] IncidentRepository - Analizado
- [x] KnowledgeRepository - Analizado
- [x] RecommendationRepository - Analizado
- [x] WorkOrderRepository - Analizado
- [x] BedRepository - Analizado
- [x] StaffRepository - Analizado
- [x] AssetRepository - Analizado
- [x] InventoryRepository - Analizado

### Servicios Existentes
- [x] KnowledgeService - Analizado
- [x] RecommendationService - Analizado
- [x] CDSSEngine - Analizado
- [x] DiagnosisEngine - Analizado
- [x] TroubleshootingEngine - Analizado

### Módulos Compartidos
- [x] core/shared - Analizado
- [x] core/events - Analizado
- [x] core/context - Analizado

---

*Documento generado: 2026-07-20*
*Auditoría: OpenHands AI Agent*
