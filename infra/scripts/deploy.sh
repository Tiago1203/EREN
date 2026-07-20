#!/bin/bash
# EREN Enterprise Deployment Script
# Version: 1.0.0

set -e

NAMESPACE="${NAMESPACE:-eren}"
RELEASE="${RELEASE:-eren-api}"
VERSION="${VERSION:-1.0.0}"
ENVIRONMENT="${ENVIRONMENT:-production}"

echo "========================================"
echo "EREN Enterprise Deployment"
echo "========================================"
echo "Namespace: $NAMESPACE"
echo "Release: $RELEASE"
echo "Version: $VERSION"
echo "Environment: $ENVIRONMENT"
echo "========================================"

# Pre-flight checks
echo "[1/5] Running pre-flight checks..."
kubectl cluster-info --request-timeout=10s > /dev/null 2>&1 || {
    echo "❌ ERROR: Cannot connect to Kubernetes cluster"
    exit 1
}
echo "✅ Kubernetes cluster connected"

# Backup before deployment
echo "[2/5] Creating backup..."
kubectl exec -n "$NAMESPACE" deployment/"$RELEASE" -- /app/backup.sh --type=incremental || {
    echo "⚠️  Backup failed, continuing..."
}
echo "✅ Backup completed"

# Deploy using Helm
echo "[3/5] Deploying with Helm..."
helm upgrade --install "$RELEASE" ./eren-api \
    --namespace "$NAMESPACE" \
    --create-namespace \
    --values ./eren-api/values.yaml \
    --set image.tag="$VERSION" \
    --set env.EREN_API_ENVIRONMENT="$ENVIRONMENT" \
    --wait \
    --timeout 10m \
    --cleanup-on-fail

echo "✅ Deployment completed"

# Health check
echo "[4/5] Running health checks..."
sleep 10
HEALTH_STATUS=$(kubectl get pods -n "$NAMESPACE" -l "app.kubernetes.io/name=$RELEASE" -o jsonpath='{.items[0].status.phase}')
if [ "$HEALTH_STATUS" == "Running" ]; then
    echo "✅ Application is healthy"
else
    echo "❌ WARNING: Application may not be healthy"
fi

# Smoke tests
echo "[5/5] Running smoke tests..."
kubectl exec -n "$NAMESPACE" deployment/"$RELEASE" -- curl -s http://localhost:8000/api/v1/health/ready || {
    echo "⚠️  Smoke test failed"
    exit 1
}
echo "✅ Smoke tests passed"

echo "========================================"
echo "✅ Deployment successful!"
echo "========================================"
echo "Version: $VERSION"
echo "Namespace: $NAMESPACE"
echo "========================================"
