"""DML AST builder functions for MERGE/UPSERT loading patterns."""

# ruff: noqa: S608  # SQL strings are parsed by SQLGlot, not executed directly

import sqlglot as sg
import sqlglot.expressions as sge

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
from data_architect.models.tie import Tie


def build_anchor_merge(anchor: Anchor, dialect: str) -> sge.Expression:
    """Build MERGE/UPSERT statement for anchor loading.

    Args:
        anchor: Anchor model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = anchor_table_name(anchor)
    identity_col = f"{anchor.mnemonic}_ID"

    # Get staging table name (use first mapping if exists, else derive default)
    if anchor.staging_mappings:
        source_table = staging_table_name(anchor.staging_mappings[0])
    else:
        source_table = f"stg_{target_table}"

    # For PostgreSQL: Use INSERT...ON CONFLICT DO NOTHING
    # Anchors are identity-only, so no updates needed
    if dialect == "postgres":
        sql = f"""
INSERT INTO {target_table} (
    {identity_col},
    metadata_recorded_at,
    metadata_recorded_by,
    metadata_id
)
SELECT
    {identity_col},
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    'architect-generated' AS metadata_id
FROM {source_table}
ON CONFLICT ({identity_col}) DO NOTHING
"""
    else:
        # For SQL Server / Snowflake: Use MERGE with WHEN NOT MATCHED
        sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON target.{identity_col} = source.{identity_col}
WHEN NOT MATCHED THEN
    INSERT (
        {identity_col},
        metadata_recorded_at,
        metadata_recorded_by,
        metadata_id
    )
    VALUES (
        source.{identity_col},
        CURRENT_TIMESTAMP,
        'architect',
        'architect-generated'
    )
"""

    return sg.parse_one(sql, dialect=dialect)


def build_attribute_merge(
    anchor: Anchor, attribute: Attribute, dialect: str
) -> sge.Expression:
    """Build MERGE/UPSERT statement for attribute loading.

    Args:
        anchor: Parent anchor model instance
        attribute: Attribute model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = attribute_table_name(anchor, attribute)
    anchor_fk = f"{anchor.mnemonic}_ID"

    # Get staging table name
    if anchor.staging_mappings:
        source_table = staging_table_name(anchor.staging_mappings[0])
    else:
        source_table = f"stg_{anchor_table_name(anchor)}"

    # Determine value column name
    if attribute.data_range:
        value_col = (
            f"{anchor.mnemonic}_{attribute.mnemonic}_"
            f"{anchor.descriptor}_{attribute.descriptor}"
        )
    else:  # knot_range
        value_col = f"{attribute.knot_range}_ID"

    # Check if historized (has time_range)
    if attribute.time_range:
        # Historized: Append-only SCD2 pattern
        # In Anchor Modeling, we never update old rows, we just insert new ones
        if dialect == "postgres":
            sql = f"""
INSERT INTO {target_table} (
    {anchor_fk},
    {value_col},
    changed_at,
    recorded_at,
    metadata_recorded_at,
    metadata_recorded_by,
    metadata_id
)
SELECT
    {anchor_fk},
    {value_col},
    changed_at,
    CURRENT_TIMESTAMP AS recorded_at,
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    'architect-generated' AS metadata_id
FROM {source_table}
ON CONFLICT ({anchor_fk}, changed_at) DO NOTHING
"""
        else:
            sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON target.{anchor_fk} = source.{anchor_fk}
   AND target.changed_at = source.changed_at
WHEN NOT MATCHED THEN
    INSERT (
        {anchor_fk},
        {value_col},
        changed_at,
        recorded_at,
        metadata_recorded_at,
        metadata_recorded_by,
        metadata_id
    )
    VALUES (
        source.{anchor_fk},
        source.{value_col},
        source.changed_at,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP,
        'architect',
        'architect-generated'
    )
"""
    else:
        # Static: Simple UPSERT
        if dialect == "postgres":
            sql = f"""
INSERT INTO {target_table} (
    {anchor_fk},
    {value_col},
    metadata_recorded_at,
    metadata_recorded_by,
    metadata_id
)
SELECT
    {anchor_fk},
    {value_col},
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    'architect-generated' AS metadata_id
FROM {source_table}
ON CONFLICT ({anchor_fk}) DO UPDATE SET
    {value_col} = EXCLUDED.{value_col},
    metadata_recorded_at = CURRENT_TIMESTAMP,
    metadata_recorded_by = 'architect',
    metadata_id = 'architect-generated'
"""
        else:
            sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON target.{anchor_fk} = source.{anchor_fk}
WHEN MATCHED THEN
    UPDATE SET
        {value_col} = source.{value_col},
        metadata_recorded_at = CURRENT_TIMESTAMP,
        metadata_recorded_by = 'architect',
        metadata_id = 'architect-generated'
WHEN NOT MATCHED THEN
    INSERT (
        {anchor_fk},
        {value_col},
        metadata_recorded_at,
        metadata_recorded_by,
        metadata_id
    )
    VALUES (
        source.{anchor_fk},
        source.{value_col},
        CURRENT_TIMESTAMP,
        'architect',
        'architect-generated'
    )
"""

    return sg.parse_one(sql, dialect=dialect)


def build_knot_merge(knot: Knot, dialect: str) -> sge.Expression:
    """Build MERGE/UPSERT statement for knot loading.

    Args:
        knot: Knot model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = knot_table_name(knot)
    identity_col = f"{knot.mnemonic}_ID"
    value_col = f"{knot.mnemonic}_{knot.descriptor}"

    # Knots typically have their own staging tables
    source_table = f"stg_{target_table}"

    # Knots are static reference data - INSERT-ignore pattern
    if dialect == "postgres":
        sql = f"""
INSERT INTO {target_table} (
    {identity_col},
    {value_col},
    metadata_recorded_at,
    metadata_recorded_by,
    metadata_id
)
SELECT
    {identity_col},
    {value_col},
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    'architect-generated' AS metadata_id
FROM {source_table}
ON CONFLICT ({identity_col}) DO NOTHING
"""
    else:
        sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON target.{identity_col} = source.{identity_col}
WHEN NOT MATCHED THEN
    INSERT (
        {identity_col},
        {value_col},
        metadata_recorded_at,
        metadata_recorded_by,
        metadata_id
    )
    VALUES (
        source.{identity_col},
        source.{value_col},
        CURRENT_TIMESTAMP,
        'architect',
        'architect-generated'
    )
"""

    return sg.parse_one(sql, dialect=dialect)


def build_tie_merge(tie: Tie, dialect: str) -> sge.Expression:
    """Build MERGE/UPSERT statement for tie loading.

    Args:
        tie: Tie model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = tie_table_name(tie)
    source_table = f"stg_{target_table}"

    # Build role FK columns
    role_columns = [f"{role.type_}_ID_{role.role}" for role in tie.roles]

    # Build ON clause for matching (all role FKs)
    if dialect == "postgres":
        " AND ".join([f"{col} = EXCLUDED.{col}" for col in role_columns])
    else:
        " AND ".join([f"target.{col} = source.{col}" for col in role_columns])

    if tie.time_range:
        # Historized tie: Append-only pattern with bitemporal columns
        if dialect == "postgres":
            columns_list = ", ".join(
                [
                    *role_columns,
                    "changed_at",
                    "recorded_at",
                    "metadata_recorded_at",
                    "metadata_recorded_by",
                    "metadata_id",
                ]
            )
            select_list = ", ".join(
                [
                    *role_columns,
                    "changed_at",
                    "CURRENT_TIMESTAMP AS recorded_at",
                    "CURRENT_TIMESTAMP AS metadata_recorded_at",
                    "'architect' AS metadata_recorded_by",
                    "'architect-generated' AS metadata_id",
                ]
            )
            conflict_cols = ", ".join([*role_columns, "changed_at"])

            sql = f"""
INSERT INTO {target_table} (
    {columns_list}
)
SELECT
    {select_list}
FROM {source_table}
ON CONFLICT ({conflict_cols}) DO NOTHING
"""
        else:
            role_match = " AND ".join(
                [f"target.{col} = source.{col}" for col in role_columns]
            )
            insert_cols = ", ".join(
                [
                    *role_columns,
                    "changed_at",
                    "recorded_at",
                    "metadata_recorded_at",
                    "metadata_recorded_by",
                    "metadata_id",
                ]
            )
            insert_vals = ", ".join(
                [f"source.{col}" for col in role_columns]
                + [
                    "source.changed_at",
                    "CURRENT_TIMESTAMP",
                    "CURRENT_TIMESTAMP",
                    "'architect'",
                    "'architect-generated'",
                ]
            )

            sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON {role_match}
   AND target.changed_at = source.changed_at
WHEN NOT MATCHED THEN
    INSERT (
        {insert_cols}
    )
    VALUES (
        {insert_vals}
    )
"""
    else:
        # Static tie: INSERT-ignore pattern (relationship exists or doesn't)
        if dialect == "postgres":
            columns_list = ", ".join(
                [
                    *role_columns,
                    "metadata_recorded_at",
                    "metadata_recorded_by",
                    "metadata_id",
                ]
            )
            select_list = ", ".join(
                [
                    *role_columns,
                    "CURRENT_TIMESTAMP AS metadata_recorded_at",
                    "'architect' AS metadata_recorded_by",
                    "'architect-generated' AS metadata_id",
                ]
            )
            conflict_cols = ", ".join(role_columns)

            sql = f"""
INSERT INTO {target_table} (
    {columns_list}
)
SELECT
    {select_list}
FROM {source_table}
ON CONFLICT ({conflict_cols}) DO NOTHING
"""
        else:
            role_match = " AND ".join(
                [f"target.{col} = source.{col}" for col in role_columns]
            )
            insert_cols = ", ".join(
                [
                    *role_columns,
                    "metadata_recorded_at",
                    "metadata_recorded_by",
                    "metadata_id",
                ]
            )
            insert_vals = ", ".join(
                [f"source.{col}" for col in role_columns]
                + ["CURRENT_TIMESTAMP", "'architect'", "'architect-generated'"]
            )

            sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON {role_match}
WHEN NOT MATCHED THEN
    INSERT (
        {insert_cols}
    )
    VALUES (
        {insert_vals}
    )
"""

    return sg.parse_one(sql, dialect=dialect)


def generate_all_dml(spec: Spec, dialect: str) -> dict[str, str]:
    """Generate all DML for a spec in deterministic order.

    Args:
        spec: Top-level Spec model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        Dictionary mapping filenames to SQL strings
    """
    output: dict[str, str] = {}

    # 1. Knots (sorted by mnemonic for determinism)
    for knot in sorted(spec.knots, key=lambda k: k.mnemonic):
        ast = build_knot_merge(knot, dialect)
        filename = f"{knot_table_name(knot)}_load.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 2. Anchors (sorted by mnemonic)
    for anchor in sorted(spec.anchors, key=lambda a: a.mnemonic):
        # Anchor table load
        ast = build_anchor_merge(anchor, dialect)
        filename = f"{anchor_table_name(anchor)}_load.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

        # Attribute table loads (sorted by mnemonic)
        for attr in sorted(anchor.attributes, key=lambda at: at.mnemonic):
            ast = build_attribute_merge(anchor, attr, dialect)
            filename = f"{attribute_table_name(anchor, attr)}_load.sql"
            output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 3. Ties (sorted by table name for determinism)
    sorted_ties = sorted(spec.ties, key=lambda t: tie_table_name(t))
    for tie in sorted_ties:
        ast = build_tie_merge(tie, dialect)
        filename = f"{tie_table_name(tie)}_load.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    return output
