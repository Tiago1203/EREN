# EPIC 10: Phase 1 Integration Bridge

**Estado:** Implementando  
**Fecha de inicio:** 2026-07-20  
**Epic Owner:** Architecture Team  

---

## Objetivo

Conectar completamente el AI Core (FASE 2) con el Business Domain (FASE 1) para que EREN trabaje sobre datos reales del hospital.

---

## Contexto

### Situación Actual

El AI Core actualmente funciona como un sistema aislado:
- Los gateways tienen implementaciones mock
- El Memory Manager solo almacena texto
- El Tool Orchestrator no tiene herramientas reales
- El Context Builder no consulta el dominio

### Situación Deseada

EREN como Cognitive Operating System integrado:
- AI Core consume datos reales del dominio
- Contexto construido con información de dispositivos, incidentes, etc.
- Memorias que referencian entidades del dominio
- Herramientas que invocan servicios reales

---

## Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI CORE (PHASE 2)                             │
│                                                                  │
│  ┌──────────────┐                                               │
│  │ Conversation │ ←── ConversationController                     │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │    Memory    │ ←── MemoryManager (con referencias)            │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │    Context   │ ←── ContextBuilder (con datos reales)          │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │    Prompt    │ ←── PromptBuilder                              │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │    Tools     │ ←── ToolOrchestrator (con herramientas reales) │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │   Provider   │ ←── LLM Provider                               │
│  └──────┬───────┘                                               │
│         │                                                        │
│  ┌──────▼───────┐                                               │
│  │   Response   │ ←── ResponseComposer                            │
│  └──────┬───────┘                                               │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│               INTEGRATION BRIDGE (EPIC 10)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   DomainGatewayAdapter                       │ │
│  │                                                              │ │
│  │  device_gateway ──▶ DeviceRepository                         │ │
│  │  incident_gateway ──▶ IncidentRepository                    │ │
│  │  knowledge_gateway ──▶ KnowledgeRepository                 │ │
│  │  recommendation_gateway ──▶ RecommendationRepository       │ │
│  │  hospital_gateway ──▶ CapacityRepository                    │ │
│  │  workorder_gateway ──▶ WorkOrderRepository                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   MemoryBridge                              │ │
│  │                                                              │ │
│  │  - Almacena referencias a entidades del dominio            │ │
│  │  - Convierte entidades a representaciones textuales          │ │
│  │  - Mantiene mapeo ID → Tipo de entidad                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   EventBridge                               │ │
│  │                                                              │ │
│  │  - Publica eventos de AI al Event Bus                       │ │
│  │  - Suscribe a eventos del dominio                          │ │
│  │  - Mantiene coherencia entre AI y Dominio                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BUSINESS DOMAIN (PHASE 1)                         │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Device  │ │ Incident │ │Knowledge │ │ Hospital │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│       │             │             │             │                   │
│  ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐ ┌────▼─────┐            │
│  │   Repo   │ │   Repo   │ │   Repo   │ │   Repo   │            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│       │             │             │             │                   │
│       └─────────────┴──────┬──────┴─────────────┘                   │
│                            │                                        │
│                     ┌──────▼──────┐                               │
│                     │  UnitOfWork  │                               │
│                     └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes a Implementar

### 1. DomainGatewayAdapter

**Ubicación:** `core/ai/integration/domain_adapter.py`

Responsabilidades:
- Crear implementaciones reales de los gateways
- Usar UnitOfWork para acceder a repositorios
- Convertir modelos de dominio a DTOs

```python
class DomainGatewayAdapter:
    """Adapta los gateways del AI Core al dominio real."""
    
    def __init__(self, uow_factory):
        self._uow_factory = uow_factory
    
    def create_device_gateway(self) -> IDeviceGateway:
        """Crea gateway de dispositivos conectado al repositorio real."""
    
    def create_incident_gateway(self) -> IIncidentGateway:
        """Crea gateway de incidentes conectado al repositorio real."""
    
    # ... etc
```

### 2. MemoryBridge

**Ubicación:** `core/ai/integration/memory_bridge.py`

Responsabilidades:
- Almacenar referencias a entidades del dominio
- Mantener mapeo de IDs a tipos de entidad
- Serializar referencias para persistencia

```python
@dataclass
class DomainReference:
    """Referencia a una entidad del dominio."""
    entity_type: str  # "device", "incident", etc.
    entity_id: str
    display_name: str
    metadata: dict

class MemoryBridge:
    """Puente entre memoria y dominio."""
    
    def store_reference(
        self,
        memory_id: str,
        reference: DomainReference,
    ) -> None:
        """Almacena una referencia de dominio."""
    
    def get_references(
        self,
        memory_id: str,
    ) -> list[DomainReference]:
        """Obtiene referencias de dominio para una memoria."""
```

### 3. EventBridge

**Ubicación:** `core/ai/integration/event_bridge.py`

Responsabilidades:
- Publicar eventos del AI al Event Bus
- Suscribir a eventos del dominio
- Mantener coherencia

```python
class EventBridge:
    """Puente entre eventos de AI y dominio."""
    
    def __init__(self, event_bus):
        self._event_bus = event_bus
    
    async def publish_ai_event(self, event: AIEvent) -> None:
        """Publica un evento del AI al Event Bus."""
    
    async def subscribe_to_domain_events(self) -> None:
        """Suscribe a eventos del dominio."""
```

### 4. Gateways con Implementación Real

**Ubicación:** `core/ai/domain/`

| Gateway | Descripción |
|---------|-------------|
| `device_gateway.py` | Actualizado para usar DeviceRepository real |
| `incident_gateway.py` | Actualizado para usar IncidentRepository real |
| `knowledge_gateway.py` | Actualizado para usar KnowledgeRepository real |
| `recommendation_gateway.py` | Actualizado para usar RecommendationRepository real |
| `hospital_gateway.py` | Actualizado para usar CapacityRepository real |
| `workorder_gateway.py` | Actualizado para usar WorkOrderRepository real |

---

## Flujo de Integración

### Flujo de Consulta

```
1. Usuario pregunta sobre dispositivo
   ↓
2. ConversationController recibe mensaje
   ↓
3. MemoryBridge obtiene referencias previas
   ↓
4. ContextBuilder consulta DomainGatewayAdapter
   ↓
5. DomainGatewayAdapter usa UnitOfWork
   ↓
6. UnitOfWork accede a DeviceRepository
   ↓
7. Datos转换为 DeviceDTO
   ↓
8. DeviceContextProvider convierte a ContextItem
   ↓
9. Contexto se envía al Prompt
```

### Flujo de Herramienta

```
1. LLM solicita herramienta "search_device"
   ↓
2. ToolOrchestrator obtiene herramienta
   ↓
3. Tool usa DomainGatewayAdapter
   ↓
4. DomainGatewayAdapter ejecuta consulta real
   ↓
5. Resultado se formatea y devuelve al LLM
```

### Flujo de Evento

```
1. AI detecta situación crítica
   ↓
2. EventBridge publica AIEvent
   ↓
3. Event Bus distribuye evento
   ↓
4. Suscriptores procesan (ej: crear incidente)
```

---

## Compatibilidad

Este EPIC debe ser **100% compatible** con:

| EPIC | Compatibilidad |
|------|---------------|
| EPIC 0 | ✅ Kernel de AI sin cambios |
| EPIC 1 | ✅ Conversation sin cambios |
| EPIC 2 | ✅ Context sin cambios |
| EPIC 3 | ✅ Prompt sin cambios |
| EPIC 4 | ✅ Memory sin cambios |
| EPIC 5 | ✅ Tools sin cambios |
| EPIC 6 | ✅ Response sin cambios |
| EPIC 7 | ✅ Providers sin cambios |
| EPIC 8 | ✅ Sessions sin cambios |
| EPIC 9 | ✅ Integration sin cambios |

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Gateways con impl real | 6/6 (100%) |
| Context Providers actualizados | 8/8 (100%) |
| Herramientas con acceso real | 15/15 (100%) |
| Referencias de dominio en memoria | Soportado |
| Eventos publicados al Bus | Soportado |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|--------|------------|
| Acoplamiento con UnitOfWork | Media | Alto | Usar abstracciones |
| Latencia en consultas | Media | Medio | Cache y límites |
| Inconsistencia de datos | Baja | Alto | Transacciones |

---

## Timeline

| Fase | Duración | Descripción |
|------|----------|-------------|
| 1 | 2 días | DomainGatewayAdapter + Gateways |
| 2 | 2 días | MemoryBridge |
| 3 | 1 día | EventBridge |
| 4 | 2 días | Tests e integración |
| 5 | 1 día | Documentación final |

---

## Referencias

- [ADR-2110: Domain Gateway Adapter](./adr/ADR-2110.md)
- [ADR-2111: Memory Bridge Pattern](./adr/ADR-2111.md)
- [ADR-2112: Event Bridge Pattern](./adr/ADR-2112.md)
- [ADR-2113: Entity Reference Serialization](./adr/ADR-2113.md)
- [ADR-2114: UnitOfWork Integration](./adr/ADR-2114.md)
