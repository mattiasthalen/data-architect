"""DML AST builder functions for MERGE/UPSERT loading patterns."""

import sqlglot.expressions as sge

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

    Raises:
        NotImplementedError: Not yet implemented
    """
    raise NotImplementedError


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

    Raises:
        NotImplementedError: Not yet implemented
    """
    raise NotImplementedError


def build_knot_merge(knot: Knot, dialect: str) -> sge.Expression:
    """Build MERGE/UPSERT statement for knot loading.

    Args:
        knot: Knot model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT

    Raises:
        NotImplementedError: Not yet implemented
    """
    raise NotImplementedError


def build_tie_merge(tie: Tie, dialect: str) -> sge.Expression:
    """Build MERGE/UPSERT statement for tie loading.

    Args:
        tie: Tie model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot AST node for MERGE or INSERT...ON CONFLICT

    Raises:
        NotImplementedError: Not yet implemented
    """
    raise NotImplementedError


def generate_all_dml(spec: Spec, dialect: str) -> dict[str, str]:
    """Generate all DML for a spec in deterministic order.

    Args:
        spec: Top-level Spec model instance
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        Dictionary mapping filenames to SQL strings

    Raises:
        NotImplementedError: Not yet implemented
    """
    raise NotImplementedError
