"""Hospital Digital Twin for EREN OS.

PR-065: Hospital Digital Twin

Provides digital representation of hospital infrastructure,
equipment, patients, and real-time monitoring.
"""

from __future__ import annotations

from core.biomedical.hospital_twin.engine import (
    HospitalDigitalTwin,
    get_hospital_twin,
    reset_hospital_twin,
)
from core.biomedical.hospital_twin.types import (
    Alarm,
    AssetStatus,
    Building,
    Equipment,
    Floor,
    Hospital,
    HospitalType,
    ICU,
    InventoryItem,
    MaintenanceRecord,
    NetworkNode,
    OperatingRoom,
    Patient,
    Room,
    Sensor,
    SimulationConfig,
    SimulationEvent,
    Staff,
    TwinQuery,
    TwinQueryResult,
    TwinState,
)

__all__ = [
    # Engine
    "HospitalDigitalTwin",
    "get_hospital_twin",
    "reset_hospital_twin",
    # Types
    "HospitalType",
    "Hospital",
    "Building",
    "Floor",
    "Room",
    "OperatingRoom",
    "ICU",
    "Equipment",
    "AssetStatus",
    "InventoryItem",
    "Patient",
    "Staff",
    "Alarm",
    "MaintenanceRecord",
    "NetworkNode",
    "Sensor",
    "TwinState",
    "TwinQuery",
    "TwinQueryResult",
    "SimulationConfig",
    "SimulationEvent",
]
