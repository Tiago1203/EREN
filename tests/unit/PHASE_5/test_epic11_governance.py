"""
Tests for EPIC 11: Multi-Agent Governance

Test suite for the Multi-Agent Governance.
"""

import pytest
from datetime import UTC, datetime

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.epic11_governance import (
    GovernanceService,
    GovernanceServiceConfig,
    PermissionService,
    AuditService,
    PolicyEngine,
    ComplianceValidator,
)

from core.PHASE_5.epic11_governance.domain import (
    AgentPolicy,
    PolicyType,
    PolicyStatus,
    AgentPermission,
    PermissionType,
    AgentAudit,
    AuditType,
    AuditStatus,
    GovernanceRule,
    RuleType,
    AgentVersion,
    VersionStatus,
    GovernanceReport,
    ReportType,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def governance_config():
    """Create governance config."""
    return GovernanceServiceConfig(
        enable_audit=True,
        enable_policy=True,
        enable_compliance=True,
        enable_permissions=True,
    )


@pytest.fixture
def governance_service(governance_config):
    """Create governance service."""
    return GovernanceService(config=governance_config)


# =============================================================================
# TEST GOVERNANCE SERVICE
# =============================================================================

class TestGovernanceService:
    """Tests for GovernanceService."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, governance_service, governance_config):
        """Test service initializes correctly."""
        assert governance_service.config == governance_config
        
        # Services should be initialized
        assert governance_service._permission_service is not None
        assert governance_service._audit_service is not None
        assert governance_service._policy_engine is not None
        assert governance_service._compliance_validator is not None
    
    @pytest.mark.asyncio
    async def test_service_initialize(self, governance_service):
        """Test service initialization method."""
        await governance_service.initialize()
    
    @pytest.mark.asyncio
    async def test_grant_permission(self, governance_service):
        """Test granting permission."""
        result = await governance_service.grant_permission(
            agent_id="agent_1",
            resource="patient_data",
            permission_type="read",
            granted_by="admin",
        )
        
        assert result is not None
        assert result.granted is True
        assert result.permission is not None
    
    @pytest.mark.asyncio
    async def test_create_audit(self, governance_service):
        """Test creating audit."""
        audit = await governance_service.create_audit(
            agent_id="agent_1",
            action="access_patient_record",
            performed_by="agent_1",
            audit_type="access",
        )
        
        assert audit is not None
        assert audit.agent_id == "agent_1"
        assert audit.audit_type == AuditType.ACCESS
    
    @pytest.mark.asyncio
    async def test_create_policy(self, governance_service):
        """Test creating policy."""
        policy = await governance_service.create_policy(
            name="Security Policy",
            policy_type="security",
            created_by="admin",
        )
        
        assert policy is not None
        assert policy.name == "Security Policy"
        assert policy.policy_type == PolicyType.SECURITY
    
    @pytest.mark.asyncio
    async def test_generate_report(self, governance_service):
        """Test generating report."""
        report = await governance_service.generate_report()
        
        assert report is not None
        assert report.report_type == ReportType.SUMMARY
    
    @pytest.mark.asyncio
    async def test_metrics(self, governance_service):
        """Test service metrics."""
        metrics = governance_service.get_metrics()
        
        assert "operations_count" in metrics
        assert "services_enabled" in metrics


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestAgentPolicy:
    """Tests for AgentPolicy."""
    
    def test_policy_creation(self):
        """Test policy creation."""
        policy = AgentPolicy(
            policy_id="policy_1",
            name="Test Policy",
            policy_type=PolicyType.SECURITY,
        )
        
        assert policy.policy_id == "policy_1"
        assert policy.name == "Test Policy"
        assert policy.status == PolicyStatus.DRAFT
    
    def test_activate_policy(self):
        """Test activating policy."""
        policy = AgentPolicy(name="Test")
        
        policy.activate()
        
        assert policy.status == PolicyStatus.ACTIVE
    
    def test_suspend_policy(self):
        """Test suspending policy."""
        policy = AgentPolicy(name="Test")
        
        policy.suspend()
        
        assert policy.status == PolicyStatus.SUSPENDED
    
    def test_add_rule(self):
        """Test adding rule."""
        policy = AgentPolicy(name="Test")
        
        policy.add_rule("require_authentication")
        
        assert "require_authentication" in policy.rules


class TestAgentPermission:
    """Tests for AgentPermission."""
    
    def test_permission_creation(self):
        """Test permission creation."""
        perm = AgentPermission(
            permission_id="perm_1",
            agent_id="agent_1",
            resource="data",
            permission_type=PermissionType.READ,
        )
        
        assert perm.permission_id == "perm_1"
        assert perm.granted is False
    
    def test_grant_permission(self):
        """Test granting permission."""
        perm = AgentPermission(
            agent_id="agent_1",
            resource="data",
        )
        
        perm.grant("admin")
        
        assert perm.granted is True
        assert perm.granted_by == "admin"
    
    def test_is_valid(self):
        """Test validity check."""
        perm = AgentPermission(
            agent_id="agent_1",
            resource="data",
        )
        
        assert perm.is_valid() is False
        
        perm.grant("admin")
        assert perm.is_valid() is True


class TestAgentAudit:
    """Tests for AgentAudit."""
    
    def test_audit_creation(self):
        """Test audit creation."""
        audit = AgentAudit(
            audit_id="audit_1",
            agent_id="agent_1",
            audit_type=AuditType.ACTION,
            action="test_action",
        )
        
        assert audit.audit_id == "audit_1"
        assert audit.status == AuditStatus.PENDING
    
    def test_complete_audit(self):
        """Test completing audit."""
        audit = AgentAudit(
            agent_id="agent_1",
            action="test",
        )
        
        audit.complete("Success")
        
        assert audit.status == AuditStatus.COMPLETED
        assert audit.result == "Success"
    
    def test_fail_audit(self):
        """Test failing audit."""
        audit = AgentAudit(
            agent_id="agent_1",
            action="test",
        )
        
        audit.fail("Error")
        
        assert audit.status == AuditStatus.FAILED
        assert audit.result == "Error"


class TestGovernanceRule:
    """Tests for GovernanceRule."""
    
    def test_rule_creation(self):
        """Test rule creation."""
        rule = GovernanceRule(
            rule_id="rule_1",
            name="Test Rule",
            rule_type=RuleType.PERMISSION,
        )
        
        assert rule.rule_id == "rule_1"
        assert rule.enabled is True
    
    def test_enable_disable(self):
        """Test enable/disable."""
        rule = GovernanceRule(name="Test")
        
        rule.disable()
        assert rule.enabled is False
        
        rule.enable()
        assert rule.enabled is True


class TestAgentVersion:
    """Tests for AgentVersion."""
    
    def test_version_creation(self):
        """Test version creation."""
        version = AgentVersion(
            version_id="v_1",
            agent_id="agent_1",
            version="1.0.0",
        )
        
        assert version.version_id == "v_1"
        assert version.version == "1.0.0"
        assert version.status == VersionStatus.DRAFT
    
    def test_release_version(self):
        """Test releasing version."""
        version = AgentVersion(
            agent_id="agent_1",
            version="1.0.0",
        )
        
        version.release()
        
        assert version.status == VersionStatus.RELEASED
        assert version.released_at is not None
    
    def test_deprecate_version(self):
        """Test deprecating version."""
        version = AgentVersion(
            agent_id="agent_1",
            version="1.0.0",
        )
        
        version.deprecate()
        
        assert version.status == VersionStatus.DEPRECATED
        assert version.deprecated_at is not None


class TestGovernanceReport:
    """Tests for GovernanceReport."""
    
    def test_report_creation(self):
        """Test report creation."""
        report = GovernanceReport(
            report_id="report_1",
            report_type=ReportType.SUMMARY,
            title="Test Report",
        )
        
        assert report.report_id == "report_1"
        assert len(report.findings) == 0
    
    def test_add_finding(self):
        """Test adding finding."""
        report = GovernanceReport(report_type=ReportType.SUMMARY)
        
        report.add_finding("Finding 1")
        
        assert "Finding 1" in report.findings
    
    def test_add_metric(self):
        """Test adding metric."""
        report = GovernanceReport(report_type=ReportType.SUMMARY)
        
        report.add_metric("count", 42)
        
        assert report.metrics["count"] == 42


# =============================================================================
# TEST SERVICES
# =============================================================================

class TestPermissionService:
    """Tests for PermissionService."""
    
    @pytest.mark.asyncio
    async def test_grant_permission(self):
        """Test granting permission."""
        service = PermissionService()
        
        result = await service.grant_permission(
            agent_id="agent_1",
            resource="data",
            permission_type=PermissionType.READ,
            granted_by="admin",
        )
        
        assert result.granted is True
        assert result.permission is not None
    
    @pytest.mark.asyncio
    async def test_check_permission(self):
        """Test checking permission."""
        service = PermissionService()
        
        await service.grant_permission(
            agent_id="agent_1",
            resource="data",
            permission_type=PermissionType.READ,
            granted_by="admin",
        )
        
        has_permission = await service.check_permission(
            agent_id="agent_1",
            resource="data",
            permission_type=PermissionType.READ,
        )
        
        assert has_permission is True


class TestAuditService:
    """Tests for AuditService."""
    
    @pytest.mark.asyncio
    async def test_create_audit(self):
        """Test creating audit."""
        service = AuditService()
        
        audit = await service.create_audit(
            agent_id="agent_1",
            audit_type=AuditType.ACTION,
            action="test_action",
            performed_by="system",
        )
        
        assert audit is not None
        assert audit.agent_id == "agent_1"
    
    @pytest.mark.asyncio
    async def test_generate_report(self):
        """Test generating report."""
        service = AuditService()
        
        await service.create_audit(
            agent_id="agent_1",
            audit_type=AuditType.ACTION,
            action="test",
            performed_by="system",
        )
        
        report = await service.generate_report()
        
        assert report is not None
        assert report.report_type == ReportType.AUDIT


class TestPolicyEngine:
    """Tests for PolicyEngine."""
    
    @pytest.mark.asyncio
    async def test_create_policy(self):
        """Test creating policy."""
        engine = PolicyEngine()
        
        policy = await engine.create_policy(
            name="Test Policy",
            policy_type=PolicyType.SECURITY,
            created_by="admin",
        )
        
        assert policy is not None
        assert policy.name == "Test Policy"
    
    @pytest.mark.asyncio
    async def test_get_active_policies(self):
        """Test getting active policies."""
        engine = PolicyEngine()
        
        policy = await engine.create_policy(
            name="Active Policy",
            policy_type=PolicyType.SECURITY,
            created_by="admin",
        )
        policy.activate()
        
        active = await engine.get_active_policies()
        
        assert len(active) >= 1


class TestComplianceValidator:
    """Tests for ComplianceValidator."""
    
    @pytest.mark.asyncio
    async def test_validate_system(self):
        """Test validating system."""
        validator = ComplianceValidator()
        
        result = await validator.validate_system()
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self):
        """Test generating compliance report."""
        validator = ComplianceValidator()
        
        report = await validator.generate_compliance_report()
        
        assert report is not None
        assert report.report_type == ReportType.COMPLIANCE


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_policy_type_values(self):
        """Test PolicyType enum values."""
        assert PolicyType.SECURITY.value == "security"
        assert PolicyType.ACCESS.value == "access"
    
    def test_permission_type_values(self):
        """Test PermissionType enum values."""
        assert PermissionType.READ.value == "read"
        assert PermissionType.WRITE.value == "write"
        assert PermissionType.EXECUTE.value == "execute"
    
    def test_audit_type_values(self):
        """Test AuditType enum values."""
        assert AuditType.ACTION.value == "action"
        assert AuditType.ACCESS.value == "access"
    
    def test_audit_status_values(self):
        """Test AuditStatus enum values."""
        assert AuditStatus.PENDING.value == "pending"
        assert AuditStatus.COMPLETED.value == "completed"
    
    def test_rule_type_values(self):
        """Test RuleType enum values."""
        assert RuleType.PERMISSION.value == "permission"
        assert RuleType.RESTRICTION.value == "restriction"
    
    def test_version_status_values(self):
        """Test VersionStatus enum values."""
        assert VersionStatus.DRAFT.value == "draft"
        assert VersionStatus.RELEASED.value == "released"
    
    def test_report_type_values(self):
        """Test ReportType enum values."""
        assert ReportType.COMPLIANCE.value == "compliance"
        assert ReportType.SECURITY.value == "security"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
