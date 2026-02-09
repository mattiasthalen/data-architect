"""Tests for keyset identity SQL expression generation."""

import pytest
import sqlglot as sg

from data_architect.generation.keyset_sql import (
    build_composite_natural_key_expr,
    build_keyset_expr,
)


def test_build_keyset_expr_postgres():
    """Test keyset expression for PostgreSQL."""
    expr = build_keyset_expr("Customer", "ERP", "ACME", "customer_id", "postgres")
    sql = expr.sql(dialect="postgres")

    # Should contain CASE WHEN NULL check
    assert "CASE" in sql.upper()
    assert "WHEN" in sql.upper()
    assert "IS NULL" in sql.upper()
    assert "THEN NULL" in sql.upper()

    # Should contain the prefix with delimiters
    assert "Customer@ERP~ACME|" in sql

    # Should contain nested REPLACE for delimiter escaping
    assert "REPLACE" in sql.upper()
    assert "'@'" in sql or '"@"' in sql
    assert "'@@'" in sql or '"@@"' in sql
    assert "'~'" in sql or '"~"' in sql
    assert "'~~'" in sql or '"~~"' in sql
    assert "'|'" in sql or '"|"' in sql
    assert "'||'" in sql or '"||"' in sql

    # Should reference the natural key column
    assert "customer_id" in sql.lower()


def test_build_keyset_expr_tsql():
    """Test keyset expression for T-SQL."""
    expr = build_keyset_expr("Product", "WMS", "CORP", "sku", "tsql")
    sql = expr.sql(dialect="tsql")

    # Core structure checks
    assert "CASE" in sql.upper()
    assert "IS NULL" in sql.upper()
    assert "Product@WMS~CORP|" in sql

    # Parsing check - should be valid SQL
    parsed = sg.parse_one(sql, dialect="tsql")
    assert parsed is not None


def test_build_keyset_expr_snowflake():
    """Test keyset expression for Snowflake."""
    expr = build_keyset_expr("Order", "OMS", "DEMO", "order_num", "snowflake")
    sql = expr.sql(dialect="snowflake")

    # Core structure checks
    assert "CASE" in sql.upper()
    assert "IS NULL" in sql.upper()
    assert "Order@OMS~DEMO|" in sql

    # Parsing check
    parsed = sg.parse_one(sql, dialect="snowflake")
    assert parsed is not None


def test_build_keyset_expr_escapes_prefix():
    """Test that prefix components are escaped at generation time."""
    # Entity name contains delimiters
    expr = build_keyset_expr("Cust@mer", "ER~P", "A|C", "id", "postgres")
    sql = expr.sql(dialect="postgres")

    # Prefix should have escaped delimiters (doubled)
    # Cust@mer -> Cust@@mer
    # ER~P -> ER~~P
    # A|C -> A||C
    assert "Cust@@mer@ER~~P~A||C|" in sql


def test_build_keyset_expr_parses_back():
    """Test that generated SQL parses back correctly via SQLGlot."""
    expr = build_keyset_expr("Customer", "ERP", "ACME", "customer_id", "postgres")
    sql = expr.sql(dialect="postgres")

    # Should parse without errors
    parsed = sg.parse_one(sql, dialect="postgres")
    assert parsed is not None

    # Re-generate to verify round-trip stability
    regenerated = parsed.sql(dialect="postgres")
    assert regenerated  # Non-empty


def test_build_composite_natural_key_single_column():
    """Test composite key with single column."""
    expr = build_composite_natural_key_expr(["id"], "postgres")
    sql = expr.sql(dialect="postgres")

    # Single column should just return the column name (no CASE/CONCAT)
    assert sql.strip().lower() == "id"


def test_build_composite_natural_key_two_columns():
    """Test composite key with two columns."""
    expr = build_composite_natural_key_expr(["warehouse_id", "sku"], "postgres")
    sql = expr.sql(dialect="postgres")

    # Should have NULL propagation
    assert "CASE" in sql.upper()
    assert "IS NULL" in sql.upper()
    assert "OR" in sql.upper()

    # Should concatenate with ':' separator (CONCAT or || depending on dialect)
    assert "':'" in sql or '":"' in sql

    # Should reference both columns
    assert "warehouse_id" in sql.lower()
    assert "sku" in sql.lower()


def test_build_composite_natural_key_three_columns():
    """Test composite key with three columns."""
    expr = build_composite_natural_key_expr(["a", "b", "c"], "postgres")
    sql = expr.sql(dialect="postgres")

    # NULL check for all three
    assert "CASE" in sql.upper()
    # Should have "a IS NULL OR b IS NULL OR c IS NULL"
    assert sql.upper().count("IS NULL") >= 3

    # All columns referenced
    assert "a" in sql.lower()
    assert "b" in sql.lower()
    assert "c" in sql.lower()


def test_build_composite_natural_key_empty_raises():
    """Test that empty column list raises error."""
    with pytest.raises(ValueError, match="At least one column required"):
        build_composite_natural_key_expr([], "postgres")


def test_build_composite_natural_key_parses():
    """Test that composite key SQL parses correctly."""
    expr = build_composite_natural_key_expr(["col1", "col2"], "postgres")
    sql = expr.sql(dialect="postgres")

    parsed = sg.parse_one(sql, dialect="postgres")
    assert parsed is not None


def test_build_keyset_expr_with_composite_key():
    """Integration test: keyset with composite natural key."""
    # First build the composite natural key
    composite_nk = build_composite_natural_key_expr(["warehouse_id", "sku"], "postgres")
    composite_sql = composite_nk.sql(dialect="postgres")

    # In practice, the composite key would be created as a derived column
    # and then passed to build_keyset_expr as a column name
    # For this test, we verify both pieces work independently

    keyset_expr = build_keyset_expr(
        "Inventory", "WMS", "ACME", "composite_key", "postgres"
    )
    keyset_sql = keyset_expr.sql(dialect="postgres")

    # Both should parse
    assert sg.parse_one(composite_sql, dialect="postgres") is not None
    assert sg.parse_one(keyset_sql, dialect="postgres") is not None

    # Keyset should have the prefix
    assert "Inventory@WMS~ACME|" in keyset_sql


def test_build_keyset_expr_all_dialects():
    """Test keyset generation for all supported dialects."""
    dialects = ["postgres", "tsql", "snowflake"]

    for dialect in dialects:
        expr = build_keyset_expr("Test", "SYS", "TEN", "id", dialect)
        sql = expr.sql(dialect=dialect)

        # Should contain core components
        assert "CASE" in sql.upper()
        assert "IS NULL" in sql.upper()
        assert "Test@SYS~TEN|" in sql

        # Should parse
        parsed = sg.parse_one(sql, dialect=dialect)
        assert parsed is not None, f"Failed to parse for dialect {dialect}"
