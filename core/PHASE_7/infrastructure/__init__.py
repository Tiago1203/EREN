"""EPIC 3: High Availability & Scalability.
Provides HA, scaling, disaster recovery, and deployment infrastructure.
"""
from core.PHASE_7.infrastructure.ha import (
    LoadBalancer, Backend, Algorithm,
    HealthChecker, HealthCheck, HealthStatus, CheckType,
    FailoverManager, Node, NodeState, FailoverEvent,
    CircuitBreaker, CircuitBreakerOpenError, CircuitBreakerRegistry,
)
from core.PHASE_7.infrastructure.scaling import (
    AutoScaler, ScalingPolicies, ScalingPolicyConfig,
    ScalingDecision, ScalingAction,
)
from core.PHASE_7.infrastructure.recovery import (
    BackupManager, BackupType, BackupStatus, BackupRetention,
    DisasterRecoveryManager, DRRunbook, DRObjectives, DRLevel, DRScenario,
    RestoreService, RestoreType, RestoreStatus,
    FailoverReplicaManager, ReadReplica, ReplicaStatus,
)
