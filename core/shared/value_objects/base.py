"""Base Value Object for EREN domain.

Value Objects are immutable objects that are defined by their attributes
rather than a unique identity. They compare by value equality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class ValueObject:
    """Base class for all Value Objects in EREN domain.

    Value Objects are immutable and compared by their attributes.
    They should be used for concepts that are defined by their value
    rather than a unique identity.

    Examples:
        - Money, Address, DateRange
        - Priority, Status (enums)
        - Confidence, Probability

    Rules:
        1. Value Objects are immutable
        2. Two Value Objects with same attributes are equal
        3. Value Objects should be self-validating
        4. Value Objects should be simple and focused

    Anti-patterns to avoid:
        ❌ Don't add ID fields to Value Objects
        ❌ Don't add timestamps unless they define the value
        ❌ Don't add mutable collections
        ❌ Don't use Value Objects for entities
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self._is_equal(other)

    def __hash__(self) -> int:
        return self._compute_hash()

    def _is_equal(self, other: ValueObject) -> bool:
        """Compare all attributes for equality."""
        return self._get_attributes() == other._get_attributes()

    def _compute_hash(self) -> int:
        """Compute hash from all attributes."""
        return hash(self._get_attributes())

    def _get_attributes(self) -> tuple[Any, ...]:
        """Return tuple of all attributes for comparison."""
        attrs = []
        for key in self.__dataclass_fields__:
            value = getattr(self, key, None)
            if isinstance(value, ValueObject):
                attrs.append(value._get_attributes())
            elif isinstance(value, (list, dict, set, frozenset)):
                attrs.append(self._make_hashable(value))
            else:
                attrs.append(value)
        return tuple(attrs)

    @staticmethod
    def _make_hashable(obj: Any) -> Any:
        """Convert mutable collections to hashable equivalents."""
        if isinstance(obj, dict):
            return tuple(sorted((k, ValueObject._make_hashable(v)) for k, v in obj.items()))
        if isinstance(obj, list):
            return tuple(ValueObject._make_hashable(item) for item in obj)
        if isinstance(obj, set):
            return frozenset(ValueObject._make_hashable(item) for item in obj)
        return obj

    def validate(self) -> None:
        """Validate the value object.

        Override this method to add validation logic.
        Raise ValueError or DomainError if invalid.
        """
        pass
