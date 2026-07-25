"""PHASE 7 - EPIC 5: Admin Panel & Migration Tests."""


class TestAdminDomain:
    def test_user_model(self):
        from core.PHASE_7.admin.domain.user import User, UserStatus
        u = User(user_id="u1", email="a@b.com", full_name="Test", status=UserStatus.ACTIVE)
        assert u.user_id == "u1"
        assert u.status == UserStatus.ACTIVE

    def test_role_model(self):
        from core.PHASE_7.admin.domain.user import Role, RoleType
        r = Role(role_id="r1", name="Admin", role_type=RoleType.SYSTEM_ADMIN, description="Admin")
        assert r.role_id == "r1"
        assert r.role_type == RoleType.SYSTEM_ADMIN


class TestAdminService:
    def test_create_user(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        svc = AdminService()
        user = svc.create_user("a@b.com", "Test User", [], "tenant-1")
        assert user["email"] == "a@b.com"
        assert user["tenant_id"] == "tenant-1"

    def test_get_user(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        svc = AdminService()
        user = svc.create_user("c@d.com", "Test", [], None)
        found = svc.get_user(user["user_id"])
        assert found is not None
        assert found["email"] == "c@d.com"

    def test_create_role(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        svc = AdminService()
        role = svc.create_role("Admin", "system_admin", "Full access", [])
        assert role["name"] == "Admin"
        assert role["is_system"] is True

    def test_assign_role(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        svc = AdminService()
        user = svc.create_user("e@f.com", "Test", [], "t1")
        role = svc.create_role("Admin", "system_admin", "Full", [])
        ok = svc.assign_role_to_user(user["user_id"], role["role_id"], "admin")
        assert ok is True

    def test_overview(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        svc = AdminService()
        overview = svc.get_system_overview()
        assert "total_users" in overview


class TestMigrationService:
    def test_migrate_equipment(self):
        from core.PHASE_7.admin.services.migration_service import MigrationService
        mig = MigrationService()
        report = mig.migrate_equipment([
            {"id": "eq1", "name": "MRI", "serial_number": "SN1"},
            {"id": "eq2", "name": "CT", "serial_number": "SN2"},
        ], "tenant-1")
        assert report.migrated == 2

    def test_migrate_kpis(self):
        from core.PHASE_7.admin.services.migration_service import MigrationService
        mig = MigrationService()
        report = mig.migrate_kpis([{"id": "k1", "name": "Uptime", "value": 99.9}], "tenant-1")
        assert report.migrated == 1

    def test_migration_status(self):
        from core.PHASE_7.admin.services.migration_service import MigrationService
        mig = MigrationService()
        status = mig.get_migration_status()
        assert "total_jobs" in status


class TestAdminAPI:
    def test_list_users(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        from core.PHASE_7.admin.api.admin_api import AdminAPI
        svc = AdminService()
        svc.create_user("x@y.com", "Test", [], None)
        api = AdminAPI(svc, None)
        r = api.list_users()
        assert r.success is True
        assert r.data["count"] >= 1

    def test_get_overview(self):
        from core.PHASE_7.admin.services.admin_service import AdminService
        from core.PHASE_7.admin.api.admin_api import AdminAPI
        api = AdminAPI(AdminService(), None)
        r = api.get_overview()
        assert r.success is True

    def test_migration_status(self):
        from core.PHASE_7.admin.services.migration_service import MigrationService
        from core.PHASE_7.admin.api.admin_api import AdminAPI
        api = AdminAPI(None, MigrationService())
        r = api.get_migration_status()
        assert r.success is True
