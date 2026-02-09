# Phase 6: YAML Schema Foundation and Spec Validation - Research

**Researched:** 2026-02-09
**Domain:** YAML schema validation with Pydantic, CLI scaffolding with Click, line-numbered error reporting
**Confidence:** HIGH

## Summary

This phase implements a YAML-based specification format for Anchor Modeling with runtime validation, referential integrity checks, and precise error reporting with line numbers. The standard Python stack for this domain is Pydantic v2 for validation models (with frozen configuration for immutability), ruamel.yaml for YAML parsing with line number preservation, and Click for CLI command structure.

The critical technical challenge is bridging Pydantic's validation error reporting (which reports field paths) with YAML line numbers (which ruamel.yaml tracks separately). The solution requires capturing line number information during YAML parsing and associating it with Pydantic field paths to produce validation errors like "Line 42: anchor AC_Customer references nonexistent attribute InvalidAttr."

The three-layer schema design (XML-compatible core, YAML extensions, export-incompatible markers) can be implemented using Pydantic's field metadata and custom serializers to ensure that only XML-compatible fields are included when exporting to anchor.xsd format.

**Primary recommendation:** Use Pydantic v2.12+ with ruamel.yaml 0.19+ for validation and line tracking, implement custom error formatting to merge Pydantic ValidationError field paths with ruamel.yaml lc (line/column) data, and use Click 8.3+ command groups for the `dab init` scaffolding command.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12.5+ | Spec validation models with frozen config, cross-field validators | Industry standard for runtime Python validation, supports complex cross-field checks via model_validator |
| ruamel.yaml | 0.19.1+ | YAML parsing with line/column tracking via lc attribute | Only mature YAML parser that preserves line numbers and comments for round-trip editing |
| click | 8.3.1+ | CLI framework for `dab init` command | De facto standard for Python CLIs, excellent composability and help generation |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic-core | (bundled) | Rust-powered validation engine | Automatically included with Pydantic v2, provides fast validation |
| pathlib | (stdlib) | File path handling for template output | Use with Click Path type for reliable file operations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ruamel.yaml | StrictYAML | StrictYAML provides schema validation but is overly restrictive (rejects valid YAML 1.2 features), built on ruamel.yaml anyway |
| ruamel.yaml | PyYAML | PyYAML is simpler but doesn't preserve line numbers or comments, uses older YAML 1.1 spec |
| Pydantic | dataclasses + manual validation | No runtime validation, no cross-field validators, no JSON schema generation |
| Click | argparse | More verbose, no composability, poor help generation |
| Click | Typer | Typer is Click wrapper with type hints, adds abstraction layer without clear benefit for simple commands |

**Installation:**
```bash
pip install pydantic>=2.12.5 ruamel.yaml>=0.19.1 click>=8.3.1
```

## Architecture Patterns

### Recommended Project Structure
```
src/architect/
├── models/              # Pydantic spec models
│   ├── __init__.py
│   ├── spec.py          # Top-level spec model
│   ├── anchor.py        # Anchor, Attribute models
│   ├── tie.py           # Tie, Role models
│   └── knot.py          # Knot models
├── validation/          # Validation engine
│   ├── __init__.py
│   ├── validator.py     # Main validation orchestrator
│   ├── referential.py   # Referential integrity checks
│   └── errors.py        # Error formatting with line numbers
├── cli/                 # Click commands
│   ├── __init__.py
│   ├── main.py          # Entry point with @click.group
│   └── init.py          # `dab init` command
└── templates/           # YAML templates for scaffolding
    └── spec_template.yaml
```

### Pattern 1: Frozen Pydantic Models for Immutable Specs
**What:** Use Pydantic's `model_config = ConfigDict(frozen=True)` to make spec models immutable after validation.
**When to use:** All spec models (Anchor, Attribute, Tie, Knot, Spec) should be frozen to prevent accidental mutation after loading.
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/models/
from pydantic import BaseModel, ConfigDict

class Anchor(BaseModel):
    model_config = ConfigDict(frozen=True)

    mnemonic: str
    descriptor: str
    attributes: list['Attribute'] = []

    # Use model_copy for updates
    def with_attribute(self, attr: 'Attribute') -> 'Anchor':
        return self.model_copy(update={'attributes': self.attributes + [attr]})
```

### Pattern 2: Cross-Field Validators for Referential Integrity
**What:** Use `@model_validator(mode='after')` to validate relationships between fields after individual field validation completes.
**When to use:** Checking that attribute anchor references exist, tie role references are valid, mnemonic uniqueness, etc.
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/validators/
from pydantic import BaseModel, model_validator
from typing_extensions import Self

class Spec(BaseModel):
    anchors: dict[str, Anchor]
    ties: dict[str, Tie]

    @model_validator(mode='after')
    def check_tie_references(self) -> Self:
        for tie_name, tie in self.ties.items():
            for role in tie.roles:
                if role.anchor not in self.anchors:
                    raise ValueError(
                        f"Tie '{tie_name}' role references "
                        f"nonexistent anchor '{role.anchor}'"
                    )
        return self
```

### Pattern 3: Line Number Preservation with ruamel.yaml
**What:** Use ruamel.yaml's `lc` attribute to track line/column information for all YAML nodes.
**When to use:** During YAML loading, capture line numbers for each key/value to later map to Pydantic validation errors.
**Example:**
```python
# Source: https://yaml.dev/doc/ruamel-yaml/ + community examples
from ruamel.yaml import YAML

yaml = YAML()
data = yaml.load(yaml_content)

# Access line info for mappings
anchor_line = data['anchors']['AC_Customer'].lc.line  # 0-based
attribute_key_line = data['anchors'].lc.key('AC_Customer')  # line of key
attribute_val_line = data['anchors'].lc.value('AC_Customer')  # line of value

# Store mapping: field_path -> line_number
line_map = {}
def capture_lines(obj, path=''):
    if hasattr(obj, 'lc'):
        line_map[path] = obj.lc.line
    if isinstance(obj, dict):
        for key, val in obj.items():
            capture_lines(val, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            capture_lines(item, f"{path}[{i}]")
```

### Pattern 4: Merging Pydantic Errors with Line Numbers
**What:** Map Pydantic ValidationError field locations to YAML line numbers using captured lc data.
**When to use:** When reporting validation errors to users.
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/errors/validation_errors/ + custom implementation
from pydantic import ValidationError

def format_validation_errors(exc: ValidationError, line_map: dict[str, int]) -> list[str]:
    """Convert Pydantic errors to line-numbered messages."""
    messages = []
    for error in exc.errors():
        # error['loc'] is tuple like ('anchors', 'AC_Customer', 'attributes', 0, 'mnemonic')
        field_path = '.'.join(str(loc) for loc in error['loc'])

        # Look up line number from captured data
        line_num = line_map.get(field_path, None)

        if line_num is not None:
            messages.append(f"Line {line_num + 1}: {error['msg']}")
        else:
            messages.append(f"{field_path}: {error['msg']}")

    return messages
```

### Pattern 5: Click Command Groups for CLI Organization
**What:** Use `@click.group()` for the main entry point and `@group.command()` for subcommands.
**When to use:** When building multi-command CLIs like `dab init`, `dab generate`, `dab validate`.
**Example:**
```python
# Source: https://click.palletsprojects.com/en/stable/commands-and-groups/
import click

@click.group()
def dab():
    """Data Architect Builder - Anchor Modeling code generation."""
    pass

@dab.command()
@click.argument('output', type=click.Path(writable=True), default='spec.yaml')
def init(output):
    """Create a new YAML spec template."""
    # Generate template with inline comments
    template = generate_spec_template()
    with open(output, 'w') as f:
        f.write(template)
    click.echo(f"Created {output}")

if __name__ == '__main__':
    dab()
```

### Pattern 6: Template Generation with ruamel.yaml for Comment Preservation
**What:** Use ruamel.yaml.dump() to generate YAML templates with inline comments.
**When to use:** Implementing `dab init` to create spec.yaml with documentation comments.
**Example:**
```python
# Source: https://ruamel.yaml.readthedocs.io/ + community examples
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

def generate_spec_template() -> str:
    yaml = YAML()
    yaml.default_flow_style = False

    spec = CommentedMap()
    spec['anchors'] = CommentedMap()
    spec.yaml_set_comment_before_after_key('anchors',
        before='Anchors represent entities or events in your domain')

    spec['attributes'] = CommentedMap()
    spec.yaml_set_comment_before_after_key('attributes',
        before='Attributes are properties of anchors')

    # Dump to string
    from io import StringIO
    stream = StringIO()
    yaml.dump(spec, stream)
    return stream.getvalue()
```

### Pattern 7: Three-Layer Schema with Field Metadata
**What:** Use Pydantic Field() metadata to tag fields as XML-core, YAML-extension, or export-incompatible.
**When to use:** Ensuring only XML-compatible fields are exported to anchor.xsd format.
**Example:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class Attribute(BaseModel):
    # XML-core fields (always exported)
    mnemonic: str = Field(metadata={'layer': 'xml-core'})
    anchor: str = Field(metadata={'layer': 'xml-core'})
    descriptor: str = Field(metadata={'layer': 'xml-core'})
    dataRange: str | None = Field(None, metadata={'layer': 'xml-core'})

    # YAML-extension fields (exported with conversion)
    staging_column: str | None = Field(None, metadata={'layer': 'yaml-ext'})

    # Export-incompatible markers (never exported)
    _line_number: int | None = Field(None, alias='__line__', metadata={'layer': 'internal'})

    def to_xml_dict(self) -> dict:
        """Export only XML-core and YAML-extension fields."""
        result = {}
        for field_name, field_info in self.model_fields.items():
            layer = field_info.metadata.get('layer') if field_info.metadata else None
            if layer in ('xml-core', 'yaml-ext'):
                val = getattr(self, field_name)
                if val is not None:
                    result[field_name] = val
        return result
```

### Anti-Patterns to Avoid
- **Mutating frozen models directly:** Use `model_copy(update={...})` instead of `setattr()` on frozen instances.
- **Using @field_validator for cross-field checks:** Always prefer `@model_validator(mode='after')` for checks involving multiple fields, as field validators execute before all fields are validated.
- **Ignoring line number capture during parsing:** Line numbers must be captured during initial YAML load; Pydantic validation happens after parsing, so you can't retroactively get line info.
- **Using PyYAML instead of ruamel.yaml:** PyYAML discards line numbers and comments, making error reporting and template generation much harder.
- **Recursive strict mode assumptions:** Pydantic strict mode is NOT recursive to nested models; set `model_config = ConfigDict(strict=True)` on each model individually if needed.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML validation | Custom parser with manual type checking | Pydantic models + YAML loader | Pydantic handles type coercion, validation, error messages, JSON schema generation; custom validation is error-prone |
| Line number tracking | Manual line counting during parse | ruamel.yaml lc attribute | YAML supports multiline strings, flow/block styles, comments; accurate line tracking is complex |
| CLI argument parsing | sys.argv manipulation | Click decorators | Click handles help generation, type conversion, validation, error messages, subcommands automatically |
| Referential integrity | Manual loops checking existence | Pydantic model_validator | model_validator runs after all fields validated, has access to full model state, integrates with error reporting |
| Mnemonic collision detection | Custom uniqueness tracking | Pydantic validator with sorted() | Deterministic collision detection requires stable ordering; Pydantic validators can enforce uniqueness constraints cleanly |
| Comment-preserving YAML dump | String manipulation to inject comments | ruamel.yaml CommentedMap | Preserving comments while round-tripping YAML requires understanding YAML structure; ruamel.yaml handles this |
| Immutable data models | Manual __setattr__ blocking | Pydantic frozen=True | Pydantic frozen models prevent mutation, provide model_copy for updates, integrate with validation |

**Key insight:** YAML validation with line-numbered error reporting is deceptively complex. ruamel.yaml preserves structural information (line numbers, comments) that gets lost when converting to Python dicts, and Pydantic validates after conversion. The bridge between these two layers (mapping field paths to line numbers) is the critical integration point. Hand-rolling either YAML parsing or validation means rebuilding years of edge case handling.

## Common Pitfalls

### Pitfall 1: Line Number Mismatch from 0-Based to 1-Based Reporting
**What goes wrong:** ruamel.yaml lc.line is 0-based, users expect 1-based line numbers in error messages.
**Why it happens:** Different conventions - Python uses 0-based indexing, editors use 1-based line numbers.
**How to avoid:** Always add 1 when formatting line numbers for user-facing messages: `f"Line {lc.line + 1}: error"`
**Warning signs:** Error messages report "Line 0" or off-by-one from editor line numbers.

### Pitfall 2: Missing Line Info for Dynamically Created Fields
**What goes wrong:** Validation errors for computed/default fields have no corresponding YAML line.
**Why it happens:** Not all Pydantic fields come from YAML; some are defaults, computed properties, or added by validators.
**How to avoid:** Check if field path exists in line_map before looking up; provide fallback error message without line number.
**Warning signs:** KeyError when mapping Pydantic loc to line numbers for fields with defaults.

### Pitfall 3: Nested Model Field Path Mapping
**What goes wrong:** Pydantic error loc like `('anchors', 'AC_Customer', 'attributes', 0, 'mnemonic')` doesn't map cleanly to YAML structure.
**Why it happens:** YAML uses nested dicts/lists, Pydantic uses tuple paths; list indices vs dict keys need different handling.
**How to avoid:** Build line_map recursively during YAML parse, capturing both dict keys and list indices as paths.
**Warning signs:** Line numbers work for top-level fields but fail for nested attributes or list items.

### Pitfall 4: Frozen Model Mutation Attempts
**What goes wrong:** Code tries to modify frozen Pydantic models, raises ValidationError or AttributeError.
**Why it happens:** Frozen models prevent setattr; developers familiar with mutable dataclasses expect assignment to work.
**How to avoid:** Use `model_copy(update={...})` pattern for all updates; document frozen=True in model docstrings.
**Warning signs:** ValidationError: "Instance is frozen" or AttributeError during model modification.

### Pitfall 5: Cross-Field Validator Ordering Issues
**What goes wrong:** `@model_validator` tries to access a field that hasn't been validated yet.
**Why it happens:** Using `mode='before'` accesses raw data; fields validated in definition order.
**How to avoid:** Always use `mode='after'` for cross-field checks; this guarantees all fields passed individual validation.
**Warning signs:** KeyError or AttributeError in model_validator for fields that should exist.

### Pitfall 6: YAML 1.1 vs 1.2 Type Coercion Surprises
**What goes wrong:** Strings like "yes", "no", "on", "off" parse as booleans instead of strings in YAML 1.1.
**Why it happens:** PyYAML uses YAML 1.1 spec; ruamel.yaml defaults to YAML 1.2 which is less aggressive with coercion.
**How to avoid:** Use ruamel.yaml with explicit version; quote strings that might be coerced: `descriptor: "yes"`.
**Warning signs:** Boolean values appearing where strings expected, especially with yes/no/on/off.

### Pitfall 7: Overly Strict Validation Blocking Valid YAML
**What goes wrong:** Pydantic strict mode rejects valid YAML like integer-as-string conversions.
**Why it happens:** `model_config = ConfigDict(strict=True)` globally disables type coercion.
**How to avoid:** Use lax mode (default) for YAML loading; apply Field(strict=True) selectively for fields requiring exact types.
**Warning signs:** Validation errors for things like `"42"` when int expected, valid YAML rejected.

### Pitfall 8: Missing Mnemonic Collision Context
**What goes wrong:** Error says "Mnemonic 'AC' is duplicate" but doesn't say which two entities collided.
**Why it happens:** Simple uniqueness check doesn't track what collided.
**How to avoid:** Validator should collect all mnemonics with their sources, report collisions with both entities: "Mnemonic 'AC' collision between Anchor 'Account' and Anchor 'Activity'".
**Warning signs:** Users can't identify which entities to rename without searching the entire spec.

### Pitfall 9: Comment Loss on Round-Trip
**What goes wrong:** Loading YAML, modifying, and saving loses all inline comments.
**Why it happens:** Using standard dict instead of ruamel.yaml CommentedMap.
**How to avoid:** Keep ruamel.yaml data structures (CommentedMap/CommentedSeq) throughout; use yaml.dump() not PyYAML.
**Warning signs:** Regenerated YAML loses documentation comments from original file.

### Pitfall 10: Path Type Validation Without exists=False
**What goes wrong:** `click.Path(exists=True)` for output file rejects non-existent paths.
**Why it happens:** Click Path type validates file existence by default.
**How to avoid:** For output files, use `click.Path(writable=True)` without exists constraint; for input use `click.Path(exists=True, readable=True)`.
**Warning signs:** `dab init` command fails when target file doesn't exist yet.

## Code Examples

Verified patterns from official sources:

### Loading YAML with Line Number Tracking
```python
# Source: https://yaml.dev/doc/ruamel-yaml/ + https://docs.pydantic.dev/latest/
from ruamel.yaml import YAML
from pydantic import ValidationError
from typing import Any

def load_spec_with_lines(yaml_path: str) -> tuple[dict, dict[str, int]]:
    """Load YAML spec and build field path -> line number mapping."""
    yaml = YAML()
    with open(yaml_path) as f:
        data = yaml.load(f)

    line_map = {}

    def capture_lines(obj: Any, path: str = ''):
        """Recursively capture line numbers for all nodes."""
        if hasattr(obj, 'lc'):
            line_map[path] = obj.lc.line

        if isinstance(obj, dict):
            for key, val in obj.items():
                key_path = f"{path}.{key}" if path else key
                # Capture line for key itself if available
                if hasattr(obj, 'lc'):
                    key_line = obj.lc.key(key)
                    if key_line is not None:
                        line_map[f"{key_path}.__key__"] = key_line
                capture_lines(val, key_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                capture_lines(item, f"{path}[{i}]")

    capture_lines(data)
    return data, line_map
```

### Validating Spec with Line-Numbered Errors
```python
# Source: https://docs.pydantic.dev/latest/errors/validation_errors/
from pydantic import ValidationError

def validate_spec(yaml_path: str, spec_model: type[BaseModel]) -> BaseModel:
    """Load and validate spec, reporting errors with line numbers."""
    data, line_map = load_spec_with_lines(yaml_path)

    try:
        spec = spec_model.model_validate(data)
        return spec
    except ValidationError as exc:
        # Format errors with line numbers
        errors = []
        for error in exc.errors():
            # Convert Pydantic loc tuple to field path string
            loc_parts = [str(part) for part in error['loc']]
            field_path = '.'.join(loc_parts)

            # Look up line number
            line_num = line_map.get(field_path)

            if line_num is not None:
                errors.append(f"Line {line_num + 1}: {error['msg']} (field: {field_path})")
            else:
                errors.append(f"{field_path}: {error['msg']}")

        # Raise formatted error
        raise ValueError(f"Validation errors in {yaml_path}:\n" + "\n".join(errors))
```

### Referential Integrity Validator
```python
# Source: https://docs.pydantic.dev/latest/concepts/validators/
from pydantic import BaseModel, model_validator
from typing_extensions import Self

class Spec(BaseModel):
    model_config = ConfigDict(frozen=True)

    anchors: dict[str, 'Anchor']
    attributes: dict[str, 'Attribute']
    ties: dict[str, 'Tie']
    knots: dict[str, 'Knot']

    @model_validator(mode='after')
    def check_attribute_anchor_references(self) -> Self:
        """Validate attributes reference existing anchors."""
        for attr_name, attr in self.attributes.items():
            if attr.anchor not in self.anchors:
                raise ValueError(
                    f"Attribute '{attr_name}' references "
                    f"nonexistent anchor '{attr.anchor}'"
                )
        return self

    @model_validator(mode='after')
    def check_mnemonic_collisions(self) -> Self:
        """Detect mnemonic collisions across anchors/knots."""
        mnemonic_sources = {}

        # Collect mnemonics from anchors
        for anchor_name, anchor in self.anchors.items():
            if anchor.mnemonic in mnemonic_sources:
                raise ValueError(
                    f"Mnemonic '{anchor.mnemonic}' collision: "
                    f"Anchor '{anchor_name}' conflicts with "
                    f"{mnemonic_sources[anchor.mnemonic]}"
                )
            mnemonic_sources[anchor.mnemonic] = f"Anchor '{anchor_name}'"

        # Collect mnemonics from knots
        for knot_name, knot in self.knots.items():
            if knot.mnemonic in mnemonic_sources:
                raise ValueError(
                    f"Mnemonic '{knot.mnemonic}' collision: "
                    f"Knot '{knot_name}' conflicts with "
                    f"{mnemonic_sources[knot.mnemonic]}"
                )
            mnemonic_sources[knot.mnemonic] = f"Knot '{knot_name}'"

        return self
```

### Deterministic Mnemonic Generation with Collision Detection
```python
# Deterministic generation by sorting names
def generate_mnemonic(names: list[str], length: int = 2) -> str:
    """Generate deterministic mnemonic from sorted names."""
    # Sort to ensure deterministic output
    sorted_names = sorted(names)

    # Take first letters up to length
    letters = ''.join(name[0].upper() for name in sorted_names[:length])
    return letters

# With override support
class Anchor(BaseModel):
    descriptor: str
    mnemonic: str | None = None  # Optional override

    @model_validator(mode='after')
    def set_mnemonic_if_missing(self) -> Self:
        """Generate mnemonic if not explicitly provided."""
        if self.mnemonic is None:
            # Generate from descriptor
            words = self.descriptor.split()
            object.__setattr__(self, 'mnemonic', generate_mnemonic(words))
        return self
```

### Click Command for `dab init`
```python
# Source: https://click.palletsprojects.com/en/stable/
import click
from pathlib import Path

@click.command()
@click.argument(
    'output',
    type=click.Path(writable=True, path_type=Path),
    default='spec.yaml'
)
@click.option(
    '--overwrite',
    is_flag=True,
    help='Overwrite existing file'
)
def init(output: Path, overwrite: bool):
    """Create a new YAML spec template with inline documentation."""
    if output.exists() and not overwrite:
        click.echo(f"Error: {output} already exists. Use --overwrite to replace.")
        raise click.Abort()

    # Generate template
    template = generate_spec_template()

    # Write to file
    output.write_text(template)
    click.echo(f"Created {output}")
```

### YAML Template Generation with Comments
```python
# Source: https://ruamel.yaml.readthedocs.io/ + community examples
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from io import StringIO

def generate_spec_template() -> str:
    """Generate YAML spec template with inline comments."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping

    spec = CommentedMap()

    # Anchors section
    spec['anchors'] = CommentedMap()
    spec.yaml_set_comment_before_after_key(
        'anchors',
        before='\n'.join([
            'Anchors represent entities or events in your domain.',
            'Each anchor must have a unique mnemonic (2-3 letter code).',
            'Example: AC_Customer for a Customer anchor with mnemonic AC'
        ])
    )

    # Example anchor
    example_anchor = CommentedMap()
    example_anchor['mnemonic'] = 'AC'
    example_anchor['descriptor'] = 'Customer'
    example_anchor.yaml_add_eol_comment('Unique 2-3 letter code', 'mnemonic')
    example_anchor.yaml_add_eol_comment('Human-readable name', 'descriptor')
    spec['anchors']['AC_Customer'] = example_anchor

    # Attributes section
    spec['attributes'] = CommentedMap()
    spec.yaml_set_comment_before_after_key(
        'attributes',
        before='\n'.join([
            'Attributes are properties of anchors.',
            'Each attribute must reference an existing anchor via the anchor field.'
        ])
    )

    # Ties section
    spec['ties'] = CommentedMap()
    spec.yaml_set_comment_before_after_key(
        'ties',
        before='Ties represent relationships between anchors.'
    )

    # Knots section
    spec['knots'] = CommentedMap()
    spec.yaml_set_comment_before_after_key(
        'knots',
        before='Knots represent shared properties like states or types.'
    )

    # Dump to string
    stream = StringIO()
    yaml.dump(spec, stream)
    return stream.getvalue()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 with custom Config class | Pydantic v2 with ConfigDict | v2.0 (Jun 2023) | ConfigDict is more explicit, frozen field replaces allow_mutation=False |
| PyYAML for all YAML parsing | ruamel.yaml for schema/config validation | ~2015 onward | ruamel.yaml preserves comments and line numbers, supports YAML 1.2 |
| Manual argparse for CLIs | Click for composable commands | ~2014 onward | Click provides decorators, help generation, type validation out of box |
| @validator decorator | @field_validator and @model_validator | Pydantic v2.0 | Clearer separation: field_validator for single fields, model_validator for cross-field |
| ValidationError.errors() returns dicts | Still returns dicts but with typed_dict option | Pydantic v2.5+ | Can request TypedDict for better type hints |

**Deprecated/outdated:**
- **Pydantic v1 Config class:** Replaced by model_config = ConfigDict(...) in v2
- **allow_mutation=False:** Replaced by frozen=True in v2
- **@validator decorator:** Replaced by @field_validator and @model_validator in v2
- **PyYAML for configuration files:** Still works but ruamel.yaml is preferred for better error reporting and comment preservation
- **parse_obj():** Replaced by model_validate() in Pydantic v2
- **dict():** Replaced by model_dump() in Pydantic v2

## Open Questions

1. **Exact line number mapping for deeply nested YAML structures**
   - What we know: ruamel.yaml provides lc.line, lc.key(), lc.value() for accessing line numbers
   - What's unclear: How to reliably map complex Pydantic error paths like `('ties', 'TieAB', 'roles', 2, 'anchor')` to the exact YAML line when list items don't have keys
   - Recommendation: Build comprehensive line_map during parsing that captures both dict keys and list indices; test with deeply nested structures early

2. **Performance impact of line tracking for large specs**
   - What we know: Capturing line numbers requires traversing entire YAML structure
   - What's unclear: Whether line tracking adds significant overhead for specs with hundreds of anchors/attributes
   - Recommendation: Implement line tracking, benchmark with realistic large specs (500+ entities), optimize if needed (lazy line capture, caching)

3. **Three-layer schema export to anchor.xsd**
   - What we know: Field metadata can tag layers (xml-core, yaml-ext, internal)
   - What's unclear: Whether Pydantic's JSON schema generation can be customized to respect layer metadata
   - Recommendation: Start with custom to_xml_dict() method on models; investigate Pydantic serializers for more automatic export later

4. **Handling YAML anchors/aliases in spec (YAML feature, not Anchor Modeling)**
   - What we know: YAML supports &anchor and *alias syntax for reusing nodes
   - What's unclear: Whether ruamel.yaml preserves line numbers correctly when YAML aliases are used, and whether Pydantic validation sees the expanded structure
   - Recommendation: Document that YAML anchors/aliases are allowed (useful for DRY knot references); test line number reporting works correctly with aliases

## Sources

### Primary (HIGH confidence)
- [Pydantic Documentation v2.12.5](https://docs.pydantic.dev/latest/) - Validated models, frozen config, validators
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/) - model_validator and field_validator patterns
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/) - Frozen models, model_copy, model_validate
- [Pydantic Validation Errors](https://docs.pydantic.dev/latest/errors/validation_errors/) - Error structure and formatting
- [Pydantic Strict Mode](https://docs.pydantic.dev/latest/concepts/strict_mode/) - Lax vs strict validation behavior
- [Click Documentation 8.3.x](https://click.palletsprojects.com/en/stable/) - Command groups, Path type, decorators
- [Click Commands and Groups](https://click.palletsprojects.com/en/stable/commands-and-groups/) - Best practices for CLI organization
- [StrictYAML Line Numbers](https://hitchdev.com/strictyaml/using/alpha/howto/what-line/) - start_line, end_line properties

### Secondary (MEDIUM confidence)
- [Real Python: YAML in Python](https://realpython.com/python-yaml/) - Comparison of PyYAML, ruamel.yaml, StrictYAML (verified with official docs)
- [Real Python: Pydantic](https://realpython.com/python-pydantic/) - Validation patterns (verified with official docs)
- [Real Python: Click](https://realpython.com/python-click/) - CLI best practices (verified with official docs)
- [PyPI: pydantic](https://pypi.org/project/pydantic/) - Current version 2.12.5, release dates
- [PyPI: click](https://pypi.org/project/click/) - Current version 8.3.1, release dates
- [PyPI: ruamel.yaml](https://pypi.org/project/ruamel.yaml/) - Current version 0.19.1
- [Anchor Modeling PDF](https://www.anchormodeling.com/wp-content/uploads/2010/09/AM-XML.pdf) - Official anchor.xsd schema structure
- [GitHub: Pydantic Discussions on frozen models](https://github.com/pydantic/pydantic/discussions/12036) - Usage patterns for frozen=True
- [Medium: Validating YAML with Pydantic](https://betterprogramming.pub/validating-yaml-configs-made-easy-with-pydantic-594522612db5) - Practical patterns (cross-referenced with official docs)
- [Medium: YAML Comment Preservation](https://medium.com/@reorx/tips-that-may-save-you-from-the-hell-of-pyyaml-572cde7e1d6f) - ruamel.yaml best practices

### Tertiary (LOW confidence - needs validation)
- [GitHub: ruamel_yaml_line_info](https://github.com/nh13/ruamel_yaml_line_info) - Third-party line info utility (not needed, built-in lc works)
- [PyPI: pydantic-yaml-parser](https://pypi.org/project/pydantic-yaml-parser/) - Third-party Pydantic YAML integration (better to build custom integration)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pydantic v2, ruamel.yaml, Click are industry standards with mature ecosystems
- Architecture patterns: HIGH - Frozen models, model_validator, Click groups are documented official patterns
- Line number mapping: MEDIUM - Pattern is established but requires custom integration code, not built-in to Pydantic
- Three-layer schema: MEDIUM - Design is sound but requires custom serialization logic
- Pitfalls: HIGH - Based on official docs, GitHub issues, and verified community experiences
- Template generation: MEDIUM - ruamel.yaml CommentedMap is documented but complex for large templates

**Research date:** 2026-02-09
**Valid until:** 2026-04-09 (60 days - stack is mature and stable)
