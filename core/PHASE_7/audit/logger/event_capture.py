"""
PHASE 7 - EPIC 1: Event Capture

Decoradores para captura automática de eventos de auditoría:
- @audit_action - Decorador para auditar funciones
- @audit_phi_access - Decorador específico para acceso PHI
- Context manager para auditoría de bloques
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional
import time
import uuid

from core.PHASE_7.audit.logger.audit_logger import (
    AuditLogger,
    AuditCategory,
    AuditAction,
    AuditEvent,
)


# Global audit logger instance
_global_audit_logger: Optional[AuditLogger] = None


def set_audit_logger(logger: AuditLogger) -> None:
    """Configura el logger global de auditoría."""
    global _global_audit_logger
    _global_audit_logger = logger


def get_audit_logger() -> AuditLogger:
    """Obtiene el logger global, creando uno si no existe."""
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
    return _global_audit_logger


def audit_action(
    category: AuditCategory,
    action: AuditAction,
    resource_type: str,
    resource_id_param: Optional[str] = None,
    capture_args: bool = True,
    capture_result: bool = False,
    phi_access: bool = False,
):
    """
    Decorador para auditar automáticamente acciones de funciones.

    Uso:
        @audit_action(
            category=AuditCategory.DATA_MODIFICATION,
            action=AuditAction.CREATE,
            resource_type="equipo",
            resource_id_param="equipo_id"
        )
        def create_equipo(equipo_id, name, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return _execute_and_log(func, args, kwargs, category, action, resource_type, resource_id_param, capture_args, capture_result, phi_access)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await _execute_and_log_async(func, args, kwargs, category, action, resource_type, resource_id_param, capture_args, capture_result, phi_access)

        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def audit_phi_access(
    resource_type: str,
    purpose_of_use: str = "treatment",
):
    """
    Decorador específico para auditar acceso PHI (HIPAA requirement).

    Uso:
        @audit_phi_access(resource_type="paciente")
        def get_patient(patient_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_audit_logger()
            start = time.time()

            # Extract actor info from kwargs or use defaults
            actor_id = kwargs.get("actor_id", kwargs.get("user_id", "system"))
            actor_name = kwargs.get("actor_name", kwargs.get("user_name", "System"))
            actor_role = kwargs.get("actor_role", kwargs.get("role", ""))

            # Extract resource ID
            resource_id = _extract_param(func, args, kwargs, resource_id=None) or str(kwargs.get("id", kwargs.get(f"{resource_type}_id", "")))

            # Extract session info
            session_id = kwargs.get("session_id", "")
            ip_address = kwargs.get("ip_address", "")

            # Execute function
            success = True
            error_msg = ""
            result = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration_ms = int((time.time() - start) * 1000)

                logger.log(
                    actor_id=actor_id,
                    actor_name=actor_name,
                    actor_role=actor_role,
                    category=AuditCategory.PHI_ACCESS,
                    action=AuditAction.READ,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    session_id=session_id,
                    ip_address=ip_address,
                    purpose_of_use=purpose_of_use,
                    is_phi_access=True,
                    success=success,
                    error_message=error_msg,
                    duration_ms=duration_ms,
                    metadata={"function": func.__name__} if capture_args else {},
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_audit_logger()
            start = time.time()

            actor_id = kwargs.get("actor_id", kwargs.get("user_id", "system"))
            actor_name = kwargs.get("actor_name", kwargs.get("user_name", "System"))
            actor_role = kwargs.get("actor_role", kwargs.get("role", ""))
            resource_id = _extract_param(func, args, kwargs, resource_id=None) or str(kwargs.get("id", ""))
            session_id = kwargs.get("session_id", "")
            ip_address = kwargs.get("ip_address", "")

            success = True
            error_msg = ""
            result = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                duration_ms = int((time.time() - start) * 1000)
                logger.log(
                    actor_id=actor_id,
                    actor_name=actor_name,
                    actor_role=actor_role,
                    category=AuditCategory.PHI_ACCESS,
                    action=AuditAction.READ,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    session_id=session_id,
                    ip_address=ip_address,
                    purpose_of_use=purpose_of_use,
                    is_phi_access=True,
                    success=success,
                    error_message=error_msg,
                    duration_ms=duration_ms,
                    metadata={"function": func.__name__},
                )

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def _execute_and_log(
    func: Callable,
    args: tuple,
    kwargs: dict,
    category: AuditCategory,
    action: AuditAction,
    resource_type: str,
    resource_id_param: Optional[str],
    capture_args: bool,
    capture_result: bool,
    phi_access: bool,
) -> Any:
    """Ejecuta función síncrona y loguea auditoría."""
    logger = get_audit_logger()
    start = time.time()

    # Extract actor info
    actor_id = kwargs.get("actor_id", "system")
    actor_name = kwargs.get("actor_name", "System")
    actor_role = kwargs.get("actor_role", "")
    session_id = kwargs.get("session_id", "")
    ip_address = kwargs.get("ip_address", "")
    reason = kwargs.get("reason", "")

    # Extract resource ID
    resource_id = _extract_param(func, args, kwargs, resource_id_param)

    # Build previous/new values for modifications
    prev_value = ""
    new_value = ""
    if capture_args and action in [AuditAction.CREATE, AuditAction.UPDATE]:
        new_value = str(kwargs)

    success = True
    error_msg = ""
    result = None

    try:
        result = func(*args, **kwargs)
        if capture_result:
            prev_value = str(kwargs)
            new_value = str(result)
        return result
    except Exception as e:
        success = False
        error_msg = str(e)
        raise
    finally:
        duration_ms = int((time.time() - start) * 1000)

        logger.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            category=category,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            session_id=session_id,
            ip_address=ip_address,
            reason=reason,
            previous_value=prev_value,
            new_value=new_value,
            is_phi_access=phi_access or category == AuditCategory.PHI_ACCESS,
            success=success,
            error_message=error_msg,
            duration_ms=duration_ms,
            metadata={"function": func.__name__} if capture_args else {},
        )


async def _execute_and_log_async(
    func: Callable,
    args: tuple,
    kwargs: dict,
    category: AuditCategory,
    action: AuditAction,
    resource_type: str,
    resource_id_param: Optional[str],
    capture_args: bool,
    capture_result: bool,
    phi_access: bool,
) -> Any:
    """Ejecuta función asíncrona y loguea auditoría."""
    logger = get_audit_logger()
    start = time.time()

    actor_id = kwargs.get("actor_id", "system")
    actor_name = kwargs.get("actor_name", "System")
    actor_role = kwargs.get("actor_role", "")
    session_id = kwargs.get("session_id", "")
    ip_address = kwargs.get("ip_address", "")
    reason = kwargs.get("reason", "")
    resource_id = _extract_param(func, args, kwargs, resource_id_param)

    prev_value = ""
    new_value = ""
    if capture_args and action in [AuditAction.CREATE, AuditAction.UPDATE]:
        new_value = str(kwargs)

    success = True
    error_msg = ""
    result = None

    try:
        result = await func(*args, **kwargs)
        if capture_result:
            prev_value = str(kwargs)
            new_value = str(result)
        return result
    except Exception as e:
        success = False
        error_msg = str(e)
        raise
    finally:
        duration_ms = int((time.time() - start) * 1000)
        logger.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            category=category,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            session_id=session_id,
            ip_address=ip_address,
            reason=reason,
            previous_value=prev_value,
            new_value=new_value,
            is_phi_access=phi_access or category == AuditCategory.PHI_ACCESS,
            success=success,
            error_message=error_msg,
            duration_ms=duration_ms,
            metadata={"function": func.__name__} if capture_args else {},
        )


def _extract_param(
    func: Callable,
    args: tuple,
    kwargs: dict,
    param_name: Optional[str],
) -> Optional[str]:
    """Extrae un parámetro de función por nombre o posición."""
    if param_name and param_name in kwargs:
        return kwargs[param_name]

    # Try first positional argument (usually ID)
    if args:
        return str(args[0])

    # Try common param names
    for name in ["id", "resource_id", f"{func.__name__.split('_')[0]}_id"]:
        if name in kwargs:
            return str(kwargs[name])

    return None


class AuditContext:
    """Context manager para auditoría de bloques de código."""

    def __init__(
        self,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        category: AuditCategory,
        action: AuditAction,
        resource_type: str,
        resource_id: str = "",
        session_id: str = "",
        ip_address: str = "",
        reason: str = "",
        is_phi_access: bool = False,
    ):
        self.actor_id = actor_id
        self.actor_name = actor_name
        self.actor_role = actor_role
        self.category = category
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.session_id = session_id
        self.ip_address = ip_address
        self.reason = reason
        self.is_phi_access = is_phi_access
        self.logger = get_audit_logger()
        self.start_time: float = 0
        self.event: Optional[AuditEvent] = None

    def __enter__(self) -> "AuditContext":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        success = exc_type is None
        error_msg = str(exc_val) if exc_val else ""

        self.event = self.logger.log(
            actor_id=self.actor_id,
            actor_name=self.actor_name,
            actor_role=self.actor_role,
            category=self.category,
            action=self.action,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            session_id=self.session_id,
            ip_address=self.ip_address,
            reason=self.reason,
            success=success,
            error_message=error_msg,
            duration_ms=duration_ms,
            is_phi_access=self.is_phi_access,
        )
