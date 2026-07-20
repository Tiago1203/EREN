# EREN Infrastructure Blueprint
## Technical Infrastructure Stack and Architecture

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This document defines the complete technical infrastructure stack for EREN. It is the **implementation blueprint** that translates the architectural decisions from Epic 0 into concrete technology choices and configurations.

This document complements:
- `EREN_ARCHITECTURE_BLUEPRINT.md` (Epic 0) — architectural decisions
- `EREN_CONSISTENCY_MODEL.md` (Epic 0) — data storage strategy
- `EREN_EVENT_ARCHITECTURE.md` (Epic 0) — event patterns

---

## Layer Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  Web (Next.js) │ Chat Interface │ Mobile │ Accessibility      │
├─────────────────────────────────────────────────────────────────┤
│                       API GATEWAY LAYER                        │
│  Kong/NGINX Ingress │ Rate Limiting │ Auth │ TLS Termination   │
├─────────────────────────────────────────────────────────────────┤
│                      APPLICATION LAYER                         │
│  Python/FastAPI │ Async Tasks (Celery) │ Business Logic        │
├─────────────────────────────────────────────────────────────────┤
│                        EVENT LAYER                             │
│  Kafka (Primary) │ Schema Registry │ Dead Letter Queue          │
├────────────────┬───────────────┬──────────────┬────────────────┤
│   DATA LAYER   │   CACHE      │   GRAPH      │  VECTOR STORE  │
│  PostgreSQL    │   Redis      │   Neo4j      │   Qdrant       │
├────────────────┴───────────────┴──────────────┴────────────────┤
│                    OBJECT STORAGE LAYER                        │
│  S3 (AWS/GCP) │ MinIO (On-Prem/Development)                   │
├─────────────────────────────────────────────────────────────────┤
│                       ORCHESTRATION LAYER                     │
│  Kubernetes (EKS/GKE) │ Helm │ KEDA │ ArgoCD                 │
├─────────────────────────────────────────────────────────────────┤
│                     OBSERVABILITY LAYER                       │
│  Prometheus │ Grafana │ Jaeger │ Loki │ Alertmanager          │
├─────────────────────────────────────────────────────────────────┤
│                      SECURITY LAYER                            │
│  HashiCorp Vault │ cert-manager │ OPA │ RLS (PostgreSQL)     │
├─────────────────────────────────────────────────────────────────┤
│                       DATA LAYER                               │
│  PostgreSQL (Primary SoT) │ Redis │ Neo4j │ Qdrant             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Containerization

### Docker

**Base Images:**
```
Python 3.12-slim (API services)
node:20-alpine (web frontend)
```

**Dockerfile Conventions:**
```dockerfile
# Multi-stage build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /deps /usr/local/lib/python3.12/site-packages
COPY . .
RUN useradd --create-home --shell /bin/bash eren
USER eren
CMD ["python", "-m", "eren.api"]
```

**Security:**
- No `root` user in containers
- `--no-cache-dir` on pip installs
- Distroless or slim images only
- All secrets injected at runtime (never in Dockerfile)

---

## Layer 2: Orchestration

### Kubernetes

**Cluster Architecture:**
```
┌──────────────────────────────────────────────────────────────┐
│                    EREN Kubernetes Cluster                    │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ API Pods   │  │ Worker Pods │  │ Frontend    │          │
│  │ (FastAPI)  │  │ (Celery)    │  │ (Next.js)   │          │
│  │ 3 replicas  │  │ 2 replicas   │  │ 2 replicas   │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                 │                 │                   │
│  ┌──────┴────────────────┴─────────────────┴──────┐          │
│  │              Kubernetes Services                  │          │
│  │  LoadBalancer │ ClusterIP │ Headless             │          │
│  └──────────────────────────┬──────────────────────┘          │
│                             │                                   │
│  ┌──────────────────────────┴──────────────────────┐          │
│  │              Ingress Controller                  │          │
│  │  (NGINX/Kong) │ TLS │ Rate Limiting            │          │
│  └──────────────────────────┬──────────────────────┘          │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│  ┌───────────────────────────┴──────────────────────┐        │
│  │              Data Layer                            │        │
│  │  PostgreSQL (RDS) │ Redis (ElastiCache) │ Neo4j   │        │
│  └───────────────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

**Namespaces:**
```
eren-production     # Production workloads
eren-staging       # Staging workloads
eren-monitoring    # Prometheus, Grafana, etc.
eren-infra         # Vault, cert-manager, ingress
```

**Helm Charts:**
```
apps/eren-api/          # FastAPI application
apps/eren-worker/        # Celery workers
apps/eren-frontend/     # Next.js web app
apps/eren-cron/         # Scheduled tasks
infra/prometheus/        # Monitoring
infra/grafana/           # Dashboards
infra/jaeger/            # Distributed tracing
infra/vault/             # Secrets management
infra/ingress-nginx/     # Ingress controller
infra/cert-manager/      # TLS certificates
infra/argocd/            # GitOps deployment
```

**Autoscaling:**
- KEDA for event-driven scaling of Celery workers
- HPA for API pods based on CPU/memory/request latency
- VPA for memory recommendations

---

## Layer 3: Data Layer

### PostgreSQL (Primary Data Store)

**Version:** PostgreSQL 16

**Deployment:**
- AWS RDS / Google Cloud SQL (production)
- Self-managed on Kubernetes (staging/development)

**Extensions:**
```sql
-- Required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- fuzzy search
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- query performance
CREATE EXTENSION IF NOT EXISTS "hstore";  -- key-value storage
```

**Schema Conventions:**
- All tables: `tenant_id UUID NOT NULL`
- All tables: `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- All tables: `updated_at TIMESTAMPTZ`
- All tables: `id UUID PRIMARY KEY DEFAULT uuid_generate_v4()`
- Soft deletes: `deleted_at TIMESTAMPTZ` (nullable)
- No hard foreign keys across bounded contexts
- UUID primary keys only

**Indexes:**
```sql
-- Always include tenant_id in indexes
CREATE INDEX idx_patients_tenant ON patients(tenant_id);
CREATE INDEX idx_patients_tenant_id ON patients(tenant_id, id);
-- Composite indexes for common queries
CREATE INDEX idx_incidents_tenant_status ON incidents(tenant_id, status);
CREATE INDEX idx_devices_tenant_type ON devices(tenant_id, device_type);
```

**Row-Level Security (RLS):**
- RLS enabled on ALL tables
- Policy: `tenant_id = current_setting('app.tenant_id')::UUID`
- Application enforces at connection level (not relying solely on RLS)
- See `ADR-0084_RLS_ALEMBIC.md`

---

### Redis (Cache + Session + Queue Backend)

**Version:** Redis 7

**Deployment:**
- AWS ElastiCache (production)
- Redis on Kubernetes (staging/development)

**Use Cases:**

| Use Case | Key Pattern | TTL | Notes |
|----------|-------------|-----|-------|
| Session | `session:{user_id}` | 24h | JWT refresh tokens |
| Rate limiting | `ratelimit:{tenant}:{endpoint}` | 60s | Sliding window |
| Cache | `cache:{context}:{id}` | 5min | Application cache |
| Lock | `lock:{resource}:{id}` | 30s | Distributed locks |
| Celery broker | — | — | See Layer 4 |
| Pub/Sub | `pubsub:{event}` | — | Real-time events |

**Configuration:**
```python
REDIS_URL = "redis://redis:6379/0"
REDIS_CACHE_URL = "redis://redis:6379/1"
REDIS_SESSION_URL = "redis://redis:6379/2"
REDIS_QUEUE_URL = "redis://redis:6379/3"
```

---

### Neo4j (Graph for Relationships)

**Version:** Neo4j 5

**Use Cases:**
- Device-to-device relationships
- Patient-device associations
- Alarm propagation graphs
- Root cause analysis causal chains

**Connection:**
```python
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]  # From Vault
```

---

### Qdrant (Vector Store)

**Version:** Qdrant 1.7

**Use Cases:**
- Semantic search for knowledge base
- Evidence retrieval for CDS
- Device documentation search

**Collections:**
```
knowledge_base_evidence     # Medical evidence embeddings
device_documentation        # Device manuals, specifications
clinical_guidelines        # Treatment guidelines
alarm_history              # Alarm patterns for similarity
```

---

## Layer 4: Messaging

### Kafka (Primary Event Bus)

**Version:** Apache Kafka 3.6 (KRaft mode)

**Deployment:**
- Confluent Cloud (production, managed)
- Apache Kafka on Kubernetes (staging/development)

**Why Kafka (not RabbitMQ):**
- See `ADR-0081_MESSAGE_QUEUE.md`

**Topics:**
```
eren-clinical.patients.events
eren-clinical.diagnosis.events
eren-clinical.treatment.events
eren-clinical.cds.recommendations

eren-biomedical.device.events
eren-biomedical.alarm.events
eren-biomedical.maintenance.events

eren-hospital.capacity.events
eren-hospital.staffing.events
eren-hospital.inventory.events

eren-system.audit.events
eren-system.notification.events
eren-system.alert.events

# Dead Letter Topics
eren-dlq.clinical.events
eren-dlq.biomedical.events
eren-dlq.hospital.events
eren-dlq.system.events
```

**Configuration:**
```yaml
# Consumer groups per service
eren-api-clinical: 3 partitions
eren-worker-clinical: 3 partitions
eren-api-biomedical: 3 partitions
eren-worker-biomedical: 3 partitions

# Retention
clinical events: 30 days
biomedical events: 90 days (compliance)
hospital events: 30 days
audit events: 7 years (HIPAA)
```

**Schema Registry:**
- Apache Avro for schema definition
- Schema evolution with backward compatibility
- JSON Schema alternative for HTTP-based services

---

### Celery (Async Task Queue)

**Why Celery:**
- Python-native async task execution
- Native Kafka support via celery-kafka
- Periodic task scheduling (celery beat)
- Distributed task queue for long-running operations

**Brokers:**
- Redis (development/staging)
- Kafka (production) via `celery-kafka`

**Queues:**
```
celery.high_priority    # CDS recommendations, critical alerts
celery.default         # Standard operations
celery.low_priority    # Analytics, batch jobs
celery.maintenance     # Scheduled maintenance tasks
```

---

## Layer 5: Object Storage

### S3 / MinIO

**Deployment:**
- AWS S3 / Google Cloud Storage (production)
- MinIO (on-premises, development)

**Why not local filesystem:**
- See `ADR-0082_OBJECT_STORAGE.md`

**Buckets:**
```
eren-{env}-exports           # Data exports (CSV, JSON)
eren-{env}-imports           # Data imports
eren-{env}-dicom             # DICOM files (encrypted)
eren-{env}-backups           # Database backups
eren-{env}-logs              # Application logs archive
eren-{env}-attachments       # File attachments
```

**Lifecycle Policies:**
```
exports: delete after 90 days
imports: delete after 30 days (after processing)
dicom: move to Glacier after 1 year
backups: move to Glacier after 7 days
logs: move to Glacier after 30 days
```

---

## Layer 6: Secrets Management

### HashiCorp Vault

**Deployment:**
- Vault (self-managed on Kubernetes) for development/staging
- AWS Secrets Manager / GCP Secret Manager for production (as Vault alternative)

**Secret Engine:**
```
pki/                  # TLS certificates
kv-v2/eren/{env}/    # Application secrets per environment
aws/                 # AWS IAM role generation
database/            # Dynamic PostgreSQL credentials
```

**Secret Categories:**
```python
# Database
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]  # From Vault

# External Services
FHIR_PASSWORD = os.environ["FHIR_PASSWORD"]  # From Vault
MQTT_API_KEY = os.environ["MQTT_API_KEY"]    # From Vault

# LLM
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # From Vault

# Multi-tenant secrets (per tenant)
TENANT_SECRET = os.environ["TENANT_SECRET"]  # Tenant-scoped
```

**Dynamic Credentials:**
- PostgreSQL credentials rotated every 24h via Vault database engine
- No long-lived database passwords stored in environment variables

**Tenant Scoping:**
```python
# Each tenant gets scoped secrets
tenant_secrets = vault.kv.v2.read_secret(
    path=f"eren/production/tenant/{tenant_id}"
)
```

---

## Layer 7: Observability

### Prometheus

**What it collects:**
- Application metrics (via OpenTelemetry)
- Kubernetes resource metrics
- PostgreSQL slow queries
- Kafka consumer lag
- Celery task metrics

**Metrics Examples:**
```python
# Application metrics (OpenTelemetry)
eren_http_requests_total{method, endpoint, status_code}
eren_http_request_duration_seconds{method, endpoint}
eren_cds_recommendations_total{decision_type, confidence_band}
eren_device_events_total{device_type, event_type}
eren_alarm_escalation_total{alarm_type, escalation_level}

# Business metrics
eren_active_patients_gauge{tenant_id}
eren_active_devices_gauge{tenant_id}
eren_open_incidents_gauge{tenant_id, priority}
```

### Grafana

**Dashboards:**
```
EREN Overview (executive)
API Performance
Celery Workers
PostgreSQL Performance
Kafka Consumer Lag
Alarm Volume and Resolution Time
CDS Recommendation Quality
Multi-Tenant Isolation Health
```

### Jaeger (Distributed Tracing)

**Traces collected:**
- All HTTP requests (API → downstream services)
- Kafka message production/consumption
- Celery task execution
- Database queries (via OpenTelemetry)

**Sampling:**
- 100% for errors
- 5% for successful requests (production)
- 100% for staging

### Loki (Log Aggregation)

**Log Format:**
```json
{
  "timestamp": "2026-07-16T10:30:00.000Z",
  "level": "INFO",
  "service": "eren-api",
  "tenant_id": "uuid",
  "trace_id": "abc123",
  "message": "CDS recommendation generated",
  "context": {
    "patient_id": "uuid",
    "device_id": "uuid",
    "confidence": 0.87
  }
}
```

**Alert Rules:**
```yaml
# Example: High error rate
- alert: HighErrorRate
  expr: rate(eren_http_requests_total{status_code=~"5.."}[5m]) > 0.01
  for: 5m
  labels:
    severity: critical
```

**See also:** `EREN_OBSERVABILITY_SETUP.md` for detailed setup

---

## Layer 8: CI/CD

### GitHub Actions (Primary CI/CD)

**Workflows:**
```
.github/workflows/
├── ci.yml              # Lint, test, type-check (every PR)
├── build.yml           # Docker build + push (on merge to main)
├── deploy-staging.yml  # Deploy to staging (on merge to main)
├── deploy-prod.yml     # Deploy to production (manual approval)
├── security-scan.yml    # SAST, dependency scan
└── infrastructure.yml   # Terraform/Helm changes
```

**Environment Promotion:**
```
PR → CI → Build → Staging (auto-deploy)
Main → Build → Staging → Manual Approval → Production
```

**Secrets in CI/CD:**
- GitHub Actions secrets for non-sensitive values
- Vault agent for runtime secrets injection
- No secrets in Git history

---

## Layer 9: Settings Model

### Environment-Based Configuration

```
EREN_ENV = "development" | "staging" | "production"
EREN_TENANT_ID = "uuid"  # Set per-request, not per-service
```

### Configuration Hierarchy

```python
# Priority (highest to lowest):
# 1. Environment variables (OS-level)
# 2. Vault secrets (dynamic credentials)
# 3. Settings files (config.yaml per environment)
# 4. Default values (settings.py)

Settings:
  database_url          # From Vault
  redis_url             # From Vault
  kafka_brokers         # From Vault
  llm_api_key           # From Vault
  secret_key            # From Vault
  allowed_hosts         # From config.yaml
  cors_origins          # From config.yaml
  log_level             # From config.yaml / env
  debug                 # From config.yaml / env (never in production)
```

**See also:** `EREN_SETTINGS_MODEL.md`

---

## Layer 10: Multi-Tenancy Enforcement

### Connection-Level Tenant Isolation

```python
# Every database connection sets tenant context
async def set_tenant_context(connection: asyncpg.Connection, tenant_id: UUID):
    await connection.execute(
        f"SET app.tenant_id = '{tenant_id}'"
    )

# Unit of Work sets tenant context on every transaction
class UnitOfWork:
    async def __aenter__(self):
        conn = await get_connection()
        await set_tenant_context(conn, self.tenant_id)
        self._conn = conn
        return self
```

### Alembic Migrations

- Every migration auto-includes `tenant_id` column
- RLS policies created by migrations
- No cross-tenant data access possible at DB level
- See `ADR-0084_RLS_ALEMBIC.md`

---

## Network Architecture

```
Internet
   │
   ▼
CloudFlare (CDN + WAF)
   │
   ▼
ALB (AWS) / Cloud Load Balancer
   │
   ▼
Kong/NGINX Ingress Controller
   │   - TLS Termination
   │   - Rate Limiting
   │   - Auth Verification
   │
   ├──► EREN API (FastAPI) ──► PostgreSQL
   │                            ├──► Redis
   │                            ├──► Neo4j
   │                            ├──► Qdrant
   │                            └──► S3/MinIO
   │
   ├──► EREN Worker (Celery) ──► Kafka
   │
   └──► EREN Frontend (Next.js) ──► API Gateway
```

---

## Directory Structure

```
eren/
├── apps/
│   ├── eren-api/              # FastAPI application
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   │   ├── env.py         # Tenant context in migrations
│   │   │   └── versions/
│   │   └── src/
│   │       ├── api/           # Routes
│   │       ├── application/   # Use cases
│   │       ├── domain/        # Entities, value objects
│   │       ├── infrastructure/# Repositories, external clients
│   │       └── main.py
│   │
│   ├── eren-worker/           # Celery workers
│   │   ├── Dockerfile
│   │   └── src/
│   │       └── tasks/
│   │
│   ├── eren-cron/             # Scheduled tasks
│   │
│   └── eren-frontend/          # Next.js web app
│       ├── Dockerfile
│       └── src/
│
├── infra/
│   ├── kubernetes/            # K8s manifests
│   │   ├── apps/
│   │   └── infra/
│   ├── helm/                  # Helm charts
│   │   ├── eren-api/
│   │   ├── eren-worker/
│   │   └── eren-frontend/
│   ├── terraform/             # Infrastructure as code
│   │   ├── modules/
│   │   └── environments/
│   └── argocd/                # ArgoCD applications
│
├── docker-compose.yml         # Local development
├── docker-compose.ci.yml      # CI environment
└── Makefile                   # Developer commands
```

---

*EREN Infrastructure Blueprint v1.0*
*Infrastructure Team - 2026-07-16*
