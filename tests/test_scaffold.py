"""Tests for the scaffold engine — TDD RED phase."""

from data_architect.scaffold import ScaffoldAction, ScaffoldResult, scaffold
from data_architect.templates import TEMPLATES


def test_manifest_has_expected_file_count():
    """TEMPLATES has exactly 14 entries."""
    assert len(TEMPLATES) == 14


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
    assert (tmp_path / ".opencode" / "skills" / "da-review").is_dir()
    assert (tmp_path / ".opencode" / "skills" / "da-status").is_dir()
    assert (tmp_path / ".opencode" / "skills" / "da-export").is_dir()
    assert (tmp_path / ".data-architect" / "specs" / "examples").is_dir()


def test_scaffold_result_types(tmp_path):
    """scaffold() returns list of ScaffoldResult with correct types."""
    results = scaffold(tmp_path)
    assert isinstance(results, list)
    for result in results:
        assert isinstance(result, ScaffoldResult)
        assert isinstance(result.action, ScaffoldAction)
        assert isinstance(result.path, str)
        assert isinstance(result.reason, str)


def test_all_skill_files_have_yaml_frontmatter():
    """Each skill SKILL.md file has complete YAML frontmatter."""
    skill_files = [p for p in TEMPLATES if "/skills/" in p]
    assert len(skill_files) == 4
    for path in skill_files:
        content = TEMPLATES[path]
        assert content.startswith("---"), f"{path} missing frontmatter opening"
        # Check for key frontmatter fields
        assert "name:" in content, f"{path} missing name field"
        assert "description:" in content, f"{path} missing description field"
        assert "agent: data-architect" in content, f"{path} missing agent field"


def test_agents_have_no_model_field():
    """Agent files should not specify model field in frontmatter."""
    agent_files = [p for p in TEMPLATES if ".opencode/agents/" in p]
    for path in agent_files:
        content = TEMPLATES[path]
        # Extract frontmatter (between first --- and second ---)
        lines = content.split("\n")
        if lines[0] == "---":
            frontmatter_lines = []
            for i in range(1, len(lines)):
                if lines[i] == "---":
                    break
                frontmatter_lines.append(lines[i])
            frontmatter = "\n".join(frontmatter_lines)
            assert "model:" not in frontmatter, f"{path} should not specify model"


def test_agents_have_cross_references():
    """Agent prompts reference other agents via @mentions."""
    agent_files = [p for p in TEMPLATES if ".opencode/agents/" in p]
    for path in agent_files:
        content = TEMPLATES[path]
        # Extract body (after second ---)
        parts = content.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            # Check if body contains at least one @ mention
            # (agents should reference each other for coordination)
            has_mention = "@" in body and any(
                agent in body
                for agent in [
                    "data-architect",
                    "business-analyst",
                    "system-analyst",
                    "data-engineer",
                    "analytics-engineer",
                    "veteran-reviewer",
                ]
            )
            assert has_mention, f"{path} should reference other agents via @mentions"


def test_agents_md_has_naming_conventions():
    """AGENTS.md includes naming convention examples."""
    agents_md = TEMPLATES.get("AGENTS.md", "")
    assert "anchor__" in agents_md, "AGENTS.md missing anchor__ examples"
    assert "tie__" in agents_md, "AGENTS.md missing tie__ examples"
    assert "knot__" in agents_md, "AGENTS.md missing knot__ examples"


def test_no_todo_stubs_remain():
    """No TEMPLATES contain TODO placeholders from earlier phases."""
    for path, content in TEMPLATES.items():
        assert "<!-- TODO:" not in content, f"{path} contains TODO stub"


def test_agents_md_has_decision_trees():
    """AGENTS.md template contains decision tree sections."""
    agents_md = TEMPLATES.get("AGENTS.md", "")
    assert "Decision Tree" in agents_md, "AGENTS.md missing Decision Tree"
    assert "Identity Check" in agents_md, "AGENTS.md missing Identity Check"
    assert "Historization Decision" in agents_md, (
        "AGENTS.md missing Historization Decision"
    )
    assert "Tie vs Nexus" in agents_md, "AGENTS.md missing Tie vs Nexus"


def test_agents_md_has_historization_default():
    """AGENTS.md template contains default historization guidance."""
    agents_md = TEMPLATES.get("AGENTS.md", "")
    # Check that guidance mentions defaulting to historized: true
    assert "default" in agents_md.lower(), "AGENTS.md missing default guidance"
    assert "historized" in agents_md, "AGENTS.md missing historized keyword"
    assert "historized: true" in agents_md, "AGENTS.md missing 'historized: true'"


def test_data_architect_has_clp_protocols():
    """Data Architect template contains CLP stage protocols."""
    da_md = TEMPLATES.get(".opencode/agents/data-architect.md", "")
    assert "Conceptual Stage" in da_md, "Data Architect missing Conceptual Stage"
    assert "Logical Stage" in da_md, "Data Architect missing Logical Stage"
    assert "Physical Stage" in da_md, "Data Architect missing Physical Stage"


def test_data_architect_has_debate_protocol():
    """Data Architect template contains debate protocol with bounded iteration."""
    da_md = TEMPLATES.get(".opencode/agents/data-architect.md", "")
    assert "Debate Protocol" in da_md, "Data Architect missing Debate Protocol"
    assert "Convergence" in da_md, "Data Architect missing Convergence section"
    assert "ESCALATE" in da_md, "Data Architect missing ESCALATE directive"
    assert "5 rounds" in da_md, "Data Architect missing 5 rounds iteration limit"
