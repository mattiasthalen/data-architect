# Architecture Research

**Domain:** Python CLI + OpenCode Agents for Data Warehouse Design
**Researched:** 2026-02-07
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
                         warehouse-architect
                         (pip-installable CLI)

┌─────────────────────────────────────────────────────────────────────────┐
│                        CLI LAYER (Click)                                │
│  ┌──────────────────┐              ┌──────────────────────────┐        │
│  │  architect init   │              │  architect generate       │        │
│  │  (scaffold agents │              │  (spec → DAS/DAR scripts) │        │
│  │   to .opencode/)  │              │  (deterministic, no AI)   │        │
│  └────────┬─────────┘              └────────────┬─────────────┘        │
├───────────┴────────────────────────────────────┴──────────────────────┤
│                    SCAFFOLDING LAYER                                    │
│  ┌────────────────────────────────────────────────────────────┐       │
│  │  Template Reader (importlib.resources)                      │       │
│  │  → reads bundled .md agent definitions from package         │       │
│  │  → copies to .opencode/agents/ in cwd                       │       │
│  └────────────────────────────────────────────────────────────┘       │
│                                                                         │
│                    GENERATION LAYER                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐        │
│  │  Spec Reader  │  │  DAS Gen     │  │  DAR Gen              │        │
│  │  (YAML/JSON   │  │  (source →   │  │  (DAB output →        │        │
│  │   → frozen     │  │   staging    │  │   star schema         │        │
│  │   dataclasses) │  │   scripts)   │  │   scripts)            │        │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘        │
│         │                  │                      │                     │
│  ┌──────┴──────────────────┴──────────────────────┴──────────┐        │
│  │  Template Engine (Jinja2)                                   │        │
│  │  → SQL DDL, dbt models, Mermaid diagrams                    │        │
│  │  → Deterministic: same spec → same output always            │        │
│  └─────────────────────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────────────────────┤
│                    DATA LAYER (Immutable)                               │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  frozen dataclasses: Spec, Anchor, Attribute, Tie, Knot     │       │
│  │  → parsed from YAML/JSON, validated with schema             │       │
│  │  → passed through pure function pipelines                   │       │
│  │  → never mutated, always replaced                           │       │
│  └─────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘

         ┌─────────────────────────────────────────────────────┐
         │  BUNDLED AGENT TEMPLATES (package data)              │
         │  warehouse_architect/_agents/                         │
         │    ├── data-architect.md     (entry point agent)      │
         │    ├── system-analyst.md     (source-system expert)   │
         │    ├── business-analyst.md   (domain expert)          │
         │    ├── data-engineer.md      (physical modeling)      │
         │    ├── analytics-engineer.md (consumption layer)      │
         │    └── veteran-reviewer.md   (grumpy critic)          │
         └─────────────────────────────────────────────────────┘

                    .opencode/agents/    (scaffolded into user project)
                    specs/               (YAML/JSON from agent debate)
                    generated/           (DAS + DAR output)
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **CLI Entry Point** | Parses `init` and `generate` commands, validates arguments, dispatches to handler functions | Click group with two commands; module-level functions, no classes |
| **Scaffolder** | Reads bundled agent template files, writes them to `.opencode/agents/` in cwd | Pure function: `scaffold_agents(target_dir: Path) -> list[Path]` using `importlib.resources` |
| **Spec Reader** | Parses YAML/JSON spec files into frozen dataclasses, validates schema | Pure function: `read_spec(path: Path) -> Spec` returning immutable data |
| **DAS Generator** | Transforms source schema specs into Data-According-to-System scripts | Pure function pipeline: `spec -> sql_fragments -> rendered_output` |
| **DAR Generator** | Transforms DAB output specs into Data-According-to-Requirements scripts | Pure function pipeline: `spec -> star_schema_fragments -> rendered_output` |
| **Template Engine** | Renders Jinja2 templates with spec data to produce SQL/dbt output | Pure function: `render_template(template_name: str, context: dict) -> str` |
| **Agent Templates** | OpenCode-format `.md` files with YAML frontmatter defining agent personas | Static files bundled in package, copied verbatim to target project |

## Recommended Project Structure

```
warehouse-architect/
├── pyproject.toml              # UV project config, hatchling build
├── Makefile                    # bootstrap, lint, type, test, check
├── uv.lock                    # lockfile (committed)
├── .python-version            # Python version pin
├── README.md
│
├── src/
│   └── warehouse_architect/
│       ├── __init__.py         # __version__ from importlib.metadata
│       │
│       ├── cli.py              # Click group: init + generate commands
│       │                       # Entry point: warehouse_architect.cli:main
│       │
│       ├── scaffold.py         # scaffold_agents() — reads templates, writes to target
│       │                       # Pure functions only
│       │
│       ├── spec.py             # Frozen dataclasses: Spec, Anchor, Attribute, Tie, Knot
│       │                       # read_spec(), validate_spec() — pure parsing + validation
│       │
│       ├── generate.py         # generate_das(), generate_dar() — orchestrates generation
│       │                       # Pure function pipelines
│       │
│       ├── das/                # DAS generation module
│       │   ├── __init__.py
│       │   └── transforms.py   # Source schema → staging layer transforms
│       │
│       ├── dar/                # DAR generation module
│       │   ├── __init__.py
│       │   └── transforms.py   # DAB output → star schema transforms
│       │
│       ├── templates/          # Jinja2 templates for code generation
│       │   ├── __init__.py     # Required for importlib.resources
│       │   ├── das/
│       │   │   ├── __init__.py
│       │   │   ├── staging.sql.j2
│       │   │   └── staging.dbt.sql.j2
│       │   └── dar/
│       │       ├── __init__.py
│       │       ├── bridge.sql.j2
│       │       ├── dimension.sql.j2
│       │       └── fact.sql.j2
│       │
│       └── _agents/            # Bundled OpenCode agent definitions
│           ├── __init__.py     # Required for importlib.resources
│           ├── data-architect.md
│           ├── system-analyst.md
│           ├── business-analyst.md
│           ├── data-engineer.md
│           ├── analytics-engineer.md
│           └── veteran-reviewer.md
│
└── tests/
    ├── conftest.py             # Shared fixtures: tmp_dir, sample specs, etc.
    ├── test_cli.py             # CLI integration tests (Click CliRunner)
    ├── test_scaffold.py        # Scaffold tests: files created, content correct
    ├── test_spec.py            # Spec parsing tests + property-based (Hypothesis)
    ├── test_generate.py        # Generation tests: deterministic output
    ├── test_das/
    │   └── test_transforms.py  # DAS transform unit tests
    ├── test_dar/
    │   └── test_transforms.py  # DAR transform unit tests
    └── snapshots/              # Syrupy snapshot files for generated SQL
```

### Structure Rationale

- **`src/` layout:** Prevents accidental imports of uninstalled package. Forces tests to run against installed package. This is the PyPA-recommended layout and UV's default for libraries. Catches packaging bugs early.

- **`_agents/` directory:** Underscore prefix signals "private/internal" to Python conventions. These are package data files, not importable modules. The `__init__.py` makes them discoverable by `importlib.resources.files()`.

- **`templates/` inside package:** Jinja2 templates co-located with Python code so `importlib.resources` can find them. Each sub-directory (`das/`, `dar/`) mirrors the generation concern it serves.

- **`spec.py` as single module:** All data types in one module because they form a single coherent schema. Frozen dataclasses are small; splitting them across files adds navigation cost without benefit.

- **`cli.py` as thin layer:** CLI module does argument parsing and error formatting only. All logic lives in `scaffold.py`, `generate.py`, and transform modules. This makes the logic testable without CLI invocation.

- **`tests/` mirrors `src/`:** Each source module has a corresponding test module. `snapshots/` directory holds Syrupy snapshot files for golden-file testing of generated SQL.

## Architectural Patterns

### Pattern 1: Pure Function Pipelines (Core Pattern)

**What:** All business logic implemented as pure functions that transform immutable data. No classes, no mutable state, no side effects in core logic. Side effects (file I/O, console output) are pushed to the edges (CLI layer, scaffold layer).

**When to use:** Everywhere in this project. The constraint is "pure functional Python, no classes."

**Trade-offs:**
- **Pros:** Every function is independently testable, composable, and predictable. Frozen dataclasses guarantee no mutation bugs. Property-based testing becomes natural.
- **Cons:** Python is not Haskell; some patterns feel awkward (e.g., passing config through function arguments instead of `self`). Deeply nested function composition can be hard to read.

**Example:**
```python
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Sequence

# Immutable data
@dataclass(frozen=True)
class Anchor:
    name: str
    identity: str
    business_key: str
    historized: bool = False

@dataclass(frozen=True)
class Spec:
    anchors: tuple[Anchor, ...]  # tuple, not list — immutable
    version: str

# Pure functions — no side effects, no mutation
def parse_anchor(raw: dict) -> Anchor:
    return Anchor(
        name=raw["name"],
        identity=raw["identity"],
        business_key=raw["business_key"],
        historized=raw.get("historized", False),
    )

def parse_spec(raw: dict) -> Spec:
    return Spec(
        anchors=tuple(parse_anchor(a) for a in raw["anchors"]),
        version=raw["version"],
    )

def validate_spec(spec: Spec) -> tuple[bool, Sequence[str]]:
    errors: list[str] = []
    for anchor in spec.anchors:
        if not anchor.name[0].isupper():
            errors.append(f"Anchor name '{anchor.name}' must be PascalCase")
    return (len(errors) == 0, tuple(errors))

# Pipeline composition
def read_and_validate(path: Path) -> tuple[Spec, Sequence[str]]:
    import yaml
    raw = yaml.safe_load(path.read_text())
    spec = parse_spec(raw)
    valid, errors = validate_spec(spec)
    return spec, errors
```

### Pattern 2: importlib.resources for Template Bundling

**What:** Agent definition files and Jinja2 templates are bundled inside the Python package using `importlib.resources`. This is the standard library mechanism for accessing non-Python files shipped with a package. No `pkg_resources` (deprecated), no `__file__` path hacking.

**When to use:** Accessing any bundled file (agent `.md` files, Jinja2 `.j2` templates).

**Trade-offs:**
- **Pros:** Works in zip-imported packages, editable installs, and standard installs. No path assumptions. Standard library, no extra dependencies.
- **Cons:** Requires `__init__.py` in data directories. Files accessed as `Traversable` objects, not raw paths (unless you use `as_file()` context manager).

**Example:**
```python
from importlib import resources
from pathlib import Path

def get_agent_templates() -> dict[str, str]:
    """Read all bundled agent .md files. Pure: returns data, no side effects."""
    agents_dir = resources.files("warehouse_architect._agents")
    result = {}
    for item in agents_dir.iterdir():
        if item.name.endswith(".md"):
            result[item.name] = item.read_text(encoding="utf-8")
    return result

def scaffold_agents(target_dir: Path) -> list[Path]:
    """Write agent templates to target directory. Side effect: file I/O."""
    agents_dir = target_dir / ".opencode" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    templates = get_agent_templates()
    written: list[Path] = []
    for filename, content in sorted(templates.items()):
        dest = agents_dir / filename
        dest.write_text(content, encoding="utf-8")
        written.append(dest)
    return written
```

### Pattern 3: Thin CLI Shell Over Pure Logic

**What:** The CLI layer (Click) handles only argument parsing, error formatting, and console output. All actual logic lives in pure function modules (`scaffold.py`, `generate.py`). The CLI module is a thin adapter between the terminal and the pure core.

**When to use:** All CLI commands. This pattern makes logic testable without invoking Click's test runner.

**Trade-offs:**
- **Pros:** Core logic testable with plain pytest (no CliRunner needed). CLI concerns (color, formatting, exit codes) isolated from business logic. Easy to add alternative interfaces later (API, library).
- **Cons:** Extra layer of indirection. Must pass all context as function arguments (no global state).

**Example:**
```python
# cli.py — thin shell
import click
from pathlib import Path
from warehouse_architect.scaffold import scaffold_agents
from warehouse_architect.generate import generate_all

@click.group()
def main():
    """Data warehouse architect — scaffold agents, generate scripts."""
    pass

@main.command()
@click.option("--target", default=".", help="Target directory for .opencode/ scaffold")
def init(target: str):
    """Scaffold OpenCode agent definitions into .opencode/agents/."""
    target_path = Path(target).resolve()
    written = scaffold_agents(target_path)
    click.echo(f"Scaffolded {len(written)} agent definitions to {target_path / '.opencode' / 'agents'}")
    for path in written:
        click.echo(f"  {path.name}")

@main.command()
@click.argument("spec_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="generated/", help="Output directory")
@click.option("--target", type=click.Choice(["das", "dar", "all"]), default="all")
def generate(spec_path: str, output: str, target: str):
    """Generate DAS/DAR scripts from YAML/JSON specs."""
    spec = Path(spec_path).resolve()
    out = Path(output).resolve()
    results = generate_all(spec, out, target)
    click.echo(f"Generated {len(results)} files to {out}")
```

### Pattern 4: Snapshot Testing for Deterministic Output

**What:** Since generators must be deterministic (same spec always produces same output), snapshot testing captures expected output and detects any drift. Syrupy (pytest plugin) stores snapshots as readable files that are committed to version control.

**When to use:** All generator output tests. Every Jinja2 template rendering gets a snapshot test.

**Trade-offs:**
- **Pros:** Catches unintended output changes immediately. Snapshots serve as documentation of expected output. Easy to update when intentional changes are made (`--snapshot-update`).
- **Cons:** Snapshot files must be reviewed in PRs. Can mask understanding if blindly updated.

**Example:**
```python
# test_generate.py
def test_anchor_ddl_generation(snapshot):
    spec = Spec(
        anchors=(
            Anchor(name="Customer", identity="CustomerID",
                   business_key="Email", historized=True),
        ),
        version="1.0.0",
    )
    result = generate_anchor_ddl(spec.anchors[0], dialect="snowflake")
    assert result == snapshot

# Snapshot file (auto-generated, committed to git):
# tests/snapshots/test_generate/test_anchor_ddl_generation.txt
# CREATE TABLE Customer_Anchor (
#     CustomerID BIGINT NOT NULL,
#     ...
# );
```

### Pattern 5: Spec as Contract Between Agents and Generators

**What:** YAML/JSON specification files are the boundary between the probabilistic world (OpenCode agents debating during DAB) and the deterministic world (Python generators producing DAS/DAR). Specs are validated against a schema on read. Generators never consume raw YAML — they receive typed, validated, frozen dataclasses.

**When to use:** Every interaction between agent output and generator input.

**Trade-offs:**
- **Pros:** Clear contract. Agents can evolve their debate process independently of generators. Schema validation catches malformed specs before generation. Type safety from frozen dataclasses.
- **Cons:** Schema must be kept in sync between agent expectations and generator consumption. Versioning needed if schema evolves.

**Data flow:**
```
Agents (in OpenCode)     →  YAML/JSON files  →  Python CLI
   debate, decide             (on disk)           read, validate, generate
   (probabilistic)            (contract)          (deterministic)
```

## Data Flow

### Init Flow (Scaffolding)

```
architect init [--target .]
    ↓
CLI parses args → target_dir: Path
    ↓
scaffold_agents(target_dir)
    ↓
importlib.resources.files("warehouse_architect._agents")
    ↓
iterate .md files → read content (pure)
    ↓
write to target_dir/.opencode/agents/ (side effect at edge)
    ↓
return list of written paths → CLI formats output
```

### Generate Flow (DAS/DAR Scripts)

```
architect generate specs/ --output generated/ --target all
    ↓
CLI parses args → spec_path, output_dir, target
    ↓
read_spec(spec_path)
    ↓
yaml.safe_load() → raw dict
    ↓
parse_spec(raw) → Spec (frozen dataclass)
    ↓
validate_spec(spec) → (valid, errors)
    ↓ (if valid)
┌─────────────────────┬──────────────────────────┐
│ generate_das(spec)   │ generate_dar(spec)        │
│   ↓                  │   ↓                       │
│ das_transforms(spec) │ dar_transforms(spec)      │
│   ↓                  │   ↓                       │
│ render_template(     │ render_template(           │
│   "das/*.sql.j2",    │   "dar/*.sql.j2",         │
│   context)           │   context)                 │
│   ↓                  │   ↓                       │
│ SQL/dbt strings      │ SQL/dbt strings            │
└──────────┬──────────┘└──────────────┬────────────┘
           ↓                          ↓
        write to output_dir/ (side effect at edge)
           ↓
        return list of generated paths → CLI formats output
```

### Key Data Flows

1. **Scaffold Flow:** Package data (bundled .md files) → `importlib.resources` reads → pure function extracts content → side-effect function writes to disk. One-way, no state.

2. **Spec Flow:** YAML/JSON on disk → `yaml.safe_load()` → `parse_spec()` pure function → frozen dataclass Spec → `validate_spec()` pure function → validated Spec ready for generation.

3. **Generation Flow:** Validated Spec (frozen) → transform functions (pure, produce intermediate dicts/tuples) → Jinja2 template rendering (deterministic) → string output → file write (side effect at edge).

4. **Agent Debate Flow (outside this tool):** User drives agents in OpenCode → agents debate through CLP stages → agents write YAML/JSON specs to disk → `architect generate` consumes specs. The Python CLI never participates in debate — it only consumes the output.

## How GSD Patterns Map to This Tool

The GSD (get-shit-done) framework uses a consistent pattern for agent definitions that directly parallels what `architect init` scaffolds:

### GSD Agent Pattern

GSD agents (`.claude/agents/*.md`) follow this structure:
1. **YAML frontmatter** with metadata: name, description, tools, color
2. **Role section** defining the agent's purpose and responsibilities
3. **Structured sections** for philosophy, process, output formats
4. **Downstream consumer documentation** explaining who uses the agent's output

### Mapping to warehouse-architect

| GSD Concept | warehouse-architect Equivalent |
|-------------|-------------------------------|
| `.claude/agents/*.md` | `.opencode/agents/*.md` (scaffolded by `architect init`) |
| YAML frontmatter (name, tools) | OpenCode YAML frontmatter (description, mode, model, tools, permissions) |
| Role section in markdown body | Agent system prompt in markdown body |
| GSD orchestrator spawns agents | User manually drives agents in OpenCode |
| `.planning/` directory for state | `specs/` directory for debate output (YAML/JSON) |
| Structured returns (YAML blocks) | Structured spec output (YAML/JSON files) |
| Agent reads project context | Agent reads source docs + business description from cwd |

### Key Structural Parallel

GSD separates concerns into:
- **Orchestrators** (slash commands) that coordinate workflow
- **Agents** (markdown definitions) that do specialized work
- **Artifacts** (planning files) that carry state between agents

warehouse-architect separates concerns into:
- **CLI commands** (`init`, `generate`) that coordinate workflow
- **Agent definitions** (markdown files) that do specialized debate work
- **Specs** (YAML/JSON files) that carry decisions from agents to generators

The pattern is the same: thin orchestration layer, specialized agents, file-based contracts between stages.

## Anti-Patterns

### Anti-Pattern 1: Classes for Everything

**What people do:** Create `Agent` class, `Generator` class, `SpecParser` class — OOP reflexes in a functional codebase.
**Why it's wrong:** Violates the project constraint (pure functional, no classes). Classes encourage mutable state, hidden dependencies through `self`, and make functions harder to compose and test in isolation.
**Do this instead:** Module-level pure functions. Frozen dataclasses for data. Pass everything through function arguments. Compose functions in pipelines.

### Anti-Pattern 2: Path Manipulation for Package Data

**What people do:** Use `__file__` to find package data: `Path(__file__).parent / "_agents" / "data-architect.md"`.
**Why it's wrong:** Breaks when package is installed as a zip (wheel), in editable mode with different layouts, or in some CI environments. `__file__` is not guaranteed to point to a real filesystem path.
**Do this instead:** Use `importlib.resources.files("warehouse_architect._agents")` which handles all installation modes correctly.

### Anti-Pattern 3: Mutable State in Transform Pipeline

**What people do:** Build up a result dict/list mutably as transforms run: `result["tables"].append(table)`.
**Why it's wrong:** Makes transforms order-dependent, harder to test in isolation, and vulnerable to accidental mutation bugs (e.g., one transform accidentally modifying shared state).
**Do this instead:** Each transform returns new data. Compose with tuple concatenation or `dataclasses.replace()`. Pipeline is: `input → transform1 → intermediate → transform2 → output`. Each step is independently testable.

### Anti-Pattern 4: Jinja2 Templates with Logic

**What people do:** Put complex Python logic inside Jinja2 templates: `{% for anchor in spec.anchors if anchor.historized and anchor.name != "Audit" %}`.
**Why it's wrong:** Logic in templates is untestable (no unit tests for template conditionals), hard to debug (Jinja2 error messages are opaque), and couples presentation to business rules.
**Do this instead:** Prepare a fully-resolved context dict in Python (pure function, testable), pass it to Jinja2 for simple iteration and substitution only. Templates should have no `if` beyond trivial formatting concerns.

### Anti-Pattern 5: Testing Through CLI Only

**What people do:** Write all tests using Click's CliRunner, testing end-to-end through the CLI interface.
**Why it's wrong:** Slow, brittle (tests break on formatting changes), and hides which specific function is broken. Also impossible to property-test CLI invocations.
**Do this instead:** Test pure functions directly with pytest. Use Hypothesis for property-based testing of spec parsing and validation. Reserve CliRunner tests for integration testing of the CLI layer itself (argument parsing, error messages, exit codes).

### Anti-Pattern 6: Agent Templates with Dynamic Content

**What people do:** Use Jinja2 or string interpolation to inject project-specific values into agent templates during scaffolding.
**Why it's wrong:** Agent definitions should be static — same content for every project. Dynamic content (project name, config) belongs in OpenCode's `opencode.json` configuration or the agent's runtime context, not baked into the markdown.
**Do this instead:** Scaffold agent `.md` files verbatim from package data. No templating during `init`. Agents read project-specific context at runtime from the filesystem.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **OpenCode** | File-based: `architect init` writes `.opencode/agents/*.md` | No API integration. Agents discovered by OpenCode at runtime from `.opencode/agents/` directory |
| **PyPI** | Standard: `pip install warehouse-architect` or `uv add warehouse-architect` | Published via UV build + twine/uv publish. Dynamic versioning from git tags |
| **Git** | Specs and generated code committed alongside project code | Specs are source of truth; generated code is reproducible artifact |
| **dbt** | Generated `.sql` files placed in dbt project structure | Generator output is valid dbt SQL with Jinja syntax |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **CLI ↔ Scaffold** | Function call: `scaffold_agents(target_dir: Path) -> list[Path]` | CLI handles UX (echo, exit codes); scaffold handles logic |
| **CLI ↔ Generate** | Function call: `generate_all(spec_path: Path, output: Path, target: str) -> list[Path]` | CLI handles UX; generate handles logic |
| **Spec Reader ↔ Generators** | Frozen dataclass: `Spec` passed as argument | Contract is the Spec type. Reader produces it, generators consume it |
| **Transforms ↔ Templates** | Dict/tuple context: transforms produce context, templates render it | Templates do no logic — all decisions made in transform functions |
| **Package ↔ Agent Files** | `importlib.resources`: package bundles agents, scaffold reads them | No runtime coupling — scaffold copies files, then agents run independently in OpenCode |

## Build Order Implications

### Phase 1: Project Foundation + Scaffolding

**Build first because:** Everything else depends on the package existing and being installable. Scaffolding is the simplest command (file copy) and proves the package structure works.

**Delivers:**
- `pyproject.toml` with UV build config, Click entry point, dynamic versioning
- `Makefile` with bootstrap, lint, type, test, check targets
- `src/warehouse_architect/` package skeleton
- `cli.py` with Click group + `init` command
- `scaffold.py` with `scaffold_agents()` pure function
- `_agents/` with at least one placeholder agent `.md` file
- Tests: CLI integration test, scaffold unit test
- CI: lint + type + test on PRs

**Why first:** You cannot build generators without a package to put them in. You cannot test anything without the test infrastructure. `init` is zero-dependency (no spec parsing, no templates) so it proves the build chain end-to-end.

### Phase 2: Spec System (Data Types + Validation)

**Build second because:** Generators consume specs. You must define and validate the spec format before you can generate from it.

**Delivers:**
- `spec.py` with frozen dataclasses (Spec, Anchor, Attribute, Tie, Knot)
- `read_spec()` and `validate_spec()` pure functions
- YAML/JSON parsing with schema validation
- Hypothesis property-based tests for spec parsing
- Syrupy snapshot tests for spec round-trip (parse → serialize → parse)

**Depends on:** Phase 1 (package structure exists)

### Phase 3: DAS Generation (Source → Staging)

**Build third because:** DAS is simpler than DAR (fewer transforms, more direct mapping from source schema to staging tables). Proves the generation pipeline before tackling the more complex DAR transforms.

**Delivers:**
- `das/transforms.py` — pure transform functions
- `templates/das/*.sql.j2` — Jinja2 templates for staging SQL
- `generate.py` — orchestration of spec → transform → render pipeline
- `generate` CLI command (DAS target)
- Snapshot tests for generated DAS SQL

**Depends on:** Phase 2 (Spec types defined and validated)

### Phase 4: DAR Generation (DAB → Star Schema)

**Build fourth because:** DAR transforms are more complex (Unified Star Schema, bridge tables, dimension/fact derivation). Requires the generation pipeline proven in Phase 3.

**Delivers:**
- `dar/transforms.py` — pure transform functions for USS pattern
- `templates/dar/*.sql.j2` — bridge, dimension, fact templates
- Extension of `generate` CLI command (DAR target)
- Snapshot tests for generated DAR SQL

**Depends on:** Phase 3 (generation pipeline proven with DAS)

### Phase 5: Agent Definitions + Demo Validation

**Build last because:** Agent definitions are static content (markdown files), not code. They require understanding of the full spec format (Phase 2) and generation capabilities (Phases 3-4) to write effective prompts. Demo validates the complete workflow.

**Delivers:**
- Complete agent `.md` files for all six roles (Data Architect, System Analyst, Business Analyst, Data Engineer, Analytics Engineer, Veteran Reviewer)
- Agent prompts reference actual spec format and generation capabilities
- E-commerce demo scenario exercising full workflow
- End-to-end integration test: scaffold → write spec → generate → validate

**Depends on:** Phases 1-4 (agents must reference real spec format and generation capabilities)

### Dependency Chain

```
Phase 1: Foundation + Scaffold
    ↓
Phase 2: Spec System
    ↓
Phase 3: DAS Generation ─────────┐
    ↓                             │
Phase 4: DAR Generation           │
    ↓                             │
Phase 5: Agent Definitions + Demo ┘
```

Phases 3 and 4 could potentially run in parallel since they share the spec system but produce independent output. However, building DAS first lets you prove the generation pipeline pattern before applying it to the more complex DAR case.

## Testing Architecture

### Test Strategy for Functional Python with TDD

| Test Type | Tool | What It Tests | When to Use |
|-----------|------|---------------|-------------|
| **Unit tests** | pytest | Individual pure functions (parse, validate, transform) | Every function gets unit tests first (TDD) |
| **Property-based** | Hypothesis | Spec parsing invariants (round-trip, validation rules) | Spec system — wide input space, many edge cases |
| **Snapshot tests** | Syrupy | Generated SQL/dbt output matches expected | All generator output — determinism guarantee |
| **Integration tests** | Click CliRunner | CLI argument parsing, error handling, exit codes | CLI layer only — thin coverage |
| **Fixture factories** | pytest fixtures + `conftest.py` | Reusable test data (sample specs, temp dirs) | Shared across test modules |

### TDD with Pure Functions

Pure functions make TDD natural:

1. **Write the test** — call the function with known input, assert expected output
2. **Run it (red)** — function does not exist yet
3. **Implement** — write the minimal function to pass
4. **Refactor** — compose, extract, clean up

No mocking needed for pure functions. No test database. No HTTP stubs. The function takes data in and returns data out. If a function needs I/O, push the I/O to the caller and test the pure core.

```python
# test_spec.py — TDD example
def test_parse_anchor_from_dict():
    raw = {"name": "Customer", "identity": "CustomerID",
           "business_key": "Email", "historized": True}
    result = parse_anchor(raw)
    assert result == Anchor(name="Customer", identity="CustomerID",
                           business_key="Email", historized=True)
    assert isinstance(result, Anchor)  # frozen dataclass

def test_parse_anchor_default_historized():
    raw = {"name": "Order", "identity": "OrderID", "business_key": "OrderNumber"}
    result = parse_anchor(raw)
    assert result.historized is False  # default
```

### Property-Based Testing with Hypothesis

For spec parsing, property-based testing catches edge cases that example-based tests miss:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_anchor_name_survives_roundtrip(name):
    """Any valid string used as anchor name should survive parse → serialize → parse."""
    raw = {"name": name, "identity": "ID", "business_key": "BK"}
    anchor = parse_anchor(raw)
    assert anchor.name == name

@given(st.booleans())
def test_historized_flag_preserved(historized):
    raw = {"name": "Test", "identity": "ID", "business_key": "BK",
           "historized": historized}
    assert parse_anchor(raw).historized == historized
```

## Sources

### Package Structure
- [Python Packaging User Guide: src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — PyPA official recommendation for src layout (HIGH confidence)
- [pyOpenSci Python Package Structure Guide](https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html) — Best practices for package organization (HIGH confidence)

### Agent Template Bundling
- [importlib.resources — Python 3 Official Docs](https://docs.python.org/3/library/importlib.resources.html) — Standard library API for package resource access (HIGH confidence)
- [Scientific Python: Including Data Files](https://learn.scientific-python.org/development/patterns/data-files/) — Pattern for bundling non-Python files with importlib.resources (HIGH confidence)
- [uv Build Backend](https://docs.astral.sh/uv/concepts/build-backend/) — UV's build backend for including package data (HIGH confidence)
- [uv Issue #11502: Non-source files in packages](https://github.com/astral-sh/uv/issues/11502) — Hatchling recommended for package data inclusion (MEDIUM confidence)

### OpenCode Agent Format
- [OpenCode Agents Documentation](https://opencode.ai/docs/agents/) — Official agent definition format (HIGH confidence)
- [OpenCode Skills Documentation](https://opencode.ai/docs/skills/) — Skills system and directory structure (HIGH confidence)
- [OpenCode Config Documentation](https://opencode.ai/docs/config/) — Configuration system and .opencode/ structure (HIGH confidence)
- [Claude Code to OpenCode Agent Conversion Guide](https://gist.github.com/RichardHightower/827c4b655f894a1dd2d14b15be6a33c0) — Field mapping and migration patterns (MEDIUM confidence)

### Functional Python Patterns
- [Python Functional Programming HOWTO — Official Docs](https://docs.python.org/3/howto/functional.html) — Core functional patterns in Python (HIGH confidence)
- [Writing Click CLIs Without Decorators](https://www.prout.tech/blog/functional_click/) — Functional approach to Click CLI construction (MEDIUM confidence)
- [Python dataclasses — Official Docs](https://docs.python.org/3/library/dataclasses.html) — Frozen dataclass documentation (HIGH confidence)

### Testing Architecture
- [Getting Started with Property-Based Testing (Hypothesis + Pytest)](https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest) — Hypothesis integration patterns (MEDIUM confidence)
- [Syrupy Snapshot Testing](https://til.simonwillison.net/pytest/syrupy) — Snapshot testing for deterministic output (MEDIUM confidence)
- [TDD with pytest — Real Python](https://realpython.com/courses/test-driven-development-pytest/) — TDD methodology with pytest (HIGH confidence)

### UV and Build System
- [UV: Creating Projects](https://docs.astral.sh/uv/concepts/projects/init/) — `uv init --lib` and src layout (HIGH confidence)
- [Dynamic Versioning for UV Projects](https://pydevtools.com/handbook/how-to/how-to-add-dynamic-versioning-to-uv-projects/) — Git tag versioning with hatchling + uv-dynamic-versioning (MEDIUM confidence)

### SQL/dbt Code Generation
- [JinjaSQL — SQL Template Language](https://github.com/sripathikrishnan/jinjasql) — Jinja2 for SQL generation patterns (MEDIUM confidence)
- [dbt Jinja and Macros](https://docs.getdbt.com/docs/build/jinja-macros) — dbt's use of Jinja for SQL templating (HIGH confidence)

---
*Architecture research for: Warehouse Architect (Python CLI + OpenCode Agents)*
*Researched: 2026-02-07*
*Replaces: previous architecture research (Claude Code skill, TypeScript stack — project pivoted to Python CLI + OpenCode agents)*
