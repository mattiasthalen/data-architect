"""Tests for XML import functionality."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from data_architect.cli import app
from data_architect.validation.loader import validate_spec
from data_architect.xml_interop import import_xml_string_to_spec, import_xml_to_spec


# Test fixtures
@pytest.fixture
def runner() -> CliRunner:
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def example_xml_path() -> Path:
    """Path to example.xml file."""
    return Path(__file__).parent.parent / ".references" / "anchor" / "example.xml"


# --- Unit tests for XML model parsing ---


def test_parse_simple_anchor_xml() -> None:
    """Parse a simple anchor with mnemonic, descriptor, identity."""
    xml = """<schema>
      <anchor mnemonic="PN" descriptor="Person" identity="int"/>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.anchors) == 1
    assert spec.anchors[0].mnemonic == "PN"
    assert spec.anchors[0].descriptor == "Person"
    assert spec.anchors[0].identity == "int"


def test_parse_anchor_with_attributes() -> None:
    """Parse anchor with attributes (one dataRange, one knotRange+timeRange)."""
    xml = """<schema>
      <knot mnemonic="GEN" descriptor="Gender" identity="int" dataRange="varchar(10)"/>
      <anchor mnemonic="AC" descriptor="Actor" identity="int">
        <attribute mnemonic="NAM" descriptor="Name" dataRange="varchar(42)"/>
        <attribute mnemonic="GEN" descriptor="Gender" knotRange="GEN"
                   timeRange="datetime"/>
      </anchor>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.anchors) == 1
    anchor = spec.anchors[0]
    assert len(anchor.attributes) == 2

    # First attribute: dataRange
    attr1 = anchor.attributes[0]
    assert attr1.mnemonic == "NAM"
    assert attr1.data_range == "varchar(42)"
    assert attr1.knot_range is None
    assert attr1.time_range is None

    # Second attribute: knotRange + timeRange
    attr2 = anchor.attributes[1]
    assert attr2.mnemonic == "GEN"
    assert attr2.knot_range == "GEN"
    assert attr2.data_range is None
    assert attr2.time_range == "datetime"


def test_parse_knot_xml() -> None:
    """Parse knot with all required fields."""
    xml = """<schema>
      <knot mnemonic="GEN" descriptor="Gender" identity="bit" dataRange="varchar(42)"/>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.knots) == 1
    knot = spec.knots[0]
    assert knot.mnemonic == "GEN"
    assert knot.descriptor == "Gender"
    assert knot.identity == "bit"
    assert knot.data_range == "varchar(42)"


def test_parse_tie_xml() -> None:
    """Parse tie with 2+ roles."""
    xml = """<schema>
      <knot mnemonic="RAT" descriptor="Rating" identity="int" dataRange="varchar(10)"/>
      <anchor mnemonic="AC" descriptor="Actor" identity="int"/>
      <anchor mnemonic="PR" descriptor="Program" identity="int"/>
      <tie timeRange="datetime">
        <role role="part" type="AC" identifier="true"/>
        <role role="in" type="PR" identifier="true"/>
        <role role="got" type="RAT" identifier="false"/>
      </tie>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.ties) == 1
    tie = spec.ties[0]
    assert tie.time_range == "datetime"
    assert len(tie.roles) == 3

    # Check roles
    assert tie.roles[0].role == "part"
    assert tie.roles[0].type_ == "AC"
    assert tie.roles[0].identifier is True

    assert tie.roles[1].role == "in"
    assert tie.roles[1].type_ == "PR"
    assert tie.roles[1].identifier is True

    assert tie.roles[2].role == "got"
    assert tie.roles[2].type_ == "RAT"
    assert tie.roles[2].identifier is False


def test_parse_nexus_xml() -> None:
    """Parse nexus with roles, attributes, identifiers."""
    xml = """<schema>
      <anchor mnemonic="ST" descriptor="Stage" identity="int"/>
      <nexus mnemonic="EV" descriptor="Event" identity="int">
        <attribute mnemonic="DAT" descriptor="Date" dataRange="datetime"/>
        <role role="wasHeldAt" type="ST" identifier="false"/>
        <identifier route="1st"/>
      </nexus>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.nexuses) == 1
    nexus = spec.nexuses[0]
    assert nexus.mnemonic == "EV"
    assert nexus.descriptor == "Event"
    assert nexus.identity == "int"
    assert len(nexus.attributes) == 1
    assert len(nexus.roles) == 1
    assert len(nexus.identifiers) == 1

    # Check attribute
    assert nexus.attributes[0].mnemonic == "DAT"
    assert nexus.attributes[0].data_range == "datetime"

    # Check role
    assert nexus.roles[0].role == "wasHeldAt"
    assert nexus.roles[0].type_ == "ST"

    # Check identifier
    assert nexus.identifiers[0].route == "1st"


def test_parse_role_with_keys() -> None:
    """Parse role containing key children."""
    xml = """<schema>
      <anchor mnemonic="ST" descriptor="Stage" identity="int"/>
      <nexus mnemonic="EV" descriptor="Event" identity="int">
        <role role="wasHeldAt" type="ST" identifier="false">
          <key stop="2" route="1st" of="EV" branch="2"/>
        </role>
      </nexus>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    nexus = spec.nexuses[0]
    role = nexus.roles[0]
    assert len(role.keys) == 1
    key = role.keys[0]
    assert key.stop == "2"
    assert key.route == "1st"
    assert key.of_ == "EV"
    assert key.branch == "2"


def test_parse_attribute_with_metadata() -> None:
    """Parse attribute containing metadata element with attributes."""
    xml = """<schema>
      <anchor mnemonic="ST" descriptor="Stage" identity="int">
        <attribute mnemonic="NAM" descriptor="Name" dataRange="varchar(42)">
          <metadata equivalent="true"/>
        </attribute>
      </anchor>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    anchor = spec.anchors[0]
    attr = anchor.attributes[0]
    assert attr.metadata_ is not None
    assert attr.metadata_["equivalent"] == "true"


# --- Integration tests for full import ---


def test_import_minimal_xml() -> None:
    """Import schema with one anchor, one attribute."""
    xml = """<schema>
      <anchor mnemonic="PN" descriptor="Person" identity="int">
        <attribute mnemonic="NAM" descriptor="Name" dataRange="varchar(100)"/>
      </anchor>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.anchors) == 1
    assert len(spec.anchors[0].attributes) == 1


def test_import_example_xml(example_xml_path: Path) -> None:
    """Parse .references/anchor/example.xml with correct element counts."""
    spec = import_xml_to_spec(example_xml_path)

    # Verify counts: 7 knots, 4 anchors, 1 nexus, 7 ties
    assert len(spec.knots) == 7
    assert len(spec.anchors) == 4
    assert len(spec.nexuses) == 1
    assert len(spec.ties) == 7

    # Verify specific anchors
    anchor_mnemonics = [a.mnemonic for a in spec.anchors]
    assert set(anchor_mnemonics) == {"PN", "ST", "AC", "PR"}

    # Verify ST has 4 attributes
    st = next(a for a in spec.anchors if a.mnemonic == "ST")
    assert len(st.attributes) == 4

    # Verify AC has 3 attributes
    ac = next(a for a in spec.anchors if a.mnemonic == "AC")
    assert len(ac.attributes) == 3

    # Verify nexus EV has 3 roles and 3 attributes
    ev = spec.nexuses[0]
    assert ev.mnemonic == "EV"
    assert len(ev.roles) == 3
    assert len(ev.attributes) == 3


def test_import_namespaced_xml() -> None:
    """Parse XML with xmlns namespace declaration."""
    xml = """<schema xmlns="http://anchormodeling.com/schema">
      <anchor mnemonic="PN" descriptor="Person" identity="int"/>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.anchors) == 1
    assert spec.anchors[0].mnemonic == "PN"


def test_import_preserves_key_elements() -> None:
    """Verify Key(stop, route, of, branch) round-trips correctly."""
    xml = """<schema>
      <anchor mnemonic="ST" descriptor="Stage" identity="int">
        <attribute mnemonic="NAM" descriptor="Name" dataRange="varchar(42)">
          <key stop="1" route="2nd" of="ST" branch="1"/>
        </attribute>
      </anchor>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    attr = spec.anchors[0].attributes[0]
    assert len(attr.keys) == 1
    key = attr.keys[0]
    assert key.stop == "1"
    assert key.route == "2nd"
    assert key.of_ == "ST"
    assert key.branch == "1"


def test_import_preserves_identifiers() -> None:
    """Verify Identifier(route) preserved on anchors/nexuses."""
    xml = """<schema>
      <anchor mnemonic="AC" descriptor="Actor" identity="int">
        <identifier route="1st"/>
      </anchor>
      <nexus mnemonic="EV" descriptor="Event" identity="int">
        <identifier route="1st"/>
      </nexus>
    </schema>"""
    spec = import_xml_string_to_spec(xml)

    # Check anchor identifier
    assert len(spec.anchors[0].identifiers) == 1
    assert spec.anchors[0].identifiers[0].route == "1st"

    # Check nexus identifier
    assert len(spec.nexuses[0].identifiers) == 1
    assert spec.nexuses[0].identifiers[0].route == "1st"


# --- CLI integration tests ---


def test_cli_import_creates_yaml(
    runner: CliRunner, example_xml_path: Path, tmp_path: Path
) -> None:
    """CLI import creates valid YAML output."""
    output_path = tmp_path / "output.yaml"
    result = runner.invoke(
        app,
        ["dab", "import", str(example_xml_path), "-o", str(output_path)],
    )
    assert result.exit_code == 0
    assert output_path.exists()

    # Verify output is valid by loading it
    spec_result = validate_spec(output_path)
    assert spec_result.spec is not None
    assert len(spec_result.spec.knots) == 7
    assert len(spec_result.spec.anchors) == 4


def test_cli_import_file_not_found(runner: CliRunner, tmp_path: Path) -> None:
    """CLI import shows error for missing XML file."""
    output_path = tmp_path / "output.yaml"
    result = runner.invoke(
        app,
        ["dab", "import", "nonexistent.xml", "-o", str(output_path)],
    )
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_cli_import_no_overwrite(
    runner: CliRunner, example_xml_path: Path, tmp_path: Path
) -> None:
    """CLI import exits when output exists without --overwrite."""
    output_path = tmp_path / "output.yaml"
    output_path.write_text("existing content")

    result = runner.invoke(
        app,
        ["dab", "import", str(example_xml_path), "-o", str(output_path)],
    )
    assert result.exit_code == 1
    assert "already exists" in result.stdout


def test_cli_import_with_overwrite(
    runner: CliRunner, example_xml_path: Path, tmp_path: Path
) -> None:
    """CLI import with --overwrite replaces existing file."""
    output_path = tmp_path / "output.yaml"
    output_path.write_text("old content")

    result = runner.invoke(
        app,
        ["dab", "import", str(example_xml_path), "-o", str(output_path), "--overwrite"],
    )
    assert result.exit_code == 0

    # Verify file was replaced (not just appended)
    content = output_path.read_text()
    assert "old content" not in content
    assert "anchor:" in content


# --- Edge cases ---


def test_import_empty_schema() -> None:
    """<schema/> produces Spec with empty lists."""
    xml = "<schema/>"
    spec = import_xml_string_to_spec(xml)
    assert len(spec.knots) == 0
    assert len(spec.anchors) == 0
    assert len(spec.nexuses) == 0
    assert len(spec.ties) == 0


def test_import_anchor_no_attributes() -> None:
    """Anchor with no child elements is valid."""
    xml = """<schema>
      <anchor mnemonic="PN" descriptor="Person" identity="int"/>
    </schema>"""
    spec = import_xml_string_to_spec(xml)
    assert len(spec.anchors) == 1
    assert len(spec.anchors[0].attributes) == 0
    assert len(spec.anchors[0].identifiers) == 0


def test_import_invalid_xml_raises_error() -> None:
    """Malformed XML raises ValueError."""
    xml = "<schema><anchor>broken"
    with pytest.raises(ValueError, match="Invalid XML"):
        import_xml_string_to_spec(xml)


def test_import_file_not_found_raises_error(tmp_path: Path) -> None:
    """import_xml_to_spec raises FileNotFoundError for missing file."""
    nonexistent = tmp_path / "missing.xml"
    with pytest.raises(FileNotFoundError, match="not found"):
        import_xml_to_spec(nonexistent)
