"""
PHASE 5 - EPIC 9: Memory Engines

Motores especializados para memoria:
- EpisodicMemory
- SharedMemory
- LongTermMemory
- ConversationMemory
- MemorySynchronizer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM EPIC 9 DOMAIN
# =============================================================================

from core.PHASE_5.epic9_memory.domain import (
    MemoryRecord,
    MemoryType,
    MemoryImportance,
    ConversationContext,
    Message,
    AgentExperience,
    ExperienceOutcome,
)


# =============================================================================
# RESULT CLASSES
# =============================================================================

@dataclass
class EpisodicResult:
    """Resultado de memoria episódica."""
    agent_id: str
    
    # Resultados
    records: list[MemoryRecord] = field(default_factory=list)
    records_count: int = 0
    
    # Metadatos
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SharedResult:
    """Resultado de memoria compartida."""
    shared_count: int = 0
    agents_count: int = 0
    
    # Metadatos
    shared_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class LongTermResult:
    """Resultado de memoria a largo plazo."""
    agent_id: str
    
    # Resultados
    experiences: list[AgentExperience] = field(default_factory=list)
    experiences_count: int = 0
    
    # Metadatos
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ConversationResult:
    """Resultado de memoria de conversación."""
    context_id: str
    
    # Resultados
    context: ConversationContext | None = None
    messages_count: int = 0
    
    # Metadatos
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SyncResult:
    """Resultado de sincronización."""
    synced_count: int = 0
    failed_count: int = 0
    
    # Metadatos
    synced_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# EPISODIC MEMORY
# =============================================================================

class EpisodicMemory:
    """
    Memoria episódica.
    
    Responsabilidades:
    - Almacenar eventos específicos
    - Recuperar eventos por contexto
    - Gestionar memoria de corto plazo
    """
    
    def __init__(self):
        self._records: dict[str, list[MemoryRecord]] = {}  # agent_id -> records
    
    async def store(
        self,
        agent_id: str,
        content: str,
        context: dict | None = None,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
    ) -> MemoryRecord:
        """Almacena un evento."""
        record = MemoryRecord(
            agent_id=agent_id,
            memory_type=memory_type,
            importance=importance,
            content=content,
            metadata=context or {},
        )
        
        if agent_id not in self._records:
            self._records[agent_id] = []
        self._records[agent_id].append(record)
        
        logger.info(f"Stored episodic memory for {agent_id}")
        return record
    
    async def retrieve(
        self,
        agent_id: str,
        session_id: str | None = None,
        limit: int = 10,
    ) -> EpisodicResult:
        """Recupera eventos."""
        records = self._records.get(agent_id, [])
        
        if session_id:
            records = [r for r in records if r.session_id == session_id]
        
        # Ordenar por fecha
        records.sort(key=lambda r: r.created_at, reverse=True)
        
        return EpisodicResult(
            agent_id=agent_id,
            records=records[:limit],
            records_count=len(records),
        )
    
    async def forget_old(self, agent_id: str, max_age_days: int = 7) -> int:
        """Olvida memorias antiguas."""
        if agent_id not in self._records:
            return 0
        
        cutoff = datetime.now(UTC) - timedelta(days=max_age_days)
        old_count = len(self._records[agent_id])
        
        self._records[agent_id] = [
            r for r in self._records[agent_id]
            if r.created_at > cutoff
        ]
        
        return old_count - len(self._records[agent_id])


# =============================================================================
# SHARED MEMORY
# =============================================================================

class SharedMemory:
    """
    Memoria compartida.
    
    Responsabilidades:
    - Compartir memorias entre agentes
    - Gestionar acceso compartido
    - Coordinar memorias colectivas
    """
    
    def __init__(self):
        self._shared_records: list[MemoryRecord] = []
    
    async def share(
        self,
        agent_id: str,
        record: MemoryRecord,
    ) -> SharedResult:
        """Comparte una memoria."""
        record.agent_id = agent_id
        self._shared_records.append(record)
        
        return SharedResult(
            shared_count=1,
            agents_count=len(set(r.agent_id for r in self._shared_records)),
        )
    
    async def get_shared(
        self,
        memory_type: MemoryType | None = None,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        """Obtiene memorias compartidas."""
        records = self._shared_records
        
        if memory_type:
            records = [r for r in records if r.memory_type == memory_type]
        
        return sorted(records, key=lambda r: r.created_at, reverse=True)[:limit]
    
    async def sync(
        self,
        agent_ids: list[str],
    ) -> list[MemoryRecord]:
        """Sincroniza memorias entre agentes."""
        return [
            r for r in self._shared_records
            if r.agent_id in agent_ids
        ]


# =============================================================================
# LONG-TERM MEMORY
# =============================================================================

class LongTermMemory:
    """
    Memoria a largo plazo.
    
    Responsabilidades:
    - Almacenar experiencias
    - Gestionar lecciones aprendidas
    - Validar experiencias
    """
    
    def __init__(self):
        self._experiences: dict[str, list[AgentExperience]] = {}  # agent_id -> experiences
    
    async def store_experience(
        self,
        agent_id: str,
        description: str,
        outcome: ExperienceOutcome,
        context: str = "",
    ) -> AgentExperience:
        """Almacena una experiencia."""
        experience = AgentExperience(
            agent_id=agent_id,
            description=description,
            context=context,
            outcome=outcome,
        )
        
        if agent_id not in self._experiences:
            self._experiences[agent_id] = []
        self._experiences[agent_id].append(experience)
        
        logger.info(f"Stored experience for {agent_id}: {outcome.value}")
        return experience
    
    async def retrieve_experiences(
        self,
        agent_id: str,
        scenario: str | None = None,
        validated_only: bool = False,
    ) -> LongTermResult:
        """Recupera experiencias."""
        experiences = self._experiences.get(agent_id, [])
        
        if scenario:
            experiences = [e for e in experiences if e.is_applicable(scenario)]
        
        if validated_only:
            experiences = [e for e in experiences if e.validated]
        
        return LongTermResult(
            agent_id=agent_id,
            experiences=experiences,
            experiences_count=len(experiences),
        )
    
    async def add_lesson(
        self,
        experience_id: str,
        agent_id: str,
        lesson: str,
    ) -> bool:
        """Agrega una lección a una experiencia."""
        experiences = self._experiences.get(agent_id, [])
        for exp in experiences:
            if exp.experience_id == experience_id:
                exp.add_lesson(lesson)
                return True
        return False


# =============================================================================
# CONVERSATION MEMORY
# =============================================================================

class ConversationMemory:
    """
    Memoria de conversación.
    
    Responsabilidades:
    - Almacenar contexto de conversaciones
    - Recuperar conversaciones pasadas
    - Gestionar resúmenes
    """
    
    def __init__(self):
        self._contexts: dict[str, ConversationContext] = {}  # context_id -> context
    
    async def create_context(
        self,
        session_id: str,
        participants: list[str],
    ) -> ConversationContext:
        """Crea un contexto de conversación."""
        context = ConversationContext(
            session_id=session_id,
            participants=participants,
        )
        
        self._contexts[context.context_id] = context
        return context
    
    async def add_message(
        self,
        context_id: str,
        sender_id: str,
        content: str,
        message_type: str = "text",
    ) -> Message | None:
        """Agrega un mensaje."""
        if context_id not in self._contexts:
            return None
        
        message = Message(
            sender_id=sender_id,
            content=content,
            message_type=message_type,
        )
        
        self._contexts[context_id].add_message(message)
        return message
    
    async def get_context(
        self,
        context_id: str,
    ) -> ConversationResult:
        """Obtiene un contexto."""
        context = self._contexts.get(context_id)
        
        return ConversationResult(
            context_id=context_id,
            context=context,
            messages_count=len(context.messages) if context else 0,
        )
    
    async def get_recent(
        self,
        agent_id: str,
        limit: int = 5,
    ) -> list[ConversationContext]:
        """Obtiene conversaciones recientes."""
        contexts = [
            c for c in self._contexts.values()
            if agent_id in c.participants
        ]
        
        contexts.sort(key=lambda c: c.updated_at, reverse=True)
        return contexts[:limit]


# =============================================================================
# MEMORY SYNCHRONIZER
# =============================================================================

class MemorySynchronizer:
    """
    Sincronizador de memoria.
    
    Responsabilidades:
    - Sincronizar memorias entre agentes
    - Resolver conflictos
    - Mantener consistencia
    """
    
    def __init__(self):
        self._sync_log: list[dict] = []
    
    async def sync_agent(
        self,
        agent_id: str,
        shared_memory: SharedMemory,
        episodic_memory: EpisodicMemory,
    ) -> SyncResult:
        """Sincroniza memorias de un agente."""
        synced = 0
        failed = 0
        
        # Obtener memorias episódicas
        result = await episodic_memory.retrieve(agent_id, limit=100)
        
        # Compartir memorias importantes
        for record in result.records:
            if record.importance in [MemoryImportance.HIGH, MemoryImportance.CRITICAL]:
                share_result = await shared_memory.share(agent_id, record)
                if share_result:
                    synced += 1
                else:
                    failed += 1
        
        self._sync_log.append({
            "agent_id": agent_id,
            "synced": synced,
            "failed": failed,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        
        return SyncResult(synced_count=synced, failed_count=failed)
    
    async def get_sync_status(self, agent_id: str) -> dict:
        """Obtiene estado de sincronización."""
        logs = [l for l in self._sync_log if l["agent_id"] == agent_id]
        
        if not logs:
            return {"status": "no_sync", "agent_id": agent_id}
        
        last_log = sorted(logs, key=lambda l: l["timestamp"])[-1]
        
        return {
            "status": "synced",
            "agent_id": agent_id,
            "last_sync": last_log["timestamp"],
            "synced_count": last_log["synced"],
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "EpisodicResult",
    "SharedResult",
    "LongTermResult",
    "ConversationResult",
    "SyncResult",
    # Engines
    "EpisodicMemory",
    "SharedMemory",
    "LongTermMemory",
    "ConversationMemory",
    "MemorySynchronizer",
]
