# EPIC 8: Consensus Engine

*Versión: 2.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Resolver conflictos entre agentes mediante deliberación y consenso.**

EPIC 8 es responsable de:
- Gestionar votación entre agentes
- Resolver conflictos
- Rankear respuestas
- Construir consenso
- **Deliberación entre expertos** *(NUEVO v2.0)*
- **Argumentación estructurada** *(NUEVO v2.0)*
- **Preservación de opiniones disidentes** *(NUEVO v2.0)*

---

## Dependencias

### EPICs
- **EPIC 7**: Collaboration Engine (provee colaboración)
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 8: Consensus Engine (v2.0)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    CONSENSUS ENGINE                                │   │
│  │  ├── VotingEngine ─────────────────── Gestión de votación        │   │
│  │  ├── ConflictResolver ─────────────── Resolución de conflictos │   │
│  │  ├── RankingEngine ─────────────────── Ranking de respuestas     │   │
│  │  └── ConsensusBuilder ─────────────── Construcción de consenso  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │         DELIBERATIVE CONSENSUS MODULE (NUEVO v2.0)                 │   │
│  │  ├── DeliberationEngine ─────────────── Motor de deliberación    │   │
│  │  ├── ArgumentationEngine ────────────── Motor de argumentación   │   │
│  │  ├── ExpertWeighting ───────────────── Ponderación de expertos   │   │
│  │  ├── DissentingOpinionPreserver ─────── Preserva opiniones       │   │
│  │  └── ConsensusLevelCalculator ───────── Calcula nivel de consenso │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── ConsensusDecision ─────────────── Decisión de consenso     │   │
│  │  ├── AgentVote ─────────────────────── Voto de agente            │   │
│  │  ├── ConflictCase ──────────────────── Caso de conflicto        │   │
│  │  ├── ExpertArgument ─────────────────── Argumento de experto    │   │
│  │  └── DeliberationSession ─────────────── Sesión de deliberación  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic8_consensus/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # ConsensusDecision, AgentVote, ConflictCase
├── engines/
│   ├── __init__.py              # VotingEngine, ConflictResolver, etc.
│   └── deliberation/            # Deliberative Consensus (NUEVO v2.0)
│       ├── __init__.py          # DeliberationEngine, ArgumentationEngine
│       ├── deliberation_engine.py
│       ├── argumentation_engine.py
│       ├── expert_weighting.py
│       └── dissent_preserver.py
└── agent/
    └── __init__.py              # ConsensusEngine
```

---

## Componentes

### 1. ConsensusEngine

Motor principal de consenso.

```python
class ConsensusEngine(BaseAgent):
    """Motor de consenso para resolver conflictos."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de consenso."""
```

**Acciones:**
- `vote`: Gestionar votación
- `resolve`: Resolver conflictos
- `rank`: Rankear respuestas
- `consensus`: Construir consenso

### 2. VotingEngine

Gestión de votación entre agentes.

```python
class VotingEngine:
    """Motor de votación."""
    
    async def vote(
        self,
        decision_id: str,
        votes: list[AgentVote],
    ) -> VotingResult:
        """Procesa una votación."""
    
    async def tally_votes(
        self,
        votes: list[AgentVote],
    ) -> dict:
        """Cuenta votos ponderados."""
```

**Opciones de voto:**
- `APPROVE`: Aprobar
- `REJECT`: Rechazar
- `ABSTAIN`: Abstenerse
- `DEFER`: Aplazar

### 3. ConflictResolver

Resolución de conflictos.

```python
class ConflictResolver:
    """Motor de resolución de conflictos."""
    
    async def resolve(
        self,
        case: ConflictCase,
        strategy: ResolutionStrategy | None,
    ) -> ResolutionResult:
        """Resuelve un conflicto."""
```

**Estrategias:**
- `MAJORITY`: Mayoría simple
- `WEIGHTED`: Ponderado por confianza
- `EXPERT`: Decide el experto
- `DELAYED`: Aplazar decisión
- `MERGED`: Fusionar respuestas

### 4. RankingEngine

Ranking de respuestas.

```python
class RankingEngine:
    """Motor de ranking."""
    
    async def rank(
        self,
        items: list[dict],
        criteria: dict | None,
    ) -> RankingResult:
        """Rankea items."""
```

### 5. ConsensusBuilder

Construcción de consenso.

```python
class ConsensusBuilder:
    """Motor de construcción de consenso."""
    
    async def build(
        self,
        session_id: str,
        responses: list[dict],
        agents: list[str],
    ) -> ConsensusResult:
        """Construye consenso."""
```

### 6. DeliberationEngine (NUEVO v2.0)

Motor de deliberación entre expertos.

```python
class DeliberationEngine:
    """Motor de deliberación."""
    
    async def deliberate(
        self,
        session: DeliberationSession,
        agents: list[ExpertAgent],
    ) -> DeliberationResult:
        """Ejecuta deliberación."""
    
    async def exchange_arguments(
        self,
        session_id: str,
        arguments: list[ExpertArgument],
    ) -> list[ExpertArgument]:
        """Intercambia argumentos."""
    
    async def update_positions(
        self,
        session_id: str,
    ) -> PositionUpdate:
        """Actualiza posiciones después de argumentos."""
```

### 7. ArgumentationEngine (NUEVO v2.0)

Motor de argumentación estructurada.

```python
class ArgumentationEngine:
    """Motor de argumentación."""
    
    async def generate_argument(
        self,
        agent: ExpertAgent,
        claim: str,
        evidence: list[Evidence],
    ) -> ExpertArgument:
        """Genera argumento estructurado."""
    
    async def evaluate_argument(
        self,
        argument: ExpertArgument,
    ) -> ArgumentEvaluation:
        """Evalúa calidad de argumento."""
    
    async def generate_counter_argument(
        self,
        counter_to: ExpertArgument,
    ) -> ExpertArgument:
        """Genera contra-argumento."""
```

### 8. ExpertWeighting (NUEVO v2.0)

Ponderación de expertos por expertise.

```python
class ExpertWeighting:
    """Ponderación de expertos."""
    
    async def calculate_weights(
        self,
        agents: list[ExpertAgent],
        context: ClinicalContext,
    ) -> dict[str, float]:
        """Calcula pesos de expertos."""
    
    async def update_weights(
        self,
        agent_id: str,
        outcome: Outcome,
    ) -> UpdatedWeight:
        """Actualiza peso basado en resultados."""
```

### 9. DissentingOpinionPreserver (NUEVO v2.0)

Preserva opiniones disidentes.

```python
class DissentingOpinionPreserver:
    """Preservador de opiniones disidentes."""
    
    async def preserve_dissent(
        self,
        opinion: ExpertOpinion,
        consensus_decision: ConsensusDecision,
    ) -> DissentingOpinion:
        """Preserva opinión disidente."""
    
    async def get_dissenting_opinions(
        self,
        decision_id: str,
    ) -> list[DissentingOpinion]:
        """Obtiene opiniones disidentes."""
    
    async def document_reconsideration(
        self,
        decision_id: str,
        new_evidence: list[Evidence],
    ) -> ReconsiderationResult:
        """Documenta reconsideración futura."""
```

---

## Domain Objects

### ConsensusDecision

```python
@dataclass
class ConsensusDecision:
    """Decisión tomada por consenso."""
    decision_id: str
    votes: list[AgentVote]
    consensus_level: ConsensusLevel
    
    def add_vote(self, vote: AgentVote) -> None:
        """Agrega un voto."""
    
    def get_approval_rate(self) -> float:
        """Obtiene tasa de aprobación."""
```

### AgentVote

```python
@dataclass
class AgentVote:
    """Voto de un agente."""
    agent_id: str
    option: VoteOption
    confidence: float
    expertise_level: float
    
    def get_weight(self) -> float:
        """Obtiene el peso del voto."""
```

### ConflictCase

```python
@dataclass
class ConflictCase:
    """Caso de conflicto."""
    case_id: str
    conflict_type: ConflictType
    conflicting_responses: list[dict]
    
    def add_response(self, agent_id: str, response: dict) -> None:
        """Agrega respuesta."""
    
    def resolve(self, strategy: ResolutionStrategy, response: dict) -> None:
        """Resuelve el conflicto."""
```

### ExpertArgument (NUEVO v2.0)

```python
@dataclass
class ExpertArgument:
    """Argumento de experto."""
    argument_id: str
    agent_id: str
    claim: str
    evidence: list[Evidence]
    reasoning_chain: ReasoningChain
    strength: ArgumentStrength
    
    def is_supported(self) -> bool:
        """Verifica si está soportado por evidencia."""
    
    def get_counter_arguments(self) -> list[str]:
        """Obtiene contra-argumentos."""
```

### DeliberationSession (NUEVO v2.0)

```python
@dataclass
class DeliberationSession:
    """Sesión de deliberación."""
    session_id: str
    topic: str
    participants: list[ExpertAgent]
    arguments: list[ExpertArgument]
    dissenting_opinions: list[DissentingOpinion]
    consensus_level: ConsensusLevel
    
    def add_argument(self, argument: ExpertArgument) -> None:
        """Agrega argumento."""
    
    def get_final_position(self) -> ExpertPosition:
        """Obtiene posición final."""
```

---

## Niveles de Consenso

| Nivel | Descripción | Umbral |
|-------|-------------|--------|
| `NONE` | Sin consenso | < 33% |
| `MINIMAL` | Mínimo | >= 33% |
| `MODERATE` | Moderado | >= 50% |
| `STRONG` | Fuerte | >= 66% |
| `UNANIMOUS` | Unánime | 100% |

---

## Uso

### Votación

```python
from core.PHASE_5.epic8_consensus import (
    ConsensusEngine,
    ConsensusEngineConfig,
)

engine = ConsensusEngine(
    agent_id="consensus_1",
    config=ConsensusEngineConfig(),
)

result = await engine.execute(AgentTask(
    task_id="task_1",
    agent_id="consensus_1",
    task_type="consensus",
    input_data={
        "action": "vote",
        "decision_id": "decision_123",
        "votes": [
            {"agent_id": "agent_1", "option": "approve", "confidence": 0.9},
            {"agent_id": "agent_2", "option": "approve", "confidence": 0.8},
            {"agent_id": "agent_3", "option": "reject", "confidence": 0.7},
        ],
    },
))
```

### Resolución de conflictos

```python
result = await engine.execute(AgentTask(
    task_id="task_2",
    agent_id="consensus_1",
    task_type="consensus",
    input_data={
        "action": "resolve",
        "case": {
            "session_id": "session_123",
            "type": "answer_conflict",
            "responses": [
                {"agent_id": "agent_1", "response": {"answer": "A"}},
                {"agent_id": "agent_2", "response": {"answer": "B"}},
            ],
        },
        "strategy": "weighted",
    },
))
```

---

## Integración con EPIC 7

```
EPIC 7 (Collaboration) ──► EPIC 8 (Consensus)
         │
         ├── ContextSharing ──► VotingEngine
         ├── AgentMessaging ──► ConflictResolver
         └── CollaborationBus ──► ConsensusBuilder
```

---

## Concatenación

```
EPIC 7 (Collaboration) ──► EPIC 8 (Consensus Engine)
EPIC 1 (Orchestrator) ──► EPIC 8 (orquesta)
EPIC 8 ──► EPIC 9 (Agent Memory Engine)
EPIC 12 (Clinical Context) ──► EPIC 8 (provee contexto)
EPIC 13 (Evidence) ──► EPIC 8 (provee evidencia)
EPIC 14 (Uncertainty) ──► EPIC 8 (provee incertidumbre)
```

---

## Estado

**✅ ACTUALIZADO v2.0**

- Voting Engine: ✅ COMPLETO
- Deliberative Consensus Module: ✅ AÑADIDO v2.0
  - DeliberationEngine
  - ArgumentationEngine
  - ExpertWeighting
  - DissentingOpinionPreserver

Este EPIC cierra parcialmente el gap de Deliberative Consensus (25/100 → 80/100).

---

## Próximos Pasos

- EPIC 9: Agent Memory Engine (v2.0)
- EPIC 10: Agent Learning & Optimization (v2.0)
- PHASE 6: Hospital Digital

---

*EREN PHASE 5 - EPIC 8 v2.0*
*Architecture Board - 2026-07-24*
