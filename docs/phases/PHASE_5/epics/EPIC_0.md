# EPIC 0: Multi-Agent Architecture Foundation

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Construir toda la infraestructura base del sistema multiagente.

---

## Responsabilidad

**Shared Kernel de la FASE 5.**

EPIC 0 proporciona:

- **Contratos**: Interfaces y protocolos base para todos los agentes
- **Tipos Compartidos**: DTOs, enums, value objects
- **Sistema de Mensajería**: Protocolos de comunicación entre agentes
- **Ciclo de Vida**: Estados y transiciones de agentes
- **Registro**: AgentRegistry para gestión centralizada
- **Eventos**: Sistema de eventos para comunicación asíncrona
- **Contexto**: AgentContext y AgentSession para estado compartido

---

## Dependencias

### Fases
- **FASE 1**: Business Domain (Device, Incident, Knowledge, Asset)
- **FASE 2**: Cognitive OS (AI Kernel, Memory, Context)
- **FASE 3**: Clinical Intelligence (Reasoning, Evidence, Decision)
- **FASE 4**: Knowledge Platform (RAG, Embeddings, Governance)

### EPICs
- Ninguno (este es el EPIC base)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EPIC 0: Multi-Agent Architecture Foundation          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      AGENT CONTRACTS                              │   │
│  │  ├── IAgent ───────────────────────────────────────────────────────│   │
│  │  ├── IAgentOrchestrator ──────────────────────────────────────────│   │
│  │  ├── IAgentRegistry ──────────────────────────────────────────────│   │
│  │  ├── IMessageBroker ──────────────────────────────────────────────│   │
│  │  └── ILifecycleManager ───────────────────────────────────────────│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       AGENT TYPES                                 │   │
│  │  ├── AgentState (IDLE, RUNNING, WAITING, COMPLETED, FAILED)       │   │
│  │  ├── AgentType (BIOMEDICAL, DIAGNOSTIC, KNOWLEDGE, RESEARCH)      │   │
│  │  ├── AgentCapability (DIAGNOSE, RESEARCH, PLAN, COLLABORATE)     │   │
│  │  ├── AgentPriority (CRITICAL, HIGH, MEDIUM, LOW)                  │   │
│  │  └── MessageType (REQUEST, RESPONSE, NOTIFICATION, ERROR)         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      DOMAIN OBJECTS                               │   │
│  │  ├── Agent ──────────────────────────────── Base agent entity     │   │
│  │  ├── AgentTask ─────────────────────────── Task definition        │   │
│  │  ├── AgentMessage ───────────────────────── Inter-agent message    │   │
│  │  ├── AgentContext ───────────────────────── Shared context        │   │
│  │  ├── AgentCapability ─────────────────────── Agent capability      │   │
│  │  └── AgentSession ────────────────────────── Agent session        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      BASE IMPLEMENTATIONS                         │   │
│  │  ├── BaseAgent ──────────────────────────── Abstract base class   │   │
│  │  ├── AgentRegistry ──────────────────────── Agent registration   │   │
│  │  ├── AgentLifecycleManager ───────────────── Lifecycle manager    │   │
│  │  ├── AgentFactory ───────────────────────── Agent factory        │   │
│  │  ├── EventBusAdapter ─────────────────────── Event bus adapter   │   │
│  │  └── InMemoryMessageBroker ───────────────── In-memory broker   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         GATEWAYS                                  │   │
│  │  ├── PHASE1Gateway ────────────────────────► PHASE_1 Contexts   │   │
│  │  ├── PHASE2Gateway ────────────────────────► PHASE_2 AI Core    │   │
│  │  ├── PHASE3Gateway ────────────────────────► PHASE_3 Intellig.  │   │
│  │  └── PHASE4Gateway ────────────────────────► PHASE_4 Knowledge  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/foundation/
├── __init__.py                    # Módulo principal (exports)
├── contracts/
│   └── __init__.py               # IAgent, IAgentOrchestrator, etc.
├── events/
│   └── __init__.py               # AgentEvent, AgentEventType, etc.
├── messaging/
│   └── __init__.py               # AgentMessage, MessageBroker, etc.
├── lifecycle/
│   └── __init__.py               # AgentLifecycleManager, AgentState
├── registry/
│   └── __init__.py               # AgentRegistry
├── context/
│   └── __init__.py               # AgentContext, AgentSession
├── types/
│   └── __init__.py               # AgentType, AgentCapability, etc.
└── gateways/
    └── __init__.py               # PHASE1-4 Gateways
```

---

## Componentes

### 1. Agent Contracts (Interfaces)

```python
class IAgent(Protocol):
    """Protocolo base para agentes."""
    
    @property
    def agent_id(self) -> str: ...
    
    @property
    def agent_type(self) -> AgentType: ...
    
    @property
    def state(self) -> AgentState: ...
    
    async def initialize(self) -> None: ...
    
    async def execute(self, task: AgentTask) -> AgentResult: ...
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage: ...
    
    async def shutdown(self) -> None: ...


class IAgentRegistry(Protocol):
    """Protocolo para registro de agentes."""
    
    async def register(self, agent: IAgent) -> bool: ...
    
    async def unregister(self, agent_id: str) -> bool: ...
    
    async def get(self, agent_id: str) -> Optional[IAgent]: ...
    
    async def get_by_type(self, agent_type: AgentType) -> list[IAgent]: ...
    
    async def get_by_capability(self, capability: AgentCapability) -> list[IAgent]: ...


class IMessageBroker(Protocol):
    """Protocolo para broker de mensajes."""
    
    async def send(self, message: AgentMessage) -> bool: ...
    
    async def subscribe(self, agent_id: str, topics: list[str]) -> bool: ...
    
    async def unsubscribe(self, agent_id: str, topics: list[str]) -> bool: ...
    
    async def receive(self, agent_id: str, timeout: int) -> Optional[AgentMessage]: ...


class ILifecycleManager(Protocol):
    """Protocolo para gestión de ciclo de vida."""
    
    async def create_agent(self, agent_type: AgentType, config: dict) -> str: ...
    
    async def destroy_agent(self, agent_id: str) -> bool: ...
    
    async def get_state(self, agent_id: str) -> AgentState: ...
    
    async def transition(self, agent_id: str, new_state: AgentState) -> bool: ...
```

### 2. Agent Types

| Enum | Descripción |
|------|-------------|
| `AgentState` | IDLE, INITIALIZING, RUNNING, WAITING, COMPLETED, FAILED, STOPPED |
| `AgentType` | BIOMEDICAL, DIAGNOSTIC, KNOWLEDGE, RESEARCH, PLANNING, ORCHESTRATOR |
| `AgentCapability` | DIAGNOSE, RESEARCH, PLAN, EXECUTE, COLLABORATE, VALIDATE |
| `AgentPriority` | CRITICAL, HIGH, MEDIUM, LOW |
| `MessageType` | REQUEST, RESPONSE, NOTIFICATION, ERROR, HEARTBEAT |

### 3. Domain Objects

| Object | Descripción |
|--------|-------------|
| `Agent` | Entidad base de agente con id, type, state, capabilities |
| `AgentTask` | Definición de tarea con input, expected_output, constraints |
| `AgentMessage` | Mensaje entre agentes con sender, receiver, content, type |
| `AgentContext` | Contexto compartido entre agentes en una sesión |
| `AgentCapability` | Capacidad específica de un agente |
| `AgentSession` | Sesión de agente con historial de interacciones |

### 4. Base Implementations

| Clase | Descripción |
|-------|-------------|
| `BaseAgent` | Clase base abstracta para todos los agentes |
| `AgentRegistry` | Registro centralizado de agentes |
| `AgentLifecycleManager` | Gestor de ciclo de vida de agentes |
| `AgentFactory` | Fábrica para crear agentes por tipo |
| `EventBusAdapter` | Adapter para event bus |
| `InMemoryMessageBroker` | Broker de mensajes en memoria |

### 5. Gateways

```python
class PHASE1Gateway:
    """Acceso a PHASE 1 - Business Domain"""
    async def get_device_context(self, device_id: str) -> DeviceContext: ...
    async def get_incident_context(self, incident_id: str) -> IncidentContext: ...
    async def get_knowledge_context(self, query: str) -> KnowledgeContext: ...

class PHASE2Gateway:
    """Acceso a PHASE 2 - Cognitive OS"""
    async def get_embeddings(self, texts: list[str]) -> list[EmbeddingVector]: ...
    async def retrieve_context(self, query: str) -> CognitiveContext: ...

class PHASE3Gateway:
    """Acceso a PHASE 3 - Clinical Intelligence"""
    async def validate_with_reasoning(self, claim: str, evidence: list) -> ReasoningResult: ...
    async def check_safety(self, content: str) -> SafetyResult: ...

class PHASE4Gateway:
    """Acceso a PHASE 4 - Knowledge Platform"""
    async def search_knowledge(self, query: KnowledgeQuery) -> RetrievalResult: ...
    async def get_governed_knowledge(self, asset_id: str) -> KnowledgeAsset: ...
```

---

## Uso

### Crear un agente básico

```python
from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentCapability,
    AgentTask,
    AgentRegistry,
)

class MyAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.BIOMEDICAL,
            capabilities=[
                AgentCapability.DIAGNOSE,
                AgentCapability.RESEARCH,
            ],
        )
    
    async def _execute_impl(self, task: AgentTask) -> dict:
        # Implementar lógica específica
        return {"result": "processed"}

# Registrar agente
registry = AgentRegistry()
agent = MyAgent("biomedical_1")
await registry.register(agent)

# Ejecutar tarea
task = AgentTask(
    task_id="task_1",
    agent_id="biomedical_1",
    input={"query": "analyze_device"},
)
result = await agent.execute(task)
```

### Comunicación entre agentes

```python
from core.PHASE_5.foundation import AgentMessage, MessageType

# Enviar mensaje
message = AgentMessage(
    sender="orchestrator_1",
    receiver="biomedical_1",
    type=MessageType.REQUEST,
    content={"action": "diagnose", "device_id": "dev_123"},
)
await message_broker.send(message)

# Recibir respuesta
response = await message_broker.receive("orchestrator_1", timeout=30)
```

---

## Flujo de Mensajería

```
┌─────────────┐      AgentMessage       ┌─────────────┐
│   Agent A   │ ───────────────────────► │   Agent B   │
│  (Sender)   │                           │ (Receiver)  │
└─────────────┘                           └─────────────┘
       ▲                                        │
       │              ┌──────────────┐          │
       │              │ MessageBroker│          │
       └──────────────│  (Hub)      │──────────┘
                      └──────────────┘
```

---

## Concatenación

```
FASE 1 ──► PHASE1Gateway ──► Foundation
FASE 2 ──► PHASE2Gateway ──► Foundation
FASE 3 ──► PHASE3Gateway ──► Foundation
FASE 4 ──► PHASE4Gateway ──► Foundation
Foundation ◄── EPIC 1-11
```

---

## Eventos del Sistema

| Evento | Descripción |
|--------|-------------|
| `AGENT_REGISTERED` | Agente registrado |
| `AGENT_UNREGISTERED` | Agente desregistrado |
| `AGENT_INITIALIZED` | Agente inicializado |
| `AGENT_STARTED` | Agente iniciado |
| `AGENT_COMPLETED` | Agente completó tarea |
| `AGENT_FAILED` | Agente falló |
| `AGENT_MESSAGE_SENT` | Mensaje enviado |
| `AGENT_MESSAGE_RECEIVED` | Mensaje recibido |

---

## Estado

**🚧 EN PROGRESO**

Implementación en curso.

---

## Hacia EPIC 1

EPIC 0 provee la infraestructura base para EPIC 1 (Agent Orchestrator):

```
Foundation ──► EPIC 1 (Orchestrator)
     │
     ├── AgentRegistry
     ├── BaseAgent
     ├── AgentContext
     ├── AgentMessage
     └── EventBusAdapter
```

---

*EREN PHASE 5 - EPIC 0*
*Architecture Board - 2026-07-23*
