# Phase 5: Pre-commit Framework Migration

**Milestone:** v0.2.0 Pre-commit Framework
**Goal:** Pre-commit framework replaces legacy bash hooks for quality enforcement.

## Requirements

- HOOK-01: Pre-commit framework installed via `make bootstrap`
- HOOK-02: `.pre-commit-config.yaml` exists with local hook running `make check`
- HOOK-03: Commit-msg hook validates conventional commit format
- HOOK-04: Legacy `scripts/hooks/` bash scripts removed
- HOOK-05: `make bootstrap` updated to use `pre-commit install`

## Success Criteria

1. Developer runs `make bootstrap` and pre-commit hooks are installed automatically
2. Developer commits code and `make check` runs automatically via pre-commit hook
3. Developer commits with invalid message format and commit is rejected with helpful error
4. Legacy `scripts/hooks/` directory does not exist in repository

## Dependencies

None (builds on v0.1.0 foundation)

## Plans

Plans for this phase will be created via `/gsd:plan-phase 5` and stored as `PLAN-*.md` files in this directory.

---
*Phase defined: 2026-02-08*
