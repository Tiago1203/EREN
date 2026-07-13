"""Type definitions for the Cognitive Tool Engine.

Provides comprehensive type definitions for tools, execution, and policies.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Tool Status and Classification
# =============================================================================


class ToolStatus(IntEnum):
    """Lifecycle status of a tool."""

    UNREGISTERED = 0
    AVAILABLE = 1
    LOADING = 2
    ACTIVE = 3
    SUSPENDED = 4
    DEPRECATED = 5
    FAILED = 6
    UNAVAILABLE = 7


class ToolPriority(IntEnum):
    """Priority levels for tool execution."""

    SYSTEM = 100
    CRITICAL = 80
    HIGH = 60
    NORMAL = 40
    LOW = 20
    BACKGROUND = 10


class SecurityLevel(IntEnum):
    """Security clearance levels for tools."""

    PUBLIC = 0
    AUTHENTICATED = 10
    PRIVILEGED = 20
    ADMIN = 30
    SYSTEM = 100


# =============================================================================
# Tool Category
# =============================================================================


class ToolCategory(str, Enum):
    """Categories of tools."""

    DATABASE = "database"  # PostgreSQL, Supabase
    VECTOR_STORE = "vector_store"  # Qdrant, Pinecone
    LLM = "llm"  # OpenAI, Anthropic
    SEARCH = "search"  # Search APIs
    FHIR = "fhir"  # FHIR/R4
    DICOM = "dicom"  # DICOM/PACS
    IMAGING = "imaging"  # Medical imaging
    SENSORS = "sensors"  # Sensor data
    API = "api"  # Generic APIs
    WEBHOOK = "webhook"  # Webhook integrations
    NOTIFICATION = "notification"  # Alerts, emails
    STORAGE = "storage"  # File storage
    COMPUTE = "compute"  # Computation
    ML = "ml"  # ML models
    INTEGRATION = "integration"  # Hospital systems


# =============================================================================
# Tool Definition
# =============================================================================


@dataclass(frozen=True, slots=True)
class ToolParameter:
    """A parameter for a tool."""

    name: str
    type: str  # string, integer, float, boolean, object, array
    description: str = ""
    required: bool = True
    default: Any = None
    enum: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ToolCapability:
    """A capability provided by a tool."""

    name: str
    description: str = ""
    version: str = "1.0.0"


# =============================================================================
# Tool Cost and Performance
# =============================================================================


@dataclass
class ToolCost:
    """Cost estimation for tool execution."""

    credits: float = 0.0  # Credit cost
    monetary: float = 0.0  # Dollar cost
    tokens: int = 0  # Token cost (for LLM)
    api_calls: int = 1  # Number of API calls


@dataclass
class ToolPerformance:
    """Performance metrics for a tool."""

    avg_execution_ms: float = 0.0
    min_execution_ms: float = 0.0
    max_execution_ms: float = 0.0
    success_rate: float = 1.0  # 0.0 to 1.0
    total_executions: int = 0


# =============================================================================
# Tool Contract
# =============================================================================


@dataclass(frozen=True, slots=True)
class ToolContract:
    """Contract definition for a tool."""

    input_schema: str = ""  # JSON schema
    output_schema: str = ""  # JSON schema
    error_schema: str = ""  # JSON schema for errors
    timeout_seconds: float = 30.0
    retry_policy: str = "none"  # none, exponential, linear


# =============================================================================
# Tool Metadata
# =============================================================================


@dataclass(frozen=True, slots=True)
class ToolMetadata:
    """Metadata for a tool."""

    version: str = "1.0.0"
    author: str = ""
    license: str = ""
    repository_url: str = ""
    documentation_url: str = ""
    support_contact: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    created_at: str = ""
    updated_at: str = ""
    deprecated_at: str = ""
    deprecation_message: str = ""

    @classmethod
    def now(cls, **kwargs) -> ToolMetadata:
        """Create metadata with current timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            created_at=timestamp,
            updated_at=timestamp,
            **kwargs,
        )


# =============================================================================
# Execution Types
# =============================================================================


class ExecutionStatus(str, Enum):
    """Status of a tool execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RATE_LIMITED = "rate_limited"


class ExecutionMode(str, Enum):
    """Mode of tool execution."""

    SYNCHRONOUS = "synchronous"  # Wait for result
    ASYNCHRONOUS = "asynchronous"  # Return immediately
    STREAMING = "streaming"  # Stream results
    BATCH = "batch"  # Batch processing


@dataclass
class ExecutionContext:
    """Context for tool execution."""

    correlation_id: str = ""
    session_id: str = ""
    user_id: str = ""
    hospital_id: str = ""
    request_id: str = ""
    priority: ToolPriority = ToolPriority.NORMAL
    mode: ExecutionMode = ExecutionMode.SYNCHRONOUS
    timeout_seconds: float = 30.0
    metadata: dict = field(default_factory=dict)


# =============================================================================
# Execution Result
# =============================================================================


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_id: str
    execution_id: str
    status: ExecutionStatus
    output: Any = None
    error: str = ""
    error_code: str = ""
    execution_time_ms: float = 0.0
    timestamp: str = ""
    retry_count: int = 0
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

    def is_retryable(self) -> bool:
        """Check if execution can be retried."""
        return self.status in (
            ExecutionStatus.FAILED,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.RATE_LIMITED,
        )


# =============================================================================
# Pipeline Types
# =============================================================================


@dataclass
class PipelineStep:
    """A step in a tool pipeline."""

    step_id: str
    tool_id: str
    parameters: dict = field(default_factory=dict)
    depends_on: tuple[str, ...] = field(default_factory=tuple)  # step_ids
    condition: str = ""  # Expression to evaluate
    timeout_seconds: float = 30.0


@dataclass
class PipelineDefinition:
    """Definition of a tool pipeline."""

    pipeline_id: str
    name: str
    description: str = ""
    steps: tuple[PipelineStep, ...] = field(default_factory=tuple)
    parallel_execution: bool = False
    continue_on_error: bool = False


@dataclass
class PipelineResult:
    """Result of a pipeline execution."""

    pipeline_id: str
    execution_id: str
    status: ExecutionStatus
    step_results: tuple[ToolResult, ...] = field(default_factory=tuple)
    total_time_ms: float = 0.0
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# =============================================================================
# Circuit Breaker Types
# =============================================================================


class CircuitState(str, Enum):
    """State of a circuit breaker."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes before closing
    timeout_seconds: float = 60.0  # Time before half-open
    half_open_max_calls: int = 3  # Max calls in half-open


# =============================================================================
# Health Check Types
# =============================================================================


class HealthStatus(str, Enum):
    """Health status of a tool."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    tool_id: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: str = ""
    last_check: str = ""
    consecutive_failures: int = 0


# =============================================================================
# Rate Limiting Types
# =============================================================================


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: float = 10.0
    requests_per_minute: float = 100.0
    requests_per_hour: float = 1000.0
    burst_size: int = 20


@dataclass
class RateLimitStatus:
    """Status of rate limiting."""

    tool_id: str
    allowed: bool = True
    remaining: int = 0
    reset_at: str = ""
    retry_after_seconds: float = 0.0


# =============================================================================
# Retry Policy Types
# =============================================================================


class RetryStrategy(str, Enum):
    """Strategy for retries."""

    NONE = "none"
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"


@dataclass
class RetryPolicy:
    """Policy for retrying failed executions."""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter: bool = True
    retry_on_timeout: bool = True
    retry_on_rate_limit: bool = True


# =============================================================================
# Observability Types
# =============================================================================


@dataclass
class ToolMetrics:
    """Metrics for a tool."""

    tool_id: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    timed_out_executions: int = 0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    p50_execution_time_ms: float = 0.0
    p95_execution_time_ms: float = 0.0
    p99_execution_time_ms: float = 0.0
    last_execution: str = ""
    last_success: str = ""
    last_failure: str = ""


@dataclass
class ToolEvent:
    """Event emitted by tool operations."""

    event_type: str  # execution.started, execution.completed, etc.
    tool_id: str
    execution_id: str = ""
    timestamp: str = ""
    data: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# =============================================================================
# Filter Types
# =============================================================================


@dataclass
class ToolFilter:
    """Filter criteria for tool queries."""

    category: ToolCategory | None = None
    status: ToolStatus | None = None
    min_priority: ToolPriority | None = None
    min_security: SecurityLevel | None = None
    capability: str | None = None
    tag: str | None = None
    provider: str | None = None
    available_only: bool = False


@dataclass
class ToolSelectorCriteria:
    """Criteria for selecting a tool."""

    capability: str
    context: ExecutionContext | None = None
    prefer_healthy: bool = True
    prefer_fast: bool = True
    prefer_cheap: bool = False
    max_cost: float | None = None
    max_latency_ms: float | None = None
