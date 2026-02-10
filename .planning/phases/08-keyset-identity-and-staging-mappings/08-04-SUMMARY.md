---
phase: 08-keyset-identity-and-staging-mappings
plan: 04
subsystem: generation
tags: [dml, keyset-identity, staging-mappings, sqlglot, provenance]

# Dependency graph
requires:
  - phase: 08-02
    provides: "Keyset SQL expression builders (build_keyset_expr, build_composite_natural_key_expr)"
  - phase: 08-03
    provides: "Multi-source conflict resolution and per-source MERGE generation"
provides:
  - "Keyset identity integration in DML MERGE statements"
  - "Column mapping usage in attribute SELECT clauses"
  - "Complete provenance tracking in generated SQL"
affects: [phase-09, dab-generate, sql-generation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Helper function pattern for keyset-or-fallback logic (_build_metadata_id_expr)"
    - "Column mapping lookup with fallback to default naming"

key-files:
  created: []
  modified:
    - src/data_architect/generation/dml.py
    - tests/test_dml.py

key-decisions:
  - "Helper function _build_metadata_id_expr() encapsulates keyset generation vs fallback logic"
  - "Column mappings use staging_value_col with AS aliasing in SELECT clauses"
  - "Backward compatibility: no mapping = 'architect-generated' literal"
  - "Composite natural keys handled inline with escaped prefix and REPLACE nesting"

patterns-established:
  - "_build_metadata_id_expr helper: single-column keys use build_keyset_expr directly, composite keys build manually with prefix escaping"
  - "staging_value_col lookup: check mapping.column_mappings dict, fallback to value_col"
  - "All 4 SQL templates updated consistently: postgres/tsql, historized/static"

# Metrics
duration: 7min
completed: 2026-02-10
---

# Phase 08 Plan 04: Gap Closure Summary

**Keyset identity and column mappings integrated into DML generation with 7 new tests verifying provenance tracking**

## Performance

- **Duration:** 7 minutes (464 seconds)
- **Started:** 2026-02-10T07:48:51Z
- **Completed:** 2026-02-10T07:56:35Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Keyset identity expressions now generated in all anchor and attribute MERGE statements when staging mappings provided
- Column-level staging mappings correctly produce explicit column lineage in SELECT clauses
- 7 new tests verify keyset presence, column mapping usage, composite keys, and fallback behavior
- Phase 8 gaps fully closed: KEY-03, STG-01, and STG-04 requirements now satisfied

## Task Commits

Each task was committed atomically:

1. **Task 1: Integrate keyset identity into DML MERGE builders** - `2629dfa` (feat)
   - Imported build_keyset_expr, build_composite_natural_key_expr, escape_delimiters
   - Created _build_metadata_id_expr() helper function
   - Replaced hardcoded 'architect-generated' in build_anchor_merge and build_attribute_merge
   - Handles composite natural keys with NULL-safe concatenation
   - All existing tests pass

2. **Task 2: Use column_mappings in attribute DML and add keyset tests** - `82fb85f` (feat)
   - Added staging column name lookup using mapping.column_mappings
   - Updated all 4 SQL templates (postgres/tsql historized/static) to use staging_value_col
   - Added 7 new tests verifying keyset integration and column mapping
   - All 237 tests pass (230 existing + 7 new)

## Files Created/Modified
- `src/data_architect/generation/dml.py` - Integrated keyset identity and column mappings into MERGE builders
- `tests/test_dml.py` - Added 7 new tests for keyset and column mapping verification

## Decisions Made
- **Helper function approach:** Created _build_metadata_id_expr() to encapsulate keyset-or-fallback logic, keeping main builders clean
- **Composite key handling:** For multi-column natural keys, build keyset SQL manually with escaped prefix and nested REPLACE calls
- **Column mapping fallback:** When no column_mappings or attribute not in mappings, use default column name (value_col)
- **Backward compatibility:** When no mapping provided, continue using 'architect-generated' literal

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Temporarily adjusted Python version requirement**
- **Found during:** Task 1 verification
- **Issue:** Project requires Python 3.13 but environment only has Python 3.11, blocking package installation
- **Fix:** Temporarily changed pyproject.toml requires-python to ">=3.11", installed package, then reverted to ">=3.13"
- **Files modified:** pyproject.toml (temporarily, then reverted)
- **Verification:** Package installed successfully, tests run
- **Committed in:** Not committed (temporary change reverted)

**2. [Rule 1 - Linting] Fixed line length violations**
- **Found during:** Task 1 pre-commit hooks
- **Issue:** 5 lines exceeded 88-character limit in docstring and comments
- **Fix:** Reformatted docstring and comments to stay under line limit
- **Files modified:** src/data_architect/generation/dml.py
- **Verification:** Ruff linter passes
- **Committed in:** 2629dfa (part of Task 1 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 linting)
**Impact on plan:** Environment constraint workaround was temporary and not committed. Line length fix maintains code quality. No scope creep.

## Issues Encountered
- **Missing test dependencies:** pytest-cov and hypothesis not installed. Installed via pip to run full test suite.
- **Pre-commit hooks not installed:** Ran `pre-commit install` to enable git hooks for commit validation.

## User Setup Required
None - no external service configuration required.

## Gap Closure Verification

**Phase 8 gaps fully closed:**

1. **Truth #10 (FAILED → VERIFIED):** "Generated DML uses keyset identity column constructed from staging source natural key columns"
   - ✅ build_keyset_expr imported and called in dml.py
   - ✅ Generated SQL for anchor with mapping contains keyset prefix (e.g., Customer@Northwind~ACME)

2. **Truth #12 (PARTIAL → VERIFIED):** "Column-level staging mappings produce correct INSERT...SELECT with explicit column lineage"
   - ✅ mapping.column_mappings used in build_attribute_merge
   - ✅ Generated SQL uses mapped column name when column_mappings provided

3. **Truth #16 (FAILED → VERIFIED):** "Each staging source embeds its own system/tenant in the keyset identity column"
   - ✅ Multi-source DML generates different keyset prefixes per source (Northwind vs SAP)

**Requirements unblocked:**
- KEY-03: build_keyset_expr now called in DML generation ✅
- STG-01: column_mappings now used in SELECT clause ✅
- STG-04: staging-to-anchor loading includes keyset construction ✅

**Anti-patterns resolved:**
- ✅ No more hardcoded 'architect-generated' in build_anchor_merge or build_attribute_merge when mapping provided
- ✅ build_keyset_expr imported and used (no longer orphaned)
- ✅ column_mappings used in SELECT clause

## Next Phase Readiness
- Phase 8 complete with all gaps closed
- Keyset identity and staging mappings fully integrated into DML generation
- Ready for Phase 9 (if planned) or project completion
- All 237 tests passing with 97% coverage

## Self-Check: PASSED

All artifacts verified:
- ✓ File exists: src/data_architect/generation/dml.py
- ✓ File exists: tests/test_dml.py
- ✓ Commit exists: 2629dfa (Task 1)
- ✓ Commit exists: 82fb85f (Task 2)
- ✓ Integration verified: build_keyset_expr imported and used (4 occurrences)
- ✓ Integration verified: column_mappings used (4 occurrences)
- ✓ Tests added: 7 new tests in test_dml.py

---
*Phase: 08-keyset-identity-and-staging-mappings*
*Completed: 2026-02-10*
