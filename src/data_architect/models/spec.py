"""Top-level Spec model and Nexus model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from data_architect.models.anchor import Anchor, Attribute
from data_architect.models.common import FROZEN_CONFIG, Identifier, xml_field
from data_architect.models.knot import Knot
from data_architect.models.tie import Role, Tie


class Nexus(BaseModel):
    """Nexus represents a first-class entity with attributes and roles.

    Matches anchor.xsd nexus element (introduced in 2025-09-25 update).
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    mnemonic: str = xml_field(description="Unique 2-3 letter code")
    descriptor: str = xml_field(description="Human-readable name")
    identity: str = xml_field(description="SQL data type for identity column")
    attributes: list[Attribute] = xml_field(
        default_factory=list, alias="attribute", description="List of attributes"
    )
    roles: list[Role] = xml_field(
        default_factory=list, alias="role", description="List of roles"
    )
    identifiers: list[Identifier] = xml_field(
        default_factory=list, alias="identifier", description="List of identifiers"
    )

    # Optional construct fields
    metadata_: dict[str, Any] | None = xml_field(
        default=None, alias="metadata", description="Metadata attributes"
    )
    layout: Any | None = xml_field(
        default=None, description="Visual layout information"
    )
    description_: str | None = xml_field(
        default=None, alias="description", description="Textual description"
    )


class Spec(BaseModel):
    """Top-level specification containing all Anchor Model entities.

    Matches anchor.xsd schema element.
    """

    model_config = FROZEN_CONFIG

    # Entity collections
    anchors: list[Anchor] = xml_field(
        default_factory=list, alias="anchor", description="List of anchors"
    )
    knots: list[Knot] = xml_field(
        default_factory=list, alias="knot", description="List of knots"
    )
    ties: list[Tie] = xml_field(
        default_factory=list, alias="tie", description="List of ties"
    )
    nexuses: list[Nexus] = xml_field(
        default_factory=list, alias="nexus", description="List of nexuses"
    )

    # Optional construct fields
    metadata_: dict[str, Any] | None = xml_field(
        default=None, alias="metadata", description="Metadata attributes"
    )
    layout: Any | None = xml_field(
        default=None, description="Visual layout information"
    )
    description_: str | None = xml_field(
        default=None, alias="description", description="Textual description"
    )
