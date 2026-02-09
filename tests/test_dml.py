"""Tests for DML/MERGE generation."""

import sqlglot
import sqlglot.expressions as sge

from data_architect.generation.dml import (
    build_anchor_merge,
    build_attribute_merge,
    build_knot_merge,
    build_tie_merge,
    generate_all_dml,
)
from data_architect.generation.naming import staging_table_name
from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.spec import Spec
from data_architect.models.tie import Role, Tie

# ============================================================================
# Anchor MERGE Tests
# ============================================================================


def test_build_anchor_merge_has_merge_keyword():
    """Verify the generated AST contains a MERGE or INSERT expression."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    result = build_anchor_merge(anchor, "tsql")

    # For tsql, should have MERGE node
    assert isinstance(result, (sge.Merge, sge.Insert))


def test_build_anchor_merge_matches_on_identity():
    """Verify the ON clause matches on the anchor identity column."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    result = build_anchor_merge(anchor, "tsql")

    sql = result.sql(dialect="tsql", pretty=True)

    # The ON clause should reference CU_ID
    assert "CU_ID" in sql


def test_build_anchor_merge_inserts_metadata():
    """Verify the INSERT clause includes metadata columns."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    result = build_anchor_merge(anchor, "postgres")

    sql = result.sql(dialect="postgres", pretty=True)

    # Metadata columns should be present
    assert "metadata_recorded_at" in sql
    assert "metadata_recorded_by" in sql
    assert "metadata_id" in sql


def test_build_anchor_merge_postgres_uses_on_conflict():
    """When dialect=postgres, verify output uses INSERT...ON CONFLICT pattern."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    result = build_anchor_merge(anchor, "postgres")

    sql = result.sql(dialect="postgres", pretty=True)

    # PostgreSQL should use INSERT...ON CONFLICT
    assert "INSERT" in sql.upper()
    assert "ON CONFLICT" in sql.upper()


def test_build_anchor_merge_tsql_uses_merge():
    """When dialect=tsql, verify output uses MERGE...WHEN NOT MATCHED syntax."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    result = build_anchor_merge(anchor, "tsql")

    sql = result.sql(dialect="tsql", pretty=True)

    # TSQL should use MERGE
    assert "MERGE" in sql.upper()
    assert "WHEN NOT MATCHED" in sql.upper()


def test_build_anchor_merge_uses_staging_table_name_convention():
    """Verify the staging source table name matches staging_table_name() exactly."""
    from data_architect.models.staging import StagingMapping

    anchor = Anchor(
        mnemonic="CU",
        descriptor="Customer",
        identity="bigint",
        staging_mappings=[
            StagingMapping(
                system="ERP",
                tenant="ACME",
                table="stg_customers",
                natural_key_columns=["customer_id"],
            )
        ],
    )
    result = build_anchor_merge(anchor, "postgres")

    sql = result.sql(dialect="postgres", pretty=True)

    # The SQL should reference the staging table name from naming.py
    expected_staging = staging_table_name(anchor.staging_mappings[0])
    assert expected_staging in sql


def test_build_anchor_merge_deterministic():
    """Two calls produce identical SQL (GEN-08)."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")

    result1 = build_anchor_merge(anchor, "postgres")
    result2 = build_anchor_merge(anchor, "postgres")

    sql1 = result1.sql(dialect="postgres", pretty=True)
    sql2 = result2.sql(dialect="postgres", pretty=True)

    assert sql1 == sql2


# ============================================================================
# Attribute MERGE Tests
# ============================================================================


def test_build_attribute_merge_historized_scd2():
    """For historized attribute, verify SCD2 append-only pattern."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="FN",
        descriptor="FirstName",
        data_range="VARCHAR(100)",
        time_range="TIMESTAMPTZ",
    )

    result = build_attribute_merge(anchor, attribute, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should insert new rows (append-only), not update old ones
    assert "INSERT" in sql.upper()
    # Should reference changed_at and recorded_at
    assert "changed_at" in sql
    assert "recorded_at" in sql


def test_build_attribute_merge_static_simple_upsert():
    """For static attribute, verify simple INSERT...ON CONFLICT DO UPDATE."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="EM", descriptor="Email", data_range="VARCHAR(255)", time_range=None
    )

    result = build_attribute_merge(anchor, attribute, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should use ON CONFLICT for static (no time_range)
    assert "ON CONFLICT" in sql.upper()


def test_build_attribute_merge_has_anchor_fk():
    """Verify the INSERT references the anchor FK column."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="FN", descriptor="FirstName", data_range="VARCHAR(100)"
    )

    result = build_attribute_merge(anchor, attribute, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should reference CU_ID (anchor FK)
    assert "CU_ID" in sql


def test_build_attribute_merge_multi_dialect():
    """Generate for postgres, tsql, snowflake -- all parse back without error."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="FN", descriptor="FirstName", data_range="VARCHAR(100)"
    )

    for dialect in ["postgres", "tsql", "snowflake"]:
        result = build_attribute_merge(anchor, attribute, dialect)
        sql = result.sql(dialect=dialect, pretty=True)

        # Should parse back cleanly
        parsed = sqlglot.parse_one(sql, dialect=dialect)
        assert parsed is not None


# ============================================================================
# Knot MERGE Tests
# ============================================================================


def test_build_knot_merge_insert_ignore():
    """Knots are static reference data. Verify INSERT-ignore pattern."""
    knot = Knot(
        mnemonic="GE", descriptor="Gender", identity="bigint", data_range="VARCHAR(20)"
    )

    result = build_knot_merge(knot, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should use INSERT...ON CONFLICT DO NOTHING for postgres
    assert "INSERT" in sql.upper()
    assert "ON CONFLICT" in sql.upper() or "DO NOTHING" in sql.upper()


def test_build_knot_merge_has_value_column():
    """Verify the knot value column is included in the INSERT."""
    knot = Knot(
        mnemonic="GE", descriptor="Gender", identity="bigint", data_range="VARCHAR(20)"
    )

    result = build_knot_merge(knot, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should reference GE_Gender (value column)
    assert "GE_Gender" in sql


# ============================================================================
# Tie MERGE Tests
# ============================================================================


def test_build_tie_merge_has_role_columns():
    """Verify all role FK columns appear in the MERGE key and INSERT."""
    tie = Tie(
        roles=[
            Role(type_="CU", role="customer"),
            Role(type_="OR", role="order"),
        ],
        time_range=None,
    )

    result = build_tie_merge(tie, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should reference both role FK columns
    assert "CU_ID_customer" in sql
    assert "OR_ID_order" in sql


def test_build_tie_merge_historized_has_bitemporal():
    """If tie has timeRange, verify bitemporal columns in pattern."""
    tie = Tie(
        roles=[
            Role(type_="CU", role="customer"),
            Role(type_="OR", role="order"),
        ],
        time_range="TIMESTAMPTZ",
    )

    result = build_tie_merge(tie, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should have bitemporal columns
    assert "changed_at" in sql
    assert "recorded_at" in sql


def test_build_tie_merge_static_insert_ignore():
    """If no timeRange, verify INSERT-ignore pattern."""
    tie = Tie(
        roles=[
            Role(type_="CU", role="customer"),
            Role(type_="PR", role="product"),
        ],
        time_range=None,
    )

    result = build_tie_merge(tie, "postgres")
    sql = result.sql(dialect="postgres", pretty=True)

    # Should use INSERT...ON CONFLICT for static
    assert "INSERT" in sql.upper()


# ============================================================================
# Integration Tests
# ============================================================================


def test_generate_all_dml_returns_dict():
    """Given a Spec, generate_all_dml(spec, dialect) returns dict[filename, sql]."""
    spec = Spec(
        anchors=[Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")],
        knots=[],
        ties=[],
    )

    result = generate_all_dml(spec, "postgres")

    assert isinstance(result, dict)
    assert len(result) > 0


def test_generate_all_dml_deterministic_order():
    """Keys and values identical across two calls."""
    spec = Spec(
        anchors=[
            Anchor(mnemonic="CU", descriptor="Customer", identity="bigint"),
            Anchor(mnemonic="OR", descriptor="Order", identity="bigint"),
        ],
        knots=[
            Knot(
                mnemonic="GE",
                descriptor="Gender",
                identity="bigint",
                data_range="VARCHAR(20)",
            )
        ],
        ties=[],
    )

    result1 = generate_all_dml(spec, "postgres")
    result2 = generate_all_dml(spec, "postgres")

    # Keys should be identical
    assert list(result1.keys()) == list(result2.keys())

    # Values should be identical
    for key in result1:
        assert result1[key] == result2[key]


def test_generate_all_dml_filenames_match_ddl():
    """DML filenames correspond to DDL entity names."""
    spec = Spec(
        anchors=[Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")],
        knots=[],
        ties=[],
    )

    result = generate_all_dml(spec, "postgres")

    # Should have a load file for the anchor
    assert "CU_Customer_load.sql" in result
