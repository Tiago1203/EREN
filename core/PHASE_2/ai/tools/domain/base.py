"""
Base Domain Tool.

Abstract base class for all domain tools.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.PHASE_2.ai.tools import ToolDefinition, ToolResult, ToolStatus


@dataclass(frozen=True)
class DomainToolConfig:
    """Configuration for domain tools."""
    name: str
    description: str
    category: str = "domain"
    parameters_schema: dict = field(default_factory=dict)
    requires_tenant: bool = True
    requires_auth: bool = True


@dataclass
class ToolExecutionContext:
    """Context for tool execution."""
    tenant_id: str
    user_id: str | None = None
    session_id: str | None = None


class BaseDomainTool(ABC):
    """
    Base class for all domain tools.
    
    Provides common functionality for tool execution,
    error handling, and result formatting.
    """
    
    config: DomainToolConfig
    
    @abstractmethod
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """
        Execute the tool with given parameters.
        
        Args:
            parameters: Tool parameters from the AI
            context: Execution context with tenant/user info
            
        Returns:
            Tool result as dict with 'status' and 'data' keys
        """
        raise NotImplementedError
    
    def _validate_parameters(
        self,
        parameters: dict,
        required: list[str],
    ) -> None:
        """Validate required parameters are present."""
        missing = [p for p in required if p not in parameters]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
    
    def _format_success(
        self,
        data: Any,
        message: str | None = None,
    ) -> dict:
        """Format successful result."""
        return {
            "status": "success",
            "data": data,
            "message": message,
        }
    
    def _format_error(
        self,
        error: str,
        details: dict | None = None,
    ) -> dict:
        """Format error result."""
        return {
            "status": "error",
            "error": error,
            "details": details or {},
        }
    
    def _format_not_found(
        self,
        resource: str,
        resource_id: str,
    ) -> dict:
        """Format not found result."""
        return {
            "status": "not_found",
            "error": f"{resource} not found: {resource_id}",
        }
