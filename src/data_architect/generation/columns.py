"""Reusable column builder functions for bitemporal and metadata columns."""

import sqlglot as sg
import sqlglot.expressions as sge


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
