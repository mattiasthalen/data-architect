"""Tests for dab init spec template generation."""

from __future__ import annotations

from ruamel.yaml import YAML

from data_architect.dab_init import generate_spec_template


def test_generate_returns_nonempty_string():
    """Result is non-empty string."""
    result = generate_spec_template()
    assert isinstance(result, str)
    assert len(result) > 0


def test_template_contains_anchor_section():
    """Output contains 'anchor' section."""
    result = generate_spec_template()
    assert "anchor" in result


def test_template_contains_knot_section():
    """Output contains 'knot' section."""
    result = generate_spec_template()
    assert "knot" in result


def test_template_contains_tie_section():
    """Output contains 'tie' section."""
    result = generate_spec_template()
    assert "tie" in result


def test_template_contains_nexus_section():
    """Output contains 'nexus' section."""
    result = generate_spec_template()
    assert "nexus" in result


def test_template_contains_anchor_comment():
    """Output contains comment text about anchors (e.g., 'entities or events')."""
    result = generate_spec_template()
    assert "entities" in result.lower() or "events" in result.lower()


def test_template_contains_staging_comment():
    """Output contains comment about staging mappings."""
    result = generate_spec_template()
    assert "staging" in result.lower()


def test_template_contains_keyset_comment():
    """Output contains comment about keyset identity format."""
    result = generate_spec_template()
    assert "keyset" in result.lower() or "@" in result


def test_template_is_valid_yaml():
    """Parse output with ruamel.yaml, no error."""
    result = generate_spec_template()
    yaml = YAML()
    data = yaml.load(result)
    assert data is not None


def test_template_has_example_anchor():
    """Parsed YAML contains at least one example anchor with mnemonic and descriptor."""
    result = generate_spec_template()
    yaml = YAML()
    data = yaml.load(result)

    assert "anchor" in data
    assert len(data["anchor"]) > 0

    first_anchor = data["anchor"][0]
    assert "mnemonic" in first_anchor
    assert "descriptor" in first_anchor


def test_template_has_example_attribute():
    """Parsed YAML contains at least one example attribute."""
    result = generate_spec_template()
    yaml = YAML()
    data = yaml.load(result)

    assert "anchor" in data
    assert len(data["anchor"]) > 0

    first_anchor = data["anchor"][0]
    assert "attribute" in first_anchor
    assert len(first_anchor["attribute"]) > 0
