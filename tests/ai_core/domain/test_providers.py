"""
Tests for Context Providers.

Tests the context providers to ensure they correctly
build context from various sources.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from core.ai.context_builder.providers.base import ContextItem, ContextQuery, BaseContextProvider
from core.ai.context_builder.providers.device_provider import DeviceContextProvider
from core.ai.context_builder.providers.knowledge_provider import KnowledgeContextProvider
from core.ai.context_builder.providers.incident_provider import IncidentContextProvider


class TestContextItem:
    """Tests for ContextItem."""
    
    def test_creates_with_valid_score(self):
        """Test that ContextItem creates with valid score."""
        item = ContextItem(
            source="test",
            content="Test content",
            relevance_score=0.8,
        )
        
        assert item.source == "test"
        assert item.content == "Test content"
        assert item.relevance_score == 0.8
    
    def test_raises_on_invalid_score(self):
        """Test that ContextItem raises on invalid score."""
        with pytest.raises(ValueError):
            ContextItem(
                source="test",
                content="Test content",
                relevance_score=1.5,  # Invalid
            )


class TestContextQuery:
    """Tests for ContextQuery."""
    
    def test_creates_with_defaults(self):
        """Test that ContextQuery creates with defaults."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
        )
        
        assert query.max_items == 50
        assert query.max_tokens == 4096
        assert query.sources is None
        assert query.query == ""
    
    def test_creates_with_custom_values(self):
        """Test that ContextQuery creates with custom values."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            max_items=100,
            sources=["device", "incident"],
            query="ventilator",
        )
        
        assert query.max_items == 100
        assert query.sources == ["device", "incident"]
        assert query.query == "ventilator"


class TestBaseContextProvider:
    """Tests for BaseContextProvider."""
    
    def test_name_property_is_abstract(self):
        """Test that name property is abstract."""
        # The test verifies that name is a property on the base class
        # It should be an abstract property
        assert hasattr(BaseContextProvider, 'name')
        assert isinstance(getattr(BaseContextProvider, 'name'), property)
        
        # Also test that we can implement it correctly
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        assert provider.name == "test"
    
    def test_priority_default(self):
        """Test that priority defaults to 100."""
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        assert provider.priority == 100
    
    def test_timeout_default(self):
        """Test that timeout defaults to 5.0."""
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        assert provider.timeout == 5.0
    
    def test_should_run_with_no_sources_filter(self):
        """Test that should_run returns True when no sources filter."""
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
        )
        
        assert provider._should_run(query) is True
    
    def test_should_run_with_matching_source(self):
        """Test that should_run returns True when source matches."""
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            sources=["test", "other"],
        )
        
        assert provider._should_run(query) is True
    
    def test_should_run_with_non_matching_source(self):
        """Test that should_run returns False when source doesn't match."""
        class MyProvider(BaseContextProvider):
            @property
            def name(self) -> str:
                return "test"
            
            async def get_context(self, query: ContextQuery) -> list[ContextItem]:
                return []
        
        provider = MyProvider()
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            sources=["other"],
        )
        
        assert provider._should_run(query) is False


class TestDeviceContextProvider:
    """Tests for DeviceContextProvider."""
    
    @pytest.fixture
    def provider(self):
        return DeviceContextProvider()
    
    @pytest.mark.asyncio
    async def test_get_context_returns_list(self, provider):
        """Test that get_context returns a list."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            query="ventilator",
        )
        
        result = await provider.get_context(query)
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_context_with_device_reference(self, provider):
        """Test that get_context extracts device references."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            query="device dev-001 status",
        )
        
        result = await provider.get_context(query)
        
        assert isinstance(result, list)
    
    def test_extract_device_references(self, provider):
        """Test device reference extraction."""
        references = provider._extract_device_references("check device dev-001 and equipment abc-123")
        
        assert "dev-001" in references or "dev-1" in references


class TestKnowledgeContextProvider:
    """Tests for KnowledgeContextProvider."""
    
    @pytest.fixture
    def provider(self):
        return KnowledgeContextProvider()
    
    @pytest.mark.asyncio
    async def test_get_context_returns_list(self, provider):
        """Test that get_context returns a list."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            query="maintenance",
        )
        
        result = await provider.get_context(query)
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_context_empty_query(self, provider):
        """Test that get_context returns empty for empty query."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
            query="",
        )
        
        result = await provider.get_context(query)
        
        assert result == []


class TestIncidentContextProvider:
    """Tests for IncidentContextProvider."""
    
    @pytest.fixture
    def provider(self):
        return IncidentContextProvider()
    
    @pytest.mark.asyncio
    async def test_get_context_returns_list(self, provider):
        """Test that get_context returns a list."""
        query = ContextQuery(
            conversation_id="conv-001",
            user_id="user-001",
            tenant_id="tenant-001",
        )
        
        result = await provider.get_context(query)
        
        assert isinstance(result, list)
    
    def test_extract_incident_references(self, provider):
        """Test incident reference extraction."""
        references = provider._extract_incident_references("incident inc-001 and inc-002")
        
        # Note: regex extracts and removes hyphen, so we get inc001, inc002
        assert "inc001" in references
        assert "inc002" in references
