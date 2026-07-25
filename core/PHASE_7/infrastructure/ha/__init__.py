"""EPIC 3: High Availability & Scalability — HA Module."""
from core.PHASE_7.infrastructure.ha.load_balancer import (
    LoadBalancer, LoadBalancerConfig, Backend, Algorithm,
)
from core.PHASE_7.infrastructure.ha.health_checker import (
    HealthChecker, HealthCheck, HealthCheckResult, HealthStatus,
    CheckType, ServiceHealth,
)
from core.PHASE_7.infrastructure.ha.failover_manager import (
    FailoverManager, Node, NodeState, FailoverEvent, FailoverTrigger,
)
from core.PHASE_7.infrastructure.ha.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerStats,
    CircuitBreakerOpenError, CircuitState, CircuitBreakerRegistry,
)
