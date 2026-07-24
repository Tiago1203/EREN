# EPIC 9: Agent Memory Engine

*Versión: 2.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Dar memoria individual y colectiva a los agentes con modelo cognitivo completo.**

EPIC 9 es responsable de:
- Persistir experiencias de agentes
- Gestionar contexto de conversaciones
- Compartir memorias entre agentes
- Sincronizar memorias colectivas
- **Memoria episódica** *(NUEVO v2.0)*
- **Memoria semántica** *(NUEVO v2.0)*
- **Memoria procedimental** *(NUEVO v2.0)*
- **Memoria de trabajo** *(NUEVO v2.0)*

---

## Dependencias

### Fases
- **FASE 2**: Cognitive Operating System (Memory)
- **FASE 4**: Knowledge Platform

### EPICs
- **EPIC 8**: Consensus Engine (lo invoca)
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 9: Agent Memory Engine (v2.0)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      COGNITIVE MEMORY MODEL (NUEVO v2.0)           │   │
│  │  ├── EpisodicMemory ─────────────────── Memoria episódica        │   │
│  │  ├── SemanticMemory ──────────────────── Memoria semántica        │   │
│  │  ├── ProceduralMemory ────────────────── Memoria procedimental   │   │
│  │  ├── WorkingMemory ───────────────────── Memoria de trabajo      │   │
│  │  └── LongTermMemory ──────────────────── Memoria a largo plazo     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      AGENT MEMORY                                    │   │
│  │  ├── SharedMemory ────────────────────── Memoria compartida       │   │
│  │  ├── ConversationMemory ─────────────── Memoria de conversación  │   │
│  │  └── MemorySynchronizer ──────────────── Sincronizador          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── MemoryRecord ───────────────────── Registro de memoria       │   │
│  │  ├── ConversationContext ─────────────── Contexto de conv.      │   │
│  │  ├── AgentExperience ─────────────────── Experiencia de agente   │   │
│  │  ├── CognitiveMemory ──────────────────── Memoria cognitiva     │   │
│  │  └── MemoryConsolidation ─────────────── Consolidación de memoria│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic9_memory/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # MemoryRecord, ConversationContext, etc.
├── engines/
│   ├── __init__.py              # EpisodicMemory, SharedMemory, etc.
│   └── cognitive/                # Cognitive Memory Model (NUEVO v2.0)
│       ├── __init__.py          # SemanticMemory, ProceduralMemory, etc.
│       ├── semantic_memory.py    # Semantic memory
│       ├── procedural_memory.py  # Procedural memory
│       ├── working_memory.py     # Working memory
│       └── consolidation.py      # Memory consolidation
└── agent/
    └── __init__.py              # AgentMemory
```

---

## Componentes

### 1. AgentMemory

Motor principal de memoria.

```python
class AgentMemory(BaseAgent):
    """Motor de memoria para agentes."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de memoria."""
```

**Acciones:**
- `store`: Almacenar memoria
- `retrieve`: Recuperar memoria
- `experience`: Gestionar experiencias
- `conversation`: Gestionar conversación
- `share`: Compartir memoria
- `sync`: Sincronizar memorias

### 2. EpisodicMemory

Memoria episódica - eventos específicos.

```python
class EpisodicMemory:
    """Memoria episódica."""
    
    async def store(
        self,
        agent_id: str,
        content: str,
        memory_type: MemoryType,
    ) -> MemoryRecord:
        """Almacena un evento."""
    
    async def retrieve(
        self,
        agent_id: str,
        session_id: str | None,
    ) -> EpisodicResult:
        """Recupera eventos."""
```

### 3. SharedMemory

Memoria compartida entre agentes.

```python
class SharedMemory:
    """Memoria compartida."""
    
    async def share(
        self,
        agent_id: str,
        record: MemoryRecord,
    ) -> SharedResult:
        """Comparte una memoria."""
    
    async def get_shared(
        self,
        memory_type: MemoryType | None,
    ) -> list[MemoryRecord]:
        """Obtiene memorias compartidas."""
```

### 4. LongTermMemory

Memoria a largo plazo - experiencias.

```python
class LongTermMemory:
    """Memoria a largo plazo."""
    
    async def store_experience(
        self,
        agent_id: str,
        description: str,
        outcome: ExperienceOutcome,
    ) -> AgentExperience:
        """Almacena una experiencia."""
    
    async def retrieve_experiences(
        self,
        agent_id: str,
        scenario: str | None,
    ) -> LongTermResult:
        """Recupera experiencias."""
```

### 5. ConversationMemory

Memoria de conversaciones.

```python
class ConversationMemory:
    """Memoria de conversación."""
    
    async def create_context(
        self,
        session_id: str,
        participants: list[str],
    ) -> ConversationContext:
        """Crea un contexto de conversación."""
    
    async def add_message(
        self,
        context_id: str,
        sender_id: str,
        content: str,
    ) -> Message:
        """Agrega un mensaje."""
```

### 6. MemorySynchronizer

Sincronizador de memorias.

```python
class MemorySynchronizer:
    """Sincronizador de memoria."""
    
    async def sync_agent(
        self,
        agent_id: str,
        shared_memory: SharedMemory,
        episodic_memory: EpisodicMemory,
    ) -> SyncResult:
        """Sincroniza memorias de un agente."""
```

### 7. SemanticMemory (NUEVO v2.0)

Memoria semántica - conocimiento general.

```python
class SemanticMemory:
    """Memoria semántica."""
    
    async def store_concept(
        self,
        concept: Concept,
        embeddings: list[float],
    ) -> SemanticRecord:
        """Almacena concepto semántico."""
    
    async def retrieve_concepts(
        self,
        query: str,
        threshold: float = 0.7,
    ) -> list[SemanticRecord]:
        """Recupera conceptos relacionados."""
```

### 8. ProceduralMemory (NUEVO v2.0)

Memoria procedimental - habilidades y procedimientos.

```python
class ProceduralMemory:
    """Memoria procedimental."""
    
    async def store_procedure(
        self,
        procedure: Procedure,
        steps: list[ProcedureStep],
    ) -> ProceduralRecord:
        """Almacena procedimiento."""
    
    async def retrieve_procedure(
        self,
        goal: str,
        context: dict,
    ) -> Procedure | None:
        """Recupera procedimiento aplicable."""
```

### 9. WorkingMemory (NUEVO v2.0)

Memoria de trabajo - información activa.

```python
class WorkingMemory:
    """Memoria de trabajo."""
    
    async def update(
        self,
        agent_id: str,
        items: list[WorkingItem],
    ) -> WorkingMemoryState:
        """Actualiza memoria de trabajo."""
    
    async def get_active(
        self,
        agent_id: str,
    ) -> list[WorkingItem]:
        """Obtiene items activos."""
    
    async def clear(
        self,
        agent_id: str,
    ) -> None:
        """Limpia memoria de trabajo."""
```

### 10. MemoryConsolidation (NUEVO v2.0)

Consolidación de memoria episódica a largo plazo.

```python
class MemoryConsolidation:
    """Consolidación de memoria."""
    
    async def consolidate(
        self,
        agent_id: str,
        episodic_records: list[EpisodicRecord],
    ) -> ConsolidationResult:
        """Consolida memorias."""
    
    async def extract_patterns(
        self,
        records: list[EpisodicRecord],
    ) -> list[MemoryPattern]:
        """Extrae patrones de memorias."""
```

---

## Domain Objects

### MemoryRecord

```python
@dataclass
class MemoryRecord:
    """Registro de memoria."""
    record_id: str
    agent_id: str
    memory_type: MemoryType
    content: str
    
    def access(self) -> None:
        """Registra acceso."""
    
    def is_expired(self) -> bool:
        """Verifica expiración."""
```

### ConversationContext

```python
@dataclass
class ConversationContext:
    """Contexto de conversación."""
    context_id: str
    participants: list[str]
    messages: list[Message]
    
    def add_message(self, message: Message) -> None:
        """Agrega mensaje."""
```

### AgentExperience

```python
@dataclass
class AgentExperience:
    """Experiencia de agente."""
    experience_id: str
    description: str
    outcome: ExperienceOutcome
    lessons_learned: list[str]
    
    def add_lesson(self, lesson: str) -> None:
        """Agrega lección."""
    
    def is_applicable(self, scenario: str) -> bool:
        """Verifica aplicabilidad."""
```

---

## Tipos de Memoria

| Tipo | Descripción |
|------|-------------|
| `EPISODIC` | Eventos específicos |
| `SEMANTIC` | Conocimiento general |
| `PROCEDURAL` | Habilidades |
| `WORKING` | Corto plazo |
| `SHARED` | Entre agentes |

---

## Uso

### Almacenar memoria

```python
from core.PHASE_5.epic9_memory import (
    AgentMemory,
    AgentMemoryConfig,
)

memory = AgentMemory(
    agent_id="memory_1",
    config=AgentMemoryConfig(),
)

result = await memory.execute(AgentTask(
    task_id="task_1",
    agent_id="memory_1",
    task_type="memory",
    input_data={
        "action": "store",
        "agent_id": "agent_1",
        "content": "Diagnosed X device failure",
        "type": "episodic",
        "importance": "high",
    },
))
```

### Recuperar experiencias

```python
result = await memory.execute(AgentTask(
    task_id="task_2",
    agent_id="memory_1",
    task_type="memory",
    input_data={
        "action": "experience",
        "operation": "retrieve",
        "agent_id": "agent_1",
        "scenario": "device_repair",
    },
))
```

---

## Integración con FASE 2 y FASE 4

```
FASE 2 (Memory) ─────────────────┐
                                 │
FASE 4 (Knowledge) ──────────────┼──► EPIC 9 (Agent Memory)
                                 │
EPIC 8 (Consensus) ──────────────┘
```

---

## Concatenación

```
EPIC 8 (Consensus) ──► EPIC 9 (Agent Memory Engine)
EPIC 1 (Orchestrator) ──► EPIC 9 (orquesta)
EPIC 9 ──► EPIC 10 (Agent Learning & Optimization)
EPIC 9 ──► EPIC 12 (provee memoria episódica)
EPIC 9 ──► EPIC 13 (provee memoria de conocimiento)
```

---

## Estado

**✅ ACTUALIZADO v2.0**

- Agent Memory base: ✅ COMPLETO
- Cognitive Memory Model: ✅ AÑADIDO v2.0
  - SemanticMemory
  - ProceduralMemory
  - WorkingMemory
  - MemoryConsolidation

Este EPIC cierra parcialmente el gap de Cognitive Memory (35/100 → 80/100).

---

## Próximos Pasos

- EPIC 10: Agent Learning & Optimization (v2.0)
- EPIC 11: Multi-Agent Governance
- PHASE 6: Hospital Digital

---

*EREN PHASE 5 - EPIC 9 v2.0*
*Architecture Board - 2026-07-24*
