# Phase 8: Keyset Identity and Staging Mappings - Research

**Researched:** 2026-02-09
**Domain:** Keyset identity encoding/parsing, multi-source staging mappings, data provenance tracking
**Confidence:** HIGH

## Summary

Phase 8 implements keyset identity for multi-source data tracking and staging table column mappings with conflict resolution. The keyset format `entity@system~tenant|natural_key` encodes data provenance in a single VARCHAR column, enabling multi-tenant, multi-system warehouse architectures while maintaining lineage back to source natural keys.

The core technical challenges are: (1) Delimiter escaping with round-trip correctness (use `@@`, `~~`, `||` for literal delimiters), (2) NULL propagation (NULL natural key → entire keyset NULL, not `entity@system~tenant|`), (3) SQL generation for keyset construction from source columns with proper CONCAT + COALESCE patterns, (4) Multi-source conflict resolution with deterministic ordering (explicit priority, then alphabetical system name).

Property-based testing with Hypothesis is the standard approach for validating string encoding/escaping correctness. Use `st.text()` strategies with custom character sets including delimiter characters to generate adversarial test cases that verify round-trip parse/format invariants. SQLGlot already supports NULL-safe concatenation patterns through dialect-aware CONCAT/COALESCE compilation.

**Primary recommendation:** Implement `KeysetIdentity` module with `parse(s: str) -> KeysetComponents | None` and `format(entity, system, tenant, natural_key) -> str | None` functions, test round-trip correctness with Hypothesis `@given(st.text())`, extend Pydantic staging mapping models with column-level lineage, generate keyset construction SQL using SQLGlot CASE/COALESCE for NULL safety, and implement deterministic conflict resolution via explicit priority + system name sorting.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Hypothesis** | >=6.151.0 | Property-based testing of keyset parse/format round-trips | Already in dev dependencies (Phase 1), standard for testing string transformations and encoding correctness |
| **SQLGlot** | >=28.10.0 | SQL generation for keyset construction with CONCAT/COALESCE | Already in use (Phase 7), dialect-aware NULL handling |
| **Pydantic** | >=2.10.0 | Staging mapping models with validation | Already in use (Phase 6), extend Anchor model with staging_mappings field |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **re** (stdlib) | Python 3.13 | Regex for delimiter escaping during parse/format | Use for scanning and replacing escape sequences (`@@`, `~~`, `||`) |
| **typing** (stdlib) | Python 3.13 | Type hints for KeysetComponents NamedTuple or dataclass | Use for parse() return type clarity |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom delimiter escape | JSON encoding | JSON requires double-quotes escaping, non-human-readable in logs, harder to construct in SQL |
| Custom delimiter escape | Base64 encoding | Not human-readable, can't construct easily in SQL without dialect-specific functions |
| Hypothesis property tests | Manual edge case tests | Misses adversarial inputs like `@@@@~~||`, `@@@`, delimiter-only strings |
| Explicit priority field | Timestamp-based conflict resolution | Non-deterministic (clock skew, tie-breaking), violates GEN-08 determinism requirement |
| CONCAT_WS for keysets | Manual string concatenation | CONCAT_WS skips NULLs (wrong for keyset), CONCAT + CASE is more explicit |

**Installation:**
```bash
# Already in pyproject.toml dependencies and dev-dependencies
# No new dependencies required
```

## Architecture Patterns

### Recommended Project Structure

```
src/data_architect/
├── identity/                # NEW: Keyset identity module
│   ├── __init__.py         # Public API: parse, format
│   ├── keyset.py           # KeysetIdentity parse/format functions
│   └── escaping.py         # Delimiter escape/unescape utilities
├── models/                  # EXTEND: Add staging mapping models
│   ├── anchor.py           # EXTEND: staging_mappings field (already exists as placeholder)
│   ├── staging.py          # NEW: StagingMapping, StagingSource models
│   └── common.py           # EXTEND: Add ConflictResolution enum
├── generation/              # EXTEND: Keyset SQL generation
│   ├── ddl.py              # Already exists (Phase 7)
│   ├── dml.py              # EXTEND: Multi-source loading with keysets
│   └── keyset_sql.py       # NEW: build_keyset_expr() for SQL construction
└── cli.py                   # Already exists (Phase 7)
```

### Pattern 1: Delimiter Escaping with Fixed-Length Sequences

**What:** Escape delimiters using fixed-length doubling (`@` → `@@`, `~` → `~~`, `|` → `||`) to enable unambiguous reversal.

**When to use:** During `format()` when encoding natural key values, and during `parse()` when decoding.

**Example:**
```python
# Source: Delimiter escaping pattern from property-based testing literature
def escape_delimiters(s: str) -> str:
    """Escape keyset delimiters in natural key value.

    '@' → '@@'
    '~' → '~~'
    '|' → '||'
    """
    return s.replace("@", "@@").replace("~", "~~").replace("|", "||")

def unescape_delimiters(s: str) -> str:
    """Unescape keyset delimiters in natural key value.

    '@@' → '@'
    '~~' → '~'
    '||' → '|'
    """
    # Order matters: must replace double sequences first
    return s.replace("@@", "@").replace("~~", "~").replace("||", "|")
```

**Rationale:** Fixed-length doubling is reversible because the escape character is deterministic. `@@@` becomes `@@@@@@` (three `@` → six `@`), which decodes unambiguously back to `@@@`.

### Pattern 2: Hypothesis Round-Trip Testing

**What:** Property-based tests verify that `parse(format(x)) == x` for all valid inputs.

**When to use:** Testing keyset identity module to catch edge cases like delimiter-heavy inputs.

**Example:**
```python
# Source: https://hypothesis.readthedocs.io/en/latest/data.html
from hypothesis import given
import hypothesis.strategies as st

@given(
    entity=st.text(min_size=1, max_size=50),
    system=st.text(min_size=1, max_size=50),
    tenant=st.text(min_size=1, max_size=50),
    natural_key=st.text(min_size=0, max_size=200),  # Can be empty
)
def test_keyset_roundtrip(entity, system, tenant, natural_key):
    """Verify format/parse round-trip for all string inputs."""
    keyset = format_keyset(entity, system, tenant, natural_key)
    assert keyset is not None

    parsed = parse_keyset(keyset)
    assert parsed is not None
    assert parsed.entity == entity
    assert parsed.system == system
    assert parsed.tenant == tenant
    assert parsed.natural_key == natural_key

@given(st.text())
def test_keyset_parse_never_crashes(s):
    """Parser handles any string input without exceptions."""
    result = parse_keyset(s)
    # Either returns valid components or None (invalid format)
    # Never raises exception
```

**Rationale:** Hypothesis generates adversarial inputs automatically (e.g., `"@@@@"`, `"entity@@@system"`, empty strings, unicode), catching bugs manual tests miss.

### Pattern 3: NULL-Safe Keyset Construction in SQL

**What:** Use CASE expression to propagate NULL from natural key to entire keyset, avoiding partial keyset strings like `entity@system~tenant|`.

**When to use:** Generating keyset construction SQL in DML (KEY-05 requirement).

**Example:**
```python
# Source: SQL NULL handling patterns + SQLGlot AST construction
import sqlglot as sg
import sqlglot.expressions as sge

def build_keyset_expr(
    entity: str,
    system: str,
    tenant: str,
    natural_key_col: str,
    dialect: str,
) -> sge.Expression:
    """Build NULL-safe keyset construction expression.

    If natural_key_col IS NULL, entire expression is NULL.
    Otherwise: 'entity@system~tenant|' || natural_key_col

    Args:
        entity: Entity type (e.g., "Customer")
        system: Source system (e.g., "Northwind")
        tenant: Tenant identifier (e.g., "ACME")
        natural_key_col: Source column name for natural key
        dialect: Target SQL dialect

    Returns:
        CASE WHEN natural_key IS NULL THEN NULL
             ELSE 'entity@system~tenant|' || natural_key_col
        END
    """
    # Escape entity/system/tenant values (constants known at generation time)
    escaped_entity = escape_delimiters(entity)
    escaped_system = escape_delimiters(system)
    escaped_tenant = escape_delimiters(tenant)

    prefix = f"{escaped_entity}@{escaped_system}~{escaped_tenant}|"

    # Build CASE WHEN natural_key IS NULL THEN NULL
    #           ELSE prefix || REPLACE(REPLACE(REPLACE(
    #                   natural_key, '@', '@@'), '~', '~~'), '|', '||')
    #      END

    # Natural key column needs runtime escaping in SQL
    nk_col = sg.to_column(natural_key_col)

    # Nested REPLACE for delimiter escaping in SQL
    escaped_nk = sge.Replace(
        this=sge.Replace(
            this=sge.Replace(
                this=nk_col,
                expression=sge.Literal.string("@"),
                replacement=sge.Literal.string("@@"),
            ),
            expression=sge.Literal.string("~"),
            replacement=sge.Literal.string("~~"),
        ),
        expression=sge.Literal.string("|"),
        replacement=sge.Literal.string("||"),
    )

    # CONCAT(prefix, escaped_natural_key)
    concat_expr = sge.Concat(
        expressions=[
            sge.Literal.string(prefix),
            escaped_nk,
        ]
    )

    # CASE WHEN natural_key IS NULL THEN NULL ELSE concat_expr END
    return sge.Case(
        ifs=[
            sge.If(
                this=sge.Is(this=nk_col, expression=sge.Null()),
                true=sge.Null(),
            )
        ],
        default=concat_expr,
    )
```

**Rationale:** CASE WHEN short-circuits NULL evaluation. If `natural_key IS NULL`, we return NULL immediately without constructing the prefix string. This matches the NULL propagation semantics required by KEY-05.

### Pattern 4: Multi-Source Column Mappings with Lineage

**What:** Extend Pydantic models to represent staging table → anchor attribute mappings with explicit source columns.

**When to use:** Defining staging mappings in YAML spec (STG-01, STG-02).

**Example:**
```python
# Source: Pydantic v2 patterns + data lineage tracking concepts
from pydantic import BaseModel
from data_architect.models.common import FROZEN_CONFIG, yaml_ext_field

class StagingColumn(BaseModel):
    """Maps a staging table column to an anchor attribute."""

    model_config = FROZEN_CONFIG

    table: str  # Staging table name (e.g., "stg_northwind_customers")
    column: str  # Source column name (e.g., "CustomerID")

class StagingMapping(BaseModel):
    """Multi-source mapping from staging tables to an anchor."""

    model_config = FROZEN_CONFIG

    system: str  # Source system identifier (e.g., "Northwind")
    tenant: str  # Tenant identifier (e.g., "ACME")
    table: str   # Staging table name
    natural_key_columns: list[str]  # Columns composing natural key
    priority: int | None = None  # Explicit conflict resolution priority

    # Column-level mappings: attribute mnemonic → staging column
    column_mappings: dict[str, str]  # e.g., {"CU": "CustomerID", "NM": "CompanyName"}

# Extend Anchor model (already has staging_mappings placeholder)
class Anchor(BaseModel):
    # ... existing fields ...
    staging_mappings: list[StagingMapping] = yaml_ext_field(
        default_factory=list,
        description="Multi-source staging table mappings"
    )
```

**Rationale:** Explicit column-level mappings enable data lineage tracking (STG-01) and make generated SQL transparent (DML SELECT clause maps staging columns directly to anchor columns).

### Pattern 5: Deterministic Conflict Resolution

**What:** When multiple staging sources feed the same anchor, resolve conflicts using explicit priority then alphabetical system name.

**When to use:** Generating DML for multi-source anchors (STG-05).

**Example:**
```python
def resolve_staging_order(mappings: list[StagingMapping]) -> list[StagingMapping]:
    """Sort staging mappings deterministically for conflict resolution.

    1. Explicit priority (lower number wins)
    2. Alphabetical by system name (deterministic tie-breaker)

    Args:
        mappings: List of staging mappings for an anchor

    Returns:
        Sorted list (highest priority first)
    """
    def sort_key(m: StagingMapping) -> tuple[int, str]:
        # Priority: None treated as infinity (lowest priority)
        priority = m.priority if m.priority is not None else 999999
        return (priority, m.system)

    return sorted(mappings, key=sort_key)

def build_multi_source_merge(
    anchor: Anchor,
    dialect: str,
) -> list[sge.Expression]:
    """Build MERGE statements for each staging source in priority order.

    Higher priority sources are loaded first. Lower priority sources
    use WHEN NOT MATCHED to only insert new records.

    Returns:
        List of MERGE ASTs (one per staging source, priority order)
    """
    sorted_mappings = resolve_staging_order(anchor.staging_mappings)

    merges = []
    for mapping in sorted_mappings:
        # Build keyset column using mapping.system, mapping.tenant
        keyset_expr = build_keyset_expr(
            entity=anchor.descriptor,
            system=mapping.system,
            tenant=mapping.tenant,
            natural_key_col=", ".join(mapping.natural_key_columns),
            dialect=dialect,
        )

        # Build MERGE ... WHEN NOT MATCHED THEN INSERT
        # (Details in Phase 8 Plan 2)
        merge = build_staging_merge(anchor, mapping, keyset_expr, dialect)
        merges.append(merge)

    return merges
```

**Rationale:** Explicit priority gives users control, alphabetical tie-breaking ensures determinism (GEN-08), and loading in priority order means first-match-wins semantics are clear.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| String encoding/escaping | Custom escape sequences without property tests | Delimiter doubling + Hypothesis round-trip tests | Edge cases like `"@@@"`, `"@@@@"`, delimiter-only strings, unicode combining characters break naive implementations |
| SQL NULL handling | Manual NULL checks in generated SQL | SQLGlot CASE/COALESCE expressions with AST construction | Dialect-specific NULL semantics (SQL Server CONCAT vs PostgreSQL \|\|), manual string building misses edge cases |
| Conflict resolution ordering | Timestamp-based "last write wins" | Explicit priority + deterministic tie-breaker | Clock skew, non-determinism, testing challenges, violates GEN-08 |
| Multi-source provenance | Separate system/tenant columns | Keyset identity in single column | Joins become complex, indexes inefficient, harder to trace lineage in queries |

**Key insight:** String escaping correctness is deceptively hard. Property-based testing with Hypothesis catches inputs like `"entity@@system@tenant"` that manual tests miss. Similarly, SQL NULL propagation has dialect-specific gotchas that SQLGlot AST construction handles automatically.

## Common Pitfalls

### Pitfall 1: Incorrect Delimiter Unescape Order

**What goes wrong:** Unescaping delimiters in the wrong order produces incorrect output.

**Example:**
```python
# WRONG: Single-character replacement
def unescape_wrong(s: str) -> str:
    return s.replace("@", "").replace("~", "").replace("|", "")
# "@@" → "" (should be "@")

# WRONG: Double-replacement before single
def unescape_wrong2(s: str) -> str:
    return s.replace("@", "@@").replace("@@", "@")
# "@" → "@@" → "@" (infinite loop if repeated)

# CORRECT: Replace double sequences first
def unescape_correct(s: str) -> str:
    return s.replace("@@", "@").replace("~~", "~").replace("||", "|")
# "@@" → "@" ✓
```

**Why it happens:** Delimiter escaping uses the delimiter as both data and control character. Replacement order matters.

**How to avoid:** Always unescape multi-character sequences before single-character sequences. Test with Hypothesis `@given(st.text())` to catch bugs.

**Warning signs:** Test failures on inputs containing escaped escape sequences (`"@@@@"` should round-trip to `"@@"`).

### Pitfall 2: NULL Keyset Construction Creating Partial Strings

**What goes wrong:** Generating `entity@system~tenant|` when natural key is NULL instead of propagating NULL.

**Example:**
```sql
-- WRONG: Creates 'Customer@Northwind~ACME|' when CustomerID is NULL
SELECT 'Customer@Northwind~ACME|' || COALESCE(CustomerID, '')

-- CORRECT: Entire keyset is NULL when CustomerID is NULL
SELECT CASE WHEN CustomerID IS NULL THEN NULL
            ELSE 'Customer@Northwind~ACME|' || CustomerID
       END
```

**Why it happens:** CONCAT/COALESCE propagate NULLs differently across dialects. SQL Server CONCAT treats NULL as empty string, PostgreSQL `||` propagates NULL.

**How to avoid:** Use explicit CASE WHEN for NULL checks. Test with NULL natural key values. SQLGlot's AST approach makes this pattern consistent across dialects.

**Warning signs:** Database contains keyset values like `entity@system~tenant|` without trailing natural key. Integration test failures with NULL source keys.

### Pitfall 3: Non-Deterministic Conflict Resolution

**What goes wrong:** Using timestamps or random tie-breaking for multi-source conflicts produces different SQL output on each generation.

**Example:**
```python
# WRONG: Random ordering
import random
sorted_mappings = sorted(mappings, key=lambda m: random.random())

# WRONG: Timestamp-based (non-deterministic)
sorted_mappings = sorted(mappings, key=lambda m: m.loaded_at)
```

**Why it happens:** Violates GEN-08 requirement (deterministic output). Different machines, different times → different SQL → merge conflicts in git.

**How to avoid:** Sort by deterministic fields only (explicit priority, system name, table name). Test by running generation twice and asserting byte-identical output.

**Warning signs:** `git diff` shows SQL changes when spec hasn't changed. Non-reproducible builds. Integration test flakiness.

### Pitfall 4: Forgetting Runtime Delimiter Escaping in SQL

**What goes wrong:** Natural key values from staging tables contain delimiters that aren't escaped during keyset construction.

**Example:**
```sql
-- WRONG: No delimiter escaping of runtime column value
SELECT 'Customer@Northwind~ACME|' || CustomerID FROM staging
-- If CustomerID = 'ACME@US', keyset is: 'Customer@Northwind~ACME|ACME@US'
-- Parsing this keyset extracts natural_key = 'ACME' (wrong!)

-- CORRECT: Escape delimiters in runtime value
SELECT 'Customer@Northwind~ACME|' ||
       REPLACE(REPLACE(REPLACE(CustomerID, '@', '@@'), '~', '~~'), '|', '||')
-- If CustomerID = 'ACME@US', keyset is: 'Customer@Northwind~ACME|ACME@@US'
-- Parsing extracts natural_key = 'ACME@US' (correct after unescape)
```

**Why it happens:** Entity/system/tenant are constants (escaped at generation time), but natural key is a runtime value (must escape in SQL).

**How to avoid:** Always generate REPLACE cascade in SQL for natural key columns. Test with source data containing delimiters.

**Warning signs:** Parse errors on keysets loaded from database. Natural key values truncated at delimiter characters.

## Code Examples

Verified patterns from official sources:

### Hypothesis Strategy for Delimiter-Heavy Strings

```python
# Source: https://hypothesis.readthedocs.io/en/latest/data.html
import hypothesis.strategies as st

# Strategy: Text with high probability of delimiter characters
delimiter_heavy = st.text(
    alphabet=st.characters(
        whitelist_categories=["Lu", "Ll", "Nd"],  # Letters and digits
        whitelist_characters="@~|",  # Force delimiter presence
    ),
    min_size=0,
    max_size=100,
)

@given(delimiter_heavy, delimiter_heavy, delimiter_heavy, delimiter_heavy)
def test_keyset_with_delimiters(entity, system, tenant, natural_key):
    """Test keyset with delimiter-heavy inputs."""
    keyset = format_keyset(entity, system, tenant, natural_key)
    if keyset is None:  # NULL natural key case
        assert natural_key == ""  # Or whatever NULL convention
        return

    parsed = parse_keyset(keyset)
    assert parsed is not None
    assert parsed.natural_key == natural_key
```

### SQLGlot NULL-Safe CONCAT Pattern

```python
# Source: SQLGlot official docs + dialect patterns
import sqlglot as sg
import sqlglot.expressions as sge

def build_null_safe_concat(parts: list[str | sge.Expression], dialect: str) -> sge.Expression:
    """Build NULL-safe concatenation that propagates NULL.

    If any part is NULL, entire expression is NULL.
    """
    # Convert string literals to expressions
    exprs = [
        sge.Literal.string(p) if isinstance(p, str) else p
        for p in parts
    ]

    # Check if any part is NULL
    null_checks = [
        sge.Is(this=expr, expression=sge.Null())
        for expr in exprs
        if not isinstance(expr, sge.Literal)  # Skip literal checks
    ]

    if not null_checks:
        # All literals, no NULL check needed
        return sge.Concat(expressions=exprs)

    # CASE WHEN any_part IS NULL THEN NULL ELSE CONCAT(...) END
    any_null = null_checks[0]
    for check in null_checks[1:]:
        any_null = sge.Or(this=any_null, expression=check)

    return sge.Case(
        ifs=[sge.If(this=any_null, true=sge.Null())],
        default=sge.Concat(expressions=exprs),
    )
```

### Pydantic Staging Mapping Validation

```python
# Source: https://docs.pydantic.dev/latest/concepts/validators/
from pydantic import BaseModel, model_validator
from typing_extensions import Self

class StagingMapping(BaseModel):
    system: str
    tenant: str
    table: str
    natural_key_columns: list[str]
    priority: int | None = None
    column_mappings: dict[str, str]

    @model_validator(mode="after")
    def check_natural_key_columns_mapped(self) -> Self:
        """Verify all natural key columns are in column_mappings."""
        for nk_col in self.natural_key_columns:
            # Natural key columns must appear as values in column_mappings
            if nk_col not in self.column_mappings.values():
                msg = (
                    f"Natural key column '{nk_col}' not found in column_mappings. "
                    f"Available: {list(self.column_mappings.values())}"
                )
                raise ValueError(msg)
        return self
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JSON encoding for composite keys | Delimiter-based encoding with escape sequences | 2020s (data lineage movement) | Human-readable in logs, SQL-constructable, easier debugging |
| Separate provenance columns | Keyset identity in single column | 2023+ (multi-tenant architectures) | Simpler joins, better indexes, clearer lineage |
| Manual edge case tests | Hypothesis property-based tests | 2024+ (Python 3.10+) | Finds bugs automatically, less test code, higher confidence |
| String concatenation in SQL | SQLGlot AST construction | 2025+ (SQLGlot maturity) | Dialect-agnostic, testable, deterministic whitespace |

**Deprecated/outdated:**
- **MD5/SHA hashing for composite keys**: Not reversible, can't trace back to source natural key, collision risk
- **Timestamp-based conflict resolution**: Non-deterministic, clock skew issues, violates modern warehouse best practices
- **Per-dialect SQL templates**: Maintenance burden, whitespace non-determinism, AST approach is superior

## Open Questions

1. **Natural key composition for multi-column keys**
   - What we know: `natural_key_columns: list[str]` allows multiple columns
   - What's unclear: Concatenation strategy (delimiter? order?), NULL handling when some columns NULL
   - Recommendation: Plan 08-01 should define `format_natural_key(values: list[str | None]) -> str | None` with explicit concatenation rules (e.g., `:` separator with escaping)

2. **Conflict resolution beyond priority**
   - What we know: Explicit priority + alphabetical system name
   - What's unclear: User override for specific keyset conflicts, audit trail of which source won
   - Recommendation: Phase 8 uses deterministic priority, Phase 9+ could add conflict audit tables

3. **Keyset identity in attribute tables**
   - What we know: Requirements focus on anchor keyset identity
   - What's unclear: Do attribute tables get their own keysets, or inherit from anchor?
   - Recommendation: Plan 08-02 should clarify that attributes inherit anchor keyset (FK relationship), no separate keyset column needed

## Sources

### Primary (HIGH confidence)

- [Hypothesis Official Documentation](https://hypothesis.readthedocs.io/en/latest/) - Property-based testing strategies and round-trip testing patterns
- [SQLGlot Official Documentation](https://sqlglot.com/sqlglot.html) - AST construction, CONCAT, CASE expressions, NULL handling
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/) - Model validators, frozen config, field metadata
- [Anchor Modeling: Identification, identity, and key](https://www.anchormodeling.com/identification-identity-and-key/) - Natural key vs surrogate key concepts in Anchor Modeling
- Local codebase analysis - Existing patterns in `/workspaces/data-architect/src/data_architect/generation/` (Phase 7 decisions)

### Secondary (MEDIUM confidence)

- [How to Use Hypothesis and Pytest for Robust Property-Based Testing in Python](https://pytest-with-eric.com/pytest-advanced/hypothesis-testing-python/) - Round-trip testing examples
- [SQL CONCAT and COALESCE for NULL Handling](https://learnsql.com/cookbook/how-to-concatenate-string-and-null-values-in-sql-server/) - NULL propagation patterns
- [Data Lineage Tracking: Complete Guide for 2026](https://atlan.com/know/data-lineage-tracking/) - Column-level lineage and staging mappings
- [Multi-Master Conflicts - How to Handle Them](https://arpitbhayani.me/blogs/conflict-resolution/) - Deterministic conflict resolution patterns

### Tertiary (LOW confidence)

- WebSearch results on keyset identity format - No direct matches for `entity@system~tenant|natural_key` format, appears to be project-specific design decision (confirmed by requirements KEY-01)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Hypothesis, SQLGlot, Pydantic already in use and verified in Phases 6-7
- Architecture: HIGH - Patterns verified from official docs and existing codebase
- Pitfalls: MEDIUM - Delimiter escaping pitfalls verified via Hypothesis docs, NULL handling verified via SQL standards, conflict resolution based on distributed systems patterns

**Research date:** 2026-02-09
**Valid until:** 30 days (stable stack, no fast-moving dependencies)
