"""Context Builder Service - builds comprehensive context for AI."""
from typing import Protocol

from core.cognitive.context.domain import (
    Context,
    ContextItem,
    ContextSource,
    ContextBuilderConfig,
)


class EntityRetriever(Protocol):
    """Protocol for retrieving entities."""
    
    async def get_device(self, device_id: str, tenant_id: str) -> dict | None:
        """Get device by ID."""
        ...
    
    async def get_incident(self, incident_id: str, tenant_id: str) -> dict | None:
        """Get incident by ID."""
        ...
    
    async def get_knowledge_articles(
        self,
        query: str,
        tenant_id: str,
        limit: int = 5,
    ) -> list[dict]:
        """Search knowledge articles."""
        ...
    
    async def get_capacity(
        self,
        hospital_id: str,
        department_id: str | None,
        tenant_id: str,
    ) -> dict | None:
        """Get capacity information."""
        ...
    
    async def get_staff(
        self,
        staff_id: str,
        tenant_id: str,
    ) -> dict | None:
        """Get staff information."""
        ...
    
    async def get_organization(
        self,
        organization_id: str,
        tenant_id: str,
    ) -> dict | None:
        """Get organization information."""
        ...
    
    async def get_recommendations(
        self,
        entity_id: str,
        entity_type: str,
        tenant_id: str,
    ) -> list[dict]:
        """Get recommendations for entity."""
        ...


class ContextBuilder:
    """
    Builds comprehensive context for AI reasoning.
    
    Aggregates information from EPIC 2 (Device, Incident, Knowledge, Recommendation)
    and EPIC 3 (Capacity, Staffing, Organization) domains.
    """
    
    def __init__(
        self,
        entity_retriever: EntityRetriever,
        config: ContextBuilderConfig | None = None,
    ):
        self.entity_retriever = entity_retriever
        self.config = config or ContextBuilderConfig()
    
    async def build(
        self,
        query: str,
        user_id: str,
        tenant_id: str,
        domain: str = "biomedical",
        conversation_id: str = "",
        entity_ids: dict[str, str] | None = None,
    ) -> Context:
        """
        Build comprehensive context from all sources.
        
        Args:
            query: User query
            user_id: User ID
            tenant_id: Tenant ID
            domain: Primary domain (biomedical, clinical, hospital)
            conversation_id: Conversation ID for session context
            entity_ids: Optional dict of entity types to IDs
                e.g., {"device_id": "123", "incident_id": "456"}
        
        Returns:
            Context with all relevant information
        """
        context = Context(
            query=query,
            user_id=user_id,
            tenant_id=tenant_id,
            domain=domain,
            conversation_id=conversation_id,
        )
        
        # Add session context if available
        if conversation_id:
            await self._add_session_context(context)
        
        # If specific entities provided, add them
        if entity_ids:
            await self._add_specific_entities(context, entity_ids, tenant_id)
        
        # Search for relevant knowledge
        await self._add_knowledge_context(context, query, tenant_id)
        
        # If biomedical domain, add device/incident context
        if domain == "biomedical":
            await self._add_biomedical_context(context, query, tenant_id)
        
        # If hospital domain, add hospital context
        elif domain == "hospital":
            await self._add_hospital_context(context, tenant_id)
        
        # If clinical domain, add clinical context
        elif domain == "clinical":
            await self._add_clinical_context(context, query, tenant_id)
        
        # Filter by relevance
        self._filter_by_relevance(context)
        
        return context
    
    async def _add_session_context(self, context: Context) -> None:
        """Add session/conversation context."""
        # In production, would retrieve from memory
        context.add_item(ContextItem(
            source=ContextSource.SESSION,
            entity_type="conversation",
            entity_id=context.conversation_id,
            data={"conversation_id": context.conversation_id},
            relevance_score=0.9,
        ))
    
    async def _add_specific_entities(
        self,
        context: Context,
        entity_ids: dict[str, str],
        tenant_id: str,
    ) -> None:
        """Add specific entities mentioned in query."""
        if device_id := entity_ids.get("device_id"):
            device = await self.entity_retriever.get_device(device_id, tenant_id)
            if device:
                context.add_item(ContextItem(
                    source=ContextSource.DEVICE,
                    entity_type="device",
                    entity_id=device_id,
                    data=device,
                    relevance_score=1.0,
                ))
        
        if incident_id := entity_ids.get("incident_id"):
            incident = await self.entity_retriever.get_incident(incident_id, tenant_id)
            if incident:
                context.add_item(ContextItem(
                    source=ContextSource.INCIDENT,
                    entity_type="incident",
                    entity_id=incident_id,
                    data=incident,
                    relevance_score=1.0,
                ))
    
    async def _add_knowledge_context(
        self,
        context: Context,
        query: str,
        tenant_id: str,
    ) -> None:
        """Add relevant knowledge articles."""
        articles = await self.entity_retriever.get_knowledge_articles(
            query=query,
            tenant_id=tenant_id,
            limit=self.config.max_items_per_source,
        )
        
        for article in articles:
            context.add_item(ContextItem(
                source=ContextSource.KNOWLEDGE,
                entity_type="knowledge_article",
                entity_id=article.get("id", ""),
                data=article,
                relevance_score=article.get("relevance", 0.8),
            ))
    
    async def _add_biomedical_context(
        self,
        context: Context,
        query: str,
        tenant_id: str,
    ) -> None:
        """Add biomedical domain context."""
        # Search for relevant devices
        # In production, would extract device mentions from query
        pass
    
    async def _add_hospital_context(
        self,
        context: Context,
        tenant_id: str,
    ) -> None:
        """Add hospital management context."""
        capacity = await self.entity_retriever.get_capacity(
            hospital_id="current",
            department_id=None,
            tenant_id=tenant_id,
        )
        if capacity:
            context.add_item(ContextItem(
                source=ContextSource.CAPACITY,
                entity_type="capacity",
                entity_id="current",
                data=capacity,
                relevance_score=0.8,
            ))
    
    async def _add_clinical_context(
        self,
        context: Context,
        query: str,
        tenant_id: str,
    ) -> None:
        """Add clinical domain context."""
        # Search for relevant recommendations
        pass
    
    def _filter_by_relevance(self, context: Context) -> None:
        """Filter context items by relevance score."""
        min_score = self.config.min_relevance_score
        context.items = [
            item for item in context.items
            if item.relevance_score >= min_score
        ]


def create_context_builder(
    entity_retriever: EntityRetriever,
) -> ContextBuilder:
    """Create a context builder."""
    return ContextBuilder(entity_retriever=entity_retriever)
