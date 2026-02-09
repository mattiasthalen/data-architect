# Stack Research

**Domain:** Python CLI tool + OpenCode.ai agent scaffolding (data warehouse design)
**Researched:** 2026-02-07
**Updated:** 2026-02-09 (Added v0.3.0 DAB generation stack)
**Confidence:** HIGH (core stack verified from official docs; OpenCode agent format confirmed)

## Executive Summary

This stack supports a Python CLI tool (`architect`) that scaffolds OpenCode.ai agent definitions and generates deterministic data warehouse scripts. The project mandates pure functional Python (no classes), TDD, UV for package management, and dynamic versioning from git tags. Every technology choice below is driven by these constraints.

The stack is centered on the Astral ecosystem (UV + Ruff + ty) for tooling, Typer for the CLI, frozen dataclasses for immutable data, Hatchling + uv-dynamic-versioning for builds, and pytest + Hypothesis for testing. OpenCode.ai agent definitions are Markdown files with YAML frontmatter, placed in `.opencode/agents/`.

**v0.3.0 Addition (DAB Generation):** Extends stack with Pydantic for YAML schema validation, lxml for XML Schema validation, and Jinja2 macros for idempotent SQL generation. Supports DAB YAML spec format (superset of Anchor XML), XML import/export, and Bruin asset output.

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
| **PyYAML** | >=6.0.2 | YAML parsing/serialization | Reading/writing YAML specs produced by agent debate. Loading YAML frontmatter for agent definitions. Fast, lightweight, YAML 1.1 compliant. | HIGH |
| **Jinja2** | >=3.1.6 | Template engine for code generation | `architect generate` renders SQL DDL, dbt models from specs + templates. Jinja is the dbt standard. De facto standard for SQL templating. | HIGH |
| **rich** | >=13.0 | Terminal output formatting | Pretty-print CLI output (tables, progress, syntax highlighting). Typer recommends rich for enhanced output. | MEDIUM |

## v0.3.0: DAB Generation Stack Additions

**Milestone:** DAB YAML spec management, XML import/export, idempotent SQL generation, Bruin asset output.

**Confidence:** HIGH (all libraries verified from official docs and version checks)

### New Core Dependencies

| Library | Version | Purpose | Why Required | Confidence |
|---------|---------|---------|--------------|------------|
| **Pydantic** | >=2.12.5 | YAML schema validation, immutable data models | Industry standard for Python data validation with runtime type checking. Rust-accelerated core (fastest validation library). Mirrors anchor.xsd structure for DAB spec. `frozen=True` config integrates with existing frozen dataclass pattern. Cross-field validators for XSD assertions. | HIGH |
| **lxml** | >=6.0.1 | XML Schema (XSD) validation, XML parsing | Python binding to libxml2/libxslt (C libraries). Full XSD 1.1 support for validating against anchor.xsd. Fastest XML processing in Python. Required for XML import/export with schema validation. Python 3.8+ compatible. | HIGH |

### Optional Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| **ruamel.yaml** | >=0.18.10 | Comment-preserving YAML roundtrip | Use for `dab export` if preserving user comments in YAML is critical. YAML 1.2 compliant. 1.6x slower than PyYAML but handles edge cases better. Import as `from ruamel.yaml import YAML` to avoid conflicts. | MEDIUM |
| **xmlschema** | >=4.3.1 | Alternative XML validation | Use if lxml's XSD support insufficient (unlikely). Pure Python, easier debugging. Slower than lxml but more Pythonic API. Python 3.10+ required. | LOW |
| **types-PyYAML** | latest | Type stubs for mypy | Required for strict type checking. Ensures YAML operations pass mypy --strict. Development-only dependency. | HIGH |
| **types-lxml** | latest | Type stubs for mypy | Required for strict type checking on lxml operations. Development-only dependency. | HIGH |

### Updated pyproject.toml for v0.3.0

```toml
[project]
dependencies = [
    "typer>=0.15.0",
    "pydantic>=2.12.5",      # NEW: YAML schema validation
    "jinja2>=3.1.6",
    "lxml>=6.0.1",           # NEW: XML validation
    "pyyaml>=6.0.2",
]

[dependency-groups]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=7.0.0",
    "hypothesis>=6.151.0",
    "mypy>=1.19.0",
    "ruff>=0.15.0",
    "pre-commit>=4.5.1",
    "types-pyyaml>=6.0.12",  # NEW: Type stubs
    "types-lxml>=2024.11.8", # NEW: Type stubs
]
```

## DAB Feature Stack Patterns

### 1. YAML Spec Parsing & Validation

**Pattern:** Pydantic models mirror anchor.xsd structure for validation + immutability.

```python
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Self

class Anchor(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mnemonic: str
    descriptor: str
    identity: str
    attributes: tuple[Attribute, ...] = ()

class Tie(BaseModel):
    model_config = ConfigDict(frozen=True)

    roles: tuple[Role, ...]  # min 2
    time_range: str | None = None

    @model_validator(mode='after')
    def validate_roles(self) -> Self:
        anchor_roles = [r for r in self.roles if r.type_category == 'anchor']
        if len(anchor_roles) < 2:
            raise ValueError("Tie must reference at least 2 anchors")
        return self

class DABSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    knots: tuple[Knot, ...]
    anchors: tuple[Anchor, ...]
    nexuses: tuple[Nexus, ...]
    ties: tuple[Tie, ...]
```

**Why Pydantic over dataclasses:**
- Runtime validation of YAML against schema (critical for external input)
- Cross-field validators (`@model_validator`) for XSD assertions
- Better error messages for validation failures
- `frozen=True` config maintains immutability pattern

**Integration with existing code:**
- Use Pydantic BaseModel for DAB spec models (validation-heavy)
- Keep frozen dataclasses for internal results/actions (ScaffoldResult, etc.)

### 2. XML Import/Export

**Import pattern:** lxml validates against anchor.xsd, translates to Pydantic models, serializes to YAML.

```python
from lxml import etree
import yaml

def import_xml(xml_path: Path, xsd_path: Path) -> DABSpec:
    """Import Anchor XML → validated DABSpec."""
    # Validate against XSD
    schema = etree.XMLSchema(etree.parse(str(xsd_path)))
    tree = etree.parse(str(xml_path))
    schema.assertValid(tree)  # Raises if invalid

    # Parse to dict
    root = tree.getroot()
    spec_dict = xml_to_dict(root)

    # Validate with Pydantic
    return DABSpec(**spec_dict)

def export_xml(spec: DABSpec, xsd_path: Path) -> str:
    """Export DABSpec → validated Anchor XML."""
    # Build lxml tree from spec
    root = etree.Element("{http://anchormodeling.com/schema}schema")
    for knot in spec.knots:
        knot_elem = etree.SubElement(root, "knot")
        knot_elem.set("mnemonic", knot.mnemonic)
        knot_elem.set("descriptor", knot.descriptor)
        # ... populate attributes

    # Validate against XSD
    schema = etree.XMLSchema(etree.parse(str(xsd_path)))
    schema.assertValid(root)  # Ensure round-trip validity

    return etree.tostring(root, pretty_print=True, encoding="unicode")
```

**Why lxml:**
- Full XSD 1.1 validation support (anchor.xsd uses assertions)
- Fastest XML processing (C library bindings)
- Mature, battle-tested (15+ years)

### 3. SQL Generation with Jinja2

**Template organization:** Mirror Anchor's dialect structure, idempotency macros.

```
src/data_architect/templates/
├── _macros.sql.j2              # Idempotency helpers
├── postgresql/
│   ├── knot.sql.j2
│   ├── anchor.sql.j2
│   ├── nexus.sql.j2
│   ├── tie.sql.j2
│   └── attribute.sql.j2
├── snowflake/
│   └── ... (same structure)
└── sqlserver/
    └── ... (same structure)
```

**Idempotency macros (_macros.sql.j2):**

```jinja2
{% macro create_table_if_not_exists(schema, table) %}
CREATE TABLE IF NOT EXISTS {{ schema }}.{{ table }}
{% endmacro %}

{% macro add_column_if_missing(schema, table, column, datatype) %}
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = '{{ schema }}'
        AND table_name = '{{ table }}'
        AND column_name = '{{ column }}'
    ) THEN
        ALTER TABLE {{ schema }}.{{ table }} ADD COLUMN {{ column }} {{ datatype }};
    END IF;
END $$;
{% endmacro %}

{% macro create_or_replace_view(schema, view) %}
CREATE OR REPLACE VIEW {{ schema }}.{{ view }} AS
{% endmacro %}
```

**SQL generation function:**

```python
from jinja2 import Environment, FileSystemLoader
from enum import Enum

class SQLDialect(Enum):
    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"

def generate_sql(spec: DABSpec, dialect: SQLDialect) -> dict[str, str]:
    """Pure function: DABSpec → SQL files."""
    env = Environment(loader=FileSystemLoader(f"templates/{dialect.value}"))

    results = {}
    for anchor in spec.anchors:
        template = env.get_template("anchor.sql.j2")
        sql = template.render(anchor=anchor, schema="dbo")
        results[f"{anchor.mnemonic}_anchor.sql"] = sql

    for knot in spec.knots:
        template = env.get_template("knot.sql.j2")
        sql = template.render(knot=knot, schema="dbo")
        results[f"{knot.mnemonic}_knot.sql"] = sql

    return results
```

**Why NOT SQLAlchemy:**
- SQLAlchemy is for runtime SQL execution, not static DDL generation
- Abstracts away dialect-specific SQL we need full control over
- Anchor's proven approach: separate template directories per dialect
- Jinja2 is industry standard for SQL templating (dbt, Airflow, Bruin)

### 4. Bruin Asset Output

**Bruin asset structure:** YAML frontmatter in SQL comment block.

```sql
/* @bruin
name: schema.table
type: snowflake.sql
materialization:
  type: table
columns:
  - name: customer_id
    type: integer
    description: Primary key
    checks:
      - name: not_null
      - name: unique
custom_checks:
  - name: revenue_positive
    query: SELECT COUNT(*) FROM {{ ref("schema.table") }} WHERE revenue < 0
@bruin */

CREATE OR REPLACE TABLE schema.table AS
SELECT ...
```

**Template: bruin_asset.sql.j2:**

```jinja2
/* @bruin
name: {{ asset.name }}
type: {{ asset.type }}
materialization:
  type: {{ asset.materialization }}
{% if asset.columns %}
columns:
{% for col in asset.columns %}
  - name: {{ col.name }}
    type: {{ col.data_type }}
    description: {{ col.description }}
    checks:
{% for check in col.checks %}
      - name: {{ check.name }}
{% if check.value %}
        value: {{ check.value }}
{% endif %}
{% endfor %}
{% endfor %}
{% endif %}
{% if asset.custom_checks %}
custom_checks:
{% for check in asset.custom_checks %}
  - name: {{ check.name }}
    query: {{ check.query }}
{% endfor %}
{% endif %}
@bruin */

{{ sql_body }}
```

**Pydantic model for Bruin assets:**

```python
class BruinCheck(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    value: str | None = None

class BruinColumn(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    data_type: str
    description: str
    checks: tuple[BruinCheck, ...] = ()

class BruinAsset(BaseModel):
    model_config = ConfigDict(frozen=True)
    name: str
    type: str
    materialization: str
    columns: tuple[BruinColumn, ...] = ()
    custom_checks: tuple[dict[str, str], ...] = ()
```

### 5. Idempotent SQL Generation Best Practices

**Patterns from research:**

1. **Delete-write pattern for data operations:**
   - First delete existing data, then write new data
   - Only delete what will be recreated

2. **Schema validation before modifications:**
   - Check `information_schema` for table/column existence
   - Use transactions to ensure atomicity

3. **Use database-native idempotency:**
   - PostgreSQL: `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO NOTHING`
   - Snowflake: `CREATE OR REPLACE`
   - SQL Server: `IF NOT EXISTS (SELECT * FROM sys.objects WHERE ...)`

4. **Verify data integrity, not just keys:**
   - Don't assume presence of idempotency key guarantees data correctness
   - Include checksums or timestamps for change detection

**Implementation in templates:**

```jinja2
{# postgresql/anchor.sql.j2 #}
{% import '_macros.sql.j2' as macros %}

-- Create anchor table (idempotent)
{{ macros.create_table_if_not_exists('dbo', anchor.mnemonic) }} (
    {{ anchor.mnemonic }}_ID {{ anchor.identity }} PRIMARY KEY,
    Metadata_{{ anchor.mnemonic }} TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add attributes (idempotent)
{% for attr in anchor.attributes %}
{{ macros.add_column_if_missing('dbo', anchor.mnemonic, attr.mnemonic, attr.data_range) }}
{% endfor %}
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not | Confidence |
|----------|-------------|-------------|---------|------------|
| YAML Validation | **Pydantic** | dataclasses + cerberus | Cerberus lacks compile-time type safety. Pydantic faster (Rust core), more ergonomic, better type integration. | HIGH |
| YAML Validation | **Pydantic** | marshmallow | Marshmallow slower, more verbose. Pydantic v2 outperforms marshmallow in benchmarks (2-3x faster). | HIGH |
| XML Parsing | **lxml** | xml.etree.ElementTree | stdlib xml.etree lacks XSD validation. lxml required for anchor.xsd compliance. | HIGH |
| XML Parsing | **lxml** | xmlschema | xmlschema pure Python (slower), but lxml's C bindings provide better performance. Both work, lxml standard for production. | MEDIUM |
| SQL Generation | **Jinja2** | Mako | Mako more powerful but overkill. Jinja2 is dbt/Airflow/Bruin standard. Template compatibility critical. | HIGH |
| SQL Generation | **Jinja2** | SQLAlchemy Core | SQLAlchemy for runtime execution, not static DDL generation. Abstracts away dialect SQL we need control over. | HIGH |
| YAML Library | **PyYAML** (primary) | ruamel.yaml | PyYAML faster, simpler. Use ruamel.yaml only if comment preservation critical (export feature). | HIGH |
| Immutable Data | **Pydantic frozen models** | frozen dataclasses | Both work. Use Pydantic for DAB spec models (validation needed), dataclasses for internal data. | HIGH |
| CLI Framework | **Typer** | Click | Typer IS Click with type hints. Click requires more boilerplate. Typer's function-based API aligns with our functional Python mandate. | HIGH |
| CLI Framework | **Typer** | argparse | argparse is verbose, no auto-completion, no rich output. Typer generates all of this from type hints. | HIGH |
| Build Backend | **Hatchling** | setuptools | Hatchling is simpler config, better plugin system. UV recommends Hatchling. setuptools requires more boilerplate. | HIGH |
| Build Backend | **Hatchling** | flit | flit is too simple -- no plugin system for dynamic versioning. | HIGH |
| Dynamic Versioning | **uv-dynamic-versioning** | setuptools-scm | setuptools-scm requires setuptools backend. uv-dynamic-versioning is designed for Hatchling + UV stack. | HIGH |
| Dynamic Versioning | **uv-dynamic-versioning** | versioningit | versioningit works but smaller community. uv-dynamic-versioning is purpose-built for UV projects. | HIGH |
| Type Checker | **Mypy** (CI) | Pyright | Mypy is better for CI (stricter, more established). Pyright is better for IDE. Use both: Pyright via Pylance in VS Code, Mypy in CI. | HIGH |
| Type Checker | **Mypy** (CI) | ty (Astral) | ty is in beta (stable expected later 2026). 10-60x faster than Mypy. Monitor for graduation to stable, then switch. | MEDIUM |
| Linter | **Ruff** | flake8 + isort + black | Ruff replaces all three in one tool. 10-100x faster. Same team as UV. No reason to use separate tools in 2026. | HIGH |
| Template Engine | **Jinja2** | Mako | Jinja2 is the dbt standard. If generated SQL needs to work with dbt, it must be Jinja-compatible. | HIGH |
| Test Framework | **pytest** | unittest | pytest is function-based (no test classes). Better fixtures, parametrize, and plugin ecosystem. De facto standard. | HIGH |
| Package Manager | **UV** | Poetry | UV is 10-100x faster, has lockfile, replaces pyenv+pip+poetry. Astral ecosystem consistency with Ruff. Industry has converged on UV in 2026. | HIGH |
| Package Manager | **UV** | pip + venv | Manual, slow, no lockfile, no Python version management. UV does everything better. | HIGH |

## What NOT to Use

| Avoid | Why | Use Instead | Confidence |
|-------|-----|-------------|------------|
| **Classes with methods** | Project mandate: pure functional Python. Classes encourage mutable state and method-based behavior. | Frozen dataclasses for data, standalone functions for behavior. | HIGH |
| **SQLAlchemy for code generation** | Overkill. SQLAlchemy is for runtime SQL execution, not static DDL generation. Abstracts away dialect-specific SQL we need to control. Adds unnecessary complexity and dependencies. | Jinja2 templates per dialect with explicit SQL. Anchor's approach: separate template dirs (SQL/PostgreSQL/, SQL/SQLServer/). | HIGH |
| **xmltodict** | Discards XML schema information, no validation. Returns plain dicts losing type safety. Not suitable for schema-driven XML. | lxml with XSD validation via anchor.xsd. Preserves schema semantics. | HIGH |
| **JSON Schema for validation** | DAB spec is superset of Anchor XML which uses XSD. Translating XSD→JSON Schema loses semantics and validation rules. Pydantic supports JSON Schema but we need XSD-level assertions. | Pydantic models mirroring anchor.xsd structure. Use lxml to validate XML imports, Pydantic for YAML. | HIGH |
| **TemplateString (stdlib)** | Too primitive for SQL generation. No control structures (if/for), no filters, no macros. Would require building template engine from scratch. | Jinja2. Proven for complex SQL templating (dbt uses it for entire data warehouse generation). | HIGH |
| **attrs + cattrs** | attrs is fine but Pydantic standard for validation-heavy domains. cattrs for structure/unstructure, Pydantic does both + validation. | Pydantic for validation + serialization in single library. Maintains frozen pattern with `model_config = ConfigDict(frozen=True)`. | MEDIUM |
| **Poetry** | Superseded by UV in 2026. Slower, less features, less ecosystem support. | UV | HIGH |
| **Black + isort + flake8** | Three separate tools replaced by one (Ruff). More config, slower, more deps. | Ruff | HIGH |
| **Pylint** | Slow, opinionated in ways that conflict with functional style. | Ruff | HIGH |
| **pyrsistent / Expression / pfun** | External FP libraries add complexity for minimal gain. Frozen dataclasses cover our needs. | `dataclasses(frozen=True)` + stdlib | HIGH |
| **setuptools (as build backend)** | More config, less plugin support than Hatchling. UV recommends Hatchling. | Hatchling | HIGH |
| **tox** | UV replaces tox for running tests across environments. `uv run` handles venv management. | `uv run pytest` | MEDIUM |
| **pre-commit** | Adds complexity. CI catches everything. Developers can run `make check` locally. Consider adding later if team discipline is an issue. | `make check` locally, CI enforcement | MEDIUM |

## Enforcing Functional Style with Ruff

Ruff cannot directly ban `class` usage (no such rule exists). Enforcement strategy:

1. **Code review convention**: No classes except `@dataclass(frozen=True)` for data or Pydantic `BaseModel` with `frozen=True`.
2. **Ruff ANN rules**: Force type annotations on all functions -- makes function signatures explicit.
3. **Ruff FBT rules**: Ban boolean traps -- encourages explicit function parameters.
4. **Mypy strict mode**: Forces complete typing, which naturally discourages OOP patterns.
5. **Project convention in AGENTS.md / CONTRIBUTING.md**: Document the rule. Example:
   - YES: `@dataclass(frozen=True)` for data, Pydantic `BaseModel` with `frozen=True` for validation, standalone functions for logic
   - NO: Classes with methods, mutable state, inheritance (except Pydantic models)

## Project Directory Structure (Updated for v0.3.0)

```
data-architect/
  pyproject.toml
  uv.lock
  Makefile
  .python-version              # "3.13"
  .references/
    anchor/                    # Cloned Anchor repo
      anchor.xsd               # XML Schema for validation
      example.xml              # Reference XML
      SQL/                     # Sisula templates (inspiration)
  .github/
    workflows/
      ci.yml
      publish.yml
  src/data_architect/
    __init__.py                # __version__ via importlib.metadata
    cli.py                     # Typer app (architect init, architect dab ...)
    scaffold.py                # Pure functions: file creation
    templates.py               # Template content strings
    dab/                       # NEW: DAB generation module
      __init__.py
      models.py                # Pydantic models (DABSpec, Anchor, Knot, Tie, Nexus)
      parse.py                 # Pure functions: YAML → DABSpec
      xml_import.py            # Pure functions: XML → DABSpec
      xml_export.py            # Pure functions: DABSpec → XML
      generate.py              # Pure functions: DABSpec → SQL
      bruin.py                 # Pure functions: SQL → Bruin asset
    templates/                 # Jinja2 templates
      agents/                  # Agent persona templates
      sql/                     # NEW: SQL generation templates
        _macros.sql.j2
        postgresql/
          knot.sql.j2
          anchor.sql.j2
          nexus.sql.j2
          tie.sql.j2
          attribute.sql.j2
        snowflake/
          ... (same structure)
        sqlserver/
          ... (same structure)
        bruin_asset.sql.j2
  tests/
    __init__.py
    test_cli.py
    test_scaffold.py
    test_dab/                  # NEW: DAB tests
      test_models.py
      test_parse.py
      test_xml_import.py
      test_xml_export.py
      test_generate.py
      test_bruin.py
    conftest.py
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
| PyYAML | >=6.0.2 | Python >=3.6 | Stable API, YAML 1.1 |
| Jinja2 | >=3.1.6 | Python >=3.7 | Stable API, MarkupSafe bundled |
| **Pydantic** | **>=2.12.5** | **Python >=3.9** | **v2 API (breaking changes from v1). Rust-accelerated core.** |
| **lxml** | **>=6.0.1** | **Python >=3.8** | **C library bindings. Requires libxml2/libxslt system libraries.** |
| **ruamel.yaml** | **>=0.18.10** | **Python >=3.7** | **YAML 1.2. Import as `from ruamel.yaml import YAML` to avoid conflicts.** |
| **xmlschema** | **>=4.3.1** | **Python >=3.10** | **Pure Python alternative to lxml for XSD validation.** |
| rich | >=13.0 | Typer >=0.21.0 | Optional but recommended |

## Installation

```bash
# Development setup
uv sync --locked --all-extras --dev

# Or from PyPI (end user)
uv tool install data-architect
# or
pip install data-architect
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
| **Pydantic for YAML validation** | **HIGH** | **v2.12.5 verified from PyPI (Jan 2026). Rust-accelerated, fastest validation library. Standard for data validation.** |
| **lxml for XML validation** | **HIGH** | **v6.0.1 verified from PyPI (Aug 2025). Mature (15+ years), fastest XML processing, full XSD 1.1 support.** |
| **Jinja2 for SQL generation** | **HIGH** | **v3.1.6 verified from PyPI (Mar 2025). De facto standard for SQL templating (dbt, Airflow, Bruin).** |
| **Idempotent SQL patterns** | **MEDIUM** | **Best practices from multiple sources. Need to validate with real database testing across dialects.** |
| **Bruin asset format** | **HIGH** | **Verified from official Bruin docs. YAML frontmatter in SQL comments is stable format.** |

## Open Questions

### ty (Astral Type Checker)

ty is 10-60x faster than Mypy and built by the Astral team (UV, Ruff). Currently in beta, stable release expected later 2026. **Recommendation:** Start with Mypy (proven, stable). Monitor ty's progress. Switch when ty reaches stable and achieves feature parity with Mypy strict mode. The switch will be trivial since both read the same type annotations.

### Ruff Functional Style Enforcement

No existing Ruff rule bans `class` definitions (only `@dataclass` is enforceable). **Recommendation:** Enforce via code review convention and project documentation. Consider writing a custom Ruff plugin if the team grows.

### OpenCode.ai Agent Versioning

OpenCode is evolving rapidly (v1.1.53, 697 releases). Agent format may change. **Recommendation:** Keep agent template generation decoupled from the CLI core. If OpenCode changes format, only the template layer needs updating.

### Comment Preservation in YAML Export

PyYAML discards comments (YAML 1.1), ruamel.yaml preserves them (YAML 1.2). **Recommendation:** Start with PyYAML for speed. Add ruamel.yaml as optional dependency if users request comment preservation in `dab export`. Use feature flag to toggle.

## Sources

### Official Documentation (HIGH Confidence)

**v0.1.0-v0.2.0 (OpenCode):**
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

**v0.3.0 (DAB Generation):**
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) -- Model validation, frozen config, validators (v2.12.5)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) -- Template syntax, macros, filters (v3.1.6)
- [lxml Documentation](https://lxml.de/) -- XSD validation, parsing (v6.0.1)
- [lxml Validation Guide](https://lxml.de/validation.html) -- XMLSchema class, XSD validation
- [xmlschema Documentation](https://xmlschema.readthedocs.io/en/latest/usage.html) -- Alternative XML validation (v4.3.1)
- [Bruin Asset Definition Schema](https://bruin-data.github.io/bruin/assets/definition-schema.html) -- YAML frontmatter format
- [PyYAML vs ruamel.yaml Comparison](https://www.oreateai.com/blog/choosing-between-ruamelyaml-and-pyyaml-a-comprehensive-comparison/2ca85e856751622588a46a00a9a8e664) -- YAML library tradeoffs

### Package Registries (HIGH Confidence)

- [uv-dynamic-versioning on PyPI](https://pypi.org/project/uv-dynamic-versioning/) -- v0.13.0, Jan 2026
- [Ruff on PyPI](https://pypi.org/project/ruff/) -- v0.15.0, Feb 2026
- [Typer on PyPI](https://pypi.org/project/typer/) -- v0.21.1, Jan 2026
- [Mypy on PyPI](https://pypi.org/project/mypy/) -- v1.19.1, Dec 2025
- [pytest on PyPI](https://pypi.org/project/pytest/) -- v9.0.2, Feb 2026
- [Hypothesis on PyPI](https://pypi.org/project/hypothesis/) -- v6.151.5, Feb 2026
- [Hatchling on PyPI](https://pypi.org/project/hatchling/) -- v1.28.0, Jan 2026
- [Pydantic on PyPI](https://pypi.org/project/pydantic/) -- v2.12.5, Dec 2025
- [lxml on PyPI](https://pypi.org/project/lxml/) -- v6.0.1, Aug 2025
- [Jinja2 on PyPI](https://pypi.org/project/Jinja2/) -- v3.1.6, Mar 2025
- [PyYAML on PyPI](https://pypi.org/project/PyYAML/) -- v6.0.2, 2024
- [ruamel.yaml on PyPI](https://pypi.org/project/ruamel.yaml/) -- v0.18.10, 2024
- [xmlschema on PyPI](https://pypi.org/project/xmlschema/) -- v4.3.1, Jan 2026

### Ecosystem Research (MEDIUM Confidence)

- [Advanced SQL Templates with JinjaSql](https://medium.com/data-science/advanced-sql-templates-in-python-with-jinjasql-b996eadd761d) -- SQL generation patterns
- [GitHub: sripathikrishnan/jinjasql](https://github.com/sripathikrishnan/jinjasql) -- Template language for SQL
- [SQLAlchemy Dialects](https://docs.sqlalchemy.org/en/21/dialects/) -- Why NOT to use for code generation
- [Idempotent SQL DDL Best Practices](https://medium.com/full-stack-architecture/idempotent-sql-ddl-ca354a1eee62) -- SQL generation patterns
- [Start Data Engineering: Idempotent Pipelines](https://www.startdataengineering.com/post/why-how-idempotent-data-pipeline/) -- Delete-write pattern, validation
- [Statically Enforcing Frozen Dataclasses](https://rednafi.com/python/statically-enforcing-frozen-dataclasses/) -- Immutability patterns
- [Python Developer Tooling Handbook: Dynamic Versioning](https://pydevtools.com/handbook/how-to/how-to-add-dynamic-versioning-to-uv-projects/) -- uv-dynamic-versioning guide
- [Mypy vs Pyright Discussion](https://discuss.python.org/t/mypy-vs-pyright-in-practice/75984) -- Community comparison
- [Pyright Mypy Comparison](https://github.com/microsoft/pyright/blob/main/docs/mypy-comparison.md) -- Official Pyright comparison doc
- [OpenCode GitHub (sst/opencode)](https://github.com/sst/opencode) -- v1.1.53, 99.7k stars

### Primary Sources (HIGH Confidence)

- Anchor XSD (`.references/anchor/anchor.xsd`) -- Official XML schema structure, assertions, recent updates (2025-09-25)
- Anchor SQL templates (`.references/anchor/SQL/`) -- Sisula template patterns, directive structure
- Anchor Example XML (`.references/anchor/example.xml`) -- Reference implementation

---
*Stack research for: Data Architect (Python CLI + OpenCode.ai agent scaffolding + DAB generation)*
*Researched: 2026-02-07*
*Updated: 2026-02-09 (Added v0.3.0 DAB generation stack)*
*Confidence: HIGH (all core technologies verified from official sources)*
