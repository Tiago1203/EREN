"""Biomedical Knowledge Graph Types for EREN OS.

Type definitions for the biomedical knowledge graph representing
medical equipment, hospitals, manufacturers, and relationships.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Entity Types
# =============================================================================


class EntityType(str, Enum):
    """Types of entities in the biomedical knowledge graph."""

    # Equipment
    DEVICE = "device"
    SENSOR = "sensor"
    MONITOR = "monitor"
    PUMP = "pump"
    VENTILATOR = "ventilator"
    IMAGING_DEVICE = "imaging_device"

    # Organizations
    MANUFACTURER = "manufacturer"
    HOSPITAL = "hospital"
    CLINIC = "clinic"
    DEPARTMENT = "department"

    # People
    PATIENT = "patient"
    PROFESSIONAL = "professional"
    TECHNICIAN = "technician"

    # Medical
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    ALARM = "alarm"
    NORM = "norm"
    STANDARD = "standard"

    # Maintenance
    MAINTENANCE = "maintenance"
    REPLACEMENT = "replacement"
    CALIBRATION = "calibration"

    # Location
    ROOM = "room"
    OPERATING_ROOM = "operating_room"
    ICU = "icu"
    WARD = "ward"
    LOCATION = "location"

    # Documentation
    MANUAL = "manual"
    DOCUMENT = "document"
    SOFTWARE = "software"
    FIRMWARE = "firmware"

    # Components
    COMPONENT = "component"


# =============================================================================
# Relationship Types
# =============================================================================


class RelationshipType(str, Enum):
    """Types of relationships in the biomedical knowledge graph."""

    # Equipment relationships
    USES = "uses"
    REQUIRES = "requires"
    MAINTAINS = "maintains"
    INSTALLED_IN = "installed_in"
    CONNECTED_TO = "connected_to"
    CALIBRATED_BY = "calibrated_by"
    CERTIFIED_BY = "certified_by"
    DERIVED_FROM = "derived_from"
    COMPATIBLE_WITH = "compatible_with"
    DEPENDS_ON = "depends_on"

    # Organizational relationships
    BELONGS_TO = "belongs_to"
    LOCATED_IN = "located_in"
    OPERATED_BY = "operated_by"
    SERVICED_BY = "serviced_by"
    MANUFACTURED_BY = "manufactured_by"

    # Medical relationships
    TREATS = "treats"
    DIAGNOSES = "diagnoses"
    MONITORS = "monitors"
    ALERTS = "alerts"
    ADMINISTERS = "administers"
    PRESCRIBES = "prescribes"

    # Maintenance relationships
    REPLACED_BY = "replaced_by"
    UPGRADED_TO = "upgraded_to"
    PART_OF = "part_of"
    HAS_COMPONENT = "has_component"

    # Documentation relationships
    DOCUMENTS = "documents"
    REFERENCE_BY = "referenced_by"
    REQUIRES_SOFTWARE = "requires_software"
    RUNS_ON = "runs_on"

    # Compliance relationships
    COMPLIES_WITH = "complies_with"
    MEETS_STANDARD = "meets_standard"


# =============================================================================
# Entity Base
# =============================================================================


@dataclass
class BiomedicalEntity:
    """Base class for biomedical entities."""

    entity_id: str = ""
    entity_type: EntityType = EntityType.DEVICE
    name: str = ""
    description: str = ""
    properties: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "metadata": self.metadata,
            "tags": self.tags,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# =============================================================================
# Device Entity
# =============================================================================


@dataclass
class DeviceEntity(BiomedicalEntity):
    """A medical device entity."""

    entity_type: EntityType = EntityType.DEVICE
    manufacturer_id: str = ""
    model_number: str = ""
    serial_number: str = ""
    firmware_version: str = ""
    software_version: str = ""
    status: str = "active"  # active, inactive, maintenance, decommissioned
    location_id: str = ""
    installation_date: datetime | None = None
    warranty_expiration: datetime | None = None
    specifications: dict = field(default_factory=dict)
    certifications: list[str] = field(default_factory=list)


@dataclass
class SensorEntity(BiomedicalEntity):
    """A sensor entity."""

    entity_type: EntityType = EntityType.SENSOR
    device_id: str = ""
    sensor_type: str = ""  # temperature, pressure, ECG, etc.
    unit: str = ""  # °C, mmHg, bpm, etc.
    range_min: float = 0.0
    range_max: float = 0.0
    accuracy: float = 0.0
    calibration_interval_days: int = 0


# =============================================================================
# Organization Entities
# =============================================================================


@dataclass
class ManufacturerEntity(BiomedicalEntity):
    """A device manufacturer."""

    entity_type: EntityType = EntityType.MANUFACTURER
    country: str = ""
    website: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    certifications: list[str] = field(default_factory=list)
    models_produced: list[str] = field(default_factory=list)


@dataclass
class HospitalEntity(BiomedicalEntity):
    """A hospital."""

    entity_type: EntityType = EntityType.HOSPITAL
    address: str = ""
    city: str = ""
    country: str = ""
    phone: str = ""
    email: str = ""
    bed_count: int = 0
    departments: list[str] = field(default_factory=list)
    facilities: list[str] = field(default_factory=list)


# =============================================================================
# Relationship
# =============================================================================


@dataclass
class Relationship:
    """A relationship between entities."""

    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: dict = field(default_factory=dict)
    weight: float = 1.0  # Relationship strength
    bidirectional: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "relationship_id": self.relationship_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "properties": self.properties,
            "weight": self.weight,
            "bidirectional": self.bidirectional,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# Graph Query
# =============================================================================


@dataclass
class GraphQuery:
    """Query for the knowledge graph."""

    query_id: str
    entity_ids: list[str] = field(default_factory=list)
    entity_types: list[EntityType] = field(default_factory=list)
    relationship_types: list[RelationshipType] = field(default_factory=list)
    traversal_depth: int = 1
    include_properties: bool = True
    filters: dict = field(default_factory=dict)


@dataclass
class GraphQueryResult:
    """Result of a graph query."""

    query_id: str
    entities: list[BiomedicalEntity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    execution_time_ms: float = 0.0
    total_hops: int = 0


# =============================================================================
# Ontology
# =============================================================================


@dataclass
class OntologyClass:
    """An ontology class definition."""

    class_id: str = ""
    name: str = ""
    parent: str | None = None
    description: str = ""
    properties: list[str] = field(default_factory=list)
    equivalent_classes: list[str] = field(default_factory=list)
    disjoint_classes: list[str] = field(default_factory=list)


@dataclass
class OntologyProperty:
    """An ontology property definition."""

    property_id: str = ""
    name: str = ""
    domain: list[str] = field(default_factory=list)  # Classes
    range: list[str] = field(default_factory=list)  # Classes
    description: str = ""
    transitive: bool = False
    symmetric: bool = False
    functional: bool = False


# =============================================================================
# Inference
# =============================================================================


@dataclass
class InferenceRule:
    """A rule for inferring new relationships."""

    rule_id: str
    name: str
    description: str = ""
    conditions: list[dict] = field(default_factory=list)
    conclusion: dict = field(default_factory=dict)
    confidence: float = 1.0
    enabled: bool = True


@dataclass
class InferenceResult:
    """Result of inference."""

    rule_id: str
    inferred_relationships: list[Relationship] = field(default_factory=list)
    confidence: float = 1.0
    explanation: str = ""


# =============================================================================
# Versioning
# =============================================================================


@dataclass
class GraphVersion:
    """Version of the knowledge graph."""

    version_id: str
    version_number: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    entities_added: int = 0
    entities_removed: int = 0
    relationships_added: int = 0
    relationships_removed: int = 0
    description: str = ""


# =============================================================================
# Statistics
# =============================================================================


@dataclass
class GraphStatistics:
    """Statistics about the knowledge graph."""

    total_entities: int = 0
    total_relationships: int = 0
    entities_by_type: dict[str, int] = field(default_factory=dict)
    relationships_by_type: dict[str, int] = field(default_factory=dict)
    avg_degree: float = 0.0
    max_degree: int = 0
    diameter: int = 0
    density: float = 0.0
