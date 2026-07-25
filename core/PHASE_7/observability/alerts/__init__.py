"""EPIC 4: Monitoring & Observability — Alerts Module."""
from core.PHASE_7.observability.alerts.alert_manager import (
    AlertManager, AlertRule, Alert, AlertSeverity, AlertStatus,
    AlertChannel, Incident,
)
from core.PHASE_7.observability.alerts.notification_channels import (
    NotificationChannel, EmailChannel, SlackChannel,
    PagerDutyChannel, WebhookChannel, AlertPayload,
    create_channel,
)
