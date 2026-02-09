"""Keyset identity module for multi-source data provenance tracking.

Provides parsing and formatting of keyset identity strings with the format:
    entity@system~tenant|natural_key

All components support delimiter characters through automatic escaping.
NULL natural keys produce NULL keysets (KEY-05 null safety).
"""

from data_architect.identity.escaping import (
    escape_delimiters,
    unescape_delimiters,
)
from data_architect.identity.keyset import (
    KeysetComponents,
    format_keyset,
    parse_keyset,
)

__all__ = [
    "KeysetComponents",
    "escape_delimiters",
    "format_keyset",
    "parse_keyset",
    "unescape_delimiters",
]
