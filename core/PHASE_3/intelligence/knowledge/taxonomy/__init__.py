"""
Equipment Taxonomy Module

Provides taxonomy for medical devices with categories,
failure modes, and maintenance logic.
"""

from core.PHASE_3.intelligence.knowledge.taxonomy.equipment_taxonomy import (
    RiskClass,
    DeviceCategory,
    FailureSeverity,
    FailureFrequency,
    MaintenanceType,
    DeviceCategory as DeviceCategoryModel,
    FailureMode,
    MaintenanceLogic,
    CategoryHierarchy,
    FailureModeAnalysis,
    MaintenanceSchedule,
    ITaxonomyRepository,
    EquipmentTaxonomy,
)

__all__ = [
    "RiskClass",
    "DeviceCategory",
    "FailureSeverity",
    "FailureFrequency",
    "MaintenanceType",
    "DeviceCategoryModel",
    "FailureMode",
    "MaintenanceLogic",
    "CategoryHierarchy",
    "FailureModeAnalysis",
    "MaintenanceSchedule",
    "ITaxonomyRepository",
    "EquipmentTaxonomy",
]
