"""
PHASE 7 - EPIC 2: Tenant Validator

Validación de configuración de tenant:
- Config schema validation
- Plan limits enforcement
- Compliance requirements
- SLA validation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Resultado de validación."""
    valid: bool
    errors: list[str]
    warnings: list[str]


class TenantValidator:
    """Validador de configuración de tenants."""

    def validate_tenant_config(
        self,
        tenant: Any,
        subscription_tier: str,
    ) -> ValidationResult:
        """Valida configuración completa de un tenant."""
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Compliance requirements
        if tenant.config.allow_phi:
            if not tenant.hipaa_business_associate:
                errors.append("PHI access requires HIPAA Business Associate Agreement")
            if not tenant.data_processing_agreement:
                errors.append("PHI access requires Data Processing Agreement")

        # 2. Plan limits
        tier_limits = self._get_tier_limits(subscription_tier)
        if tenant.config.max_users > tier_limits.get("max_users", float("inf")):
            errors.append(f"max_users exceeds {subscription_tier} plan limit")

        if tenant.config.max_establishments > tier_limits.get("max_establishments", float("inf")):
            errors.append(f"max_establishments exceeds {subscription_tier} plan limit")

        # 3. Retention policy
        if tenant.config.retention_days < 2190:  # HIPAA minimum 6 years
            warnings.append("Retention period below HIPAA recommended minimum (6 years)")

        if tenant.config.retention_days > 36500:  # 100 years max
            errors.append("Retention period exceeds maximum (100 years)")

        # 4. GDPR compliance for EU tenants
        if tenant.country in self._eu_countries():
            if not tenant.gdpr_compliant:
                warnings.append("EU tenant should be GDPR compliant")

        # 5. Required fields
        if not tenant.name:
            errors.append("Tenant name is required")
        if not tenant.slug:
            errors.append("Tenant slug is required")
        if not tenant.contact or not tenant.contact.email:
            errors.append("Contact email is required")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_subscription(
        self,
        tenant: Any,
    ) -> ValidationResult:
        """Valida suscripción activa."""
        errors: list[str] = []
        warnings: list[str] = []

        if not tenant.subscription:
            errors.append("No subscription found")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        sub = tenant.subscription

        if not sub.is_active:
            errors.append("Subscription is not active")

        if sub.end_date:
            from datetime import datetime, timezone
            if sub.end_date < datetime.now(timezone.utc):
                errors.append("Subscription has expired")
            elif (sub.end_date - datetime.now(timezone.utc)).days < 30:
                warnings.append("Subscription expires within 30 days")

        # Check limits
        tier_limits = self._get_tier_limits(sub.tier.value)
        usage = self._estimate_usage(tenant)

        if usage["users"] > tier_limits.get("max_users", float("inf")):
            errors.append(f"User count ({usage['users']}) exceeds plan limit ({tier_limits['max_users']})")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_can_access_phi(self, tenant: Any) -> ValidationResult:
        """Valida que tenant puede acceder PHI."""
        errors: list[str] = []

        if not tenant.config.allow_phi:
            errors.append("PHI access is not enabled for this tenant")

        if not tenant.hipaa_business_associate:
            errors.append("HIPAA BAA required for PHI access")

        if not tenant.data_processing_agreement:
            errors.append("DPA required for PHI access")

        if tenant.status.value == "suspended":
            errors.append("Tenant is suspended")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[],
        )

    def validate_slug(self, slug: str) -> ValidationResult:
        """Valida formato de slug."""
        errors: list[str] = []
        warnings: list[str] = []

        if not slug:
            errors.append("Slug is required")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        if len(slug) < 3:
            errors.append("Slug must be at least 3 characters")

        if len(slug) > 50:
            errors.append("Slug must be at most 50 characters")

        if not slug.replace("-", "").replace("_", "").isalnum():
            errors.append("Slug can only contain letters, numbers, hyphens, and underscores")

        if slug[0] in ("-", "_") or slug[-1] in ("-", "_"):
            errors.append("Slug cannot start or end with hyphen/underscore")

        reserved = {"www", "api", "admin", "app", "mail", "ftp", "localhost", "tenant", "system"}
        if slug.lower() in reserved:
            errors.append(f"Slug '{slug}' is reserved")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _get_tier_limits(self, tier: str) -> dict:
        """Límites por plan."""
        limits = {
            "starter": {"max_users": 50, "max_establishments": 1, "max_api_calls_per_day": 10000},
            "professional": {"max_users": 500, "max_establishments": 5, "max_api_calls_per_day": 100000},
            "enterprise": {"max_users": 10000, "max_establishments": 100, "max_api_calls_per_day": float("inf")},
            "trial": {"max_users": 10, "max_establishments": 1, "max_api_calls_per_day": 1000},
        }
        return limits.get(tier, {})

    def _estimate_usage(self, tenant: Any) -> dict:
        """Estima uso actual del tenant."""
        # In production, this would query actual usage from DB
        return {"users": 0, "establishments": 0, "api_calls_today": 0}

    def _eu_countries(self) -> set:
        """Países de la UE para GDPR."""
        return {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
            "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
            "PL", "PT", "RO", "SK", "SI", "ES", "SE", "GB", "UK",
        }
