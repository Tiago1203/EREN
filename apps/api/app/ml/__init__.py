"""
EREN Machine Learning Module

Feedback Learning, Model Evaluation, Fine Tuning, Prompt Optimization, Analytics, AI Metrics.
"""
from .feedback_learning import FeedbackCollector, FeedbackProcessor, LearningLoop
from .model_evaluation import EvaluationRunner, BenchmarkSuite, PerformanceTracker
from .fine_tuning import DatasetGenerator, TrainingPipeline, LoRAConfig
from .prompt_optimization import PromptLibrary, PromptVersioning, PromptMetrics
from .analytics import InteractionLogger, UsageAnalyzer, TrendDetector
from .ai_metrics import AccuracyTracker, LatencyMonitor, CostTracker, QualityScore

__all__ = [
    # Feedback Learning
    "FeedbackCollector",
    "FeedbackProcessor",
    "LearningLoop",
    # Model Evaluation
    "EvaluationRunner",
    "BenchmarkSuite",
    "PerformanceTracker",
    # Fine Tuning
    "DatasetGenerator",
    "TrainingPipeline",
    "LoRAConfig",
    # Prompt Optimization
    "PromptLibrary",
    "PromptVersioning",
    "PromptMetrics",
    # Analytics
    "InteractionLogger",
    "UsageAnalyzer",
    "TrendDetector",
    # AI Metrics
    "AccuracyTracker",
    "LatencyMonitor",
    "CostTracker",
    "QualityScore",
]
__version__ = "1.0.0"
