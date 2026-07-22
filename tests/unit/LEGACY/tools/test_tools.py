"""Tests for the Cognitive Tool Engine."""

from __future__ import annotations

import pytest

from core.LEGACY.tools import (
    ToolRegistry,
    ToolExecutor,
    ToolDescriptor,
    ToolSelector,
    ToolCategory,
    ToolStatus,
    ToolPriority,
    ToolCapability,
    ToolParameter,
    ToolContract,
    ExecutionContext,
    ExecutionStatus,
    ToolTemplates,
)


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_tool(self) -> None:
        """Registering a tool should work."""
        registry = ToolRegistry()

        tool = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test Tool",
            description="A test tool",
            provider="test_provider",
            category=ToolCategory.API,
        )

        registry.register(tool)

        assert "test.tool" in registry
        assert registry.get("test.tool").name == "Test Tool"

    def test_register_duplicate_raises(self) -> None:
        """Registering a duplicate tool should raise."""
        from core.LEGACY.tools.exceptions import ToolAlreadyRegisteredError

        registry = ToolRegistry()

        tool = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test Tool",
            description="A test tool",
            provider="test_provider",
            category=ToolCategory.API,
        )

        registry.register(tool)

        with pytest.raises(ToolAlreadyRegisteredError):
            registry.register(tool)

    def test_register_with_replace(self) -> None:
        """Registering with replace should work."""
        registry = ToolRegistry()

        tool1 = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test Tool V1",
            description="A test tool",
            provider="test_provider",
            category=ToolCategory.API,
        )

        tool2 = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test Tool V2",
            description="An updated test tool",
            provider="test_provider",
            category=ToolCategory.API,
        )

        registry.register(tool1)
        registry.register(tool2, replace=True)

        assert registry.get("test.tool").name == "Test Tool V2"

    def test_find_by_capability(self) -> None:
        """Finding by capability should work."""
        registry = ToolRegistry()

        tool = ToolDescriptor.create(
            tool_id="supabase.query",
            name="Supabase Query",
            description="Query Supabase database",
            provider="supabase",
            category=ToolCategory.DATABASE,
            capabilities=(
                ToolCapability(name="query"),
                ToolCapability(name="transaction"),
            ),
        )

        registry.register(tool)

        results = registry.find_by_capability("query")
        assert len(results) == 1
        assert results[0].tool_id == "supabase.query"

    def test_find_by_category(self) -> None:
        """Finding by category should work."""
        registry = ToolRegistry()

        tool = ToolDescriptor.create(
            tool_id="qdrant.search",
            name="Qdrant Search",
            description="Vector search",
            provider="qdrant",
            category=ToolCategory.VECTOR_STORE,
        )

        registry.register(tool)

        results = registry.find_by_category(ToolCategory.VECTOR_STORE)
        assert len(results) == 1
        assert results[0].tool_id == "qdrant.search"

    def test_unregister(self) -> None:
        """Unregistering should remove the tool."""
        from core.LEGACY.tools.exceptions import ToolNotFoundError

        registry = ToolRegistry()

        tool = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test Tool",
            description="A test tool",
            provider="test_provider",
            category=ToolCategory.API,
        )

        registry.register(tool)
        registry.unregister("test.tool")

        with pytest.raises(ToolNotFoundError):
            registry.get("test.tool")


class TestToolDescriptor:
    """Tests for ToolDescriptor."""

    def test_create(self) -> None:
        """Creating a tool should work."""
        tool = ToolDescriptor.create(
            tool_id="openai.chat",
            name="OpenAI Chat",
            description="Chat completion",
            provider="openai",
            category=ToolCategory.LLM,
        )

        assert tool.tool_id == "openai.chat"
        assert tool.category == ToolCategory.LLM
        assert tool.status == ToolStatus.AVAILABLE

    def test_has_capability(self) -> None:
        """has_capability should work."""
        tool = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test",
            description="Test",
            provider="test",
            category=ToolCategory.API,
            capabilities=(
                ToolCapability(name="query"),
                ToolCapability(name="search"),
            ),
        )

        assert tool.has_capability("query")
        assert tool.has_capability("search")
        assert not tool.has_capability("other")

    def test_is_available(self) -> None:
        """is_available should check status."""
        tool = ToolDescriptor.create(
            tool_id="test.tool",
            name="Test",
            description="Test",
            provider="test",
            category=ToolCategory.API,
        )

        assert tool.is_available()

        from dataclasses import replace
        inactive = replace(tool, status=ToolStatus.SUSPENDED)
        assert not inactive.is_available()


class TestToolSelector:
    """Tests for ToolSelector."""

    def test_select_best_tool(self) -> None:
        """Selecting best tool should work."""
        registry = ToolRegistry()
        selector = ToolSelector(registry)

        tool1 = ToolDescriptor.create(
            tool_id="slow.query",
            name="Slow Query",
            description="Slow database",
            provider="slow",
            category=ToolCategory.DATABASE,
            capabilities=(ToolCapability(name="query"),),
        )

        tool2 = ToolDescriptor.create(
            tool_id="fast.query",
            name="Fast Query",
            description="Fast database",
            provider="fast",
            category=ToolCategory.DATABASE,
            capabilities=(ToolCapability(name="query"),),
        )

        registry.register(tool1)
        registry.register(tool2)

        selected = selector.select("query")
        assert selected is not None

    def test_select_no_match(self) -> None:
        """Selecting non-existent capability should return None."""
        registry = ToolRegistry()
        selector = ToolSelector(registry)

        result = selector.select("nonexistent")
        assert result is None


class TestToolTemplates:
    """Tests for tool templates."""

    def test_database_query_template(self) -> None:
        """Database query template should create correct tool."""
        tool = ToolTemplates.database_query(
            provider="supabase",
            database="clinical_db",
        )

        assert tool.category == ToolCategory.DATABASE
        assert tool.has_capability("query")
        assert tool.has_capability("transaction")

    def test_vector_search_template(self) -> None:
        """Vector search template should create correct tool."""
        tool = ToolTemplates.vector_search(
            provider="qdrant",
            collection="medical_docs",
        )

        assert tool.category == ToolCategory.VECTOR_STORE
        assert tool.has_capability("search")
        assert tool.has_capability("index")

    def test_llm_completion_template(self) -> None:
        """LLM completion template should create correct tool."""
        tool = ToolTemplates.llm_completion(
            provider="openai",
            model="gpt-4",
        )

        assert tool.category == ToolCategory.LLM
        assert tool.has_capability("completion")
        assert tool.has_capability("chat")

    def test_fhir_read_template(self) -> None:
        """FHIR read template should create correct tool."""
        tool = ToolTemplates.fhir_read(provider="epic")

        assert tool.category == ToolCategory.FHIR
        assert tool.has_capability("read")
        assert tool.has_capability("search")
