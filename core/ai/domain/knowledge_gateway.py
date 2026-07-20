"""
Knowledge Gateway.

Gateway implementation for Knowledge domain.
Provides AI Core with access to knowledge articles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .contracts import KnowledgeArticleDTO, IKnowledgeGateway
from .exceptions import KnowledgeNotFoundError

if TYPE_CHECKING:
    from core.knowledge.domain.repositories import KnowledgeRepository


class KnowledgeGateway(IKnowledgeGateway):
    """
    Gateway for Knowledge domain.
    
    AI Core uses this gateway to search and retrieve knowledge articles.
    """
    
    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
    ):
        self._repository = repository
    
    @property
    def name(self) -> str:
        return "knowledge"
    
    async def get_by_id(
        self,
        article_id: str,
        tenant_id: str,
    ) -> KnowledgeArticleDTO | None:
        """Get article by ID."""
        if self._repository is None:
            return self._mock_get_by_id(article_id)
        
        from core.shared import KnowledgeId, TenantId
        result = await self._repository.get_by_id(
            KnowledgeId(article_id),
        )
        
        if result.is_ok() and result.value:
            return self._entity_to_dto(result.value)
        return None
    
    async def search(
        self,
        query: str,
        tenant_id: str,
        filters: dict | None = None,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search knowledge articles."""
        return self._mock_search(query, limit)
    
    async def search_manuals(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search user manuals."""
        results = await self.search(query, tenant_id, {"category": "manual"}, limit)
        return [r for r in results if "manual" in r.category.lower()]
    
    async def search_procedures(
        self,
        query: str,
        tenant_id: str,
        limit: int = 10,
    ) -> list[KnowledgeArticleDTO]:
        """Search procedures."""
        results = await self.search(query, tenant_id, {"category": "procedure"}, limit)
        return [r for r in results if "procedure" in r.category.lower()]
    
    async def get_by_device(
        self,
        device_id: str,
        tenant_id: str,
    ) -> list[KnowledgeArticleDTO]:
        """Get articles related to a device."""
        if self._repository is None:
            return self._mock_get_by_device(device_id)
        
        from core.shared import TenantId
        result = await self._repository.get_by_device(
            TenantId(tenant_id),
            device_id,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(a) for a in result.value]
        return []
    
    async def get_related(
        self,
        article_id: str,
        tenant_id: str,
        limit: int = 5,
    ) -> list[KnowledgeArticleDTO]:
        """Get related articles."""
        if self._repository is None:
            return self._mock_get_related(article_id, limit)
        
        from core.shared import TenantId
        result = await self._repository.get_related_articles(
            article_id,
            TenantId(tenant_id),
            limit,
        )
        
        if result.is_ok():
            return [self._entity_to_dto(a) for a in result.value]
        return []
    
    def _entity_to_dto(self, entity: Any) -> KnowledgeArticleDTO:
        """Convert KnowledgeArticle entity to KnowledgeArticleDTO."""
        return KnowledgeArticleDTO(
            id=str(entity.id),
            title=entity.title,
            content=entity.content,
            category=str(entity.category),
            tags=list(entity.tags) if entity.tags else [],
            views=getattr(entity, 'views', 0),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    # =============================================================================
    # Mock implementations
    # =============================================================================
    
    def _mock_get_by_id(self, article_id: str) -> KnowledgeArticleDTO | None:
        """Mock implementation."""
        mock_articles = {
            "kb-001": KnowledgeArticleDTO(
                id="kb-001",
                title="Ventilator Troubleshooting Guide",
                content="Step-by-step guide for troubleshooting ventilators...",
                category="manual",
                tags=["ventilator", "troubleshooting", "critical"],
            ),
            "kb-002": KnowledgeArticleDTO(
                id="kb-002",
                title="Preventive Maintenance Schedule",
                content="Recommended maintenance schedule for medical equipment...",
                category="procedure",
                tags=["maintenance", "schedule", "preventive"],
            ),
        }
        return mock_articles.get(article_id)
    
    def _mock_search(self, query: str, limit: int) -> list[KnowledgeArticleDTO]:
        """Mock search."""
        all_articles = [
            KnowledgeArticleDTO(
                id="kb-001",
                title="Ventilator Troubleshooting Guide",
                content="Step-by-step guide for troubleshooting ventilators...",
                category="manual",
                tags=["ventilator", "troubleshooting", "critical"],
            ),
            KnowledgeArticleDTO(
                id="kb-002",
                title="Preventive Maintenance Schedule",
                content="Recommended maintenance schedule for medical equipment...",
                category="procedure",
                tags=["maintenance", "schedule", "preventive"],
            ),
            KnowledgeArticleDTO(
                id="kb-003",
                title="Infusion Pump Error Codes",
                content="List of error codes and solutions for infusion pumps...",
                category="manual",
                tags=["infusion", "pump", "error-codes"],
            ),
        ]
        
        query_lower = query.lower()
        results = [
            a for a in all_articles
            if query_lower in a.title.lower()
            or query_lower in a.content.lower()
            or any(query_lower in tag for tag in a.tags)
        ]
        return results[:limit]
    
    def _mock_get_by_device(self, device_id: str) -> list[KnowledgeArticleDTO]:
        """Mock get by device."""
        return self._mock_search("", 10)
    
    def _mock_get_related(self, article_id: str, limit: int) -> list[KnowledgeArticleDTO]:
        """Mock get related."""
        return self._mock_search("", limit)
