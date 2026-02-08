# Requirements: Data Architect

**Defined:** 2026-02-08
**Core Value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate -- not just template generation.

## v0.2.0 Requirements

Requirements for pre-commit framework migration. Each maps to roadmap phases.

### Pre-commit Framework

- [ ] **HOOK-01**: Pre-commit framework installed via `make bootstrap`
- [ ] **HOOK-02**: `.pre-commit-config.yaml` exists with a `local` hook that runs `make check`
- [ ] **HOOK-03**: Commit-msg hook validates conventional commit format via pre-commit
- [ ] **HOOK-04**: Legacy `scripts/hooks/` bash scripts removed
- [ ] **HOOK-05**: `make bootstrap` target updated to use `pre-commit install` instead of manual hook copying

## Future Requirements

Deferred to future milestones. Tracked but not in current roadmap.

### Code Generation (v0.3.0+)

- **GEN-01**: `architect generate` produces DAS scripts from source schemas (deterministic)
- **GEN-02**: `architect generate` produces DAR scripts from DAB output (deterministic)
- **GEN-03**: Demo scenario validation (e-commerce or similar)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Custom hook scripts beyond make check | `make check` is single source of truth — no per-hook config |
| CI/CD changes | CI already runs `make check`, no changes needed |
| Additional linters not in current Makefile | Scope is migration, not adding new checks |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| HOOK-01 | TBD | Pending |
| HOOK-02 | TBD | Pending |
| HOOK-03 | TBD | Pending |
| HOOK-04 | TBD | Pending |
| HOOK-05 | TBD | Pending |

**Coverage:**
- v0.2.0 requirements: 5 total
- Mapped to phases: 0
- Unmapped: 5

---
*Requirements defined: 2026-02-08*
*Last updated: 2026-02-08 after initial definition*
