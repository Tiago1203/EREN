# EREN - Especificación Técnica Completa
## Fase 2: Cross-Context Contracts

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Depende de:** Fase 1 (Domain Model)

---

## Tabla de Contenidos

1. [Filosofía de Integración](#1-filosofía-de-integración)
2. [Published Language](#2-published-language)
3. [Anti-Corruption Layer](#3-anti-corruption-layer)
4. [Commands Entre Contextos](#4-commands-entre-contextos)
5. [Queries Entre Contextos](#5-queries-entre-contextos)
6. [Integration Events](#6-integration-events)
7. [DTOs de Integración](#7-dtos-de-integración)
8. [Protocolo de Versionado](#8-protocolo-de-versionado)

---

## 1. FILOSOFÍA DE INTEGRACIÓN

### 1.1 Principios Rectores

**Principio 1: Aislamiento de Contexto**
- Cada bounded context es independiente
- La comunicación es solo a través de contratos definidos
- No hay dependencias directas entre aggregates de diferentes contextos
- Los contextos pueden evolucionar independently sin romper otros

**Principio 2: Shared Language, Translated**
- El "Published Language" es el vocabulario compartido
- Cada contexto traduce a/de su dominio interno
- Los DTOs de integración son el único canal de comunicación
- Los IDs del Shared Kernel son la lingua franca

**Principio 3: Event-Driven por Defecto**
- Los contextos se comunican Primarily a través de eventos asíncronos
- Queries síncronas solo para datos necesarios en tiempo real
- Commands síncronos solo para operaciones que requieren respuesta inmediata
- Outbox Pattern obligatorio para consistencia eventual

**Principio 4: Stability**
- Una vez publicado un contrato, es immutable para esa versión mayor
- Versiones menores pueden agregar campos opcionales
- Breaking changes requieren nueva versión mayor
- Deprecation policy de 2 versiones para cambios

### 1.2 Patrones de Integración

| Patrón | Cuándo Usar | Ejemplo |
|--------|-------------|---------|
| **Domain Event** | Notificar cambios de estado | IncidentResolved → DeviceContext |
| **Query** | Necesito datos сейчас | AI Layer → DeviceContext |
| **Command** | Necesito una acción realizada | IncidentContext → DeviceContext |
| **Saga** | Transacción larga cross-context | New Device Registration |
| **Transactional Outbox** | Guaranteed delivery | Todos los eventos |

### 1.3 Supuestos Declarados

1. **Message Broker:** RabbitMQ como broker de mensajes (puede cambiar a Kafka en v2)
2. **API Gateway:** Kong o similar para APIs internas
3. **Service Mesh:** Istio para mTLS y routing (futuro)
4. **Serialization:** JSON para eventos (APM-friendly), Protocol Buffers para alta frecuencia
5. **Tracing:** OpenTelemetry con correlation_id propagation
6. **Los contextos se deployan como Microservices separados** (pero pueden co-locate inicialmente)

---

## 2. PUBLISHED LANGUAGE

### 2.1 Vocabulario Compartido

El Published Language es el conjunto de tipos, nombres y significados que todos los contextos comparten. Es la interfaz pública de cada contexto.

#### Tipos Compartidos (Shared Kernel)

```python
# Estos tipos SON el Published Language del Shared Kernel
# Todos los contextos los usan tal cual, sin traducción

SharedKernelTypes = {
    # IDs
    "TenantId": "UUID v7 string",
    "EngineerId": "UUID v7 string prefixed 'eng_'",
    "IncidentId": "UUID v7 string prefixed 'inc_'",
    "DeviceId": "UUID v7 string prefixed 'dev_'",
    "RecommendationId": "UUID v7 string prefixed 'rec_'",
    "KnowledgeId": "UUID v7 string prefixed 'kno_'",
    "UserId": "UUID v7 string prefixed 'usr_'",
    "OrganizationId": "UUID v7 string prefixed 'org_'",
    
    # Value Objects
    "Priority": "P1_CRITICAL | P2_HIGH | P3_MEDIUM | P4_LOW",
    "SafetyLevel": "CLASS_A | CLASS_B | CLASS_C | CLASS_D",
    "Confidence": {"value": "float", "level": "VERY_LOW|LOW|MEDIUM|HIGH|VERY_HIGH"},
    
    # Temporal
    "UTCDateTime": "ISO 8601 datetime in UTC",
    
    # Audit
    "AuditInfo": {"created_by": "EngineerId", "created_at": "UTCDateTime"},
}
```

### 2.2 Glosario Cross-Context

| Término | Definición | Contexto Dueño | Contexto(s) Consumidor(es) |
|---------|-----------|---------------|---------------------------|
| Incident | Evento que interrumpe el servicio normal de un dispositivo | Incident | Todos |
| Device | Equipo biomédico hardware | Device | Todos |
| Recommendation | Sugerencia generada por IA | Recommendation | Incident, AI Layer |
| Knowledge Article | Documento técnico institucional | Knowledge | Incident, Recommendation, AI Layer |
| Engineer | Profesional de ingeniería clínica | Shared | Todos |
| Tenant | Organización hospitalaria | Shared | Todos |
| Priority | Nivel de urgencia P1-P4 | Shared | Todos |
| SafetyLevel | Clasificación de riesgo A-D | Shared | Device, Incident |
| Confidence | Nivel de certeza de una recomendación | Shared | Recommendation, AI Layer |
| Category | Clasificación temática | Cada contexto | - |

### 2.3 Ownership de Entidades

```
Ownership Map:
{
  "Incident": {
    "owner_context": "Incident",
    "readable_by": ["Incident", "Recommendation", "AI Layer", "Knowledge"],
    "writable_by": ["Incident"],
    "events_emitted": true,
  },
  "Device": {
    "owner_context": "Device",
    "readable_by": ["Device", "Incident", "Recommendation", "AI Layer", "Knowledge"],
    "writable_by": ["Device"],
    "events_emitted": true,
  },
  "AIRecommendation": {
    "owner_context": "Recommendation",
    "readable_by": ["Recommendation", "Incident", "AI Layer"],
    "writable_by": ["Recommendation"],
    "events_emitted": true,
  },
  "KnowledgeArticle": {
    "owner_context": "Knowledge",
    "readable_by": ["Knowledge", "Recommendation", "AI Layer", "Incident"],
    "writable_by": ["Knowledge"],
    "events_emitted": true,
  },
}
```

---

## 3. ANTI-CORRUPTION LAYER

### 3.1 Propósito

Cada contexto tiene un ACL que:
1. Traduce los DTOs de integración a tipos del dominio local
2. Protege el dominio de corrupciones por datos externos
3. Mantiene la integridad de los invariantes locales
4. Aplica validation rules antes de entrar al dominio

### 3.2 ACL por Contexto

#### ACL IncidentContext

```
Inbound Translators:

  From_Device_DTO_to_DeviceId(device_dto: DeviceDTO) -> DeviceId
    1. Validate device_dto.id is valid UUID v7
    2. Validate device_dto.tenant_id matches current tenant
    3. Return DeviceId(device_dto.id)
    4. Raises: InvalidTenantError if tenant mismatch

  From_Knowledge_DTO_to_KnowledgeReference(knowledge_dto) -> KnowledgeReference
    1. Validate knowledge_dto.id format
    2. Translate to local KnowledgeReference VO
    3. Validate knowledge_dto is accessible (status != DELETED)

Outbound Translators:

  From_Incident_to_IncidentDTO(incident: EngineeringIncident) -> IncidentDTO
    1. Extract fields per IncidentDTO schema
    2. Translate local status to Published Language status
    3. Translate local priority to Shared Priority VO
    4. Truncate body to max_length

  From_IncidentEvent_to_EventDTO(event) -> IntegrationEventDTO
    1. Map event attributes to EventDTO schema
    2. Add correlation_id and causation_id
    3. Validate event_type naming convention
```

#### ACL DeviceContext

```
Inbound Translators:

  From_Incident_DTO_to_IncidentId(incident_dto: IncidentDTO) -> IncidentId
    1. Validate incident_dto.id format
    2. Validate incident_dto.tenant_id
    3. Return IncidentId

  From_LocationVO_to_LocationInfo(location: LocationVO) -> LocationInfo
    1. Validate all required fields present
    2. Validate country code if provided
    3. Translate to local LocationInfo VO
```

#### ACL RecommendationContext

```
Inbound Translators:

  From_Incident_DTO_to_IncidentContext(
    incident_dto: IncidentDTO,
    device_dtos: list[DeviceDTO],
    knowledge_dtos: list[KnowledgeDTO],
  ) -> RecommendationGenerationContext
    1. Validate all IDs
    2. Build context object for AI generation
    3. Enrich with device and knowledge data
    4. Raise if critical data missing (device info required for HARDWARE category)

Outbound Translators:

  From_Recommendation_to_RecommendationDTO(rec) -> RecommendationDTO
    1. Translate to Published Language format
    2. Include explanation (serialized ReasoningChain)
    3. Include citations (in hospital format)
    4. Add AI disclosure text
```

### 3.3 Translation Rules

| Scenario | Source | Target | Rule |
|----------|--------|--------|------|
| ID Translation | DeviceDTO.id (string) | DeviceId (typed) | Validate UUID, check tenant |
| Status Translation | DeviceContext.DeviceStatus | IncidentContext.DeviceStatus | Map 1:1 via enum |
| Priority Translation | Any Priority VO | Shared.Priority | Direct (same type) |
| Location Translation | DeviceContext.LocationInfo | IncidentContext.DeviceLocation | Flatten to string |
| Confidence Translation | Recommendation.Confidence | Shared.Confidence | Direct mapping |
| Date Translation | Any datetime | UTC ISO 8601 | Normalize to UTC |
| Name Collision | Device.device_name | Incident.device_name | Rename to device_name_in_Incident |

---

## 4. COMMANDS ENTRE CONTEXTOS

### 4.1 Command Overview

```
Command Pattern:
  - Name: {SourceContext}_{Action}_{TargetContext}
  - Async: Síncrono si respuesta requerida, Asíncrono si no
  - Idempotent: Todos los comandos deben ser idempotentes
  - Timeout: 30 segundos para síncronos
  - Retry: 3 veces con exponential backoff para asíncronos
```

### 4.2 Commands Síncronos (Request-Response)

#### IC-001: GetDeviceInfo
```
Source: IncidentContext
Target: DeviceContext
Type: Synchronous Query
Pattern: Request-Response

Request:
{
  "command_type": "IC-001_GetDeviceInfo",
  "command_id": "cmd_uuid",
  "tenant_id": "tenant_uuid",
  "device_id": "dev_uuid",
  "requested_fields": ["status", "location", "manufacturer", "calibration"],
  "correlation_id": "corr_uuid",
  "timestamp": "2026-07-15T10:00:00Z"
}

Response (Success):
{
  "command_id": "cmd_uuid",
  "status": "SUCCESS",
  "data": {
    "device_id": "dev_uuid",
    "device_name": "MRI Scanner Unit 3",
    "device_type": "mri",
    "status": "active",
    "risk_class": "CLASS_C",
    "location": {
      "building": "Main Hospital",
      "floor": "2",
      "room": "MRI-201",
      "department": "Radiology"
    },
    "manufacturer": {
      "name": "Siemens Healthineers",
      "model": "MAGNETOM Vida 3T"
    },
    "serial_number": "SN-2024-78945",
    "calibration": {
      "last_calibration_date": "2026-06-01T00:00:00Z",
      "next_calibration_date": "2026-09-01T00:00:00Z",
      "status": "current"
    },
    "is_operational": true,
    "has_open_incidents": false
  },
  "version": 1
}

Response (Error):
{
  "command_id": "cmd_uuid",
  "status": "ERROR",
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device dev_uuid not found",
    "details": {}
  }
}

Error Codes:
  - DEVICE_NOT_FOUND: Device does not exist or is deleted
  - UNAUTHORIZED: Tenant mismatch
  - DEVICE_DECOMMISSIONED: Device is decommissioned
```

#### IC-002: CheckDeviceAvailability
```
Source: IncidentContext
Target: DeviceContext
Type: Synchronous Query

Request:
{
  "command_type": "IC-002_CheckDeviceAvailability",
  "command_id": "cmd_uuid",
  "device_id": "dev_uuid",
  "tenant_id": "tenant_uuid",
  "correlation_id": "corr_uuid"
}

Response:
{
  "device_id": "dev_uuid",
  "is_available": true,
  "status": "active",
  "requires_attention": false,
  "has_open_incidents": false,
  "can_create_incident": true,
  "estimated_downtime_hours": null
}
```

#### RC-001: GetIncidentContext
```
Source: RecommendationContext
Target: IncidentContext
Type: Synchronous Query

Request:
{
  "command_type": "RC-001_GetIncidentContext",
  "command_id": "cmd_uuid",
  "incident_id": "inc_uuid",
  "tenant_id": "tenant_uuid",
  "include_history": true,
  "include_actions": true,
  "include_device_info": true,
  "correlation_id": "corr_uuid"
}

Response:
{
  "incident_id": "inc_uuid",
  "title": "MRI Scanner display flickering",
  "description": "...",
  "status": "active",
  "priority": "P2_HIGH",
  "category": "HARDWARE_FAILURE",
  "device_id": "dev_uuid",
  "device_info": {
    # Full DeviceDTO from IC-001
  },
  "occurred_at": "2026-07-15T08:30:00Z",
  "detected_at": "2026-07-15T08:45:00Z",
  "symptoms": [...],
  "investigation": {
    "phase": "DATA_COLLECTION",
    "findings": [...],
    "actions": [...]
  },
  "resolution": null,  # Not yet resolved
  "related_incidents": [...],
  "knowledge_articles": [...],  # From KnowledgeContext
  "previous_incidents_for_device": [...]  # Historical pattern
}
```

#### RC-002: GetDeviceKnowledgeContext
```
Source: RecommendationContext
Target: DeviceContext + KnowledgeContext
Type: Synchronous Query (Fan-out)

Request:
{
  "command_type": "RC-002_GetDeviceKnowledgeContext",
  "device_id": "dev_uuid",
  "tenant_id": "tenant_uuid",
  "incident_category": "HARDWARE_FAILURE",
  "correlation_id": "corr_uuid"
}

Response:
{
  "device": {
    # Full DeviceDTO
  },
  "device_history": {
    "maintenance_records": [...],
    "calibration_history": [...],
    "incident_history": [...]  # Last 10 incidents
  },
  "knowledge_articles": [
    # List of KnowledgeDTOs relevant to this device and category
  ]
}
```

#### KC-001: GetActiveRecommendations
```
Source: KnowledgeContext
Target: RecommendationContext
Type: Synchronous Query

Request:
{
  "command_type": "KC-001_GetActiveRecommendations",
  "knowledge_article_id": "kno_uuid",
  "tenant_id": "tenant_uuid",
  "correlation_id": "corr_uuid"
}

Response:
{
  "article_id": "kno_uuid",
  "active_recommendations": [
    {
      "recommendation_id": "rec_uuid",
      "title": "...",
      "status": "pending",
      "accepted_by": "eng_uuid",
      "device_id": "dev_uuid"
    }
  ]
}
```

### 4.3 Commands Asíncronos (Fire-and-Forget con Confirmación via Event)

#### IC-003: LinkIncidentToDevice
```
Source: IncidentContext
Target: DeviceContext
Type: Asynchronous Command
Broker: RabbitMQ
Exchange: device.commands
Routing Key: device.incident.link

Command Message:
{
  "message_type": "Command",
  "command_type": "IC-003_LinkIncidentToDevice",
  "message_id": "msg_uuid",
  "tenant_id": "tenant_uuid",
  "payload": {
    "device_id": "dev_uuid",
    "incident_id": "inc_uuid",
    "linked_by": "eng_uuid",
    "reason": "Device malfunction reported"
  },
  "correlation_id": "corr_uuid",
  "causation_id": "inc_uuid",
  "timestamp": "2026-07-15T10:00:00Z",
  "reply_to": "incident.events"
}

Consumer: DeviceContext.IncidentLinkHandler
  Steps:
    1. Load Device aggregate
    2. Validate device exists and is active
    3. Add incident reference to device metadata
    4. Persist
    5. Emit DeviceIncidentLinkedEvent
```

#### IC-004: UpdateDeviceStatusFromIncident
```
Source: IncidentContext
Target: DeviceContext
Type: Asynchronous Command
Routing Key: device.status.update

Command Payload:
{
  "device_id": "dev_uuid",
  "incident_id": "inc_uuid",
  "action": "TAKE_OUT_OF_SERVICE",  # or RESTORE_SERVICE
  "reason": "Incident requires device to be taken offline",
  "priority": "P2_HIGH",
  "performed_by": "eng_uuid"
}
```

#### RC-003: TriggerRecommendationGeneration
```
Source: IncidentContext
Target: RecommendationContext
Type: Asynchronous Command
Routing Key: recommendation.commands.generate

Command Payload:
{
  "incident_id": "inc_uuid",
  "tenant_id": "tenant_uuid",
  "triggered_by": "system",  # or "eng_uuid"
  "generation_mode": "automatic",  # or "on_demand"
  "max_recommendations": 5,
  "include_explanations": true,
  "context": {
    "device_ids": ["dev_uuid"],
    "category": "HARDWARE_FAILURE",
    "priority": "P2_HIGH"
  }
}
```

#### KC-002: CreateKnowledgeArticleFromIncident
```
Source: IncidentContext
Target: KnowledgeContext
Type: Asynchronous Command
Routing Key: knowledge.commands.create_from_incident

Command Payload:
{
  "source_incident_id": "inc_uuid",
  "tenant_id": "tenant_uuid",
  "suggested_category": "INCIDENT_REPORT",
  "author_id": "eng_uuid",
  "author_name": "System Auto-Generated",
  "title": "Incident INC-2024-00123: MRI Scanner resolution",
  "body_template": "INCIDENT_REPORT_TEMPLATE",
  "include_resolution": true,
  "include_symptoms": true,
  "include_actions_taken": true,
  "include_root_cause": true
}
```

### 4.4 Sagas (Transacciones Largas Cross-Context)

#### Saga 1: New Device Registration with Incident Link

```
Saga Name: DeviceRegistrationSaga
Coordinator: DeviceContext
Participants: DeviceContext (primary), IncidentContext, KnowledgeContext

Steps:
  1. DeviceContext.register_device(cmd)
     -> Creates Device (status=REGISTERED)
     -> Emits DeviceRegisteredEvent
  
  2. IncidentContext consumes DeviceRegisteredEvent
     -> Check if there's a pending incident for this serial_number
     -> If found: Link incident to device
     -> Emit IncidentDeviceLinkedEvent
  
  3. KnowledgeContext consumes DeviceRegisteredEvent
     -> Query manufacturer manuals for this model
     -> Create suggested knowledge articles
     -> Emit KnowledgeArticlesSuggestedEvent
  
  4. DeviceContext completes activation
     -> Consumes IncidentDeviceLinkedEvent (optional check)
     -> Activates device
     -> Emits DeviceActivatedEvent
  
Compensation Actions:
  - If Step 2 fails: Unlink incident (soft)
  - If Step 3 fails: Log warning, saga continues
  - If Step 4 fails: Keep device in REGISTERED, alert ops

Timeout: 5 minutes
Retry: 3 attempts with backoff
```

#### Saga 2: Critical Incident Auto-Resolution

```
Saga Name: CriticalIncidentResolutionSaga
Coordinator: IncidentContext
Participants: IncidentContext, RecommendationContext, KnowledgeContext, DeviceContext

Steps:
  1. IncidentContext.resolve_incident(cmd)
     -> Status=RESOLVED
     -> Emit IncidentResolvedEvent
  
  2. RecommendationContext consumes IncidentResolvedEvent
     -> Check all pending recommendations
     -> Mark as CANCELLED (incident resolved without execution)
     -> Emit RecommendationsCancelledEvent
  
  3. KnowledgeContext consumes IncidentResolvedEvent
     -> Create incident report article
     -> Link to device and category
     -> Emit KnowledgeArticleCreatedEvent
  
  4. DeviceContext consumes IncidentResolvedEvent
     -> If device was out_of_service: suggest restoration
     -> Emit DeviceRestoreSuggestionEvent
  
Compensation:
  - This saga is compensation-free (resolution is idempotent)
  - If Step 3 fails: Retry with backoff, DLQ after 3 failures

Timeout: 30 seconds
Retry: 5 attempts
```

---

## 5. QUERIES ENTRE CONTEXTOS

### 5.1 Query Overview

```
Query Pattern:
  - Name: {SourceContext}_GET_{Data}
  - All synchronous (HTTP/gRPC)
  - Response within 500ms SLA
  - Cached when appropriate (TTL per query type)
  - Circuit breaker: Open after 5 failures in 30 seconds
```

### 5.2 Query Definitions

#### Q-001: GetDeviceForIncident
```
Source: IncidentContext, RecommendationContext, AI Layer
Target: DeviceContext
Cache: 30 seconds (device status changes infrequently)
Rate Limit: 100/min per tenant

GET /api/v1/internal/tenants/{tenant_id}/devices/{device_id}
Headers:
  X-Correlation-ID: corr_uuid
  X-Tenant-ID: tenant_uuid

Response 200:
{
  "data": {
    "device_id": "dev_uuid",
    "tenant_id": "tenant_uuid",
    "device_name": "MRI Scanner Unit 3",
    "device_type": "mri",
    "device_type_category": "IMAGING",
    "risk_class": "CLASS_C",
    "status": "active",
    "location": {
      "building": "Main Hospital",
      "floor": "2",
      "room": "MRI-201",
      "department": "Radiology",
      "full_address": "Main Hospital, Floor 2, Room MRI-201"
    },
    "manufacturer": {
      "name": "Siemens Healthineers",
      "model": "MAGNETOM Vida 3T",
      "serial_number": "SN-2024-78945"
    },
    "calibration": {
      "is_current": true,
      "next_calibration_date": "2026-09-01T00:00:00Z",
      "days_until_due": 48
    },
    "maintenance": {
      "next_maintenance_date": "2026-10-01T00:00:00Z",
      "days_until_due": 78
    },
    "operational_status": {
      "is_operational": true,
      "uptime_percentage": 99.2,
      "has_open_incidents": false,
      "requires_attention": false
    },
    "connected_devices": [],
    "last_incident_date": "2026-06-15T00:00:00Z",
    "metadata": {}
  },
  "meta": {
    "version": 15,
    "cached_at": "2026-07-15T10:00:00Z",
    "ttl_seconds": 30
  }
}

Response 404: Device not found
Response 403: Tenant mismatch
```

#### Q-002: GetIncidentSummary
```
Source: RecommendationContext, AI Layer
Target: IncidentContext
Cache: No cache (incidents change frequently)
Rate Limit: 50/min per tenant

GET /api/v1/internal/tenants/{tenant_id}/incidents/{incident_id}/summary
Headers: X-Correlation-ID, X-Tenant-ID

Response 200:
{
  "incident": {
    "id": "inc_uuid",
    "tenant_id": "tenant_uuid",
    "title": "MRI Scanner display flickering",
    "status": "active",
    "priority": "P2_HIGH",
    "category": "HARDWARE_FAILURE",
    "safety_level": "CLASS_C",
    "device_id": "dev_uuid",
    "device_name": "MRI Scanner Unit 3",
    "device_location": "Main Hospital, Floor 2, MRI-201",
    "occurred_at": "2026-07-15T08:30:00Z",
    "detected_at": "2026-07-15T08:45:00Z",
    "assigned_to": {
      "engineer_id": "eng_uuid",
      "name": "Dr. Jane Smith"
    },
    "symptoms": [
      {
        "description": "Display flickers every 5-10 minutes",
        "severity": "moderate",
        "first_observed_at": "2026-07-15T08:30:00Z"
      }
    ],
    "investigation_phase": "DATA_COLLECTION",
    "open_recommendations_count": 3,
    "linked_knowledge_count": 2,
    "related_incidents_count": 1,
    "is_sla_breached": false,
    "sla_deadline": "2026-07-16T08:30:00Z"
  },
  "timeline": [
    {
      "event_type": "incident_reported",
      "timestamp": "2026-07-15T08:45:00Z",
      "actor": "eng_uuid",
      "description": "Incident reported"
    },
    {
      "event_type": "incident_triaged",
      "timestamp": "2026-07-15T09:00:00Z",
      "actor": "eng_uuid",
      "description": "Triaged as P2_HARDWARE_FAILURE"
    }
  ]
}
```

#### Q-003: SearchKnowledgeArticles
```
Source: RecommendationContext, AI Layer
Target: KnowledgeContext
Cache: 5 minutes (knowledge changes less frequently)
Rate Limit: 200/min per tenant

POST /api/v1/internal/tenants/{tenant_id}/knowledge/search
Headers: X-Correlation-ID, X-Tenant-ID
Body:
{
  "query": "MRI display flickering troubleshooting",
  "filters": {
    "categories": ["TROUBLESHOOTING", "DEVICE_MANUAL"],
    "device_types": ["mri"],
    "status": ["PUBLISHED"],
    "language": "en",
    "date_range": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2026-07-15T00:00:00Z"
    }
  },
  "pagination": {
    "page": 1,
    "page_size": 20
  },
  "include_body_preview": true,
  "body_preview_length": 300
}

Response 200:
{
  "results": [
    {
      "article_id": "kno_uuid",
      "article_number": "KB-00042",
      "title": "MRI Display Troubleshooting Guide",
      "summary": "Step-by-step guide for diagnosing display issues...",
      "category": "TROUBLESHOOTING",
      "status": "PUBLISHED",
      "tags": ["mri", "display", "troubleshooting"],
      "quality_score": 0.87,
      "helpfulness_ratio": 0.91,
      "device_ids": ["dev_mri_type"],
      "published_at": "2026-01-15T00:00:00Z",
      "author_name": "Biomedical Team",
      "body_preview": "Step 1: Check power supply connections...",
      "reading_time_minutes": 8,
      "relevance_score": 0.94,
      "matched_terms": ["display", "troubleshooting", "mri"]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_results": 5,
    "total_pages": 1
  },
  "facets": {
    "categories": {
      "TROUBLESHOOTING": 3,
      "DEVICE_MANUAL": 2
    },
    "tags": {
      "mri": 4,
      "display": 2
    }
  }
}
```

#### Q-004: GetRecommendationsForIncident
```
Source: IncidentContext, AI Layer
Target: RecommendationContext
Cache: No cache
Rate Limit: 30/min per tenant

GET /api/v1/internal/tenants/{tenant_id}/incidents/{incident_id}/recommendations
Headers: X-Correlation-ID, X-Tenant-ID

Response 200:
{
  "incident_id": "inc_uuid",
  "recommendations": [
    {
      "recommendation_id": "rec_uuid",
      "title": "Replace display cable assembly",
      "description": "...",
      "category": "HARDWARE_REPAIR",
      "urgency": "HIGH",
      "status": "pending",
      "confidence": {
        "value": 0.82,
        "level": "HIGH",
        "data_quality": 0.85,
        "model_confidence": 0.78,
        "evidence_sufficiency": 0.83
      },
      "explanation": {
        "reasoning_chain_summary": "Based on symptom pattern...",
        "safety_class": "CAUTION",
        "confidence_score": 0.82
      },
      "actions": [
        {
          "step_number": 1,
          "description": "Power off MRI unit",
          "estimated_minutes": 5
        }
      ],
      "sources": [
        {
          "type": "knowledge_article",
          "id": "KB-00042",
          "title": "MRI Display Troubleshooting"
        }
      ],
      "created_at": "2026-07-15T09:30:00Z",
      "expires_at": "2026-07-22T09:30:00Z"
    }
  ],
  "summary": {
    "total": 3,
    "pending": 2,
    "accepted": 1,
    "rejected": 0,
    "highest_confidence": 0.87,
    "average_confidence": 0.76
  }
}
```

---

## 6. INTEGRATION EVENTS

### 6.1 Event Naming Convention

```
Format: {EntityName}{Action}Event
Version: v{MAJOR}{MINOR}
Examples:
  - IncidentReportedEvent (v1)
  - IncidentReportedEventV2 (v2)
  - DeviceActivatedEvent
  - RecommendationAcceptedEvent

Fields (Mandatory for all):
  - event_id: UUID v7
  - event_type: string (full class name)
  - version: int (starts at 1)
  - occurred_at: UTC datetime
  - tenant_id: TenantId
  - correlation_id: UUID | null
  - causation_id: UUID | null
  - schema_url: URL to JSON schema
```

### 6.2 Event Catalog

#### IncidentContext → All

| Event | Trigger | Consumers | Priority |
|-------|---------|-----------|----------|
| `IncidentReportedEvent` | Nuevo incidente reportado | Device, Recommendation, Knowledge | HIGH |
| `IncidentTriagedEvent` | Incident triaged | Recommendation, Knowledge | MEDIUM |
| `IncidentOpenedEvent` | Incident abierto | Device | HIGH |
| `IncidentProgressedEvent` | Progreso registrado | Knowledge | LOW |
| `IncidentEscalatedEvent` | Escalamiento | Device, Recommendation, Knowledge | HIGH |
| `IncidentResolvedEvent` | Resuelto | Device, Recommendation, Knowledge | HIGH |
| `IncidentClosedEvent` | Cerrado | Knowledge | MEDIUM |
| `IncidentReopenedEvent` | Reabierto | Recommendation, Device | HIGH |
| `IncidentAssignedEvent` | Asignado | Knowledge | LOW |
| `IncidentSlaBreachedEvent` | SLA violado | Notification, Analytics | HIGH |

#### DeviceContext → All

| Event | Trigger | Consumers | Priority |
|-------|---------|-----------|----------|
| `DeviceRegisteredEvent` | Nuevo dispositivo | Incident, Knowledge | HIGH |
| `DeviceActivatedEvent` | Dispositivo activado | Incident | HIGH |
| `DeviceStatusChangedEvent` | Cambio de estado | Incident, Recommendation | HIGH |
| `DeviceLocationChangedEvent` | Relocalización | Incident, Knowledge | MEDIUM |
| `DeviceCalibrationDueEvent` | Calibración próxima | Incident, Notification | MEDIUM |
| `DeviceCalibrationOverdueEvent` | Calibración vencida | Incident, Notification | HIGH |
| `DeviceMaintenanceScheduledEvent` | Mantenimiento programado | Incident | MEDIUM |
| `DeviceMaintenanceCompletedEvent` | Mantenimiento completado | Incident | MEDIUM |
| `DeviceDecommissionedEvent` | Descomisionamiento | Incident (auto-close), Knowledge | HIGH |
| `DeviceUptimeUpdatedEvent` | Nuevo cálculo de uptime | Analytics | LOW |

#### RecommendationContext → All

| Event | Trigger | Consumers | Priority |
|-------|---------|-----------|----------|
| `RecommendationGeneratedEvent` | Nueva recomendación | Incident, Knowledge | HIGH |
| `RecommendationAcceptedEvent` | Aceptada | Incident, Knowledge | HIGH |
| `RecommendationRejectedEvent` | Rechazada | Incident | MEDIUM |
| `RecommendationCompletedEvent` | Ejecutada exitosamente | Incident, Knowledge | HIGH |
| `RecommendationFailedEvent` | Ejecución fallida | Incident, Knowledge | HIGH |
| `RecommendationFeedbackReceivedEvent` | Feedback recibido | Knowledge | MEDIUM |
| `RecommendationExpiredEvent` | Expirada | Incident | LOW |

#### KnowledgeContext → All

| Event | Trigger | Consumers | Priority |
|-------|---------|-----------|----------|
| `KnowledgeArticlePublishedEvent` | Artículo publicado | Recommendation, AI Layer | HIGH |
| `KnowledgeArticleUpdatedEvent` | Artículo actualizado | Recommendation (re-evaluate) | MEDIUM |
| `KnowledgeArticleArchivedEvent` | Artículo archivado | Recommendation (mark outdated) | MEDIUM |
| `KnowledgeArticleDeprecatedEvent` | Artículo deprecado | Recommendation | MEDIUM |
| `KnowledgeArticleQualityAlertEvent` | Baja calidad detectada | Knowledge Team | HIGH |

### 6.3 Event Schema Examples

```json
// IncidentReportedEvent (v1)
{
  "event_id": "0191a2b3c4d5e6f7a8b9c0d1e",
  "event_type": "IncidentReportedEvent",
  "version": 1,
  "occurred_at": "2026-07-15T08:45:00Z",
  "tenant_id": "tenant_uuid",
  "correlation_id": "corr_uuid",
  "causation_id": "inc_uuid",
  "schema_url": "https://schemas.eren.io/events/incident/v1/ReportedEvent.json",
  "payload": {
    "incident_id": "inc_uuid",
    "title": "MRI Scanner display flickering",
    "description": "...",
    "priority": "P2_HIGH",
    "safety_level": "CLASS_C",
    "category": "HARDWARE_FAILURE",
    "device_id": "dev_uuid",
    "device_name": "MRI Scanner Unit 3",
    "occurred_at": "2026-07-15T08:30:00Z",
    "detected_at": "2026-07-15T08:45:00Z",
    "reported_by": "eng_uuid",
    "patient_impact": "NO_IMPACT",
    "tags": ["mri", "display", "hardware"]
  }
}
```

### 6.4 Event Delivery Guarantees

```
Guarantees:
  - At-least-once delivery (not exactly-once)
  - Events are persisted in Outbox before publishing
  - Idempotency keys prevent duplicate processing
  - Events are immutable (never mutated after emit)

Ordering:
  - Within a partition/queue: FIFO
  - Across partitions: Not guaranteed
  - Correlation ID groups enable re-ordering at consumer level

Retry Policy:
  - Exponential backoff: 1s, 2s, 4s, 8s, 16s
  - Max 5 retries
  - After max retries: Dead Letter Queue

Dead Letter Queue:
  - Topic: {original_exchange}.dlq
  - Retention: 7 days
  - Alert after 10 messages in DLQ
```

### 6.5 Idempotency

```
Every event handler must:
  1. Check if event_id was already processed (idempotency table)
  2. If processed: skip silently, log as duplicate
  3. If not processed: process, then record event_id + processed_at

Idempotency Table Schema:
  CREATE TABLE idempotency_log (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(200),
    processed_at TIMESTAMPTZ NOT NULL,
    result VARCHAR(50),
    handler_id VARCHAR(200),
    INDEX idx_processed_at (processed_at)
  );

  Retention: 90 days
```

---

## 7. DTOs DE INTEGRACIÓN

### 7.1 DTO Naming Convention

```
Format: {Context}{Entity}DTO
Examples:
  - IncidentContextIncidentDTO (or shorter: IncidentDTO)
  - DeviceContextDeviceDTO (or shorter: DeviceDTO)
  - RecommendationContextRecommendationDTO (or shorter: RecommendationDTO)
  - KnowledgeContextArticleDTO (or shorter: KnowledgeArticleDTO)

Version suffix (breaking changes only):
  - IncidentDTOV2

Immutable: Todos los DTOs son inmutables
Serializable: Todos los campos son JSON-serializables
```

### 7.2 DTO Schemas

#### IncidentDTO
```json
{
  "incident_id": "string (UUID)",
  "tenant_id": "string (UUID)",
  "article_number": "string (INC-XXXXX)",
  "title": "string (max 200)",
  "description": "string (max 5000)",
  "status": "enum: REPORTED|TRIAGED|ACTIVE|ESCALATED|RESOLVED|CLOSED",
  "priority": "enum: P1_CRITICAL|P2_HIGH|P3_MEDIUM|P4_LOW",
  "safety_level": "enum: CLASS_A|CLASS_B|CLASS_C|CLASS_D",
  "category": "string",
  "device_id": "string (UUID) | null",
  "device_name": "string | null",
  "device_location": "string | null",
  "patient_impact": "string | null",
  "occurred_at": "string (ISO 8601 UTC)",
  "detected_at": "string (ISO 8601 UTC)",
  "reported_by": "string (EngineerId)",
  "assigned_to": "string (EngineerId) | null",
  "assigned_at": "string (ISO 8601 UTC) | null",
  "resolved_at": "string (ISO 8601 UTC) | null",
  "closed_at": "string (ISO 8601 UTC) | null",
  "symptoms": [
    {
      "description": "string",
      "severity": "enum: minor|moderate|severe|critical",
      "first_observed_at": "string (ISO 8601 UTC)"
    }
  ],
  "tags": ["string"],
  "version": "int",
  "created_at": "string (ISO 8601 UTC)",
  "updated_at": "string (ISO 8601 UTC)"
}
```

#### DeviceDTO
```json
{
  "device_id": "string (UUID)",
  "tenant_id": "string (UUID)",
  "serial_number": "string",
  "device_name": "string",
  "device_type": "string",
  "device_type_category": "string",
  "risk_class": "enum: CLASS_A|CLASS_B|CLASS_C|CLASS_D",
  "status": "enum: REGISTERED|ACTIVE|CALIBRATION_DUE|IN_MAINTENANCE|OUT_OF_SERVICE|DECOMMISSIONED",
  "location": {
    "building": "string",
    "floor": "string",
    "room": "string",
    "department": "string",
    "full_address": "string"
  },
  "manufacturer": {
    "name": "string",
    "model": "string"
  },
  "calibration": {
    "is_current": "boolean",
    "next_calibration_date": "string (ISO 8601 UTC) | null",
    "days_until_due": "int | null"
  },
  "maintenance": {
    "next_maintenance_date": "string (ISO 8601 UTC) | null",
    "days_until_due": "int | null"
  },
  "operational_status": {
    "is_operational": "boolean",
    "uptime_percentage": "float",
    "has_open_incidents": "boolean"
  },
  "warranty_expiry": "string (ISO 8601 UTC) | null",
  "installation_date": "string (ISO 8601 UTC) | null",
  "version": "int",
  "created_at": "string (ISO 8601 UTC)"
}
```

#### RecommendationDTO
```json
{
  "recommendation_id": "string (UUID)",
  "tenant_id": "string (UUID)",
  "incident_id": "string (UUID) | null",
  "title": "string (max 200)",
  "description": "string (max 3000)",
  "category": "string",
  "urgency": "enum: LOW|NORMAL|HIGH|CRITICAL",
  "status": "enum: GENERATED|PENDING|ACCEPTED|REJECTED|ACTIVE|COMPLETED|EXPIRED|CANCELLED",
  "confidence": {
    "value": "float [0.0-1.0]",
    "level": "enum: VERY_LOW|LOW|MEDIUM|HIGH|VERY_HIGH",
    "data_quality": "float",
    "model_confidence": "float",
    "evidence_sufficiency": "float",
    "historical_accuracy": "float"
  },
  "explanation": {
    "reasoning_chain_summary": "string",
    "safety_class": "enum: SAFE|CAUTION|WARNING|CRITICAL|UNSAFE",
    "risk_factors": ["string"],
    "confidence_score": "float",
    "human_review_required": "boolean",
    "ai_disclosure": "string"
  },
  "actions": [
    {
      "step_number": "int",
      "description": "string",
      "estimated_minutes": "int | null",
      "safety_notes": "string | null"
    }
  ],
  "evidence": [
    {
      "evidence_type": "string",
      "content_summary": "string",
      "source_name": "string",
      "relevance_score": "float"
    }
  ],
  "sources": [
    {
      "source_type": "string",
      "source_id": "string",
      "title": "string",
      "url": "string | null"
    }
  ],
  "device_ids": ["string (UUID)"],
  "knowledge_article_ids": ["string (UUID)"],
  "generated_by": "string (AI model identifier)",
  "generation_method": "string",
  "created_at": "string (ISO 8601 UTC)",
  "expires_at": "string (ISO 8601 UTC) | null"
}
```

#### KnowledgeArticleDTO
```json
{
  "article_id": "string (UUID)",
  "tenant_id": "string (UUID)",
  "article_number": "string (KB-XXXXX)",
  "title": "string (max 300)",
  "summary": "string (max 500)",
  "body": "string (max 50000) | null (null if include_body=false)",
  "body_preview": "string (max 500) | null",
  "content_format": "enum: MARKDOWN|HTML|PLAIN",
  "category": "string",
  "status": "enum: DRAFT|IN_REVIEW|APPROVED|PUBLISHED|ARCHIVED|DEPRECATED",
  "tags": ["string"],
  "device_ids": ["string (UUID)"],
  "device_types": ["string"],  # Device types this article applies to
  "incident_type_tags": ["string"],
  "author_name": "string",
  "published_at": "string (ISO 8601 UTC) | null",
  "quality_score": "float | null",
  "helpfulness_ratio": "float | null",
  "view_count": "int",
  "helpful_count": "int",
  "language": "string (ISO 639-1)",
  "reading_time_minutes": "int",
  "difficulty_level": "enum: BEGINNER|INTERMEDIATE|ADVANCED|EXPERT",
  "references": [
    {
      "reference_type": "string",
      "reference_id": "string",
      "title": "string",
      "url": "string | null"
    }
  ],
  "related_article_ids": ["string (UUID)"],
  "superseded_by": "string (UUID) | null",
  "version": "int",
  "created_at": "string (ISO 8601 UTC)",
  "updated_at": "string (ISO 8601 UTC)"
}
```

---

## 8. PROTOCOLO DE VERSIONADO

### 8.1 Versionado de DTOs

```
MAJOR.MINOR.PATCH

MAJOR (X.0.0):
  - Breaking changes
  - Removed fields
  - Changed field types
  - Changed field semantics
  - Requires: API version bump, consumer migration
  - Deprecation: 2 major versions

MINOR (0.X.0):
  - Additive changes (new fields)
  - New optional fields default to null/empty
  - Consumers ignoring unknown fields work unchanged
  - Requires: API minor version bump
  - No consumer migration needed

PATCH (0.0.X):
  - Bug fixes, documentation changes
  - No API change
  - No consumer migration needed
```

### 8.2 Versionado de Eventos

```
Event Versioning Rules:
  1. Never remove fields from events (backward compatibility)
  2. Never change the meaning of existing fields
  3. Only ADD optional fields
  4. Major version bump only for structural changes
  5. Consumers must ignore unknown fields (Forward compatibility)
  6. Producers must include all known fields (Backward compatibility)

Version Header: X-Event-Version: 1
Schema Registry: Confluent Schema Registry or custom
Schema Storage: S3 with versioned paths
```

### 8.3 Compatibility Matrix

```
Producer: IncidentContext v2
Consumers:
  DeviceContext: v2 ✅ (full compatibility)
  RecommendationContext: v1-v2 ✅ (v1 fields preserved)
  KnowledgeContext: v1-v2 ✅
  AI Layer: v1-v2 ✅

If breaking change needed:
  1. Emit new versioned event name: IncidentReportedEventV2
  2. Keep v1 running for 2 major versions
  3. Emit BOTH v1 and v2 during transition
  4. Consumers migrate at their pace
  5. Remove v1 after migration complete
```

### 8.4 Deprecation Policy

```
DTO Field Deprecation:
  1. Mark field as deprecated in schema (add @deprecated annotation)
  2. Continue emitting field for 1 major version
  3. Emit warning in response headers
  4. Remove field in next major version

Event Deprecation:
  1. Mark event type as deprecated
  2. Emit deprecation notice in consumer headers
  3. Continue emitting for 2 major versions
  4. Remove in next major version

Entire Event/Command:
  1. Publish deprecation notice in schema registry
  2. Emit both old and new for 1 version
  3. Remove old after migration window
```

---

*Documento generado para implementación. Fase 2 completa.*
