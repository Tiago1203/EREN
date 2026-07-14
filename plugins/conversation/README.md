# Conversation Memory Plugin

> **EREN's first REAL memory system.** Provides conversation memory capability for EREN OS.

This plugin implements `BaseMemoryInterface` and registers with the Plugin Framework to provide conversation memory functionality.

## Features

- ✅ Store conversation history
- ✅ Retrieve recent conversations
- ✅ Search by text
- ✅ Search by date
- ✅ Search by session
- ✅ Configurable context window
- ✅ Configurable TTL
- ✅ Automatic deletion
- ✅ Multi-user support
- ✅ Multi-session support

## Architecture

```
ExecutionCoordinator
        │
        ▼
MemoryEngine
        │
        ▼
MemoryCoordinator
        │
        ▼
Conversation Memory Plugin
        │
        ▼
SQLite (dev) → PostgreSQL (production)
```

## Usage

### Direct Usage

```python
from plugins.conversation import (
    ConversationMemoryPlugin,
    ConversationEntry,
    ConversationRole,
)

# Create plugin
plugin = ConversationMemoryPlugin()
plugin.initialize({"database_path": "conversations.db"})

# Get provider for Memory Coordinator
provider = plugin.memory_provider

# Or use repository directly
from plugins.conversation import ConversationRepository, ConversationConfiguration

config = ConversationConfiguration()
repo = ConversationRepository(config)

# Create conversation
metadata = ConversationMetadata(
    conversation_id="conv-123",
    user_id="user-1",
    session_id="session-1",
)
repo.create_conversation(metadata)

# Add entry
entry = ConversationEntry(
    entry_id="entry-1",
    conversation_id="conv-123",
    role=ConversationRole.USER,
    content="Hello, what can you tell me about patients?",
)
repo.add_entry(entry)

# Get entries
entries = repo.get_entries("conv-123")

# Search
results = repo.search(ConversationSearch(query="patient"))
```

### With Memory Coordinator

```python
from core.memory import MemoryCoordinator, MemoryEntry, MemoryType

# Create coordinator
coordinator = MemoryCoordinator()

# Register conversation memory
from plugins.conversation import ConversationMemoryPlugin
plugin = ConversationMemoryPlugin()
plugin.initialize({})
coordinator.registry.register(plugin.memory_provider)

# Write through coordinator
entry = MemoryEntry(
    content="User asked about patient history",
    memory_type=MemoryType.CONVERSATION,
    metadata={
        "conversation_id": "conv-123",
        "role": "user",
    },
)
coordinator.write(entry)

# Read through coordinator
response = coordinator.read("conv-123")
```

## Answering Questions

This plugin enables EREN to answer questions like:

- "¿Qué me preguntaste hace diez minutos?" (What did you ask me ten minutes ago?)
- "¿Cómo se llamaba el paciente del que hablábamos?" (What was the patient's name we were talking about?)
- "¿En qué quedó la conversación anterior?" (What was the previous conversation about?)

## Storage

- **Development**: SQLite (`:memory:` or file)
- **Production**: Replace with PostgreSQL, MySQL, etc. without modifying the Kernel

## Configuration

```python
config = ConversationConfiguration(
    max_context_entries=20,      # Entries in context window
    max_tokens_per_entry=4000,  # Max tokens per entry
    summary_threshold_entries=50,  # Entries before summarization
    summary_max_length=500,     # Max summary length
    ttl_days=30,               # Time to live
    auto_archive_days=7,        # Days before archive
    enable_summarization=True, # Enable summarization
    enable_full_text_search=True,  # Enable FTS
    database_path=":memory:",   # SQLite path
    enable_multi_user=True,     # Multi-user support
    enable_multi_session=True,  # Multi-session support
)
```

## Integration

### With Plugin Framework

```python
from core.plugins import PluginManager

manager = PluginManager()
plugin = manager.load_plugin("plugins/conversation/manifest.json")
manager.activate_plugin("conversation-memory")
```

### With Memory Engine

```python
from core.memory import CognitiveMemoryEngine

engine = CognitiveMemoryEngine()
engine.register_plugin(ConversationMemoryPlugin())
```

## License

EREN OS License
