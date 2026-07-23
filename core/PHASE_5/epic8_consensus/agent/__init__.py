"""
PHASE 5 - EPIC 8: Consensus Engine

Motor de consenso para resolver conflictos entre agentes.
Combina respuestas y genera una única respuesta validada.
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
# IMPORTS FROM EPIC 8 DOMAIN
# =============================================================================

from core.PHASE_5.epic8_consensus.domain import (
    ConsensusDecision,
    ConsensusLevel,
    AgentVote,
    VoteOption,
    ConflictCase,
    ConflictType,
    ResolutionStrategy,
)

# =============================================================================
# IMPORTS FROM EPIC 8 ENGINES
# =============================================================================

from core.PHASE_5.epic8_consensus.engines import (
    VotingEngine,
    ConflictResolver,
    RankingEngine,
    ConsensusBuilder,
)


# =============================================================================
# CONSENSUS ENGINE CONFIG
# =============================================================================

@dataclass
class ConsensusEngineConfig:
    """Configuración del Consensus Engine."""
    # Engines
    enable_voting: bool = True
    enable_conflict_resolution: bool = True
    enable_ranking: bool = True
    enable_consensus_building: bool = True
    
    # Comportamiento
    min_consensus_level: ConsensusLevel = ConsensusLevel.MODERATE
    max_conflicts: int = 100
    
    # Estrategias
    default_resolution_strategy: ResolutionStrategy = ResolutionStrategy.WEIGHTED


# =============================================================================
# CONSENSUS ENGINE
# =============================================================================

class ConsensusEngine(BaseAgent):
    """
    Motor de consenso para resolver conflictos entre agentes.
    
    Responsabilidades:
    - Gestionar votación entre agentes
    - Resolver conflictos
    - Rankear respuestas
    - Construir consenso
    
    Hereda de BaseAgent para integrarse con el sistema de agentes.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: ConsensusEngineConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.CONSENSUS,
            name="Consensus Engine",
            description="Motor de consenso para resolver conflictos",
        )
        
        self.config = config or ConsensusEngineConfig()
        
        # Inicializar motores
        self._voting_engine = VotingEngine() if self.config.enable_voting else None
        self._conflict_resolver = ConflictResolver() if self.config.enable_conflict_resolution else None
        self._ranking_engine = RankingEngine() if self.config.enable_ranking else None
        self._consensus_builder = ConsensusBuilder() if self.config.enable_consensus_building else None
        
        # Métricas
        self._decisions_made = 0
        self._conflicts_resolved = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el motor."""
        await super().initialize()
        logger.info(f"ConsensusEngine {self.agent_id} initialized")
        logger.info(f"  - Voting: {self._voting_engine is not None}")
        logger.info(f"  - Conflict Resolution: {self._conflict_resolver is not None}")
        logger.info(f"  - Ranking: {self._ranking_engine is not None}")
        logger.info(f"  - Consensus Building: {self._consensus_builder is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el motor."""
        await super().shutdown()
        logger.info(f"ConsensusEngine {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de consenso."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Obtener parámetros
            input_data = task.input_data
            action = input_data.get("action", "vote")
            
            # Procesar según acción
            if action == "vote":
                result = await self._handle_vote(input_data)
            elif action == "resolve":
                result = await self._handle_resolve(input_data)
            elif action == "rank":
                result = await self._handle_rank(input_data)
            elif action == "consensus":
                result = await self._handle_consensus(input_data)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            self._decisions_made += 1
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.92,
            )
            
        except Exception as e:
            logger.error(f"ConsensusEngine execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # VOTE HANDLERS
    # =============================================================================
    
    async def _handle_vote(self, input_data: dict) -> dict:
        """Maneja operaciones de votación."""
        result = {"action": "vote"}
        
        decision_id = input_data.get("decision_id", "")
        votes_data = input_data.get("votes", [])
        
        # Convertir votos
        votes = []
        for vote_data in votes_data:
            try:
                vote = AgentVote(
                    agent_id=vote_data.get("agent_id", ""),
                    option=VoteOption(vote_data.get("option", "abstain")),
                    justification=vote_data.get("justification", ""),
                    confidence=vote_data.get("confidence", 0.5),
                    expertise_level=vote_data.get("expertise_level", 0.5),
                )
                votes.append(vote)
            except ValueError:
                pass
        
        # Procesar votación
        if self._voting_engine:
            voting_result = await self._voting_engine.vote(decision_id, votes)
            
            result["decision_id"] = voting_result.decision_id
            result["votes_count"] = voting_result.votes_count
            result["approval_rate"] = voting_result.approval_rate
            result["consensus_level"] = voting_result.consensus_level.value
        
        return result
    
    async def cast_vote(
        self,
        agent_id: str,
        option: str,
        confidence: float = 0.5,
    ) -> AgentVote:
        """Crea un voto."""
        try:
            vote_option = VoteOption(option)
        except ValueError:
            vote_option = VoteOption.ABSTAIN
        
        return AgentVote(
            agent_id=agent_id,
            option=vote_option,
            confidence=confidence,
        )
    
    # =============================================================================
    # CONFLICT HANDLERS
    # =============================================================================
    
    async def _handle_resolve(self, input_data: dict) -> dict:
        """Maneja resolución de conflictos."""
        result = {"action": "resolve"}
        
        case_data = input_data.get("case", {})
        strategy_str = input_data.get("strategy")
        
        # Crear caso
        case = ConflictCase(
            session_id=case_data.get("session_id", ""),
            conflict_type=ConflictType(case_data.get("type", "answer_conflict")),
        )
        
        # Agregar respuestas
        for response in case_data.get("responses", []):
            case.add_response(
                response.get("agent_id", ""),
                response.get("response", {}),
            )
        
        # Estrategia
        strategy = None
        if strategy_str:
            try:
                strategy = ResolutionStrategy(strategy_str)
            except ValueError:
                pass
        
        # Resolver
        if self._conflict_resolver:
            resolution_result = await self._conflict_resolver.resolve(case, strategy)
            
            result["case_id"] = resolution_result.case_id
            result["resolved"] = resolution_result.resolved
            result["strategy_used"] = resolution_result.strategy_used.value if resolution_result.strategy_used else None
            result["confidence"] = resolution_result.confidence
            
            self._conflicts_resolved += 1
        
        return result
    
    async def create_conflict_case(
        self,
        session_id: str,
        conflict_type: str,
        responses: list[dict],
    ) -> ConflictCase:
        """Crea un caso de conflicto."""
        try:
            c_type = ConflictType(conflict_type)
        except ValueError:
            c_type = ConflictType.ANSWER_CONFLICT
        
        case = ConflictCase(
            session_id=session_id,
            conflict_type=c_type,
        )
        
        for response in responses:
            case.add_response(
                response.get("agent_id", ""),
                response.get("response", {}),
            )
        
        return case
    
    # =============================================================================
    # RANK HANDLERS
    # =============================================================================
    
    async def _handle_rank(self, input_data: dict) -> dict:
        """Maneja operaciones de ranking."""
        result = {"action": "rank"}
        
        items = input_data.get("items", [])
        criteria = input_data.get("criteria")
        
        if self._ranking_engine:
            ranking_result = await self._ranking_engine.rank(items, criteria)
            
            result["ranked_items"] = ranking_result.ranked_items
            result["top_score"] = ranking_result.top_score
        
        return result
    
    # =============================================================================
    # CONSENSUS HANDLERS
    # =============================================================================
    
    async def _handle_consensus(self, input_data: dict) -> dict:
        """Maneja construcción de consenso."""
        result = {"action": "consensus"}
        
        session_id = input_data.get("session_id", "")
        responses = input_data.get("responses", [])
        agents = input_data.get("agents", [])
        
        if self._consensus_builder:
            consensus_result = await self._consensus_builder.build(
                session_id=session_id,
                responses=responses,
                agents=agents,
            )
            
            result["success"] = consensus_result.success
            result["consensus_level"] = consensus_result.consensus_level.value
            result["final_decision"] = consensus_result.final_decision
            result["reasoning"] = consensus_result.reasoning
            result["confidence"] = consensus_result.confidence
        
        return result
    
    async def build_consensus(
        self,
        session_id: str,
        responses: list[dict],
    ) -> dict:
        """Construye consenso."""
        if self._consensus_builder:
            result = await self._consensus_builder.build(
                session_id=session_id,
                responses=responses,
                agents=[],
            )
            
            return {
                "success": result.success,
                "level": result.consensus_level.value,
                "decision": result.final_decision,
                "confidence": result.confidence,
            }
        
        return {"success": False}
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del motor."""
        return {
            "decisions_made": self._decisions_made,
            "conflicts_resolved": self._conflicts_resolved,
            "engines_enabled": {
                "voting": self._voting_engine is not None,
                "conflict_resolution": self._conflict_resolver is not None,
                "ranking": self._ranking_engine is not None,
                "consensus_building": self._consensus_builder is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ConsensusEngine",
    "ConsensusEngineConfig",
]
