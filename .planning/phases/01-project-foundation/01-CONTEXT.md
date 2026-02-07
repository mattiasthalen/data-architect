# Phase 1: Project Foundation - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

A pip-installable Python package exists with pure-functional conventions enforced, all quality tooling operational, and CI validating every PR. This phase delivers the build system, test infrastructure, pre-commit hooks, and CI pipeline — the foundation every subsequent phase builds on. No CLI commands, no agents, no business logic.

</domain>

<decisions>
## Implementation Decisions

### Package structure
- src layout: `src/data_architect/`
- Module name: `data_architect` (mirrors PyPI name `data-architect`, underscored)
- Pre-structure for CLI: `__init__.py` + `__main__.py` + `cli.py` + `py.typed` — empty cli module ready for Phase 2
- Data containers: frozen dataclasses (`@dataclass(frozen=True)`) — no NamedTuples, no mutable state

### TDD conventions
- Tests at project root: `tests/` alongside `src/`
- Mirror source structure: `tests/test_cli.py`, `tests/test_init.py` — one test file per source module
- Test-first always: every task starts with a failing test, then implementation — strict red-green-refactor
- Enforce minimum coverage threshold in CI (e.g., 90%)

### Pre-commit & quality gates
- Linter/formatter: Ruff (all-in-one — replaces flake8, isort, black)
- Type checker: mypy
- Zero tolerance: lint errors, type errors, AND failing tests all block the commit
- Hook order: Format (ruff format) -> Lint (ruff check) -> Type (mypy) -> Test (pytest)
- Pre-commit hooks call `make check` — single source of truth
- CI also calls `make check` — no drift between local and CI validation
- Failing tests must never be committed

### CI pipeline shape
- Workflow file: `.github/workflows/ci.yml`
- Triggers: PRs + pushes to main
- Python matrix: 3.11 + 3.12
- OS: Linux only (ubuntu-latest)
- Pipeline steps: checkout + install deps -> `make check` -> `uv build`
- No coverage reporting, no install-test — keep Phase 1 CI minimal

### Claude's Discretion
- Ruff rule selection and configuration
- mypy strictness level
- Exact coverage threshold number
- Makefile target implementation details
- pyproject.toml metadata fields
- pytest configuration and plugin choices

</decisions>

<specifics>
## Specific Ideas

- Pre-commit and CI both call `make check` — one command, one source of truth, no drift
- `make check` runs lint + type-check + test (the three quality gates)
- `make bootstrap` installs deps + pre-commit hooks
- CD workflow (`publish.yml`) is deferred to Milestone 2

</specifics>

<deferred>
## Deferred Ideas

- CD pipeline (publish.yml, PyPI publishing) — Milestone 2 (requirement CD-01)
- Multi-OS CI testing (macOS, Windows) — revisit if user reports cross-platform issues
- Coverage reporting to external service (Codecov) — revisit when project matures

</deferred>

---

*Phase: 01-project-foundation*
*Context gathered: 2026-02-07*
