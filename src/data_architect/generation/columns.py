"""Reusable column builder functions for bitemporal and metadata columns."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlglot as sg
import sqlglot.expressions as sge

from data_architect.generation.keyset_sql import (
    build_composite_natural_key_expr,
    build_keyset_expr,
)
from data_architect.identity.escaping import escape_delimiters

if TYPE_CHECKING:
    from data_architect.models.anchor import Anchor
    from data_architect.models.staging import StagingMapping


def build_bitemporal_columns(dialect: str) -> list[sge.ColumnDef]:
    """Build changed_at and recorded_at columns (valid time + transaction time).

    Args:
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        List of two ColumnDef nodes for changed_at and recorded_at
    """
    # Use TIMESTAMPTZ for postgres/tsql, TIMESTAMP_NTZ for snowflake
    timestamp_type = "TIMESTAMPTZ" if dialect != "snowflake" else "TIMESTAMP_NTZ"

    return [
        sge.ColumnDef(
            this=sg.to_identifier("changed_at"),
            kind=sge.DataType.build(timestamp_type, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.NotNullColumnConstraint())],
        ),
        sge.ColumnDef(
            this=sg.to_identifier("recorded_at"),
            kind=sge.DataType.build(timestamp_type, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.NotNullColumnConstraint())],
        ),
    ]


def build_metadata_columns(dialect: str) -> list[sge.ColumnDef]:
    """Build metadata columns per GEN-07.

    Args:
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        List of three ColumnDef nodes for metadata_recorded_at,
        metadata_recorded_by, metadata_id
    """
    # metadata_recorded_at is NOT NULL, others are nullable
    timestamp_type = "TIMESTAMPTZ" if dialect != "snowflake" else "TIMESTAMP_NTZ"

    return [
        sge.ColumnDef(
            this=sg.to_identifier("metadata_recorded_at"),
            kind=sge.DataType.build(timestamp_type, dialect=dialect),
            constraints=[sge.ColumnConstraint(kind=sge.NotNullColumnConstraint())],
        ),
        sge.ColumnDef(
            this=sg.to_identifier("metadata_recorded_by"),
            kind=sge.DataType.build("VARCHAR(255)", dialect=dialect),
        ),
        sge.ColumnDef(
            this=sg.to_identifier("metadata_id"),
            kind=sge.DataType.build("VARCHAR(255)", dialect=dialect),
        ),
    ]


def build_keyset_column(
    anchor: Anchor, mapping: StagingMapping, dialect: str
) -> sge.ColumnDef:
    """Build keyset_id computed column for staging table.

    Generates a GENERATED ALWAYS AS ... STORED (or AS ... PERSISTED for tsql)
    column that materializes the keyset identity expression.

    For single natural key:
        keyset_id = entity@system~tenant|natural_key_value
        (with NULL propagation)

    For composite natural keys:
        keyset_id = entity@system~tenant|key1:key2:key3
        (with NULL propagation if any component is NULL)

    Args:
        anchor: Anchor model instance (for entity descriptor)
        mapping: StagingMapping model instance (for system, tenant, natural key)
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        ColumnDef node with ComputedColumnConstraint containing keyset expression
    """
    # Determine if single or composite natural key
    if len(mapping.natural_key_columns) == 1:
        # Single natural key: use build_keyset_expr directly
        keyset_expr = build_keyset_expr(
            entity=anchor.descriptor,
            system=mapping.system,
            tenant=mapping.tenant,
            natural_key_col=mapping.natural_key_columns[0],
            dialect=dialect,
        )
    else:
        # Composite natural key: build composite key expr, then wrap in keyset
        # Build the composite natural key expression first
        composite_nk_expr = build_composite_natural_key_expr(
            mapping.natural_key_columns, dialect
        )

        # Build the keyset prefix: entity@system~tenant|
        esc_entity = escape_delimiters(anchor.descriptor)
        esc_system = escape_delimiters(mapping.system)
        esc_tenant = escape_delimiters(mapping.tenant)
        prefix = f"{esc_entity}@{esc_system}~{esc_tenant}|"

        # The composite expression already handles NULL propagation and concatenation
        # with ':' separators, but we need to escape the result and prepend the prefix.

        # Build nested REPLACE on the composite expression to escape delimiters
        # REPLACE(REPLACE(REPLACE(composite_nk_expr, '@', '@@'), '~', '~~'), '|', '||')
        escaped_composite = sge.Replace(
            this=composite_nk_expr,
            expression=sge.Literal.string("@"),
            replacement=sge.Literal.string("@@"),
        )
        escaped_composite = sge.Replace(
            this=escaped_composite,
            expression=sge.Literal.string("~"),
            replacement=sge.Literal.string("~~"),
        )
        escaped_composite = sge.Replace(
            this=escaped_composite,
            expression=sge.Literal.string("|"),
            replacement=sge.Literal.string("||"),
        )

        # Build CONCAT(prefix, escaped_composite)
        concat_expr = sge.Concat(
            expressions=[
                sge.Literal.string(prefix),
                escaped_composite,
            ]
        )

        # The composite expression already includes CASE WHEN ... IS NULL logic,
        # so we need to preserve that. The composite_nk_expr is already a CASE
        # expression, so when it evaluates to NULL, the entire result should be NULL.
        # We need to wrap our CONCAT in a CASE that checks if composite is NULL.

        # Build NULL check for composite key (any column NULL)
        null_checks = [
            sge.Is(this=sg.to_identifier(col), expression=sge.Null())
            for col in mapping.natural_key_columns
        ]
        any_null: sge.Expression = null_checks[0]
        for check in null_checks[1:]:
            any_null = sge.Or(this=any_null, expression=check)

        # Wrap in CASE WHEN any_null THEN NULL ELSE concat_expr END
        keyset_expr = sge.Case(
            ifs=[sge.If(this=any_null, true=sge.Null())],
            default=concat_expr,
        )

    # Build the ColumnDef with ComputedColumnConstraint
    return sge.ColumnDef(
        this=sg.to_identifier("keyset_id"),
        kind=sge.DataType.build("VARCHAR(500)", dialect=dialect),
        constraints=[
            sge.ColumnConstraint(
                kind=sge.ComputedColumnConstraint(this=keyset_expr, persisted=True)
            )
        ],
    )
