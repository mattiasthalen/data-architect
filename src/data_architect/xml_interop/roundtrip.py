"""Round-trip utilities for XML canonicalization and semantic comparison.

Uses C14N (Canonical XML) to normalize XML for semantic equivalence testing,
ignoring differences in attribute order, whitespace, and namespace prefixes.
"""

from __future__ import annotations

from lxml import etree


def _strip_namespace(xml_bytes: bytes) -> bytes:
    """Strip namespace from all elements in XML.

    This is needed for round-trip comparison because:
    - Original Anchor Modeler XML may lack xmlns declaration
    - Exported XML always includes xmlns="http://anchormodeling.com/schema"
    - We want to compare semantic content, not namespace formatting

    Args:
        xml_bytes: XML content as bytes.

    Returns:
        XML with namespaces stripped from all elements.
    """
    # Use lxml cleanup_namespaces to remove unused namespace declarations
    parser = etree.XMLParser(remove_blank_text=False)
    doc = etree.fromstring(xml_bytes, parser)

    # Strip namespace from all element tags
    for elem in doc.iter():
        # Remove namespace from tag (Clark notation {namespace}localname)
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    # Now rebuild tree without namespace to remove xmlns from nsmap
    # Create new root element without namespace
    new_root = etree.Element(doc.tag, nsmap=None)
    new_root.attrib.update(doc.attrib)
    new_root.text = doc.text
    new_root.tail = doc.tail

    # Copy all children
    for child in doc:
        new_root.append(child)

    return etree.tostring(new_root)


def canonicalize_xml(xml_string: str) -> bytes:
    """Canonicalize XML using C14N for semantic comparison.

    Normalizes:
    - Attribute order (alphabetical)
    - Whitespace between elements (removed)
    - Namespace prefixes
    - XML declaration and encoding

    Note: C14N does NOT reorder child elements. Element order matters.

    Args:
        xml_string: XML content as string.

    Returns:
        Canonical XML as bytes (C14N form) with whitespace stripped.
    """
    xml_bytes = (
        xml_string.encode("utf-8") if isinstance(xml_string, str) else xml_string
    )

    # Strip namespace for comparison (export adds namespace, original may not have it)
    xml_bytes = _strip_namespace(xml_bytes)

    # Parse and remove whitespace-only text nodes
    parser = etree.XMLParser(remove_blank_text=True)
    doc = etree.fromstring(xml_bytes, parser)

    # Canonicalize using C14N 2.0
    canonical = etree.tostring(doc, method="c14n2")

    return canonical


def assert_roundtrip_equivalent(original_xml: str, roundtrip_xml: str) -> None:
    """Assert two XML strings are semantically equivalent.

    Uses C14N canonicalization to ignore formatting differences.
    Raises AssertionError with details if not equivalent.

    Args:
        original_xml: Original XML string.
        roundtrip_xml: Round-trip XML string (import -> export).

    Raises:
        AssertionError: If XML is not semantically equivalent.
    """
    canonical_original = canonicalize_xml(original_xml)
    canonical_roundtrip = canonicalize_xml(roundtrip_xml)

    if canonical_original != canonical_roundtrip:
        # Provide helpful error message with diff preview
        orig_preview = canonical_original[:200].decode("utf-8", errors="replace")
        rt_preview = canonical_roundtrip[:200].decode("utf-8", errors="replace")

        msg = (
            f"XML round-trip mismatch:\n"
            f"Original (first 200 bytes): {orig_preview}...\n"
            f"Round-trip (first 200 bytes): {rt_preview}..."
        )
        raise AssertionError(msg)
