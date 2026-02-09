"""Tests for staging mapping models."""

import pytest

from data_architect.models.anchor import Anchor
from data_architect.models.staging import StagingColumn, StagingMapping


def test_staging_column_full():
    """Test StagingColumn with all fields."""
    col = StagingColumn(
        name="customer_name",
        type="VARCHAR(100)",
        maps_to="NM",
    )
    assert col.name == "customer_name"
    assert col.type == "VARCHAR(100)"
    assert col.maps_to == "NM"


def test_staging_column_minimal():
    """Test StagingColumn without maps_to."""
    col = StagingColumn(
        name="id",
        type="BIGINT",
    )
    assert col.name == "id"
    assert col.type == "BIGINT"
    assert col.maps_to is None


def test_staging_column_frozen():
    """Test that StagingColumn is immutable."""
    from pydantic import ValidationError

    col = StagingColumn(name="test", type="INT")
    with pytest.raises(ValidationError):
        col.name = "modified"  # type: ignore[misc]


def test_staging_mapping_full():
    """Test StagingMapping with all fields."""
    mapping = StagingMapping(
        system="ERP",
        tenant="ACME",
        table="stg_customers",
        natural_key_columns=["customer_id"],
        columns=[
            StagingColumn(name="customer_id", type="BIGINT"),
            StagingColumn(name="customer_name", type="VARCHAR(100)", maps_to="NM"),
        ],
        column_mappings={"NM": "customer_name"},
        priority=1,
    )
    assert mapping.system == "ERP"
    assert mapping.tenant == "ACME"
    assert mapping.table == "stg_customers"
    assert mapping.natural_key_columns == ["customer_id"]
    assert len(mapping.columns) == 2
    assert mapping.column_mappings == {"NM": "customer_name"}
    assert mapping.priority == 1


def test_staging_mapping_minimal():
    """Test StagingMapping with minimal required fields."""
    mapping = StagingMapping(
        system="CRM",
        tenant="CORP",
        table="stg_contacts",
        natural_key_columns=["contact_id"],
    )
    assert mapping.system == "CRM"
    assert mapping.tenant == "CORP"
    assert mapping.table == "stg_contacts"
    assert mapping.natural_key_columns == ["contact_id"]
    assert mapping.columns == []
    assert mapping.column_mappings == {}
    assert mapping.priority is None


def test_staging_mapping_composite_key():
    """Test StagingMapping with composite natural key."""
    mapping = StagingMapping(
        system="WMS",
        tenant="ACME",
        table="stg_inventory",
        natural_key_columns=["warehouse_id", "sku"],
    )
    assert mapping.natural_key_columns == ["warehouse_id", "sku"]


def test_staging_mapping_frozen():
    """Test that StagingMapping is immutable."""
    from pydantic import ValidationError

    mapping = StagingMapping(
        system="ERP",
        tenant="ACME",
        table="stg_test",
        natural_key_columns=["id"],
    )
    with pytest.raises(ValidationError):
        mapping.system = "CRM"  # type: ignore[misc]


def test_anchor_staging_mappings_typed():
    """Test that Anchor.staging_mappings accepts list[StagingMapping]."""
    mapping = StagingMapping(
        system="ERP",
        tenant="ACME",
        table="stg_customers",
        natural_key_columns=["customer_id"],
    )

    anchor = Anchor(
        mnemonic="CU",
        descriptor="Customer",
        identity="BIGINT",
        staging_mappings=[mapping],
    )

    assert len(anchor.staging_mappings) == 1
    assert isinstance(anchor.staging_mappings[0], StagingMapping)
    assert anchor.staging_mappings[0].system == "ERP"


def test_anchor_staging_mappings_empty():
    """Test Anchor with empty staging_mappings."""
    anchor = Anchor(
        mnemonic="CU",
        descriptor="Customer",
        identity="BIGINT",
    )
    assert anchor.staging_mappings == []


def test_staging_mapping_column_mapping_usage():
    """Test column_mappings separate from columns list."""
    # columns define DDL structure
    # column_mappings define DML lineage
    mapping = StagingMapping(
        system="ERP",
        tenant="ACME",
        table="stg_customers",
        natural_key_columns=["cust_id"],
        columns=[
            StagingColumn(name="cust_id", type="BIGINT"),
            StagingColumn(name="cust_name", type="VARCHAR(100)"),
            StagingColumn(name="cust_email", type="VARCHAR(255)"),
        ],
        column_mappings={
            "NM": "cust_name",  # Attribute NM maps to staging column cust_name
            "EM": "cust_email",  # Attribute EM maps to staging column cust_email
        },
    )

    # DDL uses mapping.columns
    assert len(mapping.columns) == 3
    assert mapping.columns[0].name == "cust_id"

    # DML uses mapping.column_mappings
    assert mapping.column_mappings["NM"] == "cust_name"
    assert mapping.column_mappings["EM"] == "cust_email"
