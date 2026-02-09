"""Knot model - shared properties like states or types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from data_architect.models.common import FROZEN_CONFIG, xml_field


class Knot(BaseModel):
    """Knot represents shared properties like states or types.

    Matches anchor.xsd knot element.
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    mnemonic: str = xml_field(description="Unique 2-3 letter code")
    descriptor: str = xml_field(description="Human-readable name")
    identity: str = xml_field(description="SQL data type for identity column")
    data_range: str = xml_field(
        alias="dataRange", description="SQL data type for value column"
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
