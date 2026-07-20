"""Hospital Digital Twin Engine for EREN OS.

Provides digital representation of hospital infrastructure.
"""

from __future__ import annotations

import asyncio
import random
import threading
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

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


class HospitalDigitalTwin:
    """Digital twin of a hospital.

    Features:
    - Hospital structure (buildings, floors, rooms)
    - Equipment tracking
    - Patient management
    - Staff tracking
    - Alarm management
    - Maintenance tracking
    - Network monitoring
    - Sensor data
    - Simulation mode
    - Natural language queries
    """

    def __init__(self, hospital: Hospital | None = None):
        """Initialize digital twin.

        Args:
            hospital: Hospital configuration.
        """
        self._hospital = hospital or Hospital(hospital_id="default")
        self._buildings: dict[str, Building] = {}
        self._floors: dict[str, Floor] = {}
        self._rooms: dict[str, Room] = {}
        self._operating_rooms: dict[str, OperatingRoom] = {}
        self._icus: dict[str, ICU] = {}
        self._equipment: dict[str, Equipment] = {}
        self._inventory: dict[str, InventoryItem] = {}
        self._patients: dict[str, Patient] = {}
        self._staff: dict[str, Staff] = {}
        self._alarms: dict[str, Alarm] = {}
        self._maintenance: dict[str, list[MaintenanceRecord]] = defaultdict(list)
        self._network: dict[str, NetworkNode] = {}
        self._sensors: dict[str, Sensor] = {}

        self._simulation_config = SimulationConfig()
        self._simulation_running = False
        self._simulation_task: asyncio.Task | None = None

        self._lock = threading.RLock()
        self._event_callbacks: list[Callable] = []

    # =========================================================================
    # Hospital Structure
    # =========================================================================

    def set_hospital(self, hospital: Hospital) -> None:
        """Set hospital configuration."""
        with self._lock:
            self._hospital = hospital

    def add_building(self, building: Building) -> None:
        """Add building."""
        with self._lock:
            self._buildings[building.building_id] = building

    def add_floor(self, floor: Floor) -> None:
        """Add floor."""
        with self._lock:
            self._floors[floor.floor_id] = floor

    def add_room(self, room: Room) -> None:
        """Add room."""
        with self._lock:
            self._rooms[room.room_id] = room

    def add_operating_room(self, or_room: OperatingRoom) -> None:
        """Add operating room."""
        with self._lock:
            self._operating_rooms[or_room.room_id] = or_room

    def add_icu(self, icu: ICU) -> None:
        """Add ICU."""
        with self._lock:
            self._icus[icu.icu_id] = icu

    def get_structure(self) -> dict:
        """Get hospital structure."""
        with self._lock:
            return {
                "hospital": self._hospital,
                "buildings": list(self._buildings.values()),
                "floors": list(self._floors.values()),
                "rooms": list(self._rooms.values()),
                "operating_rooms": list(self._operating_rooms.values()),
                "icus": list(self._icus.values()),
            }

    # =========================================================================
    # Equipment Management
    # =========================================================================

    def add_equipment(self, equipment: Equipment) -> None:
        """Add equipment."""
        with self._lock:
            self._equipment[equipment.equipment_id] = equipment

    def get_equipment(
        self,
        room_id: str | None = None,
        status: AssetStatus | None = None,
    ) -> list[Equipment]:
        """Get equipment with optional filters."""
        with self._lock:
            results = list(self._equipment.values())

            if room_id:
                results = [e for e in results if e.room_id == room_id]

            if status:
                results = [e for e in results if e.status == status]

            return results

    def update_equipment_status(
        self,
        equipment_id: str,
        status: AssetStatus,
    ) -> bool:
        """Update equipment status."""
        with self._lock:
            if equipment_id not in self._equipment:
                return False

            self._equipment[equipment_id].status = status
            return True

    def find_equipment_needing_maintenance(self) -> list[Equipment]:
        """Find equipment that needs maintenance."""
        with self._lock:
            now = datetime.now(UTC)
            results = []

            for eq in self._equipment.values():
                if eq.next_maintenance and eq.next_maintenance <= now:
                    results.append(eq)

            return results

    def get_equipment_by_status(self, status: AssetStatus) -> list[Equipment]:
        """Get equipment by status."""
        with self._lock:
            return [e for e in self._equipment.values() if e.status == status]

    # =========================================================================
    # Patients
    # =========================================================================

    def admit_patient(self, patient: Patient) -> None:
        """Admit a patient."""
        with self._lock:
            self._patients[patient.patient_id] = patient

    def discharge_patient(self, patient_id: str) -> bool:
        """Discharge a patient."""
        with self._lock:
            if patient_id in self._patients:
                self._patients[patient_id].status = "discharged"
                return True
            return False

    def get_patients(self, room_id: str | None = None) -> list[Patient]:
        """Get patients."""
        with self._lock:
            results = [p for p in self._patients.values() if p.status == "admitted"]

            if room_id:
                results = [p for p in results if p.room_id == room_id]

            return results

    # =========================================================================
    # Alarms
    # =========================================================================

    def create_alarm(self, alarm: Alarm) -> None:
        """Create alarm."""
        with self._lock:
            self._alarms[alarm.alarm_id] = alarm
            self._emit_event("alarm_created", alarm)

    def acknowledge_alarm(self, alarm_id: str, staff_id: str) -> bool:
        """Acknowledge alarm."""
        with self._lock:
            if alarm_id in self._alarms:
                self._alarms[alarm_id].acknowledged = True
                return True
            return False

    def resolve_alarm(self, alarm_id: str) -> bool:
        """Resolve alarm."""
        with self._lock:
            if alarm_id in self._alarms:
                self._alarms[alarm_id].resolved = True
                return True
            return False

    def get_active_alarms(
        self,
        priority: str | None = None,
    ) -> list[Alarm]:
        """Get active alarms."""
        with self._lock:
            results = [a for a in self._alarms.values() if not a.resolved]

            if priority:
                results = [a for a in results if a.priority == priority]

            return results

    def get_critical_alarms(self) -> list[Alarm]:
        """Get critical alarms."""
        return self.get_active_alarms(priority="critical")

    # =========================================================================
    # Network Monitoring
    # =========================================================================

    def add_network_node(self, node: NetworkNode) -> None:
        """Add network node."""
        with self._lock:
            self._network[node.node_id] = node

    def get_network_status(self) -> dict:
        """Get overall network status."""
        with self._lock:
            total = len(self._network)
            online = sum(1 for n in self._network.values() if n.status == "online")

            return {
                "total_nodes": total,
                "online": online,
                "offline": total - online,
                "status": "online" if online == total else "degraded",
            }

    def get_offline_devices(self) -> list[NetworkNode]:
        """Get offline network devices."""
        with self._lock:
            return [n for n in self._network.values() if n.status != "online"]

    # =========================================================================
    # Maintenance
    # =========================================================================

    def add_maintenance_record(self, record: MaintenanceRecord) -> None:
        """Add maintenance record."""
        with self._lock:
            self._maintenance[record.equipment_id].append(record)

            # Update equipment last maintenance
            if record.equipment_id in self._equipment:
                self._equipment[record.equipment_id].last_maintenance = record.date

    def get_maintenance_history(
        self,
        equipment_id: str,
    ) -> list[MaintenanceRecord]:
        """Get maintenance history."""
        with self._lock:
            return self._maintenance.get(equipment_id, [])

    # =========================================================================
    # Sensors
    # =========================================================================

    def add_sensor(self, sensor: Sensor) -> None:
        """Add sensor."""
        with self._lock:
            self._sensors[sensor.sensor_id] = sensor

    def update_sensor_reading(
        self,
        sensor_id: str,
        value: float,
    ) -> bool:
        """Update sensor reading."""
        with self._lock:
            if sensor_id in self._sensors:
                self._sensors[sensor_id].current_value = value
                self._sensors[sensor_id].last_reading = datetime.now(UTC)
                return True
            return False

    def get_sensors_by_room(self, room_id: str) -> list[Sensor]:
        """Get sensors in a room."""
        with self._lock:
            return [s for s in self._sensors.values() if s.location == room_id]

    # =========================================================================
    # State & Statistics
    # =========================================================================

    def get_current_state(self) -> TwinState:
        """Get current digital twin state."""
        with self._lock:
            # Calculate occupancy
            total_beds = sum(r.beds for r in self._rooms.values())
            occupied_beds = len([p for p in self._patients.values() if p.status == "admitted"])
            occupancy = occupied_beds / total_beds if total_beds > 0 else 0

            # Count equipment by status
            equipment_status = {}
            for status in AssetStatus:
                count = sum(1 for e in self._equipment.values() if e.status == status)
                equipment_status[status.value] = count

            # Count alarms
            active = self.get_active_alarms()
            critical = sum(1 for a in active if a.priority == "critical")

            return TwinState(
                timestamp=datetime.now(UTC),
                occupancy_rate=occupancy,
                bed_occupancy=(occupied_beds, total_beds),
                equipment_status=equipment_status,
                active_alarms=len(active),
                critical_alarms=critical,
                network_status=self.get_network_status()["status"],
            )

    def get_statistics(self) -> dict:
        """Get hospital statistics."""
        with self._lock:
            state = self.get_current_state()

            return {
                "hospital": {
                    "name": self._hospital.name,
                    "type": self._hospital.hospital_type.value,
                    "bed_count": self._hospital.bed_count,
                },
                "structure": {
                    "buildings": len(self._buildings),
                    "floors": len(self._floors),
                    "rooms": len(self._rooms),
                    "operating_rooms": len(self._operating_rooms),
                    "icus": len(self._icus),
                },
                "patients": {
                    "current": len([p for p in self._patients.values() if p.status == "admitted"]),
                    "total": len(self._patients),
                },
                "equipment": state.equipment_status,
                "alarms": {
                    "active": state.active_alarms,
                    "critical": state.critical_alarms,
                },
                "network": self.get_network_status(),
                "occupancy": {
                    "rate": f"{state.occupancy_rate * 100:.1f}%",
                    "beds": f"{state.bed_occupancy[0]}/{state.bed_occupancy[1]}",
                },
            }

    # =========================================================================
    # Natural Language Queries
    # =========================================================================

    def query(self, query: TwinQuery) -> TwinQueryResult:
        """Execute natural language-like query.

        Supported queries:
        - "equipment needing maintenance"
        - "critical alarms"
        - "offline devices"
        - "rooms with patients"
        - "equipment in room X"
        """
        start_time = time.time()
        results: list[dict] = []

        with self._lock:
            query_type = query.query_type.lower()

            if query_type == "equipment":
                if "maintenance" in query.filters.get("filters", "").lower():
                    equipment = self.find_equipment_needing_maintenance()
                    results = [e.__dict__ for e in equipment]
                elif "status" in query.filters:
                    equipment = self.get_equipment_by_status(
                        AssetStatus(query.filters["status"])
                    )
                    results = [e.__dict__ for e in equipment]
                else:
                    results = [e.__dict__ for e in self._equipment.values()]

            elif query_type == "alarms":
                priority = query.filters.get("priority")
                alarms = self.get_active_alarms(priority=priority)
                results = [a.__dict__ for a in alarms]

            elif query_type == "critical_alarms":
                alarms = self.get_critical_alarms()
                results = [a.__dict__ for a in alarms]

            elif query_type == "network":
                if "offline" in query.filters.get("filters", "").lower():
                    nodes = self.get_offline_devices()
                    results = [n.__dict__ for n in nodes]
                else:
                    results = [n.__dict__ for n in self._network.values()]

            elif query_type == "rooms":
                results = [r.__dict__ for r in self._rooms.values()]

            elif query_type == "patients":
                room_id = query.filters.get("room_id")
                patients = self.get_patients(room_id=room_id)
                results = [p.__dict__ for p in patients]

        execution_time = (time.time() - start_time) * 1000

        return TwinQueryResult(
            query_id=str(uuid.uuid4()),
            results=results,
            count=len(results),
            execution_time_ms=execution_time,
        )

    # =========================================================================
    # Simulation
    # =========================================================================

    def start_simulation(self, config: SimulationConfig | None = None) -> None:
        """Start hospital simulation."""
        if config:
            self._simulation_config = config

        self._simulation_running = True
        self._simulation_task = asyncio.create_task(self._simulation_loop())

    def stop_simulation(self) -> None:
        """Stop simulation."""
        self._simulation_running = False
        if self._simulation_task:
            self._simulation_task.cancel()

    async def _simulation_loop(self) -> None:
        """Main simulation loop."""
        while self._simulation_running:
            try:
                # Simulate events
                if self._simulation_config.enable_random_events:
                    self._simulate_random_event()

                # Update sensor readings
                self._simulate_sensors()

                # Wait for next tick
                await asyncio.sleep(1.0 / self._simulation_config.simulation_speed)

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def _simulate_random_event(self) -> None:
        """Generate random simulation event."""
        if random.random() > 0.1:  # 10% chance per tick
            return

        event_type = random.choice([
            "equipment_status_change",
            "sensor_reading_change",
            "alarm_triggered",
        ])

        event = SimulationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            data={},
        )

        if event_type == "equipment_status_change" and self._equipment:
            eq = random.choice(list(self._equipment.values()))
            event.data = {"equipment_id": eq.equipment_id}
            eq.status = random.choice(list(AssetStatus))

        elif event_type == "sensor_reading_change" and self._sensors:
            sensor = random.choice(list(self._sensors.values()))
            event.data = {
                "sensor_id": sensor.sensor_id,
                "value": sensor.current_value + random.uniform(-1, 1),
            }
            sensor.current_value = event.data["value"]

        self._emit_event("simulation_event", event)

    def _simulate_sensors(self) -> None:
        """Simulate sensor readings."""
        for sensor in self._sensors.values():
            # Add small random variation
            variation = random.uniform(-0.1, 0.1)
            sensor.current_value += variation
            sensor.last_reading = datetime.now(UTC)

    def on_event(self, callback: Callable) -> None:
        """Register event callback."""
        self._event_callbacks.append(callback)

    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit event to callbacks."""
        for callback in self._event_callbacks:
            try:
                callback(event_type, data)
            except Exception:
                pass

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict:
        """Export twin to dictionary."""
        with self._lock:
            return {
                "hospital": self._hospital.__dict__,
                "buildings": {k: v.__dict__ for k, v in self._buildings.items()},
                "floors": {k: v.__dict__ for k, v in self._floors.items()},
                "rooms": {k: v.__dict__ for k, v in self._rooms.items()},
                "equipment": {k: v.__dict__ for k, v in self._equipment.items()},
                "patients": {k: v.__dict__ for k, v in self._patients.items()},
                "alarms": {k: v.__dict__ for k, v in self._alarms.items()},
                "state": self.get_current_state().__dict__,
            }


# =============================================================================
# Singleton
# =============================================================================

_global_twin: HospitalDigitalTwin | None = None
_twin_lock = threading.Lock()


def get_hospital_twin() -> HospitalDigitalTwin:
    """Get global hospital twin."""
    global _global_twin
    with _twin_lock:
        if _global_twin is None:
            _global_twin = HospitalDigitalTwin()
        return _global_twin


def reset_hospital_twin() -> None:
    """Reset global twin."""
    global _global_twin
    with _twin_lock:
        _global_twin = None
