# Project Research Summary

**Project:** data-architect
**Domain:** Python CLI tool + OpenCode.ai agent scaffolding + DAB (Data According to Business) code generation for Anchor Modeling
**Researched:** 2026-02-07 (v0.1.0-v0.2.0), 2026-02-09 (v0.3.0)
**Confidence:** HIGH

## Executive Summary

Data Architect is a Python CLI tool (`architect`) that combines two core capabilities: (1) scaffolding OpenCode.ai agent teams for collaborative data warehouse design via structured CLP (Conceptual-Logical-Physical) debate, and (2) deterministic SQL code generation from YAML specifications following Anchor Modeling methodology. The v0.1.0-v0.2.0 milestones delivered `architect init` (agent scaffolding with six specialized agents: Data Architect, System Analyst, Business Analyst, Data Engineer, Analytics Engineer, Veteran Reviewer) built on pure-functional Python with the Astral ecosystem. The v0.3.0 milestone extends this with `architect dab *` subcommands to manage Anchor Modeling specifications and generate idempotent, multi-dialect SQL.

The recommended approach for v0.3.0 maintains the established pure-functional style while adding runtime validation (Pydantic), XML interoperability (lxml), and SQL templating (Jinja2). The YAML spec format is a superset of the official Anchor XML schema (anchor.xsd), enabling roundtrip import/export with the visual Anchor Modeler tool while adding novel extensions: keyset identity (`entity@system~tenant|natural_key`) for provenance tracking and multi-source staging mappings for complex ETL scenarios. Architecture extends the existing frozen dataclass + pure function patterns with strategy-pattern dialect abstraction (PostgreSQL, SQL Server, Snowflake, Oracle) and Jinja2 templates organized per dialect with shared idempotency macros.

The three highest-risk areas for v0.3.0 are: (1) lossy XML-YAML-XML conversions when YAML extensions (staging mappings, keyset identity) cannot be represented in official XML format; (2) keyset identity delimiter collision when natural keys contain `@`, `~`, `|` characters leading to parse failures or SQL injection; and (3) dialect-specific SQL idempotency patterns where `CREATE TABLE IF NOT EXISTS` works in PostgreSQL but fails in older SQL Server/Oracle versions or produces different UPSERT semantics. These are mitigated through strict three-layer schema validation (XML-compatible core + YAML extensions + export warnings), canonical escape sequences with property-based testing, and per-dialect abstraction layers with comprehensive integration testing across target databases.

## Key Findings

### Recommended Stack

**From STACK.md (v0.1.0-v0.2.0 + v0.3.0):** The stack centers on the Astral ecosystem (UV 0.10+, Ruff 0.15+, Python 3.13+) with domain-specific additions for v0.3.0. All choices are HIGH confidence, verified from official documentation. Core mandate — pure functional Python, TDD with 92.77%+ coverage, frozen dataclasses — remains unchanged.

**Core technologies:**
- **Python >=3.13 + UV >=0.10.0:** Runtime and package management. UV replaces pip/poetry/pyenv with 10-100x faster operations and cross-platform lockfile.
- **Typer >=0.21.0:** CLI framework. Function-based API aligns with functional Python mandate. Subcommand groups via `add_typer()` for `architect dab *` commands.
- **Pydantic >=2.12.5 (NEW in v0.3.0):** Runtime YAML validation with frozen models (`model_config = ConfigDict(frozen=True)`), cross-field validators for XSD assertions, Rust-accelerated performance. Required for DAB spec validation against anchor.xsd rules + extensions.
- **lxml >=6.0.1 (NEW in v0.3.0):** Full XSD 1.1 validation for Anchor XML import/export, fastest XML processing (C bindings to libxml2). Enables roundtrip to official Anchor Modeler GUI.
- **Jinja2 >=3.1.6 (NEW in v0.3.0):** SQL templating with dialect-specific templates, idempotency macros, deterministic output. De facto standard for SQL generation (dbt, Airflow, Bruin).
- **PyYAML >=6.0.2 (NEW in v0.3.0):** YAML spec parsing/serialization (YAML 1.1). Lightweight, sufficient for generation use case. Ruamel.yaml (YAML 1.2, comment-preserving) deferred as optional for export feature.
- **Hatchling + uv-dynamic-versioning:** Build backend with automatic version derivation from git tags. No hardcoded version strings.
- **Ruff >=0.15.0 + Mypy >=1.19.0:** Linting/formatting (single tool, Rust-speed) and strict static type checking. Enforces functional style through annotations.
- **pytest >=9.0.0 + Hypothesis >=6.151.0:** TDD-first testing with property-based testing for spec parsing invariants, keyset identity round-trips, deterministic generation.

**Why NOT alternatives:**
- NOT SQLAlchemy for SQL generation — abstracts away dialect SQL we need full control over; overkill for static DDL
- NOT Pydantic for all data structures — use frozen dataclasses for internal models (ScaffoldResult patterns), Pydantic only for validation-heavy DAB specs
- NOT xmltodict — discards schema info, no validation; lxml with XSD required for anchor.xsd compliance
- NOT JSON Schema for validation — DAB spec is superset of Anchor XML (XSD); translating XSD→JSON Schema loses semantics

### Expected Features

**From FEATURES.md (v0.1.0-v0.2.0 + v0.3.0):** Milestone v0.1.0-v0.2.0 delivered `architect init` (agent scaffolding). Milestone v0.3.0 adds `architect dab *` (spec management + SQL generation). MVP focuses on deterministic single-source YAML → SQL generation with PostgreSQL dialect.

**Must have (table stakes for v0.3.0):**
- Spec scaffold (`dab init`) — blank YAML template with inline comments explaining anchor.xsd structure
- YAML spec validation — parse, validate referential integrity (attributes reference valid anchors), report line numbers on errors
- SQL generation (`dab generate`) — idempotent CREATE TABLE per entity (anchors, attributes, ties, knots) following Anchor Modeling conventions (surrogate keys, metadata columns, 6NF structure)
- Per-entity output — one `.sql` file per anchor + attributes/ties, organized in `output/` directory
- Idempotent SQL output — `IF NOT EXISTS` for CREATE TABLE, additive-only schema evolution, safe to re-run on existing database
- Keyset identity generation — SQL to construct `entity@system~tenant|natural_key` from source natural key columns (VARCHAR column in anchor table)
- Staging mappings (single source) — column-level lineage: `staging_table.column → anchor.attribute` mappings in spec
- Northwind example spec — pre-filled YAML for Northwind OData as reference implementation and test case
- Deterministic output — no timestamps, UUIDs, or randomness. Same spec → same SQL every time (git-friendly)
- Metadata columns — auto-generate `metadata_recorded_at`, `metadata_recorded_by`, `metadata_id` in every table
- Validation error line numbers — parser reports line number for every error (fast debugging)

**Should have (competitive advantage for v0.3.0):**
- Keyset identity scheme — provenance tracking without lookup tables, enables multi-tenant/multi-source scenarios. UNIQUE vs official Anchor (surrogate-only).
- Column-level staging mappings — explicit source → target lineage in spec, clear data provenance. Official Anchor separates ETL from modeling.
- YAML superset of Anchor XML — ergonomic editing (YAML) + interoperability (XML import/export to official Anchor Modeler GUI). Best of both worlds.
- Bruin asset format output — SQL with Bruin YAML frontmatter (materialization strategies, column checks). Alternative to raw SQL. Materialization: merge for SCD2, view for current state.

**Defer (v0.3.x+ based on user demand):**
- Import/Export (XML ↔ YAML) — roundtrip to Anchor Modeler GUI for visual editing. Trigger: user migration request from Anchor Modeler projects.
- Multi-source staging mappings — multiple `staging_tables[]` per anchor with union semantics. Trigger: validated multi-source use case (e.g., Customer from CRM + ERP).
- SQL Server/Snowflake dialects — second/third dialects prove abstraction works. Trigger: user requests.
- Dependency ordering — knots → anchors → attributes → ties (topological sort). Prevents FK constraint errors on fresh database. Trigger: complex schema creation fails.
- Dry-run mode — `--dry-run` flag to preview SQL without writing files. Trigger: users want to inspect before committing.
- Diff-friendly formatting — consistent SQL style, one column per line, trailing commas. Trigger: noisy git diffs.

**Anti-features (commonly requested, problematic):**
- GUI for spec editing — adds complexity, breaks CLI-first workflow. Official Anchor Modeler GUI exists; use `dab import/export` for roundtrip.
- Auto-detect anchors from source schema — CLP modeling requires business context and debate (probabilistic). This is what agents are for. Deterministic detection deferred to DAS layer (v0.4.0+).
- Template customization language — every customization is maintenance burden. Users fork templates and can't upgrade. Provide dialect parameter; open issues to improve defaults for everyone.

### Architecture Approach

**From ARCHITECTURE.md (v0.1.0-v0.2.0 + v0.3.0):** The architecture follows a layered pattern: thin CLI shell (Typer/Click) dispatches to pure function modules (scaffold, spec, generate), which operate on immutable data (frozen dataclasses) and push all side effects to the edges. V0.3.0 adds new `dab/` module with all DAB functionality isolated from v0.1.0-v0.2.0 agent scaffolding.

**Major components:**
1. **CLI Entry Point (`cli.py`)** — Parses commands, formats output, handles errors. Zero business logic. V0.3.0 adds `app.add_typer(dab_cli.app, name="dab")` (single line change).
2. **Scaffolder (`scaffold.py`)** — Pure functions: reads bundled agent templates via `importlib.resources`, writes to `.opencode/agents/`. One-way file copy, no state. Unchanged in v0.3.0.
3. **Spec System (`dab/spec.py`, `dab/io.py`, `dab/keyset.py`) [NEW in v0.3.0]** — Frozen dataclasses for Anchor constructs (Anchor, Attribute, Tie, Knot, Nexus, Role, Key, Keyset, StagingMapping) matching anchor.xsd. Parse YAML via PyYAML, validate with Pydantic models, pure validation functions return `(valid, errors)`. Keyset identity parsing with canonical escape sequences.
4. **Dialect Abstraction (`dab/dialects/`) [NEW in v0.3.0]** — Strategy pattern via Protocol + pure function modules. One module per dialect (postgresql.py, snowflake.py, sqlserver.py, oracle.py). Type mapping (`int` → `INTEGER`, `varchar(42)` → `VARCHAR(42)`), idempotency patterns (`CREATE TABLE IF NOT EXISTS`).
5. **SQL Generation (`dab/generate.py`, `dab/templates/`) [NEW in v0.3.0]** — Context preparation functions (pure transforms: Spec → dict) + Jinja2 templates (simple iteration). Templates organized by dialect with shared `_macros.sql.j2` for idempotency helpers (`create_table_if_not_exists`, `add_column_if_missing`, `create_or_replace_view`).
6. **Bundled Agent Templates (`_agents/`)** — Static Markdown files with YAML frontmatter. Copied verbatim during scaffold. The actual product (v0.1.0-v0.2.0).

**Integration with existing architecture:**
- CLI layer: Single line change to add dab subcommand group (`app.add_typer(dab_cli.app, name="dab")`)
- Scaffold pattern: Reused for `dab init` (pure function + side effects at edge)
- Template system: Extended with Jinja2 for SQL (existing uses embedded strings for agents)
- Data layer: Frozen dataclasses consistent with existing `ScaffoldResult` pattern
- pyproject.toml: Add `pydantic>=2.12.5`, `lxml>=6.0.1`, `jinja2>=3.1.6`, `pyyaml>=6.0.2`

**Data flow for DAB generation:**
```
architect dab generate specs/dab.yaml --dialect postgresql --output generated/
    ↓
read_yaml(spec_path) → yaml.safe_load() → _parse_spec_dict() → Spec (frozen)
    ↓
validate_spec(spec) → (valid, errors)
    ↓ (if valid)
generate_sql(spec, output_dir, dialect, format)
    ↓
For each anchor/knot/tie/nexus:
    _prepare_*_context(element, dialect) → dict (pure transform)
    ↓
    _render_template(env, template_name, context) → SQL string (deterministic)
    ↓
    (optional) _wrap_bruin_asset(env, sql, name) → Bruin YAML + SQL
    ↓
    _write_file(output_dir, filename, content) → Path (side effect)
```

### Critical Pitfalls

**From PITFALLS.md (v0.1.0-v0.2.0 + v0.3.0):** Top 10 pitfalls identified with prevention strategies and phase assignments.

**V0.1.0-V0.2.0 Pitfalls (still relevant):**
1. **Shallow immutability in frozen dataclasses** — `frozen=True` only prevents field reassignment; nested `list`/`dict` fields remain mutable. Prevention: enforce `tuple[T, ...]` and `frozenset[T]` for all collection fields from day one. Use `__post_init__` validation.
2. **OpenCode platform instability** — OpenCode releases every 1-3 days with breaking changes possible. Prevention: use only stable frontmatter fields, embed version markers in scaffolded files, design for update-ability from the start.
3. **Prompt engineering depth gates all value** — Generic prompts produce generic output. Agents must encode specific Anchor Modeling rules, CLP checkpoint criteria, debate positions. Prevention: deep domain research before writing agent definitions.
4. **Multi-agent debate loops** — Without bounded iterations and convergence detection, agents loop indefinitely. Prevention: encode max round limits (3 rounds), convergence detection, Veteran Reviewer tie-breaking authority in prompts.
5. **Dynamic versioning fails in CI** — Shallow clones lose git tag history, causing silent `0.0.0` version fallback. Prevention: `fetch-depth: 0` + `fetch-tags: true` in CI; version validation step before any publish.

**V0.3.0 NEW Pitfalls:**
6. **Lossy XML-YAML Bidirectional Transformation** — YAML superset features (staging mappings, keyset identity) cannot round-trip to XML. Prevention: Three-layer schema (XML-compatible core, YAML extensions, export warnings). Tag YAML-only features with `# @export-incompatible` comments. Fail loudly on export unless `--force-lossy`. Round-trip validation tests: XML → YAML → XML equality. **Address:** Phase 1 (establish schema layers upfront).
7. **Keyset Identity Delimiter Collision** — Natural keys containing `@`, `~`, `|` break parser (`ACME~2024|SPECIAL@OFFER`). SQL injection risk. Prevention: Canonical escape sequence (`@@` for `@`, `~~` for `~`, `||` for `|`). Single `KeysetIdentity` dataclass with `.parse()` and `.format()` methods. Property-based tests with random delimiter-heavy strings. **Address:** Phase 1 (define format during schema validation).
8. **Idempotent SQL Dialect Divergence** — `CREATE TABLE IF NOT EXISTS` works in PostgreSQL but fails in SQL Server <2016, Oracle has different syntax. UPSERT semantics vary (ON CONFLICT vs MERGE vs INSERT IGNORE). Prevention: Dialect abstraction layer with explicit operations (`dialect.create_table_idempotent()`, `dialect.upsert_rows()`). Per-dialect test suites verifying idempotency (run script twice, compare results). **Address:** Phase 2 (implement before generating SQL).
9. **Multi-Source Merge Conflict Mishandling** — Same anchor from multiple sources (Customer from CRM + ERP) silently drops conflicts, non-deterministic last-write-wins. Prevention: Require explicit conflict resolution in YAML (priority, `wins_for` attributes). Generate conflict detection logging. Deterministic ordering. **Address:** Phase 3 (design conflict schema before merge logic).
10. **Pure-Functional Python State Leakage in Generator** — Generator functions mutate global state (mnemonic registry), breaking TDD and causing non-deterministic test failures. Prevention: All generators return new immutable objects. Thread context through parameters, not globals. Separate pure logic (generate AST) from I/O effects (write files). Property-based tests verify same input → same output. **Address:** Phase 2 (establish pure architecture before complex generators).

**Additional V0.3.0 Pitfalls:**
- **Anchor Modeling Mnemonic Naming Collisions** — Auto-generated mnemonics create collisions (`Customer` → `CU`, `Currency` → `CU`). Prevention: Collision detection, deterministic generation (sort by name), explicit overrides in YAML. **Address:** Phase 1.
- **Bruin Asset YAML Frontmatter Malformation** — Invalid YAML frontmatter (missing required fields, incorrect dependency format). Prevention: Pydantic schema validation, test with Bruin CLI (`bruin validate`). **Address:** Phase 2.
- **Temporal Data INSERT Idempotency Failure** — Temporal attributes require ON CONFLICT with valid-time keys. Bitemporal: never UPDATE, only INSERT with new transaction-time. Prevention: Temporal-aware idempotency patterns. **Address:** Phase 2.
- **Integration Test Data Unrealism** — Sanitized "happy path" data (no special characters, no conflicts, no long names). Prevention: Property-based testing with Hypothesis, adversarial test dataset. **Address:** Phase 1.

## Implications for Roadmap

Based on combined research, the following phase structure addresses v0.3.0 DAB generation milestone. This builds on the v0.1.0-v0.2.0 foundation (agent scaffolding complete).

### Phase 1: YAML Schema Foundation & Spec Scaffolding
**Rationale:** All downstream features depend on correct spec parsing and validation. Property-based testing with Hypothesis catches edge cases early (delimiter collision, mnemonic conflicts). Establish three-layer schema (XML-compatible core, YAML extensions, export warnings) to prevent lossy conversions. Keyset identity format must be defined before SQL generation uses it.

**Delivers:**
- `dab/spec.py` with frozen dataclasses (Anchor, Attribute, Tie, Knot, Nexus, Role, Key, Keyset, StagingMapping)
- `dab/io.py` with YAML read/write (PyYAML), XML deferred to Phase 5
- `dab/keyset.py` with keyset parsing (canonical escape sequences: `@@`, `~~`, `||`)
- `validate_spec()` function with anchor.xsd rules + extension validation (mnemonic uniqueness, referential integrity, line number errors)
- `dab/cli.py` with `dab init` command (spec scaffold with example anchors/knots/ties)
- Integration with main CLI (`app.add_typer(dab_cli.app, name="dab")`)
- Property-based tests with Hypothesis (keyset round-trips, mnemonic determinism)
- Adversarial test dataset (special characters, unicode, long names)

**Addresses features:**
- Spec scaffold (YAML template generation)
- YAML validation (parse, referential integrity, line number errors)
- Keyset identity parsing (delimiter collision prevention)

**Avoids pitfalls:**
- Lossy XML-YAML transformation (three-layer schema established)
- Keyset identity delimiter collision (escape sequences defined)
- Anchor Modeling mnemonic collisions (deterministic generation, collision detection)
- YAML schema validation escape hatches (strict enforcement, no bypass flags)
- Integration test data unrealism (property-based tests with Hypothesis)

**Research flags:** Standard patterns (frozen dataclasses, YAML parsing). Skip research-phase.

---

### Phase 2: Dialect Abstraction & SQL Generation (PostgreSQL)
**Rationale:** Simplest dialect (PostgreSQL, open-source, common) proves the architecture before adding complexity. Context preparation (pure Python) + Jinja2 templates pattern ensures testability. Idempotent SQL patterns must work before multi-dialect support. Pure-functional architecture established before complex generators.

**Delivers:**
- `dab/dialects/base.py` with Dialect protocol
- `dab/dialects/__init__.py` with dialect registry (`get_dialect(name)`)
- `dab/dialects/postgresql.py` with type mappings (`int→INTEGER`, `varchar(42)→VARCHAR(42)`) + idempotency patterns (`CREATE TABLE IF NOT EXISTS`)
- `dab/generate.py` with context preparation + Jinja2 rendering (pure functions, no global state)
- `dab/templates/anchor.sql.j2`, `knot.sql.j2`, `tie.sql.j2`, `nexus.sql.j2`, `_macros.sql.j2`
- `architect dab generate` command (PostgreSQL dialect)
- Snapshot tests with Syrupy (deterministic output validation: same spec → same SQL)
- Temporal-aware idempotency patterns (ON CONFLICT with valid-time keys)

**Addresses features:**
- SQL generation (idempotent CREATE TABLE per entity)
- Per-entity output (one `.sql` file per anchor)
- Deterministic output (same YAML → same SQL)
- Metadata columns (auto-generated)

**Uses stack:**
- Jinja2 for SQL templating
- Pydantic for spec validation before generation
- Frozen dataclasses for immutable context dicts

**Avoids pitfalls:**
- Idempotent SQL dialect divergence (abstraction layer established)
- Bruin asset YAML frontmatter malformation (schema validation, but Bruin deferred to Phase 5)
- Pure-functional Python state leakage (context preparation pure, side effects at edge)
- Temporal data INSERT idempotency failure (temporal-aware patterns)

**Research flags:** Standard patterns (Jinja2, strategy pattern). Skip research-phase.

---

### Phase 3: Additional Dialects (SQL Server, Snowflake)
**Rationale:** Prove multi-dialect abstraction works. SQL Server common in enterprise, Snowflake in modern cloud stacks. Straightforward extensions following PostgreSQL pattern. Can be built in parallel (independent of each other).

**Delivers:**
- `dab/dialects/sqlserver.py` with SQL Server type mappings + idempotency patterns (version-specific: `IF NOT EXISTS` for SQL Server 2016+, transactional checks for older versions)
- `dab/dialects/snowflake.py` with Snowflake type mappings (`int→NUMBER`) + idempotency patterns (`CREATE OR REPLACE`)
- Dialect-specific templates (or shared templates with dialect-specific macros)
- Per-dialect test suites + snapshot tests
- Documentation: dialect support matrix, version requirements

**Addresses features:**
- Multi-dialect SQL support (table stakes for enterprise adoption)

**Avoids pitfalls:**
- Idempotent SQL dialect divergence (verify abstraction works across dialects with different idempotency semantics)

**Research flags:** Standard patterns (follow PostgreSQL). Skip research-phase.

---

### Phase 4: Keyset Identity Generation & Staging Mappings
**Rationale:** Extends SQL generation with provenance tracking and source lineage. Requires Phase 1 (keyset format defined) and Phase 2 (SQL generation working). Single-source staging validates patterns before multi-source complexity.

**Delivers:**
- SQL generation for keyset identity construction (`entity@system~tenant|natural_key` VARCHAR column in anchor table)
- Column-level staging mappings in spec (YAML schema extension: `staging_tables[].columns[]` with `maps_to: anchor.attribute`)
- SQL to map staging columns to anchor attributes (INSERT ... SELECT with column mappings)
- Northwind example spec (validates all features: keyset identity, staging mappings, anchors/knots/ties)
- Documentation: staging mapping patterns, keyset identity usage, provenance tracking examples

**Addresses features:**
- Keyset identity generation (differentiator, provenance tracking)
- Staging mappings single source (column-level lineage)
- Northwind example (reference implementation)

**Avoids pitfalls:**
- Keyset identity delimiter collision (uses escape sequences from Phase 1)

**Research flags:** Standard patterns (SQL string construction). Skip research-phase.

---

### Phase 5: XML Import/Export & Bruin Assets (Optional)
**Rationale:** Optional features for interoperability. XML I/O enables roundtrip to official Anchor Modeler GUI (visual modeling). Bruin assets enable data pipeline integration. Deferred until user demand validated.

**Delivers:**
- `dab/io.py` XML import (anchor.xsd → Spec via lxml with XSD validation)
- `dab/io.py` XML export (Spec → anchor.xsd, drop YAML extensions with explicit warnings: `WARNING: Exporting to XML will lose keyset identity and staging mappings`)
- `architect dab import` and `architect dab export` commands
- `dab/templates/bruin.asset.j2` template (YAML frontmatter with `name`, `type`, `materialization`, `columns`, `checks` + SQL body)
- `architect dab generate --format bruin` flag
- Bruin asset schema validation with Pydantic (required fields, correct dependency format)
- Round-trip validation tests (XML → YAML → XML equality for XML-compatible core)

**Addresses features:**
- Import from XML (migration from Anchor Modeler)
- Export to XML (roundtrip to visual modeling)
- Bruin asset format (pipeline integration)

**Uses stack:**
- lxml for XSD validation
- Pydantic for spec validation before export

**Avoids pitfalls:**
- Lossy XML-YAML transformation (export warnings implemented in Phase 1 schema)
- Bruin asset YAML frontmatter malformation (schema validation with Bruin CLI: `bruin validate` in tests)

**Research flags:** Standard patterns (lxml XML parsing, Jinja2 templating). Skip research-phase.

---

### Phase 6: Multi-Source Staging & Advanced Features (v0.3.x+)
**Rationale:** Complex features requiring validated use cases. Multi-source staging adds union semantics and conflict resolution. Dependency ordering prevents FK errors in complex schemas. Defer until single-source patterns proven.

**Delivers:**
- Multi-source staging mappings in spec (multiple `staging_tables[]` per anchor with same `anchor_mnemonic`)
- Conflict resolution schema (priority per source, `wins_for` attributes, default strategy: reject vs priority-based)
- SQL generation with conflict detection + audit logging (write conflicts to audit table: `conflict_log`)
- Deterministic ordering: sort sources by declared priority, then by system name
- Dependency ordering (topological sort: knots → anchors → attributes → ties, prevents FK constraint errors)
- Dry-run mode (`--dry-run` flag shows SQL without writing files)
- Incremental generation (only regenerate changed entities, based on YAML hash)

**Addresses features:**
- Multi-source staging mappings (differentiator, complex ETL)
- Dependency ordering (prevents FK errors)
- Dry-run mode (UX improvement)

**Avoids pitfalls:**
- Multi-source merge conflict mishandling (explicit conflict resolution schema from Phase 1)

**Research flags:** Complex domain (conflict resolution). MAY need research-phase if patterns unclear during planning. Conflict resolution strategies exist (CRDT, last-write-wins, priority-based) but application to Anchor Modeling is novel.

---

### Phase Ordering Rationale

**Why this order:**
1. **Schema validation first (Phase 1)** — Prevents downstream errors. Invalid YAML caught before SQL generation wastes time. Property-based testing finds edge cases (delimiter collision, mnemonic conflicts) early. Three-layer schema established before export (Phase 5) implemented.
2. **Single dialect first (Phase 2)** — PostgreSQL proves generation patterns before multi-dialect complexity. Easier debugging, faster iteration. Idempotent SQL patterns validated before scaling.
3. **Abstractions before scaling (Phase 3)** — Dialect abstraction established with one dialect, then scales to 2+ dialects trivially. Proves strategy pattern works.
4. **Keyset & staging after generation (Phase 4)** — Extends proven SQL generation with provenance tracking. Requires Phase 1 (keyset format) and Phase 2 (SQL generation) as foundation.
5. **Optional features last (Phase 5)** — XML I/O and Bruin assets valuable but not essential for core value (YAML → SQL). Defer until validated demand.
6. **Single-source before multi-source (Phase 6)** — Staging mappings simpler without conflict resolution. Prove lineage patterns work before adding union semantics.

**How this avoids pitfalls:**
- Lossy transformations: Three-layer schema defined in Phase 1 before export implemented in Phase 5
- Delimiter collisions: Escape sequences established in Phase 1 before keyset generation in Phase 4
- Dialect divergence: Abstraction layer in Phase 2 before additional dialects in Phase 3
- State leakage: Pure-functional architecture enforced in Phase 2 before complex multi-source logic in Phase 6
- Unrealistic test data: Property-based testing in Phase 1 establishes adversarial testing pattern for all phases

**Dependencies from v0.1.0-v0.2.0:**
- CLI infrastructure (Typer, Click) — reused for `dab` subcommands
- Test framework (pytest, Hypothesis) — validation requires extensive test coverage
- Pure functional style (frozen dataclasses, pure functions) — immutable specs → deterministic SQL
- Symbol output pattern — user-friendly errors with line numbers
- Makefile targets (`make check`) — code generation quality gates
- Pre-commit hooks (`.pre-commit-config.yaml`) — prevent committing broken generators
- Dynamic versioning (git tags) — consistent versioning across CLI + generated SQL comments
- UV build system — package management, build, test, publish

### Research Flags

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (YAML Schema):** Frozen dataclasses, YAML parsing, validation patterns well-documented. Property-based testing with Hypothesis established pattern.
- **Phase 2 (SQL Generation):** Jinja2 templating, strategy pattern, context preparation standard approaches. Idempotent SQL patterns researched (sqldef, dbt).
- **Phase 3 (Additional Dialects):** Follows PostgreSQL pattern established in Phase 2. Dialect-specific SQL documented in official docs.
- **Phase 4 (Keyset & Staging):** SQL string construction, column mapping straightforward. Keyset format defined in Phase 1.
- **Phase 5 (XML & Bruin):** lxml XML parsing standard pattern. Bruin asset format documented in official Bruin docs.

**Phases potentially needing research-phase:**
- **Phase 6 (Multi-Source):** Conflict resolution patterns domain-specific. If patterns unclear during planning, trigger `/gsd:research-phase` to research data integration conflict strategies (research exists but application to Anchor Modeling novel: CRDT, priority-based resolution, multi-master replication).

**V0.1.0-V0.2.0 Research Flags (still relevant):**
- **Agent Definitions (complete):** Deep domain research complete. Anchor Modeling rules, CLP workflow checkpoint criteria, debate protocol patterns encoded in agent prompts.
- **DAR Generation (future, v0.4.0+):** Unified Star Schema patterns have sparser documentation than Anchor Modeling. Bridge table derivation logic needs domain expertise research.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified from official documentation (v0.1.0-v0.2.0 + v0.3.0). Versions confirmed compatible with Python 3.13+. Pydantic 2.12.5, lxml 6.0.1, Jinja2 3.1.6, PyYAML 6.0.2 verified from PyPI. Astral ecosystem proven in v0.1.0-v0.2.0 (92.77% coverage baseline). |
| Features | HIGH (v0.1.0-v0.2.0), MEDIUM (v0.3.0) | CLI scaffolding UX patterns well-established. OpenCode agent format verified from official docs. Anchor Modeling patterns well-established from official tools (anchor.xsd, Sisula templates). Keyset identity and multi-source staging are novel extensions requiring validation. Table stakes features (YAML→SQL, idempotency) proven in other tools (sqldef, dbt). |
| Architecture | HIGH | Pure functional Python patterns documented in official Python HOWTO. Frozen dataclasses + pure functions consistent with v0.1.0-v0.2.0 (92.77% coverage baseline). Typer subcommand groups, Jinja2 templating, dialect abstraction all standard patterns. Integration points minimal (1 line CLI change, pyproject.toml deps). |
| Pitfalls | HIGH (v0.1.0-v0.2.0), MEDIUM (v0.3.0) | Python FP pitfalls verified against official docs. OpenCode instability confirmed from live changelog. V0.3.0 pitfalls: Critical pitfalls identified from multi-source research (YAML hell, delimiter collision, idempotency patterns, temporal data). Anchor Modeling specific pitfalls (mnemonic collisions, bitemporal historization) have fewer authoritative sources but patterns extrapolated from Data Vault and temporal modeling research. |

**Overall confidence:** HIGH (v0.1.0-v0.2.0 foundation + v0.3.0 core stack/architecture) with MEDIUM caveats (v0.3.0 novel extensions need validation)

### Gaps to Address

**V0.1.0-V0.2.0 Gaps (addressed):**
- Anchor Modeling rule encoding — complete (agents encode CLP debate protocol, Anchor Modeling rules)
- CLP debate protocol design — complete (max rounds, convergence detection, Veteran Reviewer tie-breaking)
- OpenCode format stability — monitored (specific frontmatter fields verified, version markers embedded)
- Ruff enforcement of functional style — documented (code review conventions, no custom Ruff plugin yet)

**V0.3.0 NEW Gaps:**

**YAML 1.1 vs 1.2 ambiguity:**
- Research found YAML version affects parsing (1.1 treats `1e2` as string, 1.2 as number)
- **Mitigation:** Enforce YAML 1.2 with explicit `%YAML 1.2` headers in all generated files. Validate parser behavior in tests with version-specific edge cases.

**Multi-source conflict resolution patterns:**
- Identified as critical but patterns are domain-specific (data integration, not Anchor Modeling)
- **Mitigation:** Defer to Phase 6. If patterns unclear during phase planning, trigger `/gsd:research-phase` for data integration conflict strategies research (CRDT, priority-based, multi-master replication).

**Temporal/bitemporal SQL idempotency:**
- Anchor Modeling supports temporal attributes (valid-time), but idempotent INSERT patterns for temporal data complex (ON CONFLICT with valid-time keys vs never UPDATE for bitemporal)
- **Mitigation:** Phase 2 implements temporal-aware idempotency patterns. Validate with bi-temporal edge cases in tests.

**Bruin asset format schema:**
- Bruin documentation provides examples but not formal schema
- **Mitigation:** Reverse-engineer schema from examples, validate generated assets with `bruin validate` CLI in tests (Phase 5).

**Oracle dialect identifier length limit:**
- Oracle <12c has 30-character identifier limit, truncation strategy affects mnemonic generation
- **Mitigation:** Defer Oracle dialect to v0.4.0+. If added, implement intelligent truncation with collision detection (append `_1`, `_2` if truncated names collide).

## Sources

### Primary (HIGH confidence)

**Official Documentation (v0.1.0-v0.2.0):**
- [OpenCode.ai Agents Docs](https://opencode.ai/docs/agents/) — Agent definition format, frontmatter fields, modes
- [OpenCode.ai Config Docs](https://opencode.ai/docs/config/) — opencode.json schema, configuration merging
- [OpenCode.ai Skills Docs](https://opencode.ai/docs/skills/) — Skill format, SKILL.md structure
- [OpenCode.ai Rules Docs](https://opencode.ai/docs/rules/) — AGENTS.md rules format
- [UV Working on Projects](https://docs.astral.sh/uv/guides/projects/) — pyproject.toml, uv sync, uv build
- [UV GitHub Actions Guide](https://docs.astral.sh/uv/guides/integration/github/) — CI/CD workflows
- [Typer Documentation](https://typer.tiangolo.com/) — CLI framework, subcommand groups
- [Python Packaging User Guide: src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — Package structure
- [importlib.resources](https://docs.python.org/3/library/importlib.resources.html) — Package data access
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) — Property-based testing
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html) — Frozen dataclass behavior
- [Python Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html) — Functional patterns

**Official Documentation (v0.3.0):**
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) — Model validation, frozen config (v2.12.5)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) — Template syntax, macros (v3.1.6)
- [lxml Documentation](https://lxml.de/) — XSD validation, parsing (v6.0.1)
- [lxml Validation Guide](https://lxml.de/validation.html) — XMLSchema class, XSD validation
- [Bruin Asset Definition Schema](https://bruin-data.github.io/bruin/assets/definition-schema.html) — YAML frontmatter format

**Package Registries (versions verified):**
- [Pydantic on PyPI](https://pypi.org/project/pydantic/) — v2.12.5, Dec 2025
- [lxml on PyPI](https://pypi.org/project/lxml/) — v6.0.1, Aug 2025
- [Jinja2 on PyPI](https://pypi.org/project/Jinja2/) — v3.1.6, Mar 2025
- [PyYAML on PyPI](https://pypi.org/project/PyYAML/) — v6.0.2, 2024
- [uv-dynamic-versioning on PyPI](https://pypi.org/project/uv-dynamic-versioning/) — v0.13.0, Jan 2026
- [Typer on PyPI](https://pypi.org/project/typer/) — v0.21.1, Jan 2026
- [Hypothesis on PyPI](https://pypi.org/project/hypothesis/) — v6.151.5, Feb 2026

**Primary Sources (Anchor Modeling):**
- Anchor XSD (`.references/anchor/anchor.xsd`) — Official XML schema, assertions, recent updates (2025-09-25)
- Anchor SQL templates (`.references/anchor/SQL/`) — Sisula template patterns, directive structure
- Anchor Example XML (`.references/anchor/example.xml`) — Reference implementation

### Secondary (MEDIUM confidence)

**Anchor Modeling:**
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) — Methodology overview, 6NF patterns
- [Anchor Modeler GitHub](https://github.com/Roenbaeck/anchor) — Official tool, directives, multi-dialect support
- [From Anchor Model to XML (PDF)](https://www.anchormodeling.com/wp-content/uploads/2010/09/AM-XML.pdf) — XML Schema definition
- [Introducing sisula](https://www.anchormodeling.com/introducing-sisula/) — Replacement for XSLT

**YAML & Validation:**
- [The YAML Document from Hell](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) — YAML 1.1 vs 1.2 edge cases
- [JSON is not a YAML subset](https://john-millikin.com/json-is-not-a-yaml-subset) — YAML specification ambiguities
- [Yamale: Schema and Validator for YAML](https://github.com/23andMe/Yamale) — Python YAML validation library

**SQL Generation & Idempotency:**
- [sqldef: Idempotent Schema Management](https://github.com/sqldef/sqldef) — Tool for multiple dialects
- [Idempotent SQL DDL (Medium)](https://medium.com/full-stack-architecture/idempotent-sql-ddl-ca354a1eee62) — Best practices
- [Advanced SQL Templates with JinjaSql](https://medium.com/data-science/advanced-sql-templates-in-python-with-jinjasql-b996eadd761d) — SQL generation patterns
- [Advanced SQL Templates in Python with Jinja](https://medium.com/data-science/advanced-sql-templates-in-python-with-jinjasql-b996eadd761d) — Template patterns

**Temporal Data:**
- [Bitemporal History - Martin Fowler](https://martinfowler.com/articles/bitemporal-history.html) — Temporal modeling patterns
- [Bitemporal Data Modeling (Dataversity)](https://www.dataversity.net/bitemporal-data-modeling-learn-history/) — How to learn from history

**Multi-Source Integration:**
- [Data Staging Guide (Zuar)](https://www.zuar.com/blog/complete-guide-to-data-staging/) — Staging best practices
- [dbt Staging Best Practices](https://docs.getdbt.com/best-practices/how-we-structure/2-staging) — 1-to-1 source → staging
- [Data level conflicts for multi-sources (ResearchGate)](https://www.researchgate.net/publication/313545369_Data_level_conflicts_resolution_for_multi-sources_heterogeneous_databases) — Academic research

**Python Functional Programming:**
- [Pyrsistent - Persistent/Immutable data structures](https://github.com/tobgu/pyrsistent) — Immutability patterns
- [Statically Enforcing Frozen Dataclasses](https://rednafi.com/python/statically-enforcing-frozen-dataclasses/) — Immutability patterns
- [Core Functional Programming Principles for Python](https://arjancodes.com/blog/functional-programming-principles-in-python/) — Functional patterns

### Tertiary (LOW confidence, validation needed)

**SQL Dialect Abstraction:**
- [SQL-GEN: Bridging the Dialect Gap (arXiv)](https://arxiv.org/html/2408.12733v2) — Multi-dialect patterns
- [sqlglot.dialects API](https://sqlglot.com/sqlglot/dialects.html) — SQL transpilation

**Conflict Resolution:**
- [Conflict resolution in Data Synchronization (Medium)](https://mobterest.medium.com/conflict-resolution-strategies-in-data-synchronization-2a10be5b82bc) — Patterns overview

**Security:**
- [Python vulnerabilities: Code execution in Jinja templates](https://podalirius.net/en/articles/python-vulnerabilities-code-execution-in-jinja-templates/) — SSTI risks

---
*Research completed: 2026-02-07 (v0.1.0-v0.2.0), 2026-02-09 (v0.3.0)*
*Ready for roadmap: yes*
