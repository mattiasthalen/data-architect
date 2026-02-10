"""DDL AST builder functions for all Anchor Model entity types."""

import sqlglot as sg
import sqlglot.expressions as sge

from data_architect.generation.columns import (
    build_bitemporal_columns,
    build_keyset_column,
    build_metadata_columns,
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
from data_architect.models.staging import StagingMapping
from data_architect.models.tie import Tie


def build_anchor_table(anchor: Anchor, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for an anchor.

    Args:
        anchor: Anchor model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    columns = [
        # 1. Identity column (PK)
        sge.ColumnDef(
            this=sg.to_identifier(f"{anchor.mnemonic}_ID"),
            kind=sge.DataType.build(anchor.identity, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.PrimaryKeyColumnConstraint())],
        ),
        # 2. Metadata columns (always present)
        *build_metadata_columns(dialect),
    ]

    table_name = anchor_table_name(anchor)

    return sge.Create(
        kind="TABLE",
        this=sge.Schema(
            this=sge.Table(this=sg.to_identifier(table_name)),
            expressions=columns,
        ),
        exists=True,  # IF NOT EXISTS (idempotent per GEN-04)
    )


def build_attribute_table(
    anchor: Anchor, attribute: Attribute, dialect: str
) -> sge.Create:
    """Build CREATE TABLE statement for an attribute.

    Args:
        anchor: Parent anchor model instance
        attribute: Attribute model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    columns = [
        # 1. Anchor FK column (NOT NULL)
        sge.ColumnDef(
            this=sg.to_identifier(f"{anchor.mnemonic}_ID"),
            kind=sge.DataType.build(anchor.identity, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.NotNullColumnConstraint())],
        ),
    ]

    # 2. Value column (either dataRange or knotRange FK)
    if attribute.data_range:
        # Direct value column
        value_col_name = (
            f"{anchor.mnemonic}_{attribute.mnemonic}_"
            f"{anchor.descriptor}_{attribute.descriptor}"
        )
        columns.append(
            sge.ColumnDef(
                this=sg.to_identifier(value_col_name),
                kind=sge.DataType.build(attribute.data_range, dialect=dialect),
            )
        )
    elif attribute.knot_range:
        # FK to knot
        knot_fk_name = f"{attribute.knot_range}_ID"
        columns.append(
            sge.ColumnDef(
                this=sg.to_identifier(knot_fk_name),
                kind=sge.DataType.build("bigint", dialect=dialect),
            )
        )

    # 3. Bitemporal columns (only if historized)
    if attribute.time_range is not None:
        columns.extend(build_bitemporal_columns(dialect))

    # 4. Metadata columns (always present)
    columns.extend(build_metadata_columns(dialect))

    table_name = attribute_table_name(anchor, attribute)

    return sge.Create(
        kind="TABLE",
        this=sge.Schema(
            this=sge.Table(this=sg.to_identifier(table_name)),
            expressions=columns,
        ),
        exists=True,  # IF NOT EXISTS
    )


def build_knot_table(knot: Knot, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for a knot.

    Args:
        knot: Knot model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    columns = [
        # 1. Identity column (PK)
        sge.ColumnDef(
            this=sg.to_identifier(f"{knot.mnemonic}_ID"),
            kind=sge.DataType.build(knot.identity, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.PrimaryKeyColumnConstraint())],
        ),
        # 2. Value column
        sge.ColumnDef(
            this=sg.to_identifier(f"{knot.mnemonic}_{knot.descriptor}"),
            kind=sge.DataType.build(knot.data_range, dialect=dialect),
        ),
        # 3. Metadata columns (always present, no bitemporal for knots)
        *build_metadata_columns(dialect),
    ]

    table_name = knot_table_name(knot)

    return sge.Create(
        kind="TABLE",
        this=sge.Schema(
            this=sge.Table(this=sg.to_identifier(table_name)),
            expressions=columns,
        ),
        exists=True,  # IF NOT EXISTS
    )


def build_tie_table(tie: Tie, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for a tie.

    Args:
        tie: Tie model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    columns = []

    # 1. Role FK columns (one per role)
    for role in tie.roles:
        role_fk_name = f"{role.type_}_ID_{role.role}"
        columns.append(
            sge.ColumnDef(
                this=sg.to_identifier(role_fk_name),
                kind=sge.DataType.build("bigint", dialect=dialect),
            )
        )

    # 2. Bitemporal columns (only if historized)
    if tie.time_range is not None:
        columns.extend(build_bitemporal_columns(dialect))

    # 3. Metadata columns (always present)
    columns.extend(build_metadata_columns(dialect))

    table_name = tie_table_name(tie)

    return sge.Create(
        kind="TABLE",
        this=sge.Schema(
            this=sge.Table(this=sg.to_identifier(table_name)),
            expressions=columns,
        ),
        exists=True,  # IF NOT EXISTS
    )


def build_staging_table(
    name: str,
    columns: list[tuple[str, str]],
    dialect: str,
    anchor: Anchor | None = None,
    mapping: StagingMapping | None = None,
) -> sge.Create:
    """Build CREATE TABLE statement for a staging table.

    Args:
        name: Table name
        columns: List of (column_name, column_type) tuples
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")
        anchor: Optional anchor model for keyset column generation
        mapping: Optional staging mapping for keyset column generation

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    column_defs = []

    # 1. User-defined columns
    for col_name, col_type in columns:
        column_defs.append(
            sge.ColumnDef(
                this=sg.to_identifier(col_name),
                kind=sge.DataType.build(col_type, dialect=dialect),
            )
        )

    # 2. Keyset computed column (when anchor context available)
    if anchor is not None and mapping is not None:
        column_defs.append(build_keyset_column(anchor, mapping, dialect))

    # 3. Metadata columns (always present)
    column_defs.extend(build_metadata_columns(dialect))

    return sge.Create(
        kind="TABLE",
        this=sge.Schema(
            this=sge.Table(this=sg.to_identifier(name)),
            expressions=column_defs,
        ),
        exists=True,  # IF NOT EXISTS
    )


def generate_all_ddl(spec: Spec, dialect: str) -> dict[str, str]:
    """Generate all DDL for a spec in deterministic order.

    Args:
        spec: Top-level Spec model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        Dictionary mapping filenames to SQL strings
    """
    output: dict[str, str] = {}

    # 1. Knots (sorted by mnemonic for determinism)
    for knot in sorted(spec.knots, key=lambda k: k.mnemonic):
        ast = build_knot_table(knot, dialect)
        filename = f"{knot_table_name(knot)}.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 2. Anchors (sorted by mnemonic)
    for anchor in sorted(spec.anchors, key=lambda a: a.mnemonic):
        # Anchor table
        ast = build_anchor_table(anchor, dialect)
        filename = f"{anchor_table_name(anchor)}.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

        # Attribute tables (sorted by mnemonic)
        for attr in sorted(anchor.attributes, key=lambda at: at.mnemonic):
            ast = build_attribute_table(anchor, attr, dialect)
            filename = f"{attribute_table_name(anchor, attr)}.sql"
            output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 3. Ties (sorted by table name for determinism)
    sorted_ties = sorted(spec.ties, key=lambda t: tie_table_name(t))
    for tie in sorted_ties:
        ast = build_tie_table(tie, dialect)
        filename = f"{tie_table_name(tie)}.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    # 4. Staging tables (GEN-10: from anchor.staging_mappings)
    staging_tables: dict[
        str, tuple[str, Anchor, StagingMapping, list[tuple[str, str]]]
    ] = {}

    for anchor in spec.anchors:
        if anchor.staging_mappings:
            for mapping in anchor.staging_mappings:
                table = staging_table_name(mapping)
                # Extract columns from mapping model
                columns = [(col.name, col.type) for col in mapping.columns]
                staging_tables[table] = (table, anchor, mapping, columns)

    # Generate staging DDL in sorted order
    for table in sorted(staging_tables.keys()):
        name, anchor_ref, mapping_ref, columns = staging_tables[table]
        ast = build_staging_table(
            name, columns, dialect, anchor=anchor_ref, mapping=mapping_ref
        )
        filename = f"{name}.sql"
        output[filename] = ast.sql(dialect=dialect, pretty=True)

    return output
