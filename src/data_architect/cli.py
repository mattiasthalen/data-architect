"""CLI entry point for the architect command."""

from __future__ import annotations

from pathlib import Path

import typer

from data_architect.dab_init import generate_spec_template
from data_architect.scaffold import ScaffoldAction, scaffold

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
