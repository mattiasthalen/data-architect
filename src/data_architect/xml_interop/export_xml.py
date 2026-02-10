"""Export YAML Spec to Anchor Modeler XML format.

Converts Pydantic YAML models to pydantic-xml models, serializes to XML,
and validates against anchor.xsd. Detects and warns about YAML-only extensions
that cannot be represented in XML.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lxml import etree

from data_architect.xml_interop.models import SchemaXML, _set_metadata_attrs
from data_architect.xml_interop.validation import validate_xml_against_xsd

if TYPE_CHECKING:
    from data_architect.models.spec import Spec


def check_yaml_extensions(spec: Spec) -> list[str]:
    """Check for YAML-extension fields present in spec.

    YAML extensions are fields that exist in the YAML Pydantic models but
    cannot be represented in Anchor Modeler XML format. These include:
    - staging_mappings on anchors (Phase 8 feature)
    - staging_column on attributes (Phase 8 feature)

    Args:
        spec: YAML Spec to check.

    Returns:
        List of human-readable descriptions of extensions found.
        Empty list if no extensions present.
    """
    extensions = []

    # Check anchors for staging_mappings
    for anchor in spec.anchors:
        if anchor.staging_mappings:
            count = len(anchor.staging_mappings)
            plural = "s" if count > 1 else ""
            extensions.append(
                f"Anchor '{anchor.mnemonic}' has {count} staging mapping{plural}"
            )

        # Check attributes for staging_column
        for attr in anchor.attributes:
            if attr.staging_column:
                attr_name = f"{anchor.mnemonic}.{attr.mnemonic}"
                extensions.append(
                    f"Attribute '{attr_name}' has "
                    f"staging_column '{attr.staging_column}'"
                )

    # Check nexus attributes for staging_column
    for nexus in spec.nexuses:
        for attr in nexus.attributes:
            if attr.staging_column:
                attr_name = f"{nexus.mnemonic}.{attr.mnemonic}"
                extensions.append(
                    f"Attribute '{attr_name}' has "
                    f"staging_column '{attr.staging_column}'"
                )

    return extensions


def export_spec_to_xml(spec: Spec, *, force: bool = False) -> str:
    """Export YAML Spec to Anchor Modeler XML string.

    Steps:
    1. Check for YAML extensions - if present and not force, raise ValueError
    2. Convert Spec to SchemaXML via from_yaml_model()
    3. Serialize SchemaXML to XML bytes using pydantic-xml
    4. Add namespace declaration xmlns="http://anchormodeling.com/schema"
    5. Add metadata attributes back to XML elements (pydantic-xml doesn't
       handle xs:anyAttribute)
    6. Validate against anchor.xsd
    7. Pretty-print and return with XML declaration

    Args:
        spec: YAML Spec to export.
        force: If True, proceed even if YAML extensions present (they will be dropped).

    Returns:
        XML string with declaration and pretty-printing.

    Raises:
        ValueError: If YAML extensions present and force=False.
        ValueError: If generated XML fails XSD validation.
    """
    # Check for YAML extensions
    extensions = check_yaml_extensions(spec)
    if extensions and not force:
        ext_list = "\n  - ".join(extensions)
        msg = (
            f"YAML-only extensions will be dropped during export:\n  - {ext_list}\n"
            f"Use force=True to proceed."
        )
        raise ValueError(msg)

    # Convert Spec to SchemaXML
    schema_xml = SchemaXML.from_yaml_model(spec)

    # Serialize to XML bytes
    # Use exclude_none to omit None attributes but preserve empty elements
    xml_result = schema_xml.to_xml(exclude_none=True)
    xml_bytes = (
        xml_result if isinstance(xml_result, bytes) else xml_result.encode("utf-8")
    )

    # Add namespace and metadata attributes
    xml_bytes = _add_namespace_and_metadata(xml_bytes, spec)

    # Validate against XSD
    is_valid, errors = validate_xml_against_xsd(xml_bytes)
    if not is_valid:
        error_list = "\n  ".join(errors)
        msg = f"Generated XML failed XSD validation:\n  {error_list}"
        raise ValueError(msg)

    # Pretty-print
    xml_doc = etree.fromstring(xml_bytes)
    pretty_xml = etree.tostring(
        xml_doc,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )

    return pretty_xml.decode("utf-8")


def _add_namespace_and_metadata(xml_bytes: bytes, spec: Spec) -> bytes:
    """Add Anchor Modeling namespace and metadata attributes to XML.

    Args:
        xml_bytes: XML bytes from pydantic-xml serialization.
        spec: Original Spec for extracting metadata attributes.

    Returns:
        XML bytes with namespace and metadata attributes added.
    """
    NS = "http://anchormodeling.com/schema"

    # Parse XML
    doc = etree.fromstring(xml_bytes)

    # Replace the namespaced prefix (ns0:) with default namespace
    # pydantic-xml creates xmlns:ns0="..." but we want xmlns="..."
    # Strategy: remove the ns0 prefix from all tags and set nsmap on root
    for elem in doc.iter():
        # Remove namespace prefix from tag (ns0:schema -> schema)
        if "}" in elem.tag:
            # Extract local name from Clark notation {namespace}localname
            ns, local = elem.tag.split("}", 1)
            elem.tag = f"{ns}}}{local}"  # Keep it as is for now

    # Create new root with default namespace (no prefix)
    # We need to rebuild the tree to change nsmap
    nsmap: dict[str | None, str] = {None: NS}  # Default namespace (no prefix)
    attrib_dict: dict[str, str] = {
        (k if isinstance(k, str) else k.decode()): (
            v if isinstance(v, str) else v.decode()
        )
        for k, v in doc.attrib.items()
    }
    new_root = etree.Element(
        doc.tag.split("}", 1)[1] if "}" in doc.tag else doc.tag,
        nsmap=nsmap,  # type: ignore[arg-type]
        attrib=attrib_dict,
    )

    # Copy all children
    for child in doc:
        new_root.append(child)

    doc = new_root

    # Now set namespace on all elements (using default namespace)
    for elem in doc.iter():
        if "}" not in elem.tag:  # Only add namespace if not already present
            elem.tag = f"{{{NS}}}{elem.tag}"

    # Add metadata attributes from original models
    # Schema-level metadata
    if spec.metadata_:
        _set_metadata_attrs(doc, spec.metadata_)

    # Knot metadata
    for i, knot in enumerate(spec.knots):
        if knot.metadata_:
            knot_elems = doc.findall(f"{{{NS}}}knot")
            if i < len(knot_elems):
                _set_metadata_attrs(knot_elems[i], knot.metadata_)

    # Anchor metadata
    for i, anchor in enumerate(spec.anchors):
        anchor_elems = doc.findall(f"{{{NS}}}anchor")
        if i < len(anchor_elems):
            anchor_elem = anchor_elems[i]

            # Set anchor-level metadata if present
            if anchor.metadata_:
                _set_metadata_attrs(anchor_elem, anchor.metadata_)

            # Attribute metadata
            for j, attr in enumerate(anchor.attributes):
                if attr.metadata_:
                    attr_elems = anchor_elem.findall(f"{{{NS}}}attribute")
                    if j < len(attr_elems):
                        _set_metadata_attrs(attr_elems[j], attr.metadata_)

    # Nexus metadata
    for i, nexus in enumerate(spec.nexuses):
        nexus_elems = doc.findall(f"{{{NS}}}nexus")
        if i < len(nexus_elems):
            nexus_elem = nexus_elems[i]

            # Set nexus-level metadata if present
            if nexus.metadata_:
                _set_metadata_attrs(nexus_elem, nexus.metadata_)

            # Attribute metadata
            for j, attr in enumerate(nexus.attributes):
                if attr.metadata_:
                    attr_elems = nexus_elem.findall(f"{{{NS}}}attribute")
                    if j < len(attr_elems):
                        _set_metadata_attrs(attr_elems[j], attr.metadata_)

            # Role metadata
            for j, role in enumerate(nexus.roles):
                if role.metadata_:
                    role_elems = nexus_elem.findall(f"{{{NS}}}role")
                    if j < len(role_elems):
                        _set_metadata_attrs(role_elems[j], role.metadata_)

    # Tie metadata
    for i, tie in enumerate(spec.ties):
        tie_elems = doc.findall(f"{{{NS}}}tie")
        if i < len(tie_elems):
            tie_elem = tie_elems[i]

            # Set tie-level metadata if present
            if tie.metadata_:
                _set_metadata_attrs(tie_elem, tie.metadata_)

            # Role metadata
            for j, role in enumerate(tie.roles):
                if role.metadata_:
                    role_elems = tie_elem.findall(f"{{{NS}}}role")
                    if j < len(role_elems):
                        _set_metadata_attrs(role_elems[j], role.metadata_)

    return etree.tostring(doc)
