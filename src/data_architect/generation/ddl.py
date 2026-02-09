"""DDL AST builder functions for all Anchor Model entity types."""

import sqlglot.expressions as sge

from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.spec import Spec
from data_architect.models.tie import Tie


def build_anchor_table(anchor: Anchor, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for an anchor.

    Args:
        anchor: Anchor model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    raise NotImplementedError


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
    raise NotImplementedError


def build_knot_table(knot: Knot, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for a knot.

    Args:
        knot: Knot model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    raise NotImplementedError


def build_tie_table(tie: Tie, dialect: str) -> sge.Create:
    """Build CREATE TABLE statement for a tie.

    Args:
        tie: Tie model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    raise NotImplementedError


def build_staging_table(
    name: str, columns: list[tuple[str, str]], dialect: str
) -> sge.Create:
    """Build CREATE TABLE statement for a staging table.

    Args:
        name: Table name
        columns: List of (column_name, column_type) tuples
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Create AST node with IF NOT EXISTS
    """
    raise NotImplementedError


def generate_all_ddl(spec: Spec, dialect: str) -> dict[str, str]:
    """Generate all DDL for a spec in deterministic order.

    Args:
        spec: Top-level Spec model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        Dictionary mapping filenames to SQL strings
    """
    raise NotImplementedError
