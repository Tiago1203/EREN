"""
Continuous Improvement Engine Module

Complete implementation of EPIC 11 for EREN PHASE 3.

This module provides continuous improvement governance:
- Learning Review
- Quality Analysis
- Conflict Detection
- Version Management
- Governance
- Rollback
- Performance Monitoring

ARCHITECTURE NOTE:
- RevisionStatus, ApprovalDecision, RollbackTrigger, QualityDimension
  are imported from Foundation (single source of truth)
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Import shared enums from Foundation (SINGLE SOURCE OF TRUTH)
from core.intelligence.foundation import (
    RevisionStatus,
    ApprovalDecision,
    RollbackTrigger,
    QualityDimension,
)


# Version
__version__ = "1.0.0"


# ============ DOMAIN MODELS ============

@dataclass
class KnowledgeRevision:
    """Revision of knowledge."""
    revision_id: str
    learning_package_id: str
    quality_score: float
    conflicts_detected: list[str]
    status: RevisionStatus
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]


@dataclass
class QualityScore:
    """Quality score breakdown."""
    accuracy: float
    consistency: float
    evidence: float
    repeatability: float
    coverage: float
    impact: float
    total_score: float
    passed: bool


@dataclass
class QualityReport:
    """Complete quality analysis report."""
    report_id: str
    knowledge_id: str
    scores: QualityScore
    analysis_timestamp: datetime


@dataclass
class KnowledgeVersion:
    """Version of knowledge base."""
    version: str
    major: int
    minor: int
    patch: int
    created_at: datetime
    changes: list[dict]
    approved_by: str
    notes: str


@dataclass
class ApprovalRecord:
    """Record of approval."""
    approval_id: str
    version: str
    approved_by: str
    approved_at: datetime
    decision: ApprovalDecision
    comments: str


@dataclass
class RollbackOperation:
    """Rollback operation record."""
    rollback_id: str
    trigger: RollbackTrigger
    from_version: str
    to_version: str
    initiated_by: str
    reason: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str


@dataclass
class PerformanceMetric:
    """Performance metric snapshot."""
    metric_name: str
    value: float
    threshold: float
    timestamp: datetime


@dataclass
class ImprovementResult:
    """Result of improvement process."""
    approved: bool
    new_version: Optional[str]
    changes: list[dict]
    conflicts: list[str]
    warnings: list[str]


# ============ LEARNING REVIEW MANAGER ============

class LearningReviewManager:
    """Manages review of learning packages."""
    
    def __init__(self):
        self.revisions: list[KnowledgeRevision] = []
    
    async def create_revision(
        self,
        package_id: str,
        initial_score: float = 0.5,
    ) -> KnowledgeRevision:
        """Create new revision for review."""
        
        revision = KnowledgeRevision(
            revision_id=f"rev_{datetime.now().timestamp()}",
            learning_package_id=package_id,
            quality_score=initial_score,
            conflicts_detected=[],
            status=RevisionStatus.PENDING,
            reviewed_by=None,
            reviewed_at=None,
        )
        
        self.revisions.append(revision)
        return revision
    
    async def triage(
        self,
        revision: KnowledgeRevision,
    ) -> str:
        """Triage revision based on priority."""
        
        if revision.quality_score >= 0.9:
            return "auto_approve"
        elif revision.quality_score >= 0.75:
            return "expert_review"
        else:
            revision.status = RevisionStatus.NEEDS_REVISION
            return "needs_revision"


# ============ KNOWLEDGE QUALITY ANALYZER ============

class KnowledgeQualityAnalyzer:
    """Analyzes quality of new knowledge."""
    
    MIN_TOTAL = 0.75
    MIN_ACCURACY = 0.80
    
    async def analyze(
        self,
        new_knowledge_count: int,
        patterns_count: int,
        experience_count: int,
    ) -> QualityReport:
        """Analyze quality of knowledge."""
        
        scores = QualityScore(
            accuracy=min(1.0, experience_count / 10 + 0.5),
            consistency=min(1.0, patterns_count / 5 + 0.5),
            evidence=min(1.0, experience_count / 10),
            repeatability=0.7 if patterns_count >= 3 else 0.5,
            coverage=min(1.0, new_knowledge_count / 10),
            impact=min(1.0, new_knowledge_count / 5),
            total_score=0.0,
            passed=False,
        )
        
        # Calculate total
        scores.total_score = (
            scores.accuracy * 0.30 +
            scores.consistency * 0.20 +
            scores.evidence * 0.20 +
            scores.repeatability * 0.10 +
            scores.coverage * 0.10 +
            scores.impact * 0.10
        )
        
        scores.passed = scores.total_score >= self.MIN_TOTAL
        
        return QualityReport(
            report_id=f"qr_{datetime.now().timestamp()}",
            knowledge_id="",
            scores=scores,
            analysis_timestamp=datetime.now(),
        )


# ============ CONFLICT DETECTION ENGINE ============

class ConflictDetectionEngine:
    """Detects conflicts in knowledge."""
    
    def __init__(self):
        self.conflicts: list[dict] = []
    
    async def detect(
        self,
        patterns: list[dict],
        rules: list[dict],
    ) -> list[str]:
        """Detect conflicts in knowledge."""
        
        conflicts = []
        
        # Check for low confidence patterns
        for pattern in patterns:
            if pattern.get("confidence", 1.0) < 0.5:
                conflicts.append(
                    f"Low confidence pattern: {pattern.get('id', 'unknown')}"
                )
        
        # Check for conflicting rules
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                if self._conflicts(rule1, rule2):
                    conflicts.append(
                        f"Conflicting rules: {rule1.get('id')} vs {rule2.get('id')}"
                    )
        
        return conflicts
    
    def _conflicts(self, rule1: dict, rule2: dict) -> bool:
        """Check if two rules conflict."""
        # Simple conflict detection
        if rule1.get("condition") == rule2.get("condition"):
            if rule1.get("action") != rule2.get("action"):
                return True
        return False


# ============ EXPERT REVIEW WORKFLOW ============

class ExpertReviewWorkflow:
    """Manages expert review process."""
    
    async def review(
        self,
        quality_report: QualityReport,
        conflicts: list[str],
    ) -> ApprovalRecord:
        """Process expert review."""
        
        # Auto-approve if high quality and no conflicts
        if quality_report.scores.passed and not conflicts:
            return ApprovalRecord(
                approval_id=f"approval_{datetime.now().timestamp()}",
                version="pending",
                approved_by="auto_approval",
                approved_at=datetime.now(),
                decision=ApprovalDecision.APPROVED,
                comments="Auto-approved: High quality, no conflicts",
            )
        
        # Require review if conflicts
        if conflicts:
            return ApprovalRecord(
                approval_id=f"approval_{datetime.now().timestamp()}",
                version="pending",
                approved_by="pending",
                approved_at=datetime.now(),
                decision=ApprovalDecision.NEEDS_REVIEW,
                comments=f"Conflicts detected: {len(conflicts)}",
            )
        
        # Reject low quality
        return ApprovalRecord(
            approval_id=f"approval_{datetime.now().timestamp()}",
            version="pending",
            approved_by="auto_rejection",
            approved_at=datetime.now(),
            decision=ApprovalDecision.REJECTED,
            comments=f"Quality score {quality_report.scores.total_score:.2f} below threshold",
        )


# ============ KNOWLEDGE VERSION MANAGER ============

class KnowledgeVersionManager:
    """Manages knowledge versions."""
    
    def __init__(self):
        self.versions: list[KnowledgeVersion] = []
        self.current_version = "v1.0.0"
    
    async def create_version(
        self,
        approved: bool,
        change_type: str = "minor",
    ) -> Optional[KnowledgeVersion]:
        """Create new version if approved."""
        
        if not approved:
            return None
        
        # Calculate new version
        parts = self.current_version.replace("v", "").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if change_type == "major":
            new_version = f"v{major + 1}.0.0"
        elif change_type == "minor":
            new_version = f"v{major}.{minor + 1}.0"
        else:
            new_version = f"v{major}.{minor}.{patch + 1}"
        
        version = KnowledgeVersion(
            version=new_version,
            major=major + (1 if change_type == "major" else 0),
            minor=minor if change_type == "major" else (minor + 1 if change_type == "minor" else minor),
            patch=0 if change_type != "patch" else patch + 1,
            created_at=datetime.now(),
            changes=[],
            approved_by="system",
            notes="Approved via continuous improvement",
        )
        
        self.versions.append(version)
        self.current_version = new_version
        
        return version
    
    def get_history(self) -> list[KnowledgeVersion]:
        """Get version history."""
        return sorted(self.versions, key=lambda v: v.created_at, reverse=True)


# ============ ROLLBACK MANAGER ============

class RollbackManager:
    """Manages rollback operations."""
    
    def __init__(self):
        self.operations: list[RollbackOperation] = []
        self.version_manager = KnowledgeVersionManager()
    
    async def execute_rollback(
        self,
        trigger: RollbackTrigger,
        reason: str,
        initiated_by: str = "system",
    ) -> RollbackOperation:
        """Execute rollback to previous version."""
        
        current = self.version_manager.current_version
        previous = self._get_previous_version(current)
        
        if not previous:
            raise ValueError("No previous version available")
        
        operation = RollbackOperation(
            rollback_id=f"rb_{datetime.now().timestamp()}",
            trigger=trigger,
            from_version=current,
            to_version=previous,
            initiated_by=initiated_by,
            reason=reason,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            status="completed",
        )
        
        self.operations.append(operation)
        self.version_manager.current_version = previous
        
        return operation
    
    def _get_previous_version(self, current: str) -> Optional[str]:
        """Get previous version for rollback."""
        parts = current.replace("v", "").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if patch > 0:
            return f"v{major}.{minor}.{patch - 1}"
        elif minor > 0:
            return f"v{major}.{minor - 1}.0"
        elif major > 1:
            return f"v{major - 1}.0.0"
        return None


# ============ PERFORMANCE MONITOR ============

class PerformanceMonitor:
    """Monitors performance metrics."""
    
    def __init__(self):
        self.metrics: list[PerformanceMetric] = []
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        threshold: float,
    ) -> PerformanceMetric:
        """Record performance metric."""
        
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            timestamp=datetime.now(),
        )
        
        self.metrics.append(metric)
        return metric
    
    async def check_thresholds(self) -> list[str]:
        """Check if any metrics exceed thresholds."""
        alerts = []
        
        for metric in self.metrics[-10:]:  # Last 10 metrics
            if metric.value < metric.threshold:
                alerts.append(
                    f"{metric.metric_name}: {metric.value:.2f} < {metric.threshold}"
                )
        
        return alerts


# ============ MAIN CONTINUOUS IMPROVEMENT ENGINE ============

class ContinuousImprovementEngine:
    """
    Main continuous improvement engine.
    Guardian of EREN's evolution.
    """
    
    def __init__(self):
        self.review_manager = LearningReviewManager()
        self.quality_analyzer = KnowledgeQualityAnalyzer()
        self.conflict_detector = ConflictDetectionEngine()
        self.expert_reviewer = ExpertReviewWorkflow()
        self.version_manager = KnowledgeVersionManager()
        self.rollback_manager = RollbackManager()
        self.performance_monitor = PerformanceMonitor()
    
    async def improve(
        self,
        learning_package: dict,
    ) -> ImprovementResult:
        """Process learning package through improvement pipeline."""
        
        package_id = f"pkg_{datetime.now().timestamp()}"
        
        # 1. Create revision
        revision = await self.review_manager.create_revision(package_id)
        
        # 2. Analyze quality
        quality_report = await self.quality_analyzer.analyze(
            new_knowledge_count=len(learning_package.get("new_knowledge", [])),
            patterns_count=len(learning_package.get("patterns", [])),
            experience_count=len(learning_package.get("experience_records", [])),
        )
        
        # 3. Detect conflicts
        conflicts = await self.conflict_detector.detect(
            patterns=learning_package.get("patterns", []),
            rules=learning_package.get("suggested_rules", []),
        )
        
        # 4. Expert review
        approval = await self.expert_reviewer.review(quality_report, conflicts)
        
        # 5. Create version if approved
        new_version = None
        if approval.decision == ApprovalDecision.APPROVED:
            version = await self.version_manager.create_version(approved=True)
            new_version = version.version if version else None
        
        return ImprovementResult(
            approved=approval.decision == ApprovalDecision.APPROVED,
            new_version=new_version,
            changes=learning_package.get("new_knowledge", []),
            conflicts=conflicts,
            warnings=[approval.comments],
        )


__all__ = [
    # Version
    "__version__",
    # Enums (re-exported from Foundation for convenience)
    "RevisionStatus",
    "ApprovalDecision",
    "RollbackTrigger",
    "QualityDimension",
    # Domain Models
    "KnowledgeRevision",
    "QualityScore",
    "QualityReport",
    "KnowledgeVersion",
    "ApprovalRecord",
    "RollbackOperation",
    "PerformanceMetric",
    "ImprovementResult",
    # Components
    "LearningReviewManager",
    "KnowledgeQualityAnalyzer",
    "ConflictDetectionEngine",
    "ExpertReviewWorkflow",
    "KnowledgeVersionManager",
    "RollbackManager",
    "PerformanceMonitor",
    "ContinuousImprovementEngine",
]
