"""Import Anchor Modeler XML files to YAML Spec format."""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree

from data_architect.xml_interop.models import SchemaXML

if TYPE_CHECKING:
    from pathlib import Path

    from data_architect.models.spec import Spec


def import_xml_to_spec(xml_path: Path) -> Spec:
    """Import Anchor Modeler XML file to Spec.

    Args:
        xml_path: Path to XML file.

    Returns:
        Spec object with all entities from the XML file.

    Raises:
        FileNotFoundError: If xml_path does not exist.
        ValueError: If XML is malformed or invalid.
    """
    if not xml_path.exists():
        msg = f"XML file not found: {xml_path}"
        raise FileNotFoundError(msg)

    xml_string = xml_path.read_text(encoding="utf-8")
    return import_xml_string_to_spec(xml_string)


def import_xml_string_to_spec(xml_string: str) -> Spec:
    """Import Anchor Modeler XML string to Spec.

    Handles both namespaced and un-namespaced XML. The official example.xml
    does not use namespaces, but real Anchor Modeler exports may include
    xmlns="http://anchormodeling.com/schema".

    Args:
        xml_string: XML content as string.

    Returns:
        Spec object with all entities from the XML.

    Raises:
        ValueError: If XML is malformed or invalid.
    """
    # Strip namespace if present for un-namespaced parsing
    xml_string_clean = _strip_namespace(xml_string)

    # Parse with pydantic-xml
    xml_bytes = xml_string_clean.encode("utf-8")
    schema_xml = SchemaXML.from_xml(xml_bytes)

    # Also parse raw lxml for metadata extraction
    raw_doc = etree.fromstring(xml_bytes)

    # Convert to YAML Spec model
    spec = schema_xml.to_yaml_model(raw_elem=raw_doc)

    return spec


def _strip_namespace(xml_string: str) -> str:
    """Remove default namespace from XML for un-namespaced parsing.

    The anchor.xsd defines xmlns="http://anchormodeling.com/schema", but
    the official example.xml does not use it. We strip namespaces to support
    both cases with a single set of pydantic-xml models.

    Args:
        xml_string: Original XML string (possibly with namespace).

    Returns:
        XML string with namespace declarations and prefixes removed.
    """
    try:
        doc = etree.fromstring(xml_string.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        msg = f"Invalid XML: {e}"
        raise ValueError(msg) from e

    # Rebuild tree without namespaces by creating new elements
    def strip_ns(elem: etree._Element) -> etree._Element:
        """Recursively create new element without namespace."""
        # Get tag without namespace
        tag = elem.tag.split("}", 1)[1] if "}" in elem.tag else elem.tag

        # Create new element with same tag (no namespace) and attributes
        # Convert attrib to dict, handling str/bytes (lxml can use both)
        attribs: dict[str, str] = {
            (k if isinstance(k, str) else k.decode()): (
                v if isinstance(v, str) else v.decode()
            )
            for k, v in elem.attrib.items()
        }
        new_elem = etree.Element(tag, attrib=attribs)
        new_elem.text = elem.text
        new_elem.tail = elem.tail

        # Recursively process children
        for child in elem:
            new_elem.append(strip_ns(child))

        return new_elem

    new_doc = strip_ns(doc)

    # encoding="unicode" returns str, but mypy sees return type as str | bytes
    result = etree.tostring(new_doc, encoding="unicode")
    return str(result)
