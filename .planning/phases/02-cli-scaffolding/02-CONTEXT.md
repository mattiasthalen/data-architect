# Phase 2: CLI Scaffolding — Context

## Decisions

- **CLI framework**: Typer (first runtime dependency)
- **Placeholder content**: Minimal stubs — valid structure with TODO bodies, real content comes in Phase 3
- **File manifest**: Full set scaffolded in Phase 2 (all 6 agents, skills, AGENTS.md, opencode.json)
- **Flags**: Only what roadmap specifies — `--force`, `--dry-run`, `--dir`, `--help` (no extras)
- **Output format**: Symbols (e.g., `✓ Created .opencode/agents/data-architect.md`)

## Deferred Ideas

- Verbose/quiet flags
- Color customization flags

## Claude's Discretion

- Internal module structure (how to split scaffold logic, templates, CLI wiring)
- Pure function signatures and return types
- Test organization and fixture design
- Exact symbol choices for output (✓, ⚠, etc.)
