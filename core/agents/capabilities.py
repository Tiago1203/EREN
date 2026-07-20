"""Agent capabilities for EREN Cognitive Agent Runtime.

Defines and manages agent capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.agents.types import AgentCapability, AgentType

if TYPE_CHECKING:
    pass


class CapabilityRegistry:
    """Registry of available capabilities.

    The Registry does NOT:
    - Execute capabilities
    - Know about implementations

    It ONLY:
    - Defines capabilities
    - Maps capabilities to agents
    - Validates capability requests
    """

    # Standard capability templates
    STANDARD_CAPABILITIES = {
        # Engineering
        "engineering.analyze": AgentCapability(
            name="engineering.analyze",
            description="Analyze technical systems and data",
            risk_level="low",
        ),
        "engineering.diagnose": AgentCapability(
            name="engineering.diagnose",
            description="Diagnose technical issues",
            risk_level="medium",
        ),
        "engineering.repair": AgentCapability(
            name="engineering.repair",
            description="Recommend repair procedures",
            risk_level="high",
        ),

        # Medical
        "medical.diagnose": AgentCapability(
            name="medical.diagnose",
            description="Provide medical diagnosis support",
            risk_level="critical",
        ),
        "medical.treatment": AgentCapability(
            name="medical.treatment",
            description="Recommend treatment plans",
            risk_level="critical",
        ),
        "medical.monitor": AgentCapability(
            name="medical.monitor",
            description="Monitor patient data",
            risk_level="medium",
        ),

        # Research
        "research.query": AgentCapability(
            name="research.query",
            description="Query research databases",
            risk_level="low",
        ),
        "research.analyze": AgentCapability(
            name="research.analyze",
            description="Analyze research data",
            risk_level="low",
        ),
        "research.synthesize": AgentCapability(
            name="research.synthesize",
            description="Synthesize research findings",
            risk_level="low",
        ),

        # Device
        "device.status": AgentCapability(
            name="device.status",
            description="Check device status",
            risk_level="low",
        ),
        "device.configure": AgentCapability(
            name="device.configure",
            description="Configure device settings",
            risk_level="high",
        ),
        "device.diagnostics": AgentCapability(
            name="device.diagnostics",
            description="Run device diagnostics",
            risk_level="medium",
        ),

        # Knowledge
        "knowledge.retrieve": AgentCapability(
            name="knowledge.retrieve",
            description="Retrieve knowledge from base",
            risk_level="low",
        ),
        "knowledge.search": AgentCapability(
            name="knowledge.search",
            description="Search knowledge base",
            risk_level="low",
        ),
        "knowledge.citations": AgentCapability(
            name="knowledge.citations",
            description="Generate citations",
            risk_level="low",
        ),

        # Memory
        "memory.store": AgentCapability(
            name="memory.store",
            description="Store data in memory",
            risk_level="low",
        ),
        "memory.retrieve": AgentCapability(
            name="memory.retrieve",
            description="Retrieve from memory",
            risk_level="low",
        ),
        "memory.context": AgentCapability(
            name="memory.context",
            description="Build context from memory",
            risk_level="low",
        ),

        # Vision
        "vision.analyze": AgentCapability(
            name="vision.analyze",
            description="Analyze visual data",
            risk_level="medium",
        ),
        "vision.ocr": AgentCapability(
            name="vision.ocr",
            description="Extract text from images",
            risk_level="low",
        ),

        # Speech
        "speech.transcribe": AgentCapability(
            name="speech.transcribe",
            description="Transcribe speech to text",
            risk_level="low",
        ),
        "speech.synthesize": AgentCapability(
            name="speech.synthesize",
            description="Synthesize text to speech",
            risk_level="low",
        ),

        # Reasoning
        "reasoning.analyze": AgentCapability(
            name="reasoning.analyze",
            description="Perform analytical reasoning",
            risk_level="low",
        ),
        "reasoning.decide": AgentCapability(
            name="reasoning.decide",
            description="Make decisions",
            risk_level="medium",
        ),
        "reasoning.planning": AgentCapability(
            name="reasoning.planning",
            description="Create execution plans",
            risk_level="low",
        ),
    }

    def __init__(self):
        """Initialize capability registry."""
        self._capabilities: dict[str, AgentCapability] = {}
        self._agent_capabilities: dict[str, list[str]] = {}  # agent_id -> capabilities

        # Load standard capabilities
        for name, cap in self.STANDARD_CAPABILITIES.items():
            self._capabilities[name] = cap

    def register_capability(self, capability: AgentCapability) -> None:
        """Register a new capability.

        Args:
            capability: Capability to register.
        """
        self._capabilities[capability.name] = capability

    def get_capability(self, name: str) -> AgentCapability | None:
        """Get capability by name.

        Args:
            name: Capability name.

        Returns:
            Capability or None.
        """
        return self._capabilities.get(name)

    def get_all_capabilities(self) -> list[AgentCapability]:
        """Get all registered capabilities.

        Returns:
            List of capabilities.
        """
        return list(self._capabilities.values())

    def register_agent_capabilities(
        self,
        agent_id: str,
        capabilities: list[str],
    ) -> None:
        """Register capabilities for an agent.

        Args:
            agent_id: Agent ID.
            capabilities: List of capability names.
        """
        self._agent_capabilities[agent_id] = capabilities

    def get_agent_capabilities(self, agent_id: str) -> list[AgentCapability]:
        """Get capabilities for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of capabilities.
        """
        cap_names = self._agent_capabilities.get(agent_id, [])
        return [
            self._capabilities[name]
            for name in cap_names
            if name in self._capabilities
        ]

    def find_agents_with_capability(
        self,
        capability: str,
    ) -> list[str]:
        """Find agents with a capability.

        Args:
            capability: Capability name.

        Returns:
            List of agent IDs.
        """
        agents = []
        for agent_id, caps in self._agent_capabilities.items():
            if capability in caps:
                agents.append(agent_id)
        return agents

    def get_capabilities_for_type(
        self,
        agent_type: AgentType,
    ) -> list[AgentCapability]:
        """Get capabilities for an agent type.

        Args:
            agent_type: Type of agent.

        Returns:
            List of capabilities.
        """
        type_prefix = agent_type.value + "."
        return [
            cap for name, cap in self._capabilities.items()
            if name.startswith(type_prefix)
        ]


# Global registry
_global_registry: CapabilityRegistry | None = None
_registry_lock = __import__("threading").Lock()


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry.

    Returns:
        Global CapabilityRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = CapabilityRegistry()
        return _global_registry


def reset_capability_registry() -> None:
    """Reset the global capability registry."""
    global _global_registry
    with _registry_lock:
        _global_registry = None
