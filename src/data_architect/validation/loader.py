"""YAML loading with line number tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from pydantic import ValidationError as PydanticValidationError
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from data_architect.models.spec import Spec
from data_architect.validation.errors import ValidationError, ValidationResult
from data_architect.validation.referential import check_referential_integrity


def load_yaml_with_lines(yaml_path: Path) -> tuple[dict[str, Any], dict[str, int]]:
    """Load YAML and capture line numbers for all fields.

    Args:
        yaml_path: Path to YAML file

    Returns:
        Tuple of (parsed data, field_path -> line_number mapping)
        Line numbers are 1-based for user display.
    """
    yaml = YAML()
    yaml.preserve_quotes = True

    with yaml_path.open("r") as f:
        data = yaml.load(f)

    line_map: dict[str, int] = {}

    def _capture_lines(obj: Any, path: str) -> None:
        """Recursively capture line numbers from YAML comments."""
        if isinstance(obj, CommentedMap):
            for key in obj:
                # Get line number for the key (0-based from ruamel, add 1)
                if hasattr(obj, "lc") and obj.lc is not None:
                    key_lc = obj.lc.key(key)
                    if key_lc is not None:
                        line = key_lc[0] + 1  # Convert to 1-based
                        field_path = f"{path}.{key}" if path else str(key)
                        line_map[field_path] = line

                # Recurse into value
                value = obj[key]
                field_path = f"{path}.{key}" if path else str(key)
                _capture_lines(value, field_path)

        elif isinstance(obj, CommentedSeq):
            for i, item in enumerate(obj):
                # Get line number for list item
                if hasattr(obj, "lc") and obj.lc is not None:
                    item_lc = obj.lc.item(i)
                    if item_lc is not None:
                        line = item_lc[0] + 1  # Convert to 1-based
                        field_path = f"{path}[{i}]"
                        line_map[field_path] = line

                # Recurse into item
                field_path = f"{path}[{i}]"
                _capture_lines(item, field_path)

    _capture_lines(data, "")

    return data, line_map


def load_spec(yaml_path: Path) -> ValidationResult:
    """Load YAML spec file into Spec model with validation.

    Args:
        yaml_path: Path to YAML spec file

    Returns:
        ValidationResult with spec or errors
    """
    try:
        raw_data, line_map = load_yaml_with_lines(yaml_path)
    except Exception as e:
        return ValidationResult(
            spec=None,
            errors=[ValidationError(field_path="", message=f"YAML parse error: {e}")],
        )

    # Try to validate with Pydantic
    try:
        spec = Spec.model_validate(raw_data)
        return ValidationResult(spec=spec, errors=[])
    except PydanticValidationError as e:
        # Map Pydantic errors to ValidationError with line numbers
        errors = []
        for err in e.errors():
            # Build field path from loc tuple
            field_path = ".".join(str(x) for x in err["loc"])
            message = err["msg"]

            # Try to find line number
            line = line_map.get(field_path)

            errors.append(
                ValidationError(field_path=field_path, message=message, line=line)
            )

        return ValidationResult(spec=None, errors=errors)


def validate_spec(yaml_path: Path) -> ValidationResult:
    """Full validation pipeline: load + referential integrity checks.

    Args:
        yaml_path: Path to YAML spec file

    Returns:
        ValidationResult with all errors (structural + referential)
    """
    # First load the spec
    result = load_spec(yaml_path)

    # If loading failed, return those errors
    if not result.is_valid or result.spec is None:
        return result

    # Run referential integrity checks
    _, line_map = load_yaml_with_lines(yaml_path)
    ref_errors = check_referential_integrity(result.spec, line_map)

    # Merge errors
    return ValidationResult(spec=result.spec, errors=result.errors + ref_errors)
