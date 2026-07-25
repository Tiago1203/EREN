"""PHASE 7 - EPIC 2: Multi-Tenant Architecture Tests."""
# pytest not available in this environment
from datetime import datetime, timezone


class TestTenantManager:
    """Tests para TenantManager."""

    def test_create_starter_tenant(self):
        from core.PHASE_7.tenant import TenantManager, SubscriptionTier
        mgr = TenantManager()
        t = mgr.create_tenant("Hospital Test", "hospital-test", tier=SubscriptionTier.STARTER, contact_email="admin@test.com")
        assert t.subscription.tier == SubscriptionTier.STARTER
        assert t.config.max_users == 50

    def test_create_enterprise_tenant(self):
        from core.PHASE_7.tenant import TenantManager, SubscriptionTier
        mgr = TenantManager()
        t = mgr.create_tenant("Hospital Ent", "hospital-ent", tier=SubscriptionTier.ENTERPRISE, contact_email="admin@ent.com")
        assert t.subscription.tier == SubscriptionTier.ENTERPRISE
        assert t.config.custom_branding is True

    def test_get_by_slug(self):
        from core.PHASE_7.tenant import TenantManager
        mgr = TenantManager()
        mgr.create_tenant("H1", "h1", "A", "a@b.com")
        t = mgr.get_tenant_by_slug("h1")
        assert t is not None and t.name == "H1"

    def test_suspend_and_activate(self):
        from core.PHASE_7.tenant import TenantManager, TenantStatus, SubscriptionTier
        mgr = TenantManager()
        t = mgr.create_tenant("H2", "h2", tier=SubscriptionTier.TRIAL, contact_name="A", contact_email="a@b.com")
        mgr.suspend_tenant(t.tenant_id, "test")
        assert mgr.get_tenant(t.tenant_id).status == TenantStatus.SUSPENDED
        mgr.activate_tenant(t.tenant_id)
        assert mgr.get_tenant(t.tenant_id).status == TenantStatus.ACTIVE

    def test_list_tenants(self):
        from core.PHASE_7.tenant import TenantManager
        mgr = TenantManager()
        mgr.create_tenant("H3", "h3", contact_name="A", contact_email="a@b.com")
        assert len(mgr.list_tenants()) >= 1

    def test_statistics(self):
        from core.PHASE_7.tenant import TenantManager
        mgr = TenantManager()
        mgr.create_tenant("H4", "h4", contact_name="A", contact_email="a@b.com")
        stats = mgr.get_tenant_statistics()
        assert stats["total"] >= 1


class TestTenantContext:
    """Tests para TenantContext."""

    def test_set_and_get_context(self):
        from core.PHASE_7.tenant import set_tenant_context, get_tenant_context_manager
        ctx = set_tenant_context("t1", "u1", "admin")
        assert ctx.tenant_id == "t1"
        assert ctx.user_id == "u1"
        mgr = get_tenant_context_manager()
        assert mgr.get_required_context().tenant_id == "t1"

    def test_clear_context(self):
        from core.PHASE_7.tenant import set_tenant_context, get_tenant_context_manager
        set_tenant_context("t1", "u1", "admin")
        mgr = get_tenant_context_manager()
        mgr.clear_context()
        assert mgr.get_context() is None


class TestTenantResolver:
    """Tests para TenantResolver."""

    def test_resolve_from_header(self):
        from core.PHASE_7.tenant import TenantManager, TenantResolver, SubscriptionTier
        mgr = TenantManager()
        t = mgr.create_tenant("H5", "h5", tier=SubscriptionTier.TRIAL, contact_name="A", contact_email="a@b.com")
        resolver = TenantResolver(mgr)
        result = resolver.resolve_from_header({"X-Tenant-ID": t.tenant_id})
        assert result is not None and result.source == "header"

    def test_resolve_from_subdomain(self):
        from core.PHASE_7.tenant import TenantManager, TenantResolver, SubscriptionTier
        mgr = TenantManager()
        t = mgr.create_tenant("H6", "h6", tier=SubscriptionTier.TRIAL, contact_name="A", contact_email="a@b.com")
        resolver = TenantResolver(mgr)
        result = resolver.resolve_from_subdomain("h6.orma.systems")
        assert result is not None and result.tenant_id == t.tenant_id

    def test_resolve_with_default(self):
        from core.PHASE_7.tenant import TenantManager, TenantResolver
        mgr = TenantManager()
        resolver = TenantResolver(mgr)
        resolver.set_default_tenant("default-id")
        result = resolver.resolve()
        assert result.tenant_id == "default-id"


class TestTenantValidator:
    """Tests para TenantValidator."""

    def test_valid_slug(self):
        from core.PHASE_7.tenant import TenantValidator
        v = TenantValidator()
        assert v.validate_slug("valid-slug-123").valid is True

    def test_invalid_short_slug(self):
        from core.PHASE_7.tenant import TenantValidator
        v = TenantValidator()
        assert v.validate_slug("ab").valid is False

    def test_invalid_reserved_slug(self):
        from core.PHASE_7.tenant import TenantValidator
        v = TenantValidator()
        assert v.validate_slug("admin").valid is False


class TestRowLevelSecurity:
    """Tests para Row-Level Security."""

    def test_protected_tables(self):
        from core.PHASE_7.tenant import RowLevelSecurityManager
        rls = RowLevelSecurityManager()
        assert len(rls.get_protected_tables()) > 0
        assert "users" in rls.get_protected_tables()

    def test_generate_policy(self):
        from core.PHASE_7.tenant import RowLevelSecurityManager
        rls = RowLevelSecurityManager()
        policy = rls.get_tenant_policy("equipment")
        assert policy.table_name == "equipment"
        assert "equipment" in policy.policy_name

    def test_generate_set_tenant_sql(self):
        from core.PHASE_7.tenant import RowLevelSecurityManager
        rls = RowLevelSecurityManager()
        sql = rls.generate_set_tenant_sql("tenant-123")
        assert "SET app.current_tenant" in sql
        assert "tenant-123" in sql


class TestQueryFilter:
    """Tests para QueryFilter."""

    def test_get_tenant_filter(self):
        from core.PHASE_7.tenant import set_tenant_context, get_tenant_context_manager, QueryFilter
        set_tenant_context("t1", "u1", "admin")
        qf = QueryFilter(get_tenant_context_manager())
        assert qf.get_tenant_filter("users") == {"tenant_id": "t1"}

    def test_global_tables_bypass(self):
        from core.PHASE_7.tenant import get_tenant_context_manager, QueryFilter
        qf = QueryFilter(get_tenant_context_manager())
        assert qf.get_tenant_filter("tenants") is None


class TestDataIsolation:
    """Tests para DataIsolation."""

    def test_can_access_table(self):
        from core.PHASE_7.tenant import DataIsolation, DataBoundary, get_tenant_context_manager
        di = DataIsolation(get_tenant_context_manager())
        di.register_boundary(DataBoundary(tenant_id="t1", allowed_tables=["*"], denied_tables=[]))
        assert di.can_access_table("equipment", "t1") is True

    def test_sanitize_export(self):
        from core.PHASE_7.tenant import DataIsolation, DataBoundary, get_tenant_context_manager
        di = DataIsolation(get_tenant_context_manager())
        di.register_boundary(DataBoundary(tenant_id="t1", allowed_tables=["*"], denied_tables=[]))
        data = [{"id": 1, "password_hash": "secret", "tenant_id": "t1"}]
        sanitized = di.sanitize_export_data("users", data, "t1")
        assert len(sanitized) == 1
        assert "password_hash" not in sanitized[0]


class TestCacheIsolation:
    """Tests para CacheIsolation."""

    def test_make_key(self):
        from core.PHASE_7.tenant import CacheIsolation, get_tenant_context_manager
        ci = CacheIsolation(get_tenant_context_manager())
        key = ci.make_key("equipment", "eq-001", tenant_id="t1")
        assert "equipment" in key.to_string()
        assert "t1" in key.to_string()

    def test_tenant_rate_limiter(self):
        from core.PHASE_7.tenant import TenantRateLimiter
        limiter = TenantRateLimiter()
        assert limiter.get_limit("starter") == 1000
        assert limiter.get_limit("enterprise") == 50000


class TestQuotaManager:
    """Tests para QuotaManager."""

    def test_create_quotas(self):
        from core.PHASE_7.tenant import QuotaManager
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        assert qm.get_tenant_quotas("t1") is not None

    def test_check_quota(self):
        from core.PHASE_7.tenant import QuotaManager, ResourceType
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        allowed, reason, remaining = qm.check_quota("t1", ResourceType.USERS, 5)
        assert allowed is True

    def test_consume_quota(self):
        from core.PHASE_7.tenant import QuotaManager, ResourceType
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        assert qm.consume_quota("t1", ResourceType.USERS, 5) is True

    def test_usage_report(self):
        from core.PHASE_7.tenant import QuotaManager
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        report = qm.get_usage_report("t1")
        assert "quotas" in report


class TestUsageTracker:
    """Tests para UsageTracker."""

    def test_track_usage(self):
        from core.PHASE_7.tenant import QuotaManager, UsageTracker
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        ut = UsageTracker(qm)
        ut.track("t1", "users", 5)
        assert ut.get_current_usage("t1", "users") == 5

    def test_usage_history(self):
        from core.PHASE_7.tenant import QuotaManager, UsageTracker
        qm = QuotaManager()
        qm.create_tenant_quotas("t1", "starter")
        ut = UsageTracker(qm)
        history = ut.get_usage_history("t1", "users", 7)
        assert len(history) == 7


class TestTenantExporter:
    """Tests para TenantExporter."""

    def test_create_job(self):
        from core.PHASE_7.tenant import TenantExporter, ExportConfig, get_tenant_context_manager, DataIsolation
        di = DataIsolation(get_tenant_context_manager())
        tei = TenantExporter(get_tenant_context_manager(), di)
        job = tei.create_export_job("t1", ExportConfig(include_users=True))
        assert job.tenant_id == "t1"

    def test_estimate_size(self):
        from core.PHASE_7.tenant import TenantExporter, ExportConfig, get_tenant_context_manager, DataIsolation
        di = DataIsolation(get_tenant_context_manager())
        tei = TenantExporter(get_tenant_context_manager(), di)
        est = tei.estimate_export_size("t1", ExportConfig())
        assert "total_bytes" in est


class TestTenantImporter:
    """Tests para TenantImporter."""

    def test_validate_invalid_file(self):
        from core.PHASE_7.tenant import TenantImporter, get_tenant_context_manager, DataIsolation
        di = DataIsolation(get_tenant_context_manager())
        ti = TenantImporter(get_tenant_context_manager(), di)
        valid, errors = ti.validate_import_file("/nonexistent.json", "t1")
        assert valid is False


class TestTenantAPIService:
    """Tests para TenantAPIService."""

    def test_list_tenants(self):
        from core.PHASE_7.tenant import TenantManager, QuotaManager, UsageTracker, QuotaEnforcer, TenantAPIService
        from dataclasses import dataclass
        @dataclass
        class Req:
            status = None; tier = None; limit = 100; offset = 0
        mgr = TenantManager(); qm = QuotaManager(); ut = UsageTracker(qm); qe = QuotaEnforcer(qm, ut)
        api = TenantAPIService(mgr, qm, ut, qe)
        result = api.list_tenants(Req())
        assert "tenants" in result


class TestAdminAPIService:
    """Tests para AdminAPIService."""

    def test_system_statistics(self):
        from core.PHASE_7.tenant import TenantManager, QuotaManager, RowLevelSecurityManager, CacheIsolation, AdminAPIService, get_tenant_context_manager
        mgr = TenantManager(); qm = QuotaManager(); rls = RowLevelSecurityManager(); ci = CacheIsolation(get_tenant_context_manager())
        admin = AdminAPIService(mgr, qm, rls, ci)
        stats = admin.get_system_statistics()
        assert stats.total_tenants >= 0

    def test_compliance_report(self):
        from core.PHASE_7.tenant import TenantManager, QuotaManager, RowLevelSecurityManager, CacheIsolation, AdminAPIService, get_tenant_context_manager
        mgr = TenantManager(); qm = QuotaManager(); rls = RowLevelSecurityManager(); ci = CacheIsolation(get_tenant_context_manager())
        admin = AdminAPIService(mgr, qm, rls, ci)
        report = admin.get_cross_tenant_report("compliance_summary")
        assert report["report_type"] == "compliance_summary"
