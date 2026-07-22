"""Tests for Result monad."""

from __future__ import annotations

import pytest

from core.PHASE_1.infrastructure.shared import Err, Ok, Result


class TestOk:
    """Tests for Ok variant of Result."""

    def test_ok_creation(self) -> None:
        """Ok should contain a value."""
        result: Result[int, str] = Ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False

    def test_ok_unwrap(self) -> None:
        """Ok unwrap should return the value."""
        result: Result[int, str] = Ok(42)
        assert result.unwrap() == 42

    def test_ok_unwrap_or(self) -> None:
        """Ok unwrap_or should return the value."""
        result: Result[int, str] = Ok(42)
        assert result.unwrap_or(0) == 42

    def test_ok_unwrap_err_panics(self) -> None:
        """Ok unwrap_err should panic."""
        result: Result[int, str] = Ok(42)
        with pytest.raises(RuntimeError, match="Called unwrap_err on Ok"):
            result.unwrap_err()

    def test_ok_map(self) -> None:
        """Ok map should transform the value."""
        result: Result[int, str] = Ok(21)
        mapped = result.map(lambda x: x * 2)
        assert mapped == Ok(42)

    def test_ok_map_err_preserves(self) -> None:
        """Ok map_err should preserve the Ok."""
        result: Result[int, str] = Ok(42)
        mapped = result.map_err(lambda e: e.upper())
        assert mapped == Ok(42)

    def test_ok_flat_map(self) -> None:
        """Ok flat_map should chain operations."""
        result: Result[int, str] = Ok(21)
        chained = result.flat_map(lambda x: Ok(x * 2))
        assert chained == Ok(42)

    def test_ok_flat_map_with_err(self) -> None:
        """Ok flat_map can return Err."""
        result: Result[int, str] = Ok(21)
        chained = result.flat_map(lambda x: Err("error"))
        assert chained == Err("error")

    def test_ok_str(self) -> None:
        """Ok str should be formatted correctly."""
        result: Result[int, str] = Ok(42)
        assert str(result) == "Ok(42)"


class TestErr:
    """Tests for Err variant of Result."""

    def test_err_creation(self) -> None:
        """Err should contain an error."""
        result: Result[int, str] = Err("error message")
        assert result.is_ok() is False
        assert result.is_err() is True

    def test_err_unwrap_panics(self) -> None:
        """Err unwrap should panic."""
        result: Result[int, str] = Err("error message")
        with pytest.raises(RuntimeError, match="Called unwrap on Err"):
            result.unwrap()

    def test_err_unwrap_or(self) -> None:
        """Err unwrap_or should return the default."""
        result: Result[int, str] = Err("error")
        assert result.unwrap_or(42) == 42

    def test_err_unwrap_err(self) -> None:
        """Err unwrap_err should return the error."""
        result: Result[int, str] = Err("error message")
        assert result.unwrap_err() == "error message"

    def test_err_map_preserves(self) -> None:
        """Err map should preserve the Err."""
        result: Result[int, str] = Err("error")
        mapped = result.map(lambda x: x * 2)
        assert mapped == Err("error")

    def test_err_map_err_transforms(self) -> None:
        """Err map_err should transform the error."""
        result: Result[int, str] = Err("error")
        mapped = result.map_err(lambda e: e.upper())
        assert mapped == Err("ERROR")

    def test_err_flat_map_preserves(self) -> None:
        """Err flat_map should preserve the Err."""
        result: Result[int, str] = Err("error")
        chained = result.flat_map(lambda x: Ok(x * 2))
        assert chained == Err("error")

    def test_err_str(self) -> None:
        """Err str should be formatted correctly."""
        result: Result[int, str] = Err("error")
        assert str(result) == "Err('error')"


class TestResultChaining:
    """Tests for Result chaining patterns."""

    def test_chain_of_maps(self) -> None:
        """Result should support chain of map operations."""
        result: Result[int, str] = Ok(10)
        final = result.map(lambda x: x + 5).map(lambda x: x * 2)
        assert final == Ok(30)

    def test_chain_with_err(self) -> None:
        """Chain should short-circuit on Err."""
        result: Result[int, str] = Err("initial error")
        final = (
            result.map(lambda x: x + 5)
            .map_err(lambda e: f"Transformed: {e}")
            .map(lambda x: x * 2)
        )
        assert final == Err("Transformed: initial error")

    def test_recovery_from_err(self) -> None:
        """Should be able to recover from Err by checking error is preserved."""
        result: Result[int, str] = Err("error")
        # Err cannot be recovered with map_err (that transforms error)
        # Recovery pattern requires flat_map to return new Result
        # This test documents the behavior
        assert result.is_err() is True
        assert result.unwrap_err() == "error"

    def test_filter_with_validation(self) -> None:
        """Result should support validation patterns."""
        def validate_positive(x: int) -> Result[int, str]:
            if x > 0:
                return Ok(x)
            return Err("Not positive")

        result = validate_positive(10).flat_map(validate_positive)
        assert result == Ok(10)

        result = validate_positive(-5).flat_map(validate_positive)
        assert result == Err("Not positive")
