---
phase: 08-keyset-identity-and-staging-mappings
verified: 2026-02-09T23:15:00Z
status: gaps_found
score: 17/23 must-haves verified
gaps:
  - truth: "Generated DML uses keyset identity column constructed from staging source natural key columns"
    status: failed
    reason: "DML generation still uses hardcoded 'architect-generated' instead of keyset identity construction"
    artifacts:
      - path: "src/data_architect/generation/dml.py"
        issue: "Missing import of build_keyset_expr and integration into MERGE statements"
    missing:
      - "Import build_keyset_expr from data_architect.generation.keyset_sql in dml.py"
      - "Replace metadata_id = 'architect-generated' with build_keyset_expr() call"
      - "Use mapping.system, mapping.tenant, anchor.descriptor, and natural_key_columns in keyset construction"
      - "Handle composite natural keys using build_composite_natural_key_expr()"
  - truth: "build_keyset_expr() produces CASE WHEN ... IS NULL THEN NULL ELSE CONCAT(...) END SQL with nested REPLACE for delimiter escaping"
    status: verified
    note: "Function exists and is tested, but NOT integrated into DML generation"
  - truth: "DDL staging table generation uses StagingMapping model instead of raw dict"
    status: verified
    note: "Works correctly but keyset not used in DML"
  - truth: "Column-level staging mappings produce correct INSERT...SELECT with explicit column lineage"
    status: partial
    reason: "column_mappings exist in model but not used in DML SELECT generation"
    missing:
      - "Update build_attribute_merge() to use mapping.column_mappings for SELECT clause"
      - "Generate INSERT...SELECT with explicit staging_column -> attribute_column mapping"
---

# Phase 8: Keyset Identity and Staging Mappings Verification Report

**Phase Goal:** Users can define multi-source staging mappings with keyset identity and generate loading SQL that tracks data provenance

**Verified:** 2026-02-09T23:15:00Z
**Status:** gaps_found
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | format_keyset() produces the canonical keyset string 'entity@system~tenant\|natural_key' | ✓ VERIFIED | Function exists (168 lines), tested with 32 tests, 100% coverage, manual test passes |
| 2 | parse_keyset() returns a KeysetComponents named tuple with entity, system, tenant, natural_key fields | ✓ VERIFIED | Function exists, NamedTuple defined, round-trip tests pass |
| 3 | Round-trip parse(format(entity, system, tenant, nk)) == (entity, system, tenant, nk) for all string inputs including delimiter-heavy strings | ✓ VERIFIED | Hypothesis property-based tests with 200+ examples, filtered for ambiguous cases |
| 4 | NULL natural key produces NULL keyset (None return from format_keyset) | ✓ VERIFIED | KEY-05 null safety implemented and tested |
| 5 | Delimiter characters in any component are escaped: @ -> @@, ~ -> ~~, \| -> \|\| | ✓ VERIFIED | escape_delimiters/unescape_delimiters functions tested |
| 6 | parse_keyset never raises an exception on any string input | ✓ VERIFIED | Hypothesis crash safety test passes |
| 7 | StagingMapping Pydantic model captures system, tenant, table, natural_key_columns, column_mappings, and optional priority | ✓ VERIFIED | Model exists (42 lines), frozen, with all required fields |
| 8 | Anchor.staging_mappings field accepts list[StagingMapping] instead of list[Any] | ✓ VERIFIED | Type updated with model_rebuild(), imports StagingMapping |
| 9 | build_keyset_expr() produces CASE WHEN ... IS NULL THEN NULL ELSE CONCAT(...) END SQL with nested REPLACE for delimiter escaping | ✓ VERIFIED | Function exists (157 lines), 12 tests pass, generates correct SQL for postgres/tsql/snowflake |
| 10 | Generated DML uses keyset identity column constructed from staging source natural key columns | ✗ FAILED | DML still uses 'architect-generated', build_keyset_expr NOT imported in dml.py |
| 11 | DDL staging table generation uses StagingMapping model instead of raw dict | ✓ VERIFIED | Uses mapping.columns, no raw dict access |
| 12 | Column-level staging mappings produce correct INSERT...SELECT with explicit column lineage | ⚠️ PARTIAL | column_mappings exists in model but NOT used in DML SELECT generation |
| 13 | resolve_staging_order() sorts staging mappings by explicit priority (lower wins) then alphabetical system name | ✓ VERIFIED | Function exists (50 lines), 7 tests pass, deterministic |
| 14 | Multiple staging tables feeding the same anchor each produce a separate MERGE statement | ✓ VERIFIED | Multi-source detection in generate_all_dml(), iterates mappings |
| 15 | MERGE statements are generated in priority order (highest priority source first) | ✓ VERIFIED | Uses resolve_staging_order() before iteration |
| 16 | Each staging source embeds its own system/tenant in the keyset identity column | ✗ FAILED | Keyset NOT constructed, still uses 'architect-generated' |
| 17 | Deterministic output: same spec with multiple sources produces byte-identical SQL on every run | ✓ VERIFIED | Test test_generate_all_dml_multi_source_deterministic passes |
| 18 | DDL generates separate staging tables for each source mapping | ✓ VERIFIED | DDL iterates all staging_mappings |

**Score:** 15/18 truths verified (3 failed/partial)

### Critical Wiring Gap

**BLOCKER:** The keyset identity SQL builder exists and is fully tested, but it is NOT integrated into DML generation. This breaks the core Phase 8 goal of "generate loading SQL that tracks data provenance."

**Key Link Verification:**

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| keyset.py | escaping.py | import escape_delimiters, unescape_delimiters | ✓ WIRED | Line 11 in keyset.py |
| anchor.py | staging.py | staging_mappings: list[StagingMapping] | ✓ WIRED | Line 105, 111 in anchor.py |
| dml.py | keyset_sql.py | import build_keyset_expr | ✗ NOT_WIRED | **MISSING - plan required this** |
| dml.py | conflict.py | import resolve_staging_order | ✓ WIRED | Line 8 in dml.py, used at line 476 |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/data_architect/identity/__init__.py` | Public API re-exports | ✓ VERIFIED | 27 lines, exports parse_keyset, format_keyset, KeysetComponents, escape/unescape |
| `src/data_architect/identity/keyset.py` | KeysetComponents NamedTuple, parse/format functions | ✓ VERIFIED | 168 lines, substantive, contains KeysetComponents |
| `src/data_architect/identity/escaping.py` | escape_delimiters, unescape_delimiters | ✓ VERIFIED | 50 lines, exports both functions |
| `tests/test_keyset.py` | Hypothesis property-based tests + unit tests | ✓ VERIFIED | Contains @given, 32 tests pass |
| `src/data_architect/models/staging.py` | StagingMapping and StagingColumn models | ✓ VERIFIED | 42 lines, frozen Pydantic models |
| `src/data_architect/generation/keyset_sql.py` | build_keyset_expr() for SQL keyset construction | ✓ VERIFIED | 157 lines, substantive, contains build_keyset_expr |
| `tests/test_staging_models.py` | Tests for StagingMapping model validation | ✓ VERIFIED | 10 tests pass |
| `tests/test_keyset_sql.py` | Tests for keyset SQL generation | ✓ VERIFIED | 12 tests pass, covers all dialects |
| `src/data_architect/generation/conflict.py` | resolve_staging_order() function | ✓ VERIFIED | 50 lines, deterministic sorting |
| `tests/test_conflict.py` | Tests for conflict resolution | ✓ VERIFIED | 7 tests pass |

**All artifacts exist and are substantive.** The gap is in wiring, not in artifact creation.

### Requirements Coverage

Phase 8 requirements from REQUIREMENTS.md:

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| KEY-01: Keyset format `entity@system~tenant\|natural_key` | ✓ SATISFIED | All supporting truths verified |
| KEY-02: Canonical escape sequences for delimiter collision | ✓ SATISFIED | escape_delimiters/unescape_delimiters work |
| KEY-03: SQL generation for keyset construction from source natural key columns | ✗ BLOCKED | build_keyset_expr exists but NOT used in DML |
| KEY-04: KeysetIdentity module with parse()/format() and Hypothesis tests | ✓ SATISFIED | Module complete, 200+ examples tested |
| KEY-05: Null safety - if natural key is NULL, entire keyset is NULL | ✓ SATISFIED | Implemented and tested |
| STG-01: Column-level staging mappings in spec | ⚠️ PARTIAL | Model has column_mappings but NOT used in DML SELECT |
| STG-02: Multiple staging tables per anchor | ✓ SATISFIED | Model supports list[StagingMapping] |
| STG-03: System and tenant identifiers per staging source | ✓ SATISFIED | StagingMapping has system/tenant fields |
| STG-04: SQL generation for staging-to-anchor loading | ✗ BLOCKED | Multi-source works but keyset NOT constructed |
| STG-05: Conflict resolution strategy per multi-source anchor | ✓ SATISFIED | resolve_staging_order deterministic |

**Coverage:** 7/10 satisfied, 1 partial, 2 blocked

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| dml.py | 62, 150, 196, 267 | Hardcoded 'architect-generated' for metadata_id | 🛑 Blocker | Prevents keyset identity tracking (Phase 8 goal) |
| dml.py | N/A | Missing import of build_keyset_expr | 🛑 Blocker | Keyset SQL builder orphaned, not wired |
| dml.py | N/A | column_mappings not used in SELECT clause | ⚠️ Warning | Explicit column lineage not implemented |

### Gaps Summary

**Gap 1: Keyset identity not integrated into DML generation**

The `build_keyset_expr()` function exists and is fully tested (12 tests, 100% coverage), but it is NOT imported or used in `dml.py`. The plan explicitly states:

> "The keyset replaces metadata_id: `metadata_id` column gets the keyset expression instead of literal `'architect-generated'`"

But the actual implementation still uses:
```python
'architect-generated' AS metadata_id
```

**What's needed:**
1. Import `build_keyset_expr` and `build_composite_natural_key_expr` in `dml.py`
2. In `build_anchor_merge()`, when `mapping` is provided:
   - Build composite natural key expression from `mapping.natural_key_columns`
   - Call `build_keyset_expr(anchor.descriptor, mapping.system, mapping.tenant, composite_nk_expr, dialect)`
   - Use the resulting expression for `metadata_id` column instead of `'architect-generated'`
3. Update tests to verify keyset presence in generated SQL

**Gap 2: Column mappings not used in DML SELECT**

The `StagingMapping` model has `column_mappings: dict[str, str]` field (attribute_mnemonic -> staging_column_name), but `build_attribute_merge()` doesn't use it. The plan states:

> "When `anchor.staging_mappings` is populated and `column_mappings` exists, use `mapping.column_mappings[attribute.mnemonic]` to look up the staging column name for SELECT"

**What's needed:**
1. In `build_attribute_merge()`, check if mapping has column_mappings
2. If `attribute.mnemonic` exists in `mapping.column_mappings`, use the mapped staging column name
3. Otherwise, fall back to default naming convention

**Impact:** Without this, explicit column lineage (STG-01) is not achieved.

---

## Functional Tests Performed

### 1. Keyset Identity Round-Trip
```bash
$ python -c "from data_architect.identity import format_keyset, parse_keyset; \
  print(parse_keyset(format_keyset('Customer', 'Northwind', 'ACME', '10248')))"
KeysetComponents(entity='Customer', system='Northwind', tenant='ACME', natural_key='10248')
```
**Result:** ✓ PASS

### 2. Delimiter Escaping
```bash
$ python -c "from data_architect.identity import format_keyset, parse_keyset; \
  parsed = parse_keyset('Order@SAP@@US~Corp~~Ltd|A||B'); \
  print(f'system={parsed.system}, tenant={parsed.tenant}, nk={parsed.natural_key}')"
system=SAP@US, tenant=Corp~Ltd, nk=A|B
```
**Result:** ✓ PASS

### 3. NULL Safety
```bash
$ python -c "from data_architect.identity import format_keyset; \
  print(format_keyset('Customer', 'Northwind', 'ACME', None))"
None
```
**Result:** ✓ PASS (KEY-05)

### 4. Conflict Resolution
```bash
$ python -c "from data_architect.generation.conflict import resolve_staging_order; \
  from data_architect.models.staging import StagingMapping; \
  sorted_mappings = resolve_staging_order([
    StagingMapping(system='SAP', tenant='EU', table='s1', natural_key_columns=['id'], priority=2),
    StagingMapping(system='Northwind', tenant='US', table='s2', natural_key_columns=['id'], priority=1)
  ]); \
  print(sorted_mappings[0].system)"
Northwind
```
**Result:** ✓ PASS (priority 1 comes first)

### 5. Keyset SQL Generation
```bash
$ python -c "from data_architect.generation.keyset_sql import build_keyset_expr; \
  expr = build_keyset_expr('Customer', 'ERP', 'ACME', 'customer_id', 'postgres'); \
  sql = expr.sql(dialect='postgres'); \
  print('Has CASE WHEN:', 'CASE WHEN' in sql); \
  print('Has REPLACE:', 'REPLACE' in sql); \
  print('Has NULL safety:', 'IS NULL' in sql)"
Has CASE WHEN: True
Has REPLACE: True
Has NULL safety: True
```
**Result:** ✓ PASS

### 6. DML Keyset Integration (CRITICAL FAILURE)
```bash
$ python -c "from data_architect.models.anchor import Anchor; \
  from data_architect.models.staging import StagingMapping, StagingColumn; \
  from data_architect.generation.dml import build_anchor_merge; \
  mapping = StagingMapping(system='Northwind', tenant='ACME', table='stg_c', natural_key_columns=['CustomerID'], columns=[StagingColumn(name='CustomerID', type='varchar(10)')]); \
  anchor = Anchor(mnemonic='CU', descriptor='Customer', identity='bigint', staging_mappings=[mapping]); \
  sql = build_anchor_merge(anchor, 'postgres', mapping).sql(dialect='postgres'); \
  print('Has keyset?', 'Customer@Northwind~ACME' in sql); \
  print('Has hardcoded?', 'architect-generated' in sql)"
Has keyset? False
Has hardcoded? True
```
**Result:** ✗ FAIL - Keyset NOT constructed in DML

---

## Test Coverage

**Phase 8 Test Suite:**
- `test_keyset.py`: 32 tests, 100% coverage of identity module
- `test_staging_models.py`: 10 tests, 100% coverage of staging models
- `test_keyset_sql.py`: 12 tests, 100% coverage of keyset SQL builders
- `test_conflict.py`: 7 tests, 100% coverage of conflict resolution
- `test_dml.py`: 24 tests (includes 5 multi-source tests), **but NO tests verify keyset in SQL**

**Overall Project Coverage:** 97% (230 tests pass)

**Coverage Gap:** Tests verify that multi-source DML is generated, but they don't check if keyset identity is actually constructed in the SQL. The tests would have caught this gap if they asserted on keyset presence.

---

## Verification Summary

**Status:** gaps_found

**What Works:**
1. ✓ Keyset identity parse/format with delimiter escaping (KEY-01, KEY-02, KEY-04, KEY-05)
2. ✓ StagingMapping Pydantic models (STG-01, STG-02, STG-03)
3. ✓ Keyset SQL builder (tested, correct SQL, supports all dialects)
4. ✓ Multi-source conflict resolution (deterministic, priority-based)
5. ✓ Multi-source MERGE generation (one MERGE per source, correct file naming)
6. ✓ All 230 tests pass with 97% coverage

**What's Broken:**
1. ✗ Keyset identity NOT used in DML generation (KEY-03, STG-04 blocked)
2. ⚠️ Column mappings NOT used in DML SELECT (STG-01 partial)

**Root Cause:** The plan's Task 2 states "Update DML builders to use keyset identity when staging_mappings are present" but this was not implemented. The keyset SQL builder was created and tested, but the wiring step was skipped.

**Goal Achievement:** **PARTIAL** - Users can define multi-source staging mappings (✓) with keyset identity models (✓), but the generated loading SQL does NOT track data provenance (✗) because keyset construction is missing from DML.

---

_Verified: 2026-02-09T23:15:00Z_
_Verifier: Claude (gsd-verifier)_
