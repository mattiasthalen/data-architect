"""CLI integration tests using Typer CliRunner."""

from typer.testing import CliRunner

from data_architect.cli import app
from data_architect.templates import TEMPLATES

runner = CliRunner()


def test_init_creates_files_in_empty_dir(tmp_path):
    """architect init in empty dir creates all 14 files with checkmark output."""
    result = runner.invoke(app, ["init", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "\u2713" in result.output
    for relative_path in TEMPLATES:
        assert (tmp_path / relative_path).exists(), f"{relative_path} not created"


def test_init_creates_all_files(tmp_path):
    """Exactly 14 files are created on disk."""
    runner.invoke(app, ["init", "--dir", str(tmp_path)])
    created_files = []
    for relative_path in TEMPLATES:
        full = tmp_path / relative_path
        if full.exists():
            created_files.append(relative_path)
    assert len(created_files) == 14


def test_init_default_dir_is_cwd(tmp_path, monkeypatch):
    """init without --dir scaffolds into current working directory."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    for relative_path in TEMPLATES:
        assert (tmp_path / relative_path).exists(), f"{relative_path} not in cwd"


def test_init_skips_existing_files(tmp_path):
    """Pre-existing file is skipped with warning symbol."""
    first_path = next(iter(TEMPLATES))
    full = tmp_path / first_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("existing content")

    result = runner.invoke(app, ["init", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "\u26a0" in result.output
    # The existing file should not be overwritten
    assert full.read_text() == "existing content"


def test_init_force_overwrites(tmp_path):
    """--force overwrites existing files with checkmark for all."""
    first_path = next(iter(TEMPLATES))
    full = tmp_path / first_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("old content")

    result = runner.invoke(app, ["init", "--dir", str(tmp_path), "--force"])
    assert result.exit_code == 0
    # All should show checkmark (created)
    lines = [line for line in result.output.strip().split("\n") if line.strip()]
    # Exclude the summary line
    file_lines = [
        line
        for line in lines
        if not line.startswith("\n") and not line.startswith("Scaffolded")
    ]
    for line in file_lines:
        if line.strip() and not line.strip().startswith("Scaffolded"):
            assert "\u2713" in line or "Scaffolded" in line
    # File should be overwritten
    assert full.read_text() == TEMPLATES[first_path]


def test_init_dry_run_no_files(tmp_path):
    """--dry-run prints tilde symbols and creates no files on disk."""
    result = runner.invoke(app, ["init", "--dry-run", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "~" in result.output
    assert "Dry run" in result.output
    for relative_path in TEMPLATES:
        assert not (tmp_path / relative_path).exists(), (
            f"{relative_path} should not exist in dry-run"
        )


def test_init_help():
    """--help shows all flags and descriptions."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "--force" in result.output
    assert "--dry-run" in result.output
    assert "--dir" in result.output


def test_help_shows_usage():
    """Top-level --help shows usage and init command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output


def test_init_prints_summary(tmp_path):
    """Output contains a summary line with file count."""
    result = runner.invoke(app, ["init", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "14 created" in result.output


def test_init_prints_all_paths(tmp_path):
    """Every file path appears in output."""
    result = runner.invoke(app, ["init", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    for relative_path in TEMPLATES:
        assert relative_path in result.output, f"Path {relative_path} not in output"


def test_init_creates_target_dir(tmp_path):
    """--dir with non-existing path creates the directory."""
    target = tmp_path / "new" / "nested" / "dir"
    assert not target.exists()
    result = runner.invoke(app, ["init", "--dir", str(target)])
    assert result.exit_code == 0
    assert target.is_dir()


def test_init_skips_summary_line(tmp_path):
    """Running twice shows skipped count in summary."""
    runner.invoke(app, ["init", "--dir", str(tmp_path)])
    result = runner.invoke(app, ["init", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "14 skipped" in result.output


def test_init_dry_run_file_count(tmp_path):
    """Dry run summary shows correct file count."""
    result = runner.invoke(app, ["init", "--dry-run", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "14 files would be created" in result.output


def test_init_file_content_matches_templates(tmp_path):
    """Created files have correct content from TEMPLATES."""
    runner.invoke(app, ["init", "--dir", str(tmp_path)])
    for relative_path, expected in TEMPLATES.items():
        full = tmp_path / relative_path
        assert full.read_text() == expected, f"{relative_path} content mismatch"
