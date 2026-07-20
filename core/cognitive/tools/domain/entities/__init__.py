"""Tools domain entities."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolType(str, Enum):
    """Tool type enumeration."""
    QUERY = "query"
    ACTION = "action"
    EXTERNAL = "external"


@dataclass(frozen=True)
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str  # string, integer, float, boolean, enum, object
    description: str
    required: bool = True
    default: Any = None
    enum_values: list[str] | None = None


@dataclass(frozen=True)
class ToolReturn:
    """Tool return type definition."""
    type: str
    description: str


@dataclass
class Tool:
    """Tool definition."""
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: ToolReturn | None = None
    tool_type: ToolType = ToolType.QUERY
    requires_approval: bool = False
    
    def validate_parameters(self, params: dict) -> tuple[bool, list[str]]:
        """Validate parameters against definition."""
        errors = []
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"Missing required parameter: {param.name}")
        return len(errors) == 0, errors


@dataclass
class ToolCall:
    """A call to a tool."""
    tool_name: str
    parameters: dict
    call_id: str | None = None


@dataclass
class ToolResult:
    """Result from a tool execution."""
    success: bool
    data: Any = None
    error: str | None = None
    execution_time_ms: int = 0
    
    @classmethod
    def success(cls, data: Any, execution_time_ms: int = 0) -> "ToolResult":
        return cls(success=True, data=data, execution_time_ms=execution_time_ms)
    
    @classmethod
    def error(cls, error: str, execution_time_ms: int = 0) -> "ToolResult":
        return cls(success=False, error=error, execution_time_ms=execution_time_ms)
    
    @classmethod
    def pending_approval(cls, message: str) -> "ToolResult":
        return cls(success=False, error=f"PENDING_APPROVAL: {message}")
