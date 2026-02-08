# Roadmap: Data Architect

## Milestones

- SHIPPED **v0.1.0 Init + Agents** — Phases 1-4 (shipped 2026-02-08)
- ACTIVE **v0.2.0 Pre-commit Framework** — Phase 5 (started 2026-02-08)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>SHIPPED v0.1.0 Init + Agents (Phases 1-4) — SHIPPED 2026-02-08</summary>

- [x] Phase 1: Project Foundation (2/2 plans) — completed 2026-02-07
- [x] Phase 2: CLI Scaffolding (2/2 plans) — completed 2026-02-07
- [x] Phase 3: Agent Definitions + OpenCode Integration (2/2 plans) — completed 2026-02-08
- [x] Phase 4: Agent Quality + Modeling Workflows (3/3 plans) — completed 2026-02-08

See: `.planning/milestones/v0.1.0-ROADMAP.md` for full details.

</details>

---

## v0.2.0 Pre-commit Framework

### Phase 5: Pre-commit Framework Migration

**Goal:** Pre-commit framework replaces legacy bash hooks for quality enforcement.

**Dependencies:** None (builds on v0.1.0 foundation)

**Requirements:**
- HOOK-01: Pre-commit framework installed via `make bootstrap`
- HOOK-02: `.pre-commit-config.yaml` exists with local hook running `make check`
- HOOK-03: Commit-msg hook validates conventional commit format
- HOOK-04: Legacy `scripts/hooks/` bash scripts removed
- HOOK-05: `make bootstrap` updated to use `pre-commit install`

**Success Criteria:**
1. Developer runs `make bootstrap` and pre-commit hooks are installed automatically
2. Developer commits code and `make check` runs automatically via pre-commit hook
3. Developer commits with invalid message format and commit is rejected with helpful error
4. Legacy `scripts/hooks/` directory does not exist in repository

**Phase Directory:** `.planning/phases/05-pre-commit-framework/`

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Project Foundation | v0.1.0 | 2/2 | Complete | 2026-02-07 |
| 2. CLI Scaffolding | v0.1.0 | 2/2 | Complete | 2026-02-07 |
| 3. Agent Definitions + OpenCode Integration | v0.1.0 | 2/2 | Complete | 2026-02-08 |
| 4. Agent Quality + Modeling Workflows | v0.1.0 | 3/3 | Complete | 2026-02-08 |
| 5. Pre-commit Framework Migration | v0.2.0 | 0/? | Pending | — |

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-08 — v0.2.0 Phase 5 defined*
