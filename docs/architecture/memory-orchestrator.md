# Cognitive Memory Orchestrator (CMO)

> **Philosophy**: The Orchestrator does NOT store information. It only decides WHERE to read, WHERE to write, IN WHAT ORDER, and HOW TO COMBINE results.

This document describes the Cognitive Memory Orchestrator, the official system for coordinating all memory systems in EREN OS.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Memory Types](#memory-types)
4. [Access Policies](#access-policies)
5. [Orchestrator](#orchestrator)
6. [Contract](#contract)
7. [Integration](#integration)
8. [Events](#events)
9. [Metrics](#metrics)

---

## Overview

The Memory Orchestrator is completely decoupled from concrete implementations. It never knows PostgreSQL, Redis, Chroma, Qdrant, Pinecone, Milvus, FAISS, SQLite, or any other storage backend.

### Key Features

- **Decoupled Architecture**: Only knows contracts, not implementations
- **Multiple Memory Types**: Support for Working, Conversation, Episodic, Semantic, Vector, Clinical, Device
- **Multiple Access Policies**: FIRST_AVAILABLE, LONG_TERM_ONLY, SHORT_TERM_ONLY, MERGE_ALL, etc.
- **Full Observability**: Events, metrics, and tracing
- **Pluggable**: Add new memories without modifying the Kernel

---

## Architecture

### Module Structure

```
core/memory/
├── __init__.py           # Exports
├── base.py              # BaseMemoryInterface
├── registry.py           # MemoryRegistry
├── selector.py          # MemorySelector
├── orchestrator.py      # MemoryOrchestrator
├── types.py             # Types and enums
├── exceptions.py        # Exception types
└── README.md           # Quick start
```

### Components

| Component | Description |
|-----------|-------------|
| `BaseMemoryInterface` | Contract for memory implementations |
| `MemoryRegistry` | Manages memory registration |
| `MemorySelector` | Implements access policies |
| `MemoryOrchestrator` | Orchestrates all operations |

### Flow

```
User: "¿Recuerdas qué monitor estaba reparando ayer?"
         ↓
MemoryOrchestrator
         ↓
Working Memory
         ↓
Conversation Memory
         ↓
Long Term Memory
         ↓
Vector Search
         ↓
    Respuesta
```

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
| `SHORT_TERM` | Immediate context | Temporary |
| `LONG_TERM` | Persistent storage | Persistent |

### Classification

```python
# Short-term memories
MemoryType.is_short_term(MemoryType.WORKING)  # True

# Long-term memories
MemoryType.is_long_term(MemoryType.EPISODIC)  # True
```

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

## Orchestrator

### The Orchestrator Does NOT

- ❌ Store information
- ❌ Know PostgreSQL, Redis, Chroma, etc.
- ❌ Implement search algorithms
- ❌ Manage persistence

### The Orchestrator Only

- ✅ Decides WHERE to read
- ✅ Decides WHERE to write
- ✅ Decides IN WHAT ORDER
- ✅ Decides HOW TO COMBINE results

### Usage

```python
from core.memory import (
    MemoryOrchestrator,
    MemoryEntry,
    MemoryType,
    MemoryAccessPolicy,
)

orchestrator = MemoryOrchestrator()

# Write to memory
entry = MemoryEntry(
    content="User asked about monitor repair",
    memory_type=MemoryType.WORKING,
)
orchestrator.write(entry)

# Read from memory
response = orchestrator.read(entry.key)

# Search across all memories
query = MemoryQuery(query="monitor repair", limit=10)
results = orchestrator.search(query)

# Change policy
orchestrator.default_policy = MemoryAccessPolicy.LONG_TERM_ONLY
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
    def read_batch(self, keys: list[str]) -> MemoryResponse: ...

    def write(self, entry: MemoryEntry) -> MemoryResponse: ...
    def write_batch(self, entries: list[MemoryEntry]) -> MemoryResponse: ...

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
        cursor = self._conn.cursor()
        cursor.execute("SELECT content FROM memory WHERE key = %s", (key,))
        row = cursor.fetchone()
        # Return MemoryResponse
```

**The Orchestrator never knows this is PostgreSQL.**

---

## Integration

### With Execution Coordinator

```python
from core.execution import ExecutionCoordinator

coordinator = ExecutionCoordinator()
orchestrator = coordinator.memory

# Coordinator uses orchestrator for memory operations
result = await coordinator.execute(task, memory=orchestrator)
```

### With Pipeline

```python
from core.pipeline import Pipeline

pipeline = Pipeline()
pipeline.use_memory(MemoryOrchestrator())

# Pipeline automatically uses orchestrator
result = pipeline.execute(task)
```

### With Capability SDK

```python
from core.sdk import CapabilityContext

context = CapabilityContext(
    capability_id="reasoning",
    metadata={"memory_enabled": True},
)

# Capability can access memory through orchestrator
result = capability.execute(context)
```

---

## Events

| Event | Description |
|-------|-------------|
| `MemoryRegistered` | Memory registered |
| `MemoryUnregistered` | Memory unregistered |
| `MemoryStateChanged` | Memory state changed |
| `MemoryRead` | Read operation performed |
| `MemoryWrite` | Write operation performed |
| `MemorySearch` | Search operation performed |
| `MemoryDelete` | Delete operation performed |
| `MemoryClear` | Clear operation performed |

### Event Handling

```python
orchestrator.on("MemoryRead", lambda data: log_read(data))
orchestrator.on("MemoryWrite", lambda data: log_write(data))
```

---

## Metrics

### Tracked Metrics

- `total_reads`: Total read operations
- `total_writes`: Total write operations
- `total_searches`: Total search operations
- `total_hits`: Successful reads
- `total_misses`: Failed reads
- `hit_rate`: Hit percentage
- `average_latency_ms`: Average operation time

### Usage

```python
metrics = orchestrator.get_metrics()

for memory_id, m in metrics.items():
    print(f"{memory_id}:")
    print(f"  Hit rate: {m['hit_rate']:.1f}%")
    print(f"  Avg latency: {m['average_latency_ms']:.0f}ms")
```

---

## References

- [Runtime Architecture](./runtime.md)
- [Capability SDK](./capability-sdk.md)
- [Execution Coordinator](./execution-coordinator.md)
- [Pipeline](./pipeline.md)

---

**Last Updated**: 2024-01-16  
**Version**: 1.0.0  
**Status**: Implemented
