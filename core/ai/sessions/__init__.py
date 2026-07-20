"""EREN AI Sessions - Session Management Module.

Módulo de gestión de sesiones del AI Core.

## Características

- Session Context
- Token Budget
- Conversation Limits
- Expiration
- Resume Session

## Uso

```python
from core.ai.sessions import (
    SessionManager,
    SessionContext,
    ConversationLimit,
    TokenBudget,
)

# Crear manager
manager = SessionManager(
    default_budget=100000,
    default_limits=ConversationLimit(
        max_messages_per_session=100,
        session_timeout_minutes=30,
    ),
)

# Crear sesión
session = manager.create_session(
    user_id="user-123",
    tenant_id="tenant-456",
)

# Agregar mensajes
manager.add_message(
    session_id=session.id,
    role="user",
    content="Hola",
    tokens=10,
)

manager.add_message(
    session_id=session.id,
    role="assistant",
    content="Hola, ¿en qué puedo ayudarte?",
    tokens=20,
)

# Verificar presupuesto
budget = manager.get_budget(session.id)
print(f"Tokens restantes: {budget.remaining}")

# Pausar sesión
manager.pause_session(session.id)

# Reanudar sesión
manager.resume_session(session.id)

# Cerrar sesión
manager.close_session(session.id)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                  SESSION MANAGER                                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Session Store                               │ │
│  │          sessions: dict[str, Session]                    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Session Lifecycle                           │ │
│  │     create → pause → resume → expire → close            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Token Budget                               │ │
│  │       total_limit, used, daily, warnings                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Conversation Limits                        │ │
│  │    max_messages, timeout, max_length, max_age            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```
"""

from core.ai.sessions.models import (
    ConversationLimit,
    Message,
    Session,
    SessionContext,
    SessionEvent,
    SessionStats,
    SessionStatus,
    TokenBudget,
)
from core.ai.sessions.manager import SessionManager

__version__ = "1.0.0"

__all__ = [
    # Models
    "Session",
    "SessionContext",
    "SessionEvent",
    "SessionStats",
    "SessionStatus",
    "Message",
    "TokenBudget",
    "ConversationLimit",
    # Manager
    "SessionManager",
]
