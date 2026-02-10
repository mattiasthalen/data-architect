"""XML interoperability tests for Northwind reference example.

Tests that validate the Northwind spec works with XML export/import,
including round-trip preservation of XML-core fields and detection of
YAML-extension fields that don't round-trip.
"""

from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from data_architect.validation.loader import validate_spec
from data_architect.xml_interop import (
    check_yaml_extensions,
    export_spec_to_xml,
    import_xml_to_spec,
)

# Resolve spec path relative to project root
NORTHWIND_SPEC = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "northwind"
    / "northwind.yaml"
)


@pytest.fixture(scope="module")
def spec():
    """Load and validate Northwind spec once for all tests."""
    result = validate_spec(NORTHWIND_SPEC)
    assert result.is_valid, f"Spec validation failed: {result.errors}"
    assert result.spec is not None, "Spec is None after validation"
    return result.spec


def test_northwind_exports_to_xml(spec):
    """export_spec_to_xml() returns valid XML string without error."""
    # force=True needed because spec has YAML-only extensions (staging_mappings)
    xml_str = export_spec_to_xml(spec, force=True)

    assert xml_str, "Exported XML is empty"
    assert isinstance(xml_str, str), "Exported XML is not a string"


def test_northwind_exported_xml_is_well_formed(spec):
    """Exported XML string parses without error."""
    xml_str = export_spec_to_xml(spec, force=True)

    try:
        ET.fromstring(xml_str)  # noqa: S314 - parsing known-good XML in test
    except Exception as e:
        pytest.fail(f"XML is not well-formed: {e}")


def test_northwind_xml_reimports_without_errors(spec, tmp_path):
    """XML export can be imported back to Spec without error."""
    # Export to XML
    xml_str = export_spec_to_xml(spec, force=True)

    # Write to temp file
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")

    # Import back
    try:
        reimported_spec = import_xml_to_spec(temp_xml)
        assert reimported_spec is not None, "Reimported spec is None"
    except Exception as e:
        pytest.fail(f"XML import failed: {e}")


def test_northwind_roundtrip_preserves_anchor_count(spec, tmp_path):
    """After export→import round-trip, anchor count is preserved."""
    # Export to XML
    xml_str = export_spec_to_xml(spec, force=True)

    # Write to temp file and import
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")
    reimported_spec = import_xml_to_spec(temp_xml)

    # Compare counts
    assert len(reimported_spec.anchors) == len(spec.anchors), (
        f"Anchor count changed: {len(spec.anchors)} -> {len(reimported_spec.anchors)}"
    )


def test_northwind_roundtrip_preserves_knot_count(spec, tmp_path):
    """After export→import round-trip, knot count is preserved."""
    # Export to XML
    xml_str = export_spec_to_xml(spec, force=True)

    # Write to temp file and import
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")
    reimported_spec = import_xml_to_spec(temp_xml)

    # Compare counts
    assert len(reimported_spec.knots) == len(spec.knots), (
        f"Knot count changed: {len(spec.knots)} -> {len(reimported_spec.knots)}"
    )


def test_northwind_roundtrip_preserves_tie_count(spec, tmp_path):
    """After export→import round-trip, tie count is preserved."""
    # Export to XML
    xml_str = export_spec_to_xml(spec, force=True)

    # Write to temp file and import
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")
    reimported_spec = import_xml_to_spec(temp_xml)

    # Compare counts
    assert len(reimported_spec.ties) == len(spec.ties), (
        f"Tie count changed: {len(spec.ties)} -> {len(reimported_spec.ties)}"
    )


def test_northwind_check_yaml_extensions(spec):
    """check_yaml_extensions() returns non-empty list for Northwind spec."""
    # Northwind has staging_mappings (YAML extension), so should detect extensions
    extensions = check_yaml_extensions(spec)

    assert extensions, (
        "Expected YAML extensions (staging_mappings) but check_yaml_extensions returned empty"
    )

    # Verify staging_mappings is mentioned in extension descriptions
    extensions_text = " ".join(extensions)
    assert "staging mapping" in extensions_text.lower(), (
        "staging_mappings not detected as YAML extension"
    )


def test_northwind_roundtrip_preserves_anchor_mnemonics(spec, tmp_path):
    """After round-trip, anchor mnemonics are preserved."""
    xml_str = export_spec_to_xml(spec, force=True)
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")
    reimported_spec = import_xml_to_spec(temp_xml)

    original_mnemonics = {a.mnemonic for a in spec.anchors}
    reimported_mnemonics = {a.mnemonic for a in reimported_spec.anchors}

    assert original_mnemonics == reimported_mnemonics, (
        f"Anchor mnemonics differ: {original_mnemonics} vs {reimported_mnemonics}"
    )


def test_northwind_roundtrip_loses_staging_mappings(spec, tmp_path):
    """After round-trip, staging_mappings are lost (YAML-only field)."""
    xml_str = export_spec_to_xml(spec, force=True)
    temp_xml = tmp_path / "northwind.xml"
    temp_xml.write_text(xml_str, encoding="utf-8")
    reimported_spec = import_xml_to_spec(temp_xml)

    # Original spec has staging_mappings
    original_has_staging = any(a.staging_mappings for a in spec.anchors)
    assert original_has_staging, "Original spec should have staging_mappings"

    # Reimported spec should NOT have staging_mappings (lost in XML)
    reimported_has_staging = any(a.staging_mappings for a in reimported_spec.anchors)
    assert not reimported_has_staging, (
        "Reimported spec should not have staging_mappings (YAML-only field)"
    )
