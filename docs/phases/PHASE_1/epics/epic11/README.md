# EREN Epic 11 — Domain AI Integration

*Version 1.0 - 2026-07-20*

**Preparar la capa de dominio para el AI Core.**

Epic 11 implementa la capa de servicios de aplicación para desacoplar el dominio de negocio del AI Core.

---

## Objetivo

Crear una fachada oficial entre el dominio de negocio (FASE 1) y el AI Core (FASE 2) que:

- Exponga repositorios como Query Services
- Convierta casos de uso en servicios reutilizables
- Exponga eventos públicos para la IA
- Proporcione DTOs específicos para consumo de AI
- Elimine acoplamientos directos entre capas
- Respete DDD, Clean Architecture, SOLID y CQRS

---

## Dependencias

- **FASE 1** (Todos los bounded contexts) - ✅ COMPLETO
- **EPIC 0** (Arquitectura) - ✅ COMPLETO
- **EPIC 7** (APIs base) - ✅ COMPLETO

---

## Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           FASE 2: AI CORE                                                  │
│                                                                                          │
│  AICoreController                                                                          │
│       │                                                                                   │
│       ▼                                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │              TOOL ORCHESTRATOR (EPIC 5)                                           │   │
│  │  - DomainTool (herramientas que acceden al dominio)                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Tool Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      CORE/APPLICATION/SERVICES (EPIC 11)                                   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      QUERY SERVICES (Read Operations)                            │   │
│  │  - DeviceQueryService                                                           │   │
│  │  - IncidentQueryService                                                         │   │
│  │  - KnowledgeQueryService                                                        │   │
│  │  - RecommendationQueryService                                                   │   │
│  │  - WorkOrderQueryService                                                        │   │
│  │  - HospitalQueryService                                                         │   │
│  │  - StaffQueryService                                                           │   │
│  │  - AssetQueryService                                                           │   │
│  │  - InventoryQueryService                                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      COMMAND SERVICES (Write Operations)                           │   │
│  │  - DeviceCommandService                                                         │   │
│  │  - IncidentCommandService                                                       │   │
│  │  - KnowledgeCommandService                                                      │   │
│  │  - RecommendationCommandService                                                 │   │
│  │  - WorkOrderCommandService                                                      │   │
│  │  - ClinicalCommandService                                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      DOMAIN SERVICES (Business Logic)                             │   │
│  │  - CDSSService                                                                  │   │
│  │  - RCAAnalysisService                                                           │   │
│  │  - DiagnosisService                                                            │   │
│  │  - TroubleshootingService                                                       │   │
│  │  - PredictionService                                                            │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      EVENT SERVICES (Domain Events)                               │   │
│  │  - EventQueryService                                                            │   │
│  │  - EventSubscriptionService                                                     │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Repository Interface
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           FASE 1: BUSINESS DOMAIN                                           │
│                                                                                          │
│  Device │ Incident │ Knowledge │ Recommendation │ WorkOrder │ Hospital │ Clinical        │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │              DOMAIN LAYER (No changes)                                            │   │
│  │  - Entities (Device, Incident, etc.)                                            │   │
│  │  - Value Objects                                                                │   │
│  │  - Domain Services                                                              │   │
│  │  - Repository Interfaces (ABC)                                                  │   │
│  │  - Domain Events                                                                │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │              INFRASTRUCTURE LAYER (No changes)                                    │   │
│  │  - Repository Implementations                                                    │   │
│  │  - Database Access                                                              │   │
│  │  - External Services                                                            │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes a Implementar

### 1. Query Services (Read Operations - CQRS)

| Servicio | Responsabilidad | Métodos |
|----------|----------------|---------|
| `DeviceQueryService` | Consulta de dispositivos | get_device, list_devices, get_by_status, get_critical, get_needing_maintenance |
| `IncidentQueryService` | Consulta de incidentes | get_incident, list_incidents, get_open, get_by_device, get_by_engineer |
| `KnowledgeQueryService` | Consulta de conocimiento | search_knowledge, get_article, get_by_category, get_by_device, get_related |
| `RecommendationQueryService` | Consulta de recomendaciones | get_recommendations, get_pending, get_by_confidence |
| `WorkOrderQueryService` | Consulta de órdenes | get_work_order, get_pending, get_sla_breached |
| `HospitalQueryService` | Consulta hospitalaria | get_campus, get_building, get_room, get_bed, get_capacity |
| `StaffQueryService` | Consulta de personal | get_staff, get_by_role, get_by_shift |
| `AssetQueryService` | Consulta de activos | get_asset, get_by_contract, get_expiring |
| `InventoryQueryService` | Consulta de inventario | get_item, get_low_stock, get_by_supplier |

### 2. Command Services (Write Operations - CQRS)

| Servicio | Responsabilidad | Métodos |
|----------|----------------|---------|
| `DeviceCommandService` | Comandos de dispositivo | register_device, update_status, transfer_device, schedule_maintenance |
| `IncidentCommandService` | Comandos de incidente | create_incident, triage_incident, escalate_incident, resolve_incident |
| `KnowledgeCommandService` | Comandos de conocimiento | create_article, update_article, publish_article |
| `RecommendationCommandService` | Comandos de recomendación | generate_recommendation, accept_recommendation, reject_recommendation |
| `WorkOrderCommandService` | Comandos de orden | create_work_order, assign_work_order, complete_work_order |
| `ClinicalCommandService` | Comandos clínicos | add_knowledge_base, update_rules |

### 3. Domain Services (AI-Ready)

| Servicio | Responsabilidad | Métodos |
|----------|----------------|---------|
| `CDSSService` | Clinical Decision Support | get_recommendations, analyze_device |
| `RCAAnalysisService` | Root Cause Analysis | analyze_root_cause, get_contributing_factors |
| `DiagnosisService` | Differential Diagnosis | get_differential_diagnosis, rank_diagnoses |
| `TroubleshootingService` | Troubleshooting Guide | get_troubleshooting_steps, get_next_step |
| `PredictionService` | Predictive Analytics | predict_failure, assess_risk |

### 4. Event Services

| Servicio | Responsabilidad | Métodos |
|----------|----------------|---------|
| `EventQueryService` | Consulta de eventos | get_events, get_by_type, get_by_entity |
| `EventSubscriptionService` | Suscripción a eventos | subscribe, unsubscribe, get_subscriptions |

---

## Ubicación de Implementación

```
core/application/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── query/
│   │   ├── __init__.py
│   │   ├── device_query_service.py
│   │   ├── incident_query_service.py
│   │   ├── knowledge_query_service.py
│   │   ├── recommendation_query_service.py
│   │   ├── work_order_query_service.py
│   │   ├── hospital_query_service.py
│   │   ├── staff_query_service.py
│   │   ├── asset_query_service.py
│   │   └── inventory_query_service.py
│   ├── command/
│   │   ├── __init__.py
│   │   ├── device_command_service.py
│   │   ├── incident_command_service.py
│   │   ├── knowledge_command_service.py
│   │   ├── recommendation_command_service.py
│   │   ├── work_order_command_service.py
│   │   └── clinical_command_service.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── cdss_service.py
│   │   ├── rca_analysis_service.py
│   │   ├── diagnosis_service.py
│   │   ├── troubleshooting_service.py
│   │   └── prediction_service.py
│   └── events/
│       ├── __init__.py
│       ├── event_query_service.py
│       └── event_subscription_service.py
├── dto/
│   ├── __init__.py
│   ├── device_dtos.py
│   ├── incident_dtos.py
│   ├── knowledge_dtos.py
│   ├── recommendation_dtos.py
│   ├── work_order_dtos.py
│   ├── hospital_dtos.py
│   ├── clinical_dtos.py
│   └── event_dtos.py
└── interfaces/
    ├── __init__.py
    ├── query_service_interface.py
    ├── command_service_interface.py
    └── domain_service_interface.py
```

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-11000 | Domain AI Integration Architecture | 📋 PENDING |
| ADR-11001 | Query Services Design | 📋 PENDING |
| ADR-11002 | Command Services Design | 📋 PENDING |
| ADR-11003 | DTO Design for AI | 📋 PENDING |
| ADR-11004 | Event Exposure Strategy | 📋 PENDING |
| ADR-11005 | Dependency Inversion | 📋 PENDING |

---

## Auditoría de Componentes

### Componentes Analizados

| Módulo | Repositorio | Query Service | Command Service | Eventos | DTOs |
|--------|-------------|---------------|-----------------|---------|------|
| Device | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Incident | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Knowledge | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Recommendation | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| WorkOrder | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Capacity | ✅ Interface | ❌ Falta | ❌ Falta | ✅ Defined | ❌ Falta |
| Staffing | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Organization | ✅ Interface | ❌ Falta | ❌ Falta | ❌ Falta | ❌ Falta |
| Department | ✅ Interface | ❌ Falta | ❌ Falta | ❌ Falta | ❌ Falta |
| Inventory | ✅ Interface | ❌ Falta | ❌ Falta | ⚠️ Partial | ❌ Falta |
| Asset | ✅ Interface | ❌ Falta | ❌ Falta | ❌ Falta | ❌ Falta |
| Clinical | ⚠️ Engine only | ❌ Falta | ❌ Falta | ❌ Falta | ❌ Falta |

---

## Status

**Epic 11 Status:** 📋 DESIGN PHASE

> Este documento contiene el diseño arquitectónico. La implementación se realizará en fases.

---

## EPIC Roadmap Status

**FASE 1.1 (Domain AI Integration):**

| EPIC | Status | Descripción |
|------|--------|-------------|
| EPIC 0-10 | ✅ COMPLETE | FASE 1 Original |
| **EPIC 11 (Domain AI Integration)** | 📋 DESIGN | Fachada de dominio para AI |

---

*EREN Epic 11 v1.0 - Domain AI Integration*
*Architecture Board - 2026-07-20*
