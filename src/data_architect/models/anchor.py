"""Anchor and Attribute models - entities and their properties."""

from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, model_validator

from data_architect.models.common import (
    FROZEN_CONFIG,
    Identifier,
    Key,
    xml_field,
    yaml_ext_field,
)


class Attribute(BaseModel):
    """Attribute represents a property of an anchor or nexus.

    Matches anchor.xsd attribute element.
    Enforces exactly-one-of knotRange/dataRange per anchor.xsd assertion.
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    mnemonic: str = xml_field(description="Unique 2-3 letter code")
    descriptor: str = xml_field(description="Human-readable name")
    knot_range: str | None = xml_field(
        default=None, alias="knotRange", description="Reference to knot mnemonic"
    )
    data_range: str | None = xml_field(
        default=None, alias="dataRange", description="SQL data type"
    )
    time_range: str | None = xml_field(
        default=None,
        alias="timeRange",
        description="SQL data type for temporal tracking",
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

    # YAML-extension fields
    staging_column: str | None = yaml_ext_field(
        default=None, description="Column name in staging table"
    )

    @model_validator(mode="after")
    def check_exactly_one_range(self) -> Self:
        """Enforce exactly one of knotRange or dataRange (anchor.xsd assertion)."""
        has_knot = self.knot_range is not None
        has_data = self.data_range is not None

        if has_knot == has_data:  # Both True or both False
            msg = "Attribute must have exactly one of knotRange or dataRange"
            raise ValueError(msg)

        return self


class Anchor(BaseModel):
    """Anchor represents an entity or event in the domain.

    Matches anchor.xsd anchor element.
    """

    model_config = FROZEN_CONFIG

    # XML-core fields
    mnemonic: str = xml_field(description="Unique 2-3 letter code")
    descriptor: str = xml_field(description="Human-readable name")
    identity: str = xml_field(description="SQL data type for identity column")
    attributes: list[Attribute] = xml_field(
        default_factory=list, alias="attribute", description="List of attributes"
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

    # YAML-extension fields
    staging_mappings: list[StagingMapping] = yaml_ext_field(
        default_factory=list, description="Staging table mappings (Phase 8)"
    )


# Import after class definitions to avoid circular import
from data_architect.models.staging import StagingMapping  # noqa: E402, TC001

# Rebuild model with the now-available StagingMapping type
Anchor.model_rebuild()
