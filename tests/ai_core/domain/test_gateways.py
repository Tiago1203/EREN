"""
Tests for Domain Gateways.

Tests the domain gateways to ensure they work correctly
and provide proper DTOs to AI Core.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestDeviceGateway:
    """Tests for DeviceGateway."""
    
    @pytest.fixture
    def gateway(self):
        from core.ai.domain import DeviceGateway
        return DeviceGateway()
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_dto(self, gateway):
        """Test that get_by_id returns DeviceDTO."""
        result = await gateway.get_by_id("dev-001", "tenant-001")
        
        assert result is not None
        assert result.id == "dev-001"
        assert result.name == "Ventilator Model A"
        assert result.device_type == "Ventilator"
        assert result.status == "active"
        assert result.is_critical is True
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, gateway):
        """Test that get_by_id returns None for unknown device."""
        result = await gateway.get_by_id("unknown-device", "tenant-001")
        # Mock returns None for unknown
        assert result is None
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self, gateway):
        """Test that search returns list of DeviceDTO."""
        results = await gateway.search("ventilator", "tenant-001")
        
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'name')
    
    @pytest.mark.asyncio
    async def test_get_critical_devices(self, gateway):
        """Test that get_critical_devices returns only critical devices."""
        results = await gateway.get_critical_devices("tenant-001")
        
        assert isinstance(results, list)
        for result in results:
            assert result.is_critical is True
    
    @pytest.mark.asyncio
    async def test_get_needing_maintenance(self, gateway):
        """Test that get_needing_maintenance returns devices needing maintenance."""
        results = await gateway.get_needing_maintenance("tenant-001")
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_history(self, gateway):
        """Test that get_history returns maintenance/incident history."""
        result = await gateway.get_history("dev-001", "tenant-001")
        
        assert isinstance(result, dict)
        assert "maintenance_records" in result or "device_id" in result
    
    @pytest.mark.asyncio
    async def test_get_location(self, gateway):
        """Test that get_location returns location details."""
        result = await gateway.get_location("dev-001", "tenant-001")
        
        assert isinstance(result, dict)
        assert "building" in result
        assert "floor" in result


class TestIncidentGateway:
    """Tests for IncidentGateway."""
    
    @pytest.fixture
    def gateway(self):
        from core.ai.domain import IncidentGateway
        return IncidentGateway()
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_dto(self, gateway):
        """Test that get_by_id returns IncidentDTO."""
        result = await gateway.get_by_id("inc-001", "tenant-001")
        
        assert result is not None
        assert result.id == "inc-001"
        assert result.title == "Ventilator Alarm Malfunction"
        assert result.severity == "high"
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self, gateway):
        """Test that search returns list of IncidentDTO."""
        results = await gateway.search("alarm", "tenant-001")
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_open_incidents(self, gateway):
        """Test that get_open_incidents returns open incidents."""
        results = await gateway.get_open_incidents("tenant-001")
        
        assert isinstance(results, list)
        for result in results:
            assert result.status == "open"
    
    @pytest.mark.asyncio
    async def test_analyze(self, gateway):
        """Test that analyze returns root cause analysis."""
        result = await gateway.analyze("inc-001", "tenant-001")
        
        assert isinstance(result, dict)
        assert "root_cause" in result or "recommended_actions" in result


class TestKnowledgeGateway:
    """Tests for KnowledgeGateway."""
    
    @pytest.fixture
    def gateway(self):
        from core.ai.domain import KnowledgeGateway
        return KnowledgeGateway()
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_dto(self, gateway):
        """Test that get_by_id returns KnowledgeArticleDTO."""
        result = await gateway.get_by_id("kb-001", "tenant-001")
        
        assert result is not None
        assert result.id == "kb-001"
        assert "Troubleshooting" in result.title
    
    @pytest.mark.asyncio
    async def test_search_returns_list(self, gateway):
        """Test that search returns list of KnowledgeArticleDTO."""
        results = await gateway.search("ventilator", "tenant-001")
        
        assert isinstance(results, list)
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'title')


class TestHospitalGateway:
    """Tests for HospitalGateway."""
    
    @pytest.fixture
    def gateway(self):
        from core.ai.domain import HospitalGateway
        return HospitalGateway()
    
    @pytest.mark.asyncio
    async def test_get_by_id_returns_dto(self, gateway):
        """Test that get_by_id returns HospitalDTO."""
        result = await gateway.get_by_id("campus-001", "tenant-001")
        
        assert result is not None
        assert result.id == "campus-001"
        assert result.name == "Main Hospital"
    
    @pytest.mark.asyncio
    async def test_get_capacity(self, gateway):
        """Test that get_capacity returns CapacityDTO."""
        result = await gateway.get_capacity("campus-001", "tenant-001")
        
        assert result.total_beds > 0
        assert result.available_beds >= 0
        assert result.occupancy_rate > 0


class TestRecommendationGateway:
    """Tests for RecommendationGateway."""
    
    @pytest.fixture
    def gateway(self):
        from core.ai.domain import RecommendationGateway
        return RecommendationGateway()
    
    @pytest.mark.asyncio
    async def test_get_pending(self, gateway):
        """Test that get_pending returns pending recommendations."""
        results = await gateway.get_pending("tenant-001")
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_by_confidence(self, gateway):
        """Test that get_by_confidence returns high confidence recommendations."""
        results = await gateway.get_by_confidence("tenant-001", min_confidence=0.7)
        
        assert isinstance(results, list)
        for result in results:
            assert result.confidence >= 0.7
    
    @pytest.mark.asyncio
    async def test_generate(self, gateway):
        """Test that generate creates new recommendations."""
        results = await gateway.generate(
            device_id="dev-001",
            incident_id=None,
            tenant_id="tenant-001",
        )
        
        assert isinstance(results, list)
        assert len(results) > 0
