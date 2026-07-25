"""
PHASE 7 - EPIC 4: Alert Manager

Alert routing and management:
- Alert rules
- Notification channels
- Alert deduplication
- Integration con EPIC 1 (audit) y EPIC 3 (HA)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
import threading
import uuid


class AlertSeverity(str, Enum):
    """Severidad de alerta."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    """Estado de alerta."""
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


class AlertChannel(str, Enum):
    """Canales de notificación."""
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"


@dataclass
class AlertRule:
    """Regla de alerta."""
    rule_id: str
    name: str
    description: str
    condition: str           # e.g., "cpu_usage > 90"
    severity: AlertSeverity
    channels: list[AlertChannel]
    enabled: bool = True
    cooldown_seconds: int = 300
    tenant_id: Optional[str] = None


@dataclass
class Alert:
    """Alerta."""
    alert_id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    fired_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: str = ""
    tenant_id: Optional[str] = None
    labels: dict = field(default_factory=dict)
    annotations: dict = field(default_factory=dict)


@dataclass
class Incident:
    """Incidente (agrupación de alertas)."""
    incident_id: str
    title: str
    severity: AlertSeverity
    status: str              # open, acknowledged, resolved
    created_at: datetime
    resolved_at: Optional[datetime] = None
    assignee: str = ""
    tenant_id: Optional[str] = None
    alerts: list = field(default_factory=list)


class AlertManager:
    """Gestor de alertas."""

    def __init__(self):
        self._rules: dict[str, AlertRule] = {}
        self._alerts: list[Alert] = []
        self._incidents: list[Incident] = []
        self._last_fired: dict[str, datetime] = {}
        self._lock = threading.Lock()
        self._handlers: dict[AlertChannel, callable] = {}

    def register_handler(self, channel: AlertChannel, handler: callable) -> None:
        """Registra handler para canal."""
        self._handlers[channel] = handler

    def add_rule(self, rule: AlertRule) -> None:
        """Añade regla de alerta."""
        with self._lock:
            self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remueve regla."""
        with self._lock:
            if rule_id in self._rules:
                del self._rules[rule_id]
                return True
            return False

    def fire_alert(
        self,
        rule_id: str,
        message: str,
        labels: Optional[dict] = None,
        annotations: Optional[dict] = None,
    ) -> Optional[Alert]:
        """Dispara alerta."""
        with self._lock:
            rule = self._rules.get(rule_id)
            if not rule or not rule.enabled:
                return None

            # Check cooldown
            if rule_id in self._last_fired:
                elapsed = (datetime.now(timezone.utc) - self._last_fired[rule_id]).total_seconds()
                if elapsed < rule.cooldown_seconds:
                    return None

            self._last_fired[rule_id] = datetime.now(timezone.utc)

            alert = Alert(
                alert_id=f"alert-{uuid.uuid4().hex[:12]}",
                rule_id=rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                status=AlertStatus.FIRING,
                message=message,
                fired_at=datetime.now(timezone.utc),
                tenant_id=rule.tenant_id,
                labels=labels or {},
                annotations=annotations or {},
            )

            self._alerts.append(alert)

            # Create incident for critical/high
            if rule.severity in (AlertSeverity.CRITICAL, AlertSeverity.HIGH):
                self._create_incident(alert)

            # Send notifications
            for channel in rule.channels:
                if channel in self._handlers:
                    try:
                        self._handlers[channel](alert)
                    except Exception:
                        pass

            return alert

    def _create_incident(self, alert: Alert) -> Incident:
        """Crea incidente desde alerta."""
        incident = Incident(
            incident_id=f"inc-{uuid.uuid4().hex[:12]}",
            title=f"Incident: {alert.rule_name}",
            severity=alert.severity,
            status="open",
            created_at=datetime.now(timezone.utc),
            tenant_id=alert.tenant_id,
            alerts=[alert],
        )
        self._incidents.append(incident)
        return incident

    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        """Resuelve alerta."""
        with self._lock:
            for alert in self._alerts:
                if alert.alert_id == alert_id:
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now(timezone.utc)
                    return alert
        return None

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[Alert]:
        """Confirma alerta."""
        with self._lock:
            for alert in self._alerts:
                if alert.alert_id == alert_id:
                    alert.status = AlertStatus.ACKNOWLEDGED
                    alert.acknowledged_at = datetime.now(timezone.utc)
                    alert.acknowledged_by = acknowledged_by
                    return alert
        return None

    def get_firing_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        tenant_id: Optional[str] = None,
    ) -> list[Alert]:
        """Obtiene alertas firing."""
        with self._lock:
            alerts = [a for a in self._alerts if a.status == AlertStatus.FIRING]
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            if tenant_id:
                alerts = [a for a in alerts if a.tenant_id == tenant_id]
            return sorted(alerts, key=lambda a: a.fired_at, reverse=True)

    def get_incidents(
        self,
        status: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> list[Incident]:
        """Obtiene incidentes."""
        with self._lock:
            incidents = self._incidents
            if status:
                incidents = [i for i in incidents if i.status == status]
            if tenant_id:
                incidents = [i for i in incidents if i.tenant_id == tenant_id]
            return sorted(incidents, key=lambda i: i.created_at, reverse=True)

    def resolve_incident(self, incident_id: str) -> Optional[Incident]:
        """Resuelve incidente."""
        with self._lock:
            for incident in self._incidents:
                if incident.incident_id == incident_id:
                    incident.status = "resolved"
                    incident.resolved_at = datetime.now(timezone.utc)
                    for alert in incident.alerts:
                        self.resolve_alert(alert.alert_id)
                    return incident
        return None

    def get_alert_summary(self, tenant_id: Optional[str] = None) -> dict:
        """Resumen de alertas."""
        with self._lock:
            alerts = self._alerts
            if tenant_id:
                alerts = [a for a in alerts if a.tenant_id == tenant_id]

            firing = [a for a in alerts if a.status == AlertStatus.FIRING]
            acknowledged = [a for a in alerts if a.status == AlertStatus.ACKNOWLEDGED]
            resolved = [a for a in alerts if a.status == AlertStatus.RESOLVED]

            by_severity = {}
            for s in AlertSeverity:
                by_severity[s.value] = len([a for a in firing if a.severity == s])

            return {
                "total_alerts": len(alerts),
                "firing": len(firing),
                "acknowledged": len(acknowledged),
                "resolved": len(resolved),
                "firing_by_severity": by_severity,
                "total_incidents": len(self._incidents),
                "open_incidents": sum(1 for i in self._incidents if i.status == "open"),
            }

    # ── Predefined Rules ─────────────────────────────────────
    def setup_default_rules(self) -> None:
        """Configura reglas por defecto."""
        rules = [
            AlertRule(
                rule_id="high-error-rate",
                name="High Error Rate",
                description="Error rate > 5% in 5 minutes",
                condition="error_rate > 0.05",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_seconds=300,
            ),
            AlertRule(
                rule_id="high-latency",
                name="High API Latency",
                description="P99 latency > 2s",
                condition="p99_latency > 2000",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.SLACK],
                cooldown_seconds=600,
            ),
            AlertRule(
                rule_id="cpu-high",
                name="High CPU Usage",
                description="CPU > 90%",
                condition="cpu_percent > 90",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_seconds=300,
            ),
            AlertRule(
                rule_id="memory-high",
                name="High Memory Usage",
                description="Memory > 85%",
                condition="memory_percent > 85",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.SLACK],
                cooldown_seconds=600,
            ),
            AlertRule(
                rule_id="database-connection-exhausted",
                name="Database Connection Pool Exhausted",
                description="No available connections",
                condition="db_available_connections == 0",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY, AlertChannel.SLACK],
                cooldown_seconds=60,
            ),
            AlertRule(
                rule_id="quota-exceeded",
                name="Tenant Quota Exceeded",
                description="Tenant exceeded resource quota",
                condition="quota_usage_percent > 100",
                severity=AlertSeverity.MEDIUM,
                channels=[AlertChannel.EMAIL],
                cooldown_seconds=3600,
            ),
            AlertRule(
                rule_id="failover-triggered",
                name="Failover Triggered",
                description="Automatic failover was triggered",
                condition="failover_count > 0",
                severity=AlertSeverity.CRITICAL,
                channels=[AlertChannel.EMAIL, AlertChannel.PAGERDUTY, AlertChannel.SLACK],
                cooldown_seconds=300,
            ),
            AlertRule(
                rule_id="backup-failed",
                name="Backup Failed",
                description="Automated backup failed",
                condition="backup_status == failed",
                severity=AlertSeverity.HIGH,
                channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
                cooldown_seconds=86400,
            ),
        ]
        for rule in rules:
            self.add_rule(rule)
