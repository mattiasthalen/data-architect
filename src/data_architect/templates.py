"""File content definitions for all scaffolded files."""

TEMPLATES: dict[str, str] = {
    ".opencode/agents/data-architect.md": (
        "---\n"
        "description: Entry point and design authority for data warehouse modeling\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/agents/data-engineer.md": (
        "---\n"
        "description: Physical modeling specialist for performance and orchestration\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/agents/analytics-engineer.md": (
        "---\n"
        "description: DAR layer perspective on warehouse consumption\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/agents/system-analyst.md": (
        "---\n"
        "description: Source system expert for technical data understanding\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/agents/business-analyst.md": (
        "---\n"
        "description: Business domain expert for requirements and data meaning\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/agents/veteran-reviewer.md": (
        "---\n"
        "description: Battle-scarred DW engineer who critiques for anti-patterns\n"
        "model: anthropic:claude-sonnet-4-20250514\n"
        "---\n"
        "<!-- TODO: Full prompt in Phase 3 -->\n"
    ),
    ".opencode/skills/da-start/SKILL.md": (
        "---\n"
        "description: Start a data warehouse design session\n"
        "---\n"
        "<!-- TODO: Full skill definition in Phase 3 -->\n"
    ),
    "AGENTS.md": (
        "# Shared Agent Context\n"
        "\n"
        "<!-- TODO: ADSS and Anchor Modeling methodology context in Phase 3 -->\n"
    ),
    "opencode.json": (
        "{\n"
        '  "name": "data-architect",\n'
        '  "agents": {\n'
        '    "default": "data-architect"\n'
        "  }\n"
        "}\n"
    ),
}
