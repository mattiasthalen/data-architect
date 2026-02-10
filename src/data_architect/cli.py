"""CLI entry point for the architect command."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import typer
from ruamel.yaml import YAML

from data_architect.dab_init import generate_spec_template
from data_architect.generation import (
    format_bruin,
    format_raw,
    generate_all_ddl,
    generate_all_dml,
    write_output,
)
from data_architect.generation.naming import attribute_table_name, tie_table_name
from data_architect.scaffold import ScaffoldAction, scaffold
from data_architect.validation.errors import format_errors
from data_architect.validation.loader import validate_spec
from data_architect.xml_interop import import_xml_to_spec

app = typer.Typer(
    help="Data Architect: Scaffold OpenCode AI agents for data warehouse design.",
)

dab_app = typer.Typer(help="DAB specification management.")

_SYMBOLS: dict[ScaffoldAction, str] = {
    ScaffoldAction.CREATED: "\u2713",
    ScaffoldAction.SKIPPED: "\u26a0",
    ScaffoldAction.WOULD_CREATE: "~",
}

_STYLES: dict[ScaffoldAction, str] = {
    ScaffoldAction.CREATED: "green",
    ScaffoldAction.SKIPPED: "yellow",
    ScaffoldAction.WOULD_CREATE: "blue",
}


@app.callback()
def _callback() -> None:
    """Data Architect: Scaffold OpenCode AI agents for data warehouse design."""


app.add_typer(dab_app, name="dab")


@app.command()
def init(
    dir: Path | None = typer.Option(
        None,
        "--dir",
        help="Target directory (default: current directory)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing files",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be created without writing",
    ),
) -> None:
    """Scaffold OpenCode agent definitions into your project."""
    target = dir if dir is not None else Path.cwd()

    try:
        target.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        typer.echo(f"Error: cannot create directory '{target}': permission denied")
        raise typer.Exit(code=1) from None

    try:
        results = scaffold(target, force=force, dry_run=dry_run)
    except PermissionError:
        typer.echo(f"Error: cannot write to '{target}': permission denied")
        raise typer.Exit(code=1) from None

    for result in results:
        action = result.action
        symbol = _SYMBOLS[action]
        color = _STYLES[action]
        rel = Path(result.path).relative_to(target)
        typer.echo(typer.style(f"{symbol} {rel}", fg=color))

    count = len(results)
    if dry_run:
        typer.echo(f"\nDry run: {count} files would be created")
    else:
        created = sum(1 for r in results if r.action == ScaffoldAction.CREATED)
        skipped = sum(1 for r in results if r.action == ScaffoldAction.SKIPPED)
        parts: list[str] = []
        if created:
            parts.append(f"{created} created")
        if skipped:
            parts.append(f"{skipped} skipped")
        typer.echo(f"\nScaffolded: {', '.join(parts)}")


@dab_app.command(name="init")
def dab_init(
    output: Path = typer.Argument(
        Path("spec.yaml"),
        help="Output file path (default: spec.yaml)",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing file",
    ),
) -> None:
    """Scaffold a blank YAML spec template with inline documentation."""
    # Check if file exists and overwrite not set
    if output.exists() and not overwrite:
        typer.echo(
            typer.style(
                f"Error: {output} already exists (use --overwrite to replace)",
                fg="red",
            )
        )
        raise typer.Exit(code=1)

    # Generate template
    template_content = generate_spec_template()

    # Write to output file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template_content)

    # Success message
    symbol = "\u2713"
    typer.echo(typer.style(f"{symbol} {output}", fg="green"))


@dab_app.command(name="import")
def dab_import(
    xml_path: Path = typer.Argument(..., help="Path to Anchor Modeler XML file"),
    output: Path = typer.Option(
        Path("spec.yaml"),
        "--output",
        "-o",
        help="Output YAML spec file",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite existing YAML file",
    ),
) -> None:
    """Import Anchor Modeler XML to YAML spec format."""
    # Validate xml_path exists
    if not xml_path.exists():
        typer.echo(typer.style(f"Error: XML file not found: {xml_path}", fg="red"))
        raise typer.Exit(code=1)

    # Check output exists and not --overwrite
    if output.exists() and not overwrite:
        typer.echo(
            typer.style(
                f"Error: {output} already exists (use --overwrite to replace)",
                fg="red",
            )
        )
        raise typer.Exit(code=1)

    # Import XML to Spec
    try:
        spec = import_xml_to_spec(xml_path)
    except Exception as e:
        typer.echo(typer.style(f"Error: {e}", fg="red"))
        raise typer.Exit(code=1) from None

    # Serialize Spec to YAML
    spec_dict = spec.model_dump(by_alias=True, exclude_none=True)

    # Write YAML to output file
    output.parent.mkdir(parents=True, exist_ok=True)
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping
    with output.open("w") as f:
        yaml.dump(spec_dict, f)

    # Success message
    symbol = "\u2713"
    typer.echo(typer.style(f"{symbol} Imported {xml_path} -> {output}", fg="green"))


class OutputFormat(StrEnum):
    """Output format for generated SQL."""

    RAW = "raw"
    BRUIN = "bruin"


class Dialect(StrEnum):
    """SQL dialect for generated SQL."""

    POSTGRES = "postgres"
    TSQL = "tsql"
    SNOWFLAKE = "snowflake"


@dab_app.command(name="generate")
def dab_generate(
    spec_path: Path = typer.Argument(..., help="Path to YAML spec file"),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (default: ./output/ relative to spec)",
    ),
    format: OutputFormat = typer.Option(
        OutputFormat.RAW,
        "--format",
        "-f",
        help="Output format: raw (plain SQL) or bruin (SQL with YAML frontmatter)",
    ),
    dialect: Dialect = typer.Option(
        Dialect.POSTGRES,
        "--dialect",
        "-d",
        help="SQL dialect: postgres, tsql, snowflake",
    ),
) -> None:
    """Generate SQL from a validated YAML spec."""
    # 1. Validate spec file exists
    if not spec_path.exists():
        typer.echo(typer.style(f"Error: spec file not found: {spec_path}", fg="red"))
        raise typer.Exit(code=1)

    # 2. Load and validate spec
    result = validate_spec(spec_path)

    # 3. If validation errors, print and exit
    if not result.is_valid:
        typer.echo(typer.style("Validation errors:", fg="red"))
        typer.echo(format_errors(result.errors))
        raise typer.Exit(code=1)

    if result.spec is None:
        typer.echo(typer.style("Error: failed to load spec", fg="red"))
        raise typer.Exit(code=1)

    # 4. Generate DDL and DML
    ddl_files = generate_all_ddl(result.spec, dialect.value)
    dml_files = generate_all_dml(result.spec, dialect.value)

    # 5. Determine output directory
    output_path = output_dir if output_dir is not None else spec_path.parent / "output"

    # 6. Build historized entities lookup for Bruin format
    historized_entities: set[str] = set()
    if format == OutputFormat.BRUIN:
        # Track historized attributes and ties
        for anchor in result.spec.anchors:
            for attr in anchor.attributes:
                if attr.time_range is not None:
                    historized_entities.add(attribute_table_name(anchor, attr))
        for tie in result.spec.ties:
            if tie.time_range is not None:
                historized_entities.add(tie_table_name(tie))

    # 7. Write DDL files
    if format == OutputFormat.RAW:
        ddl_written = write_output(ddl_files, output_path, format_raw, "ddl")
    else:  # OutputFormat.BRUIN
        # DDL files always use create+replace strategy
        def ddl_formatter(sql: str, filename: str = "") -> str:
            entity_name = filename.replace(".sql", "")
            return format_bruin(sql, entity_name, "ddl", False)

        # Write DDL files with Bruin formatter
        ddl_written = []
        ddl_dir = output_path / "ddl"
        ddl_dir.mkdir(parents=True, exist_ok=True)
        for filename in sorted(ddl_files.keys()):
            sql = ddl_files[filename]
            entity_name = filename.replace(".sql", "")
            formatted_sql = format_bruin(sql, entity_name, "ddl", False)
            file_path = ddl_dir / filename
            file_path.write_text(formatted_sql)
            ddl_written.append(file_path)

    # 8. Write DML files
    if format == OutputFormat.RAW:
        dml_written = write_output(dml_files, output_path, format_raw, "dml")
    else:  # OutputFormat.BRUIN
        # DML files use merge for historized, create+replace for static
        dml_written = []
        dml_dir = output_path / "dml"
        dml_dir.mkdir(parents=True, exist_ok=True)
        for filename in sorted(dml_files.keys()):
            sql = dml_files[filename]
            # Extract entity name (remove _load.sql suffix)
            entity_name = filename.replace("_load.sql", "")
            is_historized = entity_name in historized_entities
            formatted_sql = format_bruin(sql, entity_name, "dml", is_historized)
            file_path = dml_dir / filename
            file_path.write_text(formatted_sql)
            dml_written.append(file_path)

    # 9. Print summary
    symbol = "\u2713"
    ddl_count = len(ddl_written)
    dml_count = len(dml_written)
    typer.echo(
        typer.style(
            f"{symbol} Generated {ddl_count} DDL and {dml_count} DML files",
            fg="green",
        )
    )
    typer.echo(f"Output directory: {output_path}")
