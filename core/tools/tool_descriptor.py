"""Tool descriptor for the Cognitive Tool Engine.

Defines the ToolDescriptor class - the canonical representation
of a tool in the system.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .tool_types import (
    CircuitBreakerConfig,
    RateLimitConfig,
    RetryPolicy,
    SecurityLevel,
    ToolCapability,
    ToolCategory,
    ToolContract,
    ToolCost,
    ToolMetadata,
    ToolParameter,
    ToolPerformance,
    ToolPriority,
    ToolStatus,
)

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class ToolDescriptor:
    """Canonical representation of a tool.

    A tool is an external capability that EREN can invoke. Tools are described
    by their capabilities, not by their implementation.

    Key principles:
    - Tools are defined by WHAT they do, not HOW they do it
    - EREN never knows implementation details
    - Tools declare their capabilities and requirements
    - Tools have policies for retry, timeout, circuit breaker

    Example:
        tool_id: "supabase.query"
        name: "Supabase Database Query"
        provider: "supabase_client"
        category: DATABASE
        capabilities: ["query", "transaction"]
        parameters: [...]
        timeout: 30.0
    """

    # Identity
    tool_id: str
    name: str
    description: str
    provider: str  # Provider/engine that implements this tool

    # Classification
    category: ToolCategory
    version: str = "1.0.0"
    priority: ToolPriority = ToolPriority.NORMAL
    status: ToolStatus = ToolStatus.AVAILABLE
    security_level: SecurityLevel = SecurityLevel.AUTHENTICATED

    # Capabilities
    capabilities: tuple[ToolCapability, ...] = field(default_factory=tuple)
    parameters: tuple[ToolParameter, ...] = field(default_factory=tuple)

    # Contracts
    contract: ToolContract = field(default_factory=ToolContract)

    # Policies
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    # Performance and cost
    cost: ToolCost = field(default_factory=ToolCost)
    performance: ToolPerformance = field(default_factory=ToolPerformance)

    # Metadata
    metadata: ToolMetadata = field(default_factory=ToolMetadata)

    # Factory methods
    @classmethod
    def create(
        cls,
        tool_id: str,
        name: str,
        description: str,
        provider: str,
        category: ToolCategory,
        **kwargs,
    ) -> ToolDescriptor:
        """Create a new tool descriptor with common defaults.

        Args:
            tool_id: Unique identifier
            name: Human-readable name
            description: What this tool does
            provider: Provider name
            category: Tool category
            **kwargs: Additional attributes

        Returns:
            A new ToolDescriptor instance.
        """
        return cls(
            tool_id=tool_id,
            name=name,
            description=description,
            provider=provider,
            category=ToolCategory(category) if isinstance(category, str) else category,
            metadata=ToolMetadata.now(**kwargs.pop("metadata", {})),
            **kwargs,
        )

    # Identity methods
    @property
    def id_string(self) -> str:
        """Get the tool ID as a string."""
        return self.tool_id

    # Status methods
    def is_active(self) -> bool:
        """Check if the tool is currently active."""
        return self.status == ToolStatus.ACTIVE

    def is_available(self) -> bool:
        """Check if the tool is available for execution."""
        return self.status in (
            ToolStatus.AVAILABLE,
            ToolStatus.ACTIVE,
        )

    def is_healthy(self) -> bool:
        """Check if tool health is acceptable."""
        return self.performance.success_rate >= 0.9

    # Capability methods
    def has_capability(self, capability: str) -> bool:
        """Check if tool provides a specific capability."""
        return any(c.name == capability for c in self.capabilities)

    def get_capability(self, capability: str) -> ToolCapability | None:
        """Get a specific capability."""
        for cap in self.capabilities:
            if cap.name == capability:
                return cap
        return None

    # Parameter methods
    def get_parameter(self, name: str) -> ToolParameter | None:
        """Get a parameter by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_required_parameters(self) -> tuple[ToolParameter, ...]:
        """Get all required parameters."""
        return tuple(p for p in self.parameters if p.required)

    # Policy methods
    def should_retry(self) -> bool:
        """Check if tool should be retried on failure."""
        return self.retry_policy.strategy != "none"

    def get_timeout(self) -> float:
        """Get the execution timeout."""
        return self.contract.timeout_seconds

    # Performance methods
    def get_avg_latency(self) -> float:
        """Get average execution latency."""
        return self.performance.avg_execution_ms

    def is_within_cost_budget(self, budget: float) -> bool:
        """Check if tool is within cost budget."""
        return self.cost.credits <= budget

    # String representation
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.name} ({self.tool_id}) [{self.status.name}]"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"ToolDescriptor("
            f"id={self.tool_id!r}, "
            f"name={self.name!r}, "
            f"provider={self.provider!r}, "
            f"status={self.status.name!r})"
        )


# =============================================================================
# Tool Templates
# =============================================================================


class ToolTemplates:
    """Predefined tool templates for common tool types."""

    @staticmethod
    def database_query(
        provider: str,
        database: str,
    ) -> ToolDescriptor:
        """Template for database query tools."""
        return ToolDescriptor.create(
            tool_id=f"{provider}.query",
            name=f"{database} Query",
            description=f"Execute queries on {database}",
            provider=provider,
            category=ToolCategory.DATABASE,
            capabilities=(
                ToolCapability(name="query", description="Execute SQL queries"),
                ToolCapability(name="transaction", description="Execute transactions"),
            ),
            parameters=(
                ToolParameter(
                    name="query",
                    type="string",
                    description="SQL query to execute",
                    required=True,
                ),
                ToolParameter(
                    name="params",
                    type="object",
                    description="Query parameters",
                    required=False,
                ),
            ),
        )

    @staticmethod
    def vector_search(
        provider: str,
        collection: str,
    ) -> ToolDescriptor:
        """Template for vector search tools."""
        return ToolDescriptor.create(
            tool_id=f"{provider}.search",
            name=f"{collection} Vector Search",
            description=f"Search {collection} using vector embeddings",
            provider=provider,
            category=ToolCategory.VECTOR_STORE,
            capabilities=(
                ToolCapability(name="search", description="Vector similarity search"),
                ToolCapability(name="index", description="Index new vectors"),
            ),
            parameters=(
                ToolParameter(
                    name="query_vector",
                    type="array",
                    description="Query embedding vector",
                    required=True,
                ),
                ToolParameter(
                    name="top_k",
                    type="integer",
                    description="Number of results",
                    required=False,
                    default=10,
                ),
            ),
        )

    @staticmethod
    def llm_completion(
        provider: str,
        model: str,
    ) -> ToolDescriptor:
        """Template for LLM completion tools."""
        return ToolDescriptor.create(
            tool_id=f"{provider}.completion",
            name=f"{model} Completion",
            description=f"Generate completions using {model}",
            provider=provider,
            category=ToolCategory.LLM,
            capabilities=(
                ToolCapability(name="completion", description="Text completion"),
                ToolCapability(name="chat", description="Chat completion"),
            ),
            parameters=(
                ToolParameter(
                    name="prompt",
                    type="string",
                    description="Input prompt",
                    required=True,
                ),
                ToolParameter(
                    name="max_tokens",
                    type="integer",
                    description="Maximum tokens to generate",
                    required=False,
                    default=1000,
                ),
            ),
        )

    @staticmethod
    def fhir_read(
        provider: str,
    ) -> ToolDescriptor:
        """Template for FHIR read tools."""
        return ToolDescriptor.create(
            tool_id=f"{provider}.fhir_read",
            name="FHIR Resource Read",
            description="Read FHIR resources from EHR",
            provider=provider,
            category=ToolCategory.FHIR,
            security_level=SecurityLevel.PRIVILEGED,
            capabilities=(
                ToolCapability(name="read", description="Read FHIR resources"),
                ToolCapability(name="search", description="Search FHIR resources"),
            ),
            parameters=(
                ToolParameter(
                    name="resource_type",
                    type="string",
                    description="FHIR resource type",
                    required=True,
                ),
                ToolParameter(
                    name="resource_id",
                    type="string",
                    description="Resource ID",
                    required=False,
                ),
            ),
        )
