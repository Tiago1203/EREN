"""EREN Cognitive Context Engine (CCE).

The Context Engine is responsible ONLY for building context.
It does NOT generate responses, execute models, or build prompts.

Philosophy:
    The CCE NEVER:
    - Generates responses
    - Executes models
    - Builds prompts

    It ONLY:
    - Retrieves information
    - Merges results
    - Removes duplicates
    - Ranks context
    - Limits tokens
    - Compresses context
    - Prioritizes clinical information
    - Generates Context Package
"""

from __future__ import annotations

# Types - import from local module to avoid circular imports
from core.context.engine.types import (
    ContextPriority,
    ContextSource,
    ContextItem,
    ContextPackage,
    ContextQuery,
    ContextRetrievalResult,
    generate_id,
)

# Components
from core.context.engine.deduplicator import ContextDeduplicator
from core.context.engine.merger import ContextMerger
from core.context.engine.compressor import ContextCompressor
from core.context.engine.ranking import ContextRanker
from core.context.engine.builder import ContextBuilder

# Engine
from core.context.engine.engine import (
    CognitiveContextEngine,
    get_context_engine,
    reset_context_engine,
)

__all__ = [
    # Types
    "ContextPriority",
    "ContextSource",
    "ContextItem",
    "ContextPackage",
    "ContextQuery",
    "ContextRetrievalResult",
    "generate_id",
    # Components
    "ContextDeduplicator",
    "ContextMerger",
    "ContextCompressor",
    "ContextRanker",
    "ContextBuilder",
    # Engine
    "CognitiveContextEngine",
    "get_context_engine",
    "reset_context_engine",
]
