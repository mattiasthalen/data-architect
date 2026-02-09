# Architecture: DAB Generation Integration

**Domain:** DAB YAML Spec Management + SQL Code Generation for Data Architect CLI
**Researched:** 2026-02-09
**Confidence:** HIGH

## Executive Summary

This document defines how DAB (Data According to Business) YAML spec management and SQL code generation integrate with the existing `architect` CLI. The existing tool (v0.2.0) scaffolds OpenCode agent definitions via `architect init`. The new feature adds `architect dab *` subcommands for managing Anchor Modeling specs and generating database-agnostic SQL.

**Key architectural decisions:**

1. **New module structure:** `src/data_architect/dab/` contains all DAB functionality (spec, generate, dialects)
2. **Frozen dataclasses for specs:** Immutable representations of anchors, attributes, ties, knots, nexuses matching anchor.xsd
3. **Typer subcommand groups:** `architect dab init|generate|import|export` using Typer's `add_typer()` for nested commands
4. **Jinja2 template system:** Dialect-specific SQL templates with pure Python transform functions preparing context
5. **Dialect abstraction:** Strategy pattern via pure functions, one module per dialect (postgresql, snowflake, sqlserver, oracle)
6. **Bruin asset output:** Optional format with YAML frontmatter + SQL body for data pipeline integration

**Integration points with existing architecture:**

- CLI layer extends with new `dab` subcommand group
- Scaffold pattern reused for `dab init` (spec skeleton generation)
- Template system extended for SQL generation (Jinja2, already used implicitly via embedded strings)
- Pure functional style maintained throughout (frozen dataclasses, stateless transforms)

## System Overview

```
                         data-architect
                    (pip-installable CLI, v0.3.0)

┌─────────────────────────────────────────────────────────────────────────┐
│                        CLI LAYER (Typer)                                │
│  ┌──────────────────┐              ┌─────────────────────────┐         │
│  │  architect init   │              │  architect dab          │         │
│  │  (scaffold agents)│              │  ├─ init   (spec stub)  │         │
│  │                   │              │  ├─ generate (SQL)      │         │
│  │  EXISTING         │              │  ├─ import  (XML→YAML)  │         │
│  │  (v0.1.0-v0.2.0)  │              │  └─ export  (YAML→XML)  │         │
│  └──────────────────┘              └─────────────────────────┘         │
├─────────────────────────────────────────────────────────────────────────┤
│                    EXISTING SCAFFOLD LAYER                              │
│  ┌────────────────────────────────────────────────────────────┐        │
│  │  Template Reader (templates.py)                             │        │
│  │  → embedded strings for agent definitions                   │        │
│  │  → scaffold.py: pure functions for file creation            │        │
│  └────────────────────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────────────────────┤
│                    NEW DAB LAYER                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐         │
│  │  Spec I/O     │  │  SQL Gen     │  │  Dialect Abstraction │         │
│  │              │  │              │  │                      │         │
│  │  spec.py     │  │  generate.py │  │  dialects/           │         │
│  │  ├─ parse    │  │  ├─ anchor   │  │  ├─ postgresql.py    │         │
│  │  ├─ validate │  │  ├─ knot     │  │  ├─ snowflake.py     │         │
│  │  ├─ import   │  │  ├─ tie      │  │  ├─ sqlserver.py     │         │
│  │  └─ export   │  │  └─ nexus    │  │  └─ oracle.py        │         │
│  │              │  │              │  │                      │         │
│  │  Frozen      │  │  Pure        │  │  Type mapping        │         │
│  │  dataclasses │  │  transforms  │  │  SQL dialect rules   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘         │
│         │                  │                      │                     │
│  ┌──────┴──────────────────┴──────────────────────┴──────────┐         │
│  │  Template Engine (Jinja2 templates in dab/templates/)      │         │
│  │  → anchor.sql.j2, knot.sql.j2, tie.sql.j2, nexus.sql.j2    │         │
│  │  → Deterministic: same spec + dialect → same SQL always    │         │
│  └─────────────────────────────────────────────────────────────┘         │
├─────────────────────────────────────────────────────────────────────────┤
│                    DATA LAYER (Immutable)                               │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  frozen dataclasses: Spec, Anchor, Attribute, Tie, Knot,    │       │
│  │  Nexus, Role, Key, Keyset, StagingMapping                   │       │
│  │  → parsed from YAML, validated against anchor.xsd rules     │       │
│  │  → passed through pure function pipelines                   │       │
│  │  → never mutated, always replaced via dataclasses.replace() │       │
│  └─────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘

         User workflow:
         1. architect init                    → scaffolds agents
         2. Agents debate → output YAML spec  → specs/dab.yaml
         3. architect dab generate specs/dab.yaml --dialect postgresql
            → generates SQL to generated/postgresql/
```

## Recommended Project Structure

```
data-architect/
├── src/
│   └── data_architect/
│       ├── __init__.py              # EXISTING: __version__ from metadata
│       ├── __main__.py              # EXISTING: entry point
│       ├── cli.py                   # MODIFIED: add dab subcommand group
│       │
│       ├── scaffold.py              # EXISTING: scaffold_agents()
│       ├── templates.py             # EXISTING: agent definition strings
│       │
│       ├── dab/                     # NEW: all DAB functionality
│       │   ├── __init__.py
│       │   │
│       │   ├── cli.py               # NEW: dab subcommand group (init, generate, import, export)
│       │   │
│       │   ├── spec.py              # NEW: frozen dataclasses for DAB spec
│       │   │                        #      Anchor, Attribute, Tie, Knot, Nexus, Role, Key
│       │   │                        #      parse_spec(), validate_spec()
│       │   │
│       │   ├── io.py                # NEW: spec I/O (read_yaml, write_yaml, import_xml, export_xml)
│       │   │
│       │   ├── generate.py          # NEW: orchestrates SQL generation
│       │   │                        #      generate_anchor(), generate_knot(), etc.
│       │   │
│       │   ├── keyset.py            # NEW: keyset identity parsing and validation
│       │   │                        #      parse_keyset("entity@system~tenant|key")
│       │   │
│       │   ├── dialects/            # NEW: dialect-specific implementations
│       │   │   ├── __init__.py      #      Dialect type, registry
│       │   │   ├── base.py          #      Base types, TypeMapping protocol
│       │   │   ├── postgresql.py    #      PostgreSQL type mapping + SQL rules
│       │   │   ├── snowflake.py     #      Snowflake type mapping + SQL rules
│       │   │   ├── sqlserver.py     #      SQL Server type mapping + SQL rules
│       │   │   └── oracle.py        #      Oracle type mapping + SQL rules
│       │   │
│       │   └── templates/           # NEW: Jinja2 SQL templates
│       │       ├── __init__.py      #      Required for importlib.resources
│       │       ├── anchor.sql.j2
│       │       ├── knot.sql.j2
│       │       ├── tie.sql.j2
│       │       ├── nexus.sql.j2
│       │       └── bruin.asset.j2   #      Bruin asset format wrapper
│       │
│       └── .references/             # EXISTING: external reference materials
│           └── anchor/              #      anchor.xsd, example.xml, Sisula SQL
│
├── tests/
│   ├── conftest.py                  # EXISTING: shared fixtures
│   ├── test_cli.py                  # EXISTING: init command tests
│   ├── test_scaffold.py             # EXISTING: scaffold tests
│   │
│   └── test_dab/                    # NEW: all DAB tests
│       ├── __init__.py
│       ├── conftest.py              #      DAB-specific fixtures (sample specs)
│       ├── test_spec.py             #      Spec parsing + validation + property tests
│       ├── test_io.py               #      YAML/XML I/O round-trip tests
│       ├── test_generate.py         #      SQL generation tests (snapshot tests)
│       ├── test_keyset.py           #      Keyset parsing tests
│       ├── test_dialects/           #      Dialect-specific tests
│       │   ├── test_postgresql.py
│       │   ├── test_snowflake.py
│       │   ├── test_sqlserver.py
│       │   └── test_oracle.py
│       └── snapshots/               #      Syrupy snapshot files for SQL output
│           ├── test_generate/
│           └── test_dialects/
│
└── pyproject.toml                   # MODIFIED: add pyyaml + jinja2 dependencies
```

## New Module Breakdown

### `dab/cli.py` — DAB Subcommand Group

**Purpose:** CLI interface for `architect dab init|generate|import|export`

**Pattern:** Typer subcommand group added to main app via `app.add_typer()`

**Implementation:**
```python
# dab/cli.py
import typer
from pathlib import Path
from data_architect.dab.spec import parse_spec, validate_spec
from data_architect.dab.generate import generate_sql
from data_architect.dab.io import read_yaml, write_yaml, import_xml, export_xml

app = typer.Typer(help="Manage DAB specs and generate SQL")

@app.command()
def init(
    output: Path = typer.Option(Path("specs/dab.yaml"), "--output", "-o"),
) -> None:
    """Create a skeleton DAB YAML spec."""
    # Pure logic in separate function, CLI just handles I/O and formatting
    ...

@app.command()
def generate(
    spec_path: Path = typer.Argument(..., help="Path to DAB YAML spec"),
    output_dir: Path = typer.Option(Path("generated"), "--output", "-o"),
    dialect: str = typer.Option("postgresql", "--dialect", "-d"),
    format: str = typer.Option("sql", "--format", "-f", help="sql or bruin"),
) -> None:
    """Generate SQL from DAB spec."""
    spec = read_yaml(spec_path)
    valid, errors = validate_spec(spec)
    if not valid:
        for error in errors:
            typer.secho(f"✗ {error}", fg=typer.colors.RED)
        raise typer.Exit(1)

    results = generate_sql(spec, output_dir, dialect, format)
    typer.secho(f"✓ Generated {len(results)} files", fg=typer.colors.GREEN)

@app.command()
def import_cmd(  # Can't name it "import" (Python keyword)
    xml_path: Path = typer.Argument(...),
    output: Path = typer.Option(Path("specs/dab.yaml"), "--output", "-o"),
) -> None:
    """Import Anchor XML to DAB YAML."""
    spec = import_xml(xml_path)
    write_yaml(spec, output)
    typer.secho(f"✓ Imported {xml_path} → {output}", fg=typer.colors.GREEN)

@app.command()
def export(
    spec_path: Path = typer.Argument(...),
    output: Path = typer.Option(Path("anchor.xml"), "--output", "-o"),
) -> None:
    """Export DAB YAML to Anchor XML."""
    spec = read_yaml(spec_path)
    export_xml(spec, output)
    typer.secho(f"✓ Exported {spec_path} → {output}", fg=typer.colors.GREEN)
```

**Integration with main CLI:**
```python
# cli.py (existing file, modified)
from data_architect.dab import cli as dab_cli

app = typer.Typer(
    help="Data Architect: Scaffold OpenCode AI agents for data warehouse design.",
)

# EXISTING: init command
@app.command()
def init(...):
    ...

# NEW: add dab subcommand group
app.add_typer(dab_cli.app, name="dab")
```

### `dab/spec.py` — Frozen Dataclasses for DAB Spec

**Purpose:** Immutable representations of Anchor Modeling constructs

**Pattern:** Frozen dataclasses matching anchor.xsd schema, tuples for collections

**Implementation:**
```python
# dab/spec.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Key:
    """Route-based key definition (anchor.xsd <key>)."""
    stop: str        # Position in route
    route: str       # Route name
    of: str          # Anchor/nexus mnemonic this key references
    branch: str = "1"  # Branch identifier

@dataclass(frozen=True)
class Identifier:
    """Route-based identifier (anchor.xsd <identifier>)."""
    route: str

@dataclass(frozen=True)
class Attribute:
    """Anchor/nexus attribute (anchor.xsd <attribute>)."""
    mnemonic: str              # e.g., "NAM"
    descriptor: str            # e.g., "Name"
    data_range: str | None = None     # Primitive type (e.g., "varchar(42)")
    knot_range: str | None = None     # Knot mnemonic (e.g., "GEN")
    time_range: str | None = None     # Temporalization type (e.g., "datetime")
    keys: tuple[Key, ...] = ()        # Route keys
    metadata: dict[str, str] = None   # equivalent, checksum flags

    def __post_init__(self) -> None:
        # Validate: exactly one of data_range or knot_range must be set
        if (self.data_range is None) == (self.knot_range is None):
            raise ValueError(f"Attribute {self.mnemonic}: exactly one of data_range or knot_range required")

@dataclass(frozen=True)
class Role:
    """Tie/nexus role (anchor.xsd <role>)."""
    role: str                  # Role name (e.g., "wasCast")
    type: str                  # Anchor/knot mnemonic
    identifier: bool = False   # True if part of tie identity
    keys: tuple[Key, ...] = ()
    coloring: str | None = None

@dataclass(frozen=True)
class Anchor:
    """Anchor entity (anchor.xsd <anchor>)."""
    mnemonic: str              # e.g., "AC" (Actor)
    descriptor: str            # e.g., "Actor"
    identity: str              # Surrogate key type (e.g., "int")
    attributes: tuple[Attribute, ...] = ()
    identifiers: tuple[Identifier, ...] = ()
    metadata: dict[str, str] | None = None

@dataclass(frozen=True)
class Knot:
    """Knot (anchor.xsd <knot>)."""
    mnemonic: str              # e.g., "GEN"
    descriptor: str            # e.g., "Gender"
    identity: str              # Knot ID type (e.g., "bit")
    data_range: str            # Value type (e.g., "varchar(42)")
    metadata: dict[str, str] | None = None

@dataclass(frozen=True)
class Tie:
    """Tie relationship (anchor.xsd <tie>)."""
    roles: tuple[Role, ...]    # Must have >= 2 roles
    time_range: str | None = None  # Temporalization
    metadata: dict[str, str] | None = None

    def __post_init__(self) -> None:
        # Validate: at least 2 roles
        if len(self.roles) < 2:
            raise ValueError("Tie must have at least 2 roles")

@dataclass(frozen=True)
class Nexus:
    """Nexus entity (anchor.xsd <nexus>)."""
    mnemonic: str              # e.g., "EV"
    descriptor: str            # e.g., "Event"
    identity: str              # Surrogate key type
    attributes: tuple[Attribute, ...] = ()
    roles: tuple[Role, ...] = ()
    identifiers: tuple[Identifier, ...] = ()
    metadata: dict[str, str] | None = None

    def __post_init__(self) -> None:
        # Validate: at least one non-knot role (anchor reference)
        # (requires access to schema to validate, deferred to validate_spec)
        pass

@dataclass(frozen=True)
class Keyset:
    """Keyset identity: entity@system~tenant|natural_key."""
    entity: str     # Anchor/nexus mnemonic
    system: str     # Source system identifier
    tenant: str | None = None  # Optional tenant
    natural_key: str | None = None  # Optional natural key

@dataclass(frozen=True)
class StagingMapping:
    """Mapping from staging table to anchor/nexus."""
    anchor_mnemonic: str       # Target anchor/nexus
    staging_table: str         # Source staging table
    system: str                # Source system
    tenant: str | None = None
    column_mappings: dict[str, str] = None  # attribute_mnemonic -> column_name

@dataclass(frozen=True)
class Spec:
    """Complete DAB specification (superset of anchor.xsd <schema>)."""
    version: str = "1.0"
    knots: tuple[Knot, ...] = ()
    anchors: tuple[Anchor, ...] = ()
    nexuses: tuple[Nexus, ...] = ()
    ties: tuple[Tie, ...] = ()
    staging_mappings: tuple[StagingMapping, ...] = ()  # Extension
    keysets: tuple[Keyset, ...] = ()  # Extension
    metadata: dict[str, str] | None = None

# Pure validation function
def validate_spec(spec: Spec) -> tuple[bool, Sequence[str]]:
    """Validate spec against anchor.xsd rules.

    Returns (valid, errors) where errors is list of validation messages.
    """
    errors: list[str] = []

    # Build mnemonic registries
    anchor_mnemonics = {a.mnemonic for a in spec.anchors}
    nexus_mnemonics = {n.mnemonic for n in spec.nexuses}
    knot_mnemonics = {k.mnemonic for k in spec.knots}

    # Validate mnemonic uniqueness
    all_mnemonics = list(anchor_mnemonics) + list(nexus_mnemonics) + list(knot_mnemonics)
    if len(all_mnemonics) != len(set(all_mnemonics)):
        errors.append("Duplicate mnemonics found across anchors, nexuses, knots")

    # Validate attribute knot references
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            if attr.knot_range and attr.knot_range not in knot_mnemonics:
                errors.append(f"Anchor {anchor.mnemonic} attribute {attr.mnemonic}: knot '{attr.knot_range}' not found")

    # Validate tie roles
    for i, tie in enumerate(spec.ties):
        anchor_role_count = sum(1 for r in tie.roles if r.type in anchor_mnemonics or r.type in nexus_mnemonics)
        if anchor_role_count < 2:
            errors.append(f"Tie {i}: must reference at least 2 anchors/nexuses")

    # Validate nexus roles
    for nexus in spec.nexuses:
        anchor_role_count = sum(1 for r in nexus.roles if r.type in anchor_mnemonics)
        if anchor_role_count < 1:
            errors.append(f"Nexus {nexus.mnemonic}: must have at least one non-knot role")

    # Validate key/@of references
    for anchor in spec.anchors:
        for attr in anchor.attributes:
            for key in attr.keys:
                if key.of not in anchor_mnemonics and key.of not in nexus_mnemonics:
                    errors.append(f"Anchor {anchor.mnemonic} attribute {attr.mnemonic} key: '@of={key.of}' not found")

    return (len(errors) == 0, tuple(errors))
```

### `dab/io.py` — YAML/XML I/O

**Purpose:** Read/write specs to YAML, import/export Anchor XML

**Pattern:** Pure functions, use PyYAML for YAML, xml.etree for XML

**Implementation:**
```python
# dab/io.py
from pathlib import Path
import yaml
from data_architect.dab.spec import Spec, Anchor, Attribute, Knot, Tie, Nexus

def read_yaml(path: Path) -> Spec:
    """Read DAB spec from YAML file."""
    raw = yaml.safe_load(path.read_text())
    return _parse_spec_dict(raw)

def write_yaml(spec: Spec, path: Path) -> None:
    """Write DAB spec to YAML file."""
    raw = _spec_to_dict(spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(raw, sort_keys=False))

def import_xml(path: Path) -> Spec:
    """Import Anchor XML to DAB spec (anchor.xsd → Spec)."""
    import xml.etree.ElementTree as ET
    tree = ET.parse(path)
    root = tree.getroot()
    # Parse XML to frozen dataclasses
    ...

def export_xml(spec: Spec, path: Path) -> None:
    """Export DAB spec to Anchor XML (Spec → anchor.xsd)."""
    import xml.etree.ElementTree as ET
    # Build XML tree from frozen dataclasses
    ...

# Helper: dict ↔ frozen dataclass conversion
def _parse_spec_dict(raw: dict) -> Spec:
    ...

def _spec_to_dict(spec: Spec) -> dict:
    ...
```

### `dab/generate.py` — SQL Generation Orchestration

**Purpose:** Orchestrate SQL generation for all spec elements

**Pattern:** Pure functions that prepare context dicts, then render Jinja2 templates

**Implementation:**
```python
# dab/generate.py
from pathlib import Path
from typing import Sequence
from jinja2 import Environment, PackageLoader
from data_architect.dab.spec import Spec, Anchor, Knot, Tie, Nexus
from data_architect.dab.dialects import get_dialect, Dialect

def generate_sql(
    spec: Spec,
    output_dir: Path,
    dialect_name: str,
    format: str = "sql"  # "sql" or "bruin"
) -> Sequence[Path]:
    """Generate SQL files for all spec elements.

    Returns list of generated file paths.
    """
    dialect = get_dialect(dialect_name)
    env = Environment(loader=PackageLoader("data_architect.dab", "templates"))

    results: list[Path] = []

    # Generate knots
    for knot in spec.knots:
        context = _prepare_knot_context(knot, dialect)
        sql = _render_template(env, "knot.sql.j2", context)
        if format == "bruin":
            sql = _wrap_bruin_asset(env, sql, f"knot_{knot.mnemonic}", spec.version)
        path = _write_file(output_dir, f"knot_{knot.mnemonic}.sql", sql)
        results.append(path)

    # Generate anchors
    for anchor in spec.anchors:
        context = _prepare_anchor_context(anchor, dialect, spec)
        sql = _render_template(env, "anchor.sql.j2", context)
        if format == "bruin":
            sql = _wrap_bruin_asset(env, sql, f"anchor_{anchor.mnemonic}", spec.version)
        path = _write_file(output_dir, f"anchor_{anchor.mnemonic}.sql", sql)
        results.append(path)

    # Generate ties
    for i, tie in enumerate(spec.ties):
        context = _prepare_tie_context(tie, dialect, spec, i)
        sql = _render_template(env, "tie.sql.j2", context)
        if format == "bruin":
            sql = _wrap_bruin_asset(env, sql, f"tie_{i}", spec.version)
        path = _write_file(output_dir, f"tie_{i}.sql", sql)
        results.append(path)

    # Generate nexuses
    for nexus in spec.nexuses:
        context = _prepare_nexus_context(nexus, dialect, spec)
        sql = _render_template(env, "nexus.sql.j2", context)
        if format == "bruin":
            sql = _wrap_bruin_asset(env, sql, f"nexus_{nexus.mnemonic}", spec.version)
        path = _write_file(output_dir, f"nexus_{nexus.mnemonic}.sql", sql)
        results.append(path)

    return tuple(results)

def _prepare_knot_context(knot: Knot, dialect: Dialect) -> dict:
    """Prepare context dict for knot template (pure function)."""
    return {
        "mnemonic": knot.mnemonic,
        "descriptor": knot.descriptor,
        "identity_type": dialect.map_type(knot.identity),
        "data_type": dialect.map_type(knot.data_range),
        "table_name": f"{knot.mnemonic}_{knot.descriptor}",
        "has_metadata": knot.metadata is not None,
        "equivalent": knot.metadata.get("equivalent") if knot.metadata else False,
    }

def _prepare_anchor_context(anchor: Anchor, dialect: Dialect, spec: Spec) -> dict:
    """Prepare context dict for anchor template (pure function)."""
    return {
        "mnemonic": anchor.mnemonic,
        "descriptor": anchor.descriptor,
        "identity_type": dialect.map_type(anchor.identity),
        "table_name": f"{anchor.mnemonic}_{anchor.descriptor}",
        "attributes": [
            {
                "mnemonic": attr.mnemonic,
                "descriptor": attr.descriptor,
                "type": dialect.map_type(attr.data_range or attr.knot_range),
                "is_knot": attr.knot_range is not None,
                "is_temporal": attr.time_range is not None,
                "time_type": dialect.map_type(attr.time_range) if attr.time_range else None,
            }
            for attr in anchor.attributes
        ],
        "identifiers": [{"route": ident.route} for ident in anchor.identifiers],
    }

def _prepare_tie_context(tie: Tie, dialect: Dialect, spec: Spec, index: int) -> dict:
    """Prepare context dict for tie template (pure function)."""
    return {
        "index": index,
        "is_temporal": tie.time_range is not None,
        "time_type": dialect.map_type(tie.time_range) if tie.time_range else None,
        "roles": [
            {
                "role": role.role,
                "type": role.type,
                "identifier": role.identifier,
                "is_knot": role.type in {k.mnemonic for k in spec.knots},
            }
            for role in tie.roles
        ],
    }

def _prepare_nexus_context(nexus: Nexus, dialect: Dialect, spec: Spec) -> dict:
    """Prepare context dict for nexus template (pure function)."""
    return {
        "mnemonic": nexus.mnemonic,
        "descriptor": nexus.descriptor,
        "identity_type": dialect.map_type(nexus.identity),
        "table_name": f"{nexus.mnemonic}_{nexus.descriptor}",
        "attributes": [
            {
                "mnemonic": attr.mnemonic,
                "descriptor": attr.descriptor,
                "type": dialect.map_type(attr.data_range or attr.knot_range),
            }
            for attr in nexus.attributes
        ],
        "roles": [
            {
                "role": role.role,
                "type": role.type,
            }
            for role in nexus.roles
        ],
    }

def _render_template(env: Environment, template_name: str, context: dict) -> str:
    """Render Jinja2 template with context (deterministic)."""
    template = env.get_template(template_name)
    return template.render(context)

def _wrap_bruin_asset(env: Environment, sql: str, name: str, version: str) -> str:
    """Wrap SQL in Bruin asset format."""
    template = env.get_template("bruin.asset.j2")
    return template.render(name=name, version=version, sql=sql)

def _write_file(output_dir: Path, filename: str, content: str) -> Path:
    """Write content to file (side effect at edge)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content)
    return path
```

### `dab/dialects/` — Dialect Abstraction

**Purpose:** Map Anchor Modeling types to database-specific SQL types

**Pattern:** Strategy pattern via pure functions, one module per dialect

**Implementation:**
```python
# dab/dialects/base.py
from typing import Protocol

class Dialect(Protocol):
    """Protocol for database dialect implementations."""

    name: str

    def map_type(self, anchor_type: str) -> str:
        """Map Anchor type to SQL type."""
        ...

    def create_table_prefix(self) -> str:
        """SQL prefix for CREATE TABLE (e.g., 'CREATE TABLE IF NOT EXISTS')."""
        ...

# dab/dialects/__init__.py
from data_architect.dab.dialects.base import Dialect
from data_architect.dab.dialects.postgresql import PostgreSQLDialect
from data_architect.dab.dialects.snowflake import SnowflakeDialect
from data_architect.dab.dialects.sqlserver import SQLServerDialect
from data_architect.dab.dialects.oracle import OracleDialect

_DIALECTS: dict[str, Dialect] = {
    "postgresql": PostgreSQLDialect(),
    "snowflake": SnowflakeDialect(),
    "sqlserver": SQLServerDialect(),
    "oracle": OracleDialect(),
}

def get_dialect(name: str) -> Dialect:
    """Get dialect by name (pure lookup)."""
    if name not in _DIALECTS:
        raise ValueError(f"Unknown dialect: {name}")
    return _DIALECTS[name]

# dab/dialects/postgresql.py
from data_architect.dab.dialects.base import Dialect

class PostgreSQLDialect:
    """PostgreSQL type mappings."""

    name = "postgresql"

    _TYPE_MAP = {
        # Anchor XML types → PostgreSQL types
        "int": "INTEGER",
        "bigint": "BIGINT",
        "tinyint": "SMALLINT",
        "bit": "BOOLEAN",
        "varchar(42)": "VARCHAR(42)",
        "varchar(max)": "TEXT",
        "datetime": "TIMESTAMP",
        "date": "DATE",
        "money": "NUMERIC(19,4)",
        "geography": "GEOGRAPHY",
    }

    def map_type(self, anchor_type: str | None) -> str:
        if anchor_type is None:
            return "TEXT"
        return self._TYPE_MAP.get(anchor_type, anchor_type.upper())

    def create_table_prefix(self) -> str:
        return "CREATE TABLE IF NOT EXISTS"

# dab/dialects/snowflake.py (similar structure)
# dab/dialects/sqlserver.py (similar structure)
# dab/dialects/oracle.py (similar structure)
```

### `dab/templates/` — Jinja2 SQL Templates

**Purpose:** SQL DDL templates for anchors, knots, ties, nexuses

**Pattern:** Simple Jinja2 templates with minimal logic (all decisions in Python)

**Implementation:**
```jinja2
{# dab/templates/anchor.sql.j2 #}
-- Anchor: {{ mnemonic }}_{{ descriptor }}
CREATE TABLE IF NOT EXISTS {{ table_name }} (
    {{ mnemonic }}_ID {{ identity_type }} PRIMARY KEY,
    Metadata_{{ mnemonic }} INT NOT NULL
);

{% for attr in attributes %}
-- Attribute: {{ attr.mnemonic }}_{{ attr.descriptor }}
CREATE TABLE IF NOT EXISTS {{ mnemonic }}_{{ attr.mnemonic }}_{{ attr.descriptor }} (
    {{ mnemonic }}_ID_{{ attr.mnemonic }} {{ identity_type }} NOT NULL,
    {% if attr.is_knot %}
    {{ attr.mnemonic }}_ID_{{ attr.descriptor }} {{ attr.type }} NOT NULL,
    {% else %}
    {{ mnemonic }}_{{ attr.mnemonic }}_{{ attr.descriptor }} {{ attr.type }} NOT NULL,
    {% endif %}
    {% if attr.is_temporal %}
    {{ mnemonic }}_{{ attr.mnemonic }}_ChangedAt {{ attr.time_type }} NOT NULL,
    {% endif %}
    Metadata_{{ mnemonic }}_{{ attr.mnemonic }} INT NOT NULL,
    FOREIGN KEY ({{ mnemonic }}_ID_{{ attr.mnemonic }}) REFERENCES {{ table_name }}({{ mnemonic }}_ID)
);
{% endfor %}
```

```jinja2
{# dab/templates/bruin.asset.j2 #}
name: {{ name }}
type: sql
owner: data-architect
tags:
  - dab
  - version:{{ version }}

/* START DATA PIPELINE ASSET: {{ name }} */

{{ sql }}

/* END DATA PIPELINE ASSET: {{ name }} */
```

### `dab/keyset.py` — Keyset Identity Parsing

**Purpose:** Parse and validate keyset identity format `entity@system~tenant|natural_key`

**Pattern:** Pure functions with regex parsing

**Implementation:**
```python
# dab/keyset.py
import re
from dataclasses import dataclass

KEYSET_PATTERN = re.compile(
    r"^(?P<entity>[A-Z]+)@(?P<system>[a-z0-9_-]+)(~(?P<tenant>[a-z0-9_-]+))?(\|(?P<natural_key>.+))?$"
)

def parse_keyset(keyset_str: str) -> Keyset:
    """Parse keyset identity string.

    Format: entity@system~tenant|natural_key
    Examples:
      - order@northwind~eu|10248
      - customer@erp|C001
      - product@shopify
    """
    match = KEYSET_PATTERN.match(keyset_str)
    if not match:
        raise ValueError(f"Invalid keyset format: {keyset_str}")

    return Keyset(
        entity=match.group("entity"),
        system=match.group("system"),
        tenant=match.group("tenant"),
        natural_key=match.group("natural_key"),
    )

def format_keyset(keyset: Keyset) -> str:
    """Format keyset to string (inverse of parse_keyset)."""
    parts = [f"{keyset.entity}@{keyset.system}"]
    if keyset.tenant:
        parts.append(f"~{keyset.tenant}")
    if keyset.natural_key:
        parts.append(f"|{keyset.natural_key}")
    return "".join(parts)
```

## Data Flow

### DAB Init Flow (Spec Skeleton)

```
architect dab init --output specs/dab.yaml
    ↓
dab/cli.py:init() → calls pure function create_skeleton_spec()
    ↓
create_skeleton_spec() → returns Spec with example anchor/knot
    ↓
write_yaml(spec, output_path) → side effect (file write)
    ↓
CLI formats success message → user has specs/dab.yaml skeleton
```

### DAB Generate Flow (YAML → SQL)

```
architect dab generate specs/dab.yaml --dialect postgresql --output generated/
    ↓
dab/cli.py:generate() → read_yaml(spec_path)
    ↓
read_yaml() → yaml.safe_load() → _parse_spec_dict() → Spec (frozen)
    ↓
validate_spec(spec) → (valid, errors)
    ↓ (if valid)
generate_sql(spec, output_dir, dialect, format)
    ↓
For each anchor/knot/tie/nexus:
    _prepare_*_context(element, dialect) → dict (pure transform)
    ↓
    _render_template(env, template_name, context) → SQL string (deterministic)
    ↓
    (optional) _wrap_bruin_asset(env, sql, name) → Bruin YAML + SQL
    ↓
    _write_file(output_dir, filename, content) → Path (side effect)
    ↓
return list of written paths → CLI formats output
```

### DAB Import Flow (XML → YAML)

```
architect dab import anchor.xml --output specs/dab.yaml
    ↓
dab/cli.py:import_cmd() → import_xml(xml_path)
    ↓
import_xml() → xml.etree.ElementTree.parse() → Spec (frozen dataclasses)
    ↓
write_yaml(spec, output_path) → side effect (file write)
    ↓
CLI formats success message
```

## Architectural Patterns

### Pattern 1: Frozen Dataclasses for Spec Representation

**What:** All Anchor Modeling constructs (Anchor, Attribute, Tie, Knot, Nexus) represented as frozen dataclasses with tuple collections. No mutation allowed.

**When to use:** All spec data structures. This is the core data model.

**Trade-offs:**
- **Pros:** Type-safe, immutable (no accidental mutation bugs), composable via dataclasses.replace(), property-testable, aligns with existing pure-functional style.
- **Cons:** Verbose updates require dataclasses.replace() or reconstructing tuples. Less ergonomic than mutable objects in Python.

**Example:**
```python
@dataclass(frozen=True)
class Anchor:
    mnemonic: str
    descriptor: str
    identity: str
    attributes: tuple[Attribute, ...] = ()  # Tuple, not list

# Functional update (no mutation)
def add_attribute(anchor: Anchor, attr: Attribute) -> Anchor:
    return dataclasses.replace(
        anchor,
        attributes=anchor.attributes + (attr,)
    )
```

### Pattern 2: Dialect Abstraction via Strategy Pattern

**What:** Each database dialect (PostgreSQL, Snowflake, SQL Server, Oracle) implemented as a pure function module with a shared `Dialect` protocol. Type mapping and SQL rules encapsulated per dialect.

**When to use:** All SQL generation. Dialect selected at runtime via `get_dialect(name)`.

**Trade-offs:**
- **Pros:** Easy to add new dialects (new module + register in `_DIALECTS`). Testable in isolation. No inheritance or complex OOP.
- **Cons:** Duplicate logic across dialects (e.g., all have CREATE TABLE structure). Could extract common patterns later if needed.

**Example:**
```python
# Pure function approach (no classes with methods)
def map_type_postgresql(anchor_type: str) -> str:
    return {"int": "INTEGER", "varchar(42)": "VARCHAR(42)"}.get(anchor_type, anchor_type)

def map_type_snowflake(anchor_type: str) -> str:
    return {"int": "NUMBER", "varchar(42)": "VARCHAR(42)"}.get(anchor_type, anchor_type)

# Protocol for type checking
class Dialect(Protocol):
    def map_type(self, anchor_type: str) -> str: ...
```

### Pattern 3: Context Preparation + Jinja2 Rendering

**What:** SQL generation separated into two phases: (1) pure Python functions prepare a context dict with all decisions made, (2) Jinja2 templates do simple iteration and substitution only. Templates have no business logic.

**When to use:** All template rendering (SQL, Bruin assets).

**Trade-offs:**
- **Pros:** Context preparation is pure and testable. Templates are simple and readable. Clear separation of concerns.
- **Cons:** Extra layer of indirection. Context dict schema is implicit (no type checking between Python and Jinja2).

**Example:**
```python
# Pure context preparation (all logic here)
def prepare_anchor_context(anchor: Anchor, dialect: Dialect) -> dict:
    return {
        "table_name": f"{anchor.mnemonic}_{anchor.descriptor}",
        "identity_type": dialect.map_type(anchor.identity),
        "attributes": [
            {
                "name": attr.mnemonic,
                "type": dialect.map_type(attr.data_range),
                "is_temporal": attr.time_range is not None,
            }
            for attr in anchor.attributes
        ],
    }

# Simple Jinja2 template (no logic, just iteration)
"""
CREATE TABLE {{ table_name }} (
    {{ mnemonic }}_ID {{ identity_type }} PRIMARY KEY
);
{% for attr in attributes %}
-- {{ attr.name }}
{% endfor %}
"""
```

### Pattern 4: Typer Subcommand Groups via `add_typer()`

**What:** DAB commands organized as a separate Typer app, then added to main app via `app.add_typer(dab_cli.app, name="dab")`. This creates `architect dab init`, `architect dab generate`, etc.

**When to use:** Grouping related commands. Future expansions (e.g., `architect schema *` for schema management) can use the same pattern.

**Trade-offs:**
- **Pros:** Clean command organization. Each subcommand group is an independent module. Easy to discover commands (`architect dab --help`).
- **Cons:** Extra file per command group. Slightly more complex than flat command structure.

**Example:**
```python
# dab/cli.py
app = typer.Typer(help="Manage DAB specs and generate SQL")

@app.command()
def init(...): ...

@app.command()
def generate(...): ...

# cli.py (main app)
from data_architect.dab import cli as dab_cli

app = typer.Typer()
app.add_typer(dab_cli.app, name="dab")  # Creates "architect dab" group
```

### Pattern 5: Snapshot Testing for Deterministic SQL Output

**What:** Use Syrupy snapshot tests to capture expected SQL output. Same spec + dialect → same SQL always. Snapshots committed to git and reviewed in PRs.

**When to use:** All SQL generation tests. Every template has snapshot tests for each dialect.

**Trade-offs:**
- **Pros:** Catches regressions immediately. Readable snapshots (plain SQL files). Easy to update when intentional changes made.
- **Cons:** Snapshot churn if SQL format changes frequently. Must review snapshot diffs carefully in PRs.

**Example:**
```python
def test_anchor_sql_postgresql(snapshot):
    spec = Spec(anchors=(
        Anchor(mnemonic="AC", descriptor="Actor", identity="int"),
    ))
    sql = generate_anchor_sql(spec.anchors[0], "postgresql")
    assert sql == snapshot  # Snapshot saved to tests/dab/snapshots/
```

## Integration Points with Existing Architecture

### CLI Layer Integration

| Integration Point | Change Required | Notes |
|-------------------|-----------------|-------|
| `cli.py` main app | Add `app.add_typer(dab_cli.app, name="dab")` | One line change, imports `dab.cli` |
| Entry point | No change | Still `architect = "data_architect.cli:app"` |
| Error handling | Reuse existing pattern | Typer's `Exit(1)` + colored output |

### Scaffold Pattern Reuse

| Pattern | Existing (`init`) | New (`dab init`) |
|---------|-------------------|------------------|
| Pure function core | `scaffold()` in `scaffold.py` | `create_skeleton_spec()` in `dab/spec.py` |
| Side effects at edge | `path.write_text()` in `scaffold()` | `write_yaml()` in `dab/io.py` |
| CLI wrapper | `init()` in `cli.py` | `init()` in `dab/cli.py` |

### Data Layer Consistency

| Existing Pattern | DAB Implementation |
|------------------|-------------------|
| `@dataclass(frozen=True)` for `ScaffoldResult` | `@dataclass(frozen=True)` for `Spec`, `Anchor`, etc. |
| `tuple` collections in return types | `tuple` collections in spec (`attributes: tuple[Attribute, ...]`) |
| Pure functions returning data | All spec parsing, validation, context preparation pure |

### Template System Extension

| Aspect | Existing | New (DAB) |
|--------|----------|-----------|
| Template storage | Embedded strings in `templates.py` | Jinja2 files in `dab/templates/` |
| Template loading | Direct access via dict | `importlib.resources` + Jinja2 `PackageLoader` |
| Rendering | String concatenation | Jinja2 `template.render(context)` |
| Why different? | Agent templates are static markdown | SQL templates need dialect-specific substitution |

## Build Order Recommendations

### Phase 1: Core Spec System (Build First)

**Delivers:**
- `dab/spec.py` with all frozen dataclasses
- `dab/io.py` with YAML read/write (XML import/export deferred)
- `dab/keyset.py` with keyset parsing
- `validate_spec()` function with anchor.xsd rules
- Tests: `test_dab/test_spec.py` (unit + property tests)
- Tests: `test_dab/test_io.py` (YAML round-trip tests)
- Tests: `test_dab/test_keyset.py` (keyset parsing tests)

**Why first:** All downstream features depend on the spec data model. Must be correct before building SQL generation. Property-based testing with Hypothesis catches edge cases early.

**Dependencies:** None (pure Python, stdlib + PyYAML)

### Phase 2: CLI Integration + DAB Init (Build Second)

**Delivers:**
- `dab/cli.py` with Typer subcommand group
- `cli.py` modified to add `app.add_typer(dab_cli.app, name="dab")`
- `architect dab init` command (creates skeleton YAML spec)
- Tests: `test_dab/test_cli.py` (CLI integration tests with CliRunner)

**Why second:** Proves CLI integration works before building complex SQL generation. Gives users a way to create spec skeletons immediately.

**Dependencies:** Phase 1 (spec system)

### Phase 3: Dialect Abstraction + PostgreSQL (Build Third)

**Delivers:**
- `dab/dialects/base.py` with `Dialect` protocol
- `dab/dialects/__init__.py` with dialect registry
- `dab/dialects/postgresql.py` with type mappings
- Tests: `test_dab/test_dialects/test_postgresql.py`

**Why third:** Simplest dialect (PostgreSQL) proves the abstraction pattern. Other dialects follow the same structure.

**Dependencies:** Phase 1 (spec system for type references)

### Phase 4: SQL Generation + Templates (Build Fourth)

**Delivers:**
- `dab/generate.py` with context preparation + rendering
- `dab/templates/anchor.sql.j2` (and knot, tie, nexus)
- `architect dab generate` command (PostgreSQL only initially)
- Tests: `test_dab/test_generate.py` with snapshot tests
- pyproject.toml: add `jinja2>=3.1` dependency

**Why fourth:** Depends on both spec system (Phase 1) and dialect abstraction (Phase 3). PostgreSQL templates prove the generation pipeline before adding more dialects.

**Dependencies:** Phases 1 (spec), 3 (dialects)

### Phase 5: Additional Dialects (Build Fifth)

**Delivers:**
- `dab/dialects/snowflake.py`
- `dab/dialects/sqlserver.py`
- `dab/dialects/oracle.py`
- Tests for each dialect
- Snapshot tests for each dialect

**Why fifth:** Straightforward extensions following the PostgreSQL pattern. Can be done in parallel if needed.

**Dependencies:** Phases 3 (dialect abstraction), 4 (SQL generation)

### Phase 6: Bruin Asset Format + XML I/O (Build Last)

**Delivers:**
- `dab/templates/bruin.asset.j2`
- `architect dab generate --format bruin`
- `architect dab import` (XML → YAML)
- `architect dab export` (YAML → XML)
- Tests for Bruin format and XML I/O

**Why last:** Optional features. Core functionality (YAML specs + SQL generation) works without these. Bruin format is a wrapper. XML I/O is for interop with legacy Anchor Modeling tools.

**Dependencies:** Phase 4 (SQL generation for Bruin), Phase 1 (spec system for XML)

### Dependency Graph

```
Phase 1: Spec System (spec.py, io.py, keyset.py)
    ↓
Phase 2: CLI Integration (dab/cli.py, cli.py modified, dab init)
    ↓
Phase 3: Dialect Abstraction (dialects/base.py, postgresql.py)
    ↓
Phase 4: SQL Generation (generate.py, templates/*.j2, dab generate)
    ↓
Phase 5: Additional Dialects (snowflake, sqlserver, oracle)
    ↓
Phase 6: Bruin + XML (bruin.asset.j2, import/export)
```

**Parallelization opportunity:** Phase 5 dialects can be built in parallel (independent of each other). Phase 6 Bruin format and XML I/O can also be built in parallel (independent of each other).

## Modified File Checklist

### Files Modified (Existing Codebase)

- `cli.py` — Add `app.add_typer(dab_cli.app, name="dab")` (1 line + import)
- `pyproject.toml` — Add `pyyaml>=6.0` and `jinja2>=3.1` to dependencies

### Files Created (New DAB Functionality)

**Modules (14 files):**
- `dab/__init__.py`
- `dab/cli.py`
- `dab/spec.py`
- `dab/io.py`
- `dab/keyset.py`
- `dab/generate.py`
- `dab/dialects/__init__.py`
- `dab/dialects/base.py`
- `dab/dialects/postgresql.py`
- `dab/dialects/snowflake.py`
- `dab/dialects/sqlserver.py`
- `dab/dialects/oracle.py`
- `dab/templates/__init__.py`

**Templates (5 files):**
- `dab/templates/anchor.sql.j2`
- `dab/templates/knot.sql.j2`
- `dab/templates/tie.sql.j2`
- `dab/templates/nexus.sql.j2`
- `dab/templates/bruin.asset.j2`

**Tests (10+ files):**
- `test_dab/__init__.py`
- `test_dab/conftest.py`
- `test_dab/test_spec.py`
- `test_dab/test_io.py`
- `test_dab/test_keyset.py`
- `test_dab/test_cli.py`
- `test_dab/test_generate.py`
- `test_dab/test_dialects/__init__.py`
- `test_dab/test_dialects/test_postgresql.py`
- `test_dab/test_dialects/test_snowflake.py`
- `test_dab/test_dialects/test_sqlserver.py`
- `test_dab/test_dialects/test_oracle.py`
- `test_dab/snapshots/` (directory for Syrupy snapshots)

**Total new files:** ~30 (14 modules + 5 templates + 10+ tests + snapshot directories)

## Anti-Patterns to Avoid

### Anti-Pattern 1: OOP-Style Spec Classes with Methods

**What people do:** Create classes with methods like `anchor.add_attribute(attr)`, `spec.validate()`.

**Why it's wrong:** Violates pure-functional constraint. Encourages mutable state (modifying objects in-place). Harder to test and compose.

**Do this instead:** Frozen dataclasses for data, standalone pure functions for behavior. `add_attribute(anchor, attr) -> Anchor` returns new anchor. `validate_spec(spec) -> (bool, errors)` is a pure function.

### Anti-Pattern 2: Logic in Jinja2 Templates

**What people do:** Put conditionals and business rules in templates: `{% if anchor.historized and anchor.name != "Audit" %}`.

**Why it's wrong:** Untestable logic in templates. Jinja2 error messages are opaque. Couples presentation to business rules.

**Do this instead:** All decisions in Python context preparation functions (testable, type-checked). Templates do simple iteration and substitution only.

### Anti-Pattern 3: Mutable Spec Construction

**What people do:** Build specs incrementally with mutation: `spec.anchors.append(anchor)`.

**Why it's wrong:** Breaks immutability. Makes specs order-dependent. Harder to reason about data flow.

**Do this instead:** Construct specs as complete frozen dataclasses. If building incrementally, accumulate in lists, then convert to tuple at the end: `Spec(anchors=tuple(anchor_list))`.

### Anti-Pattern 4: Dialect as Class Inheritance Hierarchy

**What people do:** `class PostgreSQLDialect(BaseDialect):` with inheritance and method overrides.

**Why it's wrong:** OOP in a functional codebase. Inheritance adds cognitive load. Hard to test in isolation.

**Do this instead:** Protocol for type checking, pure function modules for implementation. Each dialect is a standalone module with a `map_type()` function.

### Anti-Pattern 5: XML Parsing with String Manipulation

**What people do:** Parse Anchor XML with regex or string splitting.

**Why it's wrong:** Fragile. Breaks on valid XML (attributes, namespaces, CDATA). Error-prone for nested structures.

**Do this instead:** Use `xml.etree.ElementTree` (stdlib) for XML parsing. Tree traversal is simpler and correct. XSD validation available via `lxml` if needed.

### Anti-Pattern 6: Hardcoded SQL in Python Strings

**What people do:** Build SQL via f-strings or string concatenation in Python: `f"CREATE TABLE {name} ..."`.

**Why it's wrong:** Hard to read SQL (escaping, indentation). No syntax highlighting. Mixing concerns (SQL structure in Python code).

**Do this instead:** Jinja2 templates with `.sql.j2` extension. IDEs highlight SQL. Templates are readable and editable by non-Python users. Context preparation stays in Python.

## Scaling Considerations

### 0-100 Specs (Initial Implementation)

**Architecture:** Single-process CLI, synchronous generation, all specs in memory.

**Bottleneck:** None. Generating SQL for 100 anchors takes <1 second.

**Optimization:** Not needed.

### 100-1000 Specs (Medium Scale)

**Architecture:** Same. Consider parallel generation (multiprocessing) if generation becomes slow.

**Bottleneck:** File I/O (writing 1000+ SQL files). Likely still fast enough (<10 seconds).

**Optimization:** Optional `--parallel` flag to generate specs in parallel (multiprocessing.Pool). Low priority.

### 1000+ Specs (Large Enterprise)

**Architecture:** Consider batch mode: `architect dab generate-batch specs/*.yaml --output generated/`.

**Bottleneck:** File I/O, memory (loading 1000s of specs). Template rendering parallelizable.

**Optimization:**
1. Streaming YAML parsing (parse one spec at a time, generate, release memory)
2. Parallel generation with multiprocessing
3. Incremental generation (only regenerate changed specs)

**Note:** Most projects have <100 anchors. Premature optimization not recommended. Build for simple case first.

## Alternative Approaches Considered

### Alternative 1: Pydantic for Spec Validation

**Why considered:** Pydantic provides runtime validation with type annotations. Could replace manual validation logic.

**Why NOT chosen:**
- Pydantic is class-heavy (encourages OOP patterns). Conflicts with pure-functional constraint.
- Pydantic adds dependency. Frozen dataclasses + manual validation is simpler and sufficient.
- Pydantic's validation model is "parse into valid object or raise". Our pattern is "parse into dataclass, then validate, return errors". Different flow.
- Confidence: MEDIUM (Pydantic is excellent for its use case, but not our use case)

**Trade-off:** More verbose validation code in exchange for no extra dependency and pure-functional style.

### Alternative 2: SQLAlchemy for SQL Generation

**Why considered:** SQLAlchemy Core provides database-agnostic DDL generation via Python API.

**Why NOT chosen:**
- SQLAlchemy is OOP-heavy (Table, Column, MetaData objects). Conflicts with pure-functional constraint.
- SQLAlchemy output is SQLAlchemy-style SQL (may not match Sisula conventions from anchor.xsd reference).
- Adds heavy dependency (SQLAlchemy + dialect drivers).
- Jinja2 templates give full control over SQL format. Easier to match Sisula reference implementation.
- Confidence: HIGH (SQLAlchemy is excellent for ORMs, but overkill for DDL generation)

**Trade-off:** More control and simplicity (Jinja2 templates) vs. less code (SQLAlchemy DDL API).

### Alternative 3: JSON Schema for YAML Validation

**Why considered:** JSON Schema provides declarative validation. Could replace `validate_spec()` function.

**Why NOT chosen:**
- JSON Schema requires external library (jsonschema). Adds dependency.
- JSON Schema is less expressive than Python for complex rules (e.g., "at least 2 roles must reference anchors").
- Manual validation in Python is clearer and easier to test.
- Confidence: MEDIUM (JSON Schema is good for API validation, but manual validation is simpler here)

**Trade-off:** More flexible validation logic (Python) vs. declarative schema (JSON Schema).

## Sources

### Architectural Patterns

- [Typer Nested Subcommands Documentation](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/) — Subcommand groups via `add_typer()` (HIGH confidence)
- [Advanced SQL Templates In Python with JinjaSql](https://medium.com/data-science/advanced-sql-templates-in-python-with-jinjasql-b996eadd761d) — Jinja2 for SQL generation patterns (MEDIUM confidence)
- [Keep your SQL queries DRY with Jinja templating](https://geoffruddock.com/sql-jinja-templating/) — Jinja2 SQL best practices (MEDIUM confidence)
- [Python Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html) — Functional patterns in Python (HIGH confidence)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) — Frozen dataclass patterns (HIGH confidence)

### SQL Dialect Abstraction

- [SQLAlchemy Database Dialects](https://deepwiki.com/sqlalchemy/sqlalchemy/4-database-dialects) — Dialect abstraction patterns (MEDIUM confidence)
- [Traps and Pitfalls of Using SQL with Jinja](https://www.tobikodata.com/blog/traps-and-pitfalls-of-using-sql-with-jinja) — SQL generation anti-patterns (MEDIUM confidence)

### YAML/XML Validation

- [Cerberus Validation Schemas](https://docs.python-cerberus.org/schemas.html) — Schema validation patterns (MEDIUM confidence)
- [Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/) — Pydantic validation approach (HIGH confidence)
- [Python xml.etree.ElementTree documentation](https://docs.python.org/3/library/xml.etree.elementtree.html) — XML parsing (HIGH confidence)

### Bruin Assets

- [Bruin Asset Definition Schema](https://bruin-data.github.io/bruin/assets/definition-schema.html) — Bruin asset YAML format (HIGH confidence)
- [Bruin Quickstart](https://bruin-data.github.io/bruin/getting-started/introduction/quickstart.html) — Asset examples (HIGH confidence)

### Testing

- [Syrupy Snapshot Testing](https://til.simonwillison.net/pytest/syrupy) — Snapshot testing patterns (MEDIUM confidence)
- [Getting Started with Property-Based Testing](https://semaphore.io/blog/property-based-testing-python-hypothesis-pytest) — Hypothesis integration (MEDIUM confidence)

### Existing Research

- Data Architect v0.1.0-v0.2.0 Architecture Research — Existing patterns (HIGH confidence, internal)
- Data Architect Stack Research — Technology choices (HIGH confidence, internal)
- Anchor Modeling Official Schema (anchor.xsd) — XML schema reference (.references/anchor/anchor.xsd)
- Sisula SQL Templates — Reference SQL generation (.references/anchor/PostgreSQL_crt.directive)

---

## RESEARCH COMPLETE

**Project:** data-architect
**Mode:** ecosystem (subsequent milestone integration)
**Confidence:** HIGH

### Key Findings

1. **Module structure:** New `dab/` module contains all DAB functionality (spec, generate, dialects, templates)
2. **Frozen dataclasses:** Immutable representations of Anchor Modeling constructs matching anchor.xsd
3. **Typer subcommands:** `app.add_typer(dab_cli.app, name="dab")` creates `architect dab *` command group
4. **Dialect abstraction:** Strategy pattern via Protocol + pure function modules (one per database)
5. **Jinja2 templates:** SQL generation with context preparation in Python, simple templates

### Integration Points

- CLI: Single line change to add dab subcommand group
- Scaffold: Pattern reused for `dab init` (pure function + side effects at edge)
- Templates: Extended with Jinja2 for SQL (existing uses embedded strings)
- Data: Frozen dataclasses consistent with existing `ScaffoldResult` pattern
- pyproject.toml: Add `pyyaml>=6.0` and `jinja2>=3.1` dependencies

### Build Order

1. Spec system (spec.py, io.py, keyset.py) — Foundation
2. CLI integration (dab/cli.py, dab init) — Proves integration
3. Dialect abstraction (dialects/, PostgreSQL) — Strategy pattern
4. SQL generation (generate.py, templates/) — Core feature
5. Additional dialects (Snowflake, SQL Server, Oracle) — Extensions
6. Bruin + XML I/O (optional features) — Interop

### Pure Functional Style Maintained

- All spec data: frozen dataclasses with tuple collections
- All transforms: pure functions returning new data
- All side effects: pushed to CLI edges (file I/O, console output)
- No classes with methods (except Protocol for type checking)
- Consistent with v0.1.0-v0.2.0 architecture

---

*Architecture research for: Data Architect DAB Generation Integration*
*Researched: 2026-02-09*
*Confidence: HIGH (verified from official docs, existing codebase, and Anchor Modeling reference materials)*
