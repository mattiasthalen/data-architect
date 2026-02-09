"""Keyset identity SQL expression builders.

Functions to construct NULL-safe keyset identity expressions in SQL
using the format: entity@system~tenant|natural_key

For composite natural keys, uses ':' separator between components.
"""

import sqlglot as sg
import sqlglot.expressions as sge

from data_architect.identity.escaping import escape_delimiters


def build_keyset_expr(
    entity: str,
    system: str,
    tenant: str,
    natural_key_col: str,
    dialect: str,  # noqa: ARG001
) -> sge.Expression:
    """Build NULL-safe keyset identity construction SQL expression.

    Generates a CASE WHEN ... IS NULL THEN NULL ELSE CONCAT(...) END expression
    that constructs keyset identity from components.

    The prefix (entity@system~tenant|) is escaped at generation time.
    The natural_key_col is escaped at runtime using nested REPLACE.

    Args:
        entity: Entity/anchor descriptor (escaped at generation time)
        system: Source system identifier (escaped at generation time)
        tenant: Tenant identifier (escaped at generation time)
        natural_key_col: Column name containing the natural key value
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Expression representing NULL-safe keyset construction

    Example:
        >>> expr = build_keyset_expr(
        ...     "Customer", "ERP", "ACME", "customer_id", "postgres"
        ... )
        >>> expr.sql(dialect="postgres")
        "CASE WHEN customer_id IS NULL THEN NULL ELSE ..."
    """
    # Escape the constant prefix components at generation time
    esc_entity = escape_delimiters(entity)
    esc_system = escape_delimiters(system)
    esc_tenant = escape_delimiters(tenant)

    # Build prefix literal: entity@system~tenant|
    prefix = f"{esc_entity}@{esc_system}~{esc_tenant}|"

    # Build nested REPLACE for runtime natural key escaping
    # REPLACE(REPLACE(REPLACE(nk_col, '@', '@@'), '~', '~~'), '|', '||')
    nk_col_expr = sg.to_identifier(natural_key_col)

    # Innermost: REPLACE(nk_col, '@', '@@')
    escaped_nk = sge.Replace(
        this=nk_col_expr,
        expression=sge.Literal.string("@"),
        replacement=sge.Literal.string("@@"),
    )

    # Middle: REPLACE(..., '~', '~~')
    escaped_nk = sge.Replace(
        this=escaped_nk,
        expression=sge.Literal.string("~"),
        replacement=sge.Literal.string("~~"),
    )

    # Outermost: REPLACE(..., '|', '||')
    escaped_nk = sge.Replace(
        this=escaped_nk,
        expression=sge.Literal.string("|"),
        replacement=sge.Literal.string("||"),
    )

    # Build CONCAT(prefix_literal, escaped_nk)
    concat_expr = sge.Concat(
        expressions=[
            sge.Literal.string(prefix),
            escaped_nk,
        ]
    )

    # Wrap in CASE WHEN nk_col IS NULL THEN NULL ELSE concat_expr END
    case_expr = sge.Case(
        ifs=[
            sge.If(
                this=sge.Is(this=nk_col_expr, expression=sge.Null()),
                true=sge.Null(),
            )
        ],
        default=concat_expr,
    )

    return case_expr


def build_composite_natural_key_expr(
    columns: list[str],
    dialect: str,  # noqa: ARG001
) -> sge.Expression:
    """Build composite natural key expression from multiple columns.

    Concatenates columns with ':' separator and propagates NULL if any
    component is NULL.

    Args:
        columns: List of column names to concatenate
        dialect: Target SQL dialect (e.g., "postgres", "snowflake", "tsql")

    Returns:
        SQLGlot Expression for composite natural key with NULL propagation

    Example:
        >>> expr = build_composite_natural_key_expr(
        ...     ["col1", "col2"], "postgres"
        ... )
        >>> expr.sql(dialect="postgres")
        "CASE WHEN col1 IS NULL OR ... ELSE ... END"
    """
    if not columns:
        msg = "At least one column required for composite natural key"
        raise ValueError(msg)

    if len(columns) == 1:
        # Single column - just return the column identifier
        return sg.to_identifier(columns[0])

    # Build NULL check: col1 IS NULL OR col2 IS NULL OR ...
    null_checks = [
        sge.Is(this=sg.to_identifier(col), expression=sge.Null()) for col in columns
    ]
    any_null: sge.Expression = null_checks[0]
    for check in null_checks[1:]:
        any_null = sge.Or(this=any_null, expression=check)

    # Build CONCAT with ':' separators
    # CONCAT(col1, ':', col2, ':', col3)
    concat_parts: list[sge.Expression] = []
    for i, col in enumerate(columns):
        concat_parts.append(sg.to_identifier(col))
        if i < len(columns) - 1:  # Add separator between columns (not after last)
            concat_parts.append(sge.Literal.string(":"))

    concat_expr = sge.Concat(expressions=concat_parts)

    # Wrap in CASE WHEN any_null THEN NULL ELSE concat_expr END
    case_expr = sge.Case(
        ifs=[sge.If(this=any_null, true=sge.Null())],
        default=concat_expr,
    )

    return case_expr
