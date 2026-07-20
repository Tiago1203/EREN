# ADR-0080: Kubernetes as Deployment Platform

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Infrastructure Team

---

## Context

EREN needs a platform to deploy, scale, and manage containerized services across multiple environments (development, staging, production). The system must support:
- Horizontal autoscaling based on demand
- Rolling deployments with zero downtime
- Multi-environment configuration
- Secrets management
- Service discovery
- Health monitoring

We evaluated two options: **Kubernetes** and **Docker Compose + Ansible**.

---

## Decision

**We will use Kubernetes as the deployment platform.**

Deployment targets:
- **Production:** Amazon EKS or Google GKE (managed Kubernetes)
- **Staging:** Self-managed Kubernetes on VMs or managed K8s
- **Development:** Docker Compose (for local) + Kubernetes manifests validated via k3s or kind

---

## Reasons

### Kubernetes (Chosen)

1. **Horizontal Pod Autoscaling (HPA):** Built-in autoscaling for API pods and Celery workers based on CPU, memory, and custom metrics via KEDA
2. **Rolling Deployments:** Zero-downtime deployments with automatic rollback
3. **Multi-tenancy:** Namespace isolation per tenant with resource quotas
4. **Service Mesh readiness:** Can add Istio/Linkerd later for mTLS between services
5. **GitOps:** ArgoCD for declarative deployments from Git
6. **Ecosystem:** Helm charts, KEDA, cert-manager, ArgoCD — rich ecosystem for production workloads
7. **Industry Standard:** Most cloud providers offer managed K8s (EKS, GKE, AKS), reducing operational burden
8. **Observability:** Prometheus operator, Jaeger operator natively supported

### Docker Compose + Ansible (Rejected)

1. **No native autoscaling:** Requires custom scripting
2. **Limited orchestration:** No built-in service discovery or load balancing
3. **Not production-grade:** Appropriate for development only
4. **Manual operations:** No declarative infrastructure
5. **No rolling deployments:** Manual process with downtime risk

---

## Consequences

### Positive

- Production-grade orchestration with enterprise support
- Declarative, version-controlled infrastructure (GitOps)
- Horizontal scaling for CDS recommendations under load
- Namespace isolation supports multi-tenancy strategy
- Rich ecosystem: Helm, KEDA, cert-manager, ArgoCD

### Negative

- **Learning curve:** Team must learn Kubernetes concepts and tooling
- **Operational complexity:** Cluster management, upgrades, networking configuration
- **Cost:** Managed K8s costs (~$70/month per cluster on EKS/GKE) plus node costs
- **Overhead for development:** Local Kubernetes is heavier than Docker Compose

### Mitigations

- Use managed Kubernetes (EKS/GKE) to reduce operational burden
- Docker Compose for local development (synced manifests)
- ArgoCD for GitOps — infrastructure as code, no manual kubectl
- Invest in team Kubernetes training

---

## Implementation

### Cluster Architecture

```
Production: 1 cluster per region, multi-AZ
Staging: 1 cluster, single-AZ (lower cost)
Development: Docker Compose local
```

### Helm Charts

All services packaged as Helm charts for declarative deployment:
```
infra/helm/
├── eren-api/         # FastAPI service
├── eren-worker/       # Celery workers
├── eren-frontend/     # Next.js
├── eren-cron/         # Celery beat
└── eren-nginx/       # Ingress controller
```

### Kubernetes Manifests

For components that don't need Helm:
```
infra/kubernetes/
├── namespace.yaml
├── rbac.yaml          # Service accounts, roles
├── network-policies.yaml
└── resource-quotas.yaml
```

### Autoscaling

- **HPA** for API pods: scale on CPU > 70%, memory > 80%, request latency
- **KEDA** for Celery workers: scale on Kafka consumer lag, queue depth

---

## Related ADRs

- ADR-0030: Kubernetes Deployment (Epic 0 — referenced)
- ADR-0085: Observability Stack
- ADR-0090: GitOps with ArgoCD (Proposed)

---

*Infrastructure Team - 2026-07-16*
