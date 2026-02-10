"""DML AST builder functions for MERGE/UPSERT loading patterns."""

# ruff: noqa: S608  # SQL strings are parsed by SQLGlot, not executed directly

import sqlglot as sg
import sqlglot.expressions as sge

from data_architect.generation.conflict import resolve_staging_order
from data_architect.generation.keyset_sql import (
    build_composite_natural_key_expr,
    build_keyset_expr,
)
from data_architect.generation.naming import (
    anchor_table_name,
    attribute_table_name,
    knot_table_name,
    staging_table_name,
    tie_table_name,
)
from data_architect.identity.escaping import escape_delimiters
from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.spec import Spec
from data_architect.models.staging import StagingMapping
from data_architect.models.tie import Tie


def _build_metadata_id_expr(
    anchor: Anchor, mapping: StagingMapping | None, dialect: str
) -> str:
    """Build metadata_id expression: keyset or fallback.

    When a staging mapping is provided, constructs a keyset identity
    expression using build_keyset_expr() with the mapping's system,
    tenant, and natural key columns. For composite natural keys
    (multiple columns), uses build_composite_natural_key_expr() to
    concatenate with ':' separator and NULL propagation.

    When no mapping is provided, returns the literal
    'architect-generated' for backward compatibility.

    Args:
        anchor: Anchor model instance
        mapping: Optional staging mapping with natural key configuration
        dialect: Target SQL dialect (e.g., "postgres", "snowflake")

    Returns:
        SQL expression string for embedding in f-string SQL templates.
    """
    if mapping is None:
        return "'architect-generated'"

    # For single-column natural key, use build_keyset_expr directly
    if len(mapping.natural_key_columns) == 1:
        keyset_expr = build_keyset_expr(
            anchor.descriptor,
            mapping.system,
            mapping.tenant,
            mapping.natural_key_columns[0],
            dialect,
        )
        return keyset_expr.sql(dialect=dialect)

    # For composite natural keys, build manually
    # Build composite natural key expression
    composite_nk_expr = build_composite_natural_key_expr(
        mapping.natural_key_columns, dialect
    )
    composite_nk_sql = composite_nk_expr.sql(dialect=dialect)

    # Escape the constant prefix components at generation time
    esc_entity = escape_delimiters(anchor.descriptor)
    esc_system = escape_delimiters(mapping.system)
    esc_tenant = escape_delimiters(mapping.tenant)

    # Build prefix literal: entity@system~tenant|
    prefix = f"{esc_entity}@{esc_system}~{esc_tenant}|"

    # Build keyset SQL with composite key
    # Composite expression handles NULL propagation
    # Runtime escaping for natural key delimiters
    replace_expr = (
        f"REPLACE(REPLACE(REPLACE("
        f"CAST(({composite_nk_sql}) AS VARCHAR), "
        f"'@', '@@'), '~', '~~'), '|', '||')"
    )
    keyset_sql = f"""CASE
    WHEN {composite_nk_sql} IS NULL THEN NULL
    ELSE CONCAT('{prefix}', {replace_expr})
END"""

    return keyset_sql


def build_anchor_merge(
    anchor: Anchor, dialect: str, mapping: StagingMapping | None = None
) -> sge.Expression:
    """Build MERGE/UPSERT statement for anchor loading.

    Args:
        anchor: Anchor model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")
        mapping: Optional specific staging mapping. If None, uses first
            mapping or default.

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = anchor_table_name(anchor)
    identity_col = f"{anchor.mnemonic}_ID"

    # Get staging table name from mapping parameter, first mapping, or default
    if mapping is not None:
        source_table = staging_table_name(mapping)
    elif anchor.staging_mappings:
        source_table = staging_table_name(anchor.staging_mappings[0])
    else:
        source_table = f"stg_{target_table}"

    # Build metadata_id expression (keyset if mapping provided, else fallback)
    metadata_id_sql = _build_metadata_id_expr(anchor, mapping, dialect)

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
    {metadata_id_sql} AS metadata_id
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
        {metadata_id_sql}
    )
"""

    return sg.parse_one(sql, dialect=dialect)


def build_attribute_merge(
    anchor: Anchor,
    attribute: Attribute,
    dialect: str,
    mapping: StagingMapping | None = None,
) -> sge.Expression:
    """Build MERGE/UPSERT statement for attribute loading.

    Args:
        anchor: Parent anchor model instance
        attribute: Attribute model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")
        mapping: Optional specific staging mapping. If None, uses first
            mapping or default.

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT
    """
    target_table = attribute_table_name(anchor, attribute)
    anchor_fk = f"{anchor.mnemonic}_ID"

    # Get staging table name from mapping parameter, first mapping, or default
    if mapping is not None:
        source_table = staging_table_name(mapping)
    elif anchor.staging_mappings:
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

    # Determine staging source column name
    # Use column_mappings if available, otherwise default to value_col
    if (
        mapping
        and mapping.column_mappings
        and attribute.mnemonic in mapping.column_mappings
    ):
        staging_value_col = mapping.column_mappings[attribute.mnemonic]
    else:
        staging_value_col = value_col  # Default: same name as target

    # Build metadata_id expression (keyset if mapping provided, else fallback)
    metadata_id_sql = _build_metadata_id_expr(anchor, mapping, dialect)

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
    {staging_value_col} AS {value_col},
    changed_at,
    CURRENT_TIMESTAMP AS recorded_at,
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    {metadata_id_sql} AS metadata_id
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
        source.{staging_value_col},
        source.changed_at,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP,
        'architect',
        {metadata_id_sql}
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
    {staging_value_col} AS {value_col},
    CURRENT_TIMESTAMP AS metadata_recorded_at,
    'architect' AS metadata_recorded_by,
    {metadata_id_sql} AS metadata_id
FROM {source_table}
ON CONFLICT ({anchor_fk}) DO UPDATE SET
    {value_col} = EXCLUDED.{value_col},
    metadata_recorded_at = CURRENT_TIMESTAMP,
    metadata_recorded_by = 'architect',
    metadata_id = {metadata_id_sql}
"""
        else:
            sql = f"""
MERGE INTO {target_table} AS target
USING {source_table} AS source
ON target.{anchor_fk} = source.{anchor_fk}
WHEN MATCHED THEN
    UPDATE SET
        {value_col} = source.{staging_value_col},
        metadata_recorded_at = CURRENT_TIMESTAMP,
        metadata_recorded_by = 'architect',
        metadata_id = {metadata_id_sql}
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
        source.{staging_value_col},
        CURRENT_TIMESTAMP,
        'architect',
        {metadata_id_sql}
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
        # Handle multi-source anchors (STG-05)
        if anchor.staging_mappings and len(anchor.staging_mappings) > 1:
            # Multi-source: Generate one MERGE per source in priority order
            sorted_mappings = resolve_staging_order(anchor.staging_mappings)
            for mapping in sorted_mappings:
                # Anchor load for this source
                ast = build_anchor_merge(anchor, dialect, mapping)
                system_suffix = mapping.system.lower()
                filename = f"{anchor_table_name(anchor)}_load_{system_suffix}.sql"
                output[filename] = ast.sql(dialect=dialect, pretty=True)

                # Attribute loads for this source (sorted by mnemonic)
                for attr in sorted(anchor.attributes, key=lambda at: at.mnemonic):
                    ast = build_attribute_merge(anchor, attr, dialect, mapping)
                    attr_table = attribute_table_name(anchor, attr)
                    filename = f"{attr_table}_load_{system_suffix}.sql"
                    output[filename] = ast.sql(dialect=dialect, pretty=True)
        else:
            # Single-source (0 or 1 mapping): Original behavior
            single_mapping = (
                anchor.staging_mappings[0] if anchor.staging_mappings else None
            )
            ast = build_anchor_merge(anchor, dialect, single_mapping)
            filename = f"{anchor_table_name(anchor)}_load.sql"
            output[filename] = ast.sql(dialect=dialect, pretty=True)

            # Attribute table loads (sorted by mnemonic)
            for attr in sorted(anchor.attributes, key=lambda at: at.mnemonic):
                ast = build_attribute_merge(anchor, attr, dialect, single_mapping)
                filename = f"{attribute_table_name(anchor, attr)}_load.sql"
                output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 3. Ties (sorted by table name for determinism)
    sorted_ties = sorted(spec.ties, key=lambda t: tie_table_name(t))
    for tie in sorted_ties:
        ast = build_tie_merge(tie, dialect)
        filename = f"{tie_table_name(tie)}_load.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    return output
