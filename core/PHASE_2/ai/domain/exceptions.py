"""
Domain Gateway Exceptions.

These exceptions are raised by domain gateways when errors occur.
"""

from __future__ import annotations


class GatewayError(Exception):
    """Base exception for all gateway errors."""
    
    def __init__(self, message: str, gateway: str | None = None):
        self.message = message
        self.gateway = gateway
        super().__init__(message)
    
    def __str__(self) -> str:
        if self.gateway:
            return f"[{self.gateway}] {self.message}"
        return self.message


class DeviceNotFoundError(GatewayError):
    """Raised when a device is not found."""
    
    def __init__(
        self,
        device_id: str,
        tenant_id: str | None = None,
    ):
        self.device_id = device_id
        self.tenant_id = tenant_id
        message = f"Device not found: {device_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="DeviceGateway")


class IncidentNotFoundError(GatewayError):
    """Raised when an incident is not found."""
    
    def __init__(
        self,
        incident_id: str,
        tenant_id: str | None = None,
    ):
        self.incident_id = incident_id
        self.tenant_id = tenant_id
        message = f"Incident not found: {incident_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="IncidentGateway")


class KnowledgeNotFoundError(GatewayError):
    """Raised when a knowledge article is not found."""
    
    def __init__(
        self,
        article_id: str,
        tenant_id: str | None = None,
    ):
        self.article_id = article_id
        self.tenant_id = tenant_id
        message = f"Knowledge article not found: {article_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="KnowledgeGateway")


class RecommendationNotFoundError(GatewayError):
    """Raised when a recommendation is not found."""
    
    def __init__(
        self,
        recommendation_id: str,
        tenant_id: str | None = None,
    ):
        self.recommendation_id = recommendation_id
        self.tenant_id = tenant_id
        message = f"Recommendation not found: {recommendation_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="RecommendationGateway")


class HospitalNotFoundError(GatewayError):
    """Raised when a hospital/campus is not found."""
    
    def __init__(
        self,
        campus_id: str,
        tenant_id: str | None = None,
    ):
        self.campus_id = campus_id
        self.tenant_id = tenant_id
        message = f"Hospital/Campus not found: {campus_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="HospitalGateway")


class WorkOrderNotFoundError(GatewayError):
    """Raised when a work order is not found."""
    
    def __init__(
        self,
        work_order_id: str,
        tenant_id: str | None = None,
    ):
        self.work_order_id = work_order_id
        self.tenant_id = tenant_id
        message = f"Work order not found: {work_order_id}"
        if tenant_id:
            message += f" (tenant: {tenant_id})"
        super().__init__(message, gateway="WorkOrderGateway")


class GatewayTimeoutError(GatewayError):
    """Raised when a gateway operation times out."""
    
    def __init__(
        self,
        operation: str,
        timeout: float,
        gateway: str | None = None,
    ):
        self.operation = operation
        self.timeout = timeout
        message = f"Operation timed out: {operation} (timeout: {timeout}s)"
        super().__init__(message, gateway=gateway)


class GatewayValidationError(GatewayError):
    """Raised when validation fails."""
    
    def __init__(
        self,
        field: str,
        value: any,
        reason: str,
        gateway: str | None = None,
    ):
        self.field = field
        self.value = value
        self.reason = reason
        message = f"Validation failed for {field}={value}: {reason}"
        super().__init__(message, gateway=gateway)
