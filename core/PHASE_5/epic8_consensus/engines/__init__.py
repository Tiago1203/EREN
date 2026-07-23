"""
PHASE 5 - EPIC 8: Consensus Engines

Motores especializados para consenso:
- VotingEngine
- ConflictResolver
- RankingEngine
- ConsensusBuilder
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

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
# VOTING RESULT
# =============================================================================

@dataclass
class VotingResult:
    """Resultado de votación."""
    decision_id: str
    
    # Resultado
    votes_count: int = 0
    approval_rate: float = 0.0
    consensus_level: ConsensusLevel = ConsensusLevel.NONE
    
    # Votos
    votes_by_option: dict = field(default_factory=dict)
    
    # Metadatos
    voted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# RESOLUTION RESULT
# =============================================================================

@dataclass
class ResolutionResult:
    """Resultado de resolución."""
    case_id: str
    
    # Resultado
    resolved: bool = False
    strategy_used: ResolutionStrategy | None = None
    resolved_response: dict | None = None
    
    # Confianza
    confidence: float = 0.0
    
    # Metadatos
    resolved_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# RANKING RESULT
# =============================================================================

@dataclass
class RankingResult:
    """Resultado de ranking."""
    session_id: str
    
    # Ranking
    ranked_items: list[dict] = field(default_factory=list)
    
    # Score
    top_score: float = 0.0
    
    # Metadatos
    ranked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# CONSENSUS RESULT
# =============================================================================

@dataclass
class ConsensusResult:
    """Resultado de consenso."""
    session_id: str
    
    # Resultado
    success: bool = False
    consensus_level: ConsensusLevel = ConsensusLevel.NONE
    
    # Decisión
    final_decision: dict | None = None
    reasoning: str = ""
    
    # Confianza
    confidence: float = 0.0
    
    # Metadatos
    built_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# VOTING ENGINE
# =============================================================================

class VotingEngine:
    """
    Motor de votación.
    
    Responsabilidades:
    - Gestionar votación entre agentes
    - Calcular niveles de consenso
    - Determinar ganador
    """
    
    async def vote(
        self,
        decision_id: str,
        votes: list[AgentVote],
    ) -> VotingResult:
        """
        Procesa una votación.
        
        Args:
            decision_id: ID de la decisión
            votes: Lista de votos
        
        Returns:
            VotingResult con el resultado
        """
        logger.info(f"Processing vote for decision {decision_id}")
        
        # Crear decisión
        decision = ConsensusDecision(
            decision_id=decision_id,
        )
        
        # Agregar votos
        for vote in votes:
            decision.add_vote(vote)
        
        # Contar votos
        votes_by_option: dict[str, int] = {}
        for vote in votes:
            option = vote.option.value
            votes_by_option[option] = votes_by_option.get(option, 0) + 1
        
        return VotingResult(
            decision_id=decision_id,
            votes_count=len(votes),
            approval_rate=decision.get_approval_rate(),
            consensus_level=decision.consensus_level,
            votes_by_option=votes_by_option,
        )
    
    async def tally_votes(
        self,
        votes: list[AgentVote],
    ) -> dict:
        """
        Cuenta votos ponderados.
        
        Args:
            votes: Lista de votos
        
        Returns:
            Dict con conteo ponderado
        """
        weighted_counts: dict[str, float] = {}
        
        for vote in votes:
            if vote.option != VoteOption.ABSTAIN:
                weight = vote.get_weight()
                option = vote.option.value
                weighted_counts[option] = weighted_counts.get(option, 0.0) + weight
        
        return weighted_counts


# =============================================================================
# CONFLICT RESOLVER
# =============================================================================

class ConflictResolver:
    """
    Motor de resolución de conflictos.
    
    Responsabilidades:
    - Detectar conflictos
    - Seleccionar estrategia de resolución
    - Resolver conflictos
    """
    
    async def resolve(
        self,
        case: ConflictCase,
        strategy: ResolutionStrategy | None = None,
    ) -> ResolutionResult:
        """
        Resuelve un conflicto.
        
        Args:
            case: Caso de conflicto
            strategy: Estrategia a usar
        
        Returns:
            ResolutionResult con el resultado
        """
        logger.info(f"Resolving conflict case {case.case_id}")
        
        # Seleccionar estrategia si no seprovee
        if strategy is None:
            strategy = self._select_strategy(case)
        
        # Resolver según estrategia
        resolved_response = await self._apply_strategy(case, strategy)
        
        # Actualizar caso
        case.resolve(strategy, resolved_response)
        
        # Calcular confianza
        confidence = self._calculate_confidence(case, strategy)
        
        return ResolutionResult(
            case_id=case.case_id,
            resolved=True,
            strategy_used=strategy,
            resolved_response=resolved_response,
            confidence=confidence,
        )
    
    def _select_strategy(self, case: ConflictCase) -> ResolutionStrategy:
        """Selecciona estrategia de resolución."""
        if len(case.conflicting_responses) == 2:
            return ResolutionStrategy.MERGED
        elif len(case.agents_involved) > 3:
            return ResolutionStrategy.MAJORITY
        else:
            return ResolutionStrategy.WEIGHTED
    
    async def _apply_strategy(
        self,
        case: ConflictCase,
        strategy: ResolutionStrategy,
    ) -> dict:
        """Aplica estrategia de resolución."""
        if strategy == ResolutionStrategy.MAJORITY:
            # Seleccionar respuesta más frecuente
            return case.conflicting_responses[0]["response"] if case.conflicting_responses else {}
        
        elif strategy == ResolutionStrategy.WEIGHTED:
            # Fusionar respuestas con pesos
            return self._merge_responses(case.conflicting_responses)
        
        elif strategy == ResolutionStrategy.EXPERT:
            # Usar respuesta del experto (primero por ahora)
            return case.conflicting_responses[0]["response"] if case.conflicting_responses else {}
        
        elif strategy == ResolutionStrategy.MERGED:
            # Fusionar respuestas
            return self._merge_responses(case.conflicting_responses)
        
        else:
            return {}
    
    def _merge_responses(self, responses: list[dict]) -> dict:
        """Fusiona respuestas."""
        if not responses:
            return {}
        
        merged = {
            "type": "merged",
            "sources_count": len(responses),
            "merged_content": [],
        }
        
        for item in responses:
            merged["merged_content"].append(item.get("response", {}))
        
        return merged
    
    def _calculate_confidence(
        self,
        case: ConflictCase,
        strategy: ResolutionStrategy,
    ) -> float:
        """Calcula confianza de la resolución."""
        base = 0.7
        
        if strategy == ResolutionStrategy.MERGED:
            return base + 0.2
        elif strategy == ResolutionStrategy.MAJORITY:
            return base + 0.1
        
        return base


# =============================================================================
# RANKING ENGINE
# =============================================================================

class RankingEngine:
    """
    Motor de ranking.
    
    Responsabilidades:
    - Rankear respuestas de agentes
    - Ordenar por score
    - Seleccionar mejor opción
    """
    
    async def rank(
        self,
        items: list[dict],
        criteria: dict | None = None,
    ) -> RankingResult:
        """
        Rankea items.
        
        Args:
            items: Items a rankear
            criteria: Criterios de ranking
        
        Returns:
            RankingResult con el resultado
        """
        logger.info(f"Ranking {len(items)} items")
        
        # Score items
        scored = []
        for item in items:
            score = self._calculate_score(item, criteria)
            scored.append({
                "item": item,
                "score": score,
            })
        
        # Ordenar por score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Extraer ranking
        ranked = [{"item": s["item"], "score": s["score"]} for s in scored]
        
        top_score = scored[0]["score"] if scored else 0.0
        
        return RankingResult(
            session_id="",
            ranked_items=ranked,
            top_score=top_score,
        )
    
    def _calculate_score(self, item: dict, criteria: dict | None) -> float:
        """Calcula score de un item."""
        score = 0.5  # Score base
        
        # Factores
        if "confidence" in item:
            score += item["confidence"] * 0.3
        
        if "relevance" in item:
            score += item["relevance"] * 0.2
        
        return min(1.0, max(0.0, score))


# =============================================================================
# CONSENSUS BUILDER
# =============================================================================

class ConsensusBuilder:
    """
    Motor de construcción de consenso.
    
    Responsabilidades:
    - Construir decisión consensuada
    - Generar razonamiento
    - Validar consenso
    """
    
    async def build(
        self,
        session_id: str,
        responses: list[dict],
        agents: list[str],
    ) -> ConsensusResult:
        """
        Construye consenso.
        
        Args:
            session_id: ID de sesión
            responses: Respuestas de agentes
            agents: IDs de agentes
        
        Returns:
            ConsensusResult con el resultado
        """
        logger.info(f"Building consensus for session {session_id}")
        
        if not responses:
            return ConsensusResult(
                session_id=session_id,
                success=False,
                reasoning="No responses provided",
            )
        
        # Si hay una respuesta clara, usarla
        if len(responses) == 1:
            return ConsensusResult(
                session_id=session_id,
                success=True,
                consensus_level=ConsensusLevel.UNANIMOUS,
                final_decision=responses[0],
                reasoning="Single response - auto consensus",
                confidence=1.0,
            )
        
        # Fusionar respuestas
        merged = self._merge_responses(responses)
        
        # Calcular nivel de consenso
        consensus_level = self._estimate_consensus_level(responses)
        
        # Generar razonamiento
        reasoning = self._generate_reasoning(consensus_level, len(responses))
        
        return ConsensusResult(
            session_id=session_id,
            success=True,
            consensus_level=consensus_level,
            final_decision=merged,
            reasoning=reasoning,
            confidence=0.8 if consensus_level != ConsensusLevel.NONE else 0.3,
        )
    
    def _merge_responses(self, responses: list[dict]) -> dict:
        """Fusiona respuestas."""
        return {
            "type": "consensus",
            "sources_count": len(responses),
            "content": responses[0] if responses else {},
        }
    
    def _estimate_consensus_level(
        self,
        responses: list[dict],
    ) -> ConsensusLevel:
        """Estima nivel de consenso."""
        if len(responses) == 1:
            return ConsensusLevel.UNANIMOUS
        
        # Comparar respuestas
        first = responses[0]
        similar = sum(1 for r in responses if r == first)
        ratio = similar / len(responses)
        
        if ratio >= 0.9:
            return ConsensusLevel.STRONG
        elif ratio >= 0.7:
            return ConsensusLevel.MODERATE
        elif ratio >= 0.5:
            return ConsensusLevel.MINIMAL
        else:
            return ConsensusLevel.NONE
    
    def _generate_reasoning(
        self,
        level: ConsensusLevel,
        agents_count: int,
    ) -> str:
        """Genera razonamiento."""
        if level == ConsensusLevel.UNANIMOUS:
            return f"All {agents_count} agents agreed"
        elif level == ConsensusLevel.STRONG:
            return f"Strong consensus from {agents_count} agents"
        elif level == ConsensusLevel.MODERATE:
            return f"Moderate consensus from {agents_count} agents"
        elif level == ConsensusLevel.MINIMAL:
            return f"Minimal consensus from {agents_count} agents"
        else:
            return f"No consensus from {agents_count} agents"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "VotingResult",
    "ResolutionResult",
    "RankingResult",
    "ConsensusResult",
    # Engines
    "VotingEngine",
    "ConflictResolver",
    "RankingEngine",
    "ConsensusBuilder",
]
