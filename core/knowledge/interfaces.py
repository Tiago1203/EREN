"""Abstract interfaces (ports) for the Knowledge engine.

Defines the contract the engine exposes to the rest of EREN core. Empty
for now — method signatures will be declared here, but no logic lives here.
"""

from __future__ import annotations

from typing import Protocol


class KnowledgePort(Protocol):
    """Contract the Knowledge engine exposes to callers.

    Method signatures will be declared as responsibilities are formalized.
    Intentionally empty for now.
    """
