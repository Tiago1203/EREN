# EPIC 7: Collaboration Engine

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Permitir que los agentes trabajen juntos.**

EPIC 7 es responsable de:
- Gestionar colaboración entre agentes
- Intercambio de contexto
- Sincronización
- Mensajería entre agentes
- Workspaces compartidos

---

## Dependencias

### EPICs
- **EPIC 1**: Agent Orchestrator (lo invoca)
- **EPIC 2-6**: Agentes que colaboran

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 7: Collaboration Engine                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  COLLABORATION ENGINE                              │   │
│  │  ├── ContextSharing ────────────────── Compartición de contexto   │   │
│  │  ├── AgentMessaging ────────────────── Mensajería entre agentes  │   │
│  │  ├── CollaborationBus ──────────────── Bus de colaboración     │   │
│  │  └── SharedWorkspace ───────────────── Workspace compartido      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                 │   │
│  │  ├── SharedContext ─────────────────── Contexto compartido       │   │
│  │  ├── CollaborationSession ─────────── Sesión de colaboración   │   │
│  │  └── AgentConversation ──────────────── Conversación            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic7_collaboration/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # SharedContext, CollaborationSession, etc.
├── engines/
│   └── __init__.py              # ContextSharing, AgentMessaging, etc.
└── agent/
    └── __init__.py              # CollaborationEngine
```

---

## Componentes

### 1. CollaborationEngine

Motor principal de colaboración.

```python
class CollaborationEngine(BaseAgent):
    """Motor de colaboración entre agentes."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de colaboración."""
```

**Operaciones:**
- `session`: Gestión de sesiones
- `context`: Compartición de contexto
- `message`: Mensajería
- `bus`: Publicación/suscripción
- `workspace`: Workspaces compartidos

### 2. ContextSharing

Compartición de contexto entre agentes.

```python
class ContextSharing:
    """Motor de compartición de contexto."""
    
    async def share_context(
        self,
        session_id: str,
        source_agent_id: str,
        entries: list[tuple[str, Any, ContextType]],
    ) -> SharingResult:
        """Comparte contexto con otros agentes."""
    
    async def get_context(
        self,
        session_id: str,
        key: str | None,
    ) -> SharedContext | None:
        """Obtiene contexto compartido."""
```

**Tipos de contexto:**
- `TASK`: Contexto de tarea
- `RESULT`: Contexto de resultado
- `STATE`: Estado del agente
- `KNOWLEDGE`: Conocimiento
- `PLAN`: Plan
- `DECISION`: Decisión

### 3. AgentMessaging

Mensajería entre agentes.

```python
class AgentMessaging:
    """Motor de mensajería entre agentes."""
    
    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
    ) -> MessageResult:
        """Envía un mensaje a otro agente."""
    
    async def get_messages(
        self,
        agent_id: str,
        unread_only: bool,
    ) -> list[Message]:
        """Obtiene mensajes para un agente."""
```

**Tipos de mensaje:**
- `REQUEST`: Solicitud
- `RESPONSE`: Respuesta
- `NOTIFICATION`: Notificación
- `QUERY`: Consulta
- `COMMAND`: Comando
- `EVENT`: Evento

### 4. CollaborationBus

Bus de colaboración (pub/sub).

```python
class CollaborationBus:
    """Bus de colaboración."""
    
    async def publish(
        self,
        topic: str,
        sender_id: str,
        content: Any,
    ) -> BusMessage:
        """Publica un mensaje en el bus."""
    
    async def subscribe(
        self,
        agent_id: str,
        topic: str,
    ) -> bool:
        """Suscribe un agente a un topic."""
```

### 5. SharedWorkspace

Workspace compartido entre agentes.

```python
class SharedWorkspace:
    """Workspace compartido."""
    
    async def create_workspace(
        self,
        workspace_id: str,
        owner_id: str,
    ) -> dict:
        """Crea un workspace."""
    
    async def add_artifact(
        self,
        workspace_id: str,
        agent_id: str,
        artifact: dict,
    ) -> bool:
        """Agrega un artefacto."""
```

---

## Domain Objects

### CollaborationSession

```python
@dataclass
class CollaborationSession:
    """Sesión de colaboración."""
    session_id: str
    participants: list[Participant]
    shared_context: SharedContext
    status: SessionStatus
    
    def add_participant(self, agent_id: str, role: str) -> Participant:
        """Agrega un participante."""
    
    def start(self) -> None:
        """Inicia la sesión."""
    
    def complete(self) -> None:
        """Completa la sesión."""
```

### SharedContext

```python
@dataclass
class SharedContext:
    """Contexto compartido."""
    context_id: str
    entries: list[ContextEntry]
    
    def add_entry(self, entry: ContextEntry) -> None:
        """Agrega una entrada."""
    
    def get_entry(self, key: str) -> ContextEntry | None:
        """Obtiene una entrada."""
```

---

## Uso

### Crear sesión de colaboración

```python
from core.PHASE_5.epic7_collaboration import (
    CollaborationEngine,
    CollaborationEngineConfig,
)

# Crear motor
engine = CollaborationEngine(
    agent_id="collab_1",
    config=CollaborationEngineConfig(),
)

# Crear sesión
result = await engine.execute(AgentTask(
    task_id="task_1",
    agent_id="collab_1",
    task_type="collaboration",
    input_data={
        "action": "session",
        "operation": "create",
        "session_type": "parallel",
        "participants": ["agent_1", "agent_2", "agent_3"],
    },
))
```

### Compartir contexto

```python
result = await engine.execute(AgentTask(
    task_id="task_2",
    agent_id="collab_1",
    task_type="collaboration",
    input_data={
        "action": "context",
        "operation": "share",
        "session_id": "session_123",
        "agent_id": "agent_1",
        "entries": [
            ("diagnosis_result", {"disease": "X"}, "result"),
            ("confidence", 0.95, "state"),
        ],
    },
))
```

### Publicar evento

```python
result = await engine.execute(AgentTask(
    task_id="task_3",
    agent_id="collab_1",
    task_type="collaboration",
    input_data={
        "action": "bus",
        "operation": "publish",
        "topic": "task.completed",
        "sender_id": "agent_1",
        "content": {"task_id": "task_123", "status": "success"},
    },
))
```

---

## Integración con EPICs

```
EPIC 2 (Biomedical) ──┐
EPIC 3 (Diagnostic) ───┼──► EPIC 7 (Collaboration)
EPIC 4 (Knowledge) ────┤
EPIC 5 (Research) ─────┤
EPIC 6 (Planning) ─────┘
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `session.created` | Sesión creada |
| `session.started` | Sesión iniciada |
| `session.completed` | Sesión completada |
| `context.shared` | Contexto compartido |
| `message.sent` | Mensaje enviado |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `SessionNotFoundError` | Sesión no encontrada |
| `MaxParticipantsError` | Máximo de participantes |
| `ContextExpiredError` | Contexto expirado |

---

## Concatenación

```
EPIC 6 (Planning) ──► EPIC 7 (Collaboration Engine)
EPIC 1 (Orchestrator) ──► EPIC 7 (orquesta)
EPIC 7 ──► EPIC 8 (Consensus Engine)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 8: Consensus Engine
- EPIC 9: Agent Memory Engine

---

*EREN PHASE 5 - EPIC 7*
*Architecture Board - 2026-07-23*
