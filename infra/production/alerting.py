"""
Alerting Module for EREN Production

Alert management and routing.
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import asyncio


class AlertSeverity(str, Enum):
    P1_CRITICAL = "P1"
    P2_HIGH = "P2"
    P3_MEDIUM = "P3"
    P4_LOW = "P4"


class Alert(BaseModel):
    id: str
    name: str
    severity: AlertSeverity
    message: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    acknowledged: bool = False
    resolved: bool = False


class AlertRule(BaseModel):
    name: str
    condition: str
    severity: AlertSeverity
    duration: str = "0m"
    channels: List[str] = ["in_app"]


ALERT_RULES = [
    AlertRule(
        name="ServiceDown",
        severity=AlertSeverity.P1_CRITICAL,
        condition="up == 0",
        duration="1m",
        channels=["sms", "call"]
    ),
    AlertRule(
        name="HighErrorRate",
        severity=AlertSeverity.P2_HIGH,
        condition="error_rate > 5",
        duration="5m",
        channels=["sms"]
    ),
    AlertRule(
        name="SlowResponse",
        severity=AlertSeverity.P3_MEDIUM,
        condition="p95_latency > 1000",
        duration="10m",
        channels=["email"]
    ),
    AlertRule(
        name="DiskSpaceLow",
        severity=AlertSeverity.P4_LOW,
        condition="disk_free < 10",
        duration="30m",
        channels=["slack"]
    ),
]


class AlertManager:
    """Manages alerts and routing."""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules = ALERT_RULES
        self.channels = {
            "in_app": self._send_in_app,
            "email": self._send_email,
            "sms": self._send_sms,
            "slack": self._send_slack,
        }
    
    async def create_alert(self, rule: AlertRule, metadata: Dict) -> Alert:
        """Create and route alert."""
        alert = Alert(
            id=f"alert-{datetime.utcnow().timestamp()}",
            name=rule.name,
            severity=rule.severity,
            message=f"{rule.name} triggered",
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        
        self.alerts[alert.id] = alert
        
        # Route to channels
        for channel in rule.channels:
            if channel in self.channels:
                await self.channels[channel](alert)
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            return True
        return False
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [a for a in self.alerts.values() if not a.resolved]
    
    async def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity."""
        return [a for a in self.alerts.values() if a.severity == severity]
    
    # Channel implementations
    async def _send_in_app(self, alert: Alert):
        """Send in-app notification."""
        pass
    
    async def _send_email(self, alert: Alert):
        """Send email notification."""
        pass
    
    async def _send_sms(self, alert: Alert):
        """Send SMS notification."""
        pass
    
    async def _send_slack(self, alert: Alert):
        """Send Slack notification."""
        pass


# On-call rotation
ON_CALL_ROTATION = [
    {"name": "Engineer 1", "email": "eng1@hospital.com"},
    {"name": "Engineer 2", "email": "eng2@hospital.com"},
    {"name": "Engineer 3", "email": "eng3@hospital.com"},
]


def get_current_on_call() -> Dict:
    """Get current on-call engineer."""
    index = int(datetime.utcnow().timestamp() / (7 * 24 * 3600)) % len(ON_CALL_ROTATION)
    return ON_CALL_ROTATION[index]
