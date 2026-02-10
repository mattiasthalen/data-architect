"""XSD validation for Anchor Modeler XML.

Validates exported XML against anchor.xsd with support for XSD 1.0 validators
that don't support xs:assert elements (like lxml).
"""

from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

# Locate anchor.xsd relative to project root
_XSD_PATH = (
    Path(__file__).parent.parent.parent.parent / ".references" / "anchor" / "anchor.xsd"
)

# Cache compiled schema at module level for performance
_COMPILED_SCHEMA: etree.XMLSchema | None = None


def _strip_assertions(xsd_content: str) -> str:
    """Strip xs:assert elements from XSD content for XSD 1.0 compatibility.

    lxml's XMLSchema validator only supports XSD 1.0 which doesn't include
    xs:assert. The anchor.xsd uses assertions for semantic validation, but
    these are not critical for basic structural validation.

    Args:
        xsd_content: XSD file content as string.

    Returns:
        XSD content with xs:assert elements removed.
    """
    # Remove xs:assert elements (self-closing or with content)
    # Pattern: <xs:assert ... /> or <xs:assert ...>...</xs:assert>
    pattern = r"<xs:assert\s+[^>]*(?:/>|>.*?</xs:assert>)"
    return re.sub(pattern, "", xsd_content, flags=re.DOTALL)


def _get_compiled_schema() -> etree.XMLSchema:
    """Get cached compiled XMLSchema or compile it.

    Returns:
        Compiled XMLSchema instance.

    Raises:
        ValueError: If XSD file not found or compilation fails.
    """
    global _COMPILED_SCHEMA

    if _COMPILED_SCHEMA is not None:
        return _COMPILED_SCHEMA

    if not _XSD_PATH.exists():
        msg = f"anchor.xsd not found at {_XSD_PATH}"
        raise ValueError(msg)

    # Load XSD content
    xsd_content = _XSD_PATH.read_text(encoding="utf-8")

    # Strip assertions for XSD 1.0 compatibility
    xsd_content_stripped = _strip_assertions(xsd_content)

    # Parse and compile schema
    try:
        xsd_doc = etree.fromstring(xsd_content_stripped.encode("utf-8"))
        _COMPILED_SCHEMA = etree.XMLSchema(xsd_doc)
    except etree.XMLSchemaParseError as e:
        msg = f"Failed to compile anchor.xsd: {e}"
        raise ValueError(msg) from e

    return _COMPILED_SCHEMA


def validate_xml_against_xsd(xml_bytes: bytes) -> tuple[bool, list[str]]:
    """Validate XML bytes against anchor.xsd.

    Note: XSD assertions (xs:assert) are stripped for XSD 1.0 compatibility.
    This means semantic validations (tie must reference 2+ anchors, nexus
    must have 1+ anchor role, etc.) are not enforced by XSD validation.

    Args:
        xml_bytes: XML content as bytes.

    Returns:
        Tuple of (is_valid, error_messages).
        error_messages includes line/column numbers from lxml.
    """
    schema = _get_compiled_schema()

    # Parse XML
    try:
        xml_doc = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError as e:
        return False, [f"XML syntax error: {e}"]

    # Validate against schema
    is_valid = schema.validate(xml_doc)

    if is_valid:
        return True, []

    # Collect error messages with line/column info
    error_messages = []
    for error in schema.error_log:  # type: ignore[attr-defined]
        error_messages.append(
            f"Line {error.line}, Column {error.column}: {error.message}"
        )

    return False, error_messages
