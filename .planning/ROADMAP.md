# Roadmap: Data Architect

## Overview

Milestone 1 delivers a pip-installable Python CLI (`architect init`) that scaffolds a team of six OpenCode-compatible AI agent definitions into any project. The journey starts with the pure-functional Python package foundation and CI pipeline, builds the CLI scaffolding mechanism with all flags and error handling, creates structurally valid agent definitions with full OpenCode integration, and culminates in methodology-deep agent prompts that drive genuine Anchor Modeling debate through CLP stages. By the end, a user can `pip install data-architect`, run `architect init`, open OpenCode, and have a team of domain-expert agents guide them through data warehouse design.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Project Foundation** - Pure-functional Python package with build system, CI, and TDD infrastructure
- [ ] **Phase 2: CLI Scaffolding** - `architect init` command with all flags, error handling, and file output
- [ ] **Phase 3: Agent Definitions + OpenCode Integration** - All 6 agent files, AGENTS.md, opencode.json, and skills scaffolded correctly
- [ ] **Phase 4: Agent Quality + Modeling Workflows** - Methodology-deep prompts, CLP debate protocol, and end-to-end modeling capability

## Phase Details

### Phase 1: Project Foundation
**Goal**: A pip-installable Python package exists with pure-functional conventions enforced, all quality tooling operational, and CI validating every PR
**Depends on**: Nothing (first phase)
**Requirements**: PROJ-01, PROJ-02, PROJ-03, PROJ-04, PROJ-05, PROJ-06, PROJ-07
**Success Criteria** (what must be TRUE):
  1. `uv build` produces a wheel and `pip install` from that wheel succeeds in a clean virtualenv
  2. `make check` runs lint + type-check + test and all three pass with zero warnings
  3. Pre-commit hooks reject a commit with a type error, a lint violation, or a non-conventional commit message
  4. CI pipeline on a pull request runs lint + type + test and reports pass/fail status
  5. Package version is derived from git tags -- no hardcoded version string exists anywhere in source
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md — Package skeleton with pyproject.toml, source stubs, and TDD tests
- [x] 01-02-PLAN.md — Makefile, git hooks, CI workflow, and full pipeline validation

### Phase 2: CLI Scaffolding
**Goal**: Users can run `architect init` and get files scaffolded into their project directory with clear feedback, idempotent behavior, and helpful errors
**Depends on**: Phase 1
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04, CLI-05, CLI-06
**Success Criteria** (what must be TRUE):
  1. `architect init` in an empty directory creates all expected files and prints every file path created
  2. `architect init` in a directory with existing files skips them with a warning; `architect init --force` overwrites them
  3. `architect init --dry-run` prints what would be created without writing any files to disk
  4. `architect init --dir /some/path` scaffolds into the specified directory instead of cwd
  5. `architect init --help` displays usage with examples; common failures (not writable, missing dir) produce human-readable error messages
**Plans:** 2 plans

Plans:
- [ ] 02-01-PLAN.md — Scaffold engine (TDD): pure functions, file manifest, conflict handling, dry-run
- [ ] 02-02-PLAN.md — Typer CLI wiring, symbol output, error handling, integration tests

### Phase 3: Agent Definitions + OpenCode Integration
**Goal**: All six agent definitions and supporting OpenCode configuration are scaffolded by `architect init` and recognized by OpenCode as a working agent team
**Depends on**: Phase 2
**Requirements**: AGNT-01, AGNT-02, AGNT-03, AGNT-04, AGNT-05, AGNT-06, OCODE-01, OCODE-02, OCODE-03, OCODE-04, OCODE-05
**Success Criteria** (what must be TRUE):
  1. After `architect init`, `.opencode/agents/` contains six agent Markdown files with valid YAML frontmatter (description, model, tools, permissions) that OpenCode can parse
  2. After `architect init`, `AGENTS.md` exists in project root with shared ADSS and Anchor Modeling methodology context
  3. After `architect init`, `opencode.json` is pre-configured with default agent, model assignments, and tool permissions so the team works without manual configuration
  4. After `architect init`, `.opencode/skills/da-*/SKILL.md` files exist and are invocable as `/da:*` commands in OpenCode
  5. After `architect init`, example YAML spec schemas exist so agents have a reference format for producing consistent output
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD

### Phase 4: Agent Quality + Modeling Workflows
**Goal**: Agent prompts encode deep Anchor Modeling methodology and CLP debate protocol so that users can drive genuine multi-agent debate that produces methodology-compliant YAML specs
**Depends on**: Phase 3
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05, MODL-01, MODL-02, MODL-03, MODL-04
**Success Criteria** (what must be TRUE):
  1. Data Architect agent can receive a business description, read source documents from the filesystem, and orchestrate a structured CLP debate across agents
  2. System Analyst and Business Analyst agents take opposing default positions on modeling questions and argue through Conceptual, Logical, and Physical stages without premature consensus
  3. Debate terminates within bounded iterations -- agents detect convergence or escalate unresolved disputes to the user for final decision
  4. Veteran Reviewer agent critiques final output using a concrete anti-pattern checklist, not vague quality commentary
  5. Agents produce YAML/JSON specs as the output of CLP debate, conforming to the bootstrapped spec format
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Foundation | 2/2 | Complete | 2026-02-07 |
| 2. CLI Scaffolding | 0/2 | Not started | - |
| 3. Agent Definitions + OpenCode Integration | 0/0 | Not started | - |
| 4. Agent Quality + Modeling Workflows | 0/0 | Not started | - |

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-07 — Phase 1 complete*
