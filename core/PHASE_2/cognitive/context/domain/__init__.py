"""Context domain - builds context for AI reasoning."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContextSource(str, Enum):
    """Source of context data."""
    DEVICE = "device"
    INCIDENT = "incident"
    KNOWLEDGE = "knowledge"
    CAPACITY = "capacity"
    STAFFING = "staffing"
    ORGANIZATION = "organization"
    RECOMMENDATION = "recommendation"
    USER = "user"
    SESSION = "session"


@dataclass
class ContextItem:
    """A single context item."""
    source: ContextSource
    entity_type: str
    entity_id: str
    data: dict
    relevance_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Context:
    """
    Complete context for AI reasoning.
    
    Aggregates information from all relevant sources to provide
    a comprehensive view for AI decision-making.
    """
    items: list[ContextItem] = field(default_factory=list)
    query: str = ""
    domain: str = "biomedical"
    user_id: str = ""
    tenant_id: str = ""
    conversation_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def add_item(self, item: ContextItem) -> None:
        """Add a context item."""
        self.items.append(item)
    
    def get_by_source(self, source: ContextSource) -> list[ContextItem]:
        """Get items by source."""
        return [item for item in self.items if item.source == source]
    
    def get_by_entity_type(self, entity_type: str) -> list[ContextItem]:
        """Get items by entity type."""
        return [item for item in self.items if item.entity_type == entity_type]
    
    def to_prompt_context(self) -> str:
        """Convert context to prompt-friendly format."""
        lines = []
        lines.append("## Context Information")
        lines.append(f"Domain: {self.domain}")
        lines.append("")
        
        # Group by source
        for source in ContextSource:
            source_items = self.get_by_source(source)
            if source_items:
                lines.append(f"### {source.value.title()} Information")
                for item in source_items:
                    lines.append(f"- {item.entity_type} ({item.entity_id}): {self._format_data(item.data)}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_data(self, data: dict) -> str:
        """Format data for prompt."""
        if not data:
            return "No data available"
        
        # Take most relevant fields
        relevant_keys = ["name", "status", "description", "type", "model", "serial_number"]
        parts = []
        for key in relevant_keys:
            if key in data:
                parts.append(f"{key}: {data[key]}")
        
        return "; ".join(parts) if parts else str(data)[:200]


@dataclass
class ContextBuilderConfig:
    """Configuration for context building."""
    max_items_per_source: int = 10
    min_relevance_score: float = 0.3
    include_expired: bool = False
    cache_ttl_seconds: int = 300
