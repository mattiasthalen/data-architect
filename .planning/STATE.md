# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate -- not just template generation.
**Current focus:** v0.3.0 DAB Generation -- MILESTONE COMPLETE

## Current Position

Phase: 10 of 10 (Northwind Reference Example) -- COMPLETE
Plan: 1 of 1 in current phase (COMPLETE)
Status: v0.3.0 MILESTONE COMPLETE -- all 10 phases executed, all 25 plans delivered
Last activity: 2026-02-10 -- Phase 10 complete (Northwind reference, 339 tests passing, 93.70% coverage)

Progress: [████████████████████] 100% (25/25 plans across all milestones)

## Performance Metrics

**Velocity:**
- Total plans completed: 25
- Average duration: 10.4 min
- Total execution time: 4.65 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Project Foundation | 2/2 | 5 min | 2.5 min |
| 2. CLI Scaffolding | 2/2 | 12 min | 6.0 min |
| 3. Agent Definitions + OpenCode Integration | 2/2 | 10.7 min | 5.3 min |
| 4. Agent Quality and Modeling Workflows | 3/3 | 12.6 min | 4.2 min |
| 5. Pre-commit Framework Migration | 1/1 | 2 min | 2.0 min |
| 6. YAML Schema Foundation | 3/3 | 125 min | 41.7 min |
| 7. SQL Generation Engine | 3/3 | 28.8 min | 9.6 min |
| 8. Keyset Identity and Staging Mappings | 4/4 | 37.8 min | 9.5 min |
| 8.1 Staging Keyset Single Source of Truth | 2/2 | 10 min | 5.0 min |
| 9. XML Interoperability | 2/2 | 27 min | 13.5 min |
| 10. Northwind Reference Example | 1/1 | 8 min | 8.0 min |

## Accumulated Context

### Decisions

All decisions logged in PROJECT.md Key Decisions table with outcomes.

Recent decisions affecting current work:
- SQLGlot ASTs for SQL generation (NOT Jinja2 per-dialect templates)
- Bitemporality: `changed_at` (valid time) + `recorded_at` (transaction time)
- Keyset identity: `entity@system~tenant|natural_key` with escape sequences
- Keyset null safety: NULL natural key → entire keyset NULL (not `entity@system~tenant|`)
- `dab generate` also produces staging table DDL (not just anchor tables)
- Bruin format: `--format bruin` (SQL with frontmatter) and `--format raw` (plain SQL)
- StrEnum over str + Enum for SchemaLayer (06-01: Ruff UP042 auto-fix)
- Runtime imports for Pydantic models (06-01: TYPE_CHECKING breaks model_validate)
- TC001/ANN401 ignores for validation module (06-02: runtime type access needed)
- Column ordering convention: identity, FKs, value, bitemporal, metadata (07-01)
- Conditional bitemporal columns based on entity time_range attribute (07-01)
- Staging table DDL from raw dict structure; formal Pydantic models in Phase 8 (07-01)
- DML uses staging_table_name() from naming.py for DDL/DML staging source consistency (07-02)
- Historized attributes follow Anchor Modeling append-only: insert with new changed_at, never update (07-02)
- Metadata population uses deterministic literals: 'architect', 'architect-generated' (07-02)
- SQL generation via f-string templates parsed by SQLGlot for complex MERGE statements (07-02)
- Inline Bruin formatting in CLI (07-03): requires entity metadata unavailable in generic write_output
- Bruin strategy: DDL always create+replace, DML merge for historized, create+replace for static (07-03)
- CLI validation flow: file exists → spec validates → generate → format → write → summarize (07-03)
- Left-to-right pairing algorithm for keyset parsing (08-01): simple, consistent, works for non-ambiguous cases
- Property-based test filtering for ambiguous delimiter cases (08-01): focus on practical use cases
- StagingMapping Pydantic model with model_rebuild() for circular imports (08-02): import after class definitions
- Separate columns/column_mappings in StagingMapping (08-02): columns for DDL, column_mappings for DML lineage
- Keyset prefix escaped at generation time, natural key at runtime (08-02): nested REPLACE in SQL
- Composite natural key NULL propagation (08-02): CASE WHEN any component NULL THEN NULL
- Multi-source conflict resolution (08-03): priority (lower wins), then alphabetical by system/tenant
- Multi-source file naming (08-03): system suffix for 2+ sources, no suffix for single-source
- Per-source MERGE generation (08-03): one MERGE statement per staging mapping with deterministic ordering
- Keyset identity in DML (08-04): _build_metadata_id_expr() helper encapsulates keyset vs fallback logic
- Column mapping in attributes (08-04): staging_value_col lookup with AS aliasing for explicit lineage
- SQLGlot ComputedColumnConstraint transpiles correctly (08.1-01): postgres GENERATED ALWAYS AS, tsql/snowflake AS...PERSISTED
- Composite key delimiter escaping after concatenation (08.1-01): build_composite_natural_key_expr() handles ':' separator
- Backward compatibility via optional parameters (08.1-01): anchor/mapping default to None in build_staging_table()
- DML references staging.keyset_id column (08.1-02): single source of truth instead of inline computation
- PostgreSQL templates use source alias (08.1-02): consistent with tsql/snowflake templates
- Static DO UPDATE SET uses EXCLUDED pattern (08.1-02): cleaner than re-computing expressions
- [Phase 09]: Use pydantic-xml BaseXmlModel for XML parsing (type-safe, matches Pydantic pattern)
- [Phase 09]: Separate XML models from YAML models with to_yaml_model() conversion (clean separation of concerns)
- [Phase 09]: Use pydantic-xml BaseXmlModel for XML parsing (type-safe, matches Pydantic pattern)
- [Phase 09]: Separate XML models from YAML models with to_yaml_model() conversion (clean separation of concerns)

### Pending Todos

None.

### Roadmap Evolution

- Phase 08.1 inserted after Phase 8: Staging keyset single source of truth (URGENT)

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-10
Stopped at: Phase 10 complete (Northwind reference example with 35 E2E tests)
Resume file: .planning/phases/10-northwind-reference-example/10-01-SUMMARY.md
Next action: v0.3.0 milestone COMPLETE -- ready for release

---
*State initialized: 2026-02-07*
*Last updated: 2026-02-10 -- Phase 10 complete (Northwind reference example, 339 tests, 93.70% coverage, v0.3.0 COMPLETE)*
