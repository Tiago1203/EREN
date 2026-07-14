"""EREN Cognitive Learning Platform (CLP).

The official system for continuous learning in EREN.
Allows EREN to automatically improve from experience, results, and feedback.

Philosophy:
    Reasoning decides.
    Learning improves.

Architecture:
    Reasoning Platform
            │
            ▼
    Learning Platform
            │
            ├── Experience Collector
            ├── Feedback Analyzer
            ├── Pattern Discovery
            ├── Knowledge Consolidator
            ├── Strategy Optimizer
            └── Learning Metrics

Responsibilities:
- Register experiences
- Evaluate outcomes
- Analyze errors
- Detect patterns
- Consolidate knowledge
- Update strategies
- Improve future decisions
- Optimize agents
"""

from __future__ import annotations

# Types
from core.learning.types import (
    LearningType,
    LearningStatus,
    LearningMetrics,
    Experience,
    Feedback,
    FeedbackType,
    Pattern,
    Knowledge,
    KnowledgeType,
)

# Components
from core.learning.experience import (
    ExperienceCollector,
    get_experience_collector,
    reset_experience_collector,
)
from core.learning.feedback import (
    FeedbackAnalyzer,
    get_feedback_analyzer,
    reset_feedback_analyzer,
)
from core.learning.patterns import (
    PatternDiscovery,
    get_pattern_discovery,
    reset_pattern_discovery,
)
from core.learning.consolidation import (
    KnowledgeConsolidator,
    get_knowledge_consolidator,
    reset_knowledge_consolidator,
)
from core.learning.optimizer import (
    StrategyOptimizer,
    get_strategy_optimizer,
    reset_strategy_optimizer,
)

# Main platform
from core.learning.platform import (
    CognitiveLearningPlatform,
    get_learning_platform,
    reset_learning_platform,
)

__all__ = [
    # Types
    "LearningType",
    "LearningStatus",
    "LearningMetrics",
    "Experience",
    "Feedback",
    "FeedbackType",
    "Pattern",
    "Knowledge",
    "KnowledgeType",
    # Components
    "ExperienceCollector",
    "get_experience_collector",
    "reset_experience_collector",
    "FeedbackAnalyzer",
    "get_feedback_analyzer",
    "reset_feedback_analyzer",
    "PatternDiscovery",
    "get_pattern_discovery",
    "reset_pattern_discovery",
    "KnowledgeConsolidator",
    "get_knowledge_consolidator",
    "reset_knowledge_consolidator",
    "StrategyOptimizer",
    "get_strategy_optimizer",
    "reset_strategy_optimizer",
    # Main platform
    "CognitiveLearningPlatform",
    "get_learning_platform",
    "reset_learning_platform",
]
