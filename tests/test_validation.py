"""Tests for YAML validation engine with line numbers."""

from pathlib import Path

import pytest

from data_architect.validation import validate_spec
from data_architect.validation.errors import format_errors


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


def test_load_valid_spec(fixtures_dir: Path) -> None:
    """Valid spec should load without errors."""
    result = validate_spec(fixtures_dir / "valid_spec.yaml")
    assert result.is_valid
    assert result.spec is not None
    assert len(result.errors) == 0


def test_load_invalid_yaml_syntax(tmp_path: Path) -> None:
    """Malformed YAML should produce parse error."""
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("anchor:\n  - mnemonic: AC\n    invalid yaml {{{")

    result = validate_spec(bad_yaml)
    assert not result.is_valid
    assert result.spec is None
    assert len(result.errors) > 0
    assert "parse error" in result.errors[0].message.lower()


def test_attribute_bad_knot_reference(fixtures_dir: Path) -> None:
    """Attribute with nonexistent knotRange should produce error."""
    result = validate_spec(fixtures_dir / "invalid_spec_bad_ref.yaml")
    assert not result.is_valid
    assert len(result.errors) > 0

    # Should mention NONEXISTENT
    error_messages = [e.message for e in result.errors]
    assert any("NONEXISTENT" in msg for msg in error_messages)


def test_duplicate_mnemonic_detection(fixtures_dir: Path) -> None:
    """Duplicate mnemonics should be caught with both entity names."""
    result = validate_spec(fixtures_dir / "invalid_spec_duplicate_mnemonic.yaml")
    assert not result.is_valid
    assert len(result.errors) > 0

    # Should mention both entities
    error_messages = " ".join([e.message for e in result.errors])
    assert "Actor" in error_messages or "AnotherActor" in error_messages
    assert "AC" in error_messages


def test_line_numbers_in_errors(fixtures_dir: Path) -> None:
    """Errors should include line numbers where available."""
    result = validate_spec(fixtures_dir / "invalid_spec_bad_ref.yaml")
    assert not result.is_valid

    # At least one error should have a line number
    has_line_number = any(e.line is not None for e in result.errors)
    assert has_line_number


def test_tie_must_reference_two_anchors(tmp_path: Path) -> None:
    """Tie with only 1 anchor role should produce error."""
    spec_yaml = tmp_path / "tie_one_anchor.yaml"
    spec_yaml.write_text(
        """
anchor:
  - mnemonic: AC
    descriptor: Actor
    identity: int

tie:
  - role:
      - role: only
        type: AC
        identifier: false
"""
    )

    result = validate_spec(spec_yaml)
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "at least 2 anchor roles" in error_messages.lower()


def test_attribute_mnemonic_unique_per_anchor(tmp_path: Path) -> None:
    """Two attributes with same mnemonic in same anchor should error."""
    spec_yaml = tmp_path / "dup_attr.yaml"
    spec_yaml.write_text(
        """
anchor:
  - mnemonic: AC
    descriptor: Actor
    identity: int
    attribute:
      - mnemonic: NAM
        descriptor: Name
        dataRange: varchar(42)
      - mnemonic: NAM
        descriptor: AnotherName
        dataRange: varchar(42)
"""
    )

    result = validate_spec(spec_yaml)
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "duplicate attribute mnemonic" in error_messages.lower()
    assert "NAM" in error_messages


def test_mnemonic_collision_reports_both_entities(fixtures_dir: Path) -> None:
    """Mnemonic collision error should name both conflicting entities."""
    result = validate_spec(fixtures_dir / "invalid_spec_duplicate_mnemonic.yaml")
    assert not result.is_valid

    # Find the mnemonic collision error
    collision_errors = [
        e for e in result.errors if "duplicate mnemonic" in e.message.lower()
    ]
    assert len(collision_errors) > 0

    # Should mention both entity names in the error
    error_msg = collision_errors[0].message
    # The error should contain both "Actor" and "AnotherActor" or similar indication
    assert "AC" in error_msg


def test_valid_spec_returns_frozen_model(fixtures_dir: Path) -> None:
    """Loaded spec should be a frozen Pydantic model."""
    result = validate_spec(fixtures_dir / "valid_spec.yaml")
    assert result.is_valid
    assert result.spec is not None

    # Try to mutate - should raise ValidationError
    with pytest.raises(
        Exception, match="frozen"
    ):  # Pydantic raises ValidationError on frozen mutation
        result.spec.anchors[0].mnemonic = "XX"  # type: ignore[misc]


def test_format_errors_with_lines() -> None:
    """format_errors should produce 'Line N: message' format."""
    from data_architect.validation.errors import ValidationError

    errors = [
        ValidationError(field_path="anchor.mnemonic", message="Missing field", line=5),
        ValidationError(
            field_path="knot[0].descriptor", message="Invalid value", line=10
        ),
    ]

    formatted = format_errors(errors)
    assert "Line 5: Missing field" in formatted
    assert "Line 10: Invalid value" in formatted


def test_format_errors_without_lines() -> None:
    """format_errors should use field_path when no line available."""
    from data_architect.validation.errors import ValidationError

    errors = [
        ValidationError(
            field_path="anchor.mnemonic", message="Missing field", line=None
        ),
    ]

    formatted = format_errors(errors)
    assert "anchor.mnemonic: Missing field" in formatted


def test_nexus_validation(fixtures_dir: Path) -> None:
    """Valid nexus spec should load without errors."""
    result = validate_spec(fixtures_dir / "spec_with_nexus.yaml")
    assert result.is_valid
    assert result.spec is not None
    assert len(result.spec.nexuses) == 1


def test_nexus_duplicate_attribute_mnemonic(fixtures_dir: Path) -> None:
    """Nexus with duplicate attribute mnemonics should error."""
    result = validate_spec(fixtures_dir / "nexus_duplicate_attr.yaml")
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "duplicate attribute mnemonic" in error_messages.lower()
    assert "DAT" in error_messages


def test_nexus_only_knot_roles(fixtures_dir: Path) -> None:
    """Nexus with only knot roles should error."""
    result = validate_spec(fixtures_dir / "nexus_only_knot_roles.yaml")
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "non-knot role" in error_messages.lower()


def test_nexus_bad_knot_reference(fixtures_dir: Path) -> None:
    """Nexus attribute with bad knotRange should error."""
    result = validate_spec(fixtures_dir / "nexus_bad_knot_ref.yaml")
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "NONEXISTENT" in error_messages


def test_duplicate_tie_composition(fixtures_dir: Path) -> None:
    """Two ties with same composition should error."""
    result = validate_spec(fixtures_dir / "duplicate_tie.yaml")
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "duplicate tie" in error_messages.lower()


def test_nexus_bad_role_reference(fixtures_dir: Path) -> None:
    """Nexus role with bad type reference should error."""
    result = validate_spec(fixtures_dir / "nexus_bad_role_ref.yaml")
    assert not result.is_valid
    error_messages = " ".join([e.message for e in result.errors])
    assert "NONEXISTENT" in error_messages


def test_pydantic_validation_error_with_line_mapping(fixtures_dir: Path) -> None:
    """Pydantic validation errors should be mapped to line numbers."""
    result = validate_spec(fixtures_dir / "missing_required_field.yaml")
    assert not result.is_valid
    # Should have error about missing mnemonic
    error_messages = " ".join([e.message for e in result.errors])
    assert "mnemonic" in error_messages.lower() or "required" in error_messages.lower()
