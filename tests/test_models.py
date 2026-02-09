"""Tests for Pydantic spec models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from data_architect.models import (
    Anchor,
    Attribute,
    Key,
    Knot,
    Nexus,
    SchemaLayer,
    Spec,
    Tie,
)


def test_spec_from_valid_dict() -> None:
    """Construct Spec from dict matching example.xml structure."""
    spec_data = {
        "knot": [
            {
                "mnemonic": "GEN",
                "descriptor": "Gender",
                "identity": "bit",
                "dataRange": "varchar(42)",
            }
        ],
        "anchor": [
            {
                "mnemonic": "AC",
                "descriptor": "Actor",
                "identity": "int",
                "attribute": [
                    {
                        "mnemonic": "NAM",
                        "descriptor": "Name",
                        "dataRange": "varchar(42)",
                        "timeRange": "datetime",
                    },
                    {
                        "mnemonic": "GEN",
                        "descriptor": "Gender",
                        "knotRange": "GEN",
                    },
                ],
                "identifier": [{"route": "1st"}],
            }
        ],
        "tie": [
            {
                "role": [
                    {"role": "subset", "type": "AC", "identifier": False},
                    {"role": "of", "type": "PN", "identifier": False},
                ]
            }
        ],
    }

    spec = Spec.model_validate(spec_data)
    assert len(spec.knots) == 1
    assert len(spec.anchors) == 1
    assert len(spec.ties) == 1
    assert spec.anchors[0].mnemonic == "AC"
    assert len(spec.anchors[0].attributes) == 2


def test_anchor_requires_mnemonic() -> None:
    """Missing mnemonic raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Anchor.model_validate({"descriptor": "Customer", "identity": "int"})

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("mnemonic",) for e in errors)


def test_attribute_requires_exactly_one_range() -> None:
    """Attribute with both knotRange and dataRange raises error."""
    # Both ranges present
    with pytest.raises(ValidationError) as exc_info:
        Attribute.model_validate(
            {
                "mnemonic": "NAM",
                "descriptor": "Name",
                "knotRange": "GEN",
                "dataRange": "varchar(42)",
            }
        )
    assert "exactly one" in str(exc_info.value).lower()

    # Neither range present
    with pytest.raises(ValidationError) as exc_info:
        Attribute.model_validate({"mnemonic": "NAM", "descriptor": "Name"})
    assert "exactly one" in str(exc_info.value).lower()


def test_models_are_frozen() -> None:
    """Assigning to frozen model fields raises ValidationError."""
    anchor = Anchor(mnemonic="AC", descriptor="Customer", identity="int")

    with pytest.raises(ValidationError) as exc_info:
        anchor.mnemonic = "XX"  # type: ignore[misc]

    assert "frozen" in str(exc_info.value).lower()


def test_model_copy_works() -> None:
    """model_copy with update works on frozen models."""
    anchor = Anchor(mnemonic="AC", descriptor="Customer", identity="int")
    updated = anchor.model_copy(update={"descriptor": "NewCustomer"})

    assert updated.descriptor == "NewCustomer"
    assert anchor.descriptor == "Customer"  # Original unchanged


def test_schema_layer_tagging() -> None:
    """Inspect field metadata for schema layer tags."""
    # XML-core field
    mnemonic_field = Anchor.model_fields["mnemonic"]
    assert mnemonic_field.json_schema_extra is not None
    assert mnemonic_field.json_schema_extra["layer"] == SchemaLayer.XML_CORE.value

    # YAML-extension field
    staging_field = Anchor.model_fields["staging_mappings"]
    assert staging_field.json_schema_extra is not None
    assert staging_field.json_schema_extra["layer"] == SchemaLayer.YAML_EXT.value


def test_knot_construction() -> None:
    """Knot from valid dict succeeds."""
    knot_data = {
        "mnemonic": "GEN",
        "descriptor": "Gender",
        "identity": "bit",
        "dataRange": "varchar(42)",
    }
    knot = Knot.model_validate(knot_data)

    assert knot.mnemonic == "GEN"
    assert knot.descriptor == "Gender"
    assert knot.identity == "bit"
    assert knot.data_range == "varchar(42)"


def test_tie_with_roles() -> None:
    """Tie with list of roles from valid dict succeeds."""
    tie_data = {
        "role": [
            {"role": "subset", "type": "AC", "identifier": False},
            {"role": "of", "type": "PN", "identifier": False},
        ]
    }
    tie = Tie.model_validate(tie_data)

    assert len(tie.roles) == 2
    assert tie.roles[0].role == "subset"
    assert tie.roles[1].type_ == "PN"


def test_nexus_construction() -> None:
    """Nexus from valid dict succeeds."""
    nexus_data = {
        "mnemonic": "EV",
        "descriptor": "Event",
        "identity": "int",
        "attribute": [
            {"mnemonic": "DAT", "descriptor": "Date", "dataRange": "datetime"}
        ],
        "role": [{"role": "wasHeldAt", "type": "ST", "identifier": False}],
        "identifier": [{"route": "1st"}],
    }
    nexus = Nexus.model_validate(nexus_data)

    assert nexus.mnemonic == "EV"
    assert len(nexus.attributes) == 1
    assert len(nexus.roles) == 1
    assert len(nexus.identifiers) == 1


def test_key_alias_of() -> None:
    """Key with 'of' field works via alias."""
    key_data = {"stop": "1", "route": "1st", "of": "ST", "branch": "1"}
    key = Key.model_validate(key_data)

    assert key.of_ == "ST"
    assert key.stop == "1"
    assert key.route == "1st"


def test_attribute_data_range_only() -> None:
    """Attribute with only dataRange succeeds."""
    attr_data = {
        "mnemonic": "NAM",
        "descriptor": "Name",
        "dataRange": "varchar(42)",
    }
    attr = Attribute.model_validate(attr_data)

    assert attr.data_range == "varchar(42)"
    assert attr.knot_range is None


def test_attribute_knot_range_only() -> None:
    """Attribute with only knotRange succeeds."""
    attr_data = {"mnemonic": "GEN", "descriptor": "Gender", "knotRange": "GEN"}
    attr = Attribute.model_validate(attr_data)

    assert attr.knot_range == "GEN"
    assert attr.data_range is None
