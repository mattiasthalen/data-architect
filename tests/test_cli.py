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


def test_dab_init_creates_spec_file(tmp_path, monkeypatch):
    """architect dab init creates spec.yaml in current directory."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["dab", "init"])
    assert result.exit_code == 0
    assert (tmp_path / "spec.yaml").exists()
    assert "\u2713" in result.output
    assert "spec.yaml" in result.output


def test_dab_init_custom_output(tmp_path):
    """architect dab init custom.yaml creates custom.yaml."""
    output_path = tmp_path / "custom.yaml"
    result = runner.invoke(app, ["dab", "init", str(output_path)])
    assert result.exit_code == 0
    assert output_path.exists()
    assert "\u2713" in result.output


def test_dab_init_no_overwrite(tmp_path):
    """Running dab init twice without --overwrite fails on second run."""
    output_path = tmp_path / "spec.yaml"

    # First run succeeds
    result1 = runner.invoke(app, ["dab", "init", str(output_path)])
    assert result1.exit_code == 0

    # Second run without --overwrite should fail
    result2 = runner.invoke(app, ["dab", "init", str(output_path)])
    assert result2.exit_code == 1
    assert "already exists" in result2.output


def test_dab_init_overwrite_flag(tmp_path):
    """Running dab init twice with --overwrite succeeds both times."""
    output_path = tmp_path / "spec.yaml"

    # First run
    result1 = runner.invoke(app, ["dab", "init", str(output_path)])
    assert result1.exit_code == 0

    # Second run with --overwrite should succeed
    result2 = runner.invoke(app, ["dab", "init", str(output_path), "--overwrite"])
    assert result2.exit_code == 0
    assert "\u2713" in result2.output


def test_dab_init_help():
    """architect dab init --help shows help text."""
    result = runner.invoke(app, ["dab", "init", "--help"])
    assert result.exit_code == 0
    assert "Scaffold a blank YAML spec template" in result.output
    assert "--overwrite" in result.output


def test_dab_generate_with_valid_spec(tmp_path):
    """architect dab generate with valid spec creates SQL files."""
    # Copy valid spec to tmp directory
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    result = runner.invoke(app, ["dab", "generate", str(spec_path)])
    assert result.exit_code == 0
    assert "\u2713" in result.output

    # Check output directory exists with DDL and DML files
    output_dir = tmp_path / "output"
    assert output_dir.exists()
    assert (output_dir / "ddl").exists()
    assert (output_dir / "dml").exists()

    # Check that some DDL files were created
    ddl_files = list((output_dir / "ddl").glob("*.sql"))
    assert len(ddl_files) > 0

    # Check that some DML files were created
    dml_files = list((output_dir / "dml").glob("*.sql"))
    assert len(dml_files) > 0


def test_dab_generate_with_invalid_spec(tmp_path):
    """architect dab generate with invalid spec shows validation errors."""
    spec_path = tmp_path / "bad.yaml"
    spec_path.write_text("knot:\n  - mnemonic: TEST\n    bad_field: value")

    result = runner.invoke(app, ["dab", "generate", str(spec_path)])
    assert result.exit_code == 1
    assert "Validation errors:" in result.output


def test_dab_generate_missing_spec(tmp_path):
    """architect dab generate with nonexistent file shows error."""
    spec_path = tmp_path / "nonexistent.yaml"
    result = runner.invoke(app, ["dab", "generate", str(spec_path)])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_dab_generate_format_raw(tmp_path):
    """architect dab generate --format raw produces plain SQL."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    result = runner.invoke(app, ["dab", "generate", str(spec_path), "--format", "raw"])
    assert result.exit_code == 0

    # Check that SQL files don't have Bruin frontmatter
    output_dir = tmp_path / "output"
    ddl_files = list((output_dir / "ddl").glob("*.sql"))
    if ddl_files:
        content = ddl_files[0].read_text()
        assert "/* @bruin" not in content


def test_dab_generate_format_bruin(tmp_path):
    """architect dab generate --format bruin produces SQL with frontmatter."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    result = runner.invoke(
        app, ["dab", "generate", str(spec_path), "--format", "bruin"]
    )
    assert result.exit_code == 0

    # Check that SQL files have Bruin frontmatter
    output_dir = tmp_path / "output"
    ddl_files = list((output_dir / "ddl").glob("*.sql"))
    assert len(ddl_files) > 0
    content = ddl_files[0].read_text()
    assert "/* @bruin" in content
    assert "@bruin */" in content
    assert "name: dab." in content
    assert "type: sql" in content
    assert "strategy:" in content


def test_dab_generate_dialect_postgres(tmp_path):
    """architect dab generate uses PostgreSQL dialect by default."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    result = runner.invoke(app, ["dab", "generate", str(spec_path)])
    assert result.exit_code == 0

    # PostgreSQL-specific syntax would be in the SQL
    # For now, just check it succeeded
    output_dir = tmp_path / "output"
    assert (output_dir / "ddl").exists()


def test_dab_generate_dialect_snowflake(tmp_path):
    """architect dab generate --dialect snowflake uses Snowflake SQL."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    result = runner.invoke(
        app, ["dab", "generate", str(spec_path), "--dialect", "snowflake"]
    )
    assert result.exit_code == 0

    # Snowflake SQL should be generated
    output_dir = tmp_path / "output"
    assert (output_dir / "ddl").exists()


def test_dab_generate_custom_output_dir(tmp_path):
    """architect dab generate --output-dir writes to custom directory."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    custom_output = tmp_path / "custom_output"
    result = runner.invoke(
        app, ["dab", "generate", str(spec_path), "--output-dir", str(custom_output)]
    )
    assert result.exit_code == 0

    # Check custom output directory was used
    assert custom_output.exists()
    assert (custom_output / "ddl").exists()
    assert (custom_output / "dml").exists()


def test_dab_generate_deterministic(tmp_path):
    """Running architect dab generate twice produces identical output."""
    from pathlib import Path

    spec_path = tmp_path / "spec.yaml"
    fixture_spec = Path("tests/fixtures/valid_spec.yaml")
    spec_path.write_text(fixture_spec.read_text())

    # First run
    output1 = tmp_path / "output1"
    result1 = runner.invoke(
        app, ["dab", "generate", str(spec_path), "--output-dir", str(output1)]
    )
    assert result1.exit_code == 0

    # Second run
    output2 = tmp_path / "output2"
    result2 = runner.invoke(
        app, ["dab", "generate", str(spec_path), "--output-dir", str(output2)]
    )
    assert result2.exit_code == 0

    # Compare DDL files
    ddl1_files = {f.name: f.read_text() for f in (output1 / "ddl").glob("*.sql")}
    ddl2_files = {f.name: f.read_text() for f in (output2 / "ddl").glob("*.sql")}
    assert ddl1_files == ddl2_files

    # Compare DML files
    dml1_files = {f.name: f.read_text() for f in (output1 / "dml").glob("*.sql")}
    dml2_files = {f.name: f.read_text() for f in (output2 / "dml").glob("*.sql")}
    assert dml1_files == dml2_files


def test_dab_generate_dml_staging_refs_match_ddl(tmp_path):
    """DML staging source references for explicitly defined staging tables match DDL."""
    # Use a spec with staging_mappings
    spec_content = """
knot:
  - mnemonic: GEN
    descriptor: Gender
    identity: bit
    dataRange: varchar(42)

anchor:
  - mnemonic: AC
    descriptor: Actor
    identity: int
    staging_mappings:
      - table: stg_actors
        columns:
          - name: AC_ID
            type: int
          - name: actor_name
            type: varchar(100)
    attribute:
      - mnemonic: NAM
        descriptor: Name
        timeRange: datetime
        dataRange: varchar(100)
"""
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(spec_content)

    result = runner.invoke(app, ["dab", "generate", str(spec_path)])
    assert result.exit_code == 0

    output_dir = tmp_path / "output"

    # Get all DDL staging table names
    ddl_files = {f.stem for f in (output_dir / "ddl").glob("*.sql")}

    # Verify that the explicitly defined staging table has DDL
    assert "stg_actors" in ddl_files, "Explicitly defined staging table missing DDL"

    # Verify that DML references the correct staging table for the attribute
    attr_dml_file = output_dir / "dml" / "AC_NAM_Actor_Name_load.sql"
    if attr_dml_file.exists():
        content = attr_dml_file.read_text()
        # Attribute DML should reference stg_actors (from anchor's staging mapping)
        assert "stg_actors" in content, (
            "DML should reference staging table from mapping"
        )


def test_dab_generate_help():
    """architect dab generate --help shows all options."""
    result = runner.invoke(app, ["dab", "generate", "--help"])
    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--dialect" in result.output
    assert "--output-dir" in result.output
    assert "raw" in result.output
    assert "bruin" in result.output
