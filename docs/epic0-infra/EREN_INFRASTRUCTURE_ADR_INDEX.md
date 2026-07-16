# EREN Infrastructure ADR Index
## Architecture Decision Records for Epic 0-Infra

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-16 | Infrastructure Team | Initial |

---

## Purpose

This index tracks all Architecture Decision Records (ADRs) for EREN's infrastructure layer. These ADRs complement the ADRs from Epic 0 by documenting decisions specific to the infrastructure stack.

---

## ADR Index by Status

### Accepted

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0080 | Kubernetes as Deployment Platform | ACCEPTED | 2026-07-16 | Infrastructure Team |
| ADR-0081 | Kafka as Primary Message Broker | ACCEPTED | 2026-07-16 | Infrastructure Team |
| ADR-0082 | S3/MinIO Object Storage Strategy | ACCEPTED | 2026-07-16 | Infrastructure Team |
| ADR-0083 | Outbox Pattern for Event Publishing | ACCEPTED | 2026-07-16 | Architecture Board |
| ADR-0084 | Row-Level Security in Alembic Migrations | ACCEPTED | 2026-07-16 | Architecture Board |
| ADR-0085 | Observability Stack | ACCEPTED | 2026-07-16 | Infrastructure Team |
| ADR-0086 | Backup and Disaster Recovery Strategy | ACCEPTED | 2026-07-16 | Infrastructure Team |

### Proposed

| ADR | Title | Status | Date | Owner |
|-----|-------|--------|------|-------|
| ADR-0090 | GitOps with ArgoCD | PROPOSED | 2026-07-16 | Infrastructure Team |
| ADR-0091 | Service Mesh (Istio vs Linkerd) | PROPOSED | 2026-07-16 | Infrastructure Team |

---

## ADR Index by Category

### Containerization & Orchestration

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0080 | Kubernetes as Deployment Platform | Orchestration |

### Messaging

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0081 | Kafka as Primary Message Broker | Messaging |
| ADR-0083 | Outbox Pattern for Event Publishing | Messaging |

### Storage

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0082 | S3/MinIO Object Storage Strategy | Storage |

### Database

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0084 | Row-Level Security in Alembic Migrations | Database |

### Observability

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0085 | Observability Stack | Observability |

### Operations

| ADR | Title | Category |
|-----|-------|----------|
| ADR-0086 | Backup and Disaster Recovery Strategy | Operations |
| ADR-0090 | GitOps with ArgoCD | Operations |
| ADR-0091 | Service Mesh | Operations |

---

*EREN Infrastructure ADR Index v1.0*
*Infrastructure Team - 2026-07-16*
