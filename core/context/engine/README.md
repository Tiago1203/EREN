# Cognitive Context Engine (CCE)

## Overview

The Cognitive Context Engine is responsible ONLY for building the best possible context for a cognitive task.

## Philosophy

> The CCE **NEVER**:
> - Generates responses
> - Executes models
> - Builds prompts
> 
> **It ONLY**:
> - Retrieves information
> - Merges results
> - Removes duplicates
> - Ranks context
> - Limits tokens
> - Compresses context
> - Prioritizes clinical information
> - Generates Context Package

## Architecture

```
User Query
    │
    ▼
Cognitive Context Engine
    │
    ├──► Memory Coordinator
    │        │
    │        ├──► Conversation Memory
    │        ├──► Device Memory
    │        └──► Clinical Memory
    │
    ├──► Semantic Retrieval Engine
    │        │
    │        └──► Knowledge Asset Registry
    │                 │
    │                 └──► Vector Memory
    │
    ▼
Context Package
    │
    ▼
Prompt Builder
    │
    ▼
LLM
```

## Components

| Component | Responsibility |
|-----------|----------------|
| `engine.py` | Main CCE orchestrator |
| `builder.py` | Retrieves context from sources |
| `merger.py` | Merges results from different sources |
| `deduplicator.py` | Removes duplicate context items |
| `compressor.py` | Compresses context to fit budget |
| `ranking.py` | Ranks and prioritizes context |

## Context Sources

- **CONVERSATION**: Conversation history
- **KNOWLEDGE**: Knowledge base
- **VECTOR_MEMORY**: Vector database
- **DEVICE**: Device information
- **CLINICAL**: Clinical context (highest priority)

## Context Priority

- **CRITICAL**: Critical information
- **HIGH**: High priority
- **MEDIUM**: Medium priority
- **LOW**: Low priority

## Usage

```python
from core.context.engine import CognitiveContextEngine, ContextPackage

# Create engine
engine = CognitiveContextEngine(
    retrieval_engine=retrieval_engine,
    memory_coordinator=memory_coordinator,
)

# Build context package
package = await engine.build_context(
    query="What is the treatment for diabetes?",
    max_tokens=4000,
)

# Package is ready for Prompt Builder
print(f"Context tokens: {package.context_tokens}")
print(f"Total items: {package.total_items}")
```

## Output: ContextPackage

```python
@dataclass
class ContextPackage:
    package_id: str
    query: str
    items: list[ContextItem]
    context_text: str
    context_tokens: int
    total_items: int
    items_by_source: dict[str, int]
    avg_relevance: float
    max_relevance: float
    has_clinical_context: bool
    has_conversation_history: bool
    has_knowledge_context: bool
```

## Integration

The ContextPackage is passed to the Prompt Builder, which only receives it and constructs the final prompt. The CCE is the bridge between retrieval and generation.

```
CCE → ContextPackage → PromptBuilder → Provider → LLM
```
