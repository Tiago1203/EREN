"""
Tests for Domain Tools.

Tests the domain tools to ensure they correctly
interact with gateways and return proper results.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from core.ai.tools.domain.base import BaseDomainTool, DomainToolConfig, ToolExecutionContext
from core.ai.tools.domain.device_tools import SearchDeviceTool, GetDeviceHistoryTool
from core.ai.tools.domain.knowledge_tools import SearchKnowledgeTool
from core.ai.tools.domain.hospital_tools import GetCapacityInfoTool


class TestToolExecutionContext:
    """Tests for ToolExecutionContext."""
    
    def test_creates_with_required_fields(self):
        """Test that ToolExecutionContext creates with required fields."""
        context = ToolExecutionContext(tenant_id="tenant-001")
        
        assert context.tenant_id == "tenant-001"
        assert context.user_id is None
        assert context.session_id is None
    
    def test_creates_with_all_fields(self):
        """Test that ToolExecutionContext creates with all fields."""
        context = ToolExecutionContext(
            tenant_id="tenant-001",
            user_id="user-001",
            session_id="session-001",
        )
        
        assert context.tenant_id == "tenant-001"
        assert context.user_id == "user-001"
        assert context.session_id == "session-001"


class TestDomainToolConfig:
    """Tests for DomainToolConfig."""
    
    def test_creates_with_defaults(self):
        """Test that DomainToolConfig creates with defaults."""
        config = DomainToolConfig(
            name="test_tool",
            description="Test description",
        )
        
        assert config.name == "test_tool"
        assert config.description == "Test description"
        assert config.category == "domain"
        assert config.requires_tenant is True
        assert config.requires_auth is True
    
    def test_creates_with_custom_values(self):
        """Test that DomainToolConfig creates with custom values."""
        config = DomainToolConfig(
            name="test_tool",
            description="Test description",
            category="custom.category",
            requires_tenant=False,
        )
        
        assert config.category == "custom.category"
        assert config.requires_tenant is False


class TestSearchDeviceTool:
    """Tests for SearchDeviceTool."""
    
    @pytest.fixture
    def mock_gateway(self):
        from core.ai.domain import DeviceDTO
        gateway = MagicMock()
        gateway.search = AsyncMock(return_value=[
            DeviceDTO(
                id="dev-001",
                serial_number="SN-12345",
                name="Test Device",
                device_type="Test",
                status="active",
                manufacturer="TestCorp",
                model="Model1",
                is_critical=True,
            ),
        ])
        return gateway
    
    @pytest.fixture
    def tool(self, mock_gateway):
        return SearchDeviceTool(mock_gateway)
    
    @pytest.fixture
    def context(self):
        return ToolExecutionContext(tenant_id="tenant-001")
    
    def test_config_has_correct_name(self, tool):
        """Test that tool config has correct name."""
        assert tool.config.name == "search_device"
    
    @pytest.mark.asyncio
    async def test_execute_returns_success(self, tool, context):
        """Test that execute returns success."""
        result = await tool.execute(
            {"query": "test"},
            context,
        )
        
        assert result["status"] == "success"
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_execute_validates_parameters(self, tool, context):
        """Test that execute validates required parameters."""
        result = await tool.execute({}, context)
        
        assert result["status"] == "error"
        assert "Missing required parameters" in result["error"]


class TestGetDeviceHistoryTool:
    """Tests for GetDeviceHistoryTool."""
    
    @pytest.fixture
    def mock_gateways(self):
        from core.ai.domain import DeviceDTO
        device_gateway = MagicMock()
        device_gateway.get_by_id = AsyncMock(return_value=DeviceDTO(
            id="dev-001",
            serial_number="SN-12345",
            name="Test Device",
            device_type="Test",
            status="active",
            manufacturer="TestCorp",
            model="Model1",
            is_critical=True,
        ))
        device_gateway.get_history = AsyncMock(return_value={
            "device_id": "dev-001",
            "maintenance_records": [],
        })
        
        incident_gateway = MagicMock()
        incident_gateway.get_by_device = AsyncMock(return_value=[])
        
        return device_gateway, incident_gateway
    
    @pytest.fixture
    def tool(self, mock_gateways):
        return GetDeviceHistoryTool(mock_gateways[0], mock_gateways[1])
    
    @pytest.fixture
    def context(self):
        return ToolExecutionContext(tenant_id="tenant-001")
    
    def test_config_has_correct_name(self, tool):
        """Test that tool config has correct name."""
        assert tool.config.name == "get_device_history"
    
    @pytest.mark.asyncio
    async def test_execute_returns_not_found_for_unknown_device(self, tool, context):
        """Test that execute returns not_found for unknown device."""
        # Override the mock to return None
        tool._gateway.get_by_id = AsyncMock(return_value=None)
        
        result = await tool.execute(
            {"device_id": "unknown"},
            context,
        )
        
        assert result["status"] == "not_found"


class TestSearchKnowledgeTool:
    """Tests for SearchKnowledgeTool."""
    
    @pytest.fixture
    def mock_gateway(self):
        from core.ai.domain import KnowledgeArticleDTO
        gateway = MagicMock()
        gateway.search = AsyncMock(return_value=[
            KnowledgeArticleDTO(
                id="kb-001",
                title="Test Article",
                content="Test content",
                category="manual",
                tags=["test"],
            ),
        ])
        return gateway
    
    @pytest.fixture
    def tool(self, mock_gateway):
        return SearchKnowledgeTool(mock_gateway)
    
    @pytest.fixture
    def context(self):
        return ToolExecutionContext(tenant_id="tenant-001")
    
    def test_config_has_correct_name(self, tool):
        """Test that tool config has correct name."""
        assert tool.config.name == "search_knowledge"
    
    @pytest.mark.asyncio
    async def test_execute_returns_success(self, tool, context):
        """Test that execute returns success."""
        result = await tool.execute(
            {"query": "test"},
            context,
        )
        
        assert result["status"] == "success"
        assert "data" in result


class TestGetCapacityInfoTool:
    """Tests for GetCapacityInfoTool."""
    
    @pytest.fixture
    def mock_gateway(self):
        from core.ai.domain import CapacityDTO
        gateway = MagicMock()
        gateway.get_capacity = AsyncMock(return_value=CapacityDTO(
            campus_id="campus-001",
            campus_name="Test Hospital",
            total_beds=100,
            occupied_beds=80,
            available_beds=20,
            occupancy_rate=0.8,
            departments=[],
        ))
        return gateway
    
    @pytest.fixture
    def tool(self, mock_gateway):
        return GetCapacityInfoTool(mock_gateway)
    
    @pytest.fixture
    def context(self):
        return ToolExecutionContext(tenant_id="tenant-001")
    
    def test_config_has_correct_name(self, tool):
        """Test that tool config has correct name."""
        assert tool.config.name == "get_capacity_info"
    
    @pytest.mark.asyncio
    async def test_execute_returns_capacity_data(self, tool, context):
        """Test that execute returns capacity data."""
        result = await tool.execute({}, context)
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["total_beds"] == 100
        assert result["data"]["available_beds"] == 20
