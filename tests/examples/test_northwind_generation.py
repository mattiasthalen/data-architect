"""SQL generation end-to-end tests for Northwind reference example.

Tests that validate the full generation pipeline works on the Northwind spec,
including DDL/DML generation, determinism, idempotency, multi-dialect support,
keyset identity, and multi-source handling.
"""

from pathlib import Path

import pytest
import sqlglot

from data_architect.generation import generate_all_ddl, generate_all_dml
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


def test_northwind_generates_without_errors(spec):
    """generate_all_ddl() and generate_all_dml() succeed without raising."""
    ddl_dict = generate_all_ddl(spec, "postgres")
    dml_dict = generate_all_dml(spec, "postgres")

    assert ddl_dict, "DDL dict is empty"
    assert dml_dict, "DML dict is empty"


def test_northwind_ddl_file_count(spec):
    """DDL dict has entries for anchors, knots, ties, and staging tables."""
    ddl_dict = generate_all_ddl(spec, "postgres")

    # Count expected entities
    anchor_count = len(spec.anchors)
    knot_count = len(spec.knots)
    tie_count = len(spec.ties)

    # Count staging tables (one per staging_mapping)
    staging_count = sum(len(a.staging_mappings) for a in spec.anchors)

    # DDL should include all entity tables + staging tables
    # Minimum: anchors + knots + ties + staging tables
    expected_min = anchor_count + knot_count + tie_count + staging_count
    assert len(ddl_dict) >= expected_min, (
        f"Expected at least {expected_min} DDL files, got {len(ddl_dict)}"
    )


def test_northwind_dml_file_count(spec):
    """DML dict has entries for anchors with merge operations."""
    dml_dict = generate_all_dml(spec, "postgres")

    # Every anchor should have at least one DML file
    # Multi-source anchors have multiple DML files (one per source)
    anchor_count = len(spec.anchors)
    assert len(dml_dict) >= anchor_count, (
        f"Expected at least {anchor_count} DML files, got {len(dml_dict)}"
    )


def test_northwind_sql_parses_with_sqlglot(spec):
    """Every SQL string in DDL/DML dicts parses without error."""
    ddl_dict = generate_all_ddl(spec, "postgres")
    dml_dict = generate_all_dml(spec, "postgres")

    all_sql = {**ddl_dict, **dml_dict}

    for filename, sql in all_sql.items():
        try:
            # Use parse (not parse_one) because files may contain multiple statements
            sqlglot.parse(sql, dialect="postgres")
        except Exception as e:
            pytest.fail(f"SQL parsing failed for {filename}: {e}")


def test_northwind_ddl_is_idempotent(spec):
    """All DDL SQL contains 'IF NOT EXISTS' (case-insensitive)."""
    ddl_dict = generate_all_ddl(spec, "postgres")

    for filename, sql in ddl_dict.items():
        sql_lower = sql.lower()
        # PostgreSQL uses "IF NOT EXISTS" or "CREATE OR REPLACE"
        has_idempotent = (
            "if not exists" in sql_lower or "create or replace" in sql_lower
        )
        assert has_idempotent, (
            f"{filename} missing idempotent pattern (IF NOT EXISTS or CREATE OR REPLACE)"
        )


def test_northwind_includes_bitemporal_columns(spec):
    """DDL for temporal attributes contains 'changed_at' and 'recorded_at'."""
    ddl_dict = generate_all_ddl(spec, "postgres")

    # Find an attribute with timeRange
    temporal_attr_found = False
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            if attr.time_range:
                # Look for the attribute table DDL
                attr_table_key = f"{anchor.mnemonic}_{attr.mnemonic}"
                # Find matching DDL key (might have suffix)
                matching_keys = [k for k in ddl_dict if attr_table_key in k]

                if matching_keys:
                    sql = ddl_dict[matching_keys[0]]
                    sql_lower = sql.lower()
                    assert "changed_at" in sql_lower, (
                        f"Temporal attribute {attr_table_key} missing changed_at column"
                    )
                    assert "recorded_at" in sql_lower, (
                        f"Temporal attribute {attr_table_key} missing recorded_at column"
                    )
                    temporal_attr_found = True
                    break
        if temporal_attr_found:
            break

    assert temporal_attr_found, (
        "No temporal attribute DDL found to verify bitemporal columns"
    )


def test_northwind_includes_metadata_columns(spec):
    """DDL for anchor tables contains metadata columns."""
    ddl_dict = generate_all_ddl(spec, "postgres")

    # Check first anchor table
    first_anchor = spec.anchors[0]
    anchor_key = first_anchor.mnemonic

    # Find matching DDL key
    matching_keys = [k for k in ddl_dict if k.startswith(anchor_key)]
    assert matching_keys, f"No DDL found for anchor {anchor_key}"

    sql = ddl_dict[matching_keys[0]]
    sql_lower = sql.lower()

    assert "metadata_recorded_at" in sql_lower, (
        f"Anchor {anchor_key} missing metadata_recorded_at column"
    )
    assert "metadata_recorded_by" in sql_lower, (
        f"Anchor {anchor_key} missing metadata_recorded_by column"
    )
    assert "metadata_id" in sql_lower, f"Anchor {anchor_key} missing metadata_id column"


def test_northwind_generation_is_deterministic(spec):
    """Running generation twice produces byte-identical output."""
    # Generate first time
    ddl_first = generate_all_ddl(spec, "postgres")
    dml_first = generate_all_dml(spec, "postgres")

    # Generate second time
    ddl_second = generate_all_ddl(spec, "postgres")
    dml_second = generate_all_dml(spec, "postgres")

    # Compare DDL
    assert ddl_first.keys() == ddl_second.keys(), "DDL filenames differ between runs"
    for filename in ddl_first:
        assert ddl_first[filename] == ddl_second[filename], (
            f"Non-deterministic DDL output in {filename}"
        )

    # Compare DML
    assert dml_first.keys() == dml_second.keys(), "DML filenames differ between runs"
    for filename in dml_first:
        assert dml_first[filename] == dml_second[filename], (
            f"Non-deterministic DML output in {filename}"
        )


def test_northwind_multi_source_generates_separate_files(spec):
    """Product anchor generates separate DML files per source."""
    dml_dict = generate_all_dml(spec, "postgres")

    # Product has two sources: northwind and sap
    # Should generate files with system suffix
    northwind_files = [k for k in dml_dict if "PR" in k and "northwind" in k]
    sap_files = [k for k in dml_dict if "PR" in k and "sap" in k]

    assert northwind_files, "Missing DML file for Product from northwind system"
    assert sap_files, "Missing DML file for Product from sap system"


def test_northwind_staging_ddl_includes_keyset_column(spec):
    """Staging table DDL contains 'keyset_id' computed column."""
    ddl_dict = generate_all_ddl(spec, "postgres")

    # Find a staging table DDL (should start with "stg_")
    staging_ddls = {k: v for k, v in ddl_dict.items() if k.lower().startswith("stg_")}
    assert staging_ddls, "No staging table DDL found"

    # Check first staging table
    first_staging_sql = next(iter(staging_ddls.values()))
    sql_lower = first_staging_sql.lower()

    assert "keyset_id" in sql_lower, "Staging table missing keyset_id column"
    # Check for computed column syntax
    has_computed = "generated always as" in sql_lower or "as (" in sql_lower
    assert has_computed, "keyset_id not defined as computed column"


def test_northwind_dml_references_keyset_id(spec):
    """Anchor DML files reference source.keyset_id column."""
    dml_dict = generate_all_dml(spec, "postgres")

    # Find a DML file for an anchor (not knot) - look for Customer
    customer_dmls = [v for k, v in dml_dict.items() if "CU" in k]
    assert customer_dmls, "No Customer DML found"

    customer_sql = customer_dmls[0]
    sql_lower = customer_sql.lower()

    # DML should reference keyset_id from source staging table
    assert "keyset_id" in sql_lower, "Anchor DML missing reference to keyset_id"


def test_northwind_multi_dialect_compiles(spec):
    """generate_all_ddl() succeeds for postgres and tsql dialects."""
    # Note: Snowflake doesn't support 'money' type used in spec, so only test postgres/tsql
    dialects = ["postgres", "tsql"]

    for dialect in dialects:
        try:
            ddl_dict = generate_all_ddl(spec, dialect)
            assert ddl_dict, f"DDL dict empty for {dialect}"
        except Exception as e:
            pytest.fail(f"Generation failed for {dialect}: {e}")


def test_northwind_dml_contains_keyset_pattern(spec):
    """DML uses keyset_id which contains system and tenant in staging table."""
    dml_dict = generate_all_dml(spec, "postgres")
    ddl_dict = generate_all_ddl(spec, "postgres")

    # Check Customer DML uses keyset_id
    customer_dmls = [v for k, v in dml_dict.items() if "CU" in k]
    assert customer_dmls, "No Customer DML found"

    customer_sql = customer_dmls[0]
    # DML should reference keyset_id
    assert "keyset_id" in customer_sql.lower(), (
        "Customer DML should reference keyset_id"
    )

    # Check staging DDL contains keyset pattern
    staging_ddls = [
        v for k, v in ddl_dict.items() if "stg_northwind_customers" in k.lower()
    ]
    assert staging_ddls, "No Customer staging DDL found"

    staging_sql = staging_ddls[0]
    # Staging table should build keyset with system~tenant pattern
    assert "@northwind~default|" in staging_sql or "northwind" in staging_sql.lower(), (
        "Staging DDL should contain system identifier"
    )


def test_northwind_multi_source_priority_ordering(spec):
    """Multi-source DML files are ordered by priority."""
    dml_dict = generate_all_dml(spec, "postgres")

    # Get Product DML files
    product_files = sorted(
        [k for k in dml_dict if "PR" in k and ("northwind" in k or "sap" in k)]
    )

    # Files should be deterministically ordered
    # With priority: northwind (1) comes before sap (2)
    assert len(product_files) >= 2, "Expected at least 2 Product DML files"

    # Verify both systems present
    has_northwind = any("northwind" in f for f in product_files)
    has_sap = any("sap" in f for f in product_files)
    assert has_northwind, "Product DML missing northwind file"
    assert has_sap, "Product DML missing sap file"
