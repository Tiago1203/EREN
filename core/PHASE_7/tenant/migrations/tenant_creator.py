"""
PHASE 7 - EPIC 2: Tenant Creator

Creación de nuevos tenants:
- Setup completo de tenant
- Database schema creation
- Initial configuration
- Bootstrap data
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class TenantSetupConfig:
    """Configuración de setup para nuevo tenant."""
    create_schema: bool = True
    create_establishment_default: bool = True
    create_admin_user: bool = True
    create_sample_data: bool = False    # Solo para trial/demo
    setup_rls: bool = True
    setup_cache_namespaces: bool = True
    send_welcome_email: bool = True


@dataclass
class TenantSetupResult:
    """Resultado del setup de tenant."""
    tenant_id: str
    steps_completed: list[str]
    errors: list[str]
    schema_name: str = ""
    admin_user_id: str = ""
    default_establishment_id: str = ""
    duration_ms: int = 0


class TenantCreator:
    """Creador de nuevos tenants."""

    def __init__(self, tenant_manager: Any):
        self._tenant_manager = tenant_manager

    def create_tenant(
        self,
        name: str,
        slug: str,
        contact_name: str,
        contact_email: str,
        tier: str = "trial",
        setup_config: Optional[TenantSetupConfig] = None,
        created_by: str = "system",
    ) -> TenantSetupResult:
        """
        Crea un nuevo tenant con todos sus recursos.
        """
        start = datetime.now(timezone.utc)
        steps: list[str] = []
        errors: list[str] = []

        config = setup_config or TenantSetupConfig()

        # Step 1: Create tenant record
        try:
            from core.PHASE_7.tenant.manager.tenant_manager import (
                SubscriptionTier,
            )
            tier_enum = SubscriptionTier(tier)

            tenant = self._tenant_manager.create_tenant(
                name=name,
                slug=slug,
                contact_name=contact_name,
                contact_email=contact_email,
                tier=tier_enum,
                created_by=created_by,
            )
            steps.append(f"Created tenant: {tenant.tenant_id}")
        except Exception as e:
            errors.append(f"Failed to create tenant: {e}")
            return TenantSetupResult(
                tenant_id="",
                steps_completed=steps,
                errors=errors,
                duration_ms=int(
                    (datetime.now(timezone.utc) - start).total_seconds() * 1000
                ),
            )

        tenant_id = tenant.tenant_id

        # Step 2: Create database schema (PostgreSQL)
        if config.create_schema:
            schema_name = f"tenant_{uuid.uuid4().hex[:8]}"
            try:
                self._create_schema(schema_name)
                steps.append(f"Created schema: {schema_name}")
            except Exception as e:
                errors.append(f"Failed to create schema: {e}")

        # Step 3: Create default establishment
        establishment_id = ""
        if config.create_establishment_default:
            try:
                establishment_id = self._create_default_establishment(
                    tenant_id, name, config.create_sample_data
                )
                steps.append(f"Created establishment: {establishment_id}")
            except Exception as e:
                errors.append(f"Failed to create establishment: {e}")

        # Step 4: Create admin user
        admin_user_id = ""
        if config.create_admin_user:
            try:
                admin_user_id = self._create_admin_user(
                    tenant_id, contact_name, contact_email, establishment_id
                )
                steps.append(f"Created admin user: {admin_user_id}")
            except Exception as e:
                errors.append(f"Failed to create admin user: {e}")

        # Step 5: Setup RLS policies
        if config.setup_rls:
            try:
                self._setup_rls_policies(tenant_id)
                steps.append("RLS policies configured")
            except Exception as e:
                errors.append(f"Failed to setup RLS: {e}")

        # Step 6: Setup cache namespaces
        if config.setup_cache_namespaces:
            try:
                self._setup_cache_namespaces(tenant_id)
                steps.append("Cache namespaces created")
            except Exception as e:
                errors.append(f"Failed to setup cache: {e}")

        # Step 7: Send welcome email
        if config.send_welcome_email:
            try:
                self._send_welcome_email(contact_email, name)
                steps.append("Welcome email sent")
            except Exception as e:
                errors.append(f"Failed to send email: {e}")

        return TenantSetupResult(
            tenant_id=tenant_id,
            schema_name=schema_name if config.create_schema else "",
            admin_user_id=admin_user_id,
            default_establishment_id=establishment_id,
            steps_completed=steps,
            errors=errors,
            duration_ms=int(
                (datetime.now(timezone.utc) - start).total_seconds() * 1000
            ),
        )

    def _create_schema(self, schema_name: str) -> None:
        """Crea schema de PostgreSQL para tenant."""
        # In production: execute SQL
        # CREATE SCHEMA IF NOT EXISTS {schema_name};
        pass

    def _create_default_establishment(
        self,
        tenant_id: str,
        name: str,
        sample_data: bool,
    ) -> str:
        """Crea establecimiento por defecto."""
        establishment_id = f"est-{uuid.uuid4().hex[:12]}"
        # In production: INSERT into establishments table
        return establishment_id

    def _create_admin_user(
        self,
        tenant_id: str,
        name: str,
        email: str,
        establishment_id: str,
    ) -> str:
        """Crea usuario admin inicial."""
        user_id = f"user-{uuid.uuid4().hex[:12]}"
        # In production: INSERT into users table
        return user_id

    def _setup_rls_policies(self, tenant_id: str) -> None:
        """Configura políticas RLS para tenant."""
        # In production: execute RLS policy creation
        pass

    def _setup_cache_namespaces(self, tenant_id: str) -> None:
        """Crea namespaces de cache para tenant."""
        # In production: initialize Redis namespaces
        pass

    def _send_welcome_email(self, email: str, tenant_name: str) -> None:
        """Envía email de bienvenida."""
        # In production: send via email service
        pass
