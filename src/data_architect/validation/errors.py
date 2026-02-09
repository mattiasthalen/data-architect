"""Validation error types and formatting."""

from __future__ import annotations

from dataclasses import dataclass

from data_architect.models.spec import Spec


@dataclass(frozen=True)
class ValidationError:
    """A validation error with line number context."""

    field_path: str
    message: str
    line: int | None = None
    severity: str = "error"


@dataclass(frozen=True)
class ValidationResult:
    """Result of validation including spec and errors."""

    spec: Spec | None
    errors: list[ValidationError]

    @property
    def is_valid(self) -> bool:
        """Return True if there are no errors."""
        return len(self.errors) == 0


def format_errors(errors: list[ValidationError]) -> str:
    """Format validation errors with line numbers.

    Args:
        errors: List of validation errors

    Returns:
        Formatted error string with line numbers where available
    """
    lines = []
    for error in errors:
        if error.line is not None:
            lines.append(f"Line {error.line}: {error.message}")
        else:
            lines.append(f"{error.field_path}: {error.message}")
    return "\n".join(lines)
