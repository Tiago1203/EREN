"""
Knowledge Context Provider.

Provides knowledge base context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.PHASE_2.ai.domain import KnowledgeGateway


class KnowledgeContextProvider(BaseContextProvider):
    """
    Provides knowledge base context for the AI.
    
    Searches and retrieves relevant knowledge articles,
    manuals, and procedures.
    """
    
    def __init__(
        self,
        knowledge_gateway: KnowledgeGateway | None = None,
    ):
        self._knowledge = knowledge_gateway
    
    @property
    def name(self) -> str:
        return "knowledge"
    
    @property
    def priority(self) -> int:
        return 45  # Medium priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get knowledge context."""
        items = []
        
        if not query.query:
            return items
        
        # Search knowledge base
        articles = await self._search_safe(query.query, query.tenant_id)
        
        for article in articles[:3]:
            items.append(self._article_to_context(article))
        
        return items
    
    async def _search_safe(
        self,
        search_query: str,
        tenant_id: str,
    ) -> list[dict]:
        """Safely search knowledge."""
        if self._knowledge is None:
            return self._mock_search(search_query)
        try:
            results = await self._knowledge.search(search_query, tenant_id, limit=3)
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "category": r.category,
                    "tags": r.tags,
                }
                for r in results
            ]
        except Exception:
            return []
    
    def _article_to_context(self, article: dict) -> ContextItem:
        """Convert article to ContextItem."""
        tags_str = ", ".join(article.get("tags", [])[:5])
        return self._create_item(
            content=f"Knowledge Article: {article['title']}\n"
                   f"Category: {article['category']}\n"
                   f"Tags: {tags_str}\n"
                   f"Content: {article['content'][:500]}",
            relevance_score=0.8,
            metadata={"type": "knowledge", "article_id": article["id"]},
        )
    
    def _mock_search(self, query: str) -> list[dict]:
        """Mock search for testing."""
        mock_articles = [
            {
                "id": "kb-001",
                "title": "Ventilator Troubleshooting Guide",
                "content": "Step-by-step guide for troubleshooting ventilators. Check alarms first, then verify connections...",
                "category": "manual",
                "tags": ["ventilator", "troubleshooting"],
            },
            {
                "id": "kb-002",
                "title": "Preventive Maintenance Schedule",
                "content": "Recommended maintenance schedule: Daily checks, Weekly calibration, Monthly inspection...",
                "category": "procedure",
                "tags": ["maintenance", "schedule"],
            },
        ]
        
        query_lower = query.lower()
        return [
            a for a in mock_articles
            if query_lower in a["title"].lower() or any(query_lower in t for t in a["tags"])
        ]
