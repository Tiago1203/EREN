"""
PHASE 5 - EPIC 9: Agent Memory Engine

Motor de memoria para dar memoria individual y colectiva a los agentes.
Persiste experiencias, contexto y conversaciones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

# =============================================================================
# IMPORTS FROM EPIC 9 DOMAIN
# =============================================================================

from core.PHASE_5.epic9_memory.domain import (
    MemoryType,
    MemoryImportance,
    ExperienceOutcome,
)

# =============================================================================
# IMPORTS FROM EPIC 9 ENGINES
# =============================================================================

from core.PHASE_5.epic9_memory.engines import (
    EpisodicMemory,
    SharedMemory,
    LongTermMemory,
    ConversationMemory,
    MemorySynchronizer,
)


# =============================================================================
# AGENT MEMORY CONFIG
# =============================================================================

@dataclass
class AgentMemoryConfig:
    """Configuración del Agent Memory."""
    # Engines
    enable_episodic: bool = True
    enable_shared: bool = True
    enable_long_term: bool = True
    enable_conversation: bool = True
    enable_sync: bool = True
    
    # Comportamiento
    max_episodic_days: int = 7
    max_shared_records: int = 1000
    auto_sync_interval_seconds: int = 300


# =============================================================================
# AGENT MEMORY
# =============================================================================

class AgentMemory(BaseAgent):
    """
    Motor de memoria para agentes.
    
    Responsabilidades:
    - Gestionar memoria episódica
    - Gestionar memoria compartida
    - Gestionar memoria a largo plazo
    - Gestionar memoria de conversación
    - Sincronizar memorias entre agentes
    
    Hereda de BaseAgent para integrarse con el sistema de agentes.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: AgentMemoryConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.MEMORY,
            name="Agent Memory",
            description="Motor de memoria para agentes",
        )
        
        self.config = config or AgentMemoryConfig()
        
        # Inicializar motores
        self._episodic_memory = EpisodicMemory() if self.config.enable_episodic else None
        self._shared_memory = SharedMemory() if self.config.enable_shared else None
        self._long_term_memory = LongTermMemory() if self.config.enable_long_term else None
        self._conversation_memory = ConversationMemory() if self.config.enable_conversation else None
        self._synchronizer = MemorySynchronizer() if self.config.enable_sync else None
        
        # Métricas
        self._records_stored = 0
        self._experiences_stored = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el motor."""
        await super().initialize()
        logger.info(f"AgentMemory {self.agent_id} initialized")
        logger.info(f"  - Episodic: {self._episodic_memory is not None}")
        logger.info(f"  - Shared: {self._shared_memory is not None}")
        logger.info(f"  - Long-term: {self._long_term_memory is not None}")
        logger.info(f"  - Conversation: {self._conversation_memory is not None}")
        logger.info(f"  - Sync: {self._synchronizer is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el motor."""
        await super().shutdown()
        logger.info(f"AgentMemory {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de memoria."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Obtener parámetros
            input_data = task.input_data
            action = input_data.get("action", "store")
            
            # Procesar según acción
            if action == "store":
                result = await self._handle_store(input_data)
            elif action == "retrieve":
                result = await self._handle_retrieve(input_data)
            elif action == "experience":
                result = await self._handle_experience(input_data)
            elif action == "conversation":
                result = await self._handle_conversation(input_data)
            elif action == "share":
                result = await self._handle_share(input_data)
            elif action == "sync":
                result = await self._handle_sync(input_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.95,
            )
            
        except Exception as e:
            logger.error(f"AgentMemory execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # STORE HANDLERS
    # =============================================================================
    
    async def _handle_store(self, input_data: dict) -> dict:
        """Maneja almacenamiento de memoria."""
        result = {"action": "store"}
        
        agent_id = input_data.get("agent_id", self.agent_id)
        content = input_data.get("content", "")
        
        try:
            memory_type = MemoryType(input_data.get("type", "episodic"))
        except ValueError:
            memory_type = MemoryType.EPISODIC
        
        try:
            importance = MemoryImportance(input_data.get("importance", "medium"))
        except ValueError:
            importance = MemoryImportance.MEDIUM
        
        if self._episodic_memory:
            record = await self._episodic_memory.store(
                agent_id=agent_id,
                content=content,
                context=input_data.get("context"),
                memory_type=memory_type,
                importance=importance,
            )
            
            result["record_id"] = record.record_id
            self._records_stored += 1
        
        return result
    
    # =============================================================================
    # RETRIEVE HANDLERS
    # =============================================================================
    
    async def _handle_retrieve(self, input_data: dict) -> dict:
        """Maneja recuperación de memoria."""
        result = {"action": "retrieve"}
        
        agent_id = input_data.get("agent_id", self.agent_id)
        
        if self._episodic_memory:
            episodic_result = await self._episodic_memory.retrieve(
                agent_id=agent_id,
                session_id=input_data.get("session_id"),
                limit=input_data.get("limit", 10),
            )
            
            result["records_count"] = episodic_result.records_count
            result["records"] = [
                {"id": r.record_id, "content": r.content, "type": r.memory_type.value}
                for r in episodic_result.records
            ]
        
        return result
    
    # =============================================================================
    # EXPERIENCE HANDLERS
    # =============================================================================
    
    async def _handle_experience(self, input_data: dict) -> dict:
        """Maneja experiencias."""
        result = {"action": "experience"}
        operation = input_data.get("operation", "store")
        
        agent_id = input_data.get("agent_id", self.agent_id)
        
        if operation == "store":
            try:
                outcome = ExperienceOutcome(input_data.get("outcome", "unknown"))
            except ValueError:
                outcome = ExperienceOutcome.UNKNOWN
            
            if self._long_term_memory:
                experience = await self._long_term_memory.store_experience(
                    agent_id=agent_id,
                    description=input_data.get("description", ""),
                    outcome=outcome,
                    context=input_data.get("context", ""),
                )
                
                result["experience_id"] = experience.experience_id
                self._experiences_stored += 1
        
        elif operation == "retrieve":
            if self._long_term_memory:
                exp_result = await self._long_term_memory.retrieve_experiences(
                    agent_id=agent_id,
                    scenario=input_data.get("scenario"),
                    validated_only=input_data.get("validated_only", False),
                )
                
                result["experiences_count"] = exp_result.experiences_count
        
        return result
    
    # =============================================================================
    # CONVERSATION HANDLERS
    # =============================================================================
    
    async def _handle_conversation(self, input_data: dict) -> dict:
        """Maneja memoria de conversación."""
        result = {"action": "conversation"}
        operation = input_data.get("operation", "create")
        
        if operation == "create":
            if self._conversation_memory:
                context = await self._conversation_memory.create_context(
                    session_id=input_data.get("session_id", ""),
                    participants=input_data.get("participants", []),
                )
                result["context_id"] = context.context_id
        
        elif operation == "message":
            if self._conversation_memory:
                message = await self._conversation_memory.add_message(
                    context_id=input_data.get("context_id", ""),
                    sender_id=input_data.get("sender_id", ""),
                    content=input_data.get("content", ""),
                )
                if message:
                    result["message_id"] = message.message_id
        
        elif operation == "get":
            if self._conversation_memory:
                conv_result = await self._conversation_memory.get_context(
                    context_id=input_data.get("context_id", ""),
                )
                result["context_id"] = conv_result.context_id
                result["messages_count"] = conv_result.messages_count
        
        return result
    
    # =============================================================================
    # SHARE HANDLERS
    # =============================================================================
    
    async def _handle_share(self, input_data: dict) -> dict:
        """Maneja compartición de memoria."""
        result = {"action": "share"}
        
        agent_id = input_data.get("agent_id", self.agent_id)
        
        if self._shared_memory:
            # Crear registro para compartir
            if self._episodic_memory:
                episodic_result = await self._episodic_memory.retrieve(
                    agent_id=agent_id,
                    limit=1,
                )
                
                if episodic_result.records:
                    share_result = await self._shared_memory.share(
                        agent_id=agent_id,
                        record=episodic_result.records[0],
                    )
                    result["shared_count"] = share_result.shared_count
        
        return result
    
    # =============================================================================
    # SYNC HANDLERS
    # =============================================================================
    
    async def _handle_sync(self, input_data: dict) -> dict:
        """Maneja sincronización."""
        result = {"action": "sync"}
        
        agent_id = input_data.get("agent_id", self.agent_id)
        
        if self._synchronizer and self._shared_memory and self._episodic_memory:
            sync_result = await self._synchronizer.sync_agent(
                agent_id=agent_id,
                shared_memory=self._shared_memory,
                episodic_memory=self._episodic_memory,
            )
            
            result["synced_count"] = sync_result.synced_count
            result["failed_count"] = sync_result.failed_count
        
        return result
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del motor."""
        return {
            "records_stored": self._records_stored,
            "experiences_stored": self._experiences_stored,
            "engines_enabled": {
                "episodic": self._episodic_memory is not None,
                "shared": self._shared_memory is not None,
                "long_term": self._long_term_memory is not None,
                "conversation": self._conversation_memory is not None,
                "sync": self._synchronizer is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AgentMemory",
    "AgentMemoryConfig",
]
