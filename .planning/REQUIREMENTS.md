# Requirements: Data Architect

**Defined:** 2026-02-07
**Core Value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate -- not template generation.

## Milestone 1 Requirements

Milestone 1 scope: `architect init` + working agents in OpenCode via `/da:*` commands.

### Project Foundation

- [ ] **PROJ-01**: Python package with src/ layout, UV + Hatchling build system, pip-installable as `data-architect`
- [ ] **PROJ-02**: Pure functional Python enforced -- no classes, frozen dataclasses for data, pure functions for behavior
- [ ] **PROJ-03**: Makefile with targets: bootstrap (install deps + pre-commit), lint, type, test, check (runs all three)
- [ ] **PROJ-04**: Pre-commit hooks enforce linting, type checking, and conventional commit messages
- [ ] **PROJ-05**: CI pipeline runs lint + type + test on pull requests
- [ ] **PROJ-06**: Dynamic versioning from git tags -- no hardcoded version strings
- [ ] **PROJ-07**: TDD enforced -- tests written before implementation for all pure functions

### CLI

- [ ] **CLI-01**: `architect init` command creates all files in cwd with zero prompts and clear output showing every file created
- [ ] **CLI-02**: Idempotent re-run -- skip existing files with warning, `--force` flag to overwrite
- [ ] **CLI-03**: `--dry-run` flag shows what would be created without writing files
- [ ] **CLI-04**: `--dir` flag scaffolds into directory other than cwd
- [ ] **CLI-05**: `--help` with usage examples for all commands
- [ ] **CLI-06**: Human-readable error messages for common failures (not writable, existing files, etc.)

### Agent Definitions

- [ ] **AGNT-01**: System/Integration Analyst agent -- technical/source-system persona, understands data structures and system constraints
- [ ] **AGNT-02**: Business Analyst agent -- domain/business-needs persona, thinks in business terms and user questions
- [ ] **AGNT-03**: Data Architect agent -- entry point, Anchor Modeling expertise, synthesizes debate, orchestrates CLP workflow
- [ ] **AGNT-04**: Data Engineer agent -- physical modeling specialist, performance, indexing, partitioning concerns
- [ ] **AGNT-05**: Analytics Engineer agent -- consumption/reporting perspective, understands how warehouse will be queried
- [ ] **AGNT-06**: Veteran Reviewer agent -- grumpy veteran persona, anti-pattern detection, methodology critique

### Agent Quality

- [ ] **QUAL-01**: Agent prompts encode deep Anchor Modeling methodology rules (anchor vs attribute vs tie vs knot criteria, historization, naming conventions)
- [ ] **QUAL-02**: CLP debate protocol encoded in agent prompts -- agents argue through Conceptual -> Logical -> Physical stages
- [ ] **QUAL-03**: Debate termination logic -- bounded iterations, convergence detection, escalation to user for final decision
- [ ] **QUAL-04**: System Analyst and Business Analyst have opposing default positions to prevent premature consensus
- [ ] **QUAL-05**: Veteran Reviewer has concrete anti-pattern checklists, not vague "review for quality" instructions

### OpenCode Integration

- [ ] **OCODE-01**: All 6 agent files in `.opencode/agents/` with valid YAML frontmatter (description, model, tools, permissions)
- [ ] **OCODE-02**: AGENTS.md in project root with shared ADSS/Anchor Modeling methodology context for all agents
- [ ] **OCODE-03**: opencode.json pre-configured -- default agent, model assignments, tool permissions, team works out of the box
- [ ] **OCODE-04**: OpenCode skills in `.opencode/skills/da-*/SKILL.md` -- invoked as `/da:*` commands
- [ ] **OCODE-05**: Spec format bootstrapping -- example YAML schemas so agents produce consistent output format

### Modeling (via Agents)

- [ ] **MODL-01**: User can start from business description and agents extract initial conceptual entities
- [ ] **MODL-02**: User can point to source schemas (Swagger, OData, ERD) in filesystem and agents incorporate them
- [ ] **MODL-03**: User can provide business questions and agents use them to inform warehouse design
- [ ] **MODL-04**: Agents produce YAML/JSON specs as output of CLP debate

## Milestone 2 Requirements

Deferred to milestone 2: `architect generate` for deterministic DAS/DAR generation.

### Spec System

- **SPEC-01**: Frozen dataclasses for all Anchor Model elements (Spec, Anchor, Attribute, Tie, Knot)
- **SPEC-02**: YAML/JSON parsing with schema validation for all specs
- **SPEC-03**: Specs versioned with explicit version field; generators check compatibility
- **SPEC-04**: Naming conventions configurable and enforced during spec validation
- **SPEC-05**: Specs organized by CLP stage (conceptual/, logical/, physical/)

### DAS Generation

- **DAS-01**: `architect generate` produces DAS scripts from source schemas (deterministic)
- **DAS-02**: Jinja2 templates for SQL generation -- templates do no logic, all decisions in pure Python transforms
- **DAS-03**: Snapshot tests guarantee deterministic output

### DAR Generation

- **DAR-01**: `architect generate` produces DAR scripts from DAB output (deterministic, Unified Star Schema)
- **DAR-02**: Bridge table, dimension, and fact table derivation
- **DAR-03**: E-commerce demo scenario validates full end-to-end workflow

### CD Pipeline

- **CD-01**: CD pipeline packages release and publishes to PyPI on tagged releases

## Out of Scope

| Feature | Reason |
|---------|--------|
| Interactive init prompts | Agent team is opinionated and fixed -- nothing to ask. Adds friction. |
| Template engine during init | Files are not parameterized -- Markdown copied verbatim. YAGNI. |
| Agent orchestration in CLI | CLI scaffolds files, OpenCode runs agents. User drives manually. |
| Runtime dependency on OpenCode | Scaffold files only -- no import or shell out to OpenCode. |
| Auto-update of scaffolded files | Need merge strategy first -- users will customize agent prompts. |
| Plugin system for custom agents | Premature abstraction -- Markdown files ARE the API. |
| Web UI / dashboard | CLI tool. OpenCode provides conversation UI. |
| Visual drag-drop modeling | YAML-first, GitOps approach. |
| Support all modeling methodologies | Opinionated: ADSS + Anchor Modeling + USS. |
| Real-time streaming | Batch-first; different problem domain. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROJ-01 | Phase 1 | Pending |
| PROJ-02 | Phase 1 | Pending |
| PROJ-03 | Phase 1 | Pending |
| PROJ-04 | Phase 1 | Pending |
| PROJ-05 | Phase 1 | Pending |
| PROJ-06 | Phase 1 | Pending |
| PROJ-07 | Phase 1 | Pending |
| CLI-01 | Phase 2 | Pending |
| CLI-02 | Phase 2 | Pending |
| CLI-03 | Phase 2 | Pending |
| CLI-04 | Phase 2 | Pending |
| CLI-05 | Phase 2 | Pending |
| CLI-06 | Phase 2 | Pending |
| AGNT-01 | Phase 3 | Pending |
| AGNT-02 | Phase 3 | Pending |
| AGNT-03 | Phase 3 | Pending |
| AGNT-04 | Phase 3 | Pending |
| AGNT-05 | Phase 3 | Pending |
| AGNT-06 | Phase 3 | Pending |
| QUAL-01 | Phase 4 | Pending |
| QUAL-02 | Phase 4 | Pending |
| QUAL-03 | Phase 4 | Pending |
| QUAL-04 | Phase 4 | Pending |
| QUAL-05 | Phase 4 | Pending |
| OCODE-01 | Phase 3 | Pending |
| OCODE-02 | Phase 3 | Pending |
| OCODE-03 | Phase 3 | Pending |
| OCODE-04 | Phase 3 | Pending |
| OCODE-05 | Phase 3 | Pending |
| MODL-01 | Phase 4 | Pending |
| MODL-02 | Phase 4 | Pending |
| MODL-03 | Phase 4 | Pending |
| MODL-04 | Phase 4 | Pending |

**Coverage:**
- Milestone 1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-02-07*
*Last updated: 2026-02-07 -- roadmap phase mapping complete*
