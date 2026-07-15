"""Cognitive Tool Engine (CTE).

EREN's bridge to the external world. The CTE manages all external tools
without EREN knowing implementation details.

EREN never knows technologies. EREN only requests capabilities.
The Tool Engine decides which tool to use.

Architecture only — no AI, no implementations.
"""

from __future__ import annotations

# Re-export existing types
from core.tools.catalog import (
    DICOMTool,
    EmailTool,
    ExternalTool,
    FHIRTool,
    HL7Tool,
    OCRTool,
    PDFTool,
    SupabaseTool,
    ToolCategory,
    VoiceTool,
)
from core.tools.engine import ToolsEngine
from core.tools.exceptions import (
    CircuitBreakerOpenError,
    PipelineExecutionError,
    PipelineStepError,
    RateLimitExceededError,
    ToolAlreadyRegisteredError,
    ToolExecutionError,
    ToolHealthError,
    ToolInvocationError,
    ToolNotFoundError,
    ToolPermissionError,
    ToolsError,
    ToolTimeoutError,
    ToolUnavailableError,
    ToolValidationError,
)
from core.tools.interfaces import ToolsPort

# New CTE components
from core.tools.tool_descriptor import ToolDescriptor, ToolTemplates
from core.tools.tool_executor import ToolExecutor
from core.tools.tool_pipeline import ToolPipeline
from core.tools.tool_registry import ToolRegistry, ToolSelector
from core.tools.tool_types import (
    CircuitBreakerConfig,
    CircuitState,
    ExecutionContext,
    ExecutionMode,
    ExecutionStatus,
    HealthCheckResult,
    HealthStatus,
    RateLimitConfig,
    RateLimitStatus,
    RetryPolicy,
    RetryStrategy,
    SecurityLevel,
    ToolCapability,
    ToolContract,
    ToolCost,
    ToolParameter,
    ToolPerformance,
    ToolPriority,
    ToolResult,
    ToolSelectorCriteria,
    ToolStatus,
)

# PR-059: Universal Tool Calling Engine
from core.tools.sandbox import (
    SandboxConfig,
    SandboxManager,
    SandboxState,
    SandboxType,
    SandboxMetrics,
    ToolSandbox,
    ProcessSandbox,
    ThreadSandbox,
)
from core.tools.discovery import (
    DiscoveryConfig,
    DiscoveredTool,
    ToolDiscovery,
    tool as tool_decorator,
    get_tool_metadata,
    is_tool,
)
from core.tools.validation import (
    ValidationConfig,
    ValidationError,
    ValidationErrorType,
    ValidationLevel,
    ValidationResult,
    SchemaValidator,
    ResultValidator,
    ToolValidator,
)
from core.tools.execution import (
    ExecutionConfig,
    ExecutionEngineState,
    ExecutionMetrics,
    ToolExecutionRuntime,
)

__all__ = [
    # Legacy exports
    "ToolsEngine",
    "ToolsPort",
    "ExternalTool",
    "ToolCategory",
    "SupabaseTool",
    "PDFTool",
    "OCRTool",
    "EmailTool",
    "VoiceTool",
    "FHIRTool",
    "HL7Tool",
    "DICOMTool",
    # Exceptions
    "ToolsError",
    "ToolNotFoundError",
    "ToolAlreadyRegisteredError",
    "ToolInvocationError",
    "ToolExecutionError",
    "ToolTimeoutError",
    "ToolValidationError",
    "ToolUnavailableError",
    "ToolPermissionError",
    "CircuitBreakerOpenError",
    "RateLimitExceededError",
    "PipelineExecutionError",
    "PipelineStepError",
    "ToolHealthError",
    # Core
    "ToolRegistry",
    "ToolExecutor",
    "ToolPipeline",
    "ToolSelector",
    "ToolDescriptor",
    "ToolTemplates",
    # Types
    "ToolStatus",
    "ToolPriority",
    "SecurityLevel",
    "CircuitBreakerConfig",
    "RateLimitConfig",
    "RetryPolicy",
    "RetryStrategy",
    "CircuitState",
    "ExecutionStatus",
    "ExecutionMode",
    "ExecutionContext",
    "ToolResult",
    "HealthStatus",
    "HealthCheckResult",
    "RateLimitStatus",
    "ToolCapability",
    "ToolParameter",
    "ToolContract",
    "ToolCost",
    "ToolPerformance",
    # PR-059: Universal Tool Calling Engine
    "SandboxConfig",
    "SandboxManager",
    "SandboxState",
    "SandboxType",
    "SandboxMetrics",
    "ToolSandbox",
    "ProcessSandbox",
    "ThreadSandbox",
    "DiscoveryConfig",
    "DiscoveredTool",
    "ToolDiscovery",
    "tool_decorator",
    "get_tool_metadata",
    "is_tool",
    "ValidationConfig",
    "ValidationError",
    "ValidationErrorType",
    "ValidationLevel",
    "ValidationResult",
    "SchemaValidator",
    "ResultValidator",
    "ToolValidator",
    "ExecutionConfig",
    "ExecutionEngineState",
    "ExecutionMetrics",
    "ToolExecutionRuntime",
]
