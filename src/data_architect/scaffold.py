"""Pure scaffold engine — file creation, conflict detection, dry-run."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from data_architect.templates import TEMPLATES

if TYPE_CHECKING:
    from pathlib import Path


class ScaffoldAction(Enum):
    """Possible outcomes for each file in the scaffold manifest."""

    CREATED = "created"
    SKIPPED = "skipped"
    WOULD_CREATE = "would_create"


@dataclass(frozen=True)
class ScaffoldResult:
    """Result of scaffolding a single file."""

    path: str
    action: ScaffoldAction
    reason: str


def scaffold(
    target_dir: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> list[ScaffoldResult]:
    """Scaffold files into target_dir.

    Returns a result for each file in the manifest.

    Args:
        target_dir: Root directory for all scaffolded files.
        force: If True, overwrite existing files.
        dry_run: If True, report what would happen without writing.

    Returns:
        List of ScaffoldResult describing what happened to each file.
    """
    results: list[ScaffoldResult] = []

    for relative_path, content in TEMPLATES.items():
        full_path = target_dir / relative_path

        if dry_run:
            results.append(
                ScaffoldResult(
                    path=str(full_path),
                    action=ScaffoldAction.WOULD_CREATE,
                    reason="Dry run",
                )
            )
        elif full_path.exists() and not force:
            results.append(
                ScaffoldResult(
                    path=str(full_path),
                    action=ScaffoldAction.SKIPPED,
                    reason="Already exists",
                )
            )
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            results.append(
                ScaffoldResult(
                    path=str(full_path),
                    action=ScaffoldAction.CREATED,
                    reason="Created",
                )
            )

    return results
