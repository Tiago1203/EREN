"""Unit tests for Organization bounded context (EPIC 3)."""

from __future__ import annotations

from datetime import date

import pytest

from core.PHASE_1.domain.organization.domain.entities import Hospital, Organization
from core.PHASE_1.domain.organization.domain.entities import (
    HospitalType,
    OwnershipType,
    OrganizationStatus,
)
from core.PHASE_1.infrastructure.shared import OrganizationId, HospitalId, TenantId


class TestOrganization:
    def test_create_organization(self):
        org = Organization.create(
            tenant_id=TenantId.generate(),
            legal_name="General Hospital Corp",
            ownership_type=OwnershipType.NON_PROFIT,
        )
        assert org.legal_name == "General Hospital Corp"
        assert org.ownership_type == OwnershipType.NON_PROFIT
        assert org.status == OrganizationStatus.ACTIVE

    def test_organization_domain_events(self):
        """Organization creation is tracked via version."""
        org = Organization.create(
            tenant_id=TenantId.generate(),
            legal_name="Test Org",
            ownership_type=OwnershipType.PRIVATE,
        )
        # Version should be initialized after creation
        assert org.version >= 1


class TestHospital:
    def test_create_hospital(self):
        org = Organization.create(
            tenant_id=TenantId.generate(),
            legal_name="Test Org",
            ownership_type=OwnershipType.PRIVATE,
        )
        hospital = Hospital.create(
            tenant_id=org.tenant_id,
            organization_id=org.id,
            hospital_code="HOSP001",
            hospital_name="Main Hospital",
            hospital_type=HospitalType.ACADEMIC,
        )
        assert hospital.hospital_code == "HOSP001"
        assert hospital.hospital_name == "Main Hospital"
        assert hospital.hospital_type == HospitalType.ACADEMIC

    def test_hospital_creation_records_type(self):
        """Hospital type is recorded correctly."""
        org = Organization.create(
            tenant_id=TenantId.generate(),
            legal_name="Test Org",
            ownership_type=OwnershipType.PRIVATE,
        )
        hospital = Hospital.create(
            tenant_id=org.tenant_id,
            organization_id=org.id,
            hospital_code="HOSP002",
            hospital_name="Community Hospital",
            hospital_type=HospitalType.COMMUNITY,
        )
        assert hospital.hospital_type == HospitalType.COMMUNITY
