"""
Domain Tools Module.

This module provides domain-specific tools for the AI.
Each tool wraps a domain gateway and provides a standardized interface.

Auto-registration:
    Use register_domain_tools(orchestrator) to register all tools.
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from core.ai.tools import ToolOrchestrator

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext
from .device_tools import (
    SearchDeviceTool,
    GetDeviceHistoryTool,
    GetDeviceLocationTool,
    GetDeviceMaintenanceTool,
)
from .incident_tools import (
    SearchIncidentTool,
    GetIncidentHistoryTool,
    AnalyzeIncidentTool,
)
from .knowledge_tools import (
    SearchKnowledgeTool,
    SearchManualTool,
    SearchProcedureTool,
)
from .recommendation_tools import (
    GetRecommendationHistoryTool,
    GenerateRecommendationTool,
    GetPendingRecommendationsTool,
)
from .hospital_tools import (
    GetCapacityInfoTool,
    GetDepartmentInfoTool,
    GetAvailableBedsTool,
)

__all__ = [
    # Base
    "BaseDomainTool",
    "DomainToolConfig",
    "ToolExecutionContext",
    # Device Tools
    "SearchDeviceTool",
    "GetDeviceHistoryTool",
    "GetDeviceLocationTool",
    "GetDeviceMaintenanceTool",
    # Incident Tools
    "SearchIncidentTool",
    "GetIncidentHistoryTool",
    "AnalyzeIncidentTool",
    # Knowledge Tools
    "SearchKnowledgeTool",
    "SearchManualTool",
    "SearchProcedureTool",
    # Recommendation Tools
    "GetRecommendationHistoryTool",
    "GenerateRecommendationTool",
    "GetPendingRecommendationsTool",
    # Hospital Tools
    "GetCapacityInfoTool",
    "GetDepartmentInfoTool",
    "GetAvailableBedsTool",
    # Registration
    "register_domain_tools",
]


def register_domain_tools(
    orchestrator: "ToolOrchestrator",
    gateways: dict | None = None,
) -> None:
    """
    Register all domain tools with the orchestrator.
    
    Args:
        orchestrator: The ToolOrchestrator to register tools with
        gateways: Optional dict of gateway instances
        
    Example:
        from core.ai.tools import ToolOrchestrator
        from core.ai.domain import DeviceGateway, IncidentGateway
        from core.ai.tools.domain import register_domain_tools
        
        orchestrator = ToolOrchestrator()
        gateways = {
            "device": DeviceGateway(),
            "incident": IncidentGateway(),
        }
        register_domain_tools(orchestrator, gateways)
    """
    from core.ai.domain import (
        DeviceGateway,
        IncidentGateway,
        KnowledgeGateway,
        RecommendationGateway,
        HospitalGateway,
    )
    
    # Create gateways if not provided
    if gateways is None:
        gateways = {
            "device": DeviceGateway(),
            "incident": IncidentGateway(),
            "knowledge": KnowledgeGateway(),
            "recommendation": RecommendationGateway(),
            "hospital": HospitalGateway(),
        }
    
    device_gateway = gateways.get("device", DeviceGateway())
    incident_gateway = gateways.get("incident", IncidentGateway())
    knowledge_gateway = gateways.get("knowledge", KnowledgeGateway())
    recommendation_gateway = gateways.get("recommendation", RecommendationGateway())
    hospital_gateway = gateways.get("hospital", HospitalGateway())
    
    # Register Device tools
    _register_tool(orchestrator, SearchDeviceTool(device_gateway))
    _register_tool(orchestrator, GetDeviceHistoryTool(device_gateway, incident_gateway))
    _register_tool(orchestrator, GetDeviceLocationTool(device_gateway))
    _register_tool(orchestrator, GetDeviceMaintenanceTool(device_gateway))
    
    # Register Incident tools
    _register_tool(orchestrator, SearchIncidentTool(incident_gateway))
    _register_tool(orchestrator, GetIncidentHistoryTool(incident_gateway))
    _register_tool(orchestrator, AnalyzeIncidentTool(incident_gateway, device_gateway))
    
    # Register Knowledge tools
    _register_tool(orchestrator, SearchKnowledgeTool(knowledge_gateway))
    _register_tool(orchestrator, SearchManualTool(knowledge_gateway))
    _register_tool(orchestrator, SearchProcedureTool(knowledge_gateway))
    
    # Register Recommendation tools
    _register_tool(orchestrator, GetRecommendationHistoryTool(recommendation_gateway))
    _register_tool(orchestrator, GenerateRecommendationTool(recommendation_gateway))
    _register_tool(orchestrator, GetPendingRecommendationsTool(recommendation_gateway))
    
    # Register Hospital tools
    _register_tool(orchestrator, GetCapacityInfoTool(hospital_gateway))
    _register_tool(orchestrator, GetDepartmentInfoTool(hospital_gateway))
    _register_tool(orchestrator, GetAvailableBedsTool(hospital_gateway))


def _register_tool(
    orchestrator: "ToolOrchestrator",
    tool: BaseDomainTool,
) -> None:
    """
    Register a single tool with the orchestrator.
    
    Args:
        orchestrator: The orchestrator to register with
        tool: The tool to register
    """
    try:
        # Create tool definition from config
        from core.ai.tools import ToolDefinition, ToolCategory
        
        definition = ToolDefinition(
            name=tool.config.name,
            description=tool.config.description,
            category=ToolCategory.DOMAIN,
            parameters_schema=tool.config.parameters_schema,
            requires_tenant=tool.config.requires_tenant,
        )
        
        # Register the tool
        orchestrator.register(definition, tool)
        
    except Exception as e:
        # Log error but don't fail registration
        import logging
        logging.warning(f"Failed to register tool {tool.config.name}: {e}")


def get_all_tool_configs() -> list[DomainToolConfig]:
    """
    Get all tool configurations.
    
    Returns:
        List of all DomainToolConfig for documentation purposes
    """
    return [
        # Device
        SearchDeviceTool(DeviceGateway()).config,
        GetDeviceHistoryTool(DeviceGateway(), IncidentGateway()).config,
        GetDeviceLocationTool(DeviceGateway()).config,
        GetDeviceMaintenanceTool(DeviceGateway()).config,
        # Incident
        SearchIncidentTool(IncidentGateway()).config,
        GetIncidentHistoryTool(IncidentGateway()).config,
        AnalyzeIncidentTool(IncidentGateway(), DeviceGateway()).config,
        # Knowledge
        SearchKnowledgeTool(KnowledgeGateway()).config,
        SearchManualTool(KnowledgeGateway()).config,
        SearchProcedureTool(KnowledgeGateway()).config,
        # Recommendation
        GetRecommendationHistoryTool(RecommendationGateway()).config,
        GenerateRecommendationTool(RecommendationGateway()).config,
        GetPendingRecommendationsTool(RecommendationGateway()).config,
        # Hospital
        GetCapacityInfoTool(HospitalGateway()).config,
        GetDepartmentInfoTool(HospitalGateway()).config,
        GetAvailableBedsTool(HospitalGateway()).config,
    ]
