"""Hospital Digital Twin Types for EREN OS.

Type definitions for the hospital digital twin representation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Hospital Structure
# =============================================================================


class HospitalType(str, Enum):
    """Types of hospitals."""

    GENERAL = "general"
    SPECIALTY = "specialty"
    UNIVERSITY = "university"
    CLINIC = "clinic"
    URGENT_CARE = "urgent_care"


@dataclass
class Hospital:
    """Hospital representation."""

    hospital_id: str
    name: str = ""
    hospital_type: HospitalType = HospitalType.GENERAL
    address: str = ""
    city: str = ""
    country: str = ""
    phone: str = ""
    email: str = ""
    bed_count: int = 0
    floors: int = 0
    departments: list[str] = field(default_factory=list)
    coordinates: tuple[float, float] = (0.0, 0.0)  # lat, lon


@dataclass
class Building:
    """Building within a hospital."""

    building_id: str
    hospital_id: str
    name: str = ""
    floors: int = 0
    year_built: int = 0
    total_area_sqm: float = 0.0


@dataclass
class Floor:
    """Floor within a building."""

    floor_id: str
    building_id: str
    floor_number: int = 0  # 0 = ground, negative = basement
    name: str = ""  # e.g., "ICU Level", "Emergency"
    total_area_sqm: float = 0.0
    zones: list[str] = field(default_factory=list)


@dataclass
class Room:
    """Room within a floor."""

    room_id: str
    floor_id: str
    name: str = ""
    room_type: str = ""  # patient_room, operating_room, icu, etc.
    area_sqm: float = 0.0
    capacity: int = 0
    beds: int = 0
    equipment: list[str] = field(default_factory=list)


# =============================================================================
# Operating Room & ICU
# =============================================================================


@dataclass
class OperatingRoom:
    """Operating room."""

    room_id: str
    name: str = ""
    or_number: str = ""
    specialty: str = ""  # cardiology, orthopedics, etc.
    room_class: str = "A"  # A, B, C
    equipment: list[str] = field(default_factory=list)
    status: str = "available"  # available, in_use, maintenance, cleaning


@dataclass
class ICU:
    """Intensive Care Unit."""

    icu_id: str
    name: str = ""
    icu_type: str = ""  # medical, surgical, cardiac, neonatal
    beds: int = 0
    occupied_beds: int = 0
    staff_ratio: float = 1.0  # nurses per patient


# =============================================================================
# Equipment & Assets
# =============================================================================


class AssetStatus(str, Enum):
    """Status of hospital assets."""

    OPERATIONAL = "operational"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RESERVED = "reserved"


@dataclass
class Equipment:
    """Medical equipment."""

    equipment_id: str
    name: str = ""
    serial_number: str = ""
    manufacturer: str = ""
    model: str = ""
    room_id: str = ""
    status: AssetStatus = AssetStatus.OPERATIONAL
    purchase_date: datetime | None = None
    last_maintenance: datetime | None = None
    next_maintenance: datetime | None = None
    warranty_expiration: datetime | None = None


@dataclass
class InventoryItem:
    """Inventory item."""

    item_id: str
    name: str = ""
    category: str = ""  # supplies, medication, equipment
    quantity: int = 0
    unit: str = ""  # pcs, boxes, liters
    min_stock: int = 0
    location: str = ""  # storage room
    expiry_date: datetime | None = None


# =============================================================================
# Staff & Patients
# =============================================================================


@dataclass
class Staff:
    """Hospital staff member."""

    staff_id: str
    first_name: str = ""
    last_name: str = ""
    role: str = ""  # physician, nurse, technician
    specialty: str = ""
    department: str = ""
    room_id: str = ""


@dataclass
class Patient:
    """Patient in hospital."""

    patient_id: str
    mrn: str = ""  # Medical Record Number
    first_name: str = ""
    last_name: str = ""
    room_id: str = ""
    bed_id: str = ""
    admission_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "admitted"  # admitted, discharged, transferred


# =============================================================================
# Alarms & Monitoring
# =============================================================================


@dataclass
class Alarm:
    """Hospital alarm."""

    alarm_id: str
    source_type: str = ""  # equipment, patient, environmental
    source_id: str = ""
    priority: str = "medium"  # low, medium, high, critical
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MaintenanceRecord:
    """Maintenance record."""

    record_id: str
    equipment_id: str = ""
    maintenance_type: str = ""  # preventive, corrective
    description: str = ""
    technician: str = ""
    date: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_minutes: int = 0
    cost: float = 0.0


# =============================================================================
# Network & Sensors
# =============================================================================


@dataclass
class NetworkNode:
    """Network node."""

    node_id: str
    name: str = ""
    node_type: str = ""  # switch, router, access_point
    ip_address: str = ""
    location: str = ""  # room_id or floor_id
    status: str = "online"


@dataclass
class Sensor:
    """Environmental sensor."""

    sensor_id: str
    name: str = ""
    sensor_type: str = ""  # temperature, humidity, pressure
    location: str = ""  # room_id
    unit: str = ""
    current_value: float = 0.0
    last_reading: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Digital Twin State
# =============================================================================


@dataclass
class TwinState:
    """Current state of the digital twin."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    occupancy_rate: float = 0.0  # 0-1
    bed_occupancy: tuple[int, int] = (0, 0)  # occupied, total
    equipment_status: dict[str, int] = field(default_factory=dict)
    active_alarms: int = 0
    critical_alarms: int = 0
    network_status: str = "online"
    power_status: str = "normal"


# =============================================================================
# Queries
# =============================================================================


@dataclass
class TwinQuery:
    """Query for digital twin."""

    query_type: str = ""  # equipment, rooms, patients, alarms
    filters: dict = field(default_factory=dict)
    include_history: bool = False
    time_range: tuple[datetime, datetime] | None = None


@dataclass
class TwinQueryResult:
    """Result of digital twin query."""

    query_id: str
    results: list[dict] = field(default_factory=list)
    count: int = 0
    execution_time_ms: float = 0.0


# =============================================================================
# Simulation
# =============================================================================


@dataclass
class SimulationConfig:
    """Configuration for hospital simulation."""

    simulation_speed: float = 1.0  # 1x = real time
    patient_arrival_rate: float = 1.0  # patients per hour
    equipment_failure_rate: float = 0.01  # per day
    enable_random_events: bool = True


@dataclass
class SimulationEvent:
    """Event during simulation."""

    event_id: str
    event_type: str = ""  # patient_arrival, equipment_failure, alarm
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict = field(default_factory=dict)
