"""
Analytics Module

Interaction logging, usage analysis, and trend detection.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import defaultdict


class Interaction(BaseModel):
    """AI interaction record."""
    id: str
    user_id: str
    session_id: str
    query: str
    response: str
    model_id: str
    latency_ms: float
    tokens_used: int = 0
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class InteractionLogger:
    """Logs all AI interactions."""
    
    def __init__(self):
        self.interactions: List[Interaction] = []
        self.max_logs = 100000
    
    async def log(self, interaction: Interaction):
        """Log an interaction."""
        self.interactions.append(interaction)
        
        # Cleanup old logs
        if len(self.interactions) > self.max_logs:
            self.interactions = self.interactions[-self.max_logs:]
    
    async def query(
        self,
        user_id: str = None,
        session_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[Interaction]:
        """Query interactions."""
        results = self.interactions
        
        if user_id:
            results = [i for i in results if i.user_id == user_id]
        if session_id:
            results = [i for i in results if i.session_id == session_id]
        if start_date:
            results = [i for i in results if i.timestamp >= start_date]
        if end_date:
            results = [i for i in results if i.timestamp <= end_date]
        
        return results[-limit:]


class UsageAnalyzer:
    """Analyzes usage patterns."""
    
    def __init__(self, logger: InteractionLogger):
        self.logger = logger
    
    async def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get usage summary."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [i for i in self.logger.interactions if i.timestamp >= cutoff]
        
        return {
            "total_interactions": len(recent),
            "unique_users": len(set(i.user_id for i in recent)),
            "unique_sessions": len(set(i.session_id for i in recent)),
            "avg_latency_ms": sum(i.latency_ms for i in recent) / len(recent) if recent else 0,
            "total_tokens": sum(i.tokens_used for i in recent),
            "period_days": days
        }
    
    async def get_hourly_distribution(self) -> Dict[int, int]:
        """Get hourly distribution of interactions."""
        distribution = defaultdict(int)
        for interaction in self.logger.interactions:
            hour = interaction.timestamp.hour
            distribution[hour] += 1
        return dict(distribution)
    
    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top users by interaction count."""
        user_counts = defaultdict(int)
        for interaction in self.logger.interactions:
            user_counts[interaction.user_id] += 1
        
        return [
            {"user_id": uid, "count": count}
            for uid, count in sorted(user_counts.items(), key=lambda x: -x[1])[:limit]
        ]


class TrendDetector:
    """Detects trends in usage and performance."""
    
    def __init__(self, logger: InteractionLogger):
        self.logger = logger
    
    async def detect_latency_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Detect latency trends."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [i for i in self.logger.interactions if i.timestamp >= cutoff]
        
        if len(recent) < 10:
            return {"trend": "insufficient_data"}
        
        # Split into halves
        mid = len(recent) // 2
        first_half_avg = sum(i.latency_ms for i in recent[:mid]) / mid
        second_half_avg = sum(i.latency_ms for i in recent[mid:]) / (len(recent) - mid)
        
        change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        return {
            "trend": "increasing" if change_pct > 10 else "decreasing" if change_pct < -10 else "stable",
            "change_percent": change_pct,
            "first_half_avg": first_half_avg,
            "second_half_avg": second_half_avg
        }
    
    async def detect_usage_anomaly(self, hours: int = 24, threshold: float = 2.0) -> bool:
        """Detect usage anomalies."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [i for i in self.logger.interactions if i.timestamp >= cutoff]
        
        hourly_counts = defaultdict(int)
        for interaction in recent:
            hour = interaction.timestamp.replace(minute=0, second=0)
            hourly_counts[hour] += 1
        
        if not hourly_counts:
            return False
        
        counts = list(hourly_counts.values())
        avg = sum(counts) / len(counts)
        std = (sum((c - avg) ** 2 for c in counts) / len(counts)) ** 0.5
        
        return any(abs(c - avg) > threshold * std for c in counts)
