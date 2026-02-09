"""Tests for output formatters (raw and Bruin)."""

from pathlib import Path

from data_architect.generation.formatters import (
    format_bruin,
    format_raw,
    write_output,
)


def test_format_raw_returns_sql_with_trailing_newline() -> None:
    """Raw format should return SQL with a trailing newline."""
    sql = "SELECT 1"
    result = format_raw(sql)
    assert result == "SELECT 1\n"
    assert result.endswith("\n")


def test_format_raw_preserves_existing_newline() -> None:
    """Raw format should not add extra newlines if already present."""
    sql = "SELECT 1\n"
    result = format_raw(sql)
    assert result == "SELECT 1\n"
    assert result.count("\n") == 1


def test_format_bruin_has_frontmatter() -> None:
    """Bruin format should include frontmatter delimiters."""
    sql = "SELECT 1"
    result = format_bruin(sql, "AC_Actor", "ddl", False)
    assert "/* @bruin" in result
    assert "@bruin */" in result


def test_format_bruin_entity_name() -> None:
    """Bruin frontmatter should include entity name in asset name."""
    sql = "SELECT 1"
    result = format_bruin(sql, "AC_Actor", "ddl", False)
    assert "name: dab.AC_Actor" in result


def test_format_bruin_historized_uses_merge() -> None:
    """DML with historized entity should use merge strategy."""
    sql = "MERGE INTO foo"
    result = format_bruin(sql, "AC_NAM", "dml", is_historized=True)
    assert "strategy: merge" in result


def test_format_bruin_static_uses_create_replace() -> None:
    """DML with static entity should use create+replace strategy."""
    sql = "INSERT INTO foo"
    result = format_bruin(sql, "AC_NAM", "dml", is_historized=False)
    assert "strategy: create+replace" in result


def test_format_bruin_ddl_uses_create_replace() -> None:
    """DDL files should always use create+replace strategy."""
    sql = "CREATE TABLE foo"
    result = format_bruin(sql, "AC_Actor", "ddl", is_historized=False)
    assert "strategy: create+replace" in result

    # Even if is_historized=True, DDL should still use create+replace
    result_hist = format_bruin(sql, "AC_Actor", "ddl", is_historized=True)
    assert "strategy: create+replace" in result_hist


def test_write_output_creates_files(tmp_path: Path) -> None:
    """write_output should create files in the correct directory."""
    files = {
        "table1.sql": "SELECT 1",
        "table2.sql": "SELECT 2",
    }

    written = write_output(files, tmp_path, format_raw, "ddl")

    assert len(written) == 2
    assert (tmp_path / "ddl" / "table1.sql").exists()
    assert (tmp_path / "ddl" / "table2.sql").exists()
    assert (tmp_path / "ddl" / "table1.sql").read_text() == "SELECT 1\n"


def test_write_output_creates_subdirs(tmp_path: Path) -> None:
    """write_output should create ddl/ and dml/ subdirectories."""
    files_ddl = {"table.sql": "CREATE TABLE foo"}
    files_dml = {"load.sql": "MERGE INTO foo"}

    write_output(files_ddl, tmp_path, format_raw, "ddl")
    write_output(files_dml, tmp_path, format_raw, "dml")

    assert (tmp_path / "ddl").is_dir()
    assert (tmp_path / "dml").is_dir()
    assert (tmp_path / "ddl" / "table.sql").exists()
    assert (tmp_path / "dml" / "load.sql").exists()


def test_write_output_deterministic(tmp_path: Path) -> None:
    """Two writes should produce identical files."""
    files = {
        "z_last.sql": "SELECT 3",
        "a_first.sql": "SELECT 1",
        "m_middle.sql": "SELECT 2",
    }

    # First write
    written1 = write_output(files, tmp_path / "run1", format_raw, "ddl")
    content1 = {p.name: p.read_text() for p in written1}

    # Second write
    written2 = write_output(files, tmp_path / "run2", format_raw, "ddl")
    content2 = {p.name: p.read_text() for p in written2}

    # Should be identical
    assert content1 == content2

    # Should be sorted by filename
    assert written1[0].name == "a_first.sql"
    assert written1[1].name == "m_middle.sql"
    assert written1[2].name == "z_last.sql"


def test_write_output_with_bruin_formatter(tmp_path: Path) -> None:
    """write_output should work with Bruin formatter."""
    files = {"AC_Actor.sql": "CREATE TABLE AC_Actor"}

    def bruin_formatter(sql: str) -> str:
        return format_bruin(sql, "AC_Actor", "ddl", False)

    write_output(files, tmp_path, bruin_formatter, "ddl")

    content = (tmp_path / "ddl" / "AC_Actor.sql").read_text()
    assert "/* @bruin" in content
    assert "name: dab.AC_Actor" in content
    assert "CREATE TABLE AC_Actor" in content
