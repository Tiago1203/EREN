"""Tool Validation for EREN OS Universal Tool Calling Engine.

Validates tool schemas, parameters, and execution results.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from core.tools.catalog.base import ExternalTool
from core.tools.tool_types import ToolStatus


# =============================================================================
# Validation Types
# =============================================================================


class ValidationLevel(str, Enum):
    """Level of validation."""

    NONE = "none"
    SYNTAX = "syntax"  # Schema syntax only
    SEMANTIC = "semantic"  # Schema and types
    STRICT = "strict"  # Full validation


class ValidationErrorType(str, Enum):
    """Types of validation errors."""

    SCHEMA_INVALID = "schema_invalid"
    SCHEMA_MISSING = "schema_missing"
    PARAM_TYPE_MISMATCH = "param_type_mismatch"
    PARAM_REQUIRED_MISSING = "param_required_missing"
    PARAM_CONSTRAINT_VIOLATION = "param_constraint_violation"
    RESULT_TYPE_MISMATCH = "result_type_mismatch"
    SECURITY_VIOLATION = "security_violation"
    TIMEOUT_INVALID = "timeout_invalid"


@dataclass
class ValidationError:
    """A validation error."""

    error_type: ValidationErrorType
    message: str
    field_path: str = ""
    value: Any = None
    constraint: str = ""
    suggestion: str = ""


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


@dataclass
class ValidationConfig:
    """Configuration for validation."""

    level: ValidationLevel = ValidationLevel.SEMANTIC
    strict_types: bool = True
    allow_additional_params: bool = False
    validate_results: bool = True
    max_string_length: int = 100000
    max_array_length: int = 10000
    max_depth: int = 50


# =============================================================================
# Schema Validator
# =============================================================================


class SchemaValidator:
    """Validates JSON schemas and parameter types."""

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize schema validator.

        Args:
            config: Validation configuration.
        """
        self._config = config or ValidationConfig()

    @property
    def config(self) -> ValidationConfig:
        """Get validation configuration."""
        return self._config

    def validate_schema(self, schema: str) -> ValidationResult:
        """Validate JSON schema syntax.

        Args:
            schema: JSON schema string.

        Returns:
            Validation result.
        """
        errors = []

        try:
            parsed = json.loads(schema)
        except json.JSONDecodeError as e:
            errors.append(ValidationError(
                error_type=ValidationErrorType.SCHEMA_INVALID,
                message=f"Invalid JSON: {str(e)}",
                suggestion="Ensure schema is valid JSON",
            ))
            return ValidationResult(valid=False, errors=errors)

        # Validate schema structure
        if not isinstance(parsed, dict):
            errors.append(ValidationError(
                error_type=ValidationErrorType.SCHEMA_INVALID,
                message="Schema must be a JSON object",
            ))
            return ValidationResult(valid=False, errors=errors)

        # Check for required properties
        if "$schema" not in parsed:
            errors.append(ValidationError(
                error_type=ValidationErrorType.SCHEMA_INVALID,
                message="Missing '$schema' property",
                suggestion="Include JSON Schema draft identifier",
            ))

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def validate_parameters(
        self,
        params: dict,
        schema: str | dict,
    ) -> ValidationResult:
        """Validate parameters against schema.

        Args:
            params: Parameters to validate.
            schema: JSON schema.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Parse schema if string
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except json.JSONDecodeError:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SCHEMA_INVALID,
                    message="Invalid schema JSON",
                ))
                return ValidationResult(valid=False, errors=errors)

        # Get required properties
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required parameters
        for req_param in required:
            if req_param not in params:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_REQUIRED_MISSING,
                    message=f"Required parameter '{req_param}' is missing",
                    field_path=req_param,
                    suggestion=f"Provide value for '{req_param}'",
                ))

        # Check parameter types
        for param_name, param_value in params.items():
            if param_name not in properties:
                if not self._config.allow_additional_params:
                    warnings.append(f"Additional parameter '{param_name}' not in schema")
                continue

            param_schema = properties[param_name]
            param_errors = self._validate_param_type(
                param_name, param_value, param_schema
            )
            errors.extend(param_errors)

        # Check additional properties constraint
        if not self._config.allow_additional_params:
            additional = set(params.keys()) - set(properties.keys())
            if additional:
                for extra in additional:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.PARAM_CONSTRAINT_VIOLATION,
                        message=f"Additional property '{extra}' not allowed",
                        field_path=extra,
                    ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _validate_param_type(
        self,
        name: str,
        value: Any,
        schema: dict,
    ) -> list[ValidationError]:
        """Validate parameter type.

        Args:
            name: Parameter name.
            value: Parameter value.
            schema: Parameter schema.

        Returns:
            List of validation errors.
        """
        errors = []
        param_type = schema.get("type", "string")

        # Check type match
        if param_type == "string":
            if not isinstance(value, str):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be string",
                    field_path=name,
                    value=type(value).__name__,
                ))
            elif "maxLength" in schema:
                if len(value) > schema["maxLength"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.PARAM_CONSTRAINT_VIOLATION,
                        message=f"Parameter '{name}' exceeds max length {schema['maxLength']}",
                        field_path=name,
                        constraint=f"maxLength: {schema['maxLength']}",
                    ))

        elif param_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be integer",
                    field_path=name,
                    value=type(value).__name__,
                ))

        elif param_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be number",
                    field_path=name,
                    value=type(value).__name__,
                ))

        elif param_type == "boolean":
            if not isinstance(value, bool):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be boolean",
                    field_path=name,
                    value=type(value).__name__,
                ))

        elif param_type == "array":
            if not isinstance(value, list):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be array",
                    field_path=name,
                    value=type(value).__name__,
                ))
            elif "maxItems" in schema:
                if len(value) > schema["maxItems"]:
                    errors.append(ValidationError(
                        error_type=ValidationErrorType.PARAM_CONSTRAINT_VIOLATION,
                        message=f"Parameter '{name}' exceeds max items {schema['maxItems']}",
                        field_path=name,
                        constraint=f"maxItems: {schema['maxItems']}",
                    ))

        elif param_type == "object":
            if not isinstance(value, dict):
                errors.append(ValidationError(
                    error_type=ValidationErrorType.PARAM_TYPE_MISMATCH,
                    message=f"Parameter '{name}' must be object",
                    field_path=name,
                    value=type(value).__name__,
                ))

        return errors


# =============================================================================
# Result Validator
# =============================================================================


class ResultValidator:
    """Validates tool execution results."""

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize result validator.

        Args:
            config: Validation configuration.
        """
        self._config = config or ValidationConfig()

    def validate_result(
        self,
        result: Any,
        output_schema: str | dict | None = None,
    ) -> ValidationResult:
        """Validate execution result.

        Args:
            result: Result to validate.
            output_schema: Output schema.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Parse schema if string
        if isinstance(output_schema, str):
            try:
                output_schema = json.loads(output_schema)
            except json.JSONDecodeError:
                errors.append(ValidationError(
                    error_type=ValidationErrorType.SCHEMA_INVALID,
                    message="Invalid output schema JSON",
                ))
                return ValidationResult(valid=False, errors=errors)

        # Basic size checks
        if isinstance(result, str) and len(result) > self._config.max_string_length:
            warnings.append(f"Result string exceeds {self._config.max_string_length} chars")

        if isinstance(result, list) and len(result) > self._config.max_array_length:
            warnings.append(f"Result array exceeds {self._config.max_array_length} items")

        # Validate against schema
        if output_schema:
            schema_errors = self._validate_against_schema(result, output_schema)
            errors.extend(schema_errors)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _validate_against_schema(
        self,
        result: Any,
        schema: dict,
    ) -> list[ValidationError]:
        """Validate result against schema.

        Args:
            result: Result to validate.
            schema: Schema to validate against.

        Returns:
            List of validation errors.
        """
        errors = []
        result_type = schema.get("type", "object")

        if result_type == "string" and not isinstance(result, str):
            errors.append(ValidationError(
                error_type=ValidationErrorType.RESULT_TYPE_MISMATCH,
                message=f"Result must be string, got {type(result).__name__}",
            ))

        elif result_type == "object" and not isinstance(result, dict):
            errors.append(ValidationError(
                error_type=ValidationErrorType.RESULT_TYPE_MISMATCH,
                message=f"Result must be object, got {type(result).__name__}",
            ))

        elif result_type == "array" and not isinstance(result, list):
            errors.append(ValidationError(
                error_type=ValidationErrorType.RESULT_TYPE_MISMATCH,
                message=f"Result must be array, got {type(result).__name__}",
            ))

        return errors


# =============================================================================
# Tool Validator
# =============================================================================


class ToolValidator:
    """Validates tools and their definitions."""

    def __init__(self, config: ValidationConfig | None = None):
        """Initialize tool validator.

        Args:
            config: Validation configuration.
        """
        self._config = config or ValidationConfig()
        self._schema_validator = SchemaValidator(config)
        self._result_validator = ResultValidator(config)

    def validate_tool(self, tool: ExternalTool) -> ValidationResult:
        """Validate a tool definition.

        Args:
            tool: Tool to validate.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Check required fields
        if not tool.name:
            errors.append(ValidationError(
                error_type=ValidationErrorType.SCHEMA_MISSING,
                message="Tool name is required",
                field_path="name",
            ))

        if not tool.category:
            warnings.append("Tool category is not specified")

        # Validate input schema
        if tool.input_schema:
            schema_result = self._schema_validator.validate_schema(tool.input_schema)
            if not schema_result.valid:
                errors.extend(schema_result.errors)

        # Validate output schema
        if tool.output_schema:
            schema_result = self._schema_validator.validate_schema(tool.output_schema)
            if not schema_result.valid:
                errors.extend(schema_result.errors)

        # Validate timeout
        if tool.timeout <= 0:
            errors.append(ValidationError(
                error_type=ValidationErrorType.TIMEOUT_INVALID,
                message="Timeout must be positive",
                field_path="timeout",
                value=tool.timeout,
            ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
