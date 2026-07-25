"""
PHASE 7 - EPIC 0: Security Configuration

Configuración centralizada de seguridad:
- Security policies
- TLS/SSL configuration
- Session management
- Rate limiting
- Security headers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import secrets


class SecurityLevel(str, Enum):
    """Niveles de seguridad."""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"              # Hospitalario producción


class AllowedPurpose(str, Enum):
    """Propósitos de uso bajo HIPAA."""
    TREATMENT = "treatment"          # Tratamiento
    PAYMENT = "payment"              # Facturación
    OPERATIONS = "operations"        # Operaciones
    RESEARCH = "research"            # Investigación (anonimizado)
    PUBLIC_HEALTH = "public_health"  # Salud pública


@dataclass
class SecurityPolicy:
    """Política de seguridad."""
    policy_id: str
    name: str
    level: SecurityLevel
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    rules: dict = field(default_factory=dict)

    # TLS
    min_tls_version: str = "1.2"
    require_https: bool = True

    # Session
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    require_re_auth_for_phi: bool = True

    # Password
    min_password_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special: bool = True
    password_expiry_days: int = 90

    # Rate limiting
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    rate_limit_per_minute: int = 100

    # PHI
    require_phi_consent: bool = True
    phi_access_logging: bool = True
    auto_logout_on_inactivity_minutes: int = 15

    # MFA
    require_mfa: bool = True
    mfa_exempt_roles: list[str] = field(default_factory=list)

    # Encryption
    require_field_encryption: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90


@dataclass
class TLSConfig:
    """Configuración TLS."""
    min_version: str = "1.2"
    recommended_version: str = "1.3"
    cipher_suites: list[str] = field(default_factory=lambda: [
        "TLS_AES_256_GCM_SHA384",
        "TLS_AES_128_GCM_SHA256",
        "TLS_CHACHA20_POLY1305_SHA256",
    ])
    certificate_rotation_days: int = 90


@dataclass
class SessionConfig:
    """Configuración de sesión."""
    timeout_minutes: int = 30
    absolute_timeout_hours: int = 8
    max_concurrent: int = 3
    require_reauth_for_phi: bool = True
    reauth_grace_period_minutes: int = 5
    secure_cookie: bool = True
    http_only_cookie: bool = True
    same_site_cookie: str = "strict"
    session_token_length: int = 64


@dataclass
class RateLimitConfig:
    """Configuración de rate limiting."""
    login_attempts: int = 5
    lockout_minutes: int = 30
    api_requests_per_minute: int = 100
    burst_size: int = 20
    enable_progressive_lockout: bool = True


class SecurityConfigManager:
    """Gestor de configuración de seguridad."""

    DEFAULT_POLICIES: dict[SecurityLevel, SecurityPolicy] = {}

    def __init__(self):
        self._policies: dict[str, SecurityPolicy] = {}
        self._active_policy: Optional[SecurityPolicy] = None
        self._tls_config = TLSConfig()
        self._session_config = SessionConfig()
        self._rate_limit = RateLimitConfig()
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Inicializa políticas por defecto."""
        # Basic
        self._policies["basic"] = SecurityPolicy(
            policy_id="basic",
            name="Basic Security",
            level=SecurityLevel.BASIC,
            description="Security level for development",
            session_timeout_minutes=60,
            require_mfa=False,
            min_password_length=8,
        )

        # Standard
        self._policies["standard"] = SecurityPolicy(
            policy_id="standard",
            name="Standard Security",
            level=SecurityLevel.STANDARD,
            description="Standard security for internal use",
            session_timeout_minutes=30,
            require_mfa=True,
            require_phi_consent=True,
            auto_logout_on_inactivity_minutes=30,
        )

        # High (Hospitalario recomendado)
        self._policies["high"] = SecurityPolicy(
            policy_id="high",
            name="High Security - Hospitalario",
            level=SecurityLevel.HIGH,
            description="High security for hospital production environments",
            session_timeout_minutes=20,
            require_mfa=True,
            require_phi_consent=True,
            phi_access_logging=True,
            require_field_encryption=True,
            min_password_length=14,
            password_expiry_days=60,
            auto_logout_on_inactivity_minutes=15,
            max_login_attempts=3,
            lockout_duration_minutes=60,
            require_re_auth_for_phi=True,
        )

        # Maximum
        self._policies["maximum"] = SecurityPolicy(
            policy_id="maximum",
            name="Maximum Security",
            level=SecurityLevel.MAXIMUM,
            description="Maximum security for critical systems",
            session_timeout_minutes=15,
            require_mfa=True,
            require_phi_consent=True,
            phi_access_logging=True,
            require_field_encryption=True,
            min_password_length=16,
            password_expiry_days=30,
            auto_logout_on_inactivity_minutes=10,
            max_login_attempts=3,
            lockout_duration_minutes=120,
            require_re_auth_for_phi=True,
            mfa_exempt_roles=["emergency_override"],
        )

        self._active_policy = self._policies["high"]

    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Obtiene política por ID."""
        return self._policies.get(policy_id)

    def set_active_policy(self, policy_id: str) -> bool:
        """Activa una política."""
        policy = self._policies.get(policy_id)
        if policy:
            self._active_policy = policy
            return True
        return False

    def get_active_policy(self) -> SecurityPolicy:
        """Obtiene política activa."""
        return self._active_policy or self._policies["high"]

    def create_custom_policy(
        self,
        policy_id: str,
        name: str,
        base_on: SecurityLevel = SecurityLevel.STANDARD,
        **overrides,
    ) -> SecurityPolicy:
        """Crea política custom basada en una existente."""
        base = self._policies.get(base_on.value, self._policies["standard"])

        custom = SecurityPolicy(
            policy_id=policy_id,
            name=name,
            level=base.level,
            description=f"Custom policy: {name}",
            **{**dataclass_to_dict(base), **overrides},
        )
        self._policies[policy_id] = custom
        return custom

    def get_session_config(self) -> SessionConfig:
        return self._session_config

    def get_tls_config(self) -> TLSConfig:
        return self._tls_config

    def get_rate_limit_config(self) -> RateLimitConfig:
        return self._rate_limit

    def validate_password(self, password: str) -> tuple[bool, list[str]]:
        """Valida contraseña según política activa."""
        policy = self.get_active_policy()
        errors = []

        if len(password) < policy.min_password_length:
            errors.append(f"Mínimo {policy.min_password_length} caracteres")

        if policy.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Requiere mayúsculas")

        if policy.require_lowercase and not any(c.islower() for c in password):
            errors.append("Requiere minúsculas")

        if policy.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Requiere números")

        if policy.require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Requiere caracteres especiales")

        return len(errors) == 0, errors

    def generate_session_token(self) -> str:
        """Genera token de sesión seguro."""
        return secrets.token_urlsafe(64)

    def get_security_headers(self) -> dict[str, str]:
        """Obtiene headers de seguridad HTTP."""
        return {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


def dataclass_to_dict(obj) -> dict:
    """Convierte dataclass a dict."""
    result = {}
    for key, value in obj.__dict__.items():
        if not key.startswith("_"):
            result[key] = value
    return result
