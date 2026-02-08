# Phase 3: Agent Definitions + OpenCode Integration - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

`architect init` scaffolds all 6 agent Markdown files (with YAML frontmatter), AGENTS.md, opencode.json, skills, and example spec schemas into `.opencode/` — structurally valid and recognized by OpenCode as a working agent team. Agents have real prompts with role + methodology context, but deep CLP debate protocol is Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Agent prompt depth
- Role + methodology intro: each agent gets a real prompt with role description and brief ADSS/Anchor Modeling context
- Cross-references: agents mention each other by name (e.g., "hand off to @business-analyst") — team awareness from Phase 3
- Veteran Reviewer includes a basic anti-pattern checklist (5-10 items) — gives it teeth before Phase 4 deepens it
- Deep CLP debate protocol and methodology-deep behavioral prompts are deferred to Phase 4

### Skill design
- Full toolkit scaffolded: `/da:start`, `/da:review`, `/da:status`, `/da:export`
- All skills route through Data Architect as single orchestration point — no direct agent invocation from skills
- `/da:export` writes specs to a fixed, predictable location (not user-chosen)

### AGENTS.md shared context
- Full methodology primer: comprehensive ADSS three-layer architecture, Anchor Modeling concepts (anchors, attributes, ties, knots, nexuses), CLP stages, USS basics (~500-1000 words)
- Basic team interaction rules included: debate expectations, escalation path, user as final authority
- Naming conventions defined and enforced:
  - `anchor__<entity>` (e.g., `anchor__order`)
  - `anchor__<entity>__<attribute>` (e.g., `anchor__order__order_date`)
  - `tie__<from>__<verb>__<to>` — always many-to-one (e.g., `tie__order__placed_by__customer`)
  - `knot__<name>` (e.g., `knot__currency`)
  - `nexus__<name>` (e.g., `nexus__order_line`)
  - All snake_case, double underscore `__` as separator, NO mnemonics — full readable names

### opencode.json configuration
- Scaffolds with placeholder/no model assignments — agents are NOT pre-assigned to specific models
- Three-tier model profile system (mirrors GSD's set-profile): budget / standard / high
- Data Architect prompts user to choose tier on first interaction, then writes config
- `architect init` does NOT take a --tier flag

### Claude's Discretion
- Whether agent prompts include inline YAML spec examples or just reference the separate schema files
- Skill prompt completeness level (structural + basic instructions vs fully functional)
- Tool permissions per agent in opencode.json (read/write/shell access)

</decisions>

<specifics>
## Specific Ideas

- Mirror GSD's tier system for model profile selection — user-facing simplicity, three clear tiers
- Naming convention is opinionated and non-negotiable: no mnemonics, snake_case, double underscore separators, readable names
- Ties are always many-to-one — this is a modeling constraint, not just naming

</specifics>

<deferred>
## Deferred Ideas

- Claude Code support (scaffolding into `.claude/` alongside OpenCode definitions) — future phase
- Per-agent model overrides (e.g., Opus for Architect, Sonnet for others within a tier) — could be a Phase 4 enhancement

</deferred>

---

*Phase: 03-agent-definitions-opencode-integration*
*Context gathered: 2026-02-07*
