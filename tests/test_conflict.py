"""Tests for multi-source conflict resolution."""

from data_architect.generation.conflict import resolve_staging_order
from data_architect.models.staging import StagingMapping


def test_resolve_staging_order_single_mapping():
    """Single mapping returns as-is."""
    mapping = StagingMapping(
        system="ERP",
        tenant="ACME",
        table="stg_customers",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
    )

    result = resolve_staging_order([mapping])

    assert len(result) == 1
    assert result[0].system == "ERP"


def test_resolve_staging_order_priority_wins():
    """Lower priority number comes first."""
    mapping_high = StagingMapping(
        system="SAP",
        tenant="EU",
        table="stg_sap",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )
    mapping_low = StagingMapping(
        system="Northwind",
        tenant="US",
        table="stg_nw",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=5,
    )

    result = resolve_staging_order([mapping_low, mapping_high])

    assert len(result) == 2
    assert result[0].system == "SAP"
    assert result[1].system == "Northwind"


def test_resolve_staging_order_none_priority_last():
    """Mapping with None priority comes after explicit priority."""
    mapping_explicit = StagingMapping(
        system="Northwind",
        tenant="US",
        table="stg_nw",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )
    mapping_none = StagingMapping(
        system="SAP",
        tenant="EU",
        table="stg_sap",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
    )

    result = resolve_staging_order([mapping_none, mapping_explicit])

    assert len(result) == 2
    assert result[0].system == "Northwind"
    assert result[1].system == "SAP"


def test_resolve_staging_order_alphabetical_tiebreaker():
    """When priority is same, alphabetical by system name."""
    mapping_z = StagingMapping(
        system="Zebra",
        tenant="US",
        table="stg_z",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )
    mapping_a = StagingMapping(
        system="Alpha",
        tenant="US",
        table="stg_a",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )

    result = resolve_staging_order([mapping_z, mapping_a])

    assert len(result) == 2
    assert result[0].system == "Alpha"
    assert result[1].system == "Zebra"


def test_resolve_staging_order_three_mappings_mixed():
    """Three mappings with mixed priority and None."""
    mapping_p1 = StagingMapping(
        system="High",
        tenant="US",
        table="stg_high",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )
    mapping_p2 = StagingMapping(
        system="Medium",
        tenant="US",
        table="stg_med",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=5,
    )
    mapping_none = StagingMapping(
        system="Low",
        tenant="US",
        table="stg_low",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
    )

    result = resolve_staging_order([mapping_none, mapping_p2, mapping_p1])

    assert len(result) == 3
    assert result[0].system == "High"
    assert result[1].system == "Medium"
    assert result[2].system == "Low"


def test_resolve_staging_order_deterministic():
    """Calling twice returns identical order."""
    mappings = [
        StagingMapping(
            system="SAP",
            tenant="EU",
            table="stg_sap",
            natural_key_columns=["id"],
            columns=[],
            column_mappings={},
        ),
        StagingMapping(
            system="Northwind",
            tenant="US",
            table="stg_nw",
            natural_key_columns=["id"],
            columns=[],
            column_mappings={},
            priority=1,
        ),
    ]

    result1 = resolve_staging_order(mappings)
    result2 = resolve_staging_order(mappings)

    # Compare systems in order
    systems1 = [m.system for m in result1]
    systems2 = [m.system for m in result2]

    assert systems1 == systems2


def test_resolve_staging_order_tenant_tiebreaker():
    """When priority and system are same, tenant breaks tie."""
    mapping_z = StagingMapping(
        system="ERP",
        tenant="ZuluCorp",
        table="stg_z",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )
    mapping_a = StagingMapping(
        system="ERP",
        tenant="AcmeCorp",
        table="stg_a",
        natural_key_columns=["id"],
        columns=[],
        column_mappings={},
        priority=1,
    )

    result = resolve_staging_order([mapping_z, mapping_a])

    assert len(result) == 2
    assert result[0].tenant == "AcmeCorp"
    assert result[1].tenant == "ZuluCorp"
