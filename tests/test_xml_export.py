"""Tests for XML export functionality."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from data_architect.cli import app
from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.spec import Nexus, Spec
from data_architect.models.staging import StagingMapping
from data_architect.models.tie import Role, Tie
from data_architect.xml_interop import (
    check_yaml_extensions,
    export_spec_to_xml,
    validate_xml_against_xsd,
)

runner = CliRunner()


# ============================================================================
# Extension detection tests
# ============================================================================


def test_check_no_extensions():
    """Spec with no YAML extensions returns empty list."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM", descriptor="Name", data_range="varchar(50)"
                    )
                ],
            )
        ]
    )
    extensions = check_yaml_extensions(spec)
    assert extensions == []


def test_check_staging_mappings_detected():
    """Anchor with staging_mappings returns warning."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM", descriptor="Name", data_range="varchar(50)"
                    )
                ],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    extensions = check_yaml_extensions(spec)
    assert len(extensions) == 1
    assert "OR" in extensions[0]
    assert "1 staging mapping" in extensions[0]


def test_check_staging_column_detected():
    """Attribute with staging_column returns warning."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM",
                        descriptor="Name",
                        data_range="varchar(50)",
                        staging_column="order_name",
                    )
                ],
            )
        ]
    )
    extensions = check_yaml_extensions(spec)
    assert len(extensions) == 1
    assert "OR.NAM" in extensions[0]
    assert "staging_column" in extensions[0]
    assert "order_name" in extensions[0]


def test_check_multiple_extensions():
    """Spec with both types returns all warnings."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM",
                        descriptor="Name",
                        data_range="varchar(50)",
                        staging_column="order_name",
                    )
                ],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    extensions = check_yaml_extensions(spec)
    assert len(extensions) == 2


def test_check_nexus_staging_column():
    """Nexus attribute with staging_column is detected."""
    spec = Spec(
        nexuses=[
            Nexus(
                mnemonic="EV",
                descriptor="Event",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="DAT",
                        descriptor="Date",
                        data_range="datetime",
                        staging_column="event_date",
                    )
                ],
                roles=[
                    Role(role="wasHeldAt", type_="ST", identifier=False),
                ],
            )
        ]
    )
    extensions = check_yaml_extensions(spec)
    assert len(extensions) == 1
    assert "EV.DAT" in extensions[0]


# ============================================================================
# Export function tests
# ============================================================================


def test_export_simple_spec():
    """Export minimal spec produces valid XML with expected elements."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM", descriptor="Name", data_range="varchar(50)"
                    )
                ],
            )
        ]
    )
    xml_output = export_spec_to_xml(spec)
    assert "<schema" in xml_output
    assert "<anchor" in xml_output
    assert "<attribute" in xml_output
    assert 'mnemonic="OR"' in xml_output
    assert 'mnemonic="NAM"' in xml_output


def test_export_includes_namespace():
    """Verify namespace is present as default namespace (no prefix)."""
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    xml_output = export_spec_to_xml(spec)
    assert 'xmlns="http://anchormodeling.com/schema"' in xml_output


def test_export_includes_xml_declaration():
    """Verify XML declaration is present."""
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    xml_output = export_spec_to_xml(spec)
    assert xml_output.startswith("<?xml")


def test_export_knots_ties_nexuses():
    """Export spec with all entity types verifies all present in XML."""
    spec = Spec(
        knots=[
            Knot(
                mnemonic="GEN",
                descriptor="Gender",
                identity="int",
                data_range="varchar(10)",
            )
        ],
        anchors=[
            Anchor(mnemonic="AC", descriptor="Actor", identity="int", attributes=[])
        ],
        nexuses=[
            Nexus(
                mnemonic="EV",
                descriptor="Event",
                identity="int",
                attributes=[],
                roles=[Role(role="wasHeldAt", type_="AC", identifier=False)],
            )
        ],
        ties=[
            Tie(
                roles=[
                    Role(role="subset", type_="AC", identifier=False),
                    Role(role="of", type_="AC", identifier=False),
                ]
            )
        ],
    )
    xml_output = export_spec_to_xml(spec)
    assert "<knot" in xml_output
    assert "<anchor" in xml_output
    assert "<nexus" in xml_output
    assert "<tie" in xml_output


def test_export_preserves_timerange():
    """Historized attribute and tie export correctly."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM",
                        descriptor="Name",
                        data_range="varchar(50)",
                        time_range="datetime",
                    )
                ],
            )
        ],
        ties=[
            Tie(
                time_range="datetime",
                roles=[
                    Role(role="at", type_="OR", identifier=True),
                    Role(role="in", type_="OR", identifier=True),
                ],
            )
        ],
    )
    xml_output = export_spec_to_xml(spec)
    assert 'timeRange="datetime"' in xml_output


def test_export_preserves_keys():
    """Key elements with stop/route/of/branch are preserved."""
    from data_architect.models.common import Key

    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="ST",
                descriptor="Stage",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="LOC",
                        descriptor="Location",
                        data_range="varchar(100)",
                        keys=[
                            Key(stop="1", route="1st", of_="ST", branch="1"),
                        ],
                    )
                ],
            )
        ]
    )
    xml_output = export_spec_to_xml(spec)
    assert "<key" in xml_output
    assert 'stop="1"' in xml_output
    assert 'route="1st"' in xml_output
    assert 'of="ST"' in xml_output


def test_export_preserves_identifiers():
    """Identifier elements on anchors/nexuses are preserved."""
    from data_architect.models.common import Identifier

    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="ST",
                descriptor="Stage",
                identity="int",
                attributes=[],
                identifiers=[Identifier(route="1st"), Identifier(route="2nd")],
            )
        ]
    )
    xml_output = export_spec_to_xml(spec)
    assert '<identifier route="1st"' in xml_output
    assert '<identifier route="2nd"' in xml_output


def test_export_raises_without_force():
    """Spec with staging_mappings, no --force, raises ValueError."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    with pytest.raises(ValueError, match="YAML-only extensions"):
        export_spec_to_xml(spec)


def test_export_succeeds_with_force():
    """Spec with staging_mappings, --force=True, succeeds."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    xml_output = export_spec_to_xml(spec, force=True)
    assert "<schema" in xml_output


def test_export_no_force_needed_without_extensions():
    """Spec without extensions, force=False, succeeds."""
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    xml_output = export_spec_to_xml(spec, force=False)
    assert "<schema" in xml_output


# ============================================================================
# XSD validation tests
# ============================================================================


def test_validate_valid_xml():
    """Valid Anchor XML passes validation."""
    valid_xml = b"""<?xml version="1.0"?>
<schema xmlns="http://anchormodeling.com/schema">
    <anchor mnemonic="OR" descriptor="Order" identity="int"/>
</schema>"""
    is_valid, errors = validate_xml_against_xsd(valid_xml)
    assert is_valid
    assert errors == []


def test_validate_invalid_xml():
    """Missing required attribute fails validation."""
    invalid_xml = b"""<?xml version="1.0"?>
<schema xmlns="http://anchormodeling.com/schema">
    <anchor descriptor="Order" identity="int"/>
</schema>"""
    is_valid, errors = validate_xml_against_xsd(invalid_xml)
    assert not is_valid
    assert len(errors) > 0


def test_exported_xml_passes_xsd():
    """Export a spec, validate the output against XSD."""
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[
                    Attribute(
                        mnemonic="NAM", descriptor="Name", data_range="varchar(50)"
                    )
                ],
            )
        ]
    )
    xml_output = export_spec_to_xml(spec)
    xml_bytes = xml_output.encode("utf-8")
    is_valid, errors = validate_xml_against_xsd(xml_bytes)
    assert is_valid, f"XSD validation errors: {errors}"


# ============================================================================
# CLI integration tests
# ============================================================================


def test_cli_export_creates_xml(tmp_path: Path):
    """Write YAML spec to tmp, run dab export, verify XML output exists."""
    from ruamel.yaml import YAML

    spec_path = tmp_path / "test.yaml"
    xml_path = tmp_path / "output.xml"

    # Create simple YAML spec
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    yaml = YAML()
    with spec_path.open("w") as f:
        yaml.dump(spec_dict, f)

    # Run export command
    result = runner.invoke(app, ["dab", "export", str(spec_path), "-o", str(xml_path)])
    assert result.exit_code == 0
    assert xml_path.exists()
    assert "Exported" in result.stdout


def test_cli_export_spec_not_found(tmp_path: Path):
    """Exit code 1 and error message when spec file doesn't exist."""
    spec_path = tmp_path / "nonexistent.yaml"
    xml_path = tmp_path / "output.xml"

    result = runner.invoke(app, ["dab", "export", str(spec_path), "-o", str(xml_path)])
    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_cli_export_warns_extensions(tmp_path: Path):
    """YAML spec with staging_mappings, no --force, exit 1 with warning."""
    from ruamel.yaml import YAML

    spec_path = tmp_path / "test.yaml"
    xml_path = tmp_path / "output.xml"

    # Create spec with staging mappings
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    yaml = YAML()
    with spec_path.open("w") as f:
        yaml.dump(spec_dict, f)

    # Run export without --force
    result = runner.invoke(app, ["dab", "export", str(spec_path), "-o", str(xml_path)])
    assert result.exit_code == 1
    assert "Warning" in result.stdout
    assert "YAML-only extensions" in result.stdout


def test_cli_export_force_succeeds(tmp_path: Path):
    """Same spec with --force, exit 0."""
    from ruamel.yaml import YAML

    spec_path = tmp_path / "test.yaml"
    xml_path = tmp_path / "output.xml"

    # Create spec with staging mappings
    spec = Spec(
        anchors=[
            Anchor(
                mnemonic="OR",
                descriptor="Order",
                identity="int",
                attributes=[],
                staging_mappings=[
                    StagingMapping(
                        system="erp",
                        tenant="acme",
                        table="stg_orders",
                        natural_key_columns=["order_id"],
                    )
                ],
            )
        ]
    )
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    yaml = YAML()
    with spec_path.open("w") as f:
        yaml.dump(spec_dict, f)

    # Run export with --force
    result = runner.invoke(
        app, ["dab", "export", str(spec_path), "-o", str(xml_path), "--force"]
    )
    assert result.exit_code == 0
    assert xml_path.exists()


def test_cli_export_no_overwrite(tmp_path: Path):
    """Output exists without --overwrite, exit 1."""
    from ruamel.yaml import YAML

    spec_path = tmp_path / "test.yaml"
    xml_path = tmp_path / "output.xml"

    # Create simple YAML spec
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    yaml = YAML()
    with spec_path.open("w") as f:
        yaml.dump(spec_dict, f)

    # Create existing XML file
    xml_path.write_text("<schema/>")

    # Run export without --overwrite
    result = runner.invoke(app, ["dab", "export", str(spec_path), "-o", str(xml_path)])
    assert result.exit_code == 1
    assert "already exists" in result.stdout


def test_cli_export_with_overwrite(tmp_path: Path):
    """Output exists with --overwrite, exit 0."""
    from ruamel.yaml import YAML

    spec_path = tmp_path / "test.yaml"
    xml_path = tmp_path / "output.xml"

    # Create simple YAML spec
    spec = Spec(
        anchors=[
            Anchor(mnemonic="OR", descriptor="Order", identity="int", attributes=[])
        ]
    )
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    yaml = YAML()
    with spec_path.open("w") as f:
        yaml.dump(spec_dict, f)

    # Create existing XML file
    xml_path.write_text("<schema/>")

    # Run export with --overwrite
    result = runner.invoke(
        app, ["dab", "export", str(spec_path), "-o", str(xml_path), "--overwrite"]
    )
    assert result.exit_code == 0
    assert xml_path.exists()
