"""Tests for the scaffold engine — TDD RED phase."""

from data_architect.scaffold import ScaffoldAction, ScaffoldResult, scaffold
from data_architect.templates import TEMPLATES


def test_manifest_has_expected_file_count():
    """TEMPLATES has exactly 11 entries."""
    assert len(TEMPLATES) == 11


def test_all_agent_files_have_yaml_frontmatter():
    """Each agent .md file starts with YAML frontmatter delimiter."""
    agent_files = [p for p in TEMPLATES if ".opencode/agents/" in p]
    assert len(agent_files) == 6
    for path in agent_files:
        assert TEMPLATES[path].startswith("---"), f"{path} missing frontmatter"


def test_scaffold_creates_all_files_in_empty_dir(tmp_path):
    """scaffold() in empty dir returns CREATED for every file."""
    results = scaffold(tmp_path)
    assert len(results) == len(TEMPLATES)
    for result in results:
        assert result.action == ScaffoldAction.CREATED, (
            f"{result.path} was {result.action}, expected CREATED"
        )


def test_scaffold_files_exist_on_disk(tmp_path):
    """After scaffold(), every file exists with expected content."""
    scaffold(tmp_path)
    for relative_path, expected_content in TEMPLATES.items():
        full_path = tmp_path / relative_path
        assert full_path.exists(), f"{relative_path} not found on disk"
        assert full_path.read_text() == expected_content, (
            f"{relative_path} content mismatch"
        )


def test_scaffold_skips_existing_files(tmp_path):
    """Pre-create one file; SKIPPED for it, CREATED for rest."""
    first_path = next(iter(TEMPLATES))
    full = tmp_path / first_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("existing content")

    results = scaffold(tmp_path)
    result_map = {r.path: r for r in results}
    skipped = result_map[str(tmp_path / first_path)]
    assert skipped.action == ScaffoldAction.SKIPPED

    created_count = sum(1 for r in results if r.action == ScaffoldAction.CREATED)
    assert created_count == len(TEMPLATES) - 1


def test_scaffold_skipped_file_not_overwritten(tmp_path):
    """Pre-create file with custom content; scaffold() preserves it."""
    first_path = next(iter(TEMPLATES))
    full = tmp_path / first_path
    full.parent.mkdir(parents=True, exist_ok=True)
    custom_content = "my custom content"
    full.write_text(custom_content)

    scaffold(tmp_path)
    assert full.read_text() == custom_content


def test_scaffold_force_overwrites_existing(tmp_path):
    """Pre-create file; force=True overwrites with template content."""
    first_path = next(iter(TEMPLATES))
    full = tmp_path / first_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text("old content")

    results = scaffold(tmp_path, force=True)
    result_map = {r.path: r for r in results}
    overwritten = result_map[str(tmp_path / first_path)]
    assert overwritten.action == ScaffoldAction.CREATED
    assert full.read_text() == TEMPLATES[first_path]


def test_scaffold_dry_run_no_files_written(tmp_path):
    """dry_run=True returns WOULD_CREATE for all, writes nothing."""
    results = scaffold(tmp_path, dry_run=True)
    assert len(results) == len(TEMPLATES)
    for result in results:
        assert result.action == ScaffoldAction.WOULD_CREATE, (
            f"{result.path} was {result.action}, expected WOULD_CREATE"
        )
    for relative_path in TEMPLATES:
        assert not (tmp_path / relative_path).exists(), (
            f"{relative_path} should not exist in dry-run mode"
        )


def test_scaffold_target_dir(tmp_path):
    """scaffold(target_dir=custom) creates files under custom."""
    custom = tmp_path / "my_project"
    custom.mkdir()
    scaffold(custom)
    for relative_path in TEMPLATES:
        assert (custom / relative_path).exists(), (
            f"{relative_path} not under custom target dir"
        )


def test_scaffold_creates_subdirectories(tmp_path):
    """scaffold() creates nested directories automatically."""
    scaffold(tmp_path)
    assert (tmp_path / ".opencode" / "agents").is_dir()
    assert (tmp_path / ".opencode" / "skills" / "da-start").is_dir()


def test_scaffold_result_types(tmp_path):
    """scaffold() returns list of ScaffoldResult with correct types."""
    results = scaffold(tmp_path)
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, ScaffoldResult)
        assert isinstance(result.action, ScaffoldAction)
        assert isinstance(result.path, str)
        assert isinstance(result.reason, str)
