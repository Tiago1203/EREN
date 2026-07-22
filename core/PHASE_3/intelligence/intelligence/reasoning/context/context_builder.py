"""
Context Builder Module

Builds the reasoning context from memory, knowledge, domain, and conversation.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MemoryContext:
    """Context from historical memory."""
    recent_incidents: list[dict] = field(default_factory=list)
    equipment_history: list[dict] = field(default_factory=list)
    similar_cases: list[dict] = field(default_factory=list)
    learned_patterns: list[str] = field(default_factory=list)


@dataclass
class KnowledgeContext:
    """Context from knowledge graph and ontology."""
    relevant_concepts: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class DomainContext:
    """Context from domain knowledge."""
    equipment_type: Optional[str] = None
    equipment_id: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    risk_class: Optional[str] = None
    location: Optional[str] = None


@dataclass
class ConversationContext:
    """Context from current conversation."""
    user_query: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    constraints: list[str] = field(default_factory=list)


@dataclass
class ReasoningContext:
    """Complete reasoning context."""
    memory: MemoryContext
    knowledge: KnowledgeContext
    domain: DomainContext
    conversation: ConversationContext
    created_at: datetime = field(default_factory=datetime.now)


class ContextBuilder:
    """Builds reasoning context from various sources."""
    
    async def build(
        self,
        memory: MemoryContext,
        knowledge: KnowledgeContext,
        domain: DomainContext,
        conversation: ConversationContext,
    ) -> ReasoningContext:
        """Build complete reasoning context."""
        return ReasoningContext(
            memory=memory,
            knowledge=knowledge,
            domain=domain,
            conversation=conversation,
        )
    
    async def enrich_with_memory(
        self,
        context: ReasoningContext,
    ) -> ReasoningContext:
        """Enrich context with historical memory."""
        if context.domain.equipment_type:
            context.memory.similar_cases = [
                {"id": "case_1", "description": "Similar incident"},
            ]
        return context
    
    async def enrich_with_knowledge(
        self,
        context: ReasoningContext,
    ) -> ReasoningContext:
        """Enrich context with knowledge graph data."""
        context.knowledge.relevant_concepts = ["concept_1", "concept_2"]
        return context


__all__ = [
    "MemoryContext",
    "KnowledgeContext",
    "DomainContext",
    "ConversationContext",
    "ReasoningContext",
    "ContextBuilder",
]
