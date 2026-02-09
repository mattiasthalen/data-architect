# Data Architect

## What This Is

A Python CLI tool that scaffolds AI agent definitions and generates deterministic data warehouse scripts from Anchor Modeling specifications. `architect init` places OpenCode-compatible agent definitions into `.opencode/` — a team of data professionals that guide users through designing a DAB layer using Anchor Modeling. `architect dab` commands manage the DAB specification (a YAML superset of the official Anchor Modeling XML schema) and generate idempotent SQL loading scripts. Users can fill the spec manually, use agents to produce it, or import from the official Anchor Modeler tool.

## Core Value

The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate — system analyst vs. business analyst, architect synthesis, rule validation, user decision — not just template generation.

## Requirements

### Validated

- ✓ Python CLI with `architect init` command — v0.1.0
- ✓ `architect init` scaffolds OpenCode agent definitions into `.opencode/` in cwd — v0.1.0
- ✓ Agent team: Data Architect (entry point), Data Engineer, Analytics Engineer, System/Integration Analyst, Business Analyst, Veteran Reviewer — v0.1.0
- ✓ Data Architect agent gathers business context, reads source docs from filesystem, orchestrates CLP debate — v0.1.0
- ✓ System Analyst and Business Analyst debate pattern for DAB modeling through CLP stages — v0.1.0
- ✓ Data Architect synthesizes debate and recommends resolution — v0.1.0
- ✓ Anchor Modeling rules applied as objective check — v0.1.0
- ✓ User makes final decision on modeling disputes — v0.1.0
- ✓ Veteran Reviewer critiques output for anti-patterns and methodology violations — v0.1.0
- ✓ YAML/JSON specification format as source of truth (output of agent debate) — v0.1.0
- ✓ Multiple input types: business description, source schemas (Swagger, ERD, OData), business questions — v0.1.0
- ✓ Pre-commit framework with `.pre-commit-config.yaml` calling `make check` — v0.2.0
- ✓ Conventional commit validation via pre-commit hook — v0.2.0
- ✓ `make bootstrap` installs pre-commit framework hooks — v0.2.0

### Active

See REQUIREMENTS.md for detailed v0.3.0 requirements.

**Current Milestone: v0.3.0 DAB Generation**

**Goal:** Define a YAML specification format (superset of official Anchor XML) and generate idempotent DAB loading scripts from it.

**Target features:**
- YAML spec format extending official anchor.xsd with staging table mappings and keyset identity
- `architect dab init` scaffolds blank spec template
- `architect dab generate` produces idempotent SQL per entity (Bruin assets or raw SQL)
- `architect dab import` converts official Anchor XML → YAML
- `architect dab export` converts YAML → official Anchor XML
- Keyset identity scheme: `entity@system~tenant|natural_key`
- Multi-source support: same anchor fed by multiple staging tables/systems
- Northwind OData as reference example and test case
- Database-agnostic SQL generation (dialect-aware)

### Deferred (v0.4.0+)

- [ ] `architect generate` produces DAS scripts from source schemas (deterministic)
- [ ] `architect generate` produces DAR scripts from DAB output (deterministic)

### Out of Scope

- Web UI — this is a CLI tool, agents run in OpenCode
- Real-time streaming support — batch-first
- `architect` CLI orchestrating agents — agents are driven manually through OpenCode
- Claude Code skill — pivoted to OpenCode agents + Python CLI
- DAS/DAR agent debate — these layers are deterministic transforms, not probabilistic
- DAS generation — deferred to v0.4.0+
- DAR generation — deferred to v0.4.0+

## Context

**Current State (v0.2.0 shipped):**
- 2,161 lines of Python (src + tests), 49 tests passing, 92.77% coverage
- 14 files scaffolded by `architect init` (6 agents, 4 skills, AGENTS.md, opencode.json, 2 spec examples)
- Pure-functional codebase: frozen dataclasses for data, pure functions for behavior
- UV + Hatchling build, dynamic versioning from git tags, Makefile quality gates
- Pre-commit framework with `.pre-commit-config.yaml` calling `make check`
- Conventional commit validation via `conventional-pre-commit` hook
- `make bootstrap` installs deps + pre-commit hooks in single command

**Methodology Stack:**
- **ADSS** (Patrik Lager): Three-layer architecture — DAS (Data According to System), DAB (Data According to Business), DAR (Data According to Requirements). Unidirectional flow DAS → DAB → DAR. Each layer decouples the next from upstream changes.
- **Anchor Modeling** (DAB): Highly normalized technique — anchors, attributes, ties, knots. Each attribute is its own table. Schema evolution is non-destructive (additive only). Designed for agility and resilience to change.
- **Unified Star Schema** (Francesco Puppini, DAR): Single bridge table connecting all dimensions to facts. Eliminates fan traps and chasm traps. Isolated data products per ADSS principles.
- **CLP**: Conceptual → Logical → Physical modeling. Applies only to DAB (probabilistic, needs AI reasoning). DAS and DAR are deterministic transformations.

**Architecture Pattern:**
- **CLI tool** (`architect`): Python package, pip-installable. Commands: `init` (scaffold agents), `dab init` (scaffold spec template), `dab generate` (spec → SQL), `dab import` (XML → YAML), `dab export` (YAML → XML).
- **OpenCode agents** (`.opencode/`): Agent definitions scaffolded by `init`. User drives them manually in OpenCode. Agents handle creative/analytical work — understanding the business, debating models, checking methodology. Agents optionally produce a filled-out DAB spec.
- **DAB YAML spec**: Superset of official Anchor Modeling XML schema. Extends with staging table mappings (column-level, multi-source) and keyset identity scheme (`entity@system~tenant|natural_key`). Interoperable with official Anchor Modeler via import/export.
- **Deterministic generators**: `architect dab generate` transforms YAML spec → idempotent SQL loading scripts per entity. v1 output: Bruin assets or raw SQL. Database-agnostic (dialect-aware).
- **Keyset identity**: All IDs prefixed `anchor@system~tenant|natural_key` (e.g., `order@northwind~eu|10248`). Encodes entity type, source system, tenant, and source natural key. Enables multi-source feeding of same anchor.

**Agent Team Roles:**
- **Data Architect**: Entry point and design authority. Gathers business context and source docs from filesystem. Orchestrates debate, synthesizes recommendations, enforces naming standards and consistency.
- **Data Engineer**: Physical modeling specialist. Performance, indexing, partitioning, orchestration concerns.
- **Analytics Engineer**: DAR layer perspective. Understands how the warehouse will be consumed.
- **System/Integration Analyst**: Source system expert. Understands what data exists, how it's structured, what it means technically.
- **Business Analyst**: Business domain expert. Understands what the business needs, how they think about their data, what questions they ask.
- **Veteran Reviewer**: Grumpy, battle-scarred DW engineer who's seen every anti-pattern since Inmon's early days. Critiques everything.

**Debate Pattern (DAB):**
1. User talks to Data Architect — describes business, points to source docs in cwd
2. Data Architect reads source files, establishes context
3. System Analyst presents source-system perspective on entities and relationships
4. Business Analyst presents business-domain perspective
5. They argue through CLP stages — what's an anchor? what's an attribute? what's a tie?
6. Data Architect synthesizes and recommends
7. Anchor Modeling methodology rules are applied as an objective check
8. User gets the full picture and makes the final call
9. Veteran Reviewer critiques the final model
10. Specs written to filesystem as YAML/JSON

**User Flow:**
1. `pip install data-architect`
2. `architect init` → agent definitions + skills appear in `.opencode/`
3. `architect dab init` → blank YAML spec template scaffolded
4. Fill spec manually OR use agents (`/da:start` in OpenCode) to produce filled spec
5. `architect dab generate` → idempotent SQL loading scripts per entity
6. Optionally: `architect dab export` → official Anchor XML for use in Anchor Modeler tool
7. Optionally: `architect dab import` → bring XML from Anchor Modeler back into YAML

**Reference data:**
- Official Anchor Modeling repo cloned to `.references/anchor/` (schema: `anchor.xsd`, example: `example.xml`)
- Northwind OData metadata: `https://demodata.grapecity.com/northwind/odata/v1/$metadata`

**OpenCode Integration:**
- Agents live in `.opencode/agents/` as Markdown with YAML frontmatter
- Skills live in `.opencode/skills/da-*/SKILL.md` — invoked as `/da:*` commands
- Project rules in `AGENTS.md`, config in `opencode.json`

**Delivery:**
- Python package on PyPI (`data-architect`)
- OpenCode agent definitions + skills (scaffolded by `architect init`)
- Target user: data engineers

## Constraints

- **Language**: Python — pure functional style, no classes, pure functions + immutable data (dataclasses/NamedTuples for data, functions for behavior)
- **Testing**: TDD mandatory — tests written before implementation
- **Platform**: OpenCode.ai agents — must conform to OpenCode's agent definition format
- **CLI**: Python CLI (`architect init`, `architect generate`)
- **Tooling**: UV for package management and builds. Linting, type checking, and testing enforced.
- **Pre-commit**: Pre-commit framework (`.pre-commit-config.yaml`) installed via `make bootstrap`. Hooks call `make check` as single source of truth. Enforces lint, type check, and commit message format (conventional commits) before every commit.
- **Build**: Makefile with targets: `bootstrap` (install deps + pre-commit hooks), `lint`, `type`, `test`, `check` (runs all three)
- **Versioning**: Dynamic versioning from git tags — no hardcoded version strings
- **CI/CD**: CI runs lint + type + test on PRs. CD packages release and publishes to PyPI on tagged releases.
- **Methodology**: ADSS + Anchor Modeling + USS are non-negotiable. This is the opinion.
- **Separation**: CLP debate (probabilistic, agents) vs DAS/DAR generation (deterministic, code). Clear boundary.
- **Spec Format**: YAML/JSON source of truth. Generators consume specs, not prose.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pivot from Claude Code skill to Python CLI + OpenCode agents | More flexibility, provider-agnostic, broader reach | ✓ Good — v0.1.0 |
| Pure functional Python, no classes | Immutability reduces bugs, easier to test, fits TDD mandate | ✓ Good — v0.1.0 |
| TDD mandatory | Correctness is critical for data warehouse design tooling | ✓ Good — 49 tests, 92.77% coverage |
| OpenCode agents instead of Claude-specific | Provider flexibility, OpenCode.ai agent ecosystem | ✓ Good — v0.1.0 |
| DAB is probabilistic (agents), DAS/DAR are deterministic (generators) | CLP debate needs AI reasoning; DAS/DAR are mechanical transforms from known inputs | ✓ Good — clean separation |
| Data Architect as entry point agent | Natural design authority, gathers context before orchestrating debate | ✓ Good — v0.1.0 |
| Specs as contract between agents and generators | Clean separation of AI creativity and deterministic output | ✓ Good — v0.1.0 |
| Anchor Modeling for DAB | Maximum agility — non-destructive schema evolution, resilient to change | ✓ Good — v0.1.0 |
| Milestone 1: init + agents only | Prove the agent experience before building generators | ✓ Good — shipped in 2 days |
| UV for package management | Modern, fast, replaces pip/poetry/setuptools | ✓ Good — v0.1.0 |
| Dynamic versioning from git tags | Single source of truth for version, no manual bumps | ✓ Good — v0.1.0 |
| Makefile as task runner | Universal, no extra deps, bootstrap/lint/type/test/check | ✓ Good — v0.1.0 |
| Simple git hooks over pre-commit framework | Zero Node.js/Python deps for hooks, bash is sufficient | ✓ Revisited — migrated to pre-commit framework in v0.2.0 |
| Pre-commit framework over bash hooks | Declarative YAML config, ecosystem compatibility, automatic installation | ✓ Good — v0.2.0 |
| conventional-pre-commit external hook | Maintained hook instead of hand-rolled regex | ✓ Good — v0.2.0 |
| language: system for make-check hook | Make check needs full project environment access | ✓ Good — v0.2.0 |
| Skills route through data-architect agent | Single orchestration point, consistent entry | ✓ Good — v0.1.0 |
| Bounded iteration debate (5 rounds max) | Prevents infinite loops, forces convergence or user escalation | ✓ Good — v0.1.0 |
| DAB before DAS/DAR | DAB is the core methodology layer — prove the spec format and generation before mechanical layers | — Pending |
| YAML superset of official Anchor XML | Interoperability with official tooling while extending for staging/keyset needs | — Pending |
| Keyset identity over surrogate integers | Encodes source provenance (system + tenant) in the key itself, enables multi-source merging | — Pending |
| Bruin as v1 output format | Modern data pipeline tool with materialization strategies matching anchor patterns (merge, SCD2) | — Pending |
| Northwind as reference example | Well-known schema, OData metadata available, good mix of entity types and relationships | — Pending |

---
*Last updated: 2026-02-09 after v0.3.0 milestone start*
