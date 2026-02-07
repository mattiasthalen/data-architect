# Phase 1: Project Foundation - Research

**Researched:** 2026-02-07
**Domain:** Python package build system, quality tooling, CI pipeline
**Confidence:** HIGH

## Summary

Phase 1 creates the pip-installable Python package skeleton with all quality tooling operational. The stack is verified and mature: UV 0.10.0 + Hatchling + uv-dynamic-versioning for builds, Ruff 0.15.0 for linting/formatting, mypy 1.19.1 for type checking, pytest 9.x for testing, and GitHub Actions with `astral-sh/setup-uv@v7` for CI.

Key discoveries during research: (1) Ruff 0.15.0 has renamed `TCH` rules to `TC` and removed `ANN101`/`ANN102` — the STACK.md templates must be corrected. (2) The `pre-commit` framework is explicitly recommended against in STACK.md — use a simple git hook script that calls `make check` instead. (3) The CONTEXT.md says CI matrix of Python 3.11+3.12 but `requires-python>=3.13` makes that impossible — CI should test 3.13 only. (4) For Phase 1 with minimal code, set coverage threshold to 90% but apply it only to the `data_architect` package (not tests).

**Primary recommendation:** Follow the STACK.md patterns with corrections noted below. Use simple git hooks (not the `pre-commit` framework). CI on Python 3.13 only.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- src layout: `src/data_architect/`
- Module name: `data_architect` (mirrors PyPI name `data-architect`, underscored)
- Pre-structure for CLI: `__init__.py` + `__main__.py` + `cli.py` + `py.typed` — empty cli module ready for Phase 2
- Data containers: frozen dataclasses (`@dataclass(frozen=True)`) — no NamedTuples, no mutable state
- Tests at project root: `tests/` alongside `src/`
- Mirror source structure: `tests/test_cli.py`, `tests/test_init.py` — one test file per source module
- Test-first always: every task starts with a failing test, then implementation — strict red-green-refactor
- Enforce minimum coverage threshold in CI (e.g., 90%)
- Linter/formatter: Ruff (all-in-one)
- Type checker: mypy
- Zero tolerance: lint errors, type errors, AND failing tests all block the commit
- Hook order: Format (ruff format) -> Lint (ruff check) -> Type (mypy) -> Test (pytest)
- Pre-commit hooks call `make check` — single source of truth
- CI also calls `make check` — no drift between local and CI validation
- Failing tests must never be committed
- Workflow file: `.github/workflows/ci.yml`
- Triggers: PRs + pushes to main
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

### Deferred Ideas (OUT OF SCOPE)
- CD pipeline (publish.yml, PyPI publishing) — Milestone 2 (requirement CD-01)
- Multi-OS CI testing (macOS, Windows) — revisit if user reports cross-platform issues
- Coverage reporting to external service (Codecov) — revisit when project matures
</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | >=3.13 | Runtime | Current stable (3.13.12). Required by project. UV manages installation. |
| UV | 0.10.0 | Package management, build orchestration | Available in devcontainer. All-in-one tool. |
| Hatchling | >=1.28.0 | Build backend | UV's recommended build backend. PEP 517 compliant. |
| uv-dynamic-versioning | >=0.13.0 | Version from git tags | Hatchling plugin. Works with `uv build`. |

### Development Tools

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Ruff | >=0.15.0 | Linting + formatting | Every commit — replaces flake8, isort, black |
| mypy | >=1.19.0 | Type checking | Every commit — strict mode |
| pytest | >=9.0.0 | Test framework | Every commit — function-based |
| pytest-cov | >=7.0.0 | Coverage reporting | Every test run — enforces threshold |
| hypothesis | >=6.151.0 | Property-based testing | Future phases — installed now for readiness |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Simple git hook | `pre-commit` framework | pre-commit adds complexity, requires additional Python package. STACK.md explicitly says "Consider adding later." Simple hook calling `make check` is single source of truth. |
| Hatchling | uv build backend | uv has its own build backend now, but uv-dynamic-versioning doesn't work with it (per PyPI note). Must use Hatchling. |
| mypy | ty (Astral) | ty is in beta, expected stable later 2026. Start with mypy, switch when ty is stable. |

**Installation:**
```bash
# All dev dependencies declared in pyproject.toml
uv sync --dev
```

## Architecture Patterns

### Recommended Project Structure
```
data-architect/
├── pyproject.toml              # Build config, tool config, dynamic version
├── Makefile                    # bootstrap, lint, format, type, test, check
├── uv.lock                    # Lockfile (committed)
├── .python-version            # "3.13" — UV reads this
├── .github/
│   └── workflows/
│       └── ci.yml             # CI pipeline
├── src/
│   └── data_architect/
│       ├── __init__.py        # __version__ from importlib.metadata
│       ├── __main__.py        # Entry point stub: `python -m data_architect`
│       ├── cli.py             # Empty module — placeholder for Phase 2
│       └── py.typed           # PEP 561 marker for typed package
└── tests/
    ├── __init__.py            # Make tests a package (required for imports)
    ├── test_init.py           # Tests for __init__.py (version, import)
    └── test_cli.py            # Tests for cli.py (empty module importable)
```

### Pattern 1: Dynamic Version via importlib.metadata
**What:** Package version derived from git tags, exposed via `importlib.metadata.version()`.
**When to use:** Always — no hardcoded version strings.
**Example:**
```python
# src/data_architect/__init__.py
import importlib.metadata

try:
    __version__ = importlib.metadata.version("data-architect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
```

### Pattern 2: Makefile as Single Source of Truth
**What:** `make check` runs lint + type + test. Both pre-commit hooks and CI call `make check`.
**When to use:** Always — prevents drift between local and CI.

### Pattern 3: Simple Git Hook (not pre-commit framework)
**What:** A shell script in `.git/hooks/pre-commit` that calls `make check`. A separate `commit-msg` hook validates conventional commits.
**When to use:** Installed by `make bootstrap`.

### Anti-Patterns to Avoid
- **Using `pre-commit` framework for Phase 1:** Adds a dependency and complexity. Simple git hooks calling `make check` achieve the same result with less indirection.
- **Hardcoding version strings:** Never put version in `__init__.py` or `pyproject.toml` as a static value. Always use dynamic versioning.
- **Using `list`/`dict` in frozen dataclasses:** Use `tuple`/`frozenset` for true immutability.
- **Running Makefile recipes with `source .venv/bin/activate`:** Each recipe runs in a new shell. Use `uv run` instead.

## Concrete Answers to Phase 1 Questions

### Q1: pyproject.toml — Exact Working Configuration

**Confidence: HIGH** — Verified against uv-dynamic-versioning docs, Hatchling docs, UV docs.

Critical corrections from STACK.md:
1. Package name: `data-architect` (not `warehouse-architect`)
2. Module name: `data_architect` (not `warehouse_architect`)
3. Hatchling `packages` config needed for src layout
4. `TCH` renamed to `TC` in Ruff 0.15.0
5. `ANN101`/`ANN102` removed in Ruff 0.15.0 — cannot be in `ignore` list
6. Phase 1 has NO runtime dependencies (no typer, pyyaml, jinja2, rich)
7. Entry point can't reference a real Typer app yet — stub with a simple function
8. Need `cache-keys` in `[tool.uv]` for dynamic versioning cache awareness

```toml
[project]
name = "data-architect"
dynamic = ["version"]
description = "Scaffold OpenCode AI agents and generate data warehouse scripts"
readme = "README.md"
license = "MIT"
requires-python = ">=3.13"
authors = [{ name = "Data Architect Contributors" }]
keywords = ["data-warehouse", "anchor-modeling", "opencode", "cli"]
classifiers = [
    "Development Status :: 1 - Planning",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.13",
    "Topic :: Database",
    "Typing :: Typed",
]
dependencies = []

[project.scripts]
architect = "data_architect.cli:app"

[build-system]
requires = ["hatchling", "uv-dynamic-versioning"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.hatch.build.targets.wheel]
packages = ["src/data_architect"]

[tool.uv-dynamic-versioning]
fallback-version = "0.0.0+unknown"

[tool.uv]
dev-dependencies = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "hypothesis>=6.151.0",
    "mypy>=1.19.0",
    "ruff>=0.15.0",
]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]

[tool.ruff]
target-version = "py313"
line-length = 88
src = ["src"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "I",     # isort
    "SIM",   # flake8-simplify
    "TC",    # flake8-type-checking (was TCH, renamed in 0.15.0)
    "RUF",   # ruff-specific rules
    "PT",    # flake8-pytest-style
    "ARG",   # flake8-unused-arguments
    "C4",    # flake8-comprehensions
    "T20",   # flake8-print (no print statements)
    "ANN",   # flake8-annotations (enforce type annotations)
    "S",     # flake8-bandit (security)
]
ignore = [
    "S101",    # Use of assert (needed in tests, handled by per-file-ignores)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "ARG"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=data_architect --cov-report=term-missing --strict-markers -x"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]

[tool.coverage.run]
source = ["data_architect"]
branch = true

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]
```

**Key decisions:**
- **`packages = ["src/data_architect"]`**: Required for Hatchling to find the package in src layout. Without this, `uv build` won't include the package code in the wheel.
- **`src = ["src"]`** in `[tool.ruff]`: Tells Ruff where first-party imports live, so isort sorts correctly.
- **`fallback-version = "0.0.0+unknown"`**: Obviously wrong version so accidental publishes are visible. The `+unknown` suffix makes it PEP 440 compliant local version.
- **`cache-keys`**: Per uv-dynamic-versioning tips doc, required for proper cache invalidation with dynamic versions.
- **FBT (boolean trap) removed**: Too aggressive for Phase 1. FBT rules flag common patterns like `def foo(verbose: bool)`. Add later if desired.
- **DTZ (datetimez) removed**: No datetime usage in Phase 1.
- **`-x` in pytest addopts**: Fail fast on first error.
- **mypy overrides for tests**: Relax `disallow_untyped_defs` in tests — test functions often don't need return type annotations.

### Q2: Makefile — Bootstrap and Pre-commit Hook Installation

**Confidence: HIGH**

`make bootstrap` should: (1) sync dependencies, (2) install git hooks via simple script copy.

```makefile
.DEFAULT_GOAL := check

.PHONY: bootstrap lint format type test check clean

bootstrap:  ## Install deps + git hooks
	uv sync --dev
	@echo "Installing git hooks..."
	@cp scripts/hooks/pre-commit .git/hooks/pre-commit
	@cp scripts/hooks/commit-msg .git/hooks/commit-msg
	@chmod +x .git/hooks/pre-commit .git/hooks/commit-msg
	@echo "Done! Git hooks installed."

lint:  ## Run linter and formatter check
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint issues and format
	uv run ruff check --fix .
	uv run ruff format .

type:  ## Run type checker
	uv run mypy src

test:  ## Run tests with coverage
	uv run pytest

check: lint type test  ## Run all checks (lint + type + test)

clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/ .ruff_cache
```

**Key decisions:**
- **`uv run mypy src`** (not `uv run mypy data_architect`): With src layout, mypy needs to be pointed at the `src` directory or the package within it. `src` is cleaner.
- **No `--locked` in bootstrap**: First run may not have a lockfile yet. `uv sync --dev` will create one.
- **Git hooks via file copy**: Simple, no dependency on `pre-commit` package. Scripts live in `scripts/hooks/` and are versioned.
- **`format` target separate from `lint`**: `lint` checks only (for CI/hooks), `format` fixes (for developer convenience).

### Q3: Pre-commit Approach — Simple Git Hooks

**Confidence: HIGH** — STACK.md recommends against `pre-commit` framework. CONTEXT.md says "Pre-commit hooks call `make check`."

**Recommendation: Option B — Simple git hook scripts.**

**Rationale:**
1. STACK.md explicitly says: "pre-commit: Adds complexity. CI catches everything... Consider adding later."
2. CONTEXT.md says hooks call `make check` — this works perfectly with a simple shell script.
3. No additional Python dependency (`pre-commit` package).
4. Single source of truth: hooks call `make check`, CI calls `make check`.

**Pre-commit hook script** (`scripts/hooks/pre-commit`):
```bash
#!/usr/bin/env bash
set -e

echo "Running pre-commit checks..."
make check

echo "All checks passed!"
```

**Key caveat:** Running full `make check` (lint + type + test) on every commit can be slow. For Phase 1 with minimal code, this is fine. If it becomes slow in later phases, consider running only lint+type in the hook and leaving full tests to CI.

### Q4: Conventional Commit Enforcement

**Confidence: HIGH**

**Recommendation: Simple regex check in a git `commit-msg` hook.**

No external tools needed. A bash script with a regex pattern enforces the format.

**Commit-msg hook script** (`scripts/hooks/commit-msg`):
```bash
#!/usr/bin/env bash
set -e

commit_msg_file="$1"
commit_msg=$(head -1 "$commit_msg_file")

# Conventional commit pattern: type(optional-scope): description
# Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?: .{1,}'

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "ERROR: Commit message does not follow Conventional Commits format."
    echo ""
    echo "Expected: <type>(<scope>): <description>"
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo ""
    echo "Examples:"
    echo "  feat(cli): add init command"
    echo "  fix: correct version detection"
    echo "  docs: update README"
    echo ""
    echo "Your message: $commit_msg"
    exit 1
fi
```

**Why not commitlint or other tools:**
- commitlint requires Node.js — we're a Python project
- Python-based alternatives (commitizen, python-semantic-release) add dependencies
- A regex in bash is zero-dependency and covers 95% of conventional commit validation
- Can be enhanced later if needed

### Q5: Minimal Source Files for Phase 1

**Confidence: HIGH**

Phase 1 says "No CLI commands, no agents, no business logic." But CONTEXT.md says "Pre-structure for CLI: `__init__.py` + `__main__.py` + `cli.py` + `py.typed`."

**Files to create:**

1. **`src/data_architect/__init__.py`** — Version from importlib.metadata
```python
"""Data Architect: Scaffold OpenCode AI agents for data warehouse design."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("data-architect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
```

2. **`src/data_architect/__main__.py`** — Entry point for `python -m data_architect`
```python
"""Allow running data_architect as a module: python -m data_architect."""

from data_architect.cli import app

if __name__ == "__main__":
    app()
```

3. **`src/data_architect/cli.py`** — Empty CLI stub
```python
"""CLI entry point for the architect command. Populated in Phase 2."""


def app() -> None:
    """Placeholder CLI entry point. Will be replaced with Typer app in Phase 2."""
    msg = "data-architect CLI not yet implemented. Coming in Phase 2."
    raise SystemExit(msg)
```

**Why `cli.py` exists in Phase 1:** The `pyproject.toml` declares `architect = "data_architect.cli:app"` as a console script entry point. For `uv build` to produce a valid wheel with a working entry point, `cli.py` must exist and `app` must be a callable. A stub function that exits with a message is appropriate.

**Why not Typer yet:** Phase 1 has no runtime dependencies. Typer would be the first dependency. Keep Phase 1 zero-dependency. The `app` function is a plain Python function for now; Phase 2 replaces it with a Typer app.

4. **`src/data_architect/py.typed`** — Empty marker file (PEP 561)

5. **`scripts/hooks/pre-commit`** — Git pre-commit hook
6. **`scripts/hooks/commit-msg`** — Git commit-msg hook

### Q6: Initial Tests for Phase 1

**Confidence: HIGH**

With minimal code, tests focus on verifying the package structure works:

**`tests/__init__.py`** — Empty (makes tests a package)

**`tests/test_init.py`**:
```python
"""Tests for data_architect package initialization."""

import data_architect


def test_package_is_importable() -> None:
    """Verify the package can be imported."""
    assert data_architect is not None


def test_version_is_string() -> None:
    """Verify __version__ is a non-empty string."""
    assert isinstance(data_architect.__version__, str)
    assert len(data_architect.__version__) > 0


def test_version_not_unknown() -> None:
    """Verify version is not the fallback (package is installed)."""
    assert "+unknown" not in data_architect.__version__
```

**`tests/test_cli.py`**:
```python
"""Tests for data_architect.cli module."""

import pytest

from data_architect.cli import app


def test_cli_module_is_importable() -> None:
    """Verify the CLI module can be imported."""
    assert app is not None


def test_cli_stub_exits() -> None:
    """Verify the CLI stub exits with a message."""
    with pytest.raises(SystemExit):
        app()
```

**Why these tests are sufficient:**
- They verify the package is installable and importable (PROJ-01)
- They verify dynamic versioning works (PROJ-06)
- They verify the CLI entry point is structurally valid (pre-structure for Phase 2)
- They achieve ~90%+ coverage of the minimal source code
- They follow TDD pattern: these tests define the contract before implementation

### Q7: Coverage Threshold

**Confidence: HIGH**

**Recommendation: 90%**

Rationale:
- With only `__init__.py`, `__main__.py`, and `cli.py`, achieving 90%+ is trivial
- The `pragma: no cover` exclusion for `if __name__ == "__main__"` and `if TYPE_CHECKING:` handles the uncoverable lines
- 90% matches the CONTEXT.md suggestion
- As the project grows in later phases, 90% remains a reasonable bar

### Q8: Ruff Rule Selection

**Confidence: HIGH** — Verified against Ruff 0.15.0 (confirmed installed).

**Critical corrections from STACK.md:**
1. `TCH` → `TC`: The `flake8-type-checking` rules were renamed from `TCH` to `TC` in Ruff 0.15.0. Using `TCH` produces a deprecation warning.
2. `ANN101` / `ANN102` → **REMOVED**: These rules (missing type annotation for `self`/`cls`) were removed entirely. They cannot appear in `ignore` — Ruff will error.
3. `FBT` (boolean trap) **excluded**: Too aggressive for Phase 1. Flags common patterns like boolean parameters.
4. `DTZ` (datetimez) **excluded**: No datetime usage in Phase 1.

**Recommended rule set** (see pyproject.toml above for the complete config):
- `E`, `W`, `F` — Core pycodestyle + pyflakes
- `UP` — Pyupgrade (modern Python syntax)
- `B` — Bugbear (common pitfalls)
- `I` — Import sorting
- `SIM` — Simplify (code simplification)
- `TC` — Type checking imports (runtime vs type-checking)
- `RUF` — Ruff-specific rules
- `PT` — Pytest style
- `ARG` — Unused arguments
- `C4` — Comprehensions
- `T20` — No print statements
- `ANN` — Annotations (enforce type hints)
- `S` — Bandit security checks

**Per-file ignores:**
- `tests/**`: `S101` (assert), `ANN` (annotations), `ARG` (unused args — common in fixtures)

### Q9: mypy Strictness

**Confidence: HIGH** — Verified mypy 1.19.1.

**Recommendation: Full strict mode.**

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true
```

With an override for tests:
```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

**Why strict mode works for Phase 1:** With minimal code and a functional style mandate, every function should have full type annotations. Strict mode enforces this from day one. Relaxing tests avoids forcing return type annotations on every `test_` function.

### Q10: GitHub Actions CI

**Confidence: HIGH** — Verified against UV GitHub Actions official docs (Feb 2026).

**CI Matrix Resolution:**
The CONTEXT.md says "Python matrix: 3.11 + 3.12" but `requires-python >= 3.13`. Testing on 3.11/3.12 is impossible if the package requires 3.13. **Resolution: CI tests on 3.13 only.** No matrix needed for Phase 1. Add 3.14 when it's stable.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Full history for dynamic versioning
      - uses: astral-sh/setup-uv@v7
        with:
          version: "0.10.0"
          enable-cache: true
      - run: uv python install 3.13
      - run: uv sync --dev
      - name: Check (lint + type + test)
        run: make check
      - name: Build
        run: uv build
```

**Key decisions:**
- **`fetch-depth: 0`**: Required for dynamic versioning — shallow clone loses tag history
- **`enable-cache: true`**: Built-in caching from `setup-uv@v7`, no manual cache configuration needed
- **`make check` in CI**: Same command as local pre-commit hooks — single source of truth
- **`uv build` after check**: Validates the package builds successfully
- **No Python matrix**: `requires-python >= 3.13` means 3.11/3.12 testing is impossible
- **`actions/checkout@v6`**: Current version as shown in UV's official docs
- **`astral-sh/setup-uv@v7`**: Latest stable (v7.3.0 released Feb 6, 2026)

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Version management | Version string in source | uv-dynamic-versioning + git tags | Tags are source of truth, eliminates version drift |
| Lint + format | Custom scripts | Ruff | Written in Rust, 10-100x faster, replaces 5+ tools |
| Type checking | Manual review | mypy strict mode | Catches type errors before runtime |
| Git hooks | Complex hook manager | Simple bash scripts + `make check` | Zero dependencies, single source of truth |
| Conventional commits | commitlint (Node.js) | Regex in bash commit-msg hook | Zero external dependencies |
| CI workflow | Custom Docker images | `astral-sh/setup-uv@v7` | Official, maintained, built-in caching |

## Common Pitfalls

### Pitfall 1: Hatchling Can't Find Package in src Layout
**What goes wrong:** `uv build` produces a wheel with no package code inside.
**Why it happens:** Hatchling doesn't automatically discover `src/data_architect/` without configuration.
**How to avoid:** Add `[tool.hatch.build.targets.wheel] packages = ["src/data_architect"]` to pyproject.toml.
**Warning signs:** Built wheel is suspiciously small (< 1KB). `pip install` succeeds but `import data_architect` fails.

### Pitfall 2: Dynamic Version Falls Back to 0.0.0 in CI
**What goes wrong:** CI builds produce version `0.0.0+unknown` instead of the git tag version.
**Why it happens:** GitHub Actions `actions/checkout` defaults to `fetch-depth: 1` (shallow clone, no tags).
**How to avoid:** Use `fetch-depth: 0` in checkout step. Set `fallback-version` to obviously wrong value.
**Warning signs:** CI logs showing version as `0.0.0`. Package installs but `__version__` is wrong.

### Pitfall 3: Ruff 0.15.0 Breaking Changes from STACK.md Templates
**What goes wrong:** Ruff errors on startup or produces confusing warnings.
**Why it happens:** `TCH` was renamed to `TC`. `ANN101`/`ANN102` were removed entirely.
**How to avoid:** Use `TC` (not `TCH`). Do not reference `ANN101` or `ANN102` in config.
**Warning signs:** `ruff failed: Rule 'ANN101' was removed and cannot be selected.`

### Pitfall 4: mypy Can't Find Package with src Layout
**What goes wrong:** mypy reports "Cannot find implementation or library stub" for the package.
**Why it happens:** src layout means the package isn't on the default Python path.
**How to avoid:** Run mypy as `uv run mypy src` (which adds `src` to the path), or configure `mypy_path` in pyproject.toml.
**Warning signs:** mypy errors about missing modules on the first run.

### Pitfall 5: `uv sync --locked` Fails on First Setup
**What goes wrong:** `make bootstrap` fails because there's no `uv.lock` file yet.
**Why it happens:** `--locked` requires an existing lockfile. First clone has no lockfile.
**How to avoid:** Use `uv sync --dev` (without `--locked`) in bootstrap. Use `--locked` only in CI after the lockfile exists.
**Warning signs:** `error: No lockfile found` on first `make bootstrap`.

### Pitfall 6: Coverage Report Fails Because Package Not Installed
**What goes wrong:** pytest-cov reports 0% coverage or can't find the package.
**Why it happens:** With src layout, the package must be installed (editable or not) for coverage to work. `uv sync` handles this, but running pytest directly without `uv run` doesn't.
**How to avoid:** Always run tests via `uv run pytest`. The `uv sync --dev` in bootstrap installs the package in editable mode.
**Warning signs:** 0% coverage despite tests passing.

## Code Examples

### Complete __init__.py
```python
# Source: uv-dynamic-versioning official docs
"""Data Architect: Scaffold OpenCode AI agents for data warehouse design."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("data-architect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
```

### Complete __main__.py
```python
"""Allow running data_architect as a module: python -m data_architect."""

from data_architect.cli import app

if __name__ == "__main__":  # pragma: no cover
    app()
```

### Complete cli.py (Phase 1 stub)
```python
"""CLI entry point for the architect command. Populated in Phase 2."""


def app() -> None:
    """Placeholder CLI entry point. Will be replaced with Typer app in Phase 2."""
    msg = "data-architect CLI not yet implemented. Coming in Phase 2."
    raise SystemExit(msg)
```

### Pre-commit Hook Script
```bash
#!/usr/bin/env bash
set -e

echo "Running pre-commit checks..."
make check

echo "All checks passed!"
```

### Commit-msg Hook Script
```bash
#!/usr/bin/env bash
set -e

commit_msg_file="$1"
commit_msg=$(head -1 "$commit_msg_file")

pattern='^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_-]+\))?: .{1,}'

if ! echo "$commit_msg" | grep -qE "$pattern"; then
    echo "ERROR: Commit message does not follow Conventional Commits format."
    echo ""
    echo "Expected: <type>(<scope>): <description>"
    echo "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert"
    echo ""
    echo "Examples:"
    echo "  feat(cli): add init command"
    echo "  fix: correct version detection"
    echo "  docs: update README"
    echo ""
    echo "Your message: $commit_msg"
    exit 1
fi
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `TCH` rule prefix in Ruff | `TC` rule prefix | Ruff 0.15.0 (Feb 2026) | Must use `TC` in ruff config, `TCH` is deprecated |
| `ANN101`/`ANN102` rules | Removed | Ruff 0.15.0 | Cannot reference these rules at all |
| `pre-commit` framework | Simple git hooks for small teams | Ongoing trend | Less indirection, same effectiveness |
| `setup-uv@v5`/`v6` | `setup-uv@v7` | Jan 2026 | Built-in Python version management, better caching |
| `actions/checkout@v4` | `actions/checkout@v6` | 2025 | Current standard in UV docs |
| `setuptools-scm` for versioning | `uv-dynamic-versioning` | 2024-2025 | Purpose-built for UV/Hatchling stack |

**Deprecated/outdated from STACK.md:**
- `TCH` → use `TC` instead
- `ANN101`, `ANN102` → removed, don't reference
- `warehouse_architect` → correct name is `data_architect`

## Open Questions

1. **mypy and src layout path resolution**
   - What we know: `uv run mypy src` works because `uv run` sets up the environment properly
   - What's unclear: Whether we need explicit `mypy_path` config or if `uv run` is sufficient
   - Recommendation: Start with `uv run mypy src` in Makefile. Add `mypy_path` only if issues arise.

2. **Git hook installation on Windows**
   - What we know: The project targets Linux CI only, devcontainer is Linux
   - What's unclear: If contributors use Windows locally, bash hooks won't work natively
   - Recommendation: Out of scope per CONTEXT.md (Linux only). Document WSL requirement if needed.

3. **`uv sync` vs `uv sync --locked` in CI**
   - What we know: `--locked` fails if lockfile is stale. Without it, CI might resolve different versions.
   - What's unclear: Best practice for ensuring reproducible CI builds
   - Recommendation: Commit `uv.lock`, use `uv sync --locked --dev` in CI (not in bootstrap). CI fails fast if lockfile is stale, which is the desired behavior.

## Sources

### Primary (HIGH confidence)
- [uv-dynamic-versioning docs](https://github.com/ninoseki/uv-dynamic-versioning/blob/main/docs/version_source.md) — Version source config, pyproject.toml setup, `__version__` patterns
- [uv-dynamic-versioning tips](https://github.com/ninoseki/uv-dynamic-versioning/blob/main/docs/tips.md) — cache-keys config for UV, Dependabot workaround
- [UV GitHub Actions Guide](https://docs.astral.sh/uv/guides/integration/github/) — Official CI workflow patterns, setup-uv@v7, caching
- [UV Configuring Projects](https://docs.astral.sh/uv/concepts/projects/config/) — pyproject.toml, entry points, build systems
- [Hatch Build Configuration](https://hatch.pypa.io/latest/config/build/#packages) — `packages` config for src layout
- Ruff 0.15.0 (verified locally) — `TC` rule prefix, `ANN101`/`ANN102` removed
- mypy 1.19.1 (verified locally) — Strict mode config
- [uv-dynamic-versioning PyPI](https://pypi.org/project/uv-dynamic-versioning/) — v0.13.0, Jan 2026, confirmed doesn't work with uv build backend

### Secondary (MEDIUM confidence)
- [astral-sh/setup-uv releases](https://github.com/astral-sh/setup-uv/releases) — v7.3.0 latest (Feb 6, 2026)
- STACK.md (project research) — Base templates, corrected as noted above
- PITFALLS.md (project research) — Phase 1 pitfall identification

### Tertiary (LOW confidence)
- None — all claims verified against official sources or local tool installations

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — All versions verified via `uv run` locally, docs confirmed
- Architecture: HIGH — Standard patterns from UV/Hatchling official docs
- Pitfalls: HIGH — Ruff breaking changes verified locally, CI patterns from official guide
- pyproject.toml: HIGH — Every section verified against official tool documentation
- Git hooks: HIGH — Simple bash scripts, zero external dependencies
- CI workflow: HIGH — Based on UV's official GitHub Actions guide

**Research date:** 2026-02-07
**Valid until:** 2026-03-07 (30 days — stack is stable)
