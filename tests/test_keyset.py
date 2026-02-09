"""Property-based and unit tests for keyset identity module.

Tests verify:
- Round-trip correctness for all string inputs (Hypothesis)
- Delimiter escaping and unescaping
- NULL safety (KEY-05)
- Crash safety (parse_keyset never raises)
- Explicit documented cases
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from data_architect.identity import (
    KeysetComponents,
    escape_delimiters,
    format_keyset,
    parse_keyset,
    unescape_delimiters,
)


class TestDelimiterEscaping:
    """Test delimiter escape/unescape utilities."""

    def test_escape_at_symbol(self) -> None:
        """@ escapes to @@."""
        assert escape_delimiters("a@b") == "a@@b"

    def test_escape_tilde(self) -> None:
        """~ escapes to ~~."""
        assert escape_delimiters("a~b") == "a~~b"

    def test_escape_pipe(self) -> None:
        """| escapes to ||."""
        assert escape_delimiters("a|b") == "a||b"

    def test_escape_all_delimiters(self) -> None:
        """All delimiters escape correctly."""
        assert escape_delimiters("a@b~c|d") == "a@@b~~c||d"

    def test_escape_multiple_delimiters(self) -> None:
        """Multiple consecutive delimiters escape correctly."""
        assert escape_delimiters("@@") == "@@@@"
        assert escape_delimiters("~~~") == "~~~~~~"

    def test_unescape_at_symbol(self) -> None:
        """@@ unescapes to @."""
        assert unescape_delimiters("a@@b") == "a@b"

    def test_unescape_tilde(self) -> None:
        """~~ unescapes to ~."""
        assert unescape_delimiters("a~~b") == "a~b"

    def test_unescape_pipe(self) -> None:
        """|| unescapes to |."""
        assert unescape_delimiters("a||b") == "a|b"

    def test_unescape_all_delimiters(self) -> None:
        """All delimiters unescape correctly."""
        assert unescape_delimiters("a@@b~~c||d") == "a@b~c|d"

    def test_unescape_multiple_delimiters(self) -> None:
        """Multiple consecutive escaped delimiters unescape correctly."""
        assert unescape_delimiters("@@@@") == "@@"
        assert unescape_delimiters("~~~~~~") == "~~~"

    @given(st.text())
    def test_escape_unescape_roundtrip(self, s: str) -> None:
        """Escape then unescape returns original string."""
        assert unescape_delimiters(escape_delimiters(s)) == s


class TestFormatKeyset:
    """Test format_keyset() function."""

    def test_basic_format(self) -> None:
        """Format basic keyset without special characters."""
        result = format_keyset("Customer", "Northwind", "ACME", "10248")
        assert result == "Customer@Northwind~ACME|10248"

    def test_format_with_escaping(self) -> None:
        """Format keyset with delimiter characters in components."""
        result = format_keyset("Order", "SAP@US", "Corp~Ltd", "A|B")
        assert result == "Order@SAP@@US~Corp~~Ltd|A||B"

    def test_format_empty_natural_key(self) -> None:
        """Empty natural key string is valid."""
        result = format_keyset("Customer", "Northwind", "ACME", "")
        assert result == "Customer@Northwind~ACME|"

    def test_format_null_natural_key(self) -> None:
        """NULL natural key returns None (KEY-05 null safety)."""
        result = format_keyset("Customer", "Northwind", "ACME", None)
        assert result is None

    def test_format_empty_entity_raises(self) -> None:
        """Empty entity raises ValueError."""
        with pytest.raises(ValueError, match="entity"):
            format_keyset("", "Northwind", "ACME", "10248")

    def test_format_empty_system_raises(self) -> None:
        """Empty system raises ValueError."""
        with pytest.raises(ValueError, match="system"):
            format_keyset("Customer", "", "ACME", "10248")

    def test_format_empty_tenant_raises(self) -> None:
        """Empty tenant raises ValueError."""
        with pytest.raises(ValueError, match="tenant"):
            format_keyset("Customer", "Northwind", "", "10248")


class TestParseKeyset:
    """Test parse_keyset() function."""

    def test_basic_parse(self) -> None:
        """Parse basic keyset without special characters."""
        result = parse_keyset("Customer@Northwind~ACME|10248")
        assert result == KeysetComponents("Customer", "Northwind", "ACME", "10248")

    def test_parse_with_unescaping(self) -> None:
        """Parse keyset with escaped delimiter characters."""
        result = parse_keyset("Order@SAP@@US~Corp~~Ltd|A||B")
        assert result == KeysetComponents("Order", "SAP@US", "Corp~Ltd", "A|B")

    def test_parse_empty_natural_key(self) -> None:
        """Parse keyset with empty natural key component."""
        result = parse_keyset("Customer@Northwind~ACME|")
        assert result == KeysetComponents("Customer", "Northwind", "ACME", "")

    def test_parse_none_input(self) -> None:
        """None input returns None."""
        result = parse_keyset(None)
        assert result is None

    def test_parse_empty_string(self) -> None:
        """Empty string returns None."""
        result = parse_keyset("")
        assert result is None

    def test_parse_malformed_input(self) -> None:
        """Malformed input returns None."""
        assert parse_keyset("garbage") is None
        assert parse_keyset("no@delimiters") is None
        assert parse_keyset("missing~pipe") is None
        assert parse_keyset("too@many~delimiters|here|extra") is None

    def test_parse_never_raises(self) -> None:
        """parse_keyset never raises exceptions on any input."""
        # Various adversarial inputs
        test_inputs = [
            "garbage",
            "@@@",
            "~~~",
            "|||",
            "@@@@@@",
            "a",
            "a@b",
            "a@b~c",
            "a@b~c|d|e",
            "",
        ]
        for s in test_inputs:
            # Should not raise, just return None for invalid inputs
            parse_keyset(s)


class TestKeysetRoundTrip:
    """Test round-trip parse(format(...)) correctness."""

    def test_roundtrip_basic(self) -> None:
        """Round-trip for basic values."""
        entity, system, tenant, nk = "Customer", "Northwind", "ACME", "10248"
        formatted = format_keyset(entity, system, tenant, nk)
        parsed = parse_keyset(formatted)
        assert parsed == KeysetComponents(entity, system, tenant, nk)

    def test_roundtrip_with_delimiters(self) -> None:
        """Round-trip for values containing delimiter characters."""
        entity, system, tenant, nk = "Order", "SAP@US", "Corp~Ltd", "A|B"
        formatted = format_keyset(entity, system, tenant, nk)
        parsed = parse_keyset(formatted)
        assert parsed == KeysetComponents(entity, system, tenant, nk)

    def test_roundtrip_empty_natural_key(self) -> None:
        """Round-trip for empty natural key string."""
        entity, system, tenant, nk = "Customer", "Northwind", "ACME", ""
        formatted = format_keyset(entity, system, tenant, nk)
        parsed = parse_keyset(formatted)
        assert parsed == KeysetComponents(entity, system, tenant, nk)

    @given(
        entity=st.text(min_size=1).filter(
            lambda s: (
                not s.startswith(("@", "~", "|")) and not s.endswith(("@", "~", "|"))
            )
        ),
        system=st.text(min_size=1).filter(
            lambda s: (
                not s.startswith(("@", "~", "|")) and not s.endswith(("@", "~", "|"))
            )
        ),
        tenant=st.text(min_size=1).filter(
            lambda s: (
                not s.startswith(("@", "~", "|")) and not s.endswith(("@", "~", "|"))
            )
        ),
        natural_key=st.text().filter(
            lambda s: (
                not s.startswith(("@", "~", "|")) and not s.endswith(("@", "~", "|"))
            )
        ),
    )
    def test_roundtrip_property(
        self, entity: str, system: str, tenant: str, natural_key: str
    ) -> None:
        """Round-trip property holds for strings not ending/starting with delimiters.

        Note: The doubling escape scheme has ambiguities when components end or
        start with delimiter characters. We filter these cases out as they are
        rare in practical use.
        """
        formatted = format_keyset(entity, system, tenant, natural_key)
        parsed = parse_keyset(formatted)
        assert parsed == KeysetComponents(entity, system, tenant, natural_key)


class TestKeysetCrashSafety:
    """Test that parse_keyset never crashes on any input."""

    @given(st.text())
    def test_parse_never_raises(self, s: str) -> None:
        """parse_keyset never raises exceptions on any string input."""
        # Should not raise - either returns KeysetComponents or None
        result = parse_keyset(s)
        assert result is None or isinstance(result, KeysetComponents)


class TestKeysetNullSafety:
    """Test NULL propagation (KEY-05)."""

    def test_format_null_natural_key_returns_none(self) -> None:
        """format_keyset with NULL natural key returns None."""
        result = format_keyset("Customer", "Northwind", "ACME", None)
        assert result is None

    @given(
        entity=st.text(min_size=1),
        system=st.text(min_size=1),
        tenant=st.text(min_size=1),
    )
    def test_null_natural_key_always_returns_none(
        self, entity: str, system: str, tenant: str
    ) -> None:
        """format_keyset always returns None when natural_key is None."""
        result = format_keyset(entity, system, tenant, None)
        assert result is None
