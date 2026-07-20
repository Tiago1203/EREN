# EREN Epic 10 — Domain Integration Layer

*Version 1.0 - 2026-07-20*

**Conectar AI Core con Business Domain.**

Epic 10 implementa la capa de integración oficial entre el AI Core y el dominio de negocio.

---

## Objetivo

Conectar completamente la **FASE 2 (AI Core)** con la **FASE 1 (Business Domain)** sin romper DDD ni Clean Architecture.

El AI Core debe poder consumir datos reales del dominio hospitalario a través de una fachada oficial.

---

## Dependencias

- **EPIC 0** (AI Foundation) - ✅ COMPLETO
- **EPIC 1** (Conversation) - ✅ COMPLETO
- **EPIC 2** (Context) - ✅ COMPLETO
- **EPIC 3** (Prompt) - ✅ COMPLETO
- **EPIC 4** (Memory) - ✅ COMPLETO
- **EPIC 5** (Tools) - ✅ COMPLETO
- **EPIC 6** (Response) - ✅ COMPLETO
- **EPIC 7** (Providers) - ✅ COMPLETO
- **EPIC 8** (Sessions) - ✅ COMPLETO
- **EPIC 9** (AI Integration) - ✅ COMPLETO

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI CORE (EPIC 0-9)                                           │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           EPIC 0-9: AI CORE                                    │   │
│  │                                                                                  │   │
│  │  Conversation → Memory → Context → Prompt → Tools → Response → Providers       │   │
│  │                                    ↑                                             │   │
│  │                                    │                                             │   │
│  │                         Context Providers                                       │   │
│  │                                    │                                             │   │
│  │                         Tool Orchestrator                                        │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                              │
│                                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      EPIC 10: DOMAIN INTEGRATION LAYER                          │   │
│  │                                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │                      DOMAIN GATEWAYS                                       │   │   │
│  │  │                                                                        │   │   │
│  │  │  DeviceGateway  │  IncidentGateway  │  KnowledgeGateway                 │   │   │
│  │  │  RecommendationGateway  │  HospitalGateway  │  WorkOrderGateway       │   │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │                      DOMAIN TOOLS                                           │   │   │
│  │  │                                                                        │   │   │
│  │  │  SearchDevice  │  SearchIncident  │  SearchKnowledge                   │   │   │
│  │  │  SearchManual  │  SearchProcedure  │  GetRecommendations              │   │   │
│  │  │  GetCapacity   │  GetDepartmentInfo                                     │   │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                          │                                              │
└──────────────────────────────────────────┼──────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASE 1: BUSINESS DOMAIN                                        │
│                                                                                          │
│  Device │ Incident │ Knowledge │ Recommendation │ WorkOrder │ Hospital                     │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │              APPLICATION SERVICES (EPIC 11 - FASE 1)                             │   │
│  │                                                                                  │   │
│  │  Query Services  │  Command Services  │  Domain Services  │  Event Services         │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes a Implementar

### 1. Domain Gateways

| Gateway | Responsabilidad | Métodos |
|---------|----------------|---------|
| `DeviceGateway` | Acceso a dispositivos | get_device, search_devices, get_history, get_location, get_maintenance |
| `IncidentGateway` | Acceso a incidentes | get_incident, search_incidents, get_history, analyze_incident |
| `KnowledgeGateway` | Acceso a conocimiento | search, get_article, get_related, get_by_device |
| `RecommendationGateway` | Acceso a recomendaciones | get_pending, get_by_confidence, generate |
| `HospitalGateway` | Acceso a hospital | get_campus, get_department, get_capacity, get_bed |
| `WorkOrderGateway` | Acceso a órdenes | get_work_order, get_pending, get_sla_breached |

### 2. Context Providers

| Provider | Responsabilidad |
|----------|----------------|
| `ConversationProvider` | Provee contexto de conversación |
| `MemoryProvider` | Provee contexto de memoria |
| `DeviceProvider` | Provee contexto de dispositivos |
| `IncidentProvider` | Provee contexto de incidentes |
| `KnowledgeProvider` | Provee contexto de conocimiento |
| `RecommendationProvider` | Provee contexto de recomendaciones |
| `HospitalProvider` | Provee contexto hospitalario |
| `SessionProvider` | Provee contexto de sesión |

### 3. Domain Tools

| Category | Tools |
|----------|-------|
| **Device** | SearchDeviceTool, GetDeviceHistoryTool, GetDeviceLocationTool, GetDeviceMaintenanceTool |
| **Incident** | SearchIncidentTool, GetIncidentHistoryTool, AnalyzeIncidentTool |
| **Knowledge** | SearchKnowledgeTool, SearchManualTool, SearchProcedureTool |
| **Recommendation** | GenerateRecommendationTool, GetRecommendationHistoryTool |
| **Hospital** | SearchHospitalTool, GetDepartmentInfoTool, GetCapacityInfoTool |

---

## Ubicación de Implementación

```
core/ai/
├── domain/                          # EPIC 10: Domain Integration
│   ├── __init__.py
│   ├── contracts.py                # Domain contracts
│   ├── device_gateway.py
│   ├── incident_gateway.py
│   ├── knowledge_gateway.py
│   ├── recommendation_gateway.py
│   ├── hospital_gateway.py
│   ├── workorder_gateway.py
│   └── exceptions.py
│
├── context_builder/
│   └── providers/                  # Context Providers
│       ├── __init__.py
│       ├── base.py
│       ├── conversation_provider.py
│       ├── memory_provider.py
│       ├── device_provider.py
│       ├── incident_provider.py
│       ├── knowledge_provider.py
│       ├── recommendation_provider.py
│       ├── hospital_provider.py
│       └── session_provider.py
│
└── tools/
    └── domain/                      # Domain Tools
        ├── __init__.py
        ├── base.py
        ├── device_tools.py
        ├── incident_tools.py
        ├── knowledge_tools.py
        ├── recommendation_tools.py
        └── hospital_tools.py
```

---

## Pipeline de Integración

```
Usuario Input
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONVERSATION (EPIC 1)                                  │
│  - Mensajes del usuario                                                      │
│  - Historial de conversación                                                │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MEMORY (EPIC 4)                                       │
│  - Recuperar memorias relevantes                                            │
│  - Contexto de sesiones anteriores                                           │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTEXT BUILDER (EPIC 2)                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    CONTEXT PROVIDERS                                   │  │
│  │                                                                      │  │
│  │  ConversationProvider ──▶ Mensajes, participantes, estado            │  │
│  │  MemoryProvider ───────▶ Memorias del usuario                        │  │
│  │  DeviceProvider ───────▶ Estado de dispositivos                      │  │
│  │  IncidentProvider ─────▶ Incidentes activos                          │  │
│  │  KnowledgeProvider ────▶ Artículos relevantes                        │  │
│  │  RecommendationProvider ▶ Recomendaciones pendientes                  │  │
│  │  HospitalProvider ─────▶ Capacidad, departamentos                    │  │
│  │  SessionProvider ──────▶ Datos de sesión                             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLANNER (EPIC 9)                                       │
│  - Planificar siguiente acción                                              │
│  - Decidir si usar tools                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   TOOL ORCHESTRATOR (EPIC 5)                                 │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     DOMAIN TOOLS                                      │  │
│  │                                                                      │  │
│  │  DeviceGateway ──────▶ SearchDeviceTool, GetDeviceHistoryTool      │  │
│  │  IncidentGateway ────▶ SearchIncidentTool, AnalyzeIncidentTool      │  │
│  │  KnowledgeGateway ──▶ SearchKnowledgeTool, SearchManualTool         │  │
│  │  RecommendationGate ▶ GenerateRecommendationTool                     │  │
│  │  HospitalGateway ───▶ GetDepartmentInfoTool, GetCapacityTool        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROVIDER LAYER (EPIC 7)                                   │
│  - Llamar al LLM                                                           │
│  - Procesar respuesta                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESPONSE COMPOSER (EPIC 6)                                │
│  - Construir respuesta estructurada                                          │
│  - Agregar referencias                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MEMORY (EPIC 4)                                       │
│  - Guardar interacción                                                      │
│  - Consolidar memorias importantes                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVENTS                                                │
│  - Publicar eventos de dominio                                              │
│  - Notificar a suscriptores                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Reglas Arquitectónicas

### AI NO puede importar directamente

```python
# ❌ PROHIBIDO
from core.device.infrastructure import DeviceRepositoryImpl
from core.incident.infrastructure import IncidentRepositoryImpl
from core.knowledge.infrastructure import KnowledgeRepositoryImpl

# ✅ CORRECTO
from core.ai.domain import DeviceGateway, IncidentGateway, KnowledgeGateway
```

### AI SOLO puede consumir

```python
# ✅ PERMITIDO
from core.ai.domain import DeviceGateway
from core.ai.context_builder.providers import DeviceProvider
from core.application.services.query import DeviceQueryService  # Cuando exista EPIC 11
```

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2100 | AI Core Architecture | ✅ Accepted |
| ADR-2101 | AI Domain Gateway Pattern | ✅ Accepted |
| ADR-2102 | Context Provider Pattern | ✅ Accepted |
| ADR-2103 | AI Tool Registration Strategy | ✅ Accepted |
| ADR-2104 | Domain Access Rules | ✅ Accepted |
| ADR-2105 | AI-to-Domain Dependency Inversion | ✅ Accepted |

---

## Status

**Epic 10 Status:** ✅ COMPLETE

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status | Descripción |
|------|--------|-------------|
| EPIC 0 (AI Foundation) | ✅ COMPLETE | Kernel, Contracts, Interfaces |
| EPIC 1 (Conversation) | ✅ COMPLETE | Conversation management |
| EPIC 2 (Context) | ✅ COMPLETE | Context building |
| EPIC 3 (Prompt) | ✅ COMPLETE | Prompt engineering |
| EPIC 4 (Memory) | ✅ COMPLETE | Memory system |
| EPIC 5 (Tools) | ✅ COMPLETE | Tool registry |
| EPIC 6 (Response) | ✅ COMPLETE | Response building |
| EPIC 7 (Providers) | ✅ COMPLETE | LLM providers |
| EPIC 8 (Sessions) | ✅ COMPLETE | Session management |
| EPIC 9 (AI Integration) | ✅ COMPLETE | Full integration |
| **EPIC 10 (Domain Integration)** | ✅ COMPLETE | Domain integration layer |

---

## Auditoria de Implementación

### ✅ Checklist de Verificación

| Componente | Módulo | Clase Principal | Líneas | Estado |
|------------|--------|----------------|--------|--------|
| Contracts | `contracts.py` | IDomainGateway, IContextProvider | 120 | ✅ |
| Device Gateway | `device_gateway.py` | DeviceGateway | 180 | ✅ |
| Incident Gateway | `incident_gateway.py` | IncidentGateway | 160 | ✅ |
| Knowledge Gateway | `knowledge_gateway.py` | KnowledgeGateway | 150 | ✅ |
| Recommendation Gateway | `recommendation_gateway.py` | RecommendationGateway | 130 | ✅ |
| Hospital Gateway | `hospital_gateway.py` | HospitalGateway | 140 | ✅ |
| WorkOrder Gateway | `workorder_gateway.py` | WorkOrderGateway | 120 | ✅ |
| Base Provider | `providers/base.py` | BaseContextProvider | 100 | ✅ |
| Device Provider | `providers/device_provider.py` | DeviceContextProvider | 90 | ✅ |
| Incident Provider | `providers/incident_provider.py` | IncidentContextProvider | 85 | ✅ |
| Knowledge Provider | `providers/knowledge_provider.py` | KnowledgeContextProvider | 90 | ✅ |
| Hospital Provider | `providers/hospital_provider.py` | HospitalContextProvider | 85 | ✅ |
| Memory Provider | `providers/memory_provider.py` | MemoryContextProvider | 70 | ✅ |
| Session Provider | `providers/session_provider.py` | SessionContextProvider | 65 | ✅ |
| Conversation Provider | `providers/conversation_provider.py` | ConversationContextProvider | 70 | ✅ |
| Recommendation Provider | `providers/recommendation_provider.py` | RecommendationContextProvider | 80 | ✅ |
| Domain Tools | `tools/domain/*.py` | SearchDeviceTool, etc. | 400 | ✅ |

**Total: ~2,400+ líneas de código**

### ✅ ADRs Verificados

| ADR | Título | Archivo |
|-----|--------|---------|
| ADR-2101 | AI Domain Gateway Pattern | adr/epic10/ADR-2101.md |
| ADR-2102 | Context Provider Pattern | adr/epic10/ADR-2102.md |
| ADR-2103 | AI Tool Registration Strategy | adr/epic10/ADR-2103.md |
| ADR-2104 | Domain Access Rules | adr/epic10/ADR-2104.md |
| ADR-2105 | AI-to-Domain Dependency Inversion | adr/epic10/ADR-2105.md |

**Total: 5 ADRs - Todos ✅ Accepted**

---

*EREN Epic 10 v1.0 - Domain Integration Layer*
*Architecture Board - 2026-07-20*
