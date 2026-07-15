# EREN Architecture Blueprint
## Technical Architecture for a Cognitive Hospital Operating System

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-15 | Architecture Board | Initial draft |

---

## Overview

This document defines the technical architecture of EREN based on:
- [EREN Philosophy](./EREN_PHILOSOPHY.md)
- [Three Domains Model](./EREN_THREE_DOMAINS.md)
- [Cognitive Model](./EREN_COGNITIVE_MODEL.md)
- [Capability Map](./EREN_CAPABILITY_MAP.md)
- [Capability Dependencies](./EREN_CAPABILITY_DEPENDENCIES.md)

---

## Architectural Principles

### 1. Philosophy First

Every architectural decision must align with EREN's philosophy:
- EREN never replaces the professional
- EREN always explains decisions
- EREN always shows evidence
- EREN measures uncertainty

### 2. Domain-Driven Design

EREN operates at the intersection of three bounded contexts:
- **Clinical Domain**: Patient care decisions
- **Biomedical Domain**: Medical device management
- **Hospital Domain**: Operational optimization

### 3. Contract-First

```
Architecture Rule: Contracts before Implementations

Before writing any code:
1. Define the contract (interface)
2. Define the models
3. Define the events
4. THEN implement
```

### 4. Capability-Oriented

Modules are organized by capability, not by technical layer:
```
✅ Correct: core/capabilities/trust/
❌ Wrong: core/services/providers/
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          EREN OS                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   COGNITIVE RUNTIME                         │   │
│  │                                                              │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │
│  │  │Perceive │  │Remember │  │  Know   │  │  Trust  │       │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘       │   │
│  │       │            │            │            │              │   │
│  │       └────────────┴──────┬─────┴────────────┘              │   │
│  │                           │                                 │   │
│  │       ┌──────────────────┼──────────────────┐            │   │
│  │       │                  ↓                  │            │   │
│  │  ┌────▼────┐      ┌─────────┐      ┌────▼────┐         │   │
│  │  │AssessRisk│←────│ Reason  │────→│ Decide  │         │   │
│  │  └────┬────┘      └────┬────┘      └────┬────┘         │   │
│  │       │                │                │              │   │
│  │       └────────────────┼────────────────┘              │   │
│  │                          ↓                               │   │
│  │                    ┌─────────┐                          │   │
│  │                    │ Explain │                          │   │
│  │                    └────┬────┘                          │   │
│  │                          ↓                               │   │
│  │                    ┌─────────┐                          │   │
│  │                    │  Learn  │                          │   │
│  │                    └─────────┘                          │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         CAPABILITY LAYER                             │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │  SECURITY   │  │  CLINICAL  │  │ BIOMEDICAL │               │
│  │             │  │             │  │             │               │
│  │ Identity    │  │ ClinicalCtx │  │ DeviceReg   │               │
│  │ Authorization│  │ DecisionSup│  │ AlarmMgmt  │               │
│  │ Audit       │  │ DrugInteract│  │ Calibration │               │
│  │ Encryption  │  │ EvidenceRet │  │ MaintSched  │               │
│  │ Policy      │  │ Diagnostics │  │ AssetTrack │               │
│  │ Compliance  │  │ Treatment   │  │ RiskAsssess │               │
│  └─────────────┘  └─────────────┘  └─────────────┘               │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │  HOSPITAL   │  │ INTEGRATION │  │    KNOW     │               │
│  │             │  │             │  │             │               │
│  │ HospitalTwin│  │ FHIR        │  │ KnowledgeGr │               │
│  │ Capacity    │  │ HL7         │  │ RAG         │               │
│  │ Inventory   │  │ DICOM       │  │ Embeddings  │               │
│  │ Staffing    │  │ MQTT        │  │ VectorStore │               │
│  │ Scheduling  │  │ REST        │  │ GraphDB     │               │
│  │ Analytics   │  │ Webhooks    │  │ EvidenceBase│               │
│  └─────────────┘  └─────────────┘  └─────────────┘               │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                         INFRASTRUCTURE LAYER                         │
│                                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │  EVENT   │  │  RUNTIME │  │  STORAGE │  │  METRICS │           │
│  │   BUS    │  │          │  │          │  │          │           │
│  │          │  │ initialize│  │ Postgres │  │Prometheus│           │
│  │ Publish/ │  │ validate │  │ VectorDB │  │OtelTrace│           │
│  │ Subscribe│  │ start    │  │ Redis    │  │ Logging  │           │
│  │ Async    │  │ shutdown │  │ S3       │  │ Alerts   │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
eren/
├── core/
│   ├── capabilities/                    # Capability implementations
│   │   ├── cognitive/                  # Cognitive capabilities
│   │   │   ├── perceive/
│   │   │   ├── remember/
│   │   │   ├── know/
│   │   │   ├── trust/
│   │   │   ├── assess_risk/
│   │   │   ├── reason/
│   │   │   ├── plan/
│   │   │   ├── decide/
│   │   │   ├── explain/
│   │   │   ├── learn/
│   │   │   └── reflect/
│   │   ├── security/                   # Security capabilities
│   │   │   ├── identity/
│   │   │   ├── authorization/
│   │   │   ├── audit/
│   │   │   ├── encryption/
│   │   │   ├── secrets/
│   │   │   └── policy/
│   │   ├── clinical/                   # Clinical capabilities
│   │   │   ├── clinical_context/
│   │   │   ├── decision_support/
│   │   │   ├── drug_interaction/
│   │   │   └── evidence_retrieval/
│   │   ├── biomedical/                 # Biomedical capabilities
│   │   │   ├── device_registry/
│   │   │   ├── alarm_management/
│   │   │   └── calibration_tracking/
│   │   ├── hospital/                  # Hospital capabilities
│   │   │   ├── hospital_twin/
│   │   │   ├── capacity_management/
│   │   │   └── scheduling/
│   │   └── integration/               # Integration capabilities
│   │       ├── fhir/
│   │       ├── hl7/
│   │       ├── dicom/
│   │       └── mqtt/
│   │
│   ├── contracts/                      # Capability contracts
│   │   ├── cognitive/
│   │   ├── security/
│   │   ├── clinical/
│   │   ├── biomedical/
│   │   ├── hospital/
│   │   └── integration/
│   │
│   ├── runtime/                        # Cognitive Runtime
│   │   ├── engine.py
│   │   ├── session.py
│   │   ├── lifecycle.py
│   │   └── orchestration.py
│   │
│   ├── events/                         # Event Bus
│   │   ├── bus.py
│   │   ├── publisher.py
│   │   └── subscriber.py
│   │
│   ├── storage/                        # Storage abstractions
│   │   ├── relational/
│   │   ├── vector/
│   │   ├── graph/
│   │   └── cache/
│   │
│   └── infrastructure/                 # Cross-cutting concerns
│       ├── metrics/
│       ├── tracing/
│       ├── logging/
│       └── health/
│
├── integrations/                        # External integrations
│   ├── supabase/
│   ├── prometheus/
│   ├── kubernetes/
│   └── external_apis/
│
├── deployments/                        # Deployment configurations
│   ├── docker/
│   ├── kubernetes/
│   └── helm/
│
├── tests/                              # Test suites
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── chaos/
│   └── performance/
│
└── docs/                               # Documentation
    ├── epic0/
    ├── adr/
    ├── rfc/
    └── api/
```

---

## Capability Structure

Each capability follows a consistent structure:

```
capability/
├── contracts/                    # Public interfaces
│   ├── __init__.py
│   ├── provider.py             # Main capability contract
│   └── types.py                # Data types
│
├── models/                      # Domain models
│   ├── __init__.py
│   ├── entities.py             # Core entities
│   ├── events.py               # Domain events
│   └── exceptions.py           # Specific exceptions
│
├── implementation/              # Concrete implementations
│   ├── default/                # Default implementation
│   ├── provider_a/            # Provider-specific
│   └── provider_b/
│
├── tests/                      # Capability tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── __init__.py
└── README.md                   # Capability documentation
```

---

## Contract Pattern

### Example: Trust Capability

```python
# core/contracts/security/trust/provider.py
"""Trust capability contract."""

from typing import Protocol
from dataclasses import dataclass
from enum import Enum

class TrustLevel(Enum):
    """Trust level scale."""
    HIGH = "high"      # 80-100%
    MODERATE = "moderate"  # 50-79%
    LOW = "low"        # 20-49%
    UNCERTAIN = "uncertain"  # <20%

@dataclass(frozen=True)
class TrustScore:
    """Trust evaluation result."""
    level: TrustLevel
    confidence: float  # 0.0 to 1.0
    factors: tuple[str, ...]
    evidence: tuple[str, ...]
    assessed_at: str
    expires_at: str | None

@dataclass(frozen=True)
class TrustContext:
    """Context for trust evaluation."""
    source_id: str
    source_type: str
    temporal_relevance: str
    validation_level: str

class TrustProvider(Protocol):
    """Trust evaluation capability contract.
    
    Philosophy: EREN expresses trust in sources.
    Every recommendation must include trust assessment.
    """
    
    async def evaluate_source_trust(
        self,
        source_id: str,
        context: TrustContext
    ) -> TrustScore:
        """Evaluate trust in a source."""
        ...
    
    async def evaluate_evidence_trust(
        self,
        evidence_id: str,
        context: TrustContext
    ) -> TrustScore:
        """Evaluate trust in evidence."""
        ...
    
    async def get_trust_context(
        self,
        entity_id: str
    ) -> TrustContext:
        """Get trust context for an entity."""
        ...
```

---

## Event Architecture

### Event Bus Pattern

```python
# Events flow through the system
# Every event is typed and versioned

class DomainEvent:
    """Base for all domain events."""
    event_id: str
    event_type: str
    version: str
    timestamp: datetime
    correlation_id: str
    causation_id: str | None

# Example: Trust Evaluation Event
@dataclass
class TrustEvaluated(DomainEvent):
    """Fired when trust is evaluated."""
    source_id: str
    trust_level: TrustLevel
    confidence: float
    factors: list[str]
```

### Event Categories

```
Cognitive Events
├── PerceptionReceived
├── MemoryEncoded
├── MemoryRetrieved
├── KnowledgeQueried
├── TrustEvaluated
├── RiskAssessed
├── ReasoningCompleted
├── DecisionMade
├── ExplanationGenerated
└── LearningOccurred

Security Events
├── IdentityAuthenticated
├── AuthorizationGranted
├── AuthorizationDenied
├── AuditLogged
└── PolicyViolated

Clinical Events
├── PatientContextUpdated
├── ClinicalDecisionRecommended
├── DrugInteractionDetected
├── EvidenceRetrieved
└── AlertTriggered

Biomedical Events
├── DeviceRegistered
├── DeviceStatusChanged
├── AlarmReceived
├── CalibrationDue
└── MaintenanceScheduled

Hospital Events
├── BedStatusChanged
├── PatientAdmitted
├── PatientDischarged
└── CapacityAlert
```

---

## Data Architecture

### Primary Data Stores

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA STORES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  POSTGRES   │    │  VECTOR DB  │    │   GRAPH DB  │         │
│  │             │    │             │    │             │         │
│  │ Clinical    │    │ Knowledge   │    │ Knowledge   │         │
│  │ Context     │    │ Embeddings  │    │ Relationships│        │
│  │ Device      │    │ Evidence   │    │ Entity Graph │        │
│  │ Registry    │    │ Semantic    │    │ Dependency   │        │
│  │ Audit Logs  │    │ Search     │    │ Graph        │        │
│  │ Policies    │    │            │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         ↑                  ↑                  ↑                  │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                     ┌──────▼──────┐                            │
│                     │    REDIS     │                            │
│                     │             │                            │
│                     │ Session      │                            │
│                     │ Cache        │                            │
│                     │ Rate Limits  │                            │
│                     │ Trust Cache  │                            │
│                     └─────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Models by Domain

#### Clinical Domain
```python
@dataclass
class Patient:
    patient_id: str
    demographics: Demographics
    medical_history: list[Diagnosis]
    medications: list[Medication]
    allergies: list[Allergy]
    consent_status: ConsentStatus

@dataclass
class ClinicalEncounter:
    encounter_id: str
    patient_id: str
    encounter_type: EncounterType
    chief_complaint: str
    assessments: list[Assessment]
    plan: CarePlan
    vitals: list[Vital]
    devices: list[DeviceReading]
```

#### Biomedical Domain
```python
@dataclass
class MedicalDevice:
    device_id: str
    classification: DeviceClass  # I, II, III
    manufacturer: str
    model: str
    serial_number: str
    location: Location
    status: DeviceStatus
    last_calibration: CalibrationRecord
    maintenance_schedule: MaintenanceSchedule

@dataclass
class CalibrationRecord:
    calibration_id: str
    device_id: str
    calibration_date: datetime
    next_due: datetime
    standard: str  # NIST-traceable
    result: CalibrationResult  # PASS/FAIL
    certificate_id: str
```

---

## API Architecture

### API Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYERS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    EXTERNAL API                          │   │
│  │                                                          │   │
│  │  REST API (OpenAPI 3.0)                                 │   │
│  │  GraphQL API (optional)                                  │   │
│  │  WebSocket (real-time events)                           │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   INTERNAL API                           │   │
│  │                                                          │   │
│  │  gRPC Services (internal communication)                 │   │
│  │  Event Subscriptions (internal events)                  │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 CAPABILITY GATEWAY                       │   │
│  │                                                          │   │
│  │  Auth middleware                                         │   │
│  │  Rate limiting                                          │   │
│  │  Request validation                                     │   │
│  │  Capability routing                                     │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  CAPABILITY LAYER                        │   │
│  │                                                          │   │
│  │  Each capability exposes its own interface               │   │
│  │  Capabilities talk to each other via contracts          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### API Design Principles

1. **REST for CRUD**: Standard REST patterns for resource management
2. **gRPC for internal**: High-performance internal communication
3. **Events for integration**: Async communication via event bus
4. **WebSocket for real-time**: Live updates for monitoring/alerts

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    AUTHENTICATION                         │   │
│  │                                                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │Supabase │  │Keycloak │  │ AzureAD │  │   LDAP  │   │   │
│  │  │  Auth   │  │         │  │         │  │         │   │   │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │   │
│  │       │            │            │            │           │   │
│  │       └────────────┴─────┬──────┴────────────┘           │   │
│  │                          │                                │   │
│  └──────────────────────────┼────────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    AUTHORIZATION                         │   │
│  │                                                          │   │
│  │  RBAC + ABAC + Policy Engine                            │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │ Roles: Physician, Nurse, Biomedical, Admin       │   │   │
│  │  │ Attributes: Department, Unit, Device Access       │   │   │
│  │  │ Policies: Allow/Deny based on context            │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      AUDIT                              │   │
│  │                                                          │   │
│  │  Immutable audit log of all PHI access                  │   │
│  │  Tamper-proof storage                                   │   │
│  │  Retention per HIPAA requirements                       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   ENCRYPTION                            │   │
│  │                                                          │   │
│  │  At Rest: AES-256                                      │   │
│  │  In Transit: TLS 1.3                                    │   │
│  │  Key Management: Vault / Cloud KMS                       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Development
```
┌─────────────────┐
│   Docker Compose │
│                 │
│  Postgres       │
│  Redis          │
│  Qdrant         │
│  Neo4j          │
│  EREN API       │
│  EREN Worker    │
└─────────────────┘
```

### Production (Kubernetes)
```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    NAMESPACE: eren                       │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │    API      │  │   WORKER    │  │   EVENT     │     │   │
│  │  │  (HPA)     │  │   (HPA)     │  │  PROCESSOR  │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │              SERVICE MESH (Istio)                │   │   │
│  │  │   mTLS, circuit breakers, retries, observability │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  NAMESPACE: data                        │   │
│  │                                                          │   │
│  │  Postgres (HA)  │  Redis (Cluster)  │  VectorDB       │   │
│  │  GraphDB        │  S3-compatible   │  Monitoring     │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Observability Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  METRICS    │    │   TRACES    │    │   LOGS      │         │
│  │             │    │             │    │             │         │
│  │ Prometheus  │    │ Jaeger      │    │ Loki        │         │
│  │             │    │ OpenTelemetry│    │             │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘                │
│                             ▼                                    │
│                   ┌─────────────────┐                          │
│                   │    GRAFANA      │                          │
│                   │                 │                          │
│                   │  Dashboards    │                          │
│                   │  Alerts        │                          │
│                   │  Explore       │                          │
│                   └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Metrics to Collect

```yaml
# Required metrics per capability
cognitive:
  - reasoning_latency_seconds
  - decision_confidence_score
  - trust_evaluation_count
  - risk_assessment_count

security:
  - auth_attempts_total
  - auth_failures_total
  - authorization_decisions_total
  - audit_events_total

clinical:
  - decision_support_requests_total
  - drug_interaction_alerts_total
  - clinical_context_updates_total

biomedical:
  - device_status_changes_total
  - alarm_events_total
  - calibration_due_count
```

---

## Technology Stack

### Core
| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.12+ | Primary language |
| Async | asyncio, uvloop | Async I/O |
| Type System | Pyright, mypy | Type safety |

### Data
| Component | Technology | Purpose |
|-----------|------------|---------|
| Relational | PostgreSQL | Primary data |
| Vector | Qdrant/Milvus | Embeddings |
| Graph | Neo4j | Knowledge graph |
| Cache | Redis | Sessions, cache |
| Object Storage | S3 | Documents, files |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Container | Docker | Packaging |
| Orchestration | Kubernetes | Deployment |
| Service Mesh | Istio | Networking |
| Monitoring | Prometheus, Grafana | Observability |
| Tracing | Jaeger | Distributed tracing |

### Integration
| Component | Technology | Purpose |
|-----------|------------|---------|
| FHIR | HAPI FHIR Server | EHR integration |
| MQTT | EMQX | Device connectivity |
| Auth | Supabase/Keycloak | Authentication |

---

## Non-Functional Requirements

### Performance
| Metric | Target |
|--------|--------|
| API latency (p95) | < 200ms |
| Decision latency (p95) | < 2s |
| Event processing throughput | > 10,000 events/s |
| Concurrent users | > 1,000 |

### Reliability
| Metric | Target |
|--------|--------|
| Availability | 99.9% |
| MTTR | < 15 minutes |
| Backup frequency | Every 4 hours |
| RTO | < 1 hour |
| RPO | < 15 minutes |

### Security
| Requirement | Standard |
|-------------|----------|
| Encryption at rest | AES-256 |
| Encryption in transit | TLS 1.3 |
| Audit retention | 7 years (HIPAA) |
| Vulnerability scanning | Weekly |

---

## RFC Process

### RFC Lifecycle

```
DRAFT → REVIEW → APPROVED → IMPLEMENTED → DEPRECATED
  │         │          │            │
  └─────────┴──────────┴────────────┘
        (can return to draft)
```

### RFC Template

```markdown
RFC-XXXX: [Title]

## Status
- Created: [date]
- Status: [DRAFT/REVIEW/APPROVED/IMPLEMENTED]

## Summary
[Brief description]

## Motivation
[Why this is needed]

## Detailed Design
[Technical specification]

## Contracts
[Interfaces defined]

## Events
[Domain events]

## Dependencies
[What this depends on]

## Alternatives
[Other approaches considered]

## Implementation Plan
[Phases, milestones]
```

---

## Architectural Decision Records

### ADRs to Create

| ADR | Decision |
|-----|----------|
| ADR-0001 | Hexagonal architecture with contracts |
| ADR-0002 | Event-driven cognitive model |
| ADR-0003 | Three-domain bounded contexts |
| ADR-0004 | Contract-first development |
| ADR-0005 | Kubernetes-native deployment |
| ADR-0006 | OpenTelemetry for observability |
| ADR-0007 | PostgreSQL + VectorDB + GraphDB |
| ADR-0008 | Supabase for auth (pluggable) |

---

*EREN Architecture Blueprint v1.0*
*Architecture Board - 2026-07-15*
