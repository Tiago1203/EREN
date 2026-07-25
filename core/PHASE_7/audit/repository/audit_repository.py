"""
PHASE 7 - EPIC 1: Audit Repository

Repositorio de auditoría para acceso a datos:
- CRUD de eventos
- Consultas complejas
- Índices optimizados
- Aggregations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Any
import uuid


class AuditIndex(str, Enum):
    """Índices disponibles."""
    BY_ACTOR = "actor_id"
    BY_RESOURCE = "resource_id"
    BY_CATEGORY = "category"
    BY_TIMESTAMP = "timestamp"
    BY_SEVERITY = "severity"
    BY_TENANT = "tenant_id"
    BY_PHI = "is_phi_access"


@dataclass
class AuditQuery:
    """Consulta de auditoría."""
    query_id: str

    # Filters
    actor_ids: list[str] = field(default_factory=list)
    resource_ids: list[str] = field(default_factory=list)
    resource_types: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    severities: list[str] = field(default_factory=list)
    tenant_ids: list[str] = field(default_factory=list)
    establishment_ids: list[str] = field(default_factory=list)

    # Time range
    since: Optional[datetime] = None
    until: Optional[datetime] = None

    # PHI filter
    phi_access_only: bool = False

    # Text search
    search_text: str = ""

    # Pagination
    limit: int = 100
    offset: int = 0

    # Sorting
    sort_by: str = "timestamp"
    sort_order: str = "desc"

    # Options
    include_metadata: bool = True
    group_by: Optional[str] = None  # actor_id, category, resource_type, etc.


class AuditRepository:
    """Repositorio de auditoría con almacenamiento en memoria."""

    def __init__(self):
        self._events: list = []          # All audit events
        self._by_actor: dict[str, list] = {}
        self._by_resource: dict[str, list] = {}
        self._by_category: dict[str, list] = {}
        self._by_tenant: dict[str, list] = {}
        self._by_phi: dict[bool, list] = {True: [], False: []}
        self._indexes_built: bool = False

    def save_event(self, event: dict) -> str:
        """Guarda un evento de auditoría."""
        event_id = event.get("event_id") or f"audit-{uuid.uuid4().hex[:16]}"
        event["event_id"] = event_id
        event["_saved_at"] = datetime.now(timezone.utc)

        self._events.append(event)
        self._index_event(event)
        self._indexes_built = False  # Rebuild needed
        return event_id

    def save_batch(self, events: list[dict]) -> list[str]:
        """Guarda un batch de eventos."""
        ids = []
        for event in events:
            event_id = self.save_event(event)
            ids.append(event_id)
        return ids

    def _index_event(self, event: dict) -> None:
        """Indexa evento en índices secundarios."""
        actor_id = event.get("actor_id")
        resource_id = event.get("resource_id")
        category = event.get("category")
        tenant_id = event.get("tenant_id")
        is_phi = event.get("is_phi_access", False)

        if actor_id:
            if actor_id not in self._by_actor:
                self._by_actor[actor_id] = []
            self._by_actor[actor_id].append(event)

        if resource_id:
            if resource_id not in self._by_resource:
                self._by_resource[resource_id] = []
            self._by_resource[resource_id].append(event)

        if category:
            if category not in self._by_category:
                self._by_category[category] = []
            self._by_category[category].append(event)

        if tenant_id:
            if tenant_id not in self._by_tenant:
                self._by_tenant[tenant_id] = []
            self._by_tenant[tenant_id].append(event)

        self._by_phi[is_phi].append(event)

    def query(self, query: AuditQuery | dict) -> dict:
        """
        Ejecuta consulta de auditoría.
        Retorna dict con results y metadata.
        """
        self._ensure_indexes()

        # Support both dict and AuditQuery
        if isinstance(query, dict):
            q_offset = query.get("offset", 0)
            q_limit = query.get("limit", 100)
            q_sort_by = query.get("sort_by", "timestamp")
            q_sort_order = query.get("sort_order", "desc")
            q_group_by = query.get("group_by")
            q_query_id = query.get("query_id", "")
        else:
            q_offset = query.offset
            q_limit = query.limit
            q_sort_by = query.sort_by
            q_sort_order = query.sort_order
            q_group_by = query.group_by
            q_query_id = query.query_id

        events = self._filter_events(query)

        # Sort
        events = self._sort_events(events, q_sort_by, q_sort_order)

        # Pagination
        total = len(events)
        events = events[q_offset:q_offset + q_limit]

        # Grouping
        groups = {}
        if q_group_by:
            groups = self._group_events(events, q_group_by)

        # Aggregations
        aggregations = self._aggregate_events(events, query)

        return {
            "query_id": q_query_id,
            "events": events,
            "total": total,
            "returned": len(events),
            "offset": q_offset,
            "limit": q_limit,
            "groups": groups,
            "aggregations": aggregations,
        }

    def _ensure_indexes(self) -> None:
        """Construye índices si es necesario."""
        if self._indexes_built:
            return

        # Sort events by timestamp
        self._events.sort(key=lambda e: e.get("timestamp", datetime.min), reverse=True)
        self._indexes_built = True

    def _filter_events(self, query: AuditQuery | dict) -> list[dict]:
        """Aplica filtros a eventos."""
        q = query if isinstance(query, dict) else query
        events = self._events

        if q.get("actor_ids"):
            events = [e for e in events if e.get("actor_id") in q["actor_ids"]]

        if q.get("resource_ids"):
            events = [e for e in events if e.get("resource_id") in q["resource_ids"]]

        if q.get("resource_types"):
            events = [e for e in events if e.get("resource_type") in q["resource_types"]]

        if q.get("categories"):
            events = [e for e in events if e.get("category") in q["categories"]]

        if q.get("actions"):
            events = [e for e in events if e.get("action") in q["actions"]]

        if q.get("severities"):
            events = [e for e in events if e.get("severity") in q["severities"]]

        if q.get("tenant_ids"):
            events = [e for e in events if e.get("tenant_id") in q["tenant_ids"]]

        if q.get("establishment_ids"):
            events = [e for e in events if e.get("establishment_id") in q["establishment_ids"]]

        if q.get("phi_access_only"):
            events = [e for e in events if e.get("is_phi_access", False)]

        if q.get("since"):
            events = [e for e in events if e.get("timestamp", datetime.min) >= q["since"]]

        if q.get("until"):
            events = [e for e in events if e.get("timestamp", datetime.max) <= q["until"]]

        if q.get("search_text"):
            text = q["search_text"].lower()
            events = [
                e for e in events
                if text in str(e.get("actor_name", "")).lower()
                or text in str(e.get("resource_name", "")).lower()
                or text in str(e.get("reason", "")).lower()
            ]

        return events

    def _sort_events(
        self,
        events: list[dict],
        sort_by: str,
        sort_order: str,
    ) -> list[dict]:
        """Ordena eventos."""
        reverse = sort_order.lower() == "desc"

        if sort_by == "timestamp":
            return sorted(events, key=lambda e: e.get("timestamp", datetime.min), reverse=reverse)
        elif sort_by == "severity":
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            return sorted(
                events,
                key=lambda e: severity_order.get(e.get("severity", "info"), 99),
                reverse=reverse,
            )
        elif sort_by == "actor_id":
            return sorted(events, key=lambda e: e.get("actor_id", ""), reverse=reverse)

        return events

    def _group_events(self, events: list[dict], group_by: str) -> dict:
        """Agrupa eventos."""
        groups: dict[str, list] = {}
        for event in events:
            key = str(event.get(group_by, "unknown"))
            if key not in groups:
                groups[key] = []
            groups[key].append(event)

        # Add summary to each group
        for key, group_events in groups.items():
            groups[key] = {
                "count": len(group_events),
                "events": group_events,
                "first": group_events[-1].get("timestamp") if group_events else None,
                "last": group_events[0].get("timestamp") if group_events else None,
            }

        return groups

    def _aggregate_events(self, events: list[dict], query: AuditQuery | dict) -> dict:
        """Calcula agregaciones sobre eventos."""
        if not events:
            return {}

        by_category: dict[str, int] = {}
        by_action: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        by_user: dict[str, int] = {}
        total_phi = 0
        total_failed = 0

        for event in events:
            cat = str(event.get("category", "unknown"))
            by_category[cat] = by_category.get(cat, 0) + 1

            act = str(event.get("action", "unknown"))
            by_action[act] = by_action.get(act, 0) + 1

            sev = str(event.get("severity", "info"))
            by_severity[sev] = by_severity.get(sev, 0) + 1

            user = str(event.get("actor_name", "unknown"))
            by_user[user] = by_user.get(user, 0) + 1

            if event.get("is_phi_access"):
                total_phi += 1
            if not event.get("success", True):
                total_failed += 1

        return {
            "total_events": len(events),
            "by_category": by_category,
            "by_action": by_action,
            "by_severity": by_severity,
            "by_user": by_user,
            "phi_access_count": total_phi,
            "failed_events_count": total_failed,
        }

    def count(self, query: AuditQuery | dict) -> int:
        """Cuenta eventos que matchean la consulta (sin paginación)."""
        self._ensure_indexes()
        events = self._filter_events(query)
        return len(events)

    def get_event(self, event_id: str) -> Optional[dict]:
        """Obtiene un evento por ID."""
        for event in self._events:
            if event.get("event_id") == event_id:
                return event
        return None

    def get_events_by_actor(
        self,
        actor_id: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Obtiene eventos de un actor."""
        events = self._by_actor.get(actor_id, [])
        if since:
            events = [e for e in events if e.get("timestamp", datetime.min) >= since]
        return events[:limit]

    def get_events_by_resource(
        self,
        resource_id: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Obtiene eventos de un recurso."""
        events = self._by_resource.get(resource_id, [])
        if since:
            events = [e for e in events if e.get("timestamp", datetime.min) >= since]
        return events[:limit]

    def delete_before(self, before: datetime) -> int:
        """Elimina eventos anteriores a una fecha (para retención)."""
        before = before or datetime.now(timezone.utc) - timedelta(days=2190)
        original = len(self._events)
        self._events = [e for e in self._events if e.get("timestamp", datetime.max) > before]
        self._indexes_built = False
        return original - len(self._events)

    def get_storage_size(self) -> dict:
        """Obtiene tamaño aproximado del storage."""
        import sys
        total_events = len(self._events)
        approx_bytes = sum(sys.getsizeof(str(e)) for e in self._events)
        return {
            "total_events": total_events,
            "approx_bytes": approx_bytes,
            "approx_mb": round(approx_bytes / 1024 / 1024, 2),
        }
