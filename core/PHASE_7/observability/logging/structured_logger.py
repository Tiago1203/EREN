"""
PHASE 7 - EPIC 4: Structured Logger

JSON structured logging:
- Correlation IDs
- Multi-tenant context
- Log levels
- Context enrichment
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import json
import threading
import uuid


class LogLevel(str, Enum):
    """Niveles de log."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """Logger estructurado en JSON."""

    LEVEL_ORDER = {
        LogLevel.DEBUG: 10,
        LogLevel.INFO: 20,
        LogLevel.WARNING: 30,
        LogLevel.ERROR: 40,
        LogLevel.CRITICAL: 50,
    }

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        include_context: bool = True,
    ):
        self._name = name
        self._level = level
        self._include_context = include_context
        self._default_fields: dict[str, Any] = {}
        self._handlers: list[callable] = []
        self._tenant_context: dict[str, Any] = {}
        self._lock = threading.Lock()

    def add_handler(self, handler: callable) -> None:
        """Añade un handler de log."""
        self._handlers.append(handler)

    def set_tenant_context(self, tenant_id: Optional[str] = None, **kwargs) -> None:
        """Establece contexto de tenant."""
        with self._lock:
            if tenant_id:
                self._tenant_context["tenant_id"] = tenant_id
            self._tenant_context.update(kwargs)

    def clear_tenant_context(self) -> None:
        """Limpia contexto de tenant."""
        with self._lock:
            self._tenant_context.clear()

    def _log(
        self,
        level: LogLevel,
        message: str,
        correlation_id: Optional[str] = None,
        **extra,
    ) -> None:
        """Internal log method."""
        if self.LEVEL_ORDER[level] < self.LEVEL_ORDER[self._level]:
            return

        with self._lock:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level.value,
                "logger": self._name,
                "message": message,
                "correlation_id": correlation_id or self._default_fields.get("correlation_id") or str(uuid.uuid4()),
            }

            if self._include_context:
                record["context"] = {
                    **self._tenant_context,
                    **self._default_fields,
                    **extra,
                }

            for handler in self._handlers:
                try:
                    handler(record)
                except Exception:
                    pass

    def debug(self, message: str, **kwargs) -> None:
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Log request HTTP."""
        self.info(
            f"{method} {path} {status_code}",
            event="http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            tenant_id=tenant_id,
            user_id=user_id,
        )

    def log_audit_event(
        self,
        category: str,
        action: str,
        resource_id: str,
        actor_id: str,
        tenant_id: Optional[str] = None,
        success: bool = True,
        details: Optional[dict] = None,
    ) -> None:
        """Log evento de auditoría."""
        self.info(
            f"AUDIT: {category}/{action} on {resource_id} by {actor_id}",
            event="audit",
            audit_category=category,
            audit_action=action,
            resource_id=resource_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            success=success,
            details=details or {},
        )

    def log_tenant_operation(
        self,
        operation: str,
        tenant_id: str,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Log operación multi-tenant."""
        self.info(
            f"Tenant operation: {operation} on {tenant_id}",
            event="tenant_operation",
            operation=operation,
            tenant_id=tenant_id,
            success=success,
            duration_ms=duration_ms,
            error=error,
        )

    def log_failover(
        self,
        cluster: str,
        from_node: str,
        to_node: str,
        trigger: str,
        success: bool,
        duration_ms: float,
    ) -> None:
        """Log failover (EPIC 3)."""
        self.warning(
            f"Failover in {cluster}: {from_node} -> {to_node}",
            event="failover",
            cluster=cluster,
            from_node=from_node,
            to_node=to_node,
            trigger=trigger,
            success=success,
            duration_ms=duration_ms,
        )

    def log_scaling(
        self,
        service: str,
        old_replicas: int,
        new_replicas: int,
        trigger: str,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Log scaling event (EPIC 3)."""
        self.info(
            f"Scaling {service}: {old_replicas} -> {new_replicas}",
            event="scaling",
            service=service,
            old_replicas=old_replicas,
            new_replicas=new_replicas,
            trigger=trigger,
            tenant_id=tenant_id,
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        actor_id: str,
        resource: str,
        details: Optional[dict] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Log evento de seguridad."""
        log_fn = self.warning if severity in ("low", "medium") else self.critical
        log_fn(
            f"Security: {event_type} by {actor_id} on {resource}",
            event="security",
            security_event_type=event_type,
            severity=severity,
            actor_id=actor_id,
            resource=resource,
            tenant_id=tenant_id,
            details=details or {},
        )


# Default handlers
def console_handler(record: dict) -> None:
    """Handler que imprime a consola."""
    level = record["level"]
    color_map = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    color = color_map.get(level, "")
    reset = "\033[0m"
    ctx = record.get("context", {})
    tenant = ctx.get("tenant_id", "")
    corr_id = record.get("correlation_id", "")[:8]
    print(f"{color}{record['timestamp']} [{level}] {corr_id} {tenant} {record['message']}{reset}")


def json_file_handler(filename: str):
    """Factory de handler que escribe a archivo JSON."""
    def handler(record: dict) -> None:
        with open(filename, "a") as f:
            f.write(json.dumps(record) + "\n")
    return handler


# Global logger registry
_loggers: dict[str, StructuredLogger] = {}
_lock = threading.Lock()


def get_logger(name: str, level: LogLevel = LogLevel.INFO) -> StructuredLogger:
    """Obtiene o crea logger."""
    with _lock:
        if name not in _loggers:
            logger = StructuredLogger(name, level)
            logger.add_handler(console_handler)
            _loggers[name] = logger
        return _loggers[name]
