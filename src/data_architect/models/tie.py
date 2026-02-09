"""Tie and Role models - relationships between anchors."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from data_architect.models.common import FROZEN_CONFIG, Key, xml_field


class Role(BaseModel):
    """Role represents a participant in a tie or nexus.

    Matches anchor.xsd role element (unified role model).
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    role: str = xml_field(description="Role name (e.g., 'wasCast', 'in')")
    type_: str = xml_field(
        alias="type", description="Reference to anchor, nexus, or knot mnemonic"
    )
    identifier: bool = xml_field(
        default=False, description="Whether this role is part of the identifier"
    )
    coloring: str | None = xml_field(
        default=None, description="Optional coloring attribute"
    )
    keys: list[Key] = xml_field(
        default_factory=list, alias="key", description="Key definitions"
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


class Tie(BaseModel):
    """Tie represents a relationship between anchors.

    Matches anchor.xsd tie element.
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    roles: list[Role] = xml_field(alias="role", description="List of roles (minimum 2)")
    time_range: str | None = xml_field(
        default=None,
        alias="timeRange",
        description="SQL data type for temporal tracking",
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
