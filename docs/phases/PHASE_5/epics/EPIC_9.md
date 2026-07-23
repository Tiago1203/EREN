# EPIC 9: Agent Memory Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Dar memoria individual y colectiva a los agentes.**

EPIC 9 es responsable de:
- Persistir experiencias de agentes
- Gestionar contexto de conversaciones
- Compartir memorias entre agentes
- Sincronizar memorias colectivas

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
│                   EPIC 9: Agent Memory Engine                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      AGENT MEMORY                                    │   │
│  │  ├── EpisodicMemory ─────────────────── Memoria episódica        │   │
│  │  ├── SharedMemory ────────────────────── Memoria compartida       │   │
│  │  ├── LongTermMemory ──────────────────── Memoria a largo plazo     │   │
│  │  ├── ConversationMemory ─────────────── Memoria de conversación  │   │
│  │  └── MemorySynchronizer ──────────────── Sincronizador          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── MemoryRecord ───────────────────── Registro de memoria       │   │
│  │  ├── ConversationContext ─────────────── Contexto de conv.      │   │
│  │  └── AgentExperience ─────────────────── Experiencia de agente   │   │
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
│   └── __init__.py              # EpisodicMemory, SharedMemory, etc.
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
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 10: Agent Learning & Optimization
- EPIC 11: Multi-Agent Governance

---

*EREN PHASE 5 - EPIC 9*
*Architecture Board - 2026-07-23*
