"""Feature coverage validation tests for Northwind reference example.

Validates that northwind.yaml exercises all v0.3.0 features by inspecting
the loaded Spec model. These tests are fast (no generation needed) and verify
that the spec is comprehensive.
"""

from pathlib import Path

import pytest

from data_architect.validation.loader import validate_spec

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


def test_northwind_spec_loads_without_errors(spec):
    """Northwind spec loads via validate_spec() without errors."""
    # If we got here with the fixture, validation succeeded
    assert spec is not None


def test_northwind_entities_match_requirement(spec):
    """Spec covers all 7 required entities: 5 anchors + 2 knots."""
    anchor_descriptors = {a.descriptor for a in spec.anchors}
    knot_descriptors = {k.descriptor for k in spec.knots}

    # Required entities from NWND-01
    required_anchors = {"Customer", "Product", "Order", "Employee", "Supplier"}
    required_knots = {"Category", "Shipper"}

    assert required_anchors.issubset(anchor_descriptors), (
        f"Missing anchors: {required_anchors - anchor_descriptors}"
    )
    assert required_knots.issubset(knot_descriptors), (
        f"Missing knots: {required_knots - knot_descriptors}"
    )


def test_northwind_includes_keyset_identity(spec):
    """Every anchor has staging_mappings with system, tenant, natural_key_columns."""
    for anchor in spec.anchors:
        assert anchor.staging_mappings, (
            f"Anchor {anchor.mnemonic} missing staging_mappings (keyset identity)"
        )

        for mapping in anchor.staging_mappings:
            assert mapping.system, (
                f"{anchor.mnemonic}: missing system identifier in staging_mapping"
            )
            assert mapping.tenant, (
                f"{anchor.mnemonic}: missing tenant identifier in staging_mapping"
            )
            assert mapping.natural_key_columns, (
                f"{anchor.mnemonic}: missing natural_key_columns in staging_mapping"
            )


def test_northwind_includes_multi_source(spec):
    """At least one anchor has multiple staging_mappings (multi-source)."""
    multi_source_anchors = [a for a in spec.anchors if len(a.staging_mappings) > 1]
    assert multi_source_anchors, (
        "No anchors demonstrate multi-source staging (expected Product with northwind + sap)"
    )

    # Verify Product specifically is multi-source
    product = next((a for a in spec.anchors if a.mnemonic == "PR"), None)
    assert product is not None, "Product anchor not found"
    assert len(product.staging_mappings) == 2, (
        f"Product should have 2 sources, got {len(product.staging_mappings)}"
    )


def test_northwind_includes_temporal_attributes(spec):
    """At least one attribute has time_range (temporal/historized)."""
    temporal_attrs = []
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            if attr.time_range:
                temporal_attrs.append((anchor.mnemonic, attr.mnemonic))

    assert temporal_attrs, "No attributes demonstrate temporal tracking (timeRange)"
    # Should have many temporal attributes (names change, prices change, etc.)
    assert len(temporal_attrs) >= 3, (
        f"Expected at least 3 temporal attributes, got {len(temporal_attrs)}"
    )


def test_northwind_includes_static_attributes(spec):
    """At least one attribute has no time_range (static/non-historized)."""
    static_attrs = []
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            if attr.time_range is None:
                static_attrs.append((anchor.mnemonic, attr.mnemonic))

    assert static_attrs, "No attributes demonstrate static (no timeRange)"


def test_northwind_includes_knots(spec):
    """Spec includes knots for reference data."""
    assert len(spec.knots) >= 2, f"Expected at least 2 knots, got {len(spec.knots)}"


def test_northwind_includes_knot_reference(spec):
    """At least one attribute has knot_range (references a knot)."""
    knot_ref_attrs = []
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            if attr.knot_range:
                knot_ref_attrs.append((anchor.mnemonic, attr.mnemonic, attr.knot_range))

    assert knot_ref_attrs, "No attributes demonstrate knot references (knotRange)"

    # Verify the knot references are valid
    knot_mnemonics = {k.mnemonic for k in spec.knots}
    for anchor_mn, attr_mn, knot_ref in knot_ref_attrs:
        assert knot_ref in knot_mnemonics, (
            f"{anchor_mn}.{attr_mn} references non-existent knot {knot_ref}"
        )


def test_northwind_includes_ties(spec):
    """Spec includes ties for relationships."""
    assert len(spec.ties) >= 1, "No ties defined (missing relationship modeling)"


def test_northwind_includes_column_mappings(spec):
    """Every staging_mapping has non-empty column_mappings for lineage."""
    for anchor in spec.anchors:
        for mapping in anchor.staging_mappings:
            assert mapping.column_mappings, (
                f"{anchor.mnemonic}: missing column_mappings in staging_mapping"
            )


def test_northwind_includes_staging_columns(spec):
    """Every staging_mapping has non-empty columns list with StagingColumn objects."""
    for anchor in spec.anchors:
        for mapping in anchor.staging_mappings:
            assert mapping.columns, (
                f"{anchor.mnemonic}: missing columns in staging_mapping"
            )

            # Verify each column has required fields
            for col in mapping.columns:
                assert col.name, f"{anchor.mnemonic}: StagingColumn missing name"
                assert col.type, f"{anchor.mnemonic}: StagingColumn missing type"


def test_northwind_tie_has_identifier_roles(spec):
    """Ties have identifier roles (composite keys)."""
    for tie in spec.ties:
        identifier_roles = [r for r in tie.roles if r.identifier]
        assert len(identifier_roles) >= 2, (
            "Tie should have at least 2 identifier roles for composite key"
        )
