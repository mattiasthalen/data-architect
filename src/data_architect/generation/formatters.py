"""Output formatters for SQL generation (raw and Bruin)."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def format_raw(sql: str) -> str:
    """Format SQL as-is with consistent trailing newline.

    Args:
        sql: SQL string to format

    Returns:
        SQL string with trailing newline
    """
    return sql if sql.endswith("\n") else sql + "\n"


def format_bruin(
    sql: str, entity_name: str, entity_type: str, is_historized: bool
) -> str:
    """Format SQL with Bruin YAML frontmatter.

    Args:
        sql: SQL string to wrap
        entity_name: Entity name for bruin asset (e.g., "AC_Actor")
        entity_type: "ddl" or "dml"
        is_historized: Whether entity has time_range (affects strategy)

    Returns:
        SQL wrapped with Bruin frontmatter
    """
    # Determine materialization strategy
    if entity_type == "ddl":
        strategy = "create+replace"
    elif is_historized:
        strategy = "merge"
    else:
        strategy = "create+replace"

    frontmatter = f"""/* @bruin
name: dab.{entity_name}
type: sql
materialization:
    type: table
    strategy: {strategy}
@bruin */

"""

    return frontmatter + sql


def write_output(
    files: dict[str, str],
    output_dir: Path,
    format_fn: Callable[[str], str],
    subdir: str,
) -> list[Path]:
    """Write formatted SQL files to output directory.

    Args:
        files: Dictionary mapping filenames to SQL strings
        output_dir: Base output directory
        format_fn: Formatting function to apply to each SQL string
        subdir: Subdirectory name ("ddl" or "dml")

    Returns:
        Sorted list of written file paths (for deterministic output)
    """
    target_dir = output_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    # Sort filenames for deterministic output
    for filename in sorted(files.keys()):
        sql = files[filename]
        formatted_sql = format_fn(sql)

        file_path = target_dir / filename
        file_path.write_text(formatted_sql)
        written.append(file_path)

    return sorted(written)
