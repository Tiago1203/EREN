"""
AI Metrics Module

Core AI metrics: Accuracy, Latency, Cost, Quality Score.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import deque


class AIMetrics(BaseModel):
    """AI metrics snapshot."""
    timestamp: datetime
    accuracy: float = 0.0
    latency_p50: float = 0.0
    latency_p95: float = 0.0
    latency_p99: float = 0.0
    cost_per_query: float = 0.0
    quality_score: float = 0.0
    active_users: int = 0
    total_requests: int = 0


class AccuracyTracker:
    """Tracks accuracy metrics."""
    
    def __init__(self, window_size: int = 1000):
        self.correct = 0
        self.total = 0
        self.history: deque = deque(maxlen=window_size)
    
    def record(self, is_correct: bool):
        """Record a prediction result."""
        self.correct += int(is_correct)
        self.total += 1
        self.history.append(int(is_correct))
    
    def get_accuracy(self) -> float:
        """Get current accuracy."""
        if self.total == 0:
            return 0.0
        return self.correct / self.total
    
    def get_trend(self, window: int = 100) -> float:
        """Get accuracy trend over recent window."""
        if len(self.history) < window:
            return self.get_accuracy()
        
        recent = list(self.history)[-window:]
        return sum(recent) / len(recent)


class LatencyMonitor:
    """Monitors latency metrics."""
    
    def __init__(self, window_size: int = 10000):
        self.latencies: deque = deque(maxlen=window_size)
    
    def record(self, latency_ms: float):
        """Record latency."""
        self.latencies.append(latency_ms)
    
    def get_percentiles(self) -> Dict[str, float]:
        """Get latency percentiles."""
        if not self.latencies:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            "p50": sorted_latencies[int(n * 0.50)],
            "p95": sorted_latencies[int(n * 0.95)],
            "p99": sorted_latencies[int(n * 0.99)],
            "mean": sum(sorted_latencies) / n
        }
    
    def is_healthy(self, threshold_ms: float = 2000) -> bool:
        """Check if latency is healthy."""
        if not self.latencies:
            return True
        
        p95 = self.get_percentiles()["p95"]
        return p95 < threshold_ms


class CostTracker:
    """Tracks inference costs."""
    
    def __init__(self):
        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_requests = 0
        self.cost_per_token = 0.0001  # $0.0001 per token
    
    def record(self, tokens_used: int):
        """Record token usage."""
        self.total_tokens += tokens_used
        self.total_requests += 1
        self.total_cost = self.total_tokens * self.cost_per_token
    
    def get_cost_per_request(self) -> float:
        """Get average cost per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests
    
    def get_daily_cost(self, days: int = 1) -> float:
        """Estimate daily cost."""
        if self.total_requests == 0:
            return 0.0
        
        avg_requests_per_day = self.total_requests / max(1, (datetime.utcnow() - datetime.utcnow()).days or 1)
        return avg_requests_per_day * self.get_cost_per_request()


class QualityScore:
    """Composite quality score."""
    
    def __init__(
        self,
        accuracy_tracker: AccuracyTracker,
        latency_monitor: LatencyMonitor
    ):
        self.accuracy_tracker = accuracy_tracker
        self.latency_monitor = latency_monitor
        self.weights = {
            "accuracy": 0.4,
            "latency": 0.3,
            "cost": 0.2,
            "safety": 0.1
        }
    
    def calculate(self) -> float:
        """Calculate composite quality score (0-100)."""
        accuracy_score = self.accuracy_tracker.get_accuracy() * 100
        
        # Latency score (100 if < 500ms, decreasing for higher latency)
        p95 = self.latency_monitor.get_percentiles()["p95"]
        if p95 < 500:
            latency_score = 100
        elif p95 < 2000:
            latency_score = 100 - ((p95 - 500) / 1500) * 50
        else:
            latency_score = 50 - min(50, (p95 - 2000) / 100)
        
        # Cost score (simplified)
        cost_score = 90  # Would be based on budget
        
        # Safety score (simplified)
        safety_score = 95
        
        weighted_score = (
            accuracy_score * self.weights["accuracy"] +
            latency_score * self.weights["latency"] +
            cost_score * self.weights["cost"] +
            safety_score * self.weights["safety"]
        )
        
        return round(weighted_score, 2)
    
    def get_breakdown(self) -> Dict[str, float]:
        """Get score breakdown."""
        return {
            "accuracy": self.accuracy_tracker.get_accuracy() * 100,
            "latency": self.latency_monitor.get_percentiles()["p95"],
            "quality_score": self.calculate()
        }


class MetricsDashboard:
    """Aggregated metrics dashboard."""
    
    def __init__(self):
        self.accuracy_tracker = AccuracyTracker()
        self.latency_monitor = LatencyMonitor()
        self.cost_tracker = CostTracker()
        self.quality_score = QualityScore(self.accuracy_tracker, self.latency_monitor)
    
    def record(self, latency_ms: float, tokens_used: int, is_correct: bool = None):
        """Record metrics."""
        self.latency_monitor.record(latency_ms)
        self.cost_tracker.record(tokens_used)
        if is_correct is not None:
            self.accuracy_tracker.record(is_correct)
    
    def get_snapshot(self) -> AIMetrics:
        """Get current metrics snapshot."""
        return AIMetrics(
            timestamp=datetime.utcnow(),
            accuracy=self.accuracy_tracker.get_accuracy(),
            latency_p50=self.latency_monitor.get_percentiles()["p50"],
            latency_p95=self.latency_monitor.get_percentiles()["p95"],
            latency_p99=self.latency_monitor.get_percentiles()["p99"],
            cost_per_query=self.cost_tracker.get_cost_per_request(),
            quality_score=self.quality_score.calculate(),
            total_requests=self.cost_tracker.total_requests
        )
