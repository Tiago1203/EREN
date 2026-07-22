"""
Knowledge Domain Tools.

Tools for accessing knowledge base data from the domain.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDomainTool, DomainToolConfig, ToolExecutionContext

if TYPE_CHECKING:
    from core.PHASE_2.ai.domain import KnowledgeGateway


class SearchKnowledgeTool(BaseDomainTool):
    """
    Tool for searching knowledge articles.
    
    Usage:
        search_knowledge(query="ventilator maintenance")
    """
    
    config = DomainToolConfig(
        name="search_knowledge",
        description="Search the knowledge base for articles, manuals, and procedures.",
        category="domain.knowledge",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "category": {
                    "type": "string",
                    "enum": ["manual", "procedure", "guide", "troubleshooting"],
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    )
    
    def __init__(self, knowledge_gateway: KnowledgeGateway):
        self._gateway = knowledge_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Search knowledge."""
        try:
            self._validate_parameters(parameters, ["query"])
            
            filters = {}
            if category := parameters.get("category"):
                filters["category"] = category
            
            results = await self._gateway.search(
                query=parameters["query"],
                tenant_id=context.tenant_id,
                filters=filters if filters else None,
                limit=parameters.get("limit", 10),
            )
            
            return self._format_success([
                {
                    "id": a.id,
                    "title": a.title,
                    "category": a.category,
                    "tags": a.tags,
                    "content_preview": a.content[:200] + "..." if len(a.content) > 200 else a.content,
                }
                for a in results
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class SearchManualTool(BaseDomainTool):
    """
    Tool for searching user manuals.
    
    Usage:
        search_manual(query="ventilator")
    """
    
    config = DomainToolConfig(
        name="search_manual",
        description="Search specifically for user manuals in the knowledge base.",
        category="domain.knowledge",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    )
    
    def __init__(self, knowledge_gateway: KnowledgeGateway):
        self._gateway = knowledge_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Search manuals."""
        try:
            self._validate_parameters(parameters, ["query"])
            
            results = await self._gateway.search_manuals(
                query=parameters["query"],
                tenant_id=context.tenant_id,
                limit=parameters.get("limit", 10),
            )
            
            return self._format_success([
                {
                    "id": a.id,
                    "title": a.title,
                    "tags": a.tags,
                    "content_preview": a.content[:200] + "...",
                }
                for a in results
            ])
            
        except Exception as e:
            return self._format_error(str(e))


class SearchProcedureTool(BaseDomainTool):
    """
    Tool for searching procedures.
    
    Usage:
        search_procedure(query="maintenance")
    """
    
    config = DomainToolConfig(
        name="search_procedure",
        description="Search specifically for procedures in the knowledge base.",
        category="domain.knowledge",
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    )
    
    def __init__(self, knowledge_gateway: KnowledgeGateway):
        self._gateway = knowledge_gateway
    
    async def execute(
        self,
        parameters: dict,
        context: ToolExecutionContext,
    ) -> dict:
        """Search procedures."""
        try:
            self._validate_parameters(parameters, ["query"])
            
            results = await self._gateway.search_procedures(
                query=parameters["query"],
                tenant_id=context.tenant_id,
                limit=parameters.get("limit", 10),
            )
            
            return self._format_success([
                {
                    "id": a.id,
                    "title": a.title,
                    "tags": a.tags,
                    "content_preview": a.content[:200] + "...",
                }
                for a in results
            ])
            
        except Exception as e:
            return self._format_error(str(e))
