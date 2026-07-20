"""Result type for explicit error handling in EREN.

Result is a monad that represents either a success value or a failure.
It makes error handling explicit and prevents exceptions from being
silently ignored.

Based on Haskell's Either monad and Rust's Result type.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generic, TypeVar

if TYPE_CHECKING:
    pass

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
F = TypeVar("F")


@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    """Represents either a success (Ok) or failure (Err).

    This type makes error handling explicit and composable.
    Use Ok for success cases and Err for failures.

    Examples:
        >>> def divide(a: int, b: int) -> Result[int, str]:
        ...     if b == 0:
        ...         return Err("Division by zero")
        ...     return Ok(a / b)
        >>> result = divide(10, 2)
        >>> match result:
        ...     case Ok(value):
        ...         print(f"Result: {value}")
        ...     case Err(error):
        ...         print(f"Error: {error}")

    Anti-patterns to avoid:
        ❌ Don't use Result for expected business rules (use domain validation)
        ❌ Don't nest Results deeply (use flat_map or flatten)
        ❌ Don't ignore the error type (use specific error types)
        ❌ Don't use Result where exceptions are clearer (IO errors)
    """

    pass


@dataclass(frozen=True, slots=True)
class Ok(Result[T, E]):
    """Represents a successful result containing a value.

    Attributes:
        value: The success value of type T.
    """

    value: T

    def is_ok(self) -> bool:
        """Return True for Ok variant."""
        return True

    def is_err(self) -> bool:
        """Return False for Ok variant."""
        return False

    def unwrap(self) -> T:
        """Return the contained value.

        Panics if the result is Err.
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Return the contained value or a default."""
        return self.value

    def unwrap_err(self) -> E:
        """Panics with the contained error."""
        msg = f"Called unwrap_err on Ok({self.value})"
        raise RuntimeError(msg)

    def expect(self, message: str) -> T:
        """Return the contained value or panic with message."""
        return self.value

    def expect_err(self, message: str) -> E:
        """Panics with message (this is Err)."""
        msg = f"Called expect_err on Ok({self.value})"
        raise RuntimeError(msg)

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """Transform the contained value with fn."""
        return Ok(fn(self.value))

    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        """Transform the error with fn (identity for Ok)."""
        return Ok(self.value)

    def flat_map(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations that return Result."""
        return fn(self.value)

    def __str__(self) -> str:
        return f"Ok({self.value!r})"

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True, slots=True)
class Err(Result[T, E]):
    """Represents a failed result containing an error.

    Attributes:
        error: The failure value of type E.
    """

    error: E

    def is_ok(self) -> bool:
        """Return False for Err variant."""
        return False

    def is_err(self) -> bool:
        """Return True for Err variant."""
        return True

    def unwrap(self) -> T:
        """Panics with the contained error."""
        msg = f"Called unwrap on Err({self.error!r})"
        raise RuntimeError(msg)

    def unwrap_or(self, default: T) -> T:
        """Return the default value."""
        return default

    def unwrap_err(self) -> E:
        """Return the contained error."""
        return self.error

    def expect(self, message: str) -> T:
        """Panics with the provided message."""
        raise RuntimeError(message)

    def expect_err(self, message: str) -> E:
        """Return the contained error (this is Err)."""
        return self.error

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """Transform the value (identity for Err)."""
        return Err(self.error)

    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]:
        """Transform the error with fn."""
        return Err(fn(self.error))

    def flat_map(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations (returns this Err)."""
        return Err(self.error)

    def __str__(self) -> str:
        return f"Err({self.error!r})"

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type aliases for common usage
Success = Ok
Failure = Err
