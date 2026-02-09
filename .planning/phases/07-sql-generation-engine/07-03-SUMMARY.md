---
phase: 07-sql-generation-engine
plan: 03
subsystem: cli-generation-pipeline
tags: [cli, formatting, bruin, sql-output, end-to-end]

dependency_graph:
  requires:
    - 07-01-SUMMARY.md  # DDL generation (generate_all_ddl)
    - 07-02-SUMMARY.md  # DML generation (generate_all_dml)
    - 06-01-SUMMARY.md  # Validation pipeline (validate_spec)
  provides:
    - architect dab generate command
    - Output format flags (raw/bruin)
    - Dialect flags (postgres/tsql/snowflake)
    - File writing with deterministic output
  affects:
    - End user workflow (complete SQL generation pipeline)
    - Bruin pipeline orchestration integration

tech_stack:
  added:
    - typer StrEnum for CLI flags
  patterns:
    - CLI validation -> generation -> formatting -> file writing
    - Per-entity Bruin frontmatter with historized strategy detection
    - Deterministic file ordering and content

key_files:
  created:
    - src/data_architect/generation/formatters.py  # Output formatters (raw + Bruin)
    - tests/test_formatters.py  # Formatter unit tests
  modified:
    - src/data_architect/cli.py  # Added dab generate command
    - src/data_architect/generation/__init__.py  # Export formatters
    - tests/test_cli.py  # Added 11 CLI integration tests

decisions:
  - choice: Inline Bruin formatting in CLI rather than in formatters
    rationale: "Bruin format requires entity metadata (name, historized status) not available in generic write_output function"
    alternatives: ["Pass metadata dict to write_output", "Create entity-aware formatter factory"]
    outcome: "CLI builds historized_entities lookup from spec, applies format_bruin per-file with context"

  - choice: Use staging_table_name() from 07-02 for DML/DDL consistency
    rationale: "DML references staging tables by name; DDL must generate matching tables"
    alternatives: ["Hardcode stg_ prefix pattern", "Allow mismatched names"]
    outcome: "Cross-validation test ensures DML staging refs have corresponding DDL files"

  - choice: Separate DDL and DML file writing loops for Bruin format
    rationale: "DDL always uses create+replace; DML needs historized lookup for merge vs create+replace"
    alternatives: ["Single unified loop with entity type detection"]
    outcome: "Clear separation; DDL formatter always static, DML checks historized_entities set"

metrics:
  duration: 7.8 min
  completed: 2026-02-09
---

# Phase 7 Plan 3: CLI Integration with Output Formatters Summary

**One-liner:** Complete end-to-end `architect dab generate` command with raw/Bruin format flags, dialect selection, and deterministic file output to ddl/ and dml/ subdirectories.

## What Was Built

Completed the Phase 7 SQL generation engine by wiring DDL and DML builders (from 07-01 and 07-02) into a user-facing CLI command with format and dialect flags.

**Task 1: Output formatters (raw + Bruin)**
- Implemented `format_raw()`: Plain SQL with trailing newline
- Implemented `format_bruin()`: SQL wrapped with Bruin YAML frontmatter
  - DDL files: `strategy: create+replace` (always recreate structure)
  - DML files with historized entities: `strategy: merge` (SCD2 append-only)
  - DML files with static entities: `strategy: create+replace`
- Implemented `write_output()`: Deterministic file writing to subdirectories
- Added 11 unit tests for formatters with 100% coverage
- **Commit:** `97a6261`

**Task 2: `dab generate` CLI command**
- Added `OutputFormat` enum: `raw` (plain SQL) | `bruin` (with frontmatter)
- Added `Dialect` enum: `postgres` | `tsql` | `snowflake`
- Implemented `dab_generate()` command flow:
  1. Validate spec file exists
  2. Load and validate spec (exits with formatted errors if invalid)
  3. Generate DDL and DML using existing builders
  4. Build historized entities lookup for Bruin format strategy
  5. Write DDL files to `output_dir/ddl/`
  6. Write DML files to `output_dir/dml/`
  7. Print summary (N DDL, M DML files written)
- Added 11 CLI integration tests:
  - Valid spec creates DDL + DML files
  - Invalid spec shows validation errors (not stack traces)
  - Missing spec shows clear error
  - `--format raw` produces plain SQL
  - `--format bruin` produces SQL with frontmatter
  - `--dialect postgres|snowflake` controls SQL syntax
  - `--output-dir` writes to custom location
  - Deterministic output (GEN-08): two runs produce identical files
  - DDL/DML staging table name consistency validation
  - Help text shows all options
- **Commit:** `8b961f2`

## Deviations from Plan

None - plan executed exactly as written.

## Integration Points

**Depends on:**
- 07-01 DDL generation: `generate_all_ddl(spec, dialect)` produces DDL dict
- 07-02 DML generation: `generate_all_dml(spec, dialect)` produces DML dict
- 06-01 Validation: `validate_spec(path)` validates YAML before generation

**Provides:**
- Complete SQL generation pipeline: `architect dab generate spec.yaml`
- Bruin format support for pipeline orchestration tools
- Dialect selection for multi-platform deployment

## Key Behaviors

**Format flags:**
```bash
architect dab generate spec.yaml --format raw      # Plain SQL
architect dab generate spec.yaml --format bruin    # SQL with Bruin frontmatter
```

**Bruin frontmatter structure:**
```sql
/* @bruin
name: dab.AC_NAM_Actor_Name
type: sql
materialization:
    type: table
    strategy: merge  # or create+replace
@bruin */

INSERT INTO AC_NAM_Actor_Name ...
```

**Dialect flags:**
```bash
architect dab generate spec.yaml --dialect postgres   # PostgreSQL (default)
architect dab generate spec.yaml --dialect snowflake  # Snowflake
architect dab generate spec.yaml --dialect tsql       # T-SQL
```

**Output directory structure:**
```
output/
  ddl/
    AC_Actor.sql
    AC_NAM_Actor_Name.sql
    GEN_Gender.sql
    stg_actors.sql
  dml/
    AC_Actor_load.sql
    AC_NAM_Actor_Name_load.sql
    GEN_Gender_load.sql
```

**Error handling:**
- Missing spec file: "Error: spec file not found: {path}" (exit 1)
- Invalid spec: "Validation errors:" + formatted errors with line numbers (exit 1)
- Success: "✓ Generated N DDL and M DML files" + "Output directory: {path}"

## Test Coverage

**Formatters module:** 100% coverage (11 tests)
- format_raw trailing newline behavior
- format_bruin frontmatter structure
- Bruin strategy selection (merge vs create+replace)
- write_output file creation and determinism

**CLI integration:** 11 tests covering all features
- Valid/invalid/missing spec handling
- Format flag (raw/bruin) behavior
- Dialect flag (postgres/snowflake) behavior
- Custom output directory
- Deterministic output verification
- DDL/DML staging name consistency

**Overall coverage:** 96.9% across entire codebase (164 tests pass)

## Verification

✅ `make check` passes (lint + type + test)
✅ Manual end-to-end: `architect dab generate tests/fixtures/valid_spec.yaml` produces 6 DDL + 6 DML files
✅ `--format bruin` adds correct frontmatter with merge/create+replace strategies
✅ `--format raw` produces clean SQL without wrapper
✅ Invalid spec shows validation errors with line numbers
✅ Missing spec file shows clear error
✅ Deterministic: two runs produce byte-identical output
✅ `architect dab generate --help` shows all options

## Self-Check: PASSED

**Files created:**
- FOUND: /workspaces/data-architect/src/data_architect/generation/formatters.py
- FOUND: /workspaces/data-architect/tests/test_formatters.py

**Files modified:**
- FOUND: /workspaces/data-architect/src/data_architect/cli.py (dab_generate command present)
- FOUND: /workspaces/data-architect/src/data_architect/generation/__init__.py (formatters exported)
- FOUND: /workspaces/data-architect/tests/test_cli.py (11 new dab_generate tests)

**Commits:**
- FOUND: 97a6261 (feat(07-03): add raw and Bruin output formatters with file writing)
- FOUND: 8b961f2 (feat(07-03): wire dab generate CLI with format and dialect flags)

## Impact on Phase 7

**Phase 7 completion status:** ✅ Complete (3/3 plans)

This plan completes Phase 7 (SQL Generation Engine) by delivering the end-to-end pipeline:
1. 07-01: DDL generation with SQLGlot ASTs
2. 07-02: DML/MERGE generation with SCD2 patterns
3. **07-03: CLI integration with format/dialect flags** ← This plan

Users can now run `architect dab generate spec.yaml` and get working SQL files ready for deployment to their data warehouse.

**Next phase readiness:**
- Phase 8 (Staging Parser) can now test against generated staging table DDL
- Bruin format integration enables orchestration workflows
- Deterministic output enables version control and CI/CD pipelines

## Notes

**Bruin format strategy logic:**
- DDL files → always `create+replace` (structure changes require full recreation)
- DML historized (time_range) → `merge` (append-only SCD2, never update old rows)
- DML static (no time_range) → `create+replace` (simple upsert)

**Historized entity detection:**
Built from spec at CLI level:
- Attributes with `time_range: datetime` → historized
- Ties with `time_range: datetime` → historized
- Anchors and Knots → never historized (identity-only)

**Staging table consistency:**
Cross-validation test ensures DML references to staging tables (e.g., `FROM stg_actors`) have corresponding DDL files. This validates the naming convention linkage from 07-01 and 07-02.
