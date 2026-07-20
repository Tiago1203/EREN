#!/bin/bash
# EREN Rollback Script
# Version: 1.0.0

set -e

NAMESPACE="${NAMESPACE:-eren}"
RELEASE="${RELEASE:-eren-api}"

echo "========================================"
echo "EREN Rollback"
echo "========================================"
echo "Namespace: $NAMESPACE"
echo "Release: $RELEASE"
echo "========================================"

# Get revision to rollback to
REVISION="${1:-}"
if [ -z "$REVISION" ]; then
    echo "Fetching deployment history..."
    helm history "$RELEASE" -n "$NAMESPACE"
    echo ""
    echo "Usage: ./rollback.sh <revision_number>"
    exit 1
fi

echo "Rolling back to revision $REVISION..."

# Rollback
helm rollback "$RELEASE" "$REVISION" \
    --namespace "$NAMESPACE" \
    --wait \
    --timeout 5m

echo "✅ Rollback completed"

# Verify
echo "Verifying rollback..."
kubectl rollout status deployment/"$RELEASE" -n "$NAMESPACE" --timeout=5m

echo "========================================"
echo "✅ Rollback successful!"
echo "========================================"
