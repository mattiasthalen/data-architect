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


class IdentifierXML(BaseXmlModel, tag="identifier"):
    """XML model for identifier element."""

    route: str = attr()

    def to_yaml_model(self) -> Identifier:
        """Convert to YAML Pydantic Identifier model."""
        return Identifier(route=self.route)


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
