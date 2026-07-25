"""PHASE 7 - EPIC 1: Audit System Tests."""
# pytest not available in this environment
from datetime import datetime, timezone, timedelta


class TestAuditLogger:
    """Tests para AuditLogger."""

    def test_audit_logger_instance(self):
        from core.PHASE_7.audit import AuditLogger, set_audit_logger, get_audit_logger
        logger = AuditLogger()
        set_audit_logger(logger)
        assert get_audit_logger() is not None

    def test_log_authentication_success(self):
        from core.PHASE_7.audit import AuditLogger, AuditCategory, AuditAction
        logger = AuditLogger()
        event = logger.log_authentication("user-001", "Dr. Smith", True, "192.168.1.1")
        assert event.event_id.startswith("audit-")
        assert event.category == AuditCategory.AUTHENTICATION
        assert event.action == AuditAction.LOGIN

    def test_log_phi_access(self):
        from core.PHASE_7.audit import AuditLogger, AuditCategory, AuditSeverity
        logger = AuditLogger()
        event = logger.log_phi_access("u1", "User", "CE", "paciente", "p1")
        assert event.is_phi_access is True
        assert event.category == AuditCategory.PHI_ACCESS
        assert event.severity == AuditSeverity.CRITICAL

    def test_log_data_modification(self):
        from core.PHASE_7.audit import AuditLogger, AuditCategory, AuditAction
        logger = AuditLogger()
        event = logger.log_data_modification("u1", "User", "CE", "equipo", "eq1", AuditAction.UPDATE, reason="Maint")
        assert event.category == AuditCategory.DATA_MODIFICATION
        assert event.action == AuditAction.UPDATE

    def test_hash_chain_integrity(self):
        from core.PHASE_7.audit import AuditLogger
        logger = AuditLogger()
        e1 = logger.log_authentication("u1", "User", True, "127.0.0.1")
        e2 = logger.log_phi_access("u1", "User", "CE", "paciente", "p1")
        assert len(e1.event_hash) == 64
        assert e2.previous_event_hash == e1.event_hash

    def test_get_phi_access_events(self):
        from core.PHASE_7.audit import AuditLogger
        logger = AuditLogger()
        logger.log_phi_access("u1", "User", "CE", "paciente", "p1")
        logger.log_phi_access("u1", "User", "CE", "paciente", "p2")
        logger.log_data_access("u1", "User", "CE", "equipo", "eq1")
        phi_events = logger.get_phi_access_events()
        assert len(phi_events) == 2

    def test_statistics(self):
        from core.PHASE_7.audit import AuditLogger
        logger = AuditLogger()
        logger.log_authentication("u1", "User", True, "127.0.0.1")
        logger.log_phi_access("u1", "User", "CE", "paciente", "p1")
        stats = logger.get_statistics()
        assert stats["total_events"] == 2
        assert stats["phi_access_count"] == 1
    def test_verify_chain_integrity(self):
        from core.PHASE_7.audit import AuditLogger
        logger = AuditLogger()
        logger.log_authentication("u1", "User", True, "127.0.0.1")
        logger.log_phi_access("u1", "User", "CE", "paciente", "p1")
        valid, errors = logger.verify_chain_integrity()
        assert valid is True


class TestAuditRepository:
    """Tests para AuditRepository."""

    def test_save_and_query(self):
        from core.PHASE_7.audit import AuditRepository
        repo = AuditRepository()
        repo.save_event({
            "event_id": "e1", "timestamp": datetime.now(timezone.utc),
            "actor_id": "u1", "actor_name": "User",
            "category": "phi_access", "action": "read",
            "resource_type": "paciente", "resource_id": "p1",
            "is_phi_access": True, "severity": "critical",
            "success": True, "event_hash": "", "previous_event_hash": "",
        })
        result = repo.query({"query_id": "test", "limit": 10, "sort_by": "timestamp", "sort_order": "desc"})
        assert result["total"] == 1

    def test_query_by_actor(self):
        from core.PHASE_7.audit import AuditRepository
        repo = AuditRepository()
        for i in range(3):
            repo.save_event({
                "event_id": f"e{i}", "timestamp": datetime.now(timezone.utc),
                "actor_id": "user-001", "actor_name": "User",
                "category": "data_access", "action": "read",
                "resource_type": "equipo", "resource_id": f"eq{i}",
                "is_phi_access": False, "severity": "low",
                "success": True, "event_hash": "", "previous_event_hash": "",
            })
        result = repo.query({"query_id": "test", "actor_ids": ["user-001"], "limit": 10, "sort_by": "timestamp", "sort_order": "desc"})
        assert result["total"] == 3


class TestQueryBuilder:
    """Tests para AuditQueryBuilder."""

    def test_query_builder_phi_only(self):
        from core.PHASE_7.audit import AuditQueryBuilder
        qb = AuditQueryBuilder().actor("u1").phi_only().last_days(7)
        q = qb.build()
        assert "u1" in q["actor_ids"]
        assert q["phi_access_only"] is True

    def test_preset_phi_access(self):
        from core.PHASE_7.audit import AuditQueryBuilder, QueryPreset
        qb = AuditQueryBuilder.from_preset(QueryPreset.PHI_ACCESS)
        assert qb.build()["phi_access_only"] is True

    def test_preset_hipaa_access_log(self):
        from core.PHASE_7.audit import AuditQueryBuilder, QueryPreset
        qb = AuditQueryBuilder.from_preset(QueryPreset.HIPAA_ACCESS_LOG)
        q = qb.build()
        assert q["phi_access_only"] is True
        assert q["limit"] == 1000

    def test_preset_fda_audit_trail(self):
        from core.PHASE_7.audit import AuditQueryBuilder, QueryPreset
        qb = AuditQueryBuilder.from_preset(QueryPreset.FDA_AUDIT_TRAIL)
        assert qb.build()["limit"] == 5000


class TestArchiveService:
    """Tests para ArchiveService."""

    def test_create_archive(self):
        from core.PHASE_7.audit import ArchiveService
        arch = ArchiveService()
        metadata = arch.create_archive(
            events=[{"event_id": f"e{i}"} for i in range(100)],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            rule_id="hipaa",
        )
        assert metadata.total_events == 100
        assert metadata.format.value == "json_gz"

    def test_archive_compression(self):
        from core.PHASE_7.audit import ArchiveService
        arch = ArchiveService()
        events = [{"data": "x" * 1000} for _ in range(100)]
        metadata = arch.create_archive(events, datetime(2024, 1, 1), datetime(2024, 12, 31), "hipaa")
        assert metadata.compressed_size_bytes < metadata.original_size_bytes

    def test_archive_integrity(self):
        from core.PHASE_7.audit import ArchiveService
        arch = ArchiveService()
        metadata = arch.create_archive([{"event_id": "e1"}] * 50, datetime(2024, 1, 1), datetime(2024, 12, 31), "hipaa")
        valid, _ = arch.verify_archive_integrity(metadata.archive_id)
        assert valid is True


class TestHIPAAReporter:
    """Tests para HIPAAReporter."""

    def test_generate_access_report(self):
        from core.PHASE_7.audit import HIPAAReporter, AuditRepository
        repo = AuditRepository()
        hipaa = HIPAAReporter(repo)
        report = hipaa.generate_access_report("tenant-001", datetime.now(timezone.utc) - timedelta(days=30), datetime.now(timezone.utc))
        assert report.compliance_score >= 0


class TestFDAReporter:
    """Tests para FDAReporter."""

    def test_cfr_part_11_summary(self):
        from core.PHASE_7.audit import FDAReporter, AuditRepository
        repo = AuditRepository()
        fda = FDAReporter(repo)
        summary = fda.generate_cfr_part_11_compliance_summary("tenant-001", 365)
        assert "requirements" in summary
        assert len(summary["requirements"]) >= 4


class TestISOReporter:
    """Tests para ISOReporter."""

    def test_management_review(self):
        from core.PHASE_7.audit import ISOReporter, AuditRepository
        repo = AuditRepository()
        iso = ISOReporter(repo)
        report = iso.generate_management_review_report("tenant-001", 90)
        assert report.effectiveness_score >= 0


class TestExportService:
    """Tests para ExportService."""

    def test_export_csv(self):
        from core.PHASE_7.audit import ExportService, AuditRepository, AuditLogger, ExportFormat
        repo = AuditRepository()
        logger = AuditLogger()
        exp = ExportService(repo, logger)
        data, ctype = exp.export_audit_events([{"event_id": "e1"}], ExportFormat.CSV)
        assert len(data) > 0
        assert "csv" in ctype

    def test_export_json(self):
        from core.PHASE_7.audit import ExportService, AuditRepository, AuditLogger, ExportFormat
        repo = AuditRepository()
        logger = AuditLogger()
        exp = ExportService(repo, logger)
        data, ctype = exp.export_audit_events([{"event_id": "e1"}], ExportFormat.JSON)
        assert len(data) > 0
        assert "json" in ctype


class TestAuditDashboard:
    """Tests para AuditDashboard."""

    def test_get_metrics(self):
        from core.PHASE_7.audit import AuditDashboard, AuditLogger, AuditRepository
        logger = AuditLogger()
        repo = AuditRepository()
        dash = AuditDashboard(logger, repo)
        metrics = dash.get_metrics()
        assert metrics.total_events_24h >= 0
        assert metrics.chain_integrity is True


class TestComplianceDashboard:
    """Tests para ComplianceDashboard."""

    def test_hipaa_compliance(self):
        from core.PHASE_7.audit import ComplianceDashboard, HIPAAReporter, FDAReporter, ISOReporter, AuditRepository, ComplianceStatus
        repo = AuditRepository()
        cdash = ComplianceDashboard(repo, HIPAAReporter(repo), FDAReporter(repo), ISOReporter(repo))
        hipaa = cdash.get_hipaa_compliance("tenant-001")
        assert hipaa.overall_score >= 0
        assert hipaa.status in ComplianceStatus

    def test_fda_compliance(self):
        from core.PHASE_7.audit import ComplianceDashboard, HIPAAReporter, FDAReporter, ISOReporter, AuditRepository
        repo = AuditRepository()
        cdash = ComplianceDashboard(repo, HIPAAReporter(repo), FDAReporter(repo), ISOReporter(repo))
        fda = cdash.get_fda_compliance("tenant-001")
        assert fda.overall_score >= 0

    def test_compliance_alerts(self):
        from core.PHASE_7.audit import ComplianceDashboard, HIPAAReporter, FDAReporter, ISOReporter, AuditRepository
        repo = AuditRepository()
        cdash = ComplianceDashboard(repo, HIPAAReporter(repo), FDAReporter(repo), ISOReporter(repo))
        alerts = cdash.get_compliance_alerts("tenant-001")
        assert isinstance(alerts, list)
