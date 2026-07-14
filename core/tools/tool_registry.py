"""Tool registry for the Cognitive Tool Engine.

The central registry for all tools available to EREN.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Callable
from typing import TYPE_CHECKING

from .exceptions import ToolAlreadyRegisteredError, ToolNotFoundError
from .tool_descriptor import ToolDescriptor
from .tool_executor import ToolExecutor
from .tool_types import (
    ToolCategory,
    ToolFilter,
)

if TYPE_CHECKING:
    pass


class ToolRegistry:
    """Central registry for tools.

    The registry maintains a catalog of all available tools.
    Tools are discovered by capabilities, not by implementation.

    Features:
    - Thread-safe registration
    - Category-based organization
    - Capability-based discovery
    - Tool metadata management
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        # Primary storage: tool_id -> ToolDescriptor
        self._tools: dict[str, ToolDescriptor] = {}

        # Indexes
        self._by_category: dict[ToolCategory, list[str]] = defaultdict(list)
        self._by_provider: dict[str, list[str]] = defaultdict(list)
        self._by_capability: dict[str, list[str]] = defaultdict(list)
        self._by_tag: dict[str, list[str]] = defaultdict(list)

        # Thread safety
        self._lock = threading.RLock()

        # Executor
        self._executor = ToolExecutor()

    # =========================================================================
    # Registration Operations
    # =========================================================================

    def register(
        self,
        tool: ToolDescriptor,
        handler: Callable | None = None,
        *,
        replace: bool = False,
    ) -> None:
        """Register a tool.

        Args:
            tool: The tool descriptor.
            handler: Optional execution handler.
            replace: If True, replace existing tool.

        Raises:
            ToolAlreadyRegisteredError: If tool exists and replace=False.
        """
        with self._lock:
            if tool.tool_id in self._tools and not replace:
                raise ToolAlreadyRegisteredError(tool.tool_id)

            # Store tool
            self._tools[tool.tool_id] = tool

            # Index
            self._index_tool(tool)

            # Register with executor if handler provided
            if handler:
                self._executor.register_tool(tool, handler)

    def unregister(self, tool_id: str) -> None:
        """Unregister a tool.

        Args:
            tool_id: The tool ID.

        Raises:
            ToolNotFoundError: If tool not found.
        """
        with self._lock:
            if tool_id not in self._tools:
                raise ToolNotFoundError(tool_id)

            tool = self._tools[tool_id]
            self._unindex_tool(tool)
            del self._tools[tool_id]
            self._executor.unregister_tool(tool_id)

    def register_handler(
        self,
        tool_id: str,
        handler: Callable,
    ) -> None:
        """Register an execution handler for a tool.

        Args:
            tool_id: The tool ID.
            handler: The handler function.

        Raises:
            ToolNotFoundError: If tool not found.
        """
        with self._lock:
            if tool_id not in self._tools:
                raise ToolNotFoundError(tool_id)

            tool = self._tools[tool_id]
            self._executor.register_tool(tool, handler)

    # =========================================================================
    # Retrieval Operations
    # =========================================================================

    def get(self, tool_id: str) -> ToolDescriptor:
        """Get a tool by ID.

        Args:
            tool_id: The tool ID.

        Returns:
            The tool descriptor.

        Raises:
            ToolNotFoundError: If not found.
        """
        with self._lock:
            if tool_id not in self._tools:
                raise ToolNotFoundError(tool_id)
            return self._tools[tool_id]

    def get_or_none(self, tool_id: str) -> ToolDescriptor | None:
        """Get a tool by ID, returning None if not found."""
        return self._tools.get(tool_id)

    def list_all(self) -> list[ToolDescriptor]:
        """List all registered tools."""
        with self._lock:
            return list(self._tools.values())

    def __contains__(self, tool_id: str) -> bool:
        """Check if a tool is registered."""
        return tool_id in self._tools

    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)

    # =========================================================================
    # Discovery Operations
    # =========================================================================

    def find_by_category(
        self,
        category: ToolCategory,
    ) -> list[ToolDescriptor]:
        """Find tools by category.

        Args:
            category: The category.

        Returns:
            Tools in that category.
        """
        with self._lock:
            tool_ids = self._by_category.get(category, [])
            return [
                self._tools[tid]
                for tid in tool_ids
                if tid in self._tools
            ]

    def find_by_provider(
        self,
        provider: str,
    ) -> list[ToolDescriptor]:
        """Find tools by provider.

        Args:
            provider: The provider name.

        Returns:
            Tools from that provider.
        """
        with self._lock:
            tool_ids = self._by_provider.get(provider, [])
            return [
                self._tools[tid]
                for tid in tool_ids
                if tid in self._tools
            ]

    def find_by_capability(
        self,
        capability: str,
    ) -> list[ToolDescriptor]:
        """Find tools by capability.

        Args:
            capability: The capability name.

        Returns:
            Tools that provide the capability.
        """
        with self._lock:
            tool_ids = self._by_capability.get(capability, [])
            return [
                self._tools[tid]
                for tid in tool_ids
                if tid in self._tools
            ]

    def find_by_tag(
        self,
        tag: str,
    ) -> list[ToolDescriptor]:
        """Find tools by tag.

        Args:
            tag: The tag.

        Returns:
            Tools with that tag.
        """
        with self._lock:
            tool_ids = self._by_tag.get(tag, [])
            return [
                self._tools[tid]
                for tid in tool_ids
                if tid in self._tools
            ]

    def find_available(self) -> list[ToolDescriptor]:
        """Find all available tools.

        Returns:
            Available tools.
        """
        with self._lock:
            return [
                tool for tool in self._tools.values()
                if tool.is_available()
            ]

    def search(
        self,
        filter: ToolFilter,
    ) -> list[ToolDescriptor]:
        """Search tools with filters.

        Args:
            filter: The search filter.

        Returns:
            Matching tools.
        """
        with self._lock:
            results = list(self._tools.values())

            if filter.category:
                results = [t for t in results if t.category == filter.category]

            if filter.capability:
                results = [t for t in results if t.has_capability(filter.capability)]

            if filter.tag:
                results = [
                    t for t in results
                    if filter.tag in t.metadata.tags
                ]

            if filter.provider:
                results = [t for t in results if t.provider == filter.provider]

            if filter.available_only:
                results = [t for t in results if t.is_available()]

            return results

    # =========================================================================
    # Executor Access
    # =========================================================================

    def get_executor(self) -> ToolExecutor:
        """Get the tool executor.

        Returns:
            The tool executor.
        """
        return self._executor

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_statistics(self) -> dict:
        """Get registry statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            return {
                "total_tools": len(self._tools),
                "by_category": {
                    cat.value: len(tids)
                    for cat, tids in self._by_category.items()
                },
                "by_provider": dict(self._by_provider),
                "by_capability": dict(self._by_capability),
            }

    # =========================================================================
    # Indexing (Internal)
    # =========================================================================

    def _index_tool(self, tool: ToolDescriptor) -> None:
        """Index a tool for fast lookup."""
        # By category
        self._by_category[tool.category].append(tool.tool_id)

        # By provider
        self._by_provider[tool.provider].append(tool.tool_id)

        # By capability
        for cap in tool.capabilities:
            self._by_capability[cap.name].append(tool.tool_id)

        # By tag
        for tag in tool.metadata.tags:
            self._by_tag[tag].append(tool.tool_id)

    def _unindex_tool(self, tool: ToolDescriptor) -> None:
        """Remove tool from indexes."""
        # From category
        if tool.category in self._by_category:
            self._by_category[tool.category] = [
                tid for tid in self._by_category[tool.category]
                if tid != tool.tool_id
            ]

        # From provider
        if tool.provider in self._by_provider:
            self._by_provider[tool.provider] = [
                tid for tid in self._by_provider[tool.provider]
                if tid != tool.tool_id
            ]

        # From capabilities
        for cap in tool.capabilities:
            if cap.name in self._by_capability:
                self._by_capability[cap.name] = [
                    tid for tid in self._by_capability[cap.name]
                    if tid != tool.tool_id
                ]

        # From tags
        for tag in tool.metadata.tags:
            if tag in self._by_tag:
                self._by_tag[tag] = [
                    tid for tid in self._by_tag[tag]
                    if tid != tool.tool_id
                ]


# =============================================================================
# Tool Selector
# =============================================================================


class ToolSelector:
    """Selects the best tool for a given capability.

    The selector considers:
    - Availability
    - Performance (latency)
    - Cost
    - Health
    - User preferences
    """

    def __init__(self, registry: ToolRegistry) -> None:
        """Initialize tool selector.

        Args:
            registry: The tool registry.
        """
        self._registry = registry

    def select(
        self,
        capability: str,
        prefer_healthy: bool = True,
        prefer_fast: bool = True,
        prefer_cheap: bool = False,
    ) -> ToolDescriptor | None:
        """Select the best tool for a capability.

        Args:
            capability: The capability to select.
            prefer_healthy: Prefer healthy tools.
            prefer_fast: Prefer fast tools.
            prefer_cheap: Prefer cheap tools.

        Returns:
            The best tool or None if no tool found.
        """
        candidates = self._registry.find_by_capability(capability)

        if not candidates:
            return None

        # Filter to available
        candidates = [c for c in candidates if c.is_available()]

        if not candidates:
            return None

        # Score candidates
        scored = []
        for tool in candidates:
            score = self._calculate_score(
                tool,
                prefer_healthy=prefer_healthy,
                prefer_fast=prefer_fast,
                prefer_cheap=prefer_cheap,
            )
            scored.append((tool, score))

        # Return highest scoring
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]

    def select_with_fallback(
        self,
        capability: str,
    ) -> list[ToolDescriptor]:
        """Select tools with fallback chain.

        Args:
            capability: The capability to select.

        Returns:
            List of tools ordered by preference.
        """
        candidates = self._registry.find_by_capability(capability)
        candidates = [c for c in candidates if c.is_available()]

        # Score and sort
        scored = []
        for tool in candidates:
            score = self._calculate_score(
                tool,
                prefer_healthy=True,
                prefer_fast=True,
            )
            scored.append((tool, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in scored]

    def _calculate_score(
        self,
        tool: ToolDescriptor,
        prefer_healthy: bool,
        prefer_fast: bool,
        prefer_cheap: bool,
    ) -> float:
        """Calculate tool score."""
        score = 0.0

        # Health score (0-40)
        if prefer_healthy:
            success_rate = tool.performance.success_rate
            score += success_rate * 40

        # Speed score (0-30)
        if prefer_fast:
            # Lower latency is better
            latency = tool.performance.avg_execution_ms
            if latency > 0:
                # Score decreases as latency increases
                speed_score = max(0, 30 - (latency / 100))
                score += speed_score
            else:
                score += 30  # Unknown latency

        # Cost score (0-20)
        if prefer_cheap:
            # Lower cost is better
            cost = tool.cost.credits
            cost_score = max(0, 20 - (cost * 10))
            score += cost_score
            if cost == 0:
                score += 20

        # Availability bonus (0-10)
        if tool.status.value <= 3:  # AVAILABLE or ACTIVE
            score += 10

        return score
