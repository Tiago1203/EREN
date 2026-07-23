"""
PHASE 5 - EPIC 8: Consensus Domain Objects

Domain objects especializados para consenso:
- ConsensusDecision
- AgentVote
- ConflictCase
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class ConsensusLevel(str, Enum):
    """Nivel de consenso alcanzado."""
    NONE = "none"                     # Sin consenso
    MINIMAL = "minimal"               # Mínimo (33%+)
    MODERATE = "moderate"            # Moderado (50%+)
    STRONG = "strong"                # Fuerte (66%+)
    UNANIMOUS = "unanimous"          # Unánime (100%)


class VoteOption(str, Enum):
    """Opción de voto."""
    APPROVE = "approve"             # Aprobar
    REJECT = "reject"              # Rechazar
    ABSTAIN = "abstain"            # Abstenerse
    DEFER = "defer"                # Aplazar


class ConflictType(str, Enum):
    """Tipo de conflicto."""
    ANSWER_CONFLICT = "answer_conflict"     # Conflicto en respuestas
    PRIORITY_CONFLICT = "priority_conflict" # Conflicto en prioridad
    INTERPRETATION_CONFLICT = "interpretation_conflict"  # Conflicto en interpretación
    RESOURCE_CONFLICT = "resource_conflict" # Conflicto en recursos


class ResolutionStrategy(str, Enum):
    """Estrategia de resolución."""
    MAJORITY = "majority"                 # Mayoría simple
    WEIGHTED = "weighted"                 # Ponderado por confianza
    EXPERT = "expert"                     # Decide el experto
    DELAYED = "delayed"                  # Aplazar decisión
    MERGED = "merged"                     # Fusionar respuestas


# =============================================================================
# AGENT VOTE - Voto de agente
# =============================================================================

@dataclass
class AgentVote:
    """Voto de un agente."""
    vote_id: str = ""
    agent_id: str = ""
    
    # Voto
    option: VoteOption = VoteOption.ABSTAIN
    justification: str = ""
    
    # Ponderación
    confidence: float = 0.5  # 0.0 - 1.0
    expertise_level: float = 0.5  # 0.0 - 1.0
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.vote_id:
            self.vote_id = str(uuid.uuid4())
    
    def get_weight(self) -> float:
        """Obtiene el peso del voto."""
        return (self.confidence * 0.5) + (self.expertise_level * 0.5)


# =============================================================================
# CONSENSUS DECISION - Decisión de consenso
# =============================================================================

@dataclass
class ConsensusDecision:
    """Decisión tomada por consenso."""
    decision_id: str = ""
    session_id: str = ""
    
    # Votos
    votes: list[AgentVote] = field(default_factory=list)
    
    # Resultado
    consensus_level: ConsensusLevel = ConsensusLevel.NONE
    winning_option: VoteOption | None = None
    winning_votes: int = 0
    total_votes: int = 0
    
    # Ponderación
    weighted_winner: str = ""
    weighted_score: float = 0.0
    
    # Decisión final
    final_decision: dict = field(default_factory=dict)
    reasoning: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None
    
    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = str(uuid.uuid4())
        self.total_votes = len(self.votes)
        self._calculate_results()
    
    def add_vote(self, vote: AgentVote) -> None:
        """Agrega un voto."""
        self.votes.append(vote)
        self.total_votes = len(self.votes)
        self._calculate_results()
    
    def _calculate_results(self) -> None:
        """Calcula resultados."""
        if not self.votes:
            return
        
        # Conteo simple
        vote_counts: dict[VoteOption, int] = {}
        for vote in self.votes:
            if vote.option != VoteOption.ABSTAIN:
                vote_counts[vote.option] = vote_counts.get(vote.option, 0) + 1
        
        if vote_counts:
            self.winning_option = max(vote_counts, key=vote_counts.get)
            self.winning_votes = vote_counts[self.winning_option]
        else:
            self.winning_option = None
            self.winning_votes = 0
        
        # Nivel de consenso
        non_abstain = sum(1 for v in self.votes if v.option != VoteOption.ABSTAIN)
        if non_abstain == 0:
            self.consensus_level = ConsensusLevel.NONE
        else:
            ratio = self.winning_votes / non_abstain if non_abstain > 0 else 0
            if ratio == 1.0:
                self.consensus_level = ConsensusLevel.UNANIMOUS
            elif ratio >= 0.66:
                self.consensus_level = ConsensusLevel.STRONG
            elif ratio >= 0.5:
                self.consensus_level = ConsensusLevel.MODERATE
            elif ratio >= 0.33:
                self.consensus_level = ConsensusLevel.MINIMAL
            else:
                self.consensus_level = ConsensusLevel.NONE
    
    def get_approval_rate(self) -> float:
        """Obtiene tasa de aprobación."""
        if self.total_votes == 0:
            return 0.0
        non_abstain = sum(1 for v in self.votes if v.option != VoteOption.ABSTAIN)
        if non_abstain == 0:
            return 0.0
        approve_votes = sum(1 for v in self.votes if v.option == VoteOption.APPROVE)
        return approve_votes / non_abstain


# =============================================================================
# CONFLICT CASE - Caso de conflicto
# =============================================================================

@dataclass
class ConflictCase:
    """Caso de conflicto entre agentes."""
    case_id: str = ""
    session_id: str = ""
    
    # Tipo y estado
    conflict_type: ConflictType = ConflictType.ANSWER_CONFLICT
    status: str = "open"  # open, resolving, resolved, escalated
    
    # Respuestas en conflicto
    conflicting_responses: list[dict] = field(default_factory=list)
    agents_involved: list[str] = field(default_factory=list)
    
    # Resolución
    resolution_strategy: ResolutionStrategy | None = None
    resolved_response: dict | None = None
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    
    def __post_init__(self):
        if not self.case_id:
            self.case_id = str(uuid.uuid4())
    
    def add_response(self, agent_id: str, response: dict) -> None:
        """Agrega una respuesta en conflicto."""
        if agent_id not in self.agents_involved:
            self.agents_involved.append(agent_id)
        self.conflicting_responses.append({
            "agent_id": agent_id,
            "response": response,
        })
    
    def resolve(self, strategy: ResolutionStrategy, response: dict) -> None:
        """Resuelve el conflicto."""
        self.resolution_strategy = strategy
        self.resolved_response = response
        self.status = "resolved"
        self.resolved_at = datetime.now(UTC)
    
    def escalate(self) -> None:
        """Escala el conflicto."""
        self.status = "escalated"
    
    def is_resolved(self) -> bool:
        """Verifica si está resuelto."""
        return self.status == "resolved"
