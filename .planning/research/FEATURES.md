# Feature Research: DAB Specification Management and Anchor Modeling Code Generation

**Domain:** DAB specification management, Anchor Modeling code generation, multi-dialect SQL generation
**Researched:** 2026-02-09
**Confidence:** MEDIUM (Anchor Modeling patterns well-established from official tools; YAML validation and SQL generation patterns mature; keyset identity and multi-source staging are novel extensions)

## Context

This research covers features for `architect dab` commands in v0.3.0:
- `architect dab init` -- scaffold blank YAML spec template
- `architect dab generate` -- YAML spec → idempotent SQL per entity (Bruin assets or raw SQL)
- `architect dab import` -- official Anchor XML → YAML
- `architect dab export` -- YAML → official Anchor XML (drops extensions)

**v0.3.0 scope: DAB generation only.** Agents (v0.1.0) optionally produce filled specs. Generators consume any valid spec (manual or agent-produced).

The YAML spec is a **superset of official Anchor XML** (anchor.xsd). Extensions: staging table mappings (column-level, multi-source), keyset identity scheme (`entity@system~tenant|natural_key`). Interoperable with official Anchor Modeler via import/export.

Research dimensions:
1. Specification management patterns -- YAML validation, schema definition, error reporting
2. Anchor Modeling code generation -- SQL patterns from official tooling (Sisula, directives)
3. Multi-dialect SQL generation -- abstraction layers, template approaches
4. Idempotent SQL patterns -- IF NOT EXISTS, CREATE OR REPLACE, safe re-runs
5. Bruin asset integration -- asset format, materialization strategies
6. Staging table mapping -- column-level, multi-source patterns
7. Keyset identity management -- natural key encoding, provenance tracking

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Spec scaffold** (`dab init`) | Every code generator starts with "create new project" | LOW | Blank YAML template with schema structure. Follows proven `architect init` pattern from v0.1.0 |
| **YAML spec validation** | Users expect immediate feedback on schema correctness before generation | MEDIUM | JSON Schema or custom validator against official anchor.xsd elements + extensions. Critical for preventing downstream SQL errors |
| **SQL generation** (`dab generate`) | Core value -- spec exists to produce SQL | HIGH | Idempotent CREATE TABLE/VIEW per entity. Multi-dialect (PostgreSQL first, SQL Server/Snowflake after). Anchor conventions: surrogate keys, metadata columns, 6NF structure |
| **Idempotent SQL output** | Re-running generator must be safe, not destructive | MEDIUM | IF NOT EXISTS, CREATE OR REPLACE patterns. Existing tables untouched. Additive-only schema evolution (Anchor convention) |
| **Per-entity SQL files** | SQL organized by entity, not monolithic | LOW | One file per anchor + attributes + ties. Matches Bruin asset-per-table pattern. Easier to review/debug than 5000-line scripts |
| **Deterministic output** | Same input always produces same SQL (git-friendly) | LOW | No timestamps, UUIDs, or randomness in generated code. Diffable output |
| **Validation error messages with line numbers** | Fast error location in large specs | LOW | Parser reports `line 47: missing required field 'identity'`. Saves debugging time on 500+ line specs |
| **Import from official Anchor XML** (`dab import`) | Users have existing models in Anchor Modeler tool | MEDIUM | Parse anchor.xsd-compliant XML → YAML. Lossless for standard elements. Warn on unsupported features |
| **Export to official Anchor XML** (`dab export`) | Roundtrip to official tooling for visual modeling | MEDIUM | YAML → anchor.xsd-compliant XML. Drop extensions (staging mappings, keyset identity). Validate output against XSD |
| **Multi-dialect SQL support** | Anchor Modeler supports 5+ dialects, users expect parity | HIGH | PostgreSQL, SQL Server, Snowflake at minimum. Oracle/Vertica deferred. Dialect parameter: `--dialect postgres` |
| **Metadata columns auto-generated** | Audit trail without user specification | LOW | Every table gets `metadata_recorded_at`, `metadata_recorded_by`, `metadata_id`. Anchor convention for lineage |
| **Anchor Modeling conventions enforced** | Users choose Anchor for methodology compliance | MEDIUM | Surrogate keys (auto-increment/sequence), 6NF structure (one attribute per table), historization (valid_from/valid_to), knot tables for shared values |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Keyset identity scheme** | Provenance tracking without lookup tables | HIGH | `entity@system~tenant|natural_key` encodes source in key itself. No "where did this come from?" queries. Enables multi-tenant, multi-source anchors. UNIQUE vs official Anchor (surrogate-only) |
| **Multi-source staging mappings** | One anchor fed by multiple systems | HIGH | `staging_tables[]` array per anchor. Union semantics. Handles system-specific column names mapping to same attribute. UNIQUE vs official Anchor (ETL external) |
| **Column-level staging mappings** | Explicit source → target lineage in spec | MEDIUM | `staging_tables[].columns[]` with `maps_to: anchor.attribute`. Clear data lineage. Generates SQL to map columns. Official Anchor separates ETL from modeling |
| **YAML superset of Anchor XML** | Best of both: YAML ergonomics + XML interop | MEDIUM | Roundtrip import/export with official tooling. Extensions documented clearly. Official Anchor users can adopt incrementally |
| **Bruin asset format output** | Modern data pipeline tool integration | MEDIUM | Generate `.sql` with Bruin YAML frontmatter (materialization: merge/view, columns, checks). Alternative to raw SQL. Materialization strategies match Anchor patterns (merge for historization, view for current state) |
| **Northwind example spec** | Reference implementation for learning | LOW | Pre-filled YAML for Northwind OData. Users can `dab init --example northwind` to start with working spec. Validates all features |
| **Dependency ordering** | SQL scripts ordered by foreign keys | MEDIUM | Knots → Anchors → Attributes → Ties. Knots first (referenced by attributes). Ties last (reference anchors). Prevents FK constraint errors on fresh database |
| **Dry-run mode** | Preview SQL without writing files | LOW | `dab generate --dry-run` prints to stdout. Safe exploration of what would be generated |
| **Diff-friendly SQL formatting** | Clean git diffs on spec changes | LOW | Consistent indentation, keyword casing, column ordering. One column per line in CREATE TABLE. Trailing commas optional per dialect |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **GUI for spec editing** | Visual tools feel more accessible | Adds complexity, breaks CLI-first workflow, requires frontend stack, maintenance burden | Official Anchor Modeler GUI exists for visual modeling. Use `dab import/export` for roundtrip. YAML is the editing interface |
| **Auto-detect anchors from source schema** | Seems to save time upfront | CLP modeling requires business context and debate (probabilistic). Auto-detection produces bad models. Anchor ≠ table. This is what agents are for | Use Data Architect + agents (v0.1.0) to produce spec through CLP debate. Deterministic detection deferred to DAS layer (v0.4.0+) |
| **Support for non-Anchor patterns** | "Why can't I generate star schema directly?" | Tool is opinionated about Anchor Modeling. Mixing methodologies creates confusion. Star schema is DAR layer, not DAB | Anchor is DAB layer. DAR (USS) generation is separate concern (v0.4.0+). Clear separation of concerns |
| **Real-time CDC generation** | Modern stacks use streaming | Batch-first strategy. Streaming adds complexity (state, ordering, late arrival). Anchor is designed for batch ELT. Prove batch first | Generate batch SQL first. Streaming can be added later if validated need exists |
| **Template customization language** | "Let me tweak the SQL templates" | Every customization is a maintenance burden. Users fork templates and can't upgrade. Diverges from Anchor conventions. Creates N forks | Provide dialect parameter. If SQL doesn't match needs, open issue to improve defaults for everyone. Customization = forking |
| **Inline SQL in spec** | "Let me add custom transformations" | Spec becomes half-declarative, half-imperative. Hard to validate, version, test. Mixing concerns | Keep spec pure metadata. Custom logic belongs in staging layer (DAS) or consumption layer (DAR), not DAB spec |
| **Generate entire pipeline** | "Give me end-to-end from source to BI tool" | Scope explosion. Every org has different orchestration (Airflow, dbt, Bruin, Dagster). Hard to support all. DAB is one layer | Generate DAB SQL. Users integrate into their orchestration tool of choice. Bruin asset format is first-class but optional |
| **ORM integration** | "Generate SQLAlchemy/TypeORM models" | Anchor's 6NF structure (one attribute per table) is designed for set-based SQL, not ORM navigation. ORM impedance mismatch | DAR layer (USS) is where consumption views live. Generate views for ORM consumption, not ORM models for Anchor tables |

## Feature Dependencies

```
YAML Schema Definition
    └──enables──> Spec Scaffold (`dab init`)
                       └──enables──> Spec Validation
                                        └──enables──> SQL Generation (`dab generate`)
                                                         └──enables──> Bruin Asset Output

Spec Validation
    └──requires──> Anchor XML Schema (anchor.xsd) knowledge
    └──requires──> Extension Schema (staging, keyset) definition
    └──enables──> Line Number Error Reporting

Import (`dab import`)
    └──requires──> Anchor XML Parser (lxml with XSD)
    └──requires──> YAML Schema Definition
    └──produces──> Valid YAML Spec

Export (`dab export`)
    └──requires──> Spec Validation (must be valid before export)
    └──requires──> Anchor XML Writer (compliant with anchor.xsd)
    └──drops──> Extensions (staging, keyset)

Multi-dialect SQL
    └──requires──> Dialect Abstraction (SQLGlot or Jinja2 per dialect)
    └──requires──> Dialect-specific keywords (SERIAL vs IDENTITY vs AUTOINCREMENT)

Keyset Identity
    └──requires──> Staging Mappings (natural key columns defined)
    └──generates──> SQL to construct `entity@system~tenant|natural_key`

Multi-source Staging Mappings
    └──requires──> Column-level Staging Mappings (foundation)
    └──requires──> Union semantics (same anchor, multiple sources)

Dependency Ordering
    └──requires──> Spec Validation (detect circular dependencies)
    └──requires──> Graph traversal (topological sort)

Northwind Example
    └──requires──> Spec Scaffold (template structure)
    └──requires──> Import (OData metadata → Anchor XML → YAML)
    └──validates──> All features (keyset, multi-source, generation)

Bruin Asset Output
    └──requires──> SQL Generation (base functionality)
    └──adds──> YAML frontmatter (materialization, columns, checks)
```

### Dependency Notes

- **YAML Schema is foundation:** Can't scaffold, validate, or generate without knowing structure. Must define anchor.xsd elements + extensions early
- **Validation gates generation:** Generator assumes valid input. "Garbage in, garbage out" without validation. Line numbers critical for debugging large specs
- **Import/Export require XSD compliance:** Must parse/write official anchor.xsd format. Python `lxml` with XSD validation. Extensions are additive (import keeps them, export drops them)
- **Multi-dialect requires abstraction:** Two approaches: (1) Jinja2 templates per dialect, (2) SQLGlot transpilation. Sisula approach (regex substitution) is fragile, don't replicate
- **Keyset requires Staging Mappings:** Can't construct `entity@system~tenant|natural_key` without knowing which source columns form natural key. Staging mappings define column lineage
- **Multi-source enhances Staging:** Single-source is MVP. Multi-source adds union semantics (same anchor from multiple systems). Defer until single-source validated
- **Dependency Ordering prevents errors:** SQL must create knots before attributes reference them. Ties reference anchors so must come last. Graph sort is standard algorithm
- **Northwind validates everything:** Pre-filled spec exercises all features. If Northwind generates clean SQL, features work

## MVP Definition

### Launch With (v0.3.0)

Minimum viable product -- what's needed to validate DAB generation concept with Northwind example.

- [x] **YAML schema definition** -- Anchor elements (anchor, attribute, tie, knot) + extensions (staging_tables, keyset_identity). Document structure in schema comments
- [x] **Spec scaffold (`dab init`)** -- Generate blank YAML template with all sections, inline comments explaining each field. Same UX as `architect init` (--force, --dry-run flags)
- [x] **Spec validation** -- Parse YAML, validate required fields, check referential integrity (attributes reference valid anchors), report line numbers on errors. Fail fast before generation
- [x] **SQL generation (`dab generate`)** -- Produce idempotent CREATE TABLE + Anchor conventions (surrogate keys, metadata columns, 6NF structure). **PostgreSQL dialect first** (proven, open-source, common)
- [x] **Per-entity output** -- One `.sql` file per anchor (with attributes/ties). Organized in `output/` directory. Filenames: `anchor_name.sql`, `tie_anchor1_anchor2.sql`
- [x] **Idempotent SQL** -- IF NOT EXISTS for CREATE TABLE. Additive-only schema evolution (Anchor convention). Safe to re-run on existing database
- [x] **Keyset identity generation** -- SQL to construct `entity@system~tenant|natural_key` from source natural key columns. VARCHAR column in anchor table
- [x] **Staging mappings (single source)** -- Specify source table → anchor attribute mappings in spec. One `staging_table` per anchor for MVP. Multi-source deferred
- [x] **Northwind example** -- Pre-filled YAML spec for Northwind OData as reference implementation and test case. Validates all MVP features
- [x] **Deterministic output** -- No timestamps, random IDs. Same spec → same SQL every time. Git-friendly diffs
- [x] **Metadata columns** -- Auto-generate `metadata_recorded_at`, `metadata_recorded_by`, `metadata_id` in every table
- [x] **Validation error line numbers** -- Parser reports line number for every error. Fast debugging

### Add After Validation (v0.3.x)

Features to add once core is working and validated with Northwind example.

- [ ] **Import (`dab import`)** -- Parse official Anchor XML → YAML. Enables users to migrate existing Anchor Modeler projects — *trigger: user requests migration from Anchor Modeler*
- [ ] **Export (`dab export`)** -- YAML → official Anchor XML. Enables roundtrip to Anchor Modeler GUI for visual editing — *trigger: users want visual model view*
- [ ] **Multi-source staging mappings** -- Multiple `staging_tables[]` per anchor. Union semantics. Handles same entity from different systems — *trigger: multi-source use case validated (e.g., Customer from CRM + ERP)*
- [ ] **SQL Server dialect** -- Second dialect proves abstraction layer works. Common in enterprise — *trigger: SQL Server user request*
- [ ] **Snowflake dialect** -- Third dialect, common in modern cloud stacks — *trigger: Snowflake user request*
- [ ] **Bruin asset format** -- Output `.sql` with Bruin YAML frontmatter. Alternative to raw SQL. Materialization: merge (SCD2), view (current state) — *trigger: Bruin user request or partnership*
- [ ] **Dry-run mode** -- `--dry-run` flag to preview without writing files — *trigger: user wants to inspect SQL before committing*
- [ ] **Dependency ordering** -- Knots → Anchors → Attributes → Ties. Prevents FK constraint errors on fresh database — *trigger: complex schema with many ties fails on creation*
- [ ] **Diff-friendly formatting** -- Consistent SQL style, one column per line, trailing commas — *trigger: users complain about noisy git diffs*

### Future Consideration (v0.4.0+)

Features to defer until DAB generation is proven and adopted.

- [ ] **Oracle dialect** -- Legacy enterprise systems — *defer: smaller user base, Oracle-specific complexity (PL/SQL, sequences)*
- [ ] **Vertica dialect** -- Analytics-specific platform — *defer: niche use case*
- [ ] **Template customization** -- Allow users to override SQL templates per dialect — *defer: maintenance burden, diverges from conventions, users can't upgrade*
- [ ] **Incremental generation** -- Only regenerate changed entities — *defer: premature optimization, full generation is fast enough (<1s for Northwind)*
- [ ] **Schema diff tool** -- Compare two versions of spec, show changes — *defer: git diff on YAML is sufficient for v1*
- [ ] **Metadata registry integration** -- Push generated schema to catalog (Datahub, Amundsen) — *defer: external integration, not core value*
- [ ] **DAS generation** -- Source schemas → staging tables (deterministic) — *defer: separate milestone (v0.4.0+)*
- [ ] **DAR generation** -- DAB → USS views (deterministic) — *defer: separate milestone (v0.4.0+)*

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Notes |
|---------|------------|---------------------|----------|-------|
| YAML schema definition | HIGH | LOW | P1 | Foundation for all other features. Must define early |
| Spec scaffold (`dab init`) | HIGH | LOW | P1 | Follows proven `architect init` pattern from v0.1.0 |
| Spec validation | HIGH | MEDIUM | P1 | Prevents downstream SQL errors. Critical quality gate |
| SQL generation (PostgreSQL) | HIGH | HIGH | P1 | Core value delivery. Start with PostgreSQL (open, common) |
| Per-entity output | HIGH | LOW | P1 | Matches Anchor entity-per-table. Better UX than monolith |
| Idempotent SQL | HIGH | MEDIUM | P1 | Safe re-runs essential for tooling. IF NOT EXISTS patterns |
| Keyset identity | HIGH | MEDIUM | P1 | Differentiator, enables multi-source. Generates construction SQL |
| Staging mappings (single) | HIGH | MEDIUM | P1 | Required for SQL generation from sources |
| Northwind example | MEDIUM | MEDIUM | P1 | Reference for learning, validates all features |
| Deterministic output | HIGH | LOW | P1 | Git-friendly, reproducible builds. No randomness |
| Metadata columns | HIGH | LOW | P1 | Anchor convention, expected by users |
| Validation line numbers | MEDIUM | LOW | P1 | Better UX, not essential but cheap to add |
| Import from XML | MEDIUM | MEDIUM | P2 | Enables migration from Anchor Modeler. Nice-to-have |
| Export to XML | MEDIUM | MEDIUM | P2 | Roundtrip to official tooling. Nice-to-have |
| Multi-source staging | MEDIUM | HIGH | P2 | Powerful but complex. Defer until single-source proven |
| SQL Server dialect | MEDIUM | MEDIUM | P2 | Proves multi-dialect works. Add on demand |
| Snowflake dialect | MEDIUM | MEDIUM | P2 | Modern stack support. Add on demand |
| Bruin asset format | MEDIUM | MEDIUM | P2 | Nice integration, not essential. Add if Bruin users request |
| Dry-run mode | LOW | LOW | P2 | QOL improvement, low effort |
| Dependency ordering | MEDIUM | MEDIUM | P2 | Prevents errors in complex schemas. Add if needed |
| Diff-friendly formatting | LOW | LOW | P2 | Better git diffs. Nice-to-have |
| Oracle/Vertica dialects | LOW | HIGH | P3 | Niche use cases, high complexity |
| Template customization | LOW | HIGH | P3 | Maintenance burden, divergence risk |
| Incremental generation | LOW | MEDIUM | P3 | Premature optimization for v1 |
| Schema diff tool | LOW | MEDIUM | P3 | Git diff sufficient for v1 |
| Metadata registry | LOW | HIGH | P3 | External concern, not core |

**Priority key:**
- P1: Must have for v0.3.0 launch -- validates DAB generation concept
- P2: Should have, add in v0.3.x when users request -- enhances core value
- P3: Nice to have, defer to v0.4.0+ -- not essential for adoption

## Competitor Feature Analysis

| Feature | Official Anchor Modeler (GUI) | sqldef (Idempotent SQL) | DBT (Transform Tool) | Liquibase (Migrations) | Data Architect |
|---------|-------------------------------|-------------------------|----------------------|------------------------|----------------|
| **Visual modeling** | ✓ Drag-drop GUI | ✗ None | ✗ None | ✗ None | ✗ Use official tool, roundtrip via import/export |
| **XML import/export** | ✓ Native format | ✗ N/A | ✗ N/A | ✗ N/A | ✓ Roundtrip to official Anchor XML |
| **Multi-dialect SQL** | ✓ 5 dialects (Sisula) | ✓ 4 dialects | ✓ 10+ dialects (adapters) | ✓ All major DBs | ✓ 3+ dialects (PostgreSQL, SQL Server, Snowflake) |
| **Idempotent generation** | ✓ IF NOT EXISTS | ✓ Core feature | ✓ Incremental models | ✓ Changesets | ✓ IF NOT EXISTS, CREATE OR REPLACE |
| **YAML/code-first** | ✗ GUI-only | ✓ Plain SQL DDL | ✓ SQL + YAML config | ✓ XML/YAML/SQL | ✓ YAML spec as source of truth |
| **Staging mappings** | ✗ Manual ETL | ✗ Schema-only | ✗ Transform-only | ✗ Schema-only | ✓ Column-level, multi-source |
| **Keyset identity** | ✗ Surrogate keys only | ✗ N/A | ✗ N/A | ✗ N/A | ✓ `entity@system~tenant\|natural_key` |
| **CLI tool** | ✗ Browser-based | ✓ CLI binary | ✓ CLI binary | ✓ CLI binary | ✓ Python CLI |
| **Bruin integration** | ✗ None | ✗ None | ⊕ Similar (dbt models) | ✗ None | ✓ Optional Bruin assets |
| **Anchor methodology** | ✓ Native | ✗ Generic schemas | ✗ Transform layer | ✗ Generic schemas | ✓ Native + extensions |
| **Temporal modeling** | ✓ 6NF, historized | ✗ User responsibility | ⊕ SCD2 patterns | ✗ User responsibility | ✓ 6NF, historized (Anchor) |
| **Agent integration** | ✗ None | ✗ None | ✗ None | ✗ None | ✓ Agents produce spec via debate (v0.1.0) |
| **Dependency ordering** | ✓ Smart | ✗ User orders | ✗ ref() function | ✓ Preconditions | ✓ Automatic (topological sort) |

**Key differentiators vs competitors:**
- **vs Official Anchor Modeler:** CLI-first (not browser GUI), YAML-based (not XML-only), agent integration (CLP debate produces spec), keyset identity, staging mappings. Roundtrip to GUI for visual modeling via import/export
- **vs sqldef:** Methodology-aware (Anchor conventions), not generic DDL. Staging mappings (source → target lineage), keyset identity (provenance), agent-produced specs (probabilistic → deterministic boundary)
- **vs dbt:** Different layer (DAB not DAR), Anchor methodology (6NF not star), declarative spec (not transform SQL). dbt consumes DAB output (v0.4.0+ DAR generation). Complementary, not competitive
- **vs Liquibase:** Anchor-specific (not generic migrations), full spec (not incremental changesets), idempotent (not stateful history). Different philosophy: declare desired state, not migration path

**Where we're weaker:**
- No visual GUI (intentional -- official Anchor Modeler exists, use import/export for roundtrip)
- Fewer dialects at launch (will expand based on user demand -- PostgreSQL/SQL Server/Snowflake first)
- No incremental generation (full regeneration fine for v1 -- Northwind <1s)

**Where we're stronger:**
- **Only tool combining Anchor Modeling + staging mappings + keyset identity** -- unique position
- YAML ergonomics with XML interoperability (best of both worlds)
- Agent debate produces spec (probabilistic → deterministic boundary) -- agents in v0.1.0, generators in v0.3.0
- Multi-source staging mappings enable complex source → anchor scenarios (same Customer anchor from CRM + ERP + legacy system)
- Keyset identity encodes provenance without lookup tables (`customer@crm~acme|12345` vs `customer@erp~acme|CUST-890`)

## Dependencies on Existing Features (v0.1.0/v0.2.0)

| New Feature (v0.3.0) | Depends On (v0.1.0/v0.2.0) | Reason |
|----------------------|----------------------------|--------|
| `dab init` scaffold | `architect init` pattern (v0.1.0) | Proven CLI scaffolding approach, same flags (--force, --dry-run, --dir), same UX, same symbol output |
| Spec validation | Test framework (pytest, v0.1.0) | Validation requires extensive test coverage for edge cases (92.77% coverage baseline) |
| SQL generation | Pure functional style (v0.1.0) | Immutable specs → deterministic SQL. No side effects. Frozen dataclasses for data, pure functions for behavior |
| Error messages | Symbol output pattern (v0.1.0) | User-friendly errors with line numbers, not stack traces. Follows CLI UX from `architect init` |
| `dab` subcommands | CLI infrastructure (Click, v0.1.0) | Subcommand routing (`architect dab init`), flag parsing, help text generation |
| TDD approach | 92.77% coverage baseline (v0.1.0) | SQL generation is complex, requires comprehensive tests. TDD mandatory per project constraints |
| Makefile targets | `make check` (v0.1.0) | Code generation quality gates (lint, type, test). Same tooling for consistency |
| Pre-commit hooks | `.pre-commit-config.yaml` (v0.2.0) | Prevent committing invalid SQL templates or broken generators. Same quality enforcement |
| Dynamic versioning | Git tags (v0.1.0) | Consistent versioning across CLI + generated SQL comments (`-- Generated by data-architect v0.3.0`) |
| UV build system | UV + Hatchling (v0.1.0) | Package management, build, test, publish. No new tooling |

**No dependencies on agent definitions** -- DAB generation is deterministic, doesn't invoke agents. Agents (v0.1.0) optionally produce YAML specs, but `dab generate` works with any valid spec (manual or agent-produced). Clear separation: agents = probabilistic (CLP debate), generators = deterministic (spec → SQL).

## Sources

**Anchor Modeling (HIGH confidence):**
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) -- Methodology overview, 6NF patterns, temporalization
- [Anchor Modeler GitHub](https://github.com/Roenbaeck/anchor) -- Official tool, directives for SQL generation, multi-dialect support
- [Anchor Modeling Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) -- Core concepts (anchors, attributes, ties, knots)
- [Anchor Modeling Paper (PDF)](https://www.anchormodeling.com/wp-content/uploads/2011/05/Anchor-Modeling.pdf) -- Formal methodology definition
- [From Anchor Model to XML (PDF)](https://www.anchormodeling.com/wp-content/uploads/2010/09/AM-XML.pdf) -- XML Schema (anchor.xsd) definition, formal structure
- [Codecentric: Database Design Using Anchor Modeling](https://www.codecentric.de/en/knowledge-hub/blog/agile-database-design-using-anchor-modeling) -- Practical usage patterns
- [Anchor Modeling DBMS Tools](https://dbmstools.com/tools/anchor-modeling) -- Tool features comparison
- [GitHub: jangorecki/anchormodeling](https://github.com/jangorecki/anchormodeling) -- R implementation, metadata management, identity patterns

**Sisula Templating (MEDIUM confidence):**
- [Sisula GitHub](https://github.com/Roenbaeck/sisula) -- Simple substitution language for XML → text (SQL) transformation
- [Introducing sisula](https://www.anchormodeling.com/introducing-sisula/) -- Replacement for XSLT in Anchor Modeler
- [Metadata Driven Anchor DW Automation](https://www.anchormodeling.com/metadata-driven-anchor-dw-automation/) -- ETL framework patterns

**YAML Validation (HIGH confidence):**
- [Yamale: Schema and Validator for YAML](https://github.com/23andMe/Yamale) -- Python YAML validation library
- [JSON Schema for YAML Validation](https://json-schema-everywhere.github.io/yaml) -- Standard approach for YAML validation
- [Validate YAML in Python with Schema](https://www.andrewvillazon.com/validate-yaml-python-schema/) -- Practical validation patterns

**SQL Code Generation (MEDIUM confidence):**
- [SQL-GEN: Bridging the Dialect Gap](https://arxiv.org/html/2408.12733v2) -- Multi-dialect SQL generation patterns, synthetic data approach
- [sqlglot.dialects API](https://sqlglot.com/sqlglot/dialects.html) -- SQL dialect abstraction and transpilation
- [LangChain Text-to-SQL](https://promethium.ai/guides/llm-ai-models-text-to-sql/) -- SQL generation frameworks (SQLDatabase, SQLAlchemy)

**Idempotent SQL (HIGH confidence):**
- [sqldef: Idempotent Schema Management](https://github.com/sqldef/sqldef) -- Tool for MySQL, PostgreSQL, SQLite, SQL Server
- [Creating Idempotent DDL Scripts (Redgate)](https://www.red-gate.com/hub/product-learning/flyway/creating-idempotent-ddl-scripts-for-database-migrations) -- Best practices
- [Idempotent SQL DDL (Medium)](https://medium.com/full-stack-architecture/idempotent-sql-ddl-ca354a1eee62) -- IF NOT EXISTS patterns
- [Idempotent Database Journaling](https://diegocantor.com/idempotent-database-journaling/) -- Repeatable script sequences

**Bruin Data Pipelines (MEDIUM confidence):**
- [Bruin Asset Definition](https://bruin-data.github.io/bruin/assets/definition-schema.html) -- Asset YAML frontmatter schema
- [Bruin Quickstart](https://bruin-data.github.io/bruin/getting-started/introduction/quickstart.html) -- Pipeline structure, materialization strategies

**Data Warehouse Identity Management (MEDIUM confidence):**
- [Database Keys in Data Warehouse (Medium)](https://ikbal-arslan.medium.com/database-keys-and-keys-for-data-warehouse-96855a5fbaa7) -- Natural vs surrogate keys
- [Keys in Data Warehouse Modeling (Medium)](https://medium.com/@felipe.ramires.terrazas/keys-in-data-warehousing-modeling-a-comprehensive-guide-1901e2162d89) -- Comprehensive key patterns
- [Surrogate Keys in Data Warehousing (APXML)](https://apxml.com/courses/data-modeling-schema-design-analytics/chapter-3-advanced-dimension-handling/surrogate-keys-vs-natural-keys) -- When to use each type

**Staging Tables (HIGH confidence):**
- [Data Staging Guide (Zuar)](https://www.zuar.com/blog/complete-guide-to-data-staging/) -- Staging best practices, multi-source patterns
- [dbt Staging Best Practices](https://docs.getdbt.com/best-practices/how-we-structure/2-staging) -- 1-to-1 source → staging, naming conventions
- [Staging Layer (Roelant Vos)](https://roelantvos.com/blog/enterprise_bi_architecture_overview/the-staging-layer/) -- Architecture patterns

**Northwind OData (LOW confidence -- exists, structure unclear):**
- [Northwind OData V4 Service](https://services.odata.org/V4/Northwind/Northwind.svc/) -- Reference service
- [Northwind OData GitHub](https://github.com/JCallico/Northwind-OData) -- Implementation

**Database Schema Tools (MEDIUM confidence):**
- [Best Database Design Tools 2025 (DbSchema)](https://dbschema.com/blog/design/best-database-design-tools-2025/) -- Tool landscape
- [Top Database CI/CD Tools 2026](https://www.dbvis.com/thetable/top-database-cicd-and-schema-change-tools-in-2025/) -- Liquibase, Flyway, sqldef comparison

---
*Feature research for: DAB Specification Management and Anchor Modeling Code Generation*
*Researched: 2026-02-09*
*Confidence: MEDIUM -- Anchor Modeling patterns well-established from official tools; YAML validation and SQL generation patterns mature; keyset identity and multi-source staging are novel extensions requiring validation*
