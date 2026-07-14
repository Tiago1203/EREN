"""OpenAI Plugin for EREN OS.

Integrates OpenAI capability with the Plugin Framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from core.plugins import (
    PluginDescriptor,
    PluginContext,
    PluginState,
    PluginCategory,
    PluginPriority,
)
from plugins.openai.capability import OpenAICapability
from plugins.openai.configuration import OpenAIConfiguration

if TYPE_CHECKING:
    pass


@dataclass
class OpenAIPlugin:
    """OpenAI plugin for EREN.

    Exposes OpenAI capability through the Plugin Framework.
    """

    _plugin_id: str = "openai-reasoning"
    _version: str = "1.0.0"

    # Configuration
    _api_key: str = ""
    _config: OpenAIConfiguration | None = None

    # Capability
    _capability: OpenAICapability | None = None

    # State
    _state: PluginState = PluginState.DISCOVERED

    def __init__(
        self,
        api_key: str,
        config: OpenAIConfiguration | dict | None = None,
    ):
        """Initialize OpenAI plugin.

        Args:
            api_key: OpenAI API key.
            config: Optional configuration.
        """
        self._api_key = api_key
        self._config = config if isinstance(config, OpenAIConfiguration) else None

    def get_manifest(self) -> dict:
        """Get plugin manifest.

        Returns:
            Plugin manifest dictionary.
        """
        return {
            "plugin_id": self._plugin_id,
            "version": self._version,
            "name": "OpenAI Reasoning Plugin",
            "description": "OpenAI GPT reasoning capability for EREN",
            "author": "EREN Team",
            "category": PluginCategory.LLM.value,
            "priority": PluginPriority.HIGH.value,
            "contracts": ["ReasoningContract"],
            "dependencies": [],
            "capabilities": ["reasoning", "chat", "completion"],
        }

    def on_load(self, context: PluginContext) -> None:
        """Called when plugin is loaded.

        Args:
            context: Plugin context.
        """
        self._state = PluginState.LOADED

    def on_initialize(self, context: PluginContext) -> None:
        """Called when plugin is initialized.

        Args:
            context: Plugin context.
        """
        # Create capability
        self._capability = OpenAICapability(
            api_key=self._api_key,
            config=self._config,
        )

        # Initialize capability
        from core.sdk import CapabilityContext

        sdk_context = CapabilityContext(
            capability_id=self._plugin_id,
            runtime_context=context.runtime_config,
        )

        self._capability.initialize(sdk_context)
        self._state = PluginState.INITIALIZED

    def on_activate(self) -> None:
        """Called when plugin is activated."""
        self._state = PluginState.ACTIVE

    def on_deactivate(self) -> None:
        """Called when plugin is deactivated."""
        self._state = PluginState.PAUSED

    def get_capability(self) -> OpenAICapability | None:
        """Get the OpenAI capability.

        Returns:
            OpenAI capability instance.
        """
        return self._capability

    def get_metrics(self) -> dict:
        """Get plugin metrics.

        Returns:
            Metrics dictionary.
        """
        if self._capability:
            return self._capability.get_metrics()
        return {}

    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self._plugin_id

    @property
    def version(self) -> str:
        """Get plugin version."""
        return self._version

    @property
    def state(self) -> PluginState:
        """Get plugin state."""
        return self._state

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "plugin_id": self._plugin_id,
            "version": self._version,
            "state": self._state.value,
            "capability": "OpenAICapability" if self._capability else None,
            "metrics": self.get_metrics(),
        }


# Plugin factory
def create_openai_plugin(
    api_key: str,
    config: dict | None = None,
) -> OpenAIPlugin:
    """Create OpenAI plugin instance.

    Args:
        api_key: OpenAI API key.
        config: Optional configuration.

    Returns:
        OpenAI plugin instance.
    """
    return OpenAIPlugin(api_key=api_key, config=config)
