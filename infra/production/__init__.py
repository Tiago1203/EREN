"""
EREN Production Infrastructure Module

Production readiness components:
- Performance (Caching, Load Testing)
- Security (RBAC, HIPAA, GDPR, ISO 27001)
- Monitoring (Prometheus, Grafana, Alerting)
- Disaster Recovery (Backup, Multi-Region, HA)
"""
from .cache import CacheManager, CACHE_STRATEGIES
from .monitoring import (
    MonitoringMiddleware,
    setup_monitoring,
    REQUEST_COUNT,
    REQUEST_LATENCY,
    update_device_metrics,
    update_incident_metrics,
)
from .security import (
    RBACService,
    HIPAACompliance,
    GDPRCompliance,
    Role,
    verify_token,
    require_roles,
)
from .alerting import (
    AlertManager,
    Alert,
    AlertSeverity,
    AlertRule,
    get_current_on_call,
)
from .backup import (
    BackupManager,
    BackupJob,
    BackupType,
    DisasterRecoveryManager,
    REGIONS,
)

__all__ = [
    # Cache
    "CacheManager",
    "CACHE_STRATEGIES",
    # Monitoring
    "MonitoringMiddleware",
    "setup_monitoring",
    "REQUEST_COUNT",
    "REQUEST_LATENCY",
    "update_device_metrics",
    "update_incident_metrics",
    # Security
    "RBACService",
    "HIPAACompliance",
    "GDPRCompliance",
    "Role",
    "verify_token",
    "require_roles",
    # Alerting
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertRule",
    "get_current_on_call",
    # Backup
    "BackupManager",
    "BackupJob",
    "BackupType",
    "DisasterRecoveryManager",
    "REGIONS",
]

__version__ = "1.0.0"
