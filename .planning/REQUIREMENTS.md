# Requirements: Data Architect v0.3.0 — DAB Generation

**Defined:** 2026-02-09
**Core Value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate — not just template generation. v0.3.0 adds deterministic SQL generation from YAML specs.

## v0.3.0 Requirements

Requirements for DAB generation milestone. Each maps to roadmap phases.

### Specification Management

- [ ] **SPEC-01**: YAML schema defined as superset of official anchor.xsd — anchors, attributes, ties, knots, nexuses, roles, keys — with extension fields for staging mappings and keyset identity
- [ ] **SPEC-02**: `architect dab init` scaffolds blank YAML spec template with inline comments explaining each section and field
- [ ] **SPEC-03**: Spec validation checks referential integrity (attributes reference valid anchors), mnemonic uniqueness, and required fields
- [ ] **SPEC-04**: Validation errors report line numbers for fast debugging of large specs
- [ ] **SPEC-05**: Pydantic frozen models for runtime validation of spec structure, with cross-field validators enforcing anchor.xsd assertions
- [ ] **SPEC-06**: Three-layer schema design — XML-compatible core, YAML extension fields, export-incompatible markers — preventing lossy roundtrips
- [ ] **SPEC-07**: Mnemonic collision detection with deterministic generation (sorted by name) and explicit override support in YAML

### SQL Generation

- [ ] **GEN-01**: `architect dab generate` produces idempotent SQL per entity (anchors, attributes, ties, knots) from valid YAML spec
- [ ] **GEN-02**: SQLGlot AST-based generation — build SQL as Python ASTs, compile to any dialect (PostgreSQL, SQL Server, Snowflake, etc.)
- [ ] **GEN-03**: Per-entity output files — one `.sql` file per anchor (with its attributes), tie, and knot, organized in output directory
- [ ] **GEN-04**: Idempotent DDL — CREATE TABLE IF NOT EXISTS, additive-only schema evolution (Anchor convention), safe to re-run
- [ ] **GEN-05**: Idempotent DML — MERGE/UPSERT patterns for loading staging data into anchor tables, dialect-aware
- [ ] **GEN-06**: Bitemporal support — `changed_at` column for valid time (when data was in effect) and `recorded_at` column for transaction time (when we learned about it)
- [ ] **GEN-07**: Metadata columns auto-generated in every table — `metadata_recorded_at`, `metadata_recorded_by`, `metadata_id`
- [ ] **GEN-08**: Deterministic output — same spec produces identical SQL every time, no timestamps/UUIDs/randomness (git-friendly)
- [ ] **GEN-09**: Output format flag — `--format raw` for plain SQL, `--format bruin` for SQL with Bruin YAML frontmatter (materialization strategies: merge for SCD2, view for current state)
- [ ] **GEN-10**: `dab generate` also generates staging table DDL — CREATE TABLE for each staging table defined in the spec, with columns matching the staging mapping definitions

### Keyset Identity

- [ ] **KEY-01**: Keyset format `entity@system~tenant|natural_key` — encodes entity type, source system, tenant, and source natural key in a single VARCHAR
- [ ] **KEY-02**: Canonical escape sequences for delimiter collision — `@@` for literal `@`, `~~` for literal `~`, `||` for literal `|`
- [ ] **KEY-03**: SQL generation for keyset construction from source natural key columns defined in staging mappings
- [ ] **KEY-04**: `KeysetIdentity` module with `parse()` and `format()` functions, property-based tested with Hypothesis for round-trip correctness
- [ ] **KEY-05**: Null safety — if the natural key expression evaluates to NULL, the entire keyset must be NULL (not `entity@system~tenant|`), enforced in both Python and generated SQL

### Staging Mappings

- [ ] **STG-01**: Column-level staging mappings in spec — `staging_table.column` maps to `anchor.attribute` with explicit lineage
- [ ] **STG-02**: Multiple staging tables per anchor — same anchor fed by different source systems (e.g., Order from Northwind + SAP)
- [ ] **STG-03**: System and tenant identifiers per staging source — used in keyset construction
- [ ] **STG-04**: SQL generation for staging-to-anchor loading — INSERT...SELECT with column mappings, keyset construction, metadata population
- [ ] **STG-05**: Conflict resolution strategy per multi-source anchor — explicit priority declaration, deterministic ordering

### Interoperability

- [ ] **INTOP-01**: `architect dab import` converts official Anchor Modeler XML → YAML spec (lossless for standard anchor.xsd elements)
- [ ] **INTOP-02**: `architect dab export` converts YAML → official Anchor XML (validated against anchor.xsd with lxml)
- [ ] **INTOP-03**: Export warns about YAML-only extension features (staging mappings, keyset identity) being dropped, requires `--force` to proceed
- [ ] **INTOP-04**: Round-trip validation — XML → YAML → XML produces equivalent XML for the XML-compatible core

### Northwind Example

- [ ] **NWND-01**: Pre-filled Northwind YAML spec covering Orders, Customers, Products, Employees, Suppliers, Categories, Shippers with keyset identity and staging mappings
- [ ] **NWND-02**: Northwind spec generates valid, runnable SQL that validates all features end-to-end (keyset, staging, bitemporality, idempotency)

## Deferred (v0.4.0+)

### DAS Generation

- **DAS-01**: `architect generate` produces DAS scripts from source schemas (deterministic)
- **DAS-02**: Auto-detect staging tables from source schemas (Swagger, ERD, OData)

### DAR Generation

- **DAR-01**: `architect generate` produces DAR scripts from DAB output (deterministic)
- **DAR-02**: Unified Star Schema bridge table generation from Anchor Model

### Additional Dialects

- **DIAL-01**: Oracle dialect (PL/SQL, sequences, 30-char identifier limits)
- **DIAL-02**: Vertica dialect (analytics-specific platform)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web UI / GUI for spec editing | CLI-first tool. Official Anchor Modeler GUI exists; use import/export for visual roundtrip |
| Auto-detect anchors from source schema | CLP modeling requires business context (probabilistic). Agents handle this. DAS layer (v0.4.0+) |
| Template customization language | Maintenance burden, users fork and can't upgrade. Improve defaults instead |
| Real-time CDC generation | Batch-first strategy. Anchor designed for batch ELT. Streaming deferred |
| ORM model generation | Anchor's 6NF not designed for ORM navigation. DAR layer provides consumption views |
| Inline SQL in spec | Keeps spec pure metadata. Custom logic belongs in DAS/DAR layers |
| Generate entire pipeline (end-to-end) | Scope explosion. DAB is one layer. Users integrate into their orchestration |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SPEC-01 | Phase 6 | Pending |
| SPEC-02 | Phase 6 | Pending |
| SPEC-03 | Phase 6 | Pending |
| SPEC-04 | Phase 6 | Pending |
| SPEC-05 | Phase 6 | Pending |
| SPEC-06 | Phase 6 | Pending |
| SPEC-07 | Phase 6 | Pending |
| GEN-01 | Phase 7 | Pending |
| GEN-02 | Phase 7 | Pending |
| GEN-03 | Phase 7 | Pending |
| GEN-04 | Phase 7 | Pending |
| GEN-05 | Phase 7 | Pending |
| GEN-06 | Phase 7 | Pending |
| GEN-07 | Phase 7 | Pending |
| GEN-08 | Phase 7 | Pending |
| GEN-09 | Phase 7 | Pending |
| GEN-10 | Phase 7 | Pending |
| KEY-01 | Phase 8 | Pending |
| KEY-02 | Phase 8 | Pending |
| KEY-03 | Phase 8 | Pending |
| KEY-04 | Phase 8 | Pending |
| KEY-05 | Phase 8 | Pending |
| STG-01 | Phase 8 | Pending |
| STG-02 | Phase 8 | Pending |
| STG-03 | Phase 8 | Pending |
| STG-04 | Phase 8 | Pending |
| STG-05 | Phase 8 | Pending |
| INTOP-01 | Phase 9 | Pending |
| INTOP-02 | Phase 9 | Pending |
| INTOP-03 | Phase 9 | Pending |
| INTOP-04 | Phase 9 | Pending |
| NWND-01 | Phase 10 | Pending |
| NWND-02 | Phase 10 | Pending |

**Coverage:**
- v0.3.0 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-02-09*
*Last updated: 2026-02-09 after user feedback (staging DDL + keyset null safety)*
