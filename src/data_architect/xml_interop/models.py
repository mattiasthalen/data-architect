"""Pydantic-XML models for parsing Anchor Modeler XML.

These models mirror the anchor.xsd structure and are separate from the YAML
Pydantic models in data_architect.models. They exist solely for XML
serialization/deserialization using pydantic-xml.

Each model has a to_yaml_model() method that converts to the corresponding
YAML Pydantic model for use with the rest of the application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic_xml import BaseXmlModel, attr, element

from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.common import Identifier, Key
from data_architect.models.knot import Knot
from data_architect.models.spec import Nexus, Spec
from data_architect.models.tie import Role, Tie

if TYPE_CHECKING:
    from lxml import etree


class KeyXML(BaseXmlModel, tag="key"):
    """XML model for key element."""

    stop: str = attr()
    route: str = attr()
    of_: str = attr(name="of")
    branch: str = attr(default="1")

    def to_yaml_model(self) -> Key:
        """Convert to YAML Pydantic Key model."""
        return Key(stop=self.stop, route=self.route, of_=self.of_, branch=self.branch)

    @classmethod
    def from_yaml_model(cls, key: Key) -> KeyXML:
        """Convert from YAML Pydantic Key model."""
        return cls(stop=key.stop, route=key.route, of_=key.of_, branch=key.branch)


class IdentifierXML(BaseXmlModel, tag="identifier"):
    """XML model for identifier element."""

    route: str = attr()

    def to_yaml_model(self) -> Identifier:
        """Convert to YAML Pydantic Identifier model."""
        return Identifier(route=self.route)

    @classmethod
    def from_yaml_model(cls, identifier: Identifier) -> IdentifierXML:
        """Convert from YAML Pydantic Identifier model."""
        return cls(route=identifier.route)


class DescriptionXML(BaseXmlModel, tag="description"):
    """XML model for description element - simple text content."""

    content: str


class MetadataXML(BaseXmlModel, tag="metadata"):
    """XML model for metadata element.

    Since anchor.xsd allows xs:anyAttribute, we parse arbitrary attributes
    using lxml directly rather than pydantic-xml field definitions.
    The metadata dict is populated during conversion.
    """

    pass


class LayoutXML(BaseXmlModel, tag="layout"):
    """XML model for layout element - preserve as opaque content."""

    pass


class AttributeXML(BaseXmlModel, tag="attribute"):
    """XML model for attribute element."""

    mnemonic: str = attr()
    descriptor: str = attr()
    knot_range: str | None = attr(name="knotRange", default=None)
    data_range: str | None = attr(name="dataRange", default=None)
    time_range: str | None = attr(name="timeRange", default=None)

    keys: list[KeyXML] = element(tag="key", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Attribute:
        """Convert to YAML Pydantic Attribute model.

        Args:
            raw_elem: The raw lxml element for extracting metadata attributes.
        """
        # Extract metadata if present
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        return Attribute(
            mnemonic=self.mnemonic,
            descriptor=self.descriptor,
            knot_range=self.knot_range,
            data_range=self.data_range,
            time_range=self.time_range,
            keys=[k.to_yaml_model() for k in self.keys],
            metadata_=metadata_dict,
            layout=None,  # Layout not preserved in YAML models
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, attr: Attribute) -> AttributeXML:
        """Convert from YAML Pydantic Attribute model.

        Note: staging_column is a YAML-extension field and is NOT exported to XML.
        """
        # Create metadata element if metadata present
        metadata_elem = MetadataXML() if attr.metadata_ else None
        description_elem = (
            DescriptionXML(content=attr.description_) if attr.description_ else None
        )

        # pydantic-xml models use skip_empty during serialization
        # so we can pass all values including None
        return cls(
            mnemonic=attr.mnemonic,
            descriptor=attr.descriptor,
            knot_range=attr.knot_range,
            data_range=attr.data_range,
            time_range=attr.time_range,
            keys=[KeyXML.from_yaml_model(k) for k in attr.keys],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class RoleXML(BaseXmlModel, tag="role"):
    """XML model for role element."""

    role: str = attr()
    type_: str = attr(name="type")
    identifier: bool = attr(default=False)
    coloring: str | None = attr(default=None)

    keys: list[KeyXML] = element(tag="key", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Role:
        """Convert to YAML Pydantic Role model.

        Args:
            raw_elem: The raw lxml element for extracting metadata attributes.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        return Role(
            role=self.role,
            type_=self.type_,
            identifier=self.identifier,
            coloring=self.coloring,
            keys=[k.to_yaml_model() for k in self.keys],
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, role: Role) -> RoleXML:
        """Convert from YAML Pydantic Role model."""
        metadata_elem = MetadataXML() if role.metadata_ else None
        description_elem = (
            DescriptionXML(content=role.description_) if role.description_ else None
        )

        return cls(
            role=role.role,
            type_=role.type_,
            identifier=role.identifier,
            coloring=role.coloring,
            keys=[KeyXML.from_yaml_model(k) for k in role.keys],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class AnchorXML(BaseXmlModel, tag="anchor"):
    """XML model for anchor element."""

    mnemonic: str = attr()
    descriptor: str = attr()
    identity: str = attr()

    attributes: list[AttributeXML] = element(tag="attribute", default_factory=list)
    identifiers: list[IdentifierXML] = element(tag="identifier", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Anchor:
        """Convert to YAML Pydantic Anchor model.

        Args:
            raw_elem: The raw lxml element for extracting metadata and child elements.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        # Get child attribute elements for metadata extraction
        attr_elems = list(raw_elem.findall("attribute")) if raw_elem is not None else []

        return Anchor(
            mnemonic=self.mnemonic,
            descriptor=self.descriptor,
            identity=self.identity,
            attributes=[
                attr_xml.to_yaml_model(attr_elems[i] if i < len(attr_elems) else None)
                for i, attr_xml in enumerate(self.attributes)
            ],
            identifiers=[i.to_yaml_model() for i in self.identifiers],
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, anchor: Anchor) -> AnchorXML:
        """Convert from YAML Pydantic Anchor model.

        Note: staging_mappings is a YAML-extension field and is NOT exported to XML.
        """
        metadata_elem = MetadataXML() if anchor.metadata_ else None
        description_elem = (
            DescriptionXML(content=anchor.description_) if anchor.description_ else None
        )

        return cls(
            mnemonic=anchor.mnemonic,
            descriptor=anchor.descriptor,
            identity=anchor.identity,
            attributes=[AttributeXML.from_yaml_model(a) for a in anchor.attributes],
            identifiers=[IdentifierXML.from_yaml_model(i) for i in anchor.identifiers],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class KnotXML(BaseXmlModel, tag="knot"):
    """XML model for knot element."""

    mnemonic: str = attr()
    descriptor: str = attr()
    identity: str = attr()
    data_range: str = attr(name="dataRange")

    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Knot:
        """Convert to YAML Pydantic Knot model.

        Args:
            raw_elem: The raw lxml element for extracting metadata attributes.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        return Knot(
            mnemonic=self.mnemonic,
            descriptor=self.descriptor,
            identity=self.identity,
            data_range=self.data_range,
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, knot: Knot) -> KnotXML:
        """Convert from YAML Pydantic Knot model."""
        metadata_elem = MetadataXML() if knot.metadata_ else None
        description_elem = (
            DescriptionXML(content=knot.description_) if knot.description_ else None
        )

        return cls(
            mnemonic=knot.mnemonic,
            descriptor=knot.descriptor,
            identity=knot.identity,
            data_range=knot.data_range,
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class TieXML(BaseXmlModel, tag="tie"):
    """XML model for tie element."""

    time_range: str | None = attr(name="timeRange", default=None)

    roles: list[RoleXML] = element(tag="role", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Tie:
        """Convert to YAML Pydantic Tie model.

        Args:
            raw_elem: The raw lxml element for extracting metadata and child elements.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        # Get child role elements for metadata extraction
        role_elems = list(raw_elem.findall("role")) if raw_elem is not None else []

        return Tie(
            roles=[
                role_xml.to_yaml_model(role_elems[i] if i < len(role_elems) else None)
                for i, role_xml in enumerate(self.roles)
            ],
            time_range=self.time_range,
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, tie: Tie) -> TieXML:
        """Convert from YAML Pydantic Tie model."""
        metadata_elem = MetadataXML() if tie.metadata_ else None
        description_elem = (
            DescriptionXML(content=tie.description_) if tie.description_ else None
        )

        return cls(
            time_range=tie.time_range,
            roles=[RoleXML.from_yaml_model(r) for r in tie.roles],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class NexusXML(BaseXmlModel, tag="nexus"):
    """XML model for nexus element."""

    mnemonic: str = attr()
    descriptor: str = attr()
    identity: str = attr()

    attributes: list[AttributeXML] = element(tag="attribute", default_factory=list)
    roles: list[RoleXML] = element(tag="role", default_factory=list)
    identifiers: list[IdentifierXML] = element(tag="identifier", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Nexus:
        """Convert to YAML Pydantic Nexus model.

        Args:
            raw_elem: The raw lxml element for extracting metadata and child elements.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        # Get child elements for metadata extraction
        attr_elems = list(raw_elem.findall("attribute")) if raw_elem is not None else []
        role_elems = list(raw_elem.findall("role")) if raw_elem is not None else []

        return Nexus(
            mnemonic=self.mnemonic,
            descriptor=self.descriptor,
            identity=self.identity,
            attributes=[
                attr_xml.to_yaml_model(attr_elems[i] if i < len(attr_elems) else None)
                for i, attr_xml in enumerate(self.attributes)
            ],
            roles=[
                role_xml.to_yaml_model(role_elems[i] if i < len(role_elems) else None)
                for i, role_xml in enumerate(self.roles)
            ],
            identifiers=[i.to_yaml_model() for i in self.identifiers],
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, nexus: Nexus) -> NexusXML:
        """Convert from YAML Pydantic Nexus model."""
        metadata_elem = MetadataXML() if nexus.metadata_ else None
        description_elem = (
            DescriptionXML(content=nexus.description_) if nexus.description_ else None
        )

        return cls(
            mnemonic=nexus.mnemonic,
            descriptor=nexus.descriptor,
            identity=nexus.identity,
            attributes=[AttributeXML.from_yaml_model(a) for a in nexus.attributes],
            roles=[RoleXML.from_yaml_model(r) for r in nexus.roles],
            identifiers=[IdentifierXML.from_yaml_model(i) for i in nexus.identifiers],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


class SchemaXML(BaseXmlModel, tag="schema"):
    """XML model for schema element (top-level)."""

    knots: list[KnotXML] = element(tag="knot", default_factory=list)
    anchors: list[AnchorXML] = element(tag="anchor", default_factory=list)
    nexuses: list[NexusXML] = element(tag="nexus", default_factory=list)
    ties: list[TieXML] = element(tag="tie", default_factory=list)
    metadata_elem: MetadataXML | None = element(tag="metadata", default=None)
    layout_elem: LayoutXML | None = element(tag="layout", default=None)
    description_elem: DescriptionXML | None = element(tag="description", default=None)

    def to_yaml_model(self, raw_elem: etree._Element | None = None) -> Spec:
        """Convert to YAML Pydantic Spec model.

        Args:
            raw_elem: The raw lxml element for extracting metadata and child elements.
        """
        metadata_dict = None
        if self.metadata_elem is not None and raw_elem is not None:
            metadata_dict = _extract_metadata_attrs(raw_elem)

        # Get child elements for metadata extraction
        knot_elems = list(raw_elem.findall("knot")) if raw_elem is not None else []
        anchor_elems = list(raw_elem.findall("anchor")) if raw_elem is not None else []
        nexus_elems = list(raw_elem.findall("nexus")) if raw_elem is not None else []
        tie_elems = list(raw_elem.findall("tie")) if raw_elem is not None else []

        return Spec(
            knots=[
                knot_xml.to_yaml_model(knot_elems[i] if i < len(knot_elems) else None)
                for i, knot_xml in enumerate(self.knots)
            ],
            anchors=[
                anchor_xml.to_yaml_model(
                    anchor_elems[i] if i < len(anchor_elems) else None
                )
                for i, anchor_xml in enumerate(self.anchors)
            ],
            nexuses=[
                nexus_xml.to_yaml_model(
                    nexus_elems[i] if i < len(nexus_elems) else None
                )
                for i, nexus_xml in enumerate(self.nexuses)
            ],
            ties=[
                tie_xml.to_yaml_model(tie_elems[i] if i < len(tie_elems) else None)
                for i, tie_xml in enumerate(self.ties)
            ],
            metadata_=metadata_dict,
            layout=None,
            description_=self.description_elem.content
            if self.description_elem
            else None,
        )

    @classmethod
    def from_yaml_model(cls, spec: Spec) -> SchemaXML:
        """Convert from YAML Pydantic Spec model."""
        metadata_elem = MetadataXML() if spec.metadata_ else None
        description_elem = (
            DescriptionXML(content=spec.description_) if spec.description_ else None
        )

        return cls(
            knots=[KnotXML.from_yaml_model(k) for k in spec.knots],
            anchors=[AnchorXML.from_yaml_model(a) for a in spec.anchors],
            nexuses=[NexusXML.from_yaml_model(n) for n in spec.nexuses],
            ties=[TieXML.from_yaml_model(t) for t in spec.ties],
            metadata_elem=metadata_elem,
            layout_elem=None,
            description_elem=description_elem,
        )


def _extract_metadata_attrs(parent_elem: etree._Element) -> dict[str, Any] | None:
    """Extract metadata element attributes from raw lxml element.

    Args:
        parent_elem: Parent element containing metadata child element.

    Returns:
        Dictionary of metadata attributes or None if no metadata found.
    """
    # Find metadata element in the parent
    metadata_elem = parent_elem.find("metadata")
    if metadata_elem is None:
        return None

    # Extract all attributes (xs:anyAttribute pattern)
    # lxml attrib can have str or bytes keys/values, we ensure str
    metadata_dict: dict[str, Any] = {
        (k if isinstance(k, str) else k.decode()): (
            v if isinstance(v, str) else v.decode()
        )
        for k, v in metadata_elem.attrib.items()
    }
    return metadata_dict if metadata_dict else None


def _set_metadata_attrs(
    xml_elem: etree._Element, metadata_dict: dict[str, Any] | None
) -> None:
    """Set metadata attributes on an XML element's metadata child.

    Args:
        xml_elem: The XML element containing metadata child element.
        metadata_dict: Dictionary of metadata attributes to set.
    """
    if metadata_dict is None:
        return

    # Find metadata element - may have namespace or not
    # Try without namespace first, then with namespace
    metadata_elem = xml_elem.find("metadata")
    if metadata_elem is None:
        # Try with Anchor Modeling namespace
        NS = "http://anchormodeling.com/schema"
        metadata_elem = xml_elem.find(f"{{{NS}}}metadata")

    if metadata_elem is None:
        return

    # Set all attributes
    for key, value in metadata_dict.items():
        metadata_elem.set(key, str(value))
