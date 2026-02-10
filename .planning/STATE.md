# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-09)

**Core value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate -- not just template generation.
**Current focus:** v0.3.0 DAB Generation -- Phase 8 (Keyset Identity and Staging Mappings)

## Current Position

Phase: 8 of 10 (Keyset Identity and Staging Mappings)
Plan: 4 of 4 in current phase (COMPLETE)
Status: Phase complete - all gaps closed
Last activity: 2026-02-10 -- Phase 8 gap closure complete (keyset identity and column mappings integrated into DML)

Progress: [##########██████████] 91% (20/22 plans across all milestones)

## Performance Metrics

**Velocity:**
- Total plans completed: 20
- Average duration: 11.3 min
- Total execution time: 3.90 hours

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

### Pending Todos

None.

### Roadmap Evolution

- Phase 08.1 inserted after Phase 8: Staging keyset single source of truth (URGENT)

### Blockers/Concerns

None - Phase 8 complete with all gaps closed.

## Session Continuity

Last session: 2026-02-10
Stopped at: Phase 8 complete - gap closure plan 08-04 executed successfully
Resume file: .planning/phases/08-keyset-identity-and-staging-mappings/08-04-SUMMARY.md
Next action: Phase 8 complete. Ready to proceed to Phase 9 or project completion.

---
*State initialized: 2026-02-07*
*Last updated: 2026-02-10 -- Phase 8 complete: keyset identity and column mappings integrated into DML generation*
