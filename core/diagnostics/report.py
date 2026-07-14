"""Diagnostic Report Generator for EREN OS Diagnostics.

Generates comprehensive diagnostic reports:
- Full system validation results
- Score breakdown by category
- Production readiness determination
- Issue summaries
- Recommendations

Philosophy:
    Reports should be comprehensive, clear, and actionable.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.diagnostics.architecture import ArchitectureReport
    from core.diagnostics.contracts import ContractReport
    from core.diagnostics.dependencies import DependencyReport
    from core.diagnostics.health import HealthCheckResult
    from core.diagnostics.integration import IntegrationReport
    from core.diagnostics.liveness import LivenessReport
    from core.diagnostics.performance import PerformanceReport
    from core.diagnostics.readiness import ReadinessReport
    from core.diagnostics.runtime import RuntimeReport


@dataclass
class DiagnosticReport:
    """Complete diagnostic report for EREN OS.

    Aggregates all diagnostic results into a comprehensive report.
    """

    # Core information
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str = ""
    duration_ms: int = 0

    # Overall status
    score: float = 0.0
    production_ready: bool = False
    status: str = "UNKNOWN"

    # Component reports
    health_report: HealthCheckResult | None = None
    readiness_report: ReadinessReport | None = None
    liveness_report: LivenessReport | None = None
    architecture_report: ArchitectureReport | None = None
    contract_report: ContractReport | None = None
    dependency_report: DependencyReport | None = None
    integration_report: IntegrationReport | None = None
    runtime_report: RuntimeReport | None = None
    performance_report: PerformanceReport | None = None

    # Score categories
    scores: dict = field(default_factory=dict)

    # Summary metrics
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warnings: int = 0

    # Issues
    critical_issues: list[dict] = field(default_factory=list)
    major_issues: list[dict] = field(default_factory=list)
    minor_issues: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "correlation_id": self.correlation_id,
            "duration_ms": self.duration_ms,
            "score": self.score,
            "production_ready": self.production_ready,
            "status": self.status,
            "health_report": self.health_report.to_dict() if self.health_report else None,
            "readiness_report": self.readiness_report.to_dict() if self.readiness_report else None,
            "liveness_report": self.liveness_report.to_dict() if self.liveness_report else None,
            "architecture_report": self.architecture_report.to_dict() if self.architecture_report else None,
            "contract_report": self.contract_report.to_dict() if self.contract_report else None,
            "dependency_report": self.dependency_report.to_dict() if self.dependency_report else None,
            "integration_report": self.integration_report.to_dict() if self.integration_report else None,
            "runtime_report": self.runtime_report.to_dict() if self.runtime_report else None,
            "performance_report": self.performance_report.to_dict() if self.performance_report else None,
            "scores": self.scores,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "critical_issues": self.critical_issues,
            "major_issues": self.major_issues,
            "minor_issues": self.minor_issues,
        }

    def summary(self) -> str:
        """Generate human-readable summary.

        Returns:
            Formatted summary string.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("EREN OS DIAGNOSTIC REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {self.generated_at.isoformat()}")
        lines.append(f"Duration: {self.duration_ms}ms")
        lines.append("")
        lines.append("OVERALL STATUS")
        lines.append("-" * 60)
        lines.append(f"Final Score: {self.score:.1f}%")
        lines.append(f"Production Ready: {'YES' if self.production_ready else 'NO'}")
        lines.append(f"Status: {self.status}")
        lines.append("")

        if self.scores:
            lines.append("CATEGORY SCORES")
            lines.append("-" * 60)
            for category, score_info in sorted(self.scores.items()):
                if category.startswith("_"):
                    continue
                score = score_info.get("score", 0)
                weight = score_info.get("weight", 0)
                lines.append(f"{category:25} {score:5.1f}% (weight: {weight:.2f})")
            lines.append("")

        lines.append("CHECK RESULTS")
        lines.append("-" * 60)
        lines.append(f"Total Checks: {self.total_checks}")
        lines.append(f"Passed: {self.passed_checks}")
        lines.append(f"Failed: {self.failed_checks}")
        lines.append(f"Warnings: {self.warnings}")
        lines.append("")

        if self.critical_issues:
            lines.append("CRITICAL ISSUES")
            lines.append("-" * 60)
            for issue in self.critical_issues:
                lines.append(f"  • {issue.get('description', str(issue))}")
            lines.append("")

        if self.major_issues:
            lines.append("MAJOR ISSUES")
            lines.append("-" * 60)
            for issue in self.major_issues[:10]:  # Limit to first 10
                lines.append(f"  • {issue.get('description', str(issue))}")
            if len(self.major_issues) > 10:
                lines.append(f"  ... and {len(self.major_issues) - 10} more")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def get_recommendations(self) -> list[str]:
        """Get actionable recommendations based on report.

        Returns:
            List of recommendations.
        """
        recommendations = []

        # Based on score
        if self.score < 70:
            recommendations.append("URGENT: System score below 70%. Immediate attention required.")

        # Based on issues
        if len(self.critical_issues) > 0:
            recommendations.append(
                f"CRITICAL: {len(self.critical_issues)} critical issues must be resolved."
            )

        # Based on categories
        if self.scores:
            for category, info in self.scores.items():
                if category.startswith("_"):
                    continue
                if info.get("score", 100) < 70:
                    recommendations.append(
                        f"Category '{category}' scored below 70%. "
                        f"Improvement needed in this area."
                    )

        # Based on production readiness
        if not self.production_ready:
            recommendations.append(
                "System is not production ready. Review and resolve all "
                "critical issues before deployment."
            )

        return recommendations


class ReportGenerator:
    """Generates comprehensive diagnostic reports.

    Collects results from all validators and generates a complete report.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._report: DiagnosticReport | None = None

    def start_report(self, correlation_id: str = "") -> DiagnosticReport:
        """Start a new diagnostic report.

        Args:
            correlation_id: Optional correlation ID for tracking.

        Returns:
            New DiagnosticReport instance.
        """
        with self._lock:
            self._report = DiagnosticReport(correlation_id=correlation_id)
            return self._report

    def add_health_report(self, report: HealthCheckResult) -> None:
        """Add health check report.

        Args:
            report: Health check result.
        """
        with self._lock:
            if self._report:
                self._report.health_report = report
                self._update_totals(
                    report.component_checks,
                    len([c for c in report.component_checks if c.status.value != "healthy"]),
                )

    def add_readiness_report(self, report: ReadinessReport) -> None:
        """Add readiness check report.

        Args:
            report: Readiness check result.
        """
        with self._lock:
            if self._report:
                self._report.readiness_report = report
                self._update_totals(
                    report.checks,
                    len(report.critical_failures),
                )

    def add_liveness_report(self, report: LivenessReport) -> None:
        """Add liveness check report.

        Args:
            report: Liveness check result.
        """
        with self._lock:
            if self._report:
                self._report.liveness_report = report
                failed = len([c for c in report.checks if not c.passed])
                self._update_totals(report.checks, failed)

    def add_architecture_report(self, report: ArchitectureReport) -> None:
        """Add architecture validation report.

        Args:
            report: Architecture validation result.
        """
        with self._lock:
            if self._report:
                self._report.architecture_report = report
                self._update_totals_from_violations(
                    report.violations,
                    len([v for v in report.violations if v.severity == "critical"]),
                )

    def add_contract_report(self, report: ContractReport) -> None:
        """Add contract validation report.

        Args:
            report: Contract validation result.
        """
        with self._lock:
            if self._report:
                self._report.contract_report = report
                self._update_totals_from_violations(
                    report.violations,
                    len([v for v in report.violations if v.severity == "critical"]),
                )

    def add_dependency_report(self, report: DependencyReport) -> None:
        """Add dependency validation report.

        Args:
            report: Dependency validation result.
        """
        with self._lock:
            if self._report:
                self._report.dependency_report = report
                self._update_totals_from_issues(
                    report.issues,
                    len([i for i in report.issues if i.severity == "critical"]),
                )

    def add_integration_report(self, report: IntegrationReport) -> None:
        """Add integration validation report.

        Args:
            report: Integration validation result.
        """
        with self._lock:
            if self._report:
                self._report.integration_report = report
                self._update_totals_from_issues(
                    report.issues,
                    len([i for i in report.issues if i.severity == "critical"]),
                )

    def add_runtime_report(self, report: RuntimeReport) -> None:
        """Add runtime validation report.

        Args:
            report: Runtime validation result.
        """
        with self._lock:
            if self._report:
                self._report.runtime_report = report
                self._update_totals_from_issues(
                    report.issues,
                    len([i for i in report.issues if i.severity == "critical"]),
                )

    def add_performance_report(self, report: PerformanceReport) -> None:
        """Add performance profiling report.

        Args:
            report: Performance profiling result.
        """
        with self._lock:
            if self._report:
                self._report.performance_report = report

    def add_scores(self, scores: dict) -> None:
        """Add score breakdown.

        Args:
            scores: Score breakdown dictionary.
        """
        with self._lock:
            if self._report:
                self._report.scores = scores

    def finalize_report(self, score: float, status: str, duration_ms: int) -> DiagnosticReport:
        """Finalize and return the report.

        Args:
            score: Overall score.
            status: Production status.
            duration_ms: Total duration.

        Returns:
            Finalized DiagnosticReport.
        """
        with self._lock:
            if self._report:
                self._report.score = score
                self._report.status = status
                self._report.duration_ms = duration_ms
                self._report.production_ready = score >= 80.0
                return self._report
            return DiagnosticReport()

    def _update_totals(
        self,
        checks: list,
        failed: int,
    ) -> None:
        """Update total check counts.

        Args:
            checks: List of check results.
            failed: Number of failed checks.
        """
        if self._report:
            self._report.total_checks += len(checks)
            self._report.passed_checks += len(checks) - failed
            self._report.failed_checks += failed

    def _update_totals_from_violations(
        self,
        violations: list,
        critical: int,
    ) -> None:
        """Update totals from violation list.

        Args:
            violations: List of violations.
            critical: Number of critical violations.
        """
        if self._report:
            self._report.total_checks += len(violations)
            self._report.passed_checks += len(violations) - critical
            self._report.failed_checks += critical

    def _update_totals_from_issues(
        self,
        issues: list,
        critical: int,
    ) -> None:
        """Update totals from issues list.

        Args:
            issues: List of issues.
            critical: Number of critical issues.
        """
        if self._report:
            self._report.total_checks += len(issues)
            self._report.passed_checks += len(issues) - critical
            self._report.failed_checks += critical
