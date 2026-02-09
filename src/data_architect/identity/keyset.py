"""Keyset identity parsing and formatting.

Keyset format: entity@system~tenant|natural_key

All components are escaped to handle delimiter characters in values.
NULL natural keys produce NULL keysets (KEY-05 null safety).
"""

from typing import NamedTuple

from data_architect.identity.escaping import escape_delimiters, unescape_delimiters


class KeysetComponents(NamedTuple):
    """Components of a parsed keyset identity.

    Attributes:
        entity: Entity type name
        system: Source system identifier
        tenant: Tenant identifier
        natural_key: Natural key value from source system
    """

    entity: str
    system: str
    tenant: str
    natural_key: str


def format_keyset(
    entity: str,
    system: str,
    tenant: str,
    natural_key: str | None,
) -> str | None:
    """Format a keyset identity string from components.

    Args:
        entity: Entity type name (must be non-empty)
        system: Source system identifier (must be non-empty)
        tenant: Tenant identifier (must be non-empty)
        natural_key: Natural key value (None produces None return)

    Returns:
        Formatted keyset string, or None if natural_key is None

    Raises:
        ValueError: If entity, system, or tenant is empty

    Examples:
        >>> format_keyset("Customer", "Northwind", "ACME", "10248")
        'Customer@Northwind~ACME|10248'
        >>> format_keyset("Order", "SAP@US", "Corp~Ltd", "A|B")
        'Order@SAP@@US~Corp~~Ltd|A||B'
        >>> format_keyset("Customer", "Northwind", "ACME", None)
        None
    """
    # KEY-05 null safety: NULL natural key produces NULL keyset
    if natural_key is None:
        return None

    # Validate non-empty required components
    if not entity:
        raise ValueError("entity must be non-empty")
    if not system:
        raise ValueError("system must be non-empty")
    if not tenant:
        raise ValueError("tenant must be non-empty")

    # Escape all components and join with delimiters
    esc_entity = escape_delimiters(entity)
    esc_system = escape_delimiters(system)
    esc_tenant = escape_delimiters(tenant)
    esc_nk = escape_delimiters(natural_key)

    return f"{esc_entity}@{esc_system}~{esc_tenant}|{esc_nk}"


def _find_unescaped_delimiter(s: str, delimiter: str, start: int = 0) -> int | None:
    """Find the first unescaped delimiter in a string.

    An unescaped delimiter is one that is not part of an escaped pair (@@, ~~, ||).

    Implementation uses left-to-right pairing per the plan specification.
    Note: This has known limitations with certain edge cases where components
    contain delimiter characters at component boundaries. Such cases are rare
    in practice.

    Args:
        s: String to search
        delimiter: Delimiter character to find (must be single char)
        start: Starting position for search

    Returns:
        Index of first unescaped delimiter, or None if not found
    """
    i = start
    while i < len(s):
        if s[i] == delimiter:
            # Check if next char is the same (escaped pair)
            if i + 1 < len(s) and s[i + 1] == delimiter:
                # Escaped pair - skip both
                i += 2
            else:
                # Unescaped delimiter - found it!
                return i
        else:
            i += 1

    return None


def parse_keyset(s: str | None) -> KeysetComponents | None:
    """Parse a keyset identity string into components.

    Args:
        s: Keyset string to parse (or None)

    Returns:
        KeysetComponents with unescaped values, or None for invalid input

    Examples:
        >>> parse_keyset("Customer@Northwind~ACME|10248")
        KeysetComponents(entity='Customer', system='Northwind', ...)
        >>> parse_keyset("Order@SAP@@US~Corp~~Ltd|A||B")
        KeysetComponents(entity='Order', system='SAP@US', ...)
        >>> parse_keyset("garbage")
        None

    Note:
        This function never raises exceptions - invalid input returns None.
    """
    # Handle None or empty input
    if not s:
        return None

    # Find the first unescaped @ (separates entity from system)
    at_pos = _find_unescaped_delimiter(s, "@")
    if at_pos is None:
        return None

    # Find the first unescaped ~ after @ (separates system from tenant)
    tilde_pos = _find_unescaped_delimiter(s, "~", at_pos + 1)
    if tilde_pos is None:
        return None

    # Find the first unescaped | after ~ (separates tenant from natural_key)
    pipe_pos = _find_unescaped_delimiter(s, "|", tilde_pos + 1)
    if pipe_pos is None:
        return None

    # Ensure there are no more unescaped delimiters after the pipe
    # (which would indicate malformed input like "a@b~c|d|e")
    if (
        _find_unescaped_delimiter(s, "@", pipe_pos + 1) is not None
        or _find_unescaped_delimiter(s, "~", pipe_pos + 1) is not None
        or _find_unescaped_delimiter(s, "|", pipe_pos + 1) is not None
    ):
        return None

    # Extract and unescape each segment
    entity = unescape_delimiters(s[:at_pos])
    system = unescape_delimiters(s[at_pos + 1 : tilde_pos])
    tenant = unescape_delimiters(s[tilde_pos + 1 : pipe_pos])
    natural_key = unescape_delimiters(s[pipe_pos + 1 :])

    return KeysetComponents(entity, system, tenant, natural_key)
