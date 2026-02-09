"""Staging mapping models - multi-source configuration for anchor loading."""

from __future__ import annotations

from pydantic import BaseModel

from data_architect.models.common import FROZEN_CONFIG, yaml_ext_field


class StagingColumn(BaseModel):
    """Maps a staging table column to an anchor attribute."""

    model_config = FROZEN_CONFIG

    name: str = yaml_ext_field(description="Source column name in staging table")
    type: str = yaml_ext_field(description="SQL data type")
    maps_to: str | None = yaml_ext_field(
        default=None, description="Target attribute mnemonic"
    )


class StagingMapping(BaseModel):
    """Multi-source mapping from a staging table to an anchor."""

    model_config = FROZEN_CONFIG

    system: str = yaml_ext_field(description="Source system identifier")
    tenant: str = yaml_ext_field(description="Tenant identifier")
    table: str = yaml_ext_field(description="Staging table name")
    natural_key_columns: list[str] = yaml_ext_field(
        description="Columns composing natural key"
    )
    columns: list[StagingColumn] = yaml_ext_field(
        default_factory=list, description="Column definitions with mappings"
    )
    column_mappings: dict[str, str] = yaml_ext_field(
        default_factory=dict,
        description="attribute_mnemonic -> staging_column_name",
    )
    priority: int | None = yaml_ext_field(
        default=None, description="Conflict resolution priority (lower wins)"
    )
