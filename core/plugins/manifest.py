"""Plugin Manifest for EREN OS Cognitive Plugin Framework.

Provides the manifest definition and parsing for plugins.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from core.plugins.exceptions import PluginManifestError
from core.plugins.types import PluginCategory, PluginManifest, PluginPriority

if TYPE_CHECKING:
    pass


@dataclass
class PluginManifestParser:
    """Parser for plugin manifests."""

    @classmethod
    def from_dict(cls, data: dict) -> PluginManifest:
        """Parse manifest from dictionary.

        Args:
            data: Manifest data dictionary.

        Returns:
            PluginManifest instance.

        Raises:
            PluginManifestError: If manifest is invalid.
        """
        cls._validate_required_fields(data)

        return PluginManifest(
            plugin_id=data["plugin_id"],
            version=data["version"],
            name=data.get("name", data["plugin_id"]),
            description=data.get("description", ""),
            author=data.get("author", ""),
            category=PluginCategory(data.get("category", "custom")),
            priority=data.get("priority", PluginPriority.NORMAL.value),
            contracts=tuple(data.get("contracts", [])),
            dependencies=tuple(data.get("dependencies", [])),
            capabilities=tuple(data.get("capabilities", [])),
            configuration=data.get("configuration", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> PluginManifest:
        """Parse manifest from file.

        Args:
            path: Path to manifest file.

        Returns:
            PluginManifest instance.

        Raises:
            PluginManifestError: If file cannot be read or parsed.
        """
        path = Path(path)

        if not path.exists():
            raise PluginManifestError(f"Manifest file not found: {path}", str(path))

        try:
            with open(path) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise PluginManifestError(f"Invalid JSON in manifest: {e}", str(path)) from e
        except Exception as e:
            raise PluginManifestError(f"Error reading manifest: {e}", str(path)) from e

    @classmethod
    def from_string(cls, content: str) -> PluginManifest:
        """Parse manifest from string.

        Args:
            content: Manifest content as string.

        Returns:
            PluginManifest instance.

        Raises:
            PluginManifestError: If content is invalid.
        """
        try:
            data = json.loads(content)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise PluginManifestError(f"Invalid JSON in manifest: {e}") from e

    @classmethod
    def _validate_required_fields(cls, data: dict) -> None:
        """Validate required manifest fields.

        Args:
            data: Manifest data.

        Raises:
            PluginManifestError: If required fields are missing.
        """
        required = ["plugin_id", "version"]
        missing = [f for f in required if f not in data]

        if missing:
            raise PluginManifestError(f"Missing required fields: {missing}")

        # Validate plugin_id format
        plugin_id = data["plugin_id"]
        if not cls._is_valid_plugin_id(plugin_id):
            raise PluginManifestError(
                f"Invalid plugin_id format: {plugin_id}. "
                f"Must be lowercase alphanumeric with hyphens."
            )

        # Validate version format
        version = data["version"]
        if not cls._is_valid_version(version):
            raise PluginManifestError(
                f"Invalid version format: {version}. "
                f"Must follow semver format (e.g., 1.0.0)."
            )

    @classmethod
    def _is_valid_plugin_id(cls, plugin_id: str) -> bool:
        """Check if plugin_id is valid.

        Args:
            plugin_id: Plugin ID to validate.

        Returns:
            True if valid.
        """
        import re
        return bool(re.match(r"^[a-z0-9][a-z0-9-]*$", plugin_id))

    @classmethod
    def _is_valid_version(cls, version: str) -> bool:
        """Check if version is valid semver.

        Args:
            version: Version to validate.

        Returns:
            True if valid.
        """
        import re
        return bool(re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$", version))


@dataclass
class PluginManifestBuilder:
    """Builder for creating plugin manifests."""

    _plugin_id: str = ""
    _version: str = "1.0.0"
    _name: str = ""
    _description: str = ""
    _author: str = ""
    _category: PluginCategory = PluginCategory.CUSTOM
    _priority: int = PluginPriority.NORMAL.value
    _contracts: list[str] = field(default_factory=list)
    _dependencies: list[str] = field(default_factory=list)
    _capabilities: list[str] = field(default_factory=list)
    _configuration: dict = field(default_factory=dict)
    _metadata: dict = field(default_factory=dict)

    def plugin_id(self, plugin_id: str) -> PluginManifestBuilder:
        """Set plugin ID.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Self for chaining.
        """
        self._plugin_id = plugin_id
        return self

    def version(self, version: str) -> PluginManifestBuilder:
        """Set version.

        Args:
            version: Version string.

        Returns:
            Self for chaining.
        """
        self._version = version
        return self

    def name(self, name: str) -> PluginManifestBuilder:
        """Set name.

        Args:
            name: Plugin name.

        Returns:
            Self for chaining.
        """
        self._name = name
        return self

    def description(self, description: str) -> PluginManifestBuilder:
        """Set description.

        Args:
            description: Plugin description.

        Returns:
            Self for chaining.
        """
        self._description = description
        return self

    def author(self, author: str) -> PluginManifestBuilder:
        """Set author.

        Args:
            author: Plugin author.

        Returns:
            Self for chaining.
        """
        self._author = author
        return self

    def category(self, category: PluginCategory) -> PluginManifestBuilder:
        """Set category.

        Args:
            category: Plugin category.

        Returns:
            Self for chaining.
        """
        self._category = category
        return self

    def priority(self, priority: int) -> PluginManifestBuilder:
        """Set priority.

        Args:
            priority: Plugin priority.

        Returns:
            Self for chaining.
        """
        self._priority = priority
        return self

    def implements(self, *contracts: str) -> PluginManifestBuilder:
        """Add contracts.

        Args:
            contracts: Contract names.

        Returns:
            Self for chaining.
        """
        self._contracts.extend(contracts)
        return self

    def depends_on(self, *dependencies: str) -> PluginManifestBuilder:
        """Add dependencies.

        Args:
            dependencies: Plugin IDs of dependencies.

        Returns:
            Self for chaining.
        """
        self._dependencies.extend(dependencies)
        return self

    def provides(self, *capabilities: str) -> PluginManifestBuilder:
        """Add capabilities.

        Args:
            capabilities: Capability names.

        Returns:
            Self for chaining.
        """
        self._capabilities.extend(capabilities)
        return self

    def configuration(self, config: dict) -> PluginManifestBuilder:
        """Set configuration.

        Args:
            config: Plugin configuration.

        Returns:
            Self for chaining.
        """
        self._configuration = config
        return self

    def metadata(self, metadata: dict) -> PluginManifestBuilder:
        """Set metadata.

        Args:
            metadata: Additional metadata.

        Returns:
            Self for chaining.
        """
        self._metadata = metadata
        return self

    def build(self) -> PluginManifest:
        """Build the manifest.

        Returns:
            PluginManifest instance.

        Raises:
            PluginManifestError: If manifest is invalid.
        """
        if not self._plugin_id:
            raise PluginManifestError("plugin_id is required")

        if not self._version:
            raise PluginManifestError("version is required")

        return PluginManifest(
            plugin_id=self._plugin_id,
            version=self._version,
            name=self._name or self._plugin_id,
            description=self._description,
            author=self._author,
            category=self._category,
            priority=self._priority,
            contracts=tuple(self._contracts),
            dependencies=tuple(self._dependencies),
            capabilities=tuple(self._capabilities),
            configuration=self._configuration,
            metadata=self._metadata,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return self.build().to_dict()
