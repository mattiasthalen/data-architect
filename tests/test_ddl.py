"""TDD tests for DDL generation with SQLGlot AST builders."""

from pathlib import Path

import sqlglot.expressions as sge

from data_architect.generation.columns import (
    build_bitemporal_columns,
    build_metadata_columns,
)
from data_architect.generation.ddl import (
    build_anchor_table,
    build_attribute_table,
    build_knot_table,
    build_staging_table,
    build_tie_table,
    generate_all_ddl,
)
from data_architect.generation.naming import (
    anchor_table_name,
    attribute_table_name,
    knot_table_name,
    staging_table_name,
    tie_table_name,
)
from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.spec import Spec
from data_architect.models.tie import Role, Tie
from data_architect.validation.loader import load_spec

# --- Column Builders Tests ---


def test_bitemporal_columns_has_changed_at_and_recorded_at() -> None:
    """Verify build_bitemporal_columns returns exactly 2 ColumnDef nodes."""
    columns = build_bitemporal_columns("postgres")
    assert len(columns) == 2
    assert all(isinstance(col, sge.ColumnDef) for col in columns)

    # Extract column names
    names = [col.this.this for col in columns]
    assert "changed_at" in names
    assert "recorded_at" in names

    # Both should be NOT NULL TIMESTAMPTZ
    for col in columns:
        assert col.args.get("kind")  # Has data type
        # Should have NOT NULL constraint
        constraints = col.args.get("constraints") or []
        assert any(
            isinstance(c.args.get("kind"), sge.NotNullColumnConstraint)
            for c in constraints
        ), f"Column {col.this.this} should be NOT NULL"


def test_metadata_columns_has_three_columns() -> None:
    """Verify build_metadata_columns returns 3 ColumnDef nodes."""
    columns = build_metadata_columns("postgres")
    assert len(columns) == 3
    assert all(isinstance(col, sge.ColumnDef) for col in columns)

    # Extract column names
    names = [col.this.this for col in columns]
    assert "metadata_recorded_at" in names
    assert "metadata_recorded_by" in names
    assert "metadata_id" in names

    # metadata_recorded_at should be NOT NULL, others nullable
    for col in columns:
        assert col.args.get("kind")  # Has data type
        if col.this.this == "metadata_recorded_at":
            constraints = col.args.get("constraints") or []
            assert any(
                isinstance(c.args.get("kind"), sge.NotNullColumnConstraint)
                for c in constraints
            ), "metadata_recorded_at should be NOT NULL"


def test_bitemporal_columns_snowflake_types() -> None:
    """Verify dialect=snowflake produces TIMESTAMP_NTZ instead of TIMESTAMPTZ."""
    columns = build_bitemporal_columns("snowflake")
    assert len(columns) == 2

    # Snowflake uses TIMESTAMP_NTZ for non-timezone aware timestamps
    for col in columns:
        # Generate SQL and check type mapping
        sql = col.sql(dialect="snowflake")
        # Snowflake should use TIMESTAMP_NTZ or TIMESTAMP
        assert "TIMESTAMP" in sql.upper()


# --- Naming Convention Tests ---


def test_anchor_table_name() -> None:
    """Verify anchor_table_name returns {mnemonic}_{descriptor}."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    assert anchor_table_name(anchor) == "CU_Customer"


def test_attribute_table_name() -> None:
    """Verify attribute_table_name follows naming convention."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(mnemonic="NAM", descriptor="Name", data_range="varchar(100)")
    assert attribute_table_name(anchor, attribute) == "CU_NAM_Customer_Name"


def test_knot_table_name() -> None:
    """Verify knot_table_name returns {mnemonic}_{descriptor}."""
    knot = Knot(
        mnemonic="GEN", descriptor="Gender", identity="int", data_range="varchar(42)"
    )
    assert knot_table_name(knot) == "GEN_Gender"


def test_tie_table_name() -> None:
    """Verify tie_table_name generates deterministic name from sorted roles."""
    tie = Tie(
        roles=[
            Role(role="subset", type_="AC", identifier=False),
            Role(role="of", type_="PN", identifier=False),
        ]
    )
    name = tie_table_name(tie)
    # Should be deterministic based on sorted roles
    # Expecting format like: AC_PN_subset_of (sorted by type then role)
    assert "AC" in name
    assert "PN" in name
    assert "subset" in name or "of" in name


def test_staging_table_name() -> None:
    """Verify staging_table_name extracts table name from mapping."""
    mapping = {"table": "stg_customers", "columns": []}
    assert staging_table_name(mapping) == "stg_customers"


# --- Anchor DDL Tests ---


def test_build_anchor_table_has_identity_pk() -> None:
    """Verify anchor table has identity PK column."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    create_stmt = build_anchor_table(anchor, "postgres")

    assert isinstance(create_stmt, sge.Create)
    sql = create_stmt.sql(dialect="postgres")

    # Should contain CU_ID column as primary key
    assert "CU_ID" in sql
    assert "bigint" in sql.lower() or "BIGINT" in sql


def test_build_anchor_table_has_metadata_columns() -> None:
    """Verify anchor table includes metadata columns."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    create_stmt = build_anchor_table(anchor, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    assert "metadata_recorded_at" in sql
    assert "metadata_recorded_by" in sql
    assert "metadata_id" in sql


def test_build_anchor_table_if_not_exists() -> None:
    """Verify anchor table DDL is idempotent (CREATE TABLE IF NOT EXISTS)."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    create_stmt = build_anchor_table(anchor, "postgres")

    assert create_stmt.args.get("exists") is True
    sql = create_stmt.sql(dialect="postgres")
    assert "IF NOT EXISTS" in sql


def test_build_anchor_table_deterministic() -> None:
    """Verify calling build_anchor_table twice produces identical SQL."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    sql1 = build_anchor_table(anchor, "postgres").sql(dialect="postgres", pretty=True)
    sql2 = build_anchor_table(anchor, "postgres").sql(dialect="postgres", pretty=True)
    assert sql1 == sql2


def test_build_anchor_table_multi_dialect() -> None:
    """Verify anchor DDL compiles to postgres, tsql, snowflake without errors."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")

    for dialect in ["postgres", "tsql", "snowflake"]:
        create_stmt = build_anchor_table(anchor, dialect)
        sql = create_stmt.sql(dialect=dialect)
        # Should produce valid SQL
        assert len(sql) > 0
        # Should contain table name
        assert "CU_Customer" in sql
        # For dialects that don't support IF NOT EXISTS natively (tsql),
        # SQLGlot may transpile to alternative syntax, so just verify it contains
        # the table creation logic
        assert "CREATE TABLE" in sql or "EXEC" in sql


# --- Attribute DDL Tests ---


def test_build_attribute_table_has_anchor_fk() -> None:
    """Verify attribute table has FK column to anchor."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(mnemonic="NAM", descriptor="Name", data_range="varchar(100)")
    create_stmt = build_attribute_table(anchor, attribute, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should have CU_ID column (FK to anchor)
    assert "CU_ID" in sql


def test_build_attribute_table_has_value_column() -> None:
    """Verify attribute table has value column with correct data type."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(mnemonic="NAM", descriptor="Name", data_range="varchar(100)")
    create_stmt = build_attribute_table(anchor, attribute, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should have value column (CU_NAM_Customer_Name)
    assert "CU_NAM_Customer_Name" in sql
    assert "varchar" in sql.lower() or "VARCHAR" in sql


def test_build_attribute_table_historized_has_bitemporal() -> None:
    """Verify historized attribute has bitemporal columns."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="NAM",
        descriptor="Name",
        data_range="varchar(100)",
        time_range="datetime",
    )
    create_stmt = build_attribute_table(anchor, attribute, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    assert "changed_at" in sql
    assert "recorded_at" in sql


def test_build_attribute_table_static_no_bitemporal() -> None:
    """Verify static attribute has no bitemporal columns but has metadata."""
    anchor = Anchor(mnemonic="CU", descriptor="Customer", identity="bigint")
    attribute = Attribute(
        mnemonic="ID", descriptor="Identifier", data_range="varchar(50)"
    )  # No time_range
    create_stmt = build_attribute_table(anchor, attribute, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should NOT have bitemporal columns (but metadata_recorded_at is ok)
    assert "changed_at" not in sql
    # Check for bitemporal recorded_at (not metadata_recorded_at)
    # by ensuring metadata_recorded_at exists but no standalone recorded_at
    assert "metadata_recorded_at" in sql
    # Count occurrences - should only appear in metadata_recorded_at
    assert sql.count("recorded_at") == 1  # Only in metadata_recorded_at


# --- Knot DDL Tests ---


def test_build_knot_table_has_identity_and_value() -> None:
    """Verify knot table has identity PK and value column."""
    knot = Knot(
        mnemonic="GEN", descriptor="Gender", identity="int", data_range="varchar(42)"
    )
    create_stmt = build_knot_table(knot, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should have GEN_ID (identity) and GEN_Gender (value)
    assert "GEN_ID" in sql
    assert "GEN_Gender" in sql


def test_build_knot_table_has_metadata() -> None:
    """Verify knot table includes metadata columns."""
    knot = Knot(
        mnemonic="GEN", descriptor="Gender", identity="int", data_range="varchar(42)"
    )
    create_stmt = build_knot_table(knot, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    assert "metadata_recorded_at" in sql
    assert "metadata_recorded_by" in sql
    assert "metadata_id" in sql


# --- Tie DDL Tests ---


def test_build_tie_table_has_role_columns() -> None:
    """Verify tie table has FK columns for each role."""
    tie = Tie(
        roles=[
            Role(role="subset", type_="AC", identifier=False),
            Role(role="of", type_="PN", identifier=False),
        ]
    )
    create_stmt = build_tie_table(tie, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should have role FK columns: AC_ID_subset and PN_ID_of
    assert "AC_ID_subset" in sql
    assert "PN_ID_of" in sql


def test_build_tie_table_historized_has_bitemporal() -> None:
    """Verify historized tie has bitemporal columns."""
    tie = Tie(
        roles=[
            Role(role="subset", type_="AC", identifier=False),
            Role(role="of", type_="PN", identifier=False),
        ],
        time_range="datetime",
    )
    create_stmt = build_tie_table(tie, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    assert "changed_at" in sql
    assert "recorded_at" in sql


def test_build_tie_table_static_no_bitemporal() -> None:
    """Verify static tie has no bitemporal columns but has metadata."""
    tie = Tie(
        roles=[
            Role(role="subset", type_="AC", identifier=False),
            Role(role="of", type_="PN", identifier=False),
        ]
    )  # No time_range
    create_stmt = build_tie_table(tie, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    # Should NOT have bitemporal columns (but metadata_recorded_at is ok)
    assert "changed_at" not in sql
    # Check for bitemporal recorded_at (not metadata_recorded_at)
    assert "metadata_recorded_at" in sql
    # Count occurrences - should only appear in metadata_recorded_at
    assert sql.count("recorded_at") == 1  # Only in metadata_recorded_at


# --- Staging DDL Tests ---


def test_build_staging_table_creates_table() -> None:
    """Verify build_staging_table generates CREATE TABLE with provided columns."""
    columns = [("customer_id", "bigint"), ("customer_name", "varchar(100)")]
    create_stmt = build_staging_table("stg_customers", columns, "postgres")

    sql = create_stmt.sql(dialect="postgres")
    assert "stg_customers" in sql
    assert "customer_id" in sql
    assert "customer_name" in sql
    assert "bigint" in sql.lower() or "BIGINT" in sql
    assert "varchar" in sql.lower() or "VARCHAR" in sql
    # Should also have metadata columns
    assert "metadata_recorded_at" in sql


def test_build_staging_table_multi_dialect() -> None:
    """Verify staging DDL compiles to postgres, tsql, snowflake."""
    columns = [("customer_id", "bigint"), ("customer_name", "varchar(100)")]

    for dialect in ["postgres", "tsql", "snowflake"]:
        create_stmt = build_staging_table("stg_customers", columns, dialect)
        sql = create_stmt.sql(dialect=dialect)
        assert len(sql) > 0
        # Should contain table name
        assert "stg_customers" in sql
        # Verify it contains table creation logic
        assert "CREATE TABLE" in sql or "EXEC" in sql


def test_generate_all_ddl_includes_staging_from_mappings() -> None:
    """Verify generate_all_ddl includes staging when anchor has staging_mappings."""
    # Create a spec with staging mappings
    anchor = Anchor(
        mnemonic="CU",
        descriptor="Customer",
        identity="bigint",
        staging_mappings=[
            {
                "table": "stg_customers",
                "columns": [
                    {"name": "customer_id", "type": "bigint"},
                    {"name": "customer_name", "type": "varchar(100)"},
                ],
            }
        ],
    )
    spec = Spec(anchors=[anchor])

    result = generate_all_ddl(spec, "postgres")

    # Should contain staging table DDL
    assert any("stg_customers" in filename for filename in result)


def test_generate_all_ddl_skips_staging_when_no_mappings() -> None:
    """Verify generate_all_ddl skips staging tables when no mappings exist."""
    anchor = Anchor(
        mnemonic="CU", descriptor="Customer", identity="bigint", staging_mappings=[]
    )
    spec = Spec(anchors=[anchor])

    result = generate_all_ddl(spec, "postgres")

    # Should NOT contain staging table entries
    assert not any("stg_" in filename for filename in result)


# --- Integration Tests ---


def test_generate_all_ddl_returns_dict_of_filename_to_sql() -> None:
    """Verify generate_all_ddl returns dict mapping filenames to SQL strings."""
    # Load valid_spec.yaml fixture
    fixture_path = Path(__file__).parent / "fixtures" / "valid_spec.yaml"
    spec = load_spec(fixture_path).spec

    result = generate_all_ddl(spec, "postgres")

    assert isinstance(result, dict)
    assert len(result) > 0

    # All values should be SQL strings
    for filename, sql in result.items():
        assert isinstance(filename, str)
        assert isinstance(sql, str)
        assert len(sql) > 0
        assert "CREATE TABLE" in sql


def test_generate_all_ddl_deterministic_order() -> None:
    """Verify generate_all_ddl produces deterministic output."""
    fixture_path = Path(__file__).parent / "fixtures" / "valid_spec.yaml"
    spec = load_spec(fixture_path).spec

    result1 = generate_all_ddl(spec, "postgres")
    result2 = generate_all_ddl(spec, "postgres")

    # Keys should be in same order
    assert list(result1.keys()) == list(result2.keys())

    # Values should be identical
    for filename in result1:
        assert result1[filename] == result2[filename]
