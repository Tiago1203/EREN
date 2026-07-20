"""Memory domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class MemoryType(str, Enum):
    """Memory type enumeration."""
    WORKING = "working"
    SESSION = "session"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class RetentionPolicy(str, Enum):
    """Data retention policy."""
    EPHEMERAL = "ephemeral"  # Short-term, auto-delete
    SESSION = "session"  # Duration of session
    SHORT_TERM = "short_term"  # Days to weeks
    LONG_TERM = "long_term"  # Months to years
    SENSITIVE = "sensitive"  # Special handling required


@dataclass
class MemoryId:
    """Memory identifier."""
    value: UUID
    
    @classmethod
    def generate(cls) -> "MemoryId":
        return cls(uuid4())


@dataclass
class MemoryBlock:
    """Memory block entity."""
    id: MemoryId
    memory_type: MemoryType
    key: str
    value: any  # Any type
    metadata: dict = field(default_factory=dict)
    
    # Provenance
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    source: str = "memory"
    
    # Utility
    importance: float = 0.5  # 0.0-1.0
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    
    # Privacy
    is_sensitive: bool = False
    retention_policy: RetentionPolicy = RetentionPolicy.SHORT_TERM
