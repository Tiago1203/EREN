"""
Equipment Taxonomy Module

Provides taxonomy for medical devices with categories,
failure modes, and maintenance logic.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class RiskClass(Enum):
    """Device risk class."""
    CLASS_I = "class_i"
    CLASS_IIA = "class_iia"
    CLASS_IIB = "class_iib"
    CLASS_III = "class_iii"


class FailureSeverity(Enum):
    """Failure severity level."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    COSMETIC = "cosmetic"


class MaintenanceType(Enum):
    """Types of maintenance."""
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    CALIBRATION = "calibration"
    SAFETY = "safety"


@dataclass(frozen=True)
class DeviceCategory:
    """Medical device category."""
    category_id: str
    name: str
    description: str
    parent_category: str | None = None
    gmdn_code: str | None = None
    fda_product_code: str | None = None
    risk_class: RiskClass = RiskClass.CLASS_I
    applicable_standards: list[str] = field(default_factory=list)
    typical_failure_modes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FailureMode:
    """Equipment failure mode."""
    failure_mode_id: str
    name: str
    description: str
    category_id: str
    severity: FailureSeverity
    occurrence_probability: float = 0.5
    detection_difficulty: str = "medium"
    symptoms: list[str] = field(default_factory=list)
    root_causes: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    applicable_standards: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MaintenanceLogic:
    """Maintenance logic for equipment."""
    logic_id: str
    device_category_id: str
    maintenance_type: MaintenanceType
    trigger_conditions: list[str] = field(default_factory=list)
    frequency_days: int | None = None
    frequency_usage_hours: int | None = None
    procedures: list[str] = field(default_factory=list)
    estimated_duration_minutes: int = 60
    required_tools: list[str] = field(default_factory=list)
    required_parts: list[str] = field(default_factory=list)
    safety_precautions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CategoryHierarchy:
    """Hierarchy of device categories."""
    category: DeviceCategory
    ancestors: list[DeviceCategory] = field(default_factory=list)
    descendants: list[DeviceCategory] = field(default_factory=list)


class EquipmentTaxonomy:
    """
    Medical equipment taxonomy with failure modes
    and maintenance logic.
    """
    
    def __init__(self):
        self._categories: dict[str, DeviceCategory] = {}
        self._failure_modes: dict[str, list[FailureMode]] = {}
        self._maintenance_logic: dict[str, list[MaintenanceLogic]] = {}
    
    async def get_category(
        self,
        category_id: str,
    ) -> DeviceCategory | None:
        """Get category by ID."""
        return self._categories.get(category_id)
    
    async def get_hierarchy(
        self,
        category_id: str,
    ) -> CategoryHierarchy | None:
        """Get hierarchy for a category."""
        category = self._categories.get(category_id)
        if not category:
            return None
        
        ancestors = []
        current_id = category.parent_category
        while current_id:
            parent = self._categories.get(current_id)
            if parent:
                ancestors.append(parent)
                current_id = parent.parent_category
            else:
                break
        
        descendants = []
        for cat in self._categories.values():
            if cat.parent_category == category_id:
                descendants.append(cat)
        
        return CategoryHierarchy(
            category=category,
            ancestors=ancestors,
            descendants=descendants,
        )
    
    async def get_failure_modes(
        self,
        category_id: str,
    ) -> list[FailureMode]:
        """Get failure modes for category."""
        modes = self._failure_modes.get(category_id, [])
        
        category = self._categories.get(category_id)
        if category and category.parent_category:
            parent_modes = self._failure_modes.get(category.parent_category, [])
            modes = modes + [m for m in parent_modes if m not in modes]
        
        return modes
    
    async def get_maintenance_logic(
        self,
        device_category_id: str,
        maintenance_type: MaintenanceType | None = None,
    ) -> list[MaintenanceLogic]:
        """Get maintenance logic for device."""
        logic_list = self._maintenance_logic.get(device_category_id, [])
        
        if maintenance_type:
            logic_list = [l for l in logic_list if l.maintenance_type == maintenance_type]
        
        return logic_list
    
    async def get_standards_for_device(
        self,
        device_category_id: str,
    ) -> list[str]:
        """Get applicable standards for device category."""
        standards = set()
        
        category = self._categories.get(device_category_id)
        if category:
            standards.update(category.applicable_standards)
            
            if category.parent_category:
                parent = self._categories.get(category.parent_category)
                if parent:
                    standards.update(parent.applicable_standards)
        
        return list(standards)
    
    async def search_categories(
        self,
        query: str,
    ) -> list[DeviceCategory]:
        """Search categories by name."""
        query_lower = query.lower()
        results = []
        
        for category in self._categories.values():
            if query_lower in category.name.lower():
                results.append(category)
        
        return results


__all__ = [
    "RiskClass",
    "FailureSeverity",
    "MaintenanceType",
    "DeviceCategory",
    "FailureMode",
    "MaintenanceLogic",
    "CategoryHierarchy",
    "EquipmentTaxonomy",
]
