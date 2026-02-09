"""Multi-source conflict resolution for anchor staging mappings.

Provides deterministic ordering for staging mappings when multiple source
systems feed the same anchor. Priority is explicit (lower number wins),
with alphabetical tie-breaking for consistency (GEN-08 determinism).
"""

from data_architect.models.staging import StagingMapping


def resolve_staging_order(mappings: list[StagingMapping]) -> list[StagingMapping]:
    """Sort staging mappings deterministically for conflict resolution.

    Ordering rules:
    1. Explicit priority (lower number wins). None treated as lowest priority (999999).
    2. Alphabetical by system name (deterministic tie-breaker).
    3. Alphabetical by tenant name (further tie-breaker).

    Args:
        mappings: List of StagingMapping instances to sort

    Returns:
        Sorted list (highest priority first = lowest priority number first)

    Example:
        >>> from data_architect.models.staging import StagingMapping
        >>> mappings = [
        ...     StagingMapping(
        ...         system='SAP', tenant='EU', table='stg_sap',
        ...         natural_key_columns=['id'], columns=[],
        ...         column_mappings={}
        ...     ),
        ...     StagingMapping(
        ...         system='Northwind', tenant='US', table='stg_nw',
        ...         natural_key_columns=['id'], columns=[],
        ...         column_mappings={}, priority=1
        ...     ),
        ... ]
        >>> result = resolve_staging_order(mappings)
        >>> result[0].system
        'Northwind'
        >>> result[1].system
        'SAP'
    """

    def sort_key(m: StagingMapping) -> tuple[int, str, str]:
        priority = m.priority if m.priority is not None else 999999
        return (priority, m.system, m.tenant)

    return sorted(mappings, key=sort_key)
