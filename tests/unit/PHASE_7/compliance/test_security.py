"""
Tests for PHASE 7 - EPIC 0: Compliance & Security Foundation

Security module tests:
- Encryption Service
- Access Control
- Data Classification
- Security Configuration
"""

# pytest not available in this environment
from datetime import datetime, timedelta


class TestEncryptionService:
    """Tests for EncryptionService."""

    def test_encrypt_decrypt_aes_256(self):
        """Test basic AES-256 encryption/decryption."""
        from core.PHASE_7.compliance.security import EncryptionService

        service = EncryptionService()
        service.generate_master_key()

        plaintext = "PHI: Patient John Doe, SSN: 123-45-6789"
        encrypted = service.encrypt(plaintext)

        assert encrypted.ciphertext is not None
        assert encrypted.nonce is not None
        assert encrypted.key_id != ""
        assert encrypted.algorithm in ("aes-256-gcm", "aes-256-cbc-fallback")

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption roundtrip returns original."""
        from core.PHASE_7.compliance.security import EncryptionService

        service = EncryptionService()
        service.generate_master_key()

        original = "Sensitive clinical data"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original

    def test_encrypt_to_base64_roundtrip(self):
        """Test Base64 encoding roundtrip."""
        from core.PHASE_7.compliance.security import EncryptionService

        service = EncryptionService()
        service.generate_master_key()

        original = "Patient diagnosis: Diabetes Type 2"
        encrypted_b64 = service.encrypt_to_base64(original)
        decrypted = service.decrypt_from_base64(encrypted_b64)

        assert decrypted == original
        assert encrypted_b64 != original

    def test_tokenize_detokenize(self):
        """Test PHI tokenization."""
        from core.PHASE_7.compliance.security import EncryptionService

        service = EncryptionService()
        service.generate_master_key()

        ssn = "123-45-6789"
        token = service.tokenize(ssn)

        assert token.startswith("tok_")
        assert token != ssn
        assert service.detokenize(token) == ssn

    def test_hash_phi_verification(self):
        """Test PHI hashing for search."""
        from core.PHASE_7.compliance.security import EncryptionService

        service = EncryptionService()
        service.generate_master_key()

        ssn = "987-65-4321"
        hashed = service.hash_phi(ssn)

        # Hash should contain salt:hash format
        assert ":" in hashed
        assert service.verify_phi_hash(ssn, hashed)
        assert not service.verify_phi_hash("wrong-value", hashed)


class TestAccessControl:
    """Tests for AccessControlService."""

    def test_grant_and_check_permission(self):
        """Test RBAC permission granting."""
        from core.PHASE_7.compliance.security import (
            AccessControlService,
            AccessContext,
            Role,
            Permission,
        )

        acs = AccessControlService()
        acs.grant_access(
            user_id="user-001",
            role=Role.CLINICAL_ENGINEER,
        )

        ctx = AccessContext(
            user_id="user-001",
            role=Role.CLINICAL_ENGINEER,
        )

        decision = acs.check_permission(ctx, Permission.EQUIPOS_READ)
        assert decision.granted

        decision = acs.check_permission(ctx, Permission.USERS_WRITE)
        assert not decision.granted

    def test_revoke_access(self):
        """Test access revocation."""
        from core.PHASE_7.compliance.security import (
            AccessControlService,
            AccessContext,
            Role,
            Permission,
        )

        acs = AccessControlService()
        acs.grant_access(user_id="user-002", role=Role.VIEWER)
        acs.revoke_access("user-002")

        ctx = AccessContext(user_id="user-002", role=Role.VIEWER)
        decision = acs.check_permission(ctx, Permission.EQUIPOS_READ)

        assert not decision.granted

    def test_emergency_access_override(self):
        """Test emergency access bypass."""
        from core.PHASE_7.compliance.security import (
            AccessControlService,
            AccessContext,
            Role,
            Permission,
        )

        acs = AccessControlService()
        acs.grant_access(user_id="user-003", role=Role.VIEWER)

        ctx = AccessContext(
            user_id="user-003",
            role=Role.VIEWER,
            is_emergency=True,
            purpose_of_use="treatment",
        )

        # Emergency access allows read on PHI
        decision = acs.check_permission(ctx, Permission.PHI_READ)
        assert decision.granted


class TestDataClassifier:
    """Tests for DataClassifier."""

    def test_phi_field_classification(self):
        """Test PHI field detection."""
        from core.PHASE_7.compliance.security import DataClassifier

        classifier = DataClassifier()

        result = classifier.classify("patient_name", "John Doe")
        assert result.category.value == "phi"
        assert result.is_phi
        assert result.sensitivity.value == "restricted"
        assert result.requires_encryption
        assert result.requires_audit

    def test_pii_field_classification(self):
        """Test PII field detection."""
        from core.PHASE_7.compliance.security import DataClassifier

        classifier = DataClassifier()

        # employee_id is PII but not PHI (no patient identifier)
        result = classifier.classify("employee_id", "EMP-12345")
        assert result.category.value == "pii"
        assert result.is_pii
        assert not result.is_phi  # Not PHI under HIPAA
        assert result.requires_encryption

    def test_operational_field_classification(self):
        """Test operational field detection."""
        from core.PHASE_7.compliance.security import DataClassifier

        classifier = DataClassifier()

        result = classifier.classify("equipo_nombre", "Infusion Pump")
        assert result.category.value == "operational"
        assert not result.is_phi
        assert not result.is_pii


class TestSecurityConfigManager:
    """Tests for SecurityConfigManager."""

    def test_default_policies_exist(self):
        """Test that default policies are loaded."""
        from core.PHASE_7.compliance.security import SecurityConfigManager

        manager = SecurityConfigManager()

        assert manager.get_policy("basic") is not None
        assert manager.get_policy("high") is not None
        assert manager.get_active_policy().policy_id == "high"

    def test_password_validation(self):
        """Test password validation against policy."""
        from core.PHASE_7.compliance.security import SecurityConfigManager

        manager = SecurityConfigManager()

        # Weak password
        valid, errors = manager.validate_password("weak")
        assert not valid
        assert len(errors) > 0

        # Strong password
        valid, errors = manager.validate_password("SecurePass123!")
        assert valid or len(errors) == 0

    def test_security_headers(self):
        """Test HTTP security headers generation."""
        from core.PHASE_7.compliance.security import SecurityConfigManager

        manager = SecurityConfigManager()
        headers = manager.get_security_headers()

        assert "Strict-Transport-Security" in headers
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
