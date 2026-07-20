# EREN Deployment Guide
## Docker, Kubernetes, and GitOps

---

## Deployment Environments

| Environment | Purpose | Deployment Method |
|------------|---------|-----------------|
| Development | Local dev | `docker compose` |
| Staging | Pre-production testing | Kubernetes |
| Production | Live system | Kubernetes + GitOps |

---

## Docker Compose (Development)

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d postgres redis

# View logs
docker compose logs -f api

# Stop all
docker compose down

# Stop and remove volumes (CLEAN)
docker compose down -v
```

### Build the API image

```bash
docker build -f apps/api/Dockerfile -t eren-api:latest .
docker run -p 8000:8000 eren-api:latest
```

---

## Kubernetes (Staging / Production)

### Prerequisites

```bash
kubectl cluster-info
helm version
```

### Deploy with Helm

```bash
# Add repo (if using upstream chart)
helm repo add eren https://charts.eren.dev

# Install
helm install eren-api eren/eren-api \
  --namespace eren \
  --create-namespace \
  --values infra/helm/values.yaml

# Upgrade
helm upgrade eren-api eren/eren-api \
  --namespace eren \
  --values infra/helm/values.prod.yaml

# Uninstall
helm uninstall eren-api --namespace eren
```

### Manual kubectl deployment

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/ingress.yaml
```

### Verify deployment

```bash
kubectl get pods -n eren
kubectl get services -n eren
kubectl get ingress -n eren

# Check pod logs
kubectl logs -n eren -l app=eren-api -f

# Check health
curl http://localhost:8000/api/v1/health/ready
```

---

## Kubernetes Resources

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: eren
  labels:
    name: eren
    environment: production
```

### Deployment

Key configuration:

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
        - name: api
          image: eren-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: EREN_API_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: eren-secrets
                  key: database-url
            - name: EREN_API_RABBITMQ_URL
              valueFrom:
                secretKeyRef:
                  name: eren-secrets
                  key: rabbitmq-url
          resources:
            requests:
              cpu: 250m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          livenessProbe:
            httpGet:
              path: /api/v1/health/live
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /api/v1/health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: eren-api
  namespace: eren
spec:
  type: ClusterIP
  selector:
    app: eren-api
  ports:
    - port: 80
      targetPort: 8000
```

### Ingress (NGINX)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: eren-api
  namespace: eren
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  rules:
    - host: api.eren.dev
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: eren-api
                port:
                  number: 80
```

---

## GitOps with ArgoCD

See [ADR-0090: GitOps with ArgoCD](../adr/epic0-infra/ADR-0090.md).

### Application manifest

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: eren-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/EREN.git
    targetRevision: main
    path: infra/helm
    helm:
      valueFiles:
        - values.prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: eren
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## Environment-Specific Configuration

### Development

```yaml
# infra/helm/values.dev.yaml
replicaCount: 1
image:
  repository: eren-api
  tag: dev

env:
  EREN_API_ENVIRONMENT: development
  EREN_API_DEBUG: "true"
  EREN_API_DATABASE_URL: postgresql+asyncpg://eren:eren@postgres:5432/eren
```

### Production

```yaml
# infra/helm/values.prod.yaml
replicaCount: 3
image:
  repository: eren-api
  tag: latest
  pullPolicy: Always

env:
  EREN_API_ENVIRONMENT: production
  EREN_API_DEBUG: "false"
  EREN_API_DATABASE_URL: postgresql+asyncpg://eren:eren@postgres.prod:5432/eren
  EREN_API_OTEL_ENDPOINT: http://jaeger-collector.observability:4317

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
```

---

## Secrets Management

Use Kubernetes Secrets or HashiCorp Vault:

```bash
# Create secret from env file
kubectl create secret generic eren-secrets \
  --from-literal=database-url="postgresql+asyncpg://..." \
  --from-literal=rabbitmq-url="amqp://..." \
  --namespace eren

# Or with Vault
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: eren-secrets
  namespace: eren
type: Opaque
stringData:
  vault-token: "${VAULT_TOKEN}"
EOF
```

---

## CI/CD Pipeline

See `.github/workflows/ci.yml` for the full pipeline.

### Pipeline stages

```
push/PR
  ├── lint          ruff + black
  ├── typecheck     mypy
  ├── test          pytest (unit + integration)
  ├── build         docker build
  └── architecture  verify imports
```

### Deployment trigger

```yaml
on:
  push:
    branches: [main]
```

Production deployment is triggered automatically on merge to `main` via ArgoCD sync.

---

*EREN Deployment Guide v1.0*
*Infrastructure Team - 2026-07-16*
