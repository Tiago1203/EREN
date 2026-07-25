"""
PHASE 7 - EPIC 2: Tenant Exporter

Exportación de datos de tenant:
- Full tenant export
- Selective export (establishments, users)
- GDPR-compliant data export
- Streaming export para grandes volúmenes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import json
import uuid


@dataclass
class ExportConfig:
    """Configuración de exportación."""
    include_users: bool = True
    include_equipment: bool = True
    include_maintenances: bool = True
    include_establishments: bool = True
    include_kpis: bool = True
    include_audit_logs: bool = False   # GDPR sensitive
    include_patients: bool = False      # PHI - GDPR sensitive
    include_medical_records: bool = False  # PHI
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    establishment_ids: list[str] = field(default_factory=list)
    anonymize_phi: bool = False


@dataclass
class ExportJob:
    """Job de exportación."""
    job_id: str
    tenant_id: str
    status: str = "pending"    # pending, running, completed, failed
    config: dict = field(default_factory=dict)
    total_records: int = 0
    exported_records: int = 0
    file_path: str = ""
    file_size_bytes: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: str = ""


class TenantExporter:
    """Exportador de datos de tenant."""

    def __init__(self, context_manager: Any, data_isolation: Any):
        self._context = context_manager
        self._isolation = data_isolation

    def create_export_job(
        self,
        tenant_id: str,
        config: ExportConfig,
        created_by: str = "system",
    ) -> ExportJob:
        """Crea un job de exportación."""
        job = ExportJob(
            job_id=f"export-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            config={
                "include_users": config.include_users,
                "include_equipment": config.include_equipment,
                "include_maintenances": config.include_maintenances,
                "include_establishments": config.include_establishments,
                "include_kpis": config.include_kpis,
                "include_audit_logs": config.include_audit_logs,
                "include_patients": config.include_patients,
                "include_medical_records": config.include_medical_records,
                "anonymize_phi": config.anonymize_phi,
            },
        )

        # Validate GDPR compliance
        if config.include_patients or config.include_medical_records:
            boundary = self._isolation.get_boundary(tenant_id)
            if not boundary.allow_gdpr_export:
                job.error = "GDPR: Tenant has not authorized PHI export"
                job.status = "failed"

        return job

    def estimate_export_size(
        self,
        tenant_id: str,
        config: ExportConfig,
    ) -> dict:
        """Estima tamaño de exportación."""
        estimates = {}

        if config.include_users:
            estimates["users"] = self._estimate_table("users", tenant_id)
        if config.include_equipment:
            estimates["equipment"] = self._estimate_table("equipment", tenant_id)
        if config.include_maintenances:
            estimates["maintenances"] = self._estimate_table("maintenances", tenant_id)
        if config.include_establishments:
            estimates["establishments"] = self._estimate_table("establishments", tenant_id)
        if config.include_kpis:
            estimates["kpis"] = self._estimate_table("kpis", tenant_id)

        total_estimate = sum(estimates.values())
        can_proceed = total_estimate < 100 * 1024 * 1024  # 100MB soft limit

        return {
            "estimates": estimates,
            "total_bytes": total_estimate,
            "total_mb": round(total_estimate / (1024 * 1024), 2),
            "can_proceed": can_proceed,
            "limit_mb": 100,
        }

    def export_to_json(
        self,
        tenant_id: str,
        config: ExportConfig,
        output_path: str = "",
    ) -> dict:
        """
        Exporta datos del tenant a JSON.
        En producción usaría streaming para grandes volúmenes.
        """
        if not output_path:
            output_path = f"/tmp/export_{tenant_id}_{datetime.now().strftime('%Y%m%d')}.json"

        export_data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
            "version": "1.0",
            "data": {},
        }

        # Export users
        if config.include_users:
            export_data["data"]["users"] = self._export_table(
                "users", tenant_id, config
            )

        # Export equipment
        if config.include_equipment:
            export_data["data"]["equipment"] = self._export_table(
                "equipment", tenant_id, config
            )

        # Export establishments
        if config.include_establishments:
            export_data["data"]["establishments"] = self._export_table(
                "establishments", tenant_id, config
            )

        # GDPR: add privacy notice
        if config.include_patients or config.include_medical_records:
            export_data["_gdpr_notice"] = {
                "phi_included": True,
                "anonymized": config.anonymize_phi,
                "purpose": "Data portability under GDPR Article 20",
            }

        return {
            "output_path": output_path,
            "total_records": sum(
                len(v) for v in export_data["data"].values()
            ),
            "size_bytes": len(json.dumps(export_data)),
        }

    def _estimate_table(self, table_name: str, tenant_id: str) -> int:
        """Estima tamaño de tabla."""
        # In production: SELECT COUNT(*) FROM table WHERE tenant_id = ?
        return 1000  # Placeholder

    def _export_table(
        self,
        table_name: str,
        tenant_id: str,
        config: ExportConfig,
    ) -> list[dict]:
        """Exporta tabla de tenant."""
        # In production: SELECT * FROM table WHERE tenant_id = ?
        # with filters
        return []  # Placeholder

    def generate_export_manifest(self, job: ExportJob) -> dict:
        """Genera manifest de exportación."""
        return {
            "job_id": job.job_id,
            "tenant_id": job.tenant_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "includes": list(job.config.keys()),
            "total_records": job.total_records,
            "file_size_bytes": job.file_size_bytes,
            "checksum": "",
        }
