"""
PHASE 7 - EPIC 4: Notification Channels

Canales de notificación para alertas:
- Email
- Slack
- PagerDuty
- Webhook
- SMS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AlertPayload:
    """Payload de alerta para notificación."""
    alert_id: str
    rule_name: str
    severity: str
    message: str
    fired_at: str
    tenant_id: Optional[str]
    labels: dict
    annotations: dict


class NotificationChannel:
    """Base class para canales de notificación."""

    def send(self, alert: AlertPayload) -> bool:
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Canal de email."""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_email: str,
        to_emails: list[str],
        use_tls: bool = True,
    ):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._from_email = from_email
        self._to_emails = to_emails
        self._use_tls = use_tls

    def send(self, alert: AlertPayload) -> bool:
        """Envía email."""
        # In production: use smtplib
        print(f"[EMAIL] Sending alert {alert.alert_id} to {self._to_emails}")
        print(f"  Subject: [{alert.severity.upper()}] {alert.rule_name}")
        print(f"  Body: {alert.message}")
        return True

    def format_email(self, alert: AlertPayload) -> dict:
        """Formatea email."""
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "ℹ️",
            "info": "💡",
        }
        emoji = severity_emoji.get(alert.severity, "📢")

        subject = f"{emoji} [{alert.severity.upper()}] {alert.rule_name}"
        body = f"""
EREN Alert Notification
════════════════════════════════════════

Rule: {alert.rule_name}
Severity: {alert.severity.upper()}
Alert ID: {alert.alert_id}
Time: {alert.fired_at}
Tenant: {alert.tenant_id or "N/A"}

Message:
{alert.message}

Labels: {alert.labels}
Annotations: {alert.annotations}

---
Sent by EREN Observability System
"""
        return {"subject": subject, "body": body.strip()}


class SlackChannel(NotificationChannel):
    """Canal de Slack."""

    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self._webhook_url = webhook_url
        self._channel = channel

    def send(self, alert: AlertPayload) -> bool:
        """Envía a Slack."""
        # In production: POST to webhook_url
        print(f"[SLACK] Sending alert {alert.alert_id} to {self._channel}")
        print(f"  Text: [{alert.severity}] {alert.rule_name}: {alert.message}")
        return True

    def format_slack_message(self, alert: AlertPayload) -> dict:
        """Formatea mensaje de Slack."""
        color_map = {
            "critical": "#FF0000",
            "high": "#FFA500",
            "medium": "#FFFF00",
            "low": "#00FF00",
            "info": "#808080",
        }
        color = color_map.get(alert.severity, "#808080")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {alert.rule_name}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{alert.severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Alert ID:*\n{alert.alert_id}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{alert.fired_at}"},
                    {"type": "mrkdwn", "text": f"*Tenant:*\n{alert.tenant_id or 'N/A'}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:*\n{alert.message}"},
            },
        ]

        return {
            "channel": self._channel,
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks,
                }
            ],
        }


class PagerDutyChannel(NotificationChannel):
    """Canal de PagerDuty."""

    def __init__(self, routing_key: str):
        self._routing_key = routing_key

    def send(self, alert: AlertPayload) -> bool:
        """Envía a PagerDuty."""
        # In production: POST to PagerDuty Events API
        print(f"[PAGERDUTY] Sending alert {alert.alert_id}")
        print(f"  Summary: {alert.rule_name}: {alert.message}")
        return True

    def format_pagerduty_event(self, alert: AlertPayload) -> dict:
        """Formatea evento de PagerDuty."""
        urgency_map = {
            "critical": "high",
            "high": "high",
            "medium": "low",
            "low": "low",
            "info": "low",
        }
        return {
            "routing_key": self._routing_key,
            "event_action": "trigger",
            "dedup_key": f"eren-{alert.alert_id}",
            "payload": {
                "summary": f"[{alert.severity.upper()}] {alert.rule_name}: {alert.message}",
                "severity": urgency_map.get(alert.severity, "low"),
                "source": "EREN",
                "custom_details": {
                    "alert_id": alert.alert_id,
                    "rule_name": alert.rule_name,
                    "tenant_id": alert.tenant_id,
                    "labels": alert.labels,
                    "annotations": alert.annotations,
                },
            },
        }


class WebhookChannel(NotificationChannel):
    """Canal de webhook genérico."""

    def __init__(self, url: str, method: str = "POST", headers: Optional[dict] = None):
        self._url = url
        self._method = method
        self._headers = headers or {"Content-Type": "application/json"}

    def send(self, alert: AlertPayload) -> bool:
        """Envía webhook."""
        # In production: use httpx or requests
        print(f"[WEBHOOK] POST {self._url}")
        print(f"  Alert: {alert.alert_id} - {alert.rule_name}")
        return True

    def format_webhook_payload(self, alert: AlertPayload) -> dict:
        """Formatea payload de webhook."""
        return {
            "event": "alert.fired",
            "alert": {
                "id": alert.alert_id,
                "rule_name": alert.rule_name,
                "severity": alert.severity,
                "message": alert.message,
                "fired_at": alert.fired_at,
                "tenant_id": alert.tenant_id,
                "labels": alert.labels,
                "annotations": alert.annotations,
            },
        }


# Factory
def create_channel(
    channel_type: str,
    config: dict,
) -> NotificationChannel:
    """Factory de canales."""
    if channel_type == "email":
        return EmailChannel(
            smtp_host=config["smtp_host"],
            smtp_port=config.get("smtp_port", 587),
            from_email=config["from_email"],
            to_emails=config["to_emails"],
        )
    elif channel_type == "slack":
        return SlackChannel(
            webhook_url=config["webhook_url"],
            channel=config.get("channel", "#alerts"),
        )
    elif channel_type == "pagerduty":
        return PagerDutyChannel(routing_key=config["routing_key"])
    elif channel_type == "webhook":
        return WebhookChannel(
            url=config["url"],
            method=config.get("method", "POST"),
            headers=config.get("headers"),
        )
    else:
        raise ValueError(f"Unknown channel type: {channel_type}")
