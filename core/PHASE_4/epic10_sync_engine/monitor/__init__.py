"""
PHASE 4 - EPIC 10: Monitor Module

Monitoreo de fuentes:
- Source Monitor
- Change Detection
- Health Check
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MonitorStatus(str, Enum):
    """Estado del monitor."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class ChangeType(str, Enum):
    """Tipo de cambio."""
    NEW = "new"
    UPDATED = "updated"
    DELETED = "deleted"
    DEPRECATED = "deprecated"


@dataclass
class SourceHealth:
    """Salud de fuente."""
    source: str
    status: MonitorStatus
    
    # Metrics
    response_time_ms: float = 0.0
    last_check: str = ""
    consecutive_failures: int = 0
    
    # Availability
    uptime_percentage: float = 100.0
    last_downtime: str = ""
    last_recovery: str = ""
    
    def is_healthy(self) -> bool:
        """Verifica si está saludable."""
        return self.status == MonitorStatus.HEALTHY


@dataclass
class ChangeEvent:
    """Evento de cambio."""
    event_id: str
    source: str
    change_type: ChangeType
    
    # Document info
    document_id: str = ""
    document_title: str = ""
    
    # Change details
    version: str = ""
    previous_version: str = ""
    
    # Priority
    priority: str = "normal"  # critical, high, normal, low
    
    # Timestamp
    detected_at: str = ""
    published_at: str = ""
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.now().isoformat()
    
    def is_critical(self) -> bool:
        """Es cambio crítico."""
        return self.priority == "critical"


@dataclass
class MonitoringConfig:
    """Configuración de monitoreo."""
    source: str
    
    # Check frequency
    check_interval_seconds: int = 3600  # 1 hour
    
    # Health thresholds
    max_response_time_ms: float = 5000.0
    max_failures: int = 3
    
    # Change detection
    detect_new: bool = True
    detect_updates: bool = True
    detect_deletions: bool = False
    detect_deprecations: bool = True
    
    # Alerting
    alert_on_failure: bool = True
    alert_on_critical: bool = True


class BaseSourceMonitor(ABC):
    """Clase base para monitores de fuente."""
    
    @abstractmethod
    async def check_health(self, source: str) -> SourceHealth:
        """Verifica salud de fuente."""
        ...
    
    @abstractmethod
    async def detect_changes(self, source: str) -> list[ChangeEvent]:
        """Detecta cambios."""
        ...


class InMemorySourceMonitor(BaseSourceMonitor):
    """Monitor de fuentes en memoria."""
    
    def __init__(self):
        self._health: dict[str, SourceHealth] = {}
        self._changes: list[ChangeEvent] = []
    
    async def check_health(self, source: str) -> SourceHealth:
        """Verifica salud de fuente."""
        # Mock implementation
        health = SourceHealth(
            source=source,
            status=MonitorStatus.HEALTHY,
            response_time_ms=100.0,
            last_check=datetime.now().isoformat(),
        )
        
        self._health[source] = health
        return health
    
    async def detect_changes(self, source: str) -> list[ChangeEvent]:
        """Detecta cambios."""
        # Mock - return empty list (no changes detected)
        return []
    
    async def record_change(self, event: ChangeEvent) -> None:
        """Registra cambio."""
        self._changes.append(event)
    
    async def get_recent_changes(
        self,
        source: str | None = None,
        limit: int = 100,
    ) -> list[ChangeEvent]:
        """Obtiene cambios recientes."""
        changes = self._changes
        
        if source:
            changes = [c for c in changes if c.source == source]
        
        return changes[-limit:]
    
    async def get_critical_changes(self) -> list[ChangeEvent]:
        """Obtiene cambios críticos."""
        return [c for c in self._changes if c.is_critical()]


class HealthChecker:
    """Verificador de salud."""
    
    def __init__(self, monitor: BaseSourceMonitor):
        self._monitor = monitor
        self._thresholds = {
            "response_time_ms": 5000,
            "failure_count": 3,
            "uptime_percentage": 95.0,
        }
    
    async def check(self, source: str) -> SourceHealth:
        """Realiza verificación."""
        health = await self._monitor.check_health(source)
        
        # Apply thresholds
        if health.response_time_ms > self._thresholds["response_time_ms"]:
            health.status = MonitorStatus.DEGRADED
        
        if health.consecutive_failures >= self._thresholds["failure_count"]:
            health.status = MonitorStatus.DOWN
        
        return health
    
    async def check_all(self, sources: list[str]) -> list[SourceHealth]:
        """Verifica todas las fuentes."""
        results = []
        
        for source in sources:
            health = await self.check(source)
            results.append(health)
        
        return results
    
    def get_unhealthy_sources(self, health_list: list[SourceHealth]) -> list[str]:
        """Obtiene fuentes no saludables."""
        return [
            h.source for h in health_list
            if h.status != MonitorStatus.HEALTHY
        ]


class ChangeDetector:
    """Detector de cambios."""
    
    def __init__(self, monitor: BaseSourceMonitor):
        self._monitor = monitor
    
    async def detect_all(self, sources: list[str]) -> list[ChangeEvent]:
        """Detecta cambios en todas las fuentes."""
        all_changes = []
        
        for source in sources:
            changes = await self._monitor.detect_changes(source)
            all_changes.extend(changes)
        
        # Sort by priority and date
        all_changes.sort(
            key=lambda c: (
                0 if c.is_critical() else 1,
                c.detected_at,
            ),
            reverse=True
        )
        
        return all_changes
    
    def filter_by_type(
        self,
        changes: list[ChangeEvent],
        change_type: ChangeType,
    ) -> list[ChangeEvent]:
        """Filtra por tipo de cambio."""
        return [c for c in changes if c.change_type == change_type]
    
    def filter_by_priority(
        self,
        changes: list[ChangeEvent],
        priority: str,
    ) -> list[ChangeEvent]:
        """Filtra por prioridad."""
        return [c for c in changes if c.priority == priority]


__all__ = [
    "MonitorStatus",
    "ChangeType",
    "SourceHealth",
    "ChangeEvent",
    "MonitoringConfig",
    "BaseSourceMonitor",
    "InMemorySourceMonitor",
    "HealthChecker",
    "ChangeDetector",
]
