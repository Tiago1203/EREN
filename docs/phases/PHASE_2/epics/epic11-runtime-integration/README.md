# EPIC 11: Runtime Integration - AI Core ↔ Business Domain

**Estado:** Implementando  
**Fecha de inicio:** 2026-07-21  
**Epic Owner:** Architecture Team  

---

## Objetivo

Conectar definitivamente la FASE 1 (Business Domain) con la FASE 2 (AI Core), eliminando todos los mocks y dejando el flujo completo funcionando con datos reales.

---

## Contexto

### Situación Actual (Post EPIC 10)

EPIC 10 creó la infraestructura de integración:

```
┌─────────────────────────────────────────────────────────────────┐
│  AI CORE (EPIC 0-10)                                          │
│                                                                 │
│  ✅ AIUnitOfWorkFactory (infraestructura)                      │
│  ✅ DomainGatewayAdapter (factory de gateways)                │
│  ✅ MemoryBridge (referencias de dominio)                     │
│  ✅ EventBridge (eventos AI ↔ Domain)                         │
│  ✅ Gateways implementados (Device, Incident, Knowledge, etc.)  │
│                                                                 │
│  ❌ AICoreController NO usa Integration Layer                  │
│  ❌ Context Providers NO reciben Gateways                      │
│  ❌ Imports incorrectos (módulos inexistentes)               │
│  ❌ Repositorios faltantes (Incident, Knowledge, Recommendation)│
└─────────────────────────────────────────────────────────────────┘
```

### Situación Deseada

```
┌─────────────────────────────────────────────────────────────────┐
│  USUARIO                                                       │
│       ↓                                                         │
│  CONVERSATION CONTROLLER                                        │
│       ↓                                                         │
│  MEMORY MANAGER (via MemoryBridge)                            │
│       ↓                                                         │
│  CONTEXT BUILDER                                               │
│       ↓                                                         │
│  DEVICE PROVIDER ←── DeviceGateway ──→ DeviceRepository        │
│  INCIDENT PROVIDER ←─ IncidentGateway ──→ IncidentRepository │
│  KNOWLEDGE PROVIDER ← KnowledgeGateway ──→ KnowledgeRepository │
│  RECOMMENDATION PROVIDER ← RecGateway ──→ RecommendationRepo│
│  HOSPITAL PROVIDER ← HospitalGateway ──→ CapacityRepository    │
│  WORKORDER PROVIDER ← WorkOrderGateway ──→ WorkOrderRepository│
│       ↓                                                         │
│  PROMPT BUILDER                                               │
│       ↓                                                         │
│  PROVIDER MANAGER (OpenAI/Anthropic)                         │
│       ↓                                                         │
│  RESPONSE COMPOSER                                            │
│       ↓                                                         │
│  USUARIO                                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER REQUEST                                        │
│                     "What devices need maintenance?"                          │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONVERSATION CONTROLLER                                   │
│  • Load conversation history                                                │
│  • Extract entities                                                         │
│  • Route to context building                                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MEMORY BRIDGE                                         │
│  • Store conversation with domain references                               │
│  • Search previous references                                              │
│  • Maintain entity linkage                                                 │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CONTEXT BUILDER                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    PROVIDER PIPELINE                                │    │
│  │                                                                   │    │
│  │  DeviceProvider ──→ DeviceGateway ──→ DeviceRepository           │    │
│  │  IncidentProvider ──→ IncidentGateway ──→ IncidentRepository   │    │
│  │  KnowledgeProvider ──→ KnowledgeGateway ──→ KnowledgeRepository│    │
│  │  RecommendationProvider ──→ RecGateway ──→ RecRepository     │    │
│  │  HospitalProvider ──→ HospitalGateway ──→ CapacityRepository  │    │
│  │  WorkOrderProvider ──→ WorkOrderGateway ──→ WorkOrderRepository│    │
│  │                                                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROMPT BUILDER                                         │
│  • Combine all context into prompt                                          │
│  • Include device data, incidents, knowledge, etc.                         │
│  • Format for LLM                                                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PROVIDER MANAGER                                        │
│  • OpenAI Provider                                                       │
│  • Anthropic Provider                                                    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RESPONSE COMPOSER                                      │
│  • Parse LLM response                                                    │
│  • Include actionable items                                               │
│  • Format for user                                                       │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER RESPONSE                                     │
│  "The following devices need maintenance:                                │
│   - Ventilator ICU-1 (overdue since July 15)                            │
│   - MRI Scanner Main (calibration due in 3 days)"                        │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes a Completar

### 1. Repositorios Faltantes

| Repositorio | Ubicación Actual | Ubicación Requerida | Estado |
|------------|-----------------|-------------------|--------|
| Incident | ❌ No existe | `apps/api/app/domain/incident/repository.py` | 🔴 Crear |
| Knowledge | ❌ No existe | `apps/api/app/domain/knowledge/repository.py` | 🔴 Crear |
| Recommendation | ❌ No existe | `apps/api/app/domain/recommendation/repository.py` | 🔴 Crear |

### 2. Imports a Corregir

| Archivo | Import Incorrecto | Import Correcto |
|--------|-----------------|----------------|
| `uow_factory.py` | `apps.api.app.domain.incident.repository` | Crear o usar `core.incident.*` |
| `uow_factory.py` | `apps.api.app.domain.knowledge.repository` | Crear o usar `core.knowledge.*` |
| `uow_factory.py` | `apps.api.app.domain.recommendation.repository` | Crear o usar `core.recommendation.*` |

### 3. Dependency Injection

| Provider | Gateway Requerido | Provider Actual |
|---------|-----------------|----------------|
| DeviceContextProvider | DeviceGateway | ❌ Sin gateway |
| IncidentContextProvider | IncidentGateway | ❌ Sin gateway |
| KnowledgeContextProvider | KnowledgeGateway | ❌ Sin gateway |
| RecommendationContextProvider | RecommendationGateway | ❌ Sin gateway |
| HospitalContextProvider | HospitalGateway | ❌ Sin gateway |
| WorkOrderContextProvider | WorkOrderGateway | ❌ Sin gateway |

### 4. AICoreController Integration

```python
# current (INCORRECTO)
class AICoreController:
    def __init__(self, config):
        self._providers = []  # Vacío

# CORRECTO
class AICoreController:
    def __init__(self, config):
        integration = setup_integration()
        self._gateways = integration["gateways"]
        self._memory_bridge = integration["memory_bridge"]
        self._event_bridge = integration["event_bridge"]
```

---

## Flujo de Datos

### Dispositivo

```
1. User asks: "Status of ventilator ICU-1?"
   ↓
2. ConversationController extracts device_id
   ↓
3. ContextBuilder calls DeviceContextProvider
   ↓
4. DeviceContextProvider calls DeviceGateway.get_by_id()
   ↓
5. DeviceGateway calls AIUnitOfWorkFactory
   ↓
6. AIUnitOfWork uses DeviceRepository
   ↓
7. DeviceRepository queries PostgreSQL
   ↓
8. DeviceModel returned
   ↓
9. DeviceGateway converts to DeviceDTO
   ↓
10. DeviceContextProvider creates ContextItem
   ↓
11. Prompt includes real device data
```

### Incidente

```
1. User asks: "Show open incidents"
   ↓
2. ContextBuilder calls IncidentContextProvider
   ↓
3. IncidentContextProvider calls IncidentGateway.get_open_incidents()
   ↓
4. IncidentGateway queries PostgreSQL
   ↓
5. Returns real incidents
   ↓
6. Prompt includes real incidents
```

---

## Tareas

### Fase 1: Repositorios (2 días)

- [ ] Crear `incident/repository.py` en `apps/api/app/domain/`
- [ ] Crear `knowledge/repository.py` en `apps/api/app/domain/`
- [ ] Crear `recommendation/repository.py` en `apps/api/app/domain/`
- [ ] Verificar que todos los repositorios usan SQLAlchemy
- [ ] Verificar que implementan los métodos requeridos por los gateways

### Fase 2: Imports (1 día)

- [ ] Corregir imports en `uow_factory.py`
- [ ] Verificar que todos los gateways pueden importar sus repositorios
- [ ] Test de importación de todos los módulos

### Fase 3: Dependency Injection (2 días)

- [ ] Modificar `providers/__init__.py` para inyectar gateways
- [ ] Crear WorkOrderContextProvider si no existe
- [ ] Verificar que todos los providers reciben sus gateways
- [ ] Test de providers con gateways reales

### Fase 4: AICoreController (1 día)

- [ ] Modificar `AICoreController.initialize()` para usar `setup_integration()`
- [ ] Conectar MemoryBridge al MemoryManager
- [ ] Conectar EventBridge al sistema de eventos
- [ ] Test de AICoreController con integración completa

### Fase 5: Validación (2 días)

- [ ] Crear Integration Tests para cada gateway
- [ ] Crear End-to-End test
- [ ] Validar flujo completo usuario → respuesta
- [ ] Verificar que no hay mocks en el flujo

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Gateways con repositorio real | 6/6 (100%) |
| Context Providers con gateway | 6/6 (100%) |
| Tests de integración pasando | 9/9 (100%) |
| Flujo E2E funcionando | 100% |
| Mocks en flujo de contexto | 0% |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|------------|--------|------------|
| Repositorios no existentes | Alta | Alto | Crearlos siguiendo patrón existente |
| Breaking changes | Baja | Alto | No modificar APIs públicas |
| Performance degradation | Media | Medio | Monitorear queries |
| Circular dependencies | Baja | Alto | Verificar imports |

---

## Dependencias

- EPIC 10: Domain Integration Bridge (completo)
- EPIC 0-9: AI Core (completo)
- FASE 1: Business Domain (completo)

---

## Referencias

- [ADR-2110: Domain Gateway Adapter](../adr/epic10-domain-bridge/ADR-2110.md)
- [ADR-2111: Memory Bridge Pattern](../adr/epic10-domain-bridge/ADR-2111.md)
- [ADR-2112: Event Bridge Pattern](../adr/epic10-domain-bridge/ADR-2112.md)
- [EPIC 10 README](../epic10-domain-bridge/README.md)
