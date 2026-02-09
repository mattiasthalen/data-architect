"""Common types and utilities for spec models."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SchemaLayer(StrEnum):
    """Three-layer schema tagging for XML interoperability.

    XML_CORE: Fields from anchor.xsd specification (always exported)
    YAML_EXT: YAML extension fields (may need conversion for export)
    INTERNAL: Internal-only fields (never exported)
    """

    XML_CORE = "xml-core"
    YAML_EXT = "yaml-ext"
    INTERNAL = "internal"


def xml_field(
    default: Any = ...,
    *,
    alias: str | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> Any:
    """Create a Field marked as XML-core layer."""
    return Field(
        default,
        alias=alias,
        description=description,
        json_schema_extra={"layer": SchemaLayer.XML_CORE.value},
        **kwargs,
    )


def yaml_ext_field(
    default: Any = ...,
    *,
    alias: str | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> Any:
    """Create a Field marked as YAML-extension layer."""
    return Field(
        default,
        alias=alias,
        description=description,
        json_schema_extra={"layer": SchemaLayer.YAML_EXT.value},
        **kwargs,
    )


def internal_field(
    default: Any = ...,
    *,
    alias: str | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> Any:
    """Create a Field marked as internal layer."""
    return Field(
        default,
        alias=alias,
        description=description,
        json_schema_extra={"layer": SchemaLayer.INTERNAL.value},
        **kwargs,
    )


# Base config for all frozen models
FROZEN_CONFIG = ConfigDict(frozen=True, populate_by_name=True)


class Key(BaseModel):
    """Key element from anchor.xsd - used in attributes and roles."""

    model_config = FROZEN_CONFIG

    stop: str = xml_field(description="Stop position in route")
    route: str = xml_field(description="Route name")
    of_: str = xml_field(alias="of", description="Reference to anchor or nexus")
    branch: str = xml_field(default="1", description="Branch identifier")


class Identifier(BaseModel):
    """Identifier element from anchor.xsd - used in anchors and nexuses."""

    model_config = FROZEN_CONFIG

    route: str = xml_field(description="Route name for this identifier")
