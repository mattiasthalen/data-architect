# Roadmap: Data Architect

## Milestones

- SHIPPED **v0.1.0 Init + Agents** -- Phases 1-4 (shipped 2026-02-08)
- SHIPPED **v0.2.0 Pre-commit Framework** -- Phase 5 (shipped 2026-02-09)
- ACTIVE **v0.3.0 DAB Generation** -- Phases 6-10 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>SHIPPED v0.1.0 Init + Agents (Phases 1-4) -- SHIPPED 2026-02-08</summary>

- [x] Phase 1: Project Foundation (2/2 plans) -- completed 2026-02-07
- [x] Phase 2: CLI Scaffolding (2/2 plans) -- completed 2026-02-07
- [x] Phase 3: Agent Definitions + OpenCode Integration (2/2 plans) -- completed 2026-02-08
- [x] Phase 4: Agent Quality + Modeling Workflows (3/3 plans) -- completed 2026-02-08

See: `.planning/milestones/v0.1.0-ROADMAP.md` for full details.

</details>

<details>
<summary>SHIPPED v0.2.0 Pre-commit Framework (Phase 5) -- SHIPPED 2026-02-09</summary>

- [x] Phase 5: Pre-commit Framework Migration (1/1 plan) -- completed 2026-02-08

See: `.planning/milestones/v0.2.0-ROADMAP.md` for full details.

</details>

### ACTIVE v0.3.0 DAB Generation (Phases 6-10)

**Milestone Goal:** Define a YAML specification format (superset of official Anchor XML) and generate idempotent, dialect-agnostic SQL from it using SQLGlot ASTs. Deliver keyset identity, multi-source staging, XML interoperability, and a Northwind reference example that validates everything end-to-end.

- [ ] **Phase 6: YAML Schema Foundation and Spec Validation** - Pydantic models, YAML parsing, validation with line numbers, `dab init` scaffold
- [ ] **Phase 7: SQL Generation Engine** - SQLGlot AST-based generation, idempotent DDL/DML, bitemporality, multi-dialect compilation, output formats
- [ ] **Phase 8: Keyset Identity and Staging Mappings** - Keyset parse/format module, staging column mappings, multi-source loading, conflict resolution
- [ ] **Phase 9: XML Interoperability** - Import from Anchor Modeler XML, export with extension warnings, round-trip validation
- [ ] **Phase 10: Northwind Reference Example** - Pre-filled spec, end-to-end validation of all features

## Phase Details

### Phase 6: YAML Schema Foundation and Spec Validation
**Goal**: Users can define a valid Anchor Model specification in YAML and get immediate, precise feedback on errors
**Depends on**: Phase 5 (project infrastructure)
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05, SPEC-06, SPEC-07
**Success Criteria** (what must be TRUE):
  1. Running `architect dab init` creates a YAML spec file with inline comments explaining every section (anchors, attributes, ties, knots, staging mappings, keyset identity)
  2. A valid YAML spec loads into frozen Pydantic models without error, and an invalid spec produces validation errors citing the exact line number of each problem
  3. Referential integrity violations are caught -- an attribute referencing a nonexistent anchor, a tie referencing an undefined knot, or a duplicate mnemonic all produce clear errors
  4. The three-layer schema is enforced -- XML-compatible core fields, YAML extension fields, and export-incompatible markers are distinguishable in the model structure
  5. Mnemonic collisions are detected deterministically (sorted by name) with explicit override support in YAML
**Plans**: 3 plans

Plans:
- [ ] 06-01: Pydantic spec models and YAML schema (SPEC-01, SPEC-05, SPEC-06)
- [ ] 06-02: Spec validation engine with line numbers (SPEC-03, SPEC-04, SPEC-07)
- [ ] 06-03: CLI `dab init` scaffold command (SPEC-02)

### Phase 7: SQL Generation Engine
**Goal**: Users can generate correct, idempotent, bitemporal SQL for any supported dialect from a valid YAML spec
**Depends on**: Phase 6
**Requirements**: GEN-01, GEN-02, GEN-03, GEN-04, GEN-05, GEN-06, GEN-07, GEN-08, GEN-09, GEN-10
**Success Criteria** (what must be TRUE):
  1. Running `architect dab generate` on a valid spec produces one SQL file per entity (anchor with its attributes, each tie, each knot) plus staging table DDL in the output directory
  2. Generated DDL is idempotent -- running it twice against a database produces no errors and no duplicate objects (CREATE TABLE IF NOT EXISTS or equivalent)
  3. Generated DML uses MERGE/UPSERT patterns that are safe to re-run, with dialect-appropriate syntax (ON CONFLICT for PostgreSQL, MERGE for SQL Server/Snowflake)
  4. Every generated table includes bitemporal columns (`changed_at` for valid time, `recorded_at` for transaction time) and metadata columns (`metadata_recorded_at`, `metadata_recorded_by`, `metadata_id`)
  5. Running generation twice on the same spec produces byte-identical output -- no timestamps, UUIDs, or nondeterminism (git-friendly)
  6. `--format raw` produces plain SQL files; `--format bruin` produces SQL with Bruin YAML frontmatter (materialization strategies: merge for historized, view for current state)
**Plans**: 3 plans

Plans:
- [ ] 07-01: SQLGlot AST builders for DDL -- anchors, attributes, ties, knots, staging tables (GEN-01, GEN-02, GEN-03, GEN-04, GEN-06, GEN-07, GEN-08, GEN-10)
- [ ] 07-02: SQLGlot AST builders for DML -- MERGE/UPSERT loading patterns (GEN-05)
- [ ] 07-03: CLI `dab generate` command with format and dialect flags (GEN-09)

### Phase 8: Keyset Identity and Staging Mappings
**Goal**: Users can define multi-source staging mappings with keyset identity and generate loading SQL that tracks data provenance
**Depends on**: Phase 7
**Requirements**: KEY-01, KEY-02, KEY-03, KEY-04, KEY-05, STG-01, STG-02, STG-03, STG-04, STG-05
**Success Criteria** (what must be TRUE):
  1. The `KeysetIdentity` module can parse `entity@system~tenant|natural_key` strings and format them back, surviving round-trips through Hypothesis property-based tests including delimiter-heavy inputs (`@@`, `~~`, `||`)
  2. Generated SQL constructs keyset identity strings from staging source columns using the canonical format, with proper escaping of delimiters in natural key values and NULL propagation (if natural key is NULL, entire keyset is NULL)
  3. A spec with multiple staging tables feeding the same anchor generates correct loading SQL for each source, with system and tenant identifiers embedded in the keyset
  4. Column-level staging mappings (`staging_table.column` maps to `anchor.attribute`) produce INSERT...SELECT SQL with explicit column lineage
  5. Conflict resolution strategy is declared per multi-source anchor in the YAML spec, and generated SQL applies deterministic ordering (explicit priority, then system name)
**Plans**: 3 plans

Plans:
- [ ] 08-01: KeysetIdentity module with parse/format, null safety, and Hypothesis tests (KEY-01, KEY-02, KEY-04, KEY-05)
- [ ] 08-02: Staging mapping models and SQL generation (STG-01, STG-02, STG-03, STG-04, KEY-03)
- [ ] 08-03: Multi-source conflict resolution (STG-05)

### Phase 9: XML Interoperability
**Goal**: Users can round-trip specifications between YAML and the official Anchor Modeler XML format without silent data loss
**Depends on**: Phase 6
**Requirements**: INTOP-01, INTOP-02, INTOP-03, INTOP-04
**Success Criteria** (what must be TRUE):
  1. Running `architect dab import model.xml` converts an official Anchor Modeler XML file into a valid YAML spec, preserving all anchor.xsd elements losslessly
  2. Running `architect dab export spec.yaml` converts a YAML spec into valid Anchor XML that passes lxml XSD validation against anchor.xsd
  3. Export warns the user about YAML-only extensions (staging mappings, keyset identity) being dropped and requires `--force` to proceed
  4. An XML file imported to YAML and exported back to XML produces equivalent XML for the XML-compatible core (round-trip validation)
**Plans**: 2 plans

Plans:
- [ ] 09-01: XML import -- Anchor Modeler XML to YAML (INTOP-01)
- [ ] 09-02: XML export with extension warnings and round-trip validation (INTOP-02, INTOP-03, INTOP-04)

### Phase 10: Northwind Reference Example
**Goal**: A complete, runnable Northwind example validates every feature of the DAB generation pipeline end-to-end
**Depends on**: Phase 8 (keyset + staging), Phase 9 (import/export)
**Requirements**: NWND-01, NWND-02
**Success Criteria** (what must be TRUE):
  1. A pre-filled Northwind YAML spec exists covering Orders, Customers, Products, Employees, Suppliers, Categories, and Shippers with keyset identity and staging mappings from Northwind OData source
  2. Running `architect dab generate` on the Northwind spec produces valid SQL that exercises all features: keyset construction, staging-to-anchor loading, bitemporal columns, metadata columns, idempotent DDL/DML, and deterministic output
**Plans**: 1 plan

Plans:
- [ ] 10-01: Northwind spec and end-to-end validation (NWND-01, NWND-02)

---

## Progress

**Execution Order:**
Phases execute in numeric order: 6 -> 7 -> 8 -> 9 -> 10
(Phase 9 depends only on Phase 6, so it could run in parallel with 7-8 if needed)

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Project Foundation | v0.1.0 | 2/2 | Complete | 2026-02-07 |
| 2. CLI Scaffolding | v0.1.0 | 2/2 | Complete | 2026-02-07 |
| 3. Agent Definitions + OpenCode Integration | v0.1.0 | 2/2 | Complete | 2026-02-08 |
| 4. Agent Quality + Modeling Workflows | v0.1.0 | 3/3 | Complete | 2026-02-08 |
| 5. Pre-commit Framework Migration | v0.2.0 | 1/1 | Complete | 2026-02-08 |
| 6. YAML Schema Foundation and Spec Validation | v0.3.0 | 0/3 | Not started | - |
| 7. SQL Generation Engine | v0.3.0 | 0/3 | Not started | - |
| 8. Keyset Identity and Staging Mappings | v0.3.0 | 0/3 | Not started | - |
| 9. XML Interoperability | v0.3.0 | 0/2 | Not started | - |
| 10. Northwind Reference Example | v0.3.0 | 0/1 | Not started | - |

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-09 -- v0.3.0 phases 6-10 added*
