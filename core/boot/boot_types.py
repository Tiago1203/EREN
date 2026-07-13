"""Boot types for the Cognitive Boot Manager.

Defines all types for the boot process.

Architecture only -- no implementations, no business logic.
"""


class BootState:
    """States during the boot process."""

    CREATED = "created"
    LOAD_CONFIGURATION = "load_configuration"
    CREATE_EVENT_BUS = "create_event_bus"
    CREATE_CAPABILITY_REGISTRY = "create_capability_registry"
    CREATE_CONTEXT_MANAGER = "create_context_manager"
    CREATE_MEMORY_ENGINE = "create_memory_engine"
    CREATE_KNOWLEDGE_ENGINE = "create_knowledge_engine"
    CREATE_TOOL_ENGINE = "create_tool_engine"
    CREATE_PLANNER = "create_planner"
    CREATE_REASONING = "create_reasoning"
    CREATE_DECISION = "create_decision"
    CREATE_SCHEDULER = "create_scheduler"
    CREATE_ORCHESTRATOR = "create_orchestrator"
    READY = "ready"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class BootStatus:
    """Status of a boot step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BootStep:
    """A single step in the boot process."""

    def __init__(
        self,
        name: str,
        state: str,
        status: str = BootStatus.PENDING,
        error: str = "",
        duration_ms: int = 0,
    ):
        self.name = name
        self.state = state
        self.status = status
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state,
            "status": self.status,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class BootResult:
    """Result of the boot process."""

    def __init__(
        self,
        success: bool,
        state: str,
        steps: list = None,
        error: str = "",
        duration_ms: int = 0,
        components: dict = None,
    ):
        self.success = success
        self.state = state
        self.steps = steps or []
        self.error = error
        self.duration_ms = duration_ms
        self.components = components or {}

    def to_dict(self):
        return {
            "success": self.success,
            "state": self.state,
            "steps": [s.to_dict() for s in self.steps],
            "error": self.error,
            "duration_ms": self.duration_ms,
            "components": self.components,
        }


class BootConfiguration:
    """Configuration for the boot process."""

    def __init__(
        self,
        config_path: str = "",
        environment: str = "development",
        enable_metrics: bool = True,
        enable_tracing: bool = True,
        enable_event_bus: bool = True,
        enable_capability_registry: bool = True,
        timeout_ms: int = 30000,
    ):
        self.config_path = config_path
        self.environment = environment
        self.enable_metrics = enable_metrics
        self.enable_tracing = enable_tracing
        self.enable_event_bus = enable_event_bus
        self.enable_capability_registry = enable_capability_registry
        self.timeout_ms = timeout_ms


# Boot sequence definition
BOOT_SEQUENCE = [
    ("load_configuration", "Load Configuration", BootState.LOAD_CONFIGURATION),
    ("create_event_bus", "Create Event Bus", BootState.CREATE_EVENT_BUS),
    ("create_capability_registry", "Create Capability Registry", BootState.CREATE_CAPABILITY_REGISTRY),
    ("create_context_manager", "Create Context Manager", BootState.CREATE_CONTEXT_MANAGER),
    ("create_memory_engine", "Create Memory Engine", BootState.CREATE_MEMORY_ENGINE),
    ("create_knowledge_engine", "Create Knowledge Engine", BootState.CREATE_KNOWLEDGE_ENGINE),
    ("create_tool_engine", "Create Tool Engine", BootState.CREATE_TOOL_ENGINE),
    ("create_planner", "Create Planner", BootState.CREATE_PLANNER),
    ("create_reasoning", "Create Reasoning Engine", BootState.CREATE_REASONING),
    ("create_decision", "Create Decision Engine", BootState.CREATE_DECISION),
    ("create_scheduler", "Create Scheduler", BootState.CREATE_SCHEDULER),
    ("create_orchestrator", "Create Orchestrator", BootState.CREATE_ORCHESTRATOR),
]
