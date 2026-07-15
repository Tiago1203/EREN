"""EREN Engineering Incident Context.

This package contains the Engineering Incident bounded context,
which is the heart of the EREN Clinical Engineering Copilot.

Architecture:
- domain/entities: EngineeringIncident aggregate, Investigation sub-aggregate
- domain/value_objects: IncidentStatus, Symptom, Resolution, etc.
- domain/services: IncidentService for domain operations
- domain/repositories: Repository interfaces
- application: Commands, queries, and handlers
- infrastructure: Repository implementations, messaging
"""

from .domain import (
    Action,
    ActionResult,
    ActionType,
    ConversationMessage,
    EngineeringIncident,
    Evidence,
    IncidentRepository,
    IncidentService,
    IncidentStatus,
    Investigation,
    MessageSender,
    Priority,
    Resolution,
    SafetyLevel,
    Symptom,
)

__all__ = [
    # Entities
    "EngineeringIncident",
    "Investigation",
    "Evidence",
    "Action",
    "ConversationMessage",
    # Value Objects
    "IncidentStatus",
    "Symptom",
    "Resolution",
    "Priority",
    "SafetyLevel",
    "ActionType",
    "ActionResult",
    "MessageSender",
    # Services
    "IncidentService",
    # Repositories
    "IncidentRepository",
]
