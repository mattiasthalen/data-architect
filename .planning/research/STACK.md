# Stack Research

**Domain:** Python CLI tool + OpenCode.ai agent scaffolding (data warehouse design)
**Researched:** 2026-02-07
**Confidence:** HIGH (core stack verified from official docs; OpenCode agent format confirmed)

## Executive Summary

This stack supports a Python CLI tool (`architect`) that scaffolds OpenCode.ai agent definitions and generates deterministic data warehouse scripts. The project mandates pure functional Python (no classes), TDD, UV for package management, and dynamic versioning from git tags. Every technology choice below is driven by these constraints.

The stack is centered on the Astral ecosystem (UV + Ruff + ty) for tooling, Typer for the CLI, frozen dataclasses for immutable data, Hatchling + uv-dynamic-versioning for builds, and pytest + Hypothesis for testing. OpenCode.ai agent definitions are Markdown files with YAML frontmatter, placed in `.opencode/agents/`.

## OpenCode.ai Agent Format (CRITICAL)

**Confidence: HIGH** -- Verified from official OpenCode.ai documentation (https://opencode.ai/docs/agents/, https://opencode.ai/docs/config/, https://opencode.ai/docs/skills/, https://opencode.ai/docs/rules/).

OpenCode (v1.1.53, by SST, 99.7k GitHub stars) defines agents as **Markdown files with YAML frontmatter**. This is the format `architect init` must produce.

### Directory Structure

```
.opencode/
  agents/
    data-architect.md       # Agent definitions (Markdown + YAML frontmatter)
    system-analyst.md
    business-analyst.md
    data-engineer.md
    analytics-engineer.md
    veteran-reviewer.md
  skills/
    clp-debate/
      SKILL.md              # Reusable skill for CLP workflow
    anchor-modeling/
      SKILL.md              # Reusable skill for AM rules
  opencode.json             # Project-level OpenCode configuration (optional)
AGENTS.md                   # Project-level rules/instructions (root of project)
```

### Agent Definition Format

Each agent is a `.md` file in `.opencode/agents/`. The filename becomes the agent identifier.

```markdown
---
description: "Brief explanation of agent purpose" # REQUIRED
mode: primary|subagent|all                        # REQUIRED
model: provider/model-id                          # Optional, defaults to global
temperature: 0.0-1.0                              # Optional
tools:                                            # Optional, inherits global defaults
  write: true|false
  edit: true|false
  bash: true|false
  skill: true|false
  mymcp_*: true|false                             # Wildcard support
permission:                                       # Optional, overrides global settings
  edit: ask|allow|deny
  bash:
    "*": ask
    "git status *": allow
  task:                                           # Controls subagent invocation
    "*": deny
    "agent-name": ask
top_p: 0.0-1.0                                   # Optional
disable: true|false                               # Optional
hidden: true|false                                # Optional, hide from @ menu
color: "#hex" or theme-color-name                 # Optional
steps: number                                     # Optional, max agentic iterations
prompt: path/to/system-prompt.md                  # Optional, custom system prompt path
---

System prompt / persona content goes here as Markdown body.
This is the agent's instruction set.
```

### Agent Modes

| Mode | Purpose | Behavior |
|------|---------|----------|
| `primary` | Top-level agents users interact with directly | Shown in Tab switcher (like built-in `build` and `plan`) |
| `subagent` | Specialist agents invoked by other agents | Invoked via `@agent-name` notation or Task tool |
| `all` | Available in both contexts | Can be used directly or as subagent |

### Skill Format

Skills are reusable instruction sets loaded on-demand via the `skill` tool.

```
.opencode/skills/<skill-name>/SKILL.md
```

```markdown
---
name: "skill-name"          # REQUIRED, 1-64 chars, lowercase alphanumeric + hyphens
description: "Purpose"      # REQUIRED, 1-1024 chars
license: "MIT"              # Optional
compatibility: "opencode"   # Optional
metadata:                   # Optional, custom key-value pairs
  version: "1.0"
---

Skill instructions as Markdown body.
```

### Configuration (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "agent": {
    "data-architect": {
      "description": "Entry point agent for warehouse design",
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-5"
    }
  },
  "instructions": ["AGENTS.md"],
  "tools": { "write": true, "bash": true },
  "permission": { "edit": "ask", "bash": "ask" }
}
```

### Design Implications for `architect init`

1. **Output is pure text files** -- Markdown + YAML frontmatter + JSON. No binary formats, no compilation.
2. **Agent identity = filename** -- `data-architect.md` creates agent `data-architect`.
3. **Personas live in Markdown body** -- The system prompt IS the Markdown content after frontmatter.
4. **Skills are separate from agents** -- CLP debate rules, Anchor Modeling rules should be skills, not baked into agent prompts.
5. **Configuration merges** -- `opencode.json` in project root merges with user's global config. Don't override user settings.
6. **Rules file at root** -- `AGENTS.md` at project root provides shared context across all agents.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **Python** | >=3.13 | Runtime | 3.13 is current stable (3.13.12, Feb 2026). 3.14 exists but too new for broad compatibility. 3.13 has improved error messages, `typing` improvements. | HIGH |
| **UV** | >=0.10.0 | Package management, build orchestration, Python version management | Astral's all-in-one tool replaces pip, poetry, pyenv, virtualenv. 10-100x faster than pip. Cross-platform lockfile. Official GitHub Actions support. De facto standard for new Python projects in 2026. | HIGH |
| **Typer** | >=0.21.0 | CLI framework for `architect` command | Function-based (no classes required). Type-hint driven. Built on Click. Auto-generates `--help`. Supports subcommands natively (`architect init`, `architect generate`). Ideal for functional Python style. | HIGH |
| **Hatchling** | >=1.28.0 | Build backend | UV's recommended build backend. PEP 517 compliant. Extensible via plugins (uv-dynamic-versioning). Used by FastAPI, Pydantic, and other major projects. | HIGH |

### Immutable Data & Functional Python

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **`dataclasses` (stdlib, `frozen=True`)** | stdlib | Immutable data structures | No external dependency. `@dataclass(frozen=True)` prevents mutation. `dataclasses.replace()` for functional updates. Type-checker friendly. Sufficient for all project data models (specs, configs, agent defs). | HIGH |
| **`typing` / `typing_extensions`** | stdlib | Type annotations for functional signatures | `TypeAlias`, `TypedDict`, `Protocol`, `NamedTuple` -- all support functional patterns without classes. `Callable` types for function composition. | HIGH |
| **`functools` (stdlib)** | stdlib | Function composition, caching | `reduce`, `partial`, `lru_cache`, `@cache`. Standard library, no deps. | HIGH |
| **`pathlib` (stdlib)** | stdlib | Immutable path handling | `Path` objects are immutable. Functional chaining (`path / "subdir" / "file.md"`). | HIGH |

**Pattern: Pure functional Python without classes**

```python
from dataclasses import dataclass, replace
from typing import Sequence

# Immutable data (frozen dataclass, NOT a class with methods)
@dataclass(frozen=True)
class AgentDefinition:
    name: str
    description: str
    mode: str
    model: str | None = None
    temperature: float | None = None

# Pure function (NOT a method)
def create_agent_markdown(agent: AgentDefinition) -> str:
    """Pure function: AgentDefinition -> Markdown string."""
    frontmatter = build_frontmatter(agent)
    body = load_persona_template(agent.name)
    return f"---\n{frontmatter}---\n\n{body}"

# Functional update (NOT mutation)
def with_model(agent: AgentDefinition, model: str) -> AgentDefinition:
    return replace(agent, model=model)
```

**Why NOT external FP libraries (pyrsistent, Expression, pfun, etc.):**
- Add dependency for minimal gain -- frozen dataclasses + stdlib cover 95% of needs
- Team must learn non-standard APIs
- Type checker support is weaker for exotic FP types
- Pyrsistent's PVector/PMap are overkill for this domain (we're generating text files, not building persistent data structures)

### Development Tools

| Tool | Version | Purpose | Why Recommended | Confidence |
|------|---------|---------|-----------------|------------|
| **Ruff** | >=0.15.0 | Linting + formatting (replaces flake8, isort, black, pylint) | Single tool for lint + format. Written in Rust, extremely fast. 2026 style guide. Replaces 5+ tools. Astral ecosystem (same team as UV). | HIGH |
| **Mypy** | >=1.19.0 | Static type checking in CI | Mature, well-understood, plugin ecosystem. Strict mode catches functional style violations. Industry standard for CI type checking. | HIGH |
| **pytest** | >=9.0.0 | Test framework | De facto Python testing standard. Fixture system, parametrize, plugin ecosystem. Function-based (no test classes needed). | HIGH |
| **Hypothesis** | >=6.151.0 | Property-based testing | Generates hundreds of test cases from strategies. Essential for testing deterministic generators (same input = same output). Tests edge cases humans miss. | HIGH |
| **pytest-cov** | >=7.0.0 | Coverage reporting | Integrates coverage.py with pytest. Required for enforcing coverage thresholds. | HIGH |

### Build & Versioning

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **uv-dynamic-versioning** | >=0.13.0 | Dynamic version from git tags | Hatchling plugin. Version derived from `git tag v0.1.0`. No hardcoded version strings. Works with `uv build`. Designed specifically for UV + Hatchling stack. | HIGH |
| **Makefile** | N/A | Task runner | Universal, no extra deps. Targets: `bootstrap`, `lint`, `type`, `test`, `check`. Every developer knows Make. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| **PyYAML** | >=6.0 | YAML parsing/serialization | Reading/writing YAML specs produced by agent debate. Loading YAML frontmatter for agent definitions. | HIGH |
| **Jinja2** | >=3.1 | Template engine for code generation | `architect generate` renders SQL DDL, dbt models from specs + templates. Jinja is the dbt standard. | HIGH |
| **rich** | >=13.0 | Terminal output formatting | Pretty-print CLI output (tables, progress, syntax highlighting). Typer recommends rich for enhanced output. | MEDIUM |

## pyproject.toml Configuration

**Confidence: HIGH** -- Verified from UV docs, Hatchling docs, uv-dynamic-versioning docs.

```toml
[project]
name = "warehouse-architect"
dynamic = ["version"]
description = "Scaffold OpenCode AI agents and generate data warehouse scripts"
readme = "README.md"
license = "MIT"
requires-python = ">=3.13"
authors = [{ name = "Your Name", email = "you@example.com" }]
keywords = ["data-warehouse", "anchor-modeling", "opencode", "cli"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.13",
    "Topic :: Database",
    "Typing :: Typed",
]
dependencies = [
    "typer>=0.21.0",
    "pyyaml>=6.0",
    "jinja2>=3.1",
    "rich>=13.0",
]

[project.scripts]
architect = "warehouse_architect.cli:app"

[build-system]
requires = ["hatchling", "uv-dynamic-versioning"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "uv-dynamic-versioning"

[tool.uv-dynamic-versioning]
fallback-version = "0.0.0"

[tool.uv]
dev-dependencies = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "hypothesis>=6.151.0",
    "mypy>=1.19.0",
    "ruff>=0.15.0",
]

[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "UP",    # pyupgrade
    "B",     # flake8-bugbear
    "I",     # isort
    "SIM",   # flake8-simplify
    "TCH",   # flake8-type-checking
    "RUF",   # ruff-specific rules
    "PT",    # flake8-pytest-style
    "ARG",   # flake8-unused-arguments
    "FBT",   # flake8-boolean-trap
    "C4",    # flake8-comprehensions
    "DTZ",   # flake8-datetimez
    "T20",   # flake8-print (no print statements)
    "ANN",   # flake8-annotations (enforce type annotations)
    "S",     # flake8-bandit (security)
]
ignore = [
    "ANN101",  # Missing type annotation for self (we don't use self)
    "ANN102",  # Missing type annotation for cls (we don't use cls)
    "S101",    # Use of assert (needed for tests)
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN"]

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_subclassing_any = true
check_untyped_defs = true
no_implicit_reexport = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=warehouse_architect --cov-report=term-missing --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
]

[tool.coverage.run]
source = ["warehouse_architect"]
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

## Dynamic Versioning

**Confidence: HIGH** -- Verified from uv-dynamic-versioning docs and UV official guides.

### How It Works

1. Tag a commit: `git tag v0.1.0`
2. `uv build` reads the tag and sets the version automatically
3. Between tags, version becomes `0.1.0.devN+gHASH` (N = commits since tag)
4. No `__version__` string maintained anywhere in source code

### Exposing Version in Package

```python
# warehouse_architect/__init__.py
import importlib.metadata

try:
    __version__ = importlib.metadata.version("warehouse-architect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
```

### Version Flow

```
git tag v0.1.0  -->  uv build  -->  warehouse_architect-0.1.0-py3-none-any.whl
                                     warehouse_architect-0.1.0.tar.gz
```

## Makefile

```makefile
.DEFAULT_GOAL := check

.PHONY: bootstrap lint type test check clean

bootstrap:  ## Install all dependencies
	uv sync --locked --all-extras --dev

lint:  ## Run linter and formatter check
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint issues and format
	uv run ruff check --fix .
	uv run ruff format .

type:  ## Run type checker
	uv run mypy warehouse_architect

test:  ## Run tests with coverage
	uv run pytest

check: lint type test  ## Run all checks (lint + type + test)

clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/
```

## CI/CD with GitHub Actions

**Confidence: HIGH** -- Verified from UV official GitHub Actions guide (https://docs.astral.sh/uv/guides/integration/github/).

### CI Workflow (PRs)

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
      - uses: astral-sh/setup-uv@v7
        with:
          version: "0.10.0"
          enable-cache: true
      - run: uv python install 3.13
      - run: uv sync --locked --all-extras --dev
      - name: Lint
        run: |
          uv run ruff check .
          uv run ruff format --check .
      - name: Type check
        run: uv run mypy warehouse_architect
      - name: Test
        run: uv run pytest
```

### CD Workflow (PyPI Publish on Tags)

```yaml
name: Publish

on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # Full history for dynamic versioning
      - uses: astral-sh/setup-uv@v7
        with:
          version: "0.10.0"
      - run: uv python install 3.13
      - run: uv build
      - name: Smoke test
        run: |
          uv run --with ./dist/*.whl -- python -c "import warehouse_architect; print(warehouse_architect.__version__)"
      - run: uv publish
```

**Trusted Publishing:** PyPI supports OpenID Connect tokens from GitHub Actions. No API keys needed -- configure a Trusted Publisher on PyPI pointing to your GitHub repo.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| CLI Framework | **Typer** | Click | Typer IS Click with type hints. Click requires more boilerplate. Typer's function-based API aligns with our functional Python mandate. |
| CLI Framework | **Typer** | argparse | argparse is verbose, no auto-completion, no rich output. Typer generates all of this from type hints. |
| Build Backend | **Hatchling** | setuptools | Hatchling is simpler config, better plugin system. UV recommends Hatchling. setuptools requires more boilerplate. |
| Build Backend | **Hatchling** | flit | flit is too simple -- no plugin system for dynamic versioning. |
| Dynamic Versioning | **uv-dynamic-versioning** | setuptools-scm | setuptools-scm requires setuptools backend. uv-dynamic-versioning is designed for Hatchling + UV stack. |
| Dynamic Versioning | **uv-dynamic-versioning** | versioningit | versioningit works but smaller community. uv-dynamic-versioning is purpose-built for UV projects. |
| Type Checker | **Mypy** (CI) | Pyright | Mypy is better for CI (stricter, more established). Pyright is better for IDE. Use both: Pyright via Pylance in VS Code, Mypy in CI. |
| Type Checker | **Mypy** (CI) | ty (Astral) | ty is in beta (stable expected later 2026). 10-60x faster than Mypy. Monitor for graduation to stable, then switch. |
| Linter | **Ruff** | flake8 + isort + black | Ruff replaces all three in one tool. 10-100x faster. Same team as UV. No reason to use separate tools in 2026. |
| Template Engine | **Jinja2** | Mako | Jinja2 is the dbt standard. If generated SQL needs to work with dbt, it must be Jinja-compatible. |
| YAML Library | **PyYAML** | ruamel.yaml | PyYAML is simpler and sufficient. ruamel.yaml preserves comments (useful if we need round-trip editing later, but not for generation). |
| Immutable Data | **frozen dataclasses** | pyrsistent | External dep for minimal gain. frozen dataclasses are stdlib, type-checker friendly, and sufficient for this domain. |
| Immutable Data | **frozen dataclasses** | NamedTuple | NamedTuple is slightly lighter but frozen dataclasses have better defaults, `replace()` support, and clearer intent. |
| Test Framework | **pytest** | unittest | pytest is function-based (no test classes). Better fixtures, parametrize, and plugin ecosystem. De facto standard. |
| Package Manager | **UV** | Poetry | UV is 10-100x faster, has lockfile, replaces pyenv+pip+poetry. Astral ecosystem consistency with Ruff. Industry has converged on UV in 2026. |
| Package Manager | **UV** | pip + venv | Manual, slow, no lockfile, no Python version management. UV does everything better. |

## What NOT to Use

| Avoid | Why | Use Instead | Confidence |
|-------|-----|-------------|------------|
| **Classes with methods** | Project mandate: pure functional Python. Classes encourage mutable state and method-based behavior. | Frozen dataclasses for data, standalone functions for behavior. | HIGH |
| **Poetry** | Superseded by UV in 2026. Slower, less features, less ecosystem support. | UV | HIGH |
| **Black + isort + flake8** | Three separate tools replaced by one (Ruff). More config, slower, more deps. | Ruff | HIGH |
| **Pylint** | Slow, opinionated in ways that conflict with functional style. | Ruff | HIGH |
| **pyrsistent / Expression / pfun** | External FP libraries add complexity for minimal gain. Frozen dataclasses cover our needs. | `dataclasses(frozen=True)` + stdlib | HIGH |
| **setuptools (as build backend)** | More config, less plugin support than Hatchling. UV recommends Hatchling. | Hatchling | HIGH |
| **tox** | UV replaces tox for running tests across environments. `uv run` handles venv management. | `uv run pytest` | MEDIUM |
| **pre-commit** | Adds complexity. CI catches everything. Developers can run `make check` locally. Consider adding later if team discipline is an issue. | `make check` locally, CI enforcement | MEDIUM |
| **Pydantic** | Overkill for this project. Pydantic is for runtime validation of external data (APIs, user input). Our specs are YAML files validated at load time. Frozen dataclasses + manual validation functions are sufficient and avoid the class-heavy Pydantic API. | Frozen dataclasses + validation functions | MEDIUM |

## Enforcing Functional Style with Ruff

Ruff cannot directly ban `class` usage (no such rule exists). Enforcement strategy:

1. **Code review convention**: No classes except `@dataclass(frozen=True)` for data.
2. **Ruff ANN rules**: Force type annotations on all functions -- makes function signatures explicit.
3. **Ruff FBT rules**: Ban boolean traps -- encourages explicit function parameters.
4. **Mypy strict mode**: Forces complete typing, which naturally discourages OOP patterns.
5. **Project convention in AGENTS.md / CONTRIBUTING.md**: Document the rule. Example:
   - YES: `@dataclass(frozen=True)` for data, standalone functions for logic
   - NO: Classes with methods, mutable state, inheritance

## Project Directory Structure

```
warehouse-architect/
  pyproject.toml
  uv.lock
  Makefile
  .python-version              # "3.13"
  .github/
    workflows/
      ci.yml
      publish.yml
  warehouse_architect/
    __init__.py                 # __version__ via importlib.metadata
    cli.py                      # Typer app (architect init, architect generate)
    init/
      __init__.py
      scaffold.py               # Pure functions: create .opencode/ structure
      agents.py                 # Pure functions: generate agent markdown
      skills.py                 # Pure functions: generate skill markdown
      config.py                 # Pure functions: generate opencode.json
    generate/
      __init__.py
      das.py                    # Pure functions: spec -> DAS SQL
      dar.py                    # Pure functions: spec -> DAR SQL
      templates/                # Jinja2 templates for SQL generation
    models/
      __init__.py
      agent.py                  # Frozen dataclasses for agent definitions
      spec.py                   # Frozen dataclasses for warehouse specs
    templates/
      agents/                   # Agent persona templates (Markdown)
        data-architect.md.j2
        system-analyst.md.j2
        business-analyst.md.j2
        data-engineer.md.j2
        analytics-engineer.md.j2
        veteran-reviewer.md.j2
      skills/                   # Skill templates
        clp-debate.md.j2
        anchor-modeling.md.j2
      config/
        opencode.json.j2        # OpenCode config template
  tests/
    __init__.py
    test_cli.py
    test_init/
      test_scaffold.py
      test_agents.py
      test_skills.py
    test_generate/
      test_das.py
      test_dar.py
    test_models/
      test_agent.py
      test_spec.py
    conftest.py                 # Shared fixtures
```

## Version Compatibility Matrix

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| Python | >=3.13 | All listed packages | 3.13.12 is current stable (Feb 2026) |
| UV | >=0.10.0 | Hatchling, uv-dynamic-versioning | Pin in CI for reproducibility |
| Hatchling | >=1.28.0 | uv-dynamic-versioning >=0.13.0 | Build backend |
| uv-dynamic-versioning | >=0.13.0 | Hatchling >=1.28.0 | Requires git tags |
| Typer | >=0.21.0 | Click >=8.3.0 (auto-installed) | Typer depends on Click internally |
| Ruff | >=0.15.0 | Python >=3.13 target | 2026 style guide |
| Mypy | >=1.19.0 | Python 3.13 | strict mode recommended |
| pytest | >=9.0.0 | Python >=3.13 | Function-based tests only |
| Hypothesis | >=6.151.0 | pytest >=9.0.0 | Requires Python >=3.10 |
| pytest-cov | >=7.0.0 | coverage.py >=7.13 | Auto-installed |
| PyYAML | >=6.0 | Python >=3.13 | Stable API |
| Jinja2 | >=3.1 | Python >=3.13 | Stable API |
| rich | >=13.0 | Typer >=0.21.0 | Optional but recommended |

## Installation

```bash
# Development setup
uv sync --locked --all-extras --dev

# Or from PyPI (end user)
uv tool install warehouse-architect
# or
pip install warehouse-architect
```

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| OpenCode.ai agent format | HIGH | Verified from official docs (opencode.ai/docs/agents/, /config/, /skills/, /rules/). Format is Markdown + YAML frontmatter. Clear and stable. |
| UV + Hatchling + dynamic versioning | HIGH | Verified from official Astral docs and uv-dynamic-versioning PyPI page. Well-documented, actively maintained. |
| CLI framework (Typer) | HIGH | Mature (v0.21), function-based API, built on Click. Widely adopted. |
| Functional Python patterns | HIGH | stdlib frozen dataclasses are well-understood. No exotic deps needed. |
| Linting (Ruff) | HIGH | v0.15.0, Feb 2026 release. De facto standard. |
| Type checking (Mypy) | HIGH | v1.19.0, mature. ty (Astral) is promising but still beta. |
| Testing (pytest + Hypothesis) | HIGH | Both mature, actively maintained, well-documented. |
| CI/CD (GitHub Actions + UV) | HIGH | Official UV GitHub Actions guide with complete workflow examples. Trusted Publishing supported. |
| Dynamic versioning | HIGH | uv-dynamic-versioning v0.13.0, designed for this exact stack. |

## Open Questions

### ty (Astral Type Checker)

ty is 10-60x faster than Mypy and built by the Astral team (UV, Ruff). Currently in beta, stable release expected later 2026. **Recommendation:** Start with Mypy (proven, stable). Monitor ty's progress. Switch when ty reaches stable and achieves feature parity with Mypy strict mode. The switch will be trivial since both read the same type annotations.

### Ruff Functional Style Enforcement

No existing Ruff rule bans `class` definitions (only `@dataclass` is enforceable). **Recommendation:** Enforce via code review convention and project documentation. Consider writing a custom Ruff plugin if the team grows.

### OpenCode.ai Agent Versioning

OpenCode is evolving rapidly (v1.1.53, 697 releases). Agent format may change. **Recommendation:** Keep agent template generation decoupled from the CLI core. If OpenCode changes format, only the template layer needs updating.

## Sources

### Official Documentation (HIGH Confidence)
- [OpenCode.ai Agents Docs](https://opencode.ai/docs/agents/) -- Agent definition format, frontmatter fields, modes
- [OpenCode.ai Config Docs](https://opencode.ai/docs/config/) -- opencode.json schema, configuration merging
- [OpenCode.ai Skills Docs](https://opencode.ai/docs/skills/) -- Skill format, SKILL.md structure, permissions
- [OpenCode.ai Rules Docs](https://opencode.ai/docs/rules/) -- AGENTS.md rules format
- [UV Working on Projects](https://docs.astral.sh/uv/guides/projects/) -- pyproject.toml, uv sync, uv build
- [UV GitHub Actions Guide](https://docs.astral.sh/uv/guides/integration/github/) -- CI/CD workflows
- [UV Building and Publishing](https://docs.astral.sh/uv/guides/package/) -- uv build, uv publish, trusted publishing
- [Ruff v0.15.0 Release](https://astral.sh/blog/ruff-v0.15.0) -- 2026 style guide, current version
- [Astral ty Blog Post](https://astral.sh/blog/ty) -- ty beta status, performance benchmarks
- [Typer Documentation](https://typer.tiangolo.com/) -- CLI framework, function-based API
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) -- Property-based testing

### Package Registries (HIGH Confidence)
- [uv-dynamic-versioning on PyPI](https://pypi.org/project/uv-dynamic-versioning/) -- v0.13.0, Jan 2026
- [Ruff on PyPI](https://pypi.org/project/ruff/) -- v0.15.0, Feb 2026
- [Typer on PyPI](https://pypi.org/project/typer/) -- v0.21.1, Jan 2026
- [Mypy on PyPI](https://pypi.org/project/mypy/) -- v1.19.1, Dec 2025
- [pytest on PyPI](https://pypi.org/project/pytest/) -- v9.0.2, Feb 2026
- [Hypothesis on PyPI](https://pypi.org/project/hypothesis/) -- v6.151.5, Feb 2026
- [Hatchling on PyPI](https://pypi.org/project/hatchling/) -- v1.28.0, Jan 2026

### Ecosystem Research (MEDIUM Confidence)
- [Python Developer Tooling Handbook: Dynamic Versioning](https://pydevtools.com/handbook/how-to/how-to-add-dynamic-versioning-to-uv-projects/) -- uv-dynamic-versioning guide
- [Mypy vs Pyright Discussion](https://discuss.python.org/t/mypy-vs-pyright-in-practice/75984) -- Community comparison
- [Pyright Mypy Comparison](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md) -- Official Pyright comparison doc
- [OpenCode GitHub (sst/opencode)](https://github.com/sst/opencode) -- v1.1.53, 99.7k stars

---
*Stack research for: Warehouse Architect (Python CLI + OpenCode.ai agent scaffolding)*
*Researched: 2026-02-07*
*Confidence: HIGH (all core technologies verified from official sources)*
