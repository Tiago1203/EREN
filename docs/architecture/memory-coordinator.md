# Cognitive Memory Coordinator (CMC)

> **Philosophy**: The Coordinator is an INTERNAL component of MemoryEngine responsible ONLY for coordinating access to different memory systems. It does NOT store information.

---

## Overview

The Memory Coordinator is an **internal component** of the MemoryEngine system. It is responsible for:

- **WHERE to read?**
- **WHERE to write?**
- **IN WHAT ORDER?**
- **HOW TO COMBINE results?**
- **WHAT POLICY to apply?**

### Important Distinction

```
┌──────────────────────────────────────────────────────────────────────┐
│                      ExecutionCoordinator                              │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                        MemoryEngine (PUBLIC API)
                               │
                               ▼
                     MemoryCoordinator (INTERNAL)
                               │
                        ┌──────┼──────┐
                        ▼      ▼      ▼
                   Registry Selector Policies
                        │
                        ▼
                 Memory Providers
```

The **ExecutionCoordinator** NEVER accesses the MemoryCoordinator directly. All interaction passes through **MemoryEngine**.

---

## Architecture

### Module Structure

```
core/memory/
├── __init__.py           # Exports
├── base.py              # BaseMemoryInterface (CONTRACT)
├── registry.py          # MemoryRegistry
├── selector.py          # MemorySelector
├── coordinator.py        # MemoryCoordinator (INTERNAL)
├── types.py             # Types and enums
├── exceptions.py        # Exception types
└── README.md           # Quick start
```

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `BaseMemoryInterface` | Contract | Interface for memory providers |
| `MemoryRegistry` | Internal | Manages memory registration |
| `MemorySelector` | Internal | Implements access policies |
| `MemoryCoordinator` | Internal | Coordinates all operations |

---

## Memory Types

| Type | Description | Persistence |
|------|-------------|-------------|
| `WORKING` | Short-term, session-based | Temporary |
| `CONVERSATION` | Current conversation context | Session |
| `EPISODIC` | Past experiences/events | Persistent |
| `SEMANTIC` | General knowledge/facts | Persistent |
| `VECTOR` | Embedding-based search | Persistent |
| `CLINICAL` | Medical/clinical information | Persistent |
| `DEVICE` | Device state/metrics | Real-time |

---

## Access Policies

| Policy | Description | Use Case |
|--------|-------------|----------|
| `FIRST_AVAILABLE` | Use first available memory | Default |
| `LONG_TERM_ONLY` | Only long-term memories | Persistent queries |
| `SHORT_TERM_ONLY` | Only short-term memories | Current context |
| `MERGE_ALL` | Merge results from all | Comprehensive search |
| `READ_ONLY` | No writes | Query operations |
| `WRITE_THROUGH` | Write to all memories | Full persistence |
| `CACHE_FIRST` | Check cache (Working) first | Performance |

---

## The Coordinator Does NOT

❌ Store information  
❌ Know PostgreSQL, Redis, Chroma, Qdrant, etc.  
❌ Implement search algorithms  
❌ Manage persistence  
❌ Know concrete implementations  

## The Coordinator Only

✅ Decides WHERE to read  
✅ Decides WHERE to write  
✅ Decides IN WHAT ORDER  
✅ Decides HOW TO COMBINE results  
✅ Decides WHAT POLICY to apply  

---

## Usage

### Through MemoryEngine (Recommended)

```python
from core.memory import CognitiveMemoryEngine

engine = CognitiveMemoryEngine()

# The engine internally uses the coordinator
engine.store("conversation", content="User asked about...")
results = engine.retrieve("conversation")
```

### Direct Coordinator Access

```python
from core.memory import MemoryCoordinator

coordinator = MemoryCoordinator()

# Read
response = coordinator.read("key")

# Write
from core.memory import MemoryEntry, MemoryType
entry = MemoryEntry(
    content="Data",
    memory_type=MemoryType.WORKING,
)
coordinator.write(entry)

# Search
from core.memory import MemoryQuery
query = MemoryQuery(query="search term", limit=10)
results = coordinator.search(query)
```

---

## Contract

All memory implementations must implement `BaseMemoryInterface`:

```python
class BaseMemoryInterface(ABC):
    @property
    def memory_id(self) -> str: ...

    @property
    def memory_type(self) -> MemoryType: ...

    def initialize(self, config: dict) -> None: ...
    def shutdown(self) -> None: ...

    def read(self, key: str) -> MemoryResponse: ...
    def write(self, entry: MemoryEntry) -> MemoryResponse: ...
    def search(self, query: MemoryQuery) -> MemoryResponse: ...
    def delete(self, key: str) -> MemoryResponse: ...
    def clear(self) -> MemoryResponse: ...
```

### Example Implementation

```python
class PostgreSQLMemory(BaseMemoryInterface):
    def initialize(self, config: dict) -> None:
        # Setup PostgreSQL connection
        self._conn = psycopg2.connect(config["url"])

    def read(self, key: str) -> MemoryResponse:
        # Read from PostgreSQL
        # Return MemoryResponse
```

**The Coordinator never knows this is PostgreSQL.**

---

## Integration

### With MemoryEngine

```python
from core.memory import CognitiveMemoryEngine

engine = CognitiveMemoryEngine()

# Engine uses coordinator internally
engine.store("working", content="Data")
```

### With ExecutionCoordinator

```python
from core.execution import ExecutionCoordinator

coordinator = ExecutionCoordinator()
# Uses MemoryEngine which uses MemoryCoordinator internally
```

---

## Events

| Event | Description |
|-------|-------------|
| `MemoryRegistered` | Memory registered |
| `MemoryRead` | Read operation performed |
| `MemoryWrite` | Write operation performed |
| `MemorySearch` | Search operation performed |
| `MemoryDelete` | Delete operation performed |

---

## Metrics

```python
metrics = coordinator.get_metrics()

for memory_id, m in metrics.items():
    print(f"{memory_id}:")
    print(f"  Hit rate: {m['hit_rate']:.1f}%")
    print(f"  Avg latency: {m['average_latency_ms']:.0f}ms")
```

---

## Backward Compatibility

For legacy code using the old `MemoryOrchestrator` name:

```python
from core.memory import MemoryOrchestrator  # Still works!

orchestrator = MemoryOrchestrator()  # Same as MemoryCoordinator()
```

---

## References

- [Runtime Architecture](./runtime.md)
- [Memory System](./cognitive-memory-system.md)
- [Capability SDK](./capability-sdk.md)
- [Execution Coordinator](./execution-coordinator.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.1.0  
**Status**: Implemented (Refactored from Orchestrator)
