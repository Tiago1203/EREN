# ADR-7004: High Availability & Scalability Strategy

## Status
**Implemented** ✅ (Julio 2025)

## Context
EREN needs production-grade high availability for hospital deployments requiring 99.9% uptime. Critical for clinical operations where system unavailability can impact patient care.

## Decision
We implement a multi-layered HA strategy:

### 1. Load Balancing
- **Algorithm**: Round-robin (default), with least-connections for high-traffic
- **Health-aware routing**: Only route to healthy backends
- **Connection management**: Pool limits per backend

### 2. Health Monitoring
- **Check types**: HTTP, TCP, database, Redis, custom
- **States**: HEALTHY → DEGRADED → UNHEALTHY
- **Failure thresholds**: 3 consecutive failures = unhealthy
- **Recovery thresholds**: 2 consecutive successes = healthy

### 3. Failover
- **Primary/Standby**: Automatic election based on priority
- **State transfer**: Event-driven with listeners
- **Manual override**: Admin can trigger failover

### 4. Circuit Breaker
- **States**: CLOSED → OPEN → HALF_OPEN → CLOSED
- **Configurable**: failure_threshold, timeout, success_threshold
- **Per-service**: CircuitBreakerRegistry for multiple services

### 5. Auto-Scaling
- **Metrics**: CPU (70%), Memory (80%), RPS
- **Policies**: Conservative (critical), Balanced (default), Aggressive (AI), Cost-optimized (batch)
- **Cooldown**: 5 min up, 5 min down
- **HPA**: Kubernetes HPA with 2-20 replicas

### 6. Disaster Recovery
- **Backup**: Daily full + hourly incremental
- **Retention**: HIPAA 7 years
- **DR Tiers**: TIER_1 (active-active <1min) to TIER_4 (archive >24hr)
- **Runbooks**: 6 scenarios automated

## Consequences
### Positive
- 99.9% uptime target achievable
- Graceful degradation under load
- No single point of failure
- HIPAA-compliant backup retention
### Negative
- Increased infrastructure complexity
- Cost of running multiple replicas
- Monitoring overhead
- DR testing required quarterly
