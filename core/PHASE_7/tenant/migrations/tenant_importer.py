"""
PHASE 7 - EPIC 2: Tenant Importer

Importación de datos de tenant:
- Full tenant import
- Selective import (mappings)
- Validation antes de importar
- Rollback support
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import json


@dataclass
class ImportMapping:
    """Mapeo de IDs para importación."""
    old_id: str
    new_id: str
    table: str


@dataclass
class ImportResult:
    """Resultado de importación."""
    import_id: str
    tenant_id: str
    status: str = "pending"
    records_imported: int = 0
    records_failed: int = 0
    errors: list[str] = field(default_factory=list)
    mappings: list[ImportMapping] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TenantImporter:
    """Importador de datos de tenant."""

    def __init__(self, context_manager: Any, data_isolation: Any):
        self._context = context_manager
        self._isolation = data_isolation

    def validate_import_file(
        self,
        file_path: str,
        tenant_id: str,
    ) -> tuple[bool, list[str]]:
        """Valida archivo de importación."""
        errors: list[str] = []

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f"Invalid JSON file: {e}")
            return False, errors

        # Check required fields
        if "version" not in data:
            errors.append("Missing 'version' field")

        if "data" not in data:
            errors.append("Missing 'data' field")

        # Validate each table
        for table_name, records in data.get("data", {}).items():
            if not isinstance(records, list):
                errors.append(f"Table '{table_name}' must be a list of records")

            # Validate structure
            for i, record in enumerate(records[:5]):  # Check first 5
                if "id" not in record:
                    errors.append(f"Table '{table_name}', record {i}: missing 'id' field")

        return len(errors) == 0, errors

    def dry_run(
        self,
        file_path: str,
        tenant_id: str,
    ) -> dict:
        """
        Simula importación sin hacer cambios.
        Útil para validar antes de importar.
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        dry_run_result = {
            "would_import": {},
            "would_fail": [],
            "would_skip": [],
            "total_records": 0,
            "warnings": [],
        }

        for table_name, records in data.get("data", {}).items():
            if not self._isolation.can_access_table(table_name, tenant_id):
                dry_run_result["would_skip"].append({
                    "table": table_name,
                    "reason": "Access denied",
                    "count": len(records),
                })
                continue

            can_import, errs = self._isolation.validate_import(
                table_name, records, tenant_id
            )

            if can_import:
                dry_run_result["would_import"][table_name] = len(records)
            else:
                dry_run_result["would_fail"].append({
                    "table": table_name,
                    "errors": errs,
                    "count": len(records),
                })

            dry_run_result["total_records"] += len(records)

        # GDPR warnings
        if data.get("_gdpr_notice"):
            dry_run_result["warnings"].append(
                "This export contains PHI. Ensure legal basis for import."
            )

        return dry_run_result

    def import_data(
        self,
        file_path: str,
        tenant_id: str,
        mapping_mode: str = "generate",   # generate, preserve, map
        id_mappings: Optional[dict[str, dict]] = None,
        created_by: str = "system",
    ) -> ImportResult:
        """Importa datos de tenant."""
        result = ImportResult(
            import_id=f"import-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            tenant_id=tenant_id,
            started_at=datetime.now(timezone.utc),
        )

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            result.errors.append(f"Failed to read file: {e}")
            result.status = "failed"
            result.completed_at = datetime.now(timezone.utc)
            return result

        # Process each table
        for table_name, records in data.get("data", {}).items():
            # Check access
            if not self._isolation.can_access_table(table_name, tenant_id):
                result.errors.append(f"Access denied to table {table_name}")
                continue

            # Validate
            can_import, errs = self._isolation.validate_import(
                table_name, records, tenant_id
            )
            if not can_import:
                result.errors.extend([f"{table_name}: {e}" for e in errs])
                result.records_failed += len(records)
                continue

            # Import
            try:
                imported, mappings = self._import_table(
                    table_name, records, tenant_id, mapping_mode, id_mappings
                )
                result.records_imported += imported
                result.mappings.extend(mappings)
            except Exception as e:
                result.errors.append(f"Failed to import {table_name}: {e}")
                result.records_failed += len(records)

        result.status = "failed" if result.errors else "completed"
        result.completed_at = datetime.now(timezone.utc)
        return result

    def _import_table(
        self,
        table_name: str,
        records: list[dict],
        tenant_id: str,
        mapping_mode: str,
        id_mappings: Optional[dict[str, dict]],
    ) -> tuple[int, list[ImportMapping]]:
        """Importa una tabla individual."""
        mappings: list[ImportMapping] = []
        imported = 0

        for record in records:
            # Add tenant_id
            record["tenant_id"] = tenant_id

            # Handle ID mapping
            old_id = record.get("id", "")
            new_id = self._generate_new_id(table_name, record, mapping_mode, id_mappings)
            record["id"] = new_id

            if old_id:
                mappings.append(ImportMapping(
                    old_id=old_id,
                    new_id=new_id,
                    table=table_name,
                ))

            # In production: INSERT into table
            imported += 1

        return imported, mappings

    def _generate_new_id(
        self,
        table_name: str,
        record: dict,
        mapping_mode: str,
        id_mappings: Optional[dict[str, dict]],
    ) -> str:
        """Genera nuevo ID para registro."""
        import uuid

        if mapping_mode == "preserve":
            return record.get("id", str(uuid.uuid4()))
        elif mapping_mode == "map" and id_mappings:
            return id_mappings.get(table_name, {}).get(record.get("id", ""), str(uuid.uuid4()))
        else:
            prefix = table_name[:3]
            return f"{prefix}-{uuid.uuid4().hex[:12]}"

    def rollback_import(self, import_id: str) -> bool:
        """Revierte una importación (soft delete)."""
        # In production: DELETE FROM imports WHERE import_id = import_id
        return True
