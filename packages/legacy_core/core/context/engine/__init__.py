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

from core.context.engine.builder import ContextBuilder
from core.context.engine.compressor import ContextCompressor

# Components
from core.context.engine.deduplicator import ContextDeduplicator

# Engine
from core.context.engine.engine import (
    CognitiveContextEngine,
    get_context_engine,
    reset_context_engine,
)
from core.context.engine.merger import ContextMerger
from core.context.engine.ranking import ContextRanker

# Types - import from local module to avoid circular imports
from core.context.engine.types import (
    ContextItem,
    ContextPackage,
    ContextPriority,
    ContextQuery,
    ContextRetrievalResult,
    ContextSource,
    generate_id,
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
