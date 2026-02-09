"""Deterministic naming conventions for tables and files."""

from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.staging import StagingMapping
from data_architect.models.tie import Tie


def anchor_table_name(anchor: Anchor) -> str:
    """Generate anchor table name.

    Args:
        anchor: Anchor model instance

    Returns:
        Table name in format: {mnemonic}_{descriptor}
    """
    return f"{anchor.mnemonic}_{anchor.descriptor}"


def attribute_table_name(anchor: Anchor, attribute: Attribute) -> str:
    """Generate attribute table name.

    Args:
        anchor: Parent anchor model instance
        attribute: Attribute model instance

    Returns:
        Table name in format:
        {anchor_mnemonic}_{attr_mnemonic}_{anchor_descriptor}_{attr_descriptor}
    """
    return (
        f"{anchor.mnemonic}_{attribute.mnemonic}_"
        f"{anchor.descriptor}_{attribute.descriptor}"
    )


def knot_table_name(knot: Knot) -> str:
    """Generate knot table name.

    Args:
        knot: Knot model instance

    Returns:
        Table name in format: {mnemonic}_{descriptor}
    """
    return f"{knot.mnemonic}_{knot.descriptor}"


def tie_table_name(tie: Tie) -> str:
    """Generate tie table name based on sorted roles.

    Args:
        tie: Tie model instance

    Returns:
        Table name composed from sorted role types and names
    """
    # Sort roles by (type_, role) for determinism
    sorted_roles = sorted(tie.roles, key=lambda r: (r.type_, r.role))

    # Build name from sorted roles: type1_type2_role1_role2
    types = "_".join(r.type_ for r in sorted_roles)
    roles = "_".join(r.role for r in sorted_roles)

    return f"{types}_{roles}"


def staging_table_name(mapping: StagingMapping) -> str:
    """Extract staging table name from mapping definition.

    Args:
        mapping: Staging mapping model instance

    Returns:
        Table name from mapping.table
    """
    return mapping.table
