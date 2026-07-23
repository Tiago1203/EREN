"""Unit tests for EPIC 11: Knowledge Governance & Lifecycle."""

import pytest
import asyncio


class TestEPIC11Imports:
    """Tests for EPIC 11 module imports."""

    def test_import_epic11(self):
        """Test EPIC 11 module imports."""
        from core.PHASE_4.epic11_governance import (
            AuditEntry,
            KnowledgeSnapshot,
            GovernancePolicy,
        )
        assert AuditEntry is not None
        assert KnowledgeSnapshot is not None

    def test_import_lifecycle(self):
        """Test lifecycle module imports."""
        from core.PHASE_4.epic11_governance.lifecycle import (
            LifecycleStage,
            KnowledgeSnapshot,
            InMemoryLifecycleManager,
        )
        assert LifecycleStage is not None
        assert KnowledgeSnapshot is not None

    def test_import_compliance(self):
        """Test compliance module imports."""
        from core.PHASE_4.epic11_governance.compliance import (
            RetentionPolicy,
            GovernancePolicy,
            InMemoryComplianceManager,
        )
        assert RetentionPolicy is not None
        assert GovernancePolicy is not None

    def test_import_audit(self):
        """Test audit module imports."""
        from core.PHASE_4.epic11_governance.audit import (
            AuditAction,
            AuditEntry,
            InMemoryAuditManager,
        )
        assert AuditAction is not None
        assert AuditEntry is not None


class TestKnowledgeSnapshot:
    """Tests for KnowledgeSnapshot."""

    def test_snapshot_creation(self):
        """Test snapshot creation."""
        from core.PHASE_4.epic11_governance.lifecycle import (
            KnowledgeSnapshot,
            LifecycleStage,
        )
        
        snapshot = KnowledgeSnapshot(
            snapshot_id="snap_1",
            document_id="doc_1",
            content="Document content",
            content_hash="abc123",
            version="v1.0.0",
            stage=LifecycleStage.DRAFT,
        )
        
        assert snapshot.snapshot_id == "snap_1"
        assert snapshot.version == "v1.0.0"


class TestLifecycleManager:
    """Tests for InMemoryLifecycleManager."""

    @pytest.mark.asyncio
    async def test_create_snapshot(self):
        """Test creating snapshot."""
        from core.PHASE_4.epic11_governance.lifecycle import InMemoryLifecycleManager
        
        manager = InMemoryLifecycleManager()
        snapshot = await manager.create_snapshot("doc_1", "Content here")
        
        assert snapshot.document_id == "doc_1"
        assert snapshot.content_hash is not None

    @pytest.mark.asyncio
    async def test_get_snapshots(self):
        """Test getting snapshots."""
        from core.PHASE_4.epic11_governance.lifecycle import InMemoryLifecycleManager
        
        manager = InMemoryLifecycleManager()
        await manager.create_snapshot("doc_1", "Content 1")
        await manager.create_snapshot("doc_1", "Content 2")
        
        snapshots = await manager.get_snapshots("doc_1")
        
        assert len(snapshots) == 2


class TestGovernancePolicy:
    """Tests for GovernancePolicy."""

    def test_policy_creation(self):
        """Test policy creation."""
        from core.PHASE_4.epic11_governance.compliance import (
            GovernancePolicy,
            RetentionPolicy,
        )
        
        policy = GovernancePolicy(
            policy_id="pol_1",
            name="Clinical Standard",
            description="Standard clinical policy",
            retention_policy=RetentionPolicy.STANDARD,
        )
        
        assert policy.policy_id == "pol_1"
        assert policy.retention_policy == RetentionPolicy.STANDARD


class TestComplianceManager:
    """Tests for InMemoryComplianceManager."""

    @pytest.mark.asyncio
    async def test_add_policy(self):
        """Test adding policy."""
        from core.PHASE_4.epic11_governance.compliance import (
            GovernancePolicy,
            InMemoryComplianceManager,
            RetentionPolicy,
        )
        
        manager = InMemoryComplianceManager()
        policy = GovernancePolicy(
            policy_id="pol_1",
            name="Test",
            description="Test policy",
            retention_policy=RetentionPolicy.STANDARD,
        )
        
        result = await manager.add_policy(policy)
        
        assert result.policy_id == "pol_1"

    @pytest.mark.asyncio
    async def test_check_compliance(self):
        """Test checking compliance."""
        from core.PHASE_4.epic11_governance.compliance import (
            GovernancePolicy,
            InMemoryComplianceManager,
            RetentionPolicy,
            ComplianceStatus,
        )
        
        manager = InMemoryComplianceManager()
        policy = GovernancePolicy(
            policy_id="pol_1",
            name="Test",
            description="Test policy",
            retention_policy=RetentionPolicy.STANDARD,
        )
        
        await manager.add_policy(policy)
        await manager.apply_policy("doc_1", "pol_1")
        
        status = await manager.check_compliance("doc_1")
        
        assert status == ComplianceStatus.COMPLIANT


class TestAuditEntry:
    """Tests for AuditEntry."""

    def test_entry_creation(self):
        """Test audit entry creation."""
        from core.PHASE_4.epic11_governance.audit import (
            AuditEntry,
            AuditAction,
        )
        
        entry = AuditEntry(
            entry_id="entry_1",
            timestamp="2024-01-01T00:00:00",
            action=AuditAction.CREATED,
            entity_type="KnowledgeAsset",
            entity_id="asset_1",
        )
        
        assert entry.entry_id == "entry_1"
        assert entry.action == AuditAction.CREATED


class TestAuditManager:
    """Tests for InMemoryAuditManager."""

    @pytest.mark.asyncio
    async def test_log(self):
        """Test logging audit entry."""
        from core.PHASE_4.epic11_governance.audit import (
            InMemoryAuditManager,
            AuditAction,
        )
        
        manager = InMemoryAuditManager()
        entry = await manager.log(
            action=AuditAction.CREATED,
            entity_type="Document",
            entity_id="doc_1",
            user_id="user_1",
        )
        
        assert entry.action == AuditAction.CREATED
        assert entry.entity_id == "doc_1"

    @pytest.mark.asyncio
    async def test_query(self):
        """Test querying audit entries."""
        from core.PHASE_4.epic11_governance.audit import (
            InMemoryAuditManager,
            AuditAction,
            AuditQuery,
        )
        
        manager = InMemoryAuditManager()
        await manager.log(AuditAction.CREATED, "Document", "doc_1")
        await manager.log(AuditAction.UPDATED, "Document", "doc_2")
        
        query = AuditQuery(entity_type="Document")
        results = await manager.query(query)
        
        assert len(results) == 2


class TestLifecycleStages:
    """Tests for LifecycleStage."""

    def test_stages(self):
        """Test lifecycle stage enum."""
        from core.PHASE_4.epic11_governance.lifecycle import LifecycleStage
        
        assert LifecycleStage.DRAFT.value == "draft"
        assert LifecycleStage.PUBLISHED.value == "published"
        assert LifecycleStage.ARCHIVED.value == "archived"


class TestRetentionPolicies:
    """Tests for RetentionPolicy."""

    def test_policies(self):
        """Test retention policy enum."""
        from core.PHASE_4.epic11_governance.compliance import RetentionPolicy
        
        assert RetentionPolicy.PERMANENT.value == "permanent"
        assert RetentionPolicy.STANDARD.value == "standard"
        assert RetentionPolicy.SHORT_TERM.value == "short_term"


class TestAuditActions:
    """Tests for AuditAction."""

    def test_actions(self):
        """Test audit action enum."""
        from core.PHASE_4.epic11_governance.audit import AuditAction
        
        assert AuditAction.CREATED.value == "created"
        assert AuditAction.UPDATED.value == "updated"
        assert AuditAction.DELETED.value == "deleted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
