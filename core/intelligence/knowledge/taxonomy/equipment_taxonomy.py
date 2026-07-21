"""
Equipment Taxonomy Module

Complete implementation for medical device taxonomy with categories,
failure modes, maintenance logic, and compliance mapping.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Protocol
from collections import defaultdict
from datetime import datetime


class RiskClass(Enum):
    """Device risk class per MDR/EUAMD."""
    CLASS_I = "class_i"           # Low risk
    CLASS_IIA = "class_iia"       # Medium-low risk
    CLASS_IIB = "class_iib"       # Medium-high risk
    CLASS_III = "class_iii"       # High risk


class DeviceCategory(Enum):
    """High-level device categories."""
    LIFE_SUPPORT = "life_support"
    DIAGNOSTIC = "diagnostic"
    THERAPEUTIC = "therapeutic"
    MONITORING = "monitoring"
    IMAGING = "imaging"
    LABORATORY = "laboratory"
    SURGICAL = "surgical"
    REHABILITATION = "rehabilitation"
    SUPPORT = "support"
    STERILIZATION = "sterilization"


class FailureSeverity(Enum):
    """Severity of equipment failure."""
    CRITICAL = "critical"         # Can cause death/serious injury
    MAJOR = "major"              # Significant functional failure
    MINOR = "minor"              # Minor impact
    COSMETIC = "cosmetic"        # Appearance only


class MaintenanceType(Enum):
    """Types of maintenance."""
    PREVENTIVE = "preventive"          # Time-based
    PREDICTIVE = "predictive"          # Condition-based
    CORRECTIVE = "corrective"          # Repair after failure
    CALIBRATION = "calibration"        # Accuracy verification
    SAFETY = "safety"                  # Safety checks
    INSPECTION = "inspection"          # Visual/functional inspection


class FailureFrequency(Enum):
    """Failure frequency estimation."""
    VERY_RARE = "very_rare"    # < 1%
    RARE = "rare"              # 1-5%
    OCCASIONAL = "occasional"  # 5-10%
    FREQUENT = "frequent"      # 10-20%
    COMMON = "common"          # > 20%


@dataclass(frozen=True)
class DeviceCategory:
    """
    Medical device category with hierarchy and metadata.
    """
    category_id: str
    name: str
    description: str
    parent_category: Optional[str] = None
    gmdn_code: Optional[str] = None
    gmdn_term_name: Optional[str] = None
    fda_product_code: Optional[str] = None
    risk_class: RiskClass = RiskClass.CLASS_I
    applicable_standards: list[str] = field(default_factory=list)
    typical_failure_modes: list[str] = field(default_factory=list)
    typical_accessories: list[str] = field(default_factory=list)
    required_certifications: list[str] = field(default_factory=list)
    suggested_frequency_days: Optional[int] = None
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.risk_class, str):
            object.__setattr__(self, 'risk_class', RiskClass(self.risk_class))


@dataclass(frozen=True)
class FailureMode:
    """
    Equipment failure mode with causes, symptoms, and remediation.
    """
    failure_mode_id: str
    name: str
    description: str
    category_id: str
    severity: FailureSeverity
    frequency: FailureFrequency = FailureFrequency.OCCASIONAL
    occurrence_probability: float = 0.5
    detection_difficulty: str = "medium"
    symptoms: list[str] = field(default_factory=list)
    root_causes: list[str] = field(default_factory=list)
    affected_components: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    estimated_repair_time_minutes: int = 60
    required_tools: list[str] = field(default_factory=list)
    required_parts: list[str] = field(default_factory=list)
    safety_precautions: list[str] = field(default_factory=list)
    applicable_standards: list[str] = field(default_factory=list)
    related_failure_modes: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.severity, str):
            object.__setattr__(self, 'severity', FailureSeverity(self.severity))
        if isinstance(self.frequency, str):
            object.__setattr__(self, 'frequency', FailureFrequency(self.frequency))


@dataclass(frozen=True)
class MaintenanceLogic:
    """
    Maintenance logic with procedures and schedules.
    """
    logic_id: str
    device_category_id: str
    maintenance_type: MaintenanceType
    name: str
    description: str
    trigger_conditions: list[str] = field(default_factory=list)
    frequency_days: Optional[int] = None
    frequency_usage_hours: Optional[int] = None
    frequency_cycles: Optional[int] = None
    priority: int = 1
    procedures: list[str] = field(default_factory=list)
    checklist_items: list[str] = field(default_factory=list)
    estimated_duration_minutes: int = 60
    required_tools: list[str] = field(default_factory=list)
    required_parts: list[str] = field(default_factory=list)
    safety_precautions: list[str] = field(default_factory=list)
    documentation_required: list[str] = field(default_factory=list)
    applicable_standards: list[str] = field(default_factory=list)
    cost_estimate: Optional[float] = None
    requires_certification: bool = False
    
    def __post_init__(self):
        if isinstance(self.maintenance_type, str):
            object.__setattr__(self, 'maintenance_type', MaintenanceType(self.maintenance_type))


@dataclass(frozen=True)
class CategoryHierarchy:
    """Hierarchy of device categories."""
    category: DeviceCategory
    ancestors: list[DeviceCategory] = field(default_factory=list)
    descendants: list[DeviceCategory] = field(default_factory=list)
    siblings: list[DeviceCategory] = field(default_factory=list)


@dataclass(frozen=True)
class FailureModeAnalysis:
    """Failure Mode and Effects Analysis (FMEA)."""
    analysis_id: str
    device_category_id: str
    failure_modes: list[FailureMode]
    rpn_threshold: int = 100
    critical_modes: list[FailureMode] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MaintenanceSchedule:
    """Scheduled maintenance task."""
    schedule_id: str
    device_id: str
    maintenance_logic_id: str
    maintenance_type: MaintenanceType
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    status: str = "scheduled"
    technician: Optional[str] = None
    notes: Optional[str] = None
    parts_used: list[str] = field(default_factory=list)
    labor_hours: Optional[float] = None


class ITaxonomyRepository(Protocol):
    """Repository interface for taxonomy persistence."""
    
    async def get_category(self, category_id: str) -> DeviceCategory | None: ...
    async def get_all_categories(self) -> list[DeviceCategory]: ...
    async def get_failure_modes(self, category_id: str) -> list[FailureMode]: ...
    async def get_maintenance_logic(
        self,
        category_id: str,
        maintenance_type: MaintenanceType | None = None,
    ) -> list[MaintenanceLogic]: ...


class EquipmentTaxonomy:
    """
    Medical equipment taxonomy with categories, failure modes,
    maintenance logic, and compliance mapping.
    """
    
    def __init__(
        self,
        repository: Optional[ITaxonomyRepository] = None,
    ):
        self._repository = repository
        self._categories: dict[str, DeviceCategory] = {}
        self._failure_modes: dict[str, list[FailureMode]] = defaultdict(list)
        self._maintenance_logic: dict[str, list[MaintenanceLogic]] = defaultdict(list)
        self._code_to_category: dict[str, str] = {}
    
    async def get_category(
        self,
        category_id: str,
    ) -> DeviceCategory | None:
        """Get category by ID."""
        if self._repository:
            return await self._repository.get_category(category_id)
        return self._categories.get(category_id)
    
    async def add_category(
        self,
        category: DeviceCategory,
    ) -> None:
        """Add a device category."""
        self._categories[category.category_id] = category
        if category.gmdn_code:
            self._code_to_category[category.gmdn_code] = category.category_id
    
    async def get_hierarchy(
        self,
        category_id: str,
    ) -> CategoryHierarchy | None:
        """Get complete hierarchy for a category."""
        category = await self.get_category(category_id)
        if not category:
            return None
        
        ancestors = []
        current_id = category.parent_category
        while current_id:
            parent = await self.get_category(current_id)
            if parent:
                ancestors.append(parent)
                current_id = parent.parent_category
            else:
                break
        
        descendants = []
        for cat in self._categories.values():
            if cat.parent_category == category_id:
                descendants.append(cat)
        
        siblings = []
        if category.parent_category:
            parent = await self.get_category(category.parent_category)
            if parent:
                for child_id in self._get_children_ids(category.parent_category):
                    if child_id != category_id:
                        sibling = await self.get_category(child_id)
                        if sibling:
                            siblings.append(sibling)
        
        return CategoryHierarchy(
            category=category,
            ancestors=ancestors,
            descendants=descendants,
            siblings=siblings,
        )
    
    async def get_all_categories(
        self,
        parent_id: str | None = None,
    ) -> list[DeviceCategory]:
        """Get all categories, optionally filtered by parent."""
        if parent_id is None:
            return list(self._categories.values())
        
        return [
            cat for cat in self._categories.values()
            if cat.parent_category == parent_id
        ]
    
    async def get_category_by_gmdn(
        self,
        gmdn_code: str,
    ) -> DeviceCategory | None:
        """Get category by GMDN code."""
        category_id = self._code_to_category.get(gmdn_code)
        if category_id:
            return await self.get_category(category_id)
        return None
    
    async def get_failure_modes(
        self,
        category_id: str,
        include_inherited: bool = True,
    ) -> list[FailureMode]:
        """Get failure modes for category."""
        modes = list(self._failure_modes.get(category_id, []))
        
        if include_inherited:
            category = await self.get_category(category_id)
            if category and category.parent_category:
                parent_modes = await self.get_failure_modes(
                    category.parent_category, include_inherited=True
                )
                existing_ids = {m.failure_mode_id for m in modes}
                for pm in parent_modes:
                    if pm.failure_mode_id not in existing_ids:
                        modes.append(pm)
        
        return modes
    
    async def add_failure_mode(
        self,
        failure_mode: FailureMode,
    ) -> None:
        """Add a failure mode."""
        self._failure_modes[failure_mode.category_id].append(failure_mode)
    
    async def get_critical_failure_modes(
        self,
        category_id: str,
    ) -> list[FailureMode]:
        """Get critical (severity=CRITICAL) failure modes."""
        all_modes = await self.get_failure_modes(category_id)
        return [m for m in all_modes if m.severity == FailureSeverity.CRITICAL]
    
    async def get_maintenance_logic(
        self,
        device_category_id: str,
        maintenance_type: MaintenanceType | None = None,
    ) -> list[MaintenanceLogic]:
        """Get maintenance logic for device category."""
        logic_list = list(self._maintenance_logic.get(device_category_id, []))
        
        if maintenance_type:
            logic_list = [
                l for l in logic_list
                if l.maintenance_type == maintenance_type
            ]
        
        category = await self.get_category(device_category_id)
        if category and category.parent_category:
            parent_logic = await self.get_maintenance_logic(
                category.parent_category,
                maintenance_type,
            )
            existing_ids = {l.logic_id for l in logic_list}
            for pl in parent_logic:
                if pl.logic_id not in existing_ids:
                    logic_list.append(pl)
        
        return logic_list
    
    async def add_maintenance_logic(
        self,
        logic: MaintenanceLogic,
    ) -> None:
        """Add maintenance logic."""
        self._maintenance_logic[logic.device_category_id].append(logic)
    
    async def get_preventive_maintenance_schedule(
        self,
        category_id: str,
    ) -> list[MaintenanceLogic]:
        """Get preventive maintenance schedule."""
        return await self.get_maintenance_logic(
            category_id,
            MaintenanceType.PREVENTIVE,
        )
    
    async def get_standards_for_device(
        self,
        device_category_id: str,
    ) -> list[str]:
        """Get applicable standards for device category."""
        standards = set()
        
        category = await self.get_category(device_category_id)
        if category:
            standards.update(category.applicable_standards)
            
            if category.parent_category:
                parent = await self.get_category(category.parent_category)
                if parent:
                    standards.update(parent.applicable_standards)
        
        hierarchy = await self.get_hierarchy(device_category_id)
        if hierarchy:
            for ancestor in hierarchy.ancestors:
                standards.update(ancestor.applicable_standards)
        
        return list(standards)
    
    async def search_categories(
        self,
        query: str,
    ) -> list[DeviceCategory]:
        """Search categories by name or description."""
        query_lower = query.lower()
        results = []
        
        for category in self._categories.values():
            if query_lower in category.name.lower():
                results.append(category)
            elif query_lower in category.description.lower():
                results.append(category)
            elif category.gmdn_code and query_lower in category.gmdn_code:
                results.append(category)
        
        return results
    
    async def calculate_rpn(
        self,
        failure_mode: FailureMode,
    ) -> int:
        """
        Calculate Risk Priority Number (RPN) for FMEA.
        RPN = Severity × Occurrence × Detection
        """
        severity_scores = {
            FailureSeverity.CRITICAL: 10,
            FailureSeverity.MAJOR: 7,
            FailureSeverity.MINOR: 4,
            FailureSeverity.COSMETIC: 1,
        }
        
        frequency_scores = {
            FailureFrequency.VERY_RARE: 1,
            FailureFrequency.RARE: 2,
            FailureFrequency.OCCASIONAL: 5,
            FailureFrequency.FREQUENT: 7,
            FailureFrequency.COMMON: 10,
        }
        
        detection_scores = {
            "very_easy": 1,
            "easy": 3,
            "medium": 5,
            "difficult": 7,
            "very_difficult": 10,
        }
        
        severity = severity_scores.get(failure_mode.severity, 5)
        frequency = frequency_scores.get(failure_mode.frequency, 5)
        detection = detection_scores.get(failure_mode.detection_difficulty.lower(), 5)
        
        return severity * frequency * detection
    
    async def perform_fmea(
        self,
        category_id: str,
    ) -> FailureModeAnalysis:
        """Perform Failure Mode and Effects Analysis."""
        failure_modes = await self.get_failure_modes(category_id)
        
        critical_modes = []
        all_actions = []
        
        for mode in failure_modes:
            rpn = await self.calculate_rpn(mode)
            if rpn >= 100:
                critical_modes.append(mode)
                all_actions.extend(mode.recommended_actions)
        
        return FailureModeAnalysis(
            analysis_id=f"fmea_{category_id}_{datetime.now().timestamp()}",
            device_category_id=category_id,
            failure_modes=failure_modes,
            critical_modes=critical_modes,
            recommended_actions=list(set(all_actions)),
        )
    
    async def get_accessories_for_category(
        self,
        category_id: str,
    ) -> list[str]:
        """Get typical accessories for a category."""
        accessories = set()
        
        category = await self.get_category(category_id)
        if category:
            accessories.update(category.typical_accessories)
        
        hierarchy = await self.get_hierarchy(category_id)
        if hierarchy:
            for ancestor in hierarchy.ancestors:
                accessories.update(ancestor.typical_accessories)
        
        return list(accessories)
    
    async def get_recommended_inspection_interval(
        self,
        category_id: str,
    ) -> int:
        """Get recommended inspection interval in days."""
        category = await self.get_category(category_id)
        if category and category.suggested_frequency_days:
            return category.suggested_frequency_days
        
        risk_intervals = {
            RiskClass.CLASS_III: 30,
            RiskClass.CLASS_IIB: 90,
            RiskClass.CLASS_IIA: 180,
            RiskClass.CLASS_I: 365,
        }
        
        category_obj = await self.get_category(category_id)
        if category_obj:
            return risk_intervals.get(category_obj.risk_class, 180)
        
        return 180
    
    def _get_children_ids(self, category_id: str) -> list[str]:
        """Get IDs of all child categories."""
        return [
            cat.category_id for cat in self._categories.values()
            if cat.parent_category == category_id
        ]


__all__ = [
    "RiskClass",
    "DeviceCategory",
    "FailureSeverity",
    "FailureFrequency",
    "MaintenanceType",
    "DeviceCategory",
    "FailureMode",
    "MaintenanceLogic",
    "CategoryHierarchy",
    "FailureModeAnalysis",
    "MaintenanceSchedule",
    "ITaxonomyRepository",
    "EquipmentTaxonomy",
]
