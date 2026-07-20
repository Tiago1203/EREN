"""EREN AI Conversation - Conversation Controller Module.

Módulo de gestión de conversaciones del AI Core.

## Componentes

- **models**: Modelos de datos (Conversation, Session, Message, etc.)
- **events**: Sistema de eventos
- **lifecycle**: Gestión del ciclo de vida
- **repository**: Repositorio abstracto e implementación
- **controller**: Controlador principal

## Uso

```python
from core.ai.conversation import ConversationController

# Create controller
controller = ConversationController()

# Create conversation
conversation = controller.create_conversation(
    tenant_id="tenant-1",
    title="Support Chat",
    created_by="user-1",
)

# Add message
message = controller.add_message(
    conversation_id=conversation.id,
    role="user",
    content="Hello!",
    created_by="user-1",
)

# Start session
session = controller.start_session(
    conversation_id=conversation.id,
    tenant_id="tenant-1",
    user_id="user-1",
)

# Get messages
messages = controller.list_messages(conversation.id)
```

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│              CONVERSATION CONTROLLER                                │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                 Lifecycle Manager                        │ │
│  │    (create, update, close, pause, resume, archive)       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │   Session    │ │   Message    │ │     Participant      │ │
│  │  Lifecycle   │ │  Management  │ │     Management       │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Repository                             │ │
│  │           (Abstract + InMemory Implementation)            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Event Dispatcher                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```
"""

from core.ai.conversation.controller import ConversationController
from core.ai.conversation.events import (
    ConversationEvent,
    ConversationEventDispatcher,
    ConversationEventType,
    get_event_dispatcher,
    reset_event_dispatcher,
)
from core.ai.conversation.lifecycle import ConversationLifecycle, SessionLifecycle
from core.ai.conversation.models import (
    Conversation,
    ConversationContext,
    ConversationMetadata,
    ConversationMessage,
    ConversationParticipant,
    ConversationSession,
    ConversationState,
    ConversationType,
)
from core.ai.conversation.repository import (
    ConversationRepository,
    InMemoryConversationRepository,
)

__version__ = "1.0.0"

__all__ = [
    # Controller
    "ConversationController",
    # Lifecycle
    "ConversationLifecycle",
    "SessionLifecycle",
    # Models
    "Conversation",
    "ConversationContext",
    "ConversationMetadata",
    "ConversationMessage",
    "ConversationParticipant",
    "ConversationSession",
    "ConversationState",
    "ConversationType",
    # Repository
    "ConversationRepository",
    "InMemoryConversationRepository",
    # Events
    "ConversationEvent",
    "ConversationEventDispatcher",
    "ConversationEventType",
    "get_event_dispatcher",
    "reset_event_dispatcher",
]
