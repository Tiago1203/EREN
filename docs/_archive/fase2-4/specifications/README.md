# EREN - Especificación Técnica Completa

> **Proyecto:** EREN - Clinical Engineering Decision Support Platform  
> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  

---

## Objetivo

Este repositorio contiene la especificación técnica completa y exhaustiva para la implementación de EREN. Cada decisión arquitectónica está documentada y justificada. Un equipo de desarrollo puede implementar EREN sin necesidad de tomar decisiones arquitectónicas adicionales.

---

## Arquitectura General

```
EREN es una plataforma de Clinical Engineering Decision Support
construida con Domain-Driven Design (DDD) y Clean Architecture.

Core Domain: Clinical Engineering Decision Support
  - Incident Context: Gestión de incidentes de ingeniería clínica
  - Device Context: Gestión de dispositivos biomédicos
  - Recommendation Context: Recomendaciones de IA con explicabilidad
  - Knowledge Context: Base de conocimientos técnicos
  - Shared Kernel: Bloques de construcción compartidos

AI Layer: Orquestación (NO dominio)
  - Conversation Controller
  - Reasoning Engine
  - Prompt Builder
  - Memory Manager
  - Safety Engine
  - Confidence Engine
  - Explainability Engine
  - RAG Orchestrator
  - Knowledge Retriever
  - Response Composer
```

---

## Índice de Especificaciones

### Fase 1: Domain Model
📄 **01-DOMAIN-MODEL.md**

Diseño completo de los bounded contexts:

| Bounded Context | Aggregate Root | Entidades | Value Objects |
|-----------------|---------------|-----------|--------------|
| Shared Kernel | - | BaseEntity, AggregateRoot | EntityIds, Priority, SafetyLevel, Confidence |
| Incident | EngineeringIncident | Investigation | IncidentStatus, Symptom, Resolution, Priority |
| Recommendation | AIRecommendation | - | RecommendationStatus, Confidence, Explanation |
| Device | Device | - | DeviceStatus, DeviceType, LocationInfo, CalibrationInfo |
| Knowledge | KnowledgeArticle | - | KnowledgeStatus, Category, ReviewInfo |

Incluye:
- State machines completas
- Business rules
- Invariants
- Domain services
- Repository interfaces
- Cross-context integration model

---

### Fase 2: Cross-Context Contracts
📄 **02-CROSS-CONTEXT-CONTRACTS.md**

Contratos entre bounded contexts:

- **Published Language:** Vocabulario compartido
- **Anti-Corruption Layer:** Traducción entre contextos
- **Commands:** IC-001 a IC-004, RC-001 a RC-003, KC-001 a KC-002
- **Queries:** Q-001 a Q-004 (incluyendo cache strategy)
- **Integration Events:** Catálogo completo de eventos cross-context
- **DTOs:** IncidentDTO, DeviceDTO, RecommendationDTO, KnowledgeArticleDTO
- **Saga Patterns:** DeviceRegistrationSaga, CriticalIncidentResolutionSaga
- **Protocolo de Versionado:** SemVer para eventos y DTOs

---

### Fase 3: AI Layer
📄 **03-AI-LAYER.md**

Arquitectura completa de la capa de orquestación de IA:

| Componente | Responsabilidad |
|-----------|----------------|
| ConversationController | Control de flujo conversacional |
| ReasoningEngine | Estrategias de razonamiento (ChainOfThought, SafetyFirst, EvidenceBased) |
| PromptBuilder | Construcción de prompts optimizados |
| MemoryManager | Memoria de trabajo, episódica y semántica |
| ContextBuilder | Agregación de contexto desde múltiples fuentes |
| SafetyEngine | Validación de seguridad clínica |
| ConfidenceEngine | Cálculo de confianza desglosado |
| ExplainabilityEngine | Generación de explicaciones |
| FeedbackEngine | Procesamiento de feedback |
| RAGOrchestrator | Pipeline RAG completo |
| ToolOrchestrator | Gestión de herramientas disponibles |
| KnowledgeRetriever | Recuperación de conocimiento |
| ResponseComposer | Composición de respuestas por rol |

Incluye diagrama de secuencia completo para recommendation generation.

---

### Fase 4: Explainability
📄 **04-EXPLAINABILITY.md**

Sistema completo de explicabilidad para recomendaciones:

- **Reasoning Chain:** Modelo completo con ReasoningStep, AlternativePath
- **Evidence Model:** Jerarquía de evidencia, calidad, confiabilidad
- **Sources & Citations:** Source model, Citation model, formatos (APA, Hospital, Regulatory)
- **Confidence Calculation:** Fórmula completa con componentes
- **Provenance Tracking:** Lineage completo desde inputs hasta output
- **Safety Classification:** 5 niveles de seguridad clínica
- **Evidence Ranking:** Algoritmo de ranking con detección de conflictos
- **Format Outputs:** 4 niveles de explicabilidad (Summary, Clinical, Engineering, Audit)

Incluye ejemplos completos de reasoning chain y formatos de salida.

---

### Fase 5: Modelo Conversacional
📄 **05-CONVERSATIONAL-MODEL.md**

Sistema completo de conversación:

- **Conversation Model:** Entities, threads, sessions
- **Message Types:** 20+ tipos de mensajes (USER, AI, SYSTEM, TOOL)
- **Memory Architecture:** 4 capas (working, episodic, semantic, cross-session)
- **Tool Calls:** Modelo completo con display en conversación
- **Context Window Management:** Budget de 128K tokens, overflow strategies
- **Persistence:** 3 tiers (Redis hot, PostgreSQL warm, S3 cold)
- **Auto-Summary:** Triggers y generación de resúmenes

---

### Fase 6: Sistema de Eventos
📄 **06-EVENT-SYSTEM.md**

Arquitectura de eventos completa:

- **Domain Events:** Catálogo de ~35 eventos
- **Integration Events:** Estructura y mapeo cross-context
- **Outbox Pattern:** Implementación completa con PostgreSQL
- **Event Versioning:** SemVer con modos de compatibilidad
- **Naming Conventions:** Estándares para tipos, routing keys, exchanges
- **Idempotencia:** Tabla y handler de idempotencia
- **Ordering:** Guarantees y partition strategy
- **Retries & DLQ:** Política de retry, backoff, DLQ table
- **Schema Registry:** Almacenamiento y validación de schemas
- **Monitoring:** Métricas Prometheus y alertas

---

### Fase 7: Persistence
📄 **07-PERSISTENCE.md**

Diseño de base de datos:

- **PostgreSQL 16+** con extensiones (pg_trgm, uuid-ossp)
- **~30 tablas** con schemas completos (incidents, devices, recommendations, knowledge, outbox, audit_log)
- **Indexes** optimizados para queries comunes
- **Multi-tenancy** con Row-Level Security
- **Soft Delete** con triggers
- **Audit Log** immutable
- **Constraints** para integridad de datos

---

### Fase 8: APIs
📄 **08-APIS.md**

Diseño de APIs REST:

- **~40 endpoints** completos con schemas
- **Internal APIs** para comunicación service-to-service
- **Request/Response DTOs** con validación (Pydantic)
- **Error Handling:** Códigos de error estandarizados
- **Versioning Strategy:** URL versioning con backward compatibility

---

### Fase 9: Seguridad
📄 **09-SECURITY.md**

Sistema de seguridad completo:

- **Authentication:** OAuth2, JWT, MFA
- **RBAC:** 5 roles con permisos granulares
- **Multi-tenant Isolation:** Row-Level Security, token isolation
- **Clinical Safety:** AI safety, human-in-the-loop
- **Prompt Injection Protection:** Sanitización, immutability
- **Audit:** Trail completo de acciones
- **Secret Management:** HashiCorp Vault

---

### Fase 10: Observabilidad
📄 **10-OBSERVABILITY.md**

Sistema de observabilidad:

- **Logging:** Formato JSON estructurado, correlación
- **Tracing:** OpenTelemetry, distributed tracing
- **Metrics:** ~40 métricas de negocio + sistema
- **Alerting:** ~15 alertas configuradas

---

### Fase 11: Testing
📄 **11-TESTING.md**

Estrategia de testing completa:

- **Pyramid:** 1000 unit + 200 integration + 100 contract + 50 E2E
- **Unit Tests:** Patrón Given-When-Then, builders
- **Integration Tests:** Testcontainers
- **Contract Tests:** Pact
- **E2E Tests:** Playwright, critical user journeys

---

### Fase 12: Roadmap de Implementación
📄 **12-IMPLEMENTATION-ROADMAP.md**

 roadmap de implementación:

- **10 épicas** con sprints, deliverables, definition of done
- **MVP en 10 meses** (40 sprints)
- **~45 PRs** planeadas
- **Cronograma:** 20 meses para plataforma completa
- **Equipo:** 4 FTE recomendados
- **Riesgos:** Identificados y con mitigación

---

## Principios Arquitectónicos

1. **DDD:** Cada bounded context es independiente y tiene su propio modelo de dominio
2. **Clean Architecture:** Separación clara de concerns (domain → application → infrastructure)
3. **Event-Driven:** Eventos como primitivo de comunicación cross-context
4. **CQRS:** Preparado para separar commands y queries
5. **Outbox Pattern:** Consistencia eventual garantizada
6. **Optimistic Locking:** Control de concurrencia en aggregates
7. **Multi-tenancy desde el inicio:** Row-Level Security
8. **Clinical Safety First:** AI como herramienta de soporte, no como decisor
9. **Explainability:** Toda recomendación de AI debe ser completamente explicable
10. **Audit Everything:** Logging completo para compliance

---

## Cómo Usar Esta Especificación

### Para el Tech Lead
- Leer todas las fases en orden
- Tomar decisiones de stack tecnológico alineadas con la especificación
- Planificar sprints basándose en el roadmap

### Para el Backend Developer
- Comenzar con Fase 1 (Domain Model) para entender el modelo de dominio
- Usar Fase 7 (Persistence) para schemas de base de datos
- Usar Fase 8 (APIs) para endpoints
- Usar Fase 6 (Event System) para mensajería

### Para el AI Engineer
- Leer Fase 3 (AI Layer) para entender la arquitectura
- Leer Fase 4 (Explainability) para el sistema de explicabilidad
- Leer Fase 5 (Conversational Model) para el sistema de conversación

### Para el QA Engineer
- Leer Fase 11 (Testing) para la estrategia de tests
- Usar las especificaciones para escribir criterios de aceptación

---

## Supuestos Declarados

1. PostgreSQL 16+ como base de datos primary
2. RabbitMQ como message broker (Kafka en v2)
3. OpenAI GPT-4o como LLM primary (Claude como fallback)
4. Kubernetes como plataforma de orquestación
5. OAuth2/JWT para autenticación
6. HashiCorp Vault para secrets management
7. Azure AD como identity provider primary
8. 20 meses para implementación completa
9. 4 desarrolladores para MVP

---

*Especificación generada para implementación. Cada decisión está completamente justificada y documentada.*
