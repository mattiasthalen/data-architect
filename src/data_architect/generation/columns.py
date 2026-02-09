"""Reusable column builder functions for bitemporal and metadata columns."""

import sqlglot.expressions as sge


def build_bitemporal_columns(dialect: str) -> list[sge.ColumnDef]:
    """Build changed_at and recorded_at columns (valid time + transaction time).

    Args:
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        List of two ColumnDef nodes for changed_at and recorded_at
    """
    raise NotImplementedError


def build_metadata_columns(dialect: str) -> list[sge.ColumnDef]:
    """Build metadata columns per GEN-07.

    Args:
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        List of three ColumnDef nodes for metadata_recorded_at,
        metadata_recorded_by, metadata_id
    """
    raise NotImplementedError
