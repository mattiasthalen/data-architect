"""Deterministic naming conventions for tables and files."""

from typing import Any

from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.knot import Knot
from data_architect.models.tie import Tie


def anchor_table_name(anchor: Anchor) -> str:
    """Generate anchor table name.

    Args:
        anchor: Anchor model instance

    Returns:
        Table name in format: {mnemonic}_{descriptor}
    """
    raise NotImplementedError


def attribute_table_name(anchor: Anchor, attribute: Attribute) -> str:
    """Generate attribute table name.

    Args:
        anchor: Parent anchor model instance
        attribute: Attribute model instance

    Returns:
        Table name in format:
        {anchor_mnemonic}_{attr_mnemonic}_{anchor_descriptor}_{attr_descriptor}
    """
    raise NotImplementedError


def knot_table_name(knot: Knot) -> str:
    """Generate knot table name.

    Args:
        knot: Knot model instance

    Returns:
        Table name in format: {mnemonic}_{descriptor}
    """
    raise NotImplementedError


def tie_table_name(tie: Tie) -> str:
    """Generate tie table name based on sorted roles.

    Args:
        tie: Tie model instance

    Returns:
        Table name composed from sorted role types and names
    """
    raise NotImplementedError


def staging_table_name(mapping: dict[str, Any]) -> str:
    """Extract staging table name from mapping definition.

    Args:
        mapping: Staging mapping dictionary with "table" key

    Returns:
        Table name from mapping["table"]
    """
    raise NotImplementedError
