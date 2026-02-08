# Phase 3: Agent Definitions + OpenCode Integration - Research

**Researched:** 2026-02-08
**Domain:** OpenCode multi-agent platform, agent configuration, skill scaffolding
**Confidence:** MEDIUM

## Summary

Phase 3 scaffolds six agent definitions, shared methodology context (AGENTS.md), OpenCode configuration (opencode.json), four skills (/da:start, /da:review, /da:status, /da:export), and example YAML spec schemas. The scaffolding follows OpenCode's agent/skill conventions and mirrors existing Phase 2 patterns (template dict + scaffold() function).

OpenCode (fork of Claude Code) uses markdown files with YAML frontmatter for agent definitions in `.opencode/agents/`, skill definitions in `.opencode/skills/<name>/SKILL.md`, and project-level shared context in `AGENTS.md`. Configuration goes in `opencode.json` at project root. Agents invoke each other via @mention syntax, with a primary agent orchestrating specialized subagents.

The research confirms OpenCode uses the Agent Skills open standard (agentskills.io), which was released by Anthropic in December 2025 and adopted by OpenAI for Codex/ChatGPT. This means the file formats are stable and widely supported.

**Primary recommendation:** Use template expansion pattern from Phase 2 (TEMPLATES dict), add full agent prompts and skill instructions as multi-line strings, leverage OpenCode's explicit permission model for tool restrictions.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Agent prompt depth:**
- Role + methodology intro: each agent gets a real prompt with role description and brief ADSS/Anchor Modeling context
- Cross-references: agents mention each other by name (e.g., "hand off to @business-analyst") — team awareness from Phase 3
- Veteran Reviewer includes a basic anti-pattern checklist (5-10 items) — gives it teeth before Phase 4 deepens it
- Deep CLP debate protocol and methodology-deep behavioral prompts are deferred to Phase 4

**Skill design:**
- Full toolkit scaffolded: `/da:start`, `/da:review`, `/da:status`, `/da:export`
- All skills route through Data Architect as single orchestration point — no direct agent invocation from skills
- `/da:export` writes specs to a fixed, predictable location (not user-chosen)

**AGENTS.md shared context:**
- Full methodology primer: comprehensive ADSS three-layer architecture, Anchor Modeling concepts (anchors, attributes, ties, knots, nexuses), CLP stages, USS basics (~500-1000 words)
- Basic team interaction rules included: debate expectations, escalation path, user as final authority
- Naming conventions defined and enforced:
  - `anchor__<entity>` (e.g., `anchor__order`)
  - `anchor__<entity>__<attribute>` (e.g., `anchor__order__order_date`)
  - `tie__<from>__<verb>__<to>` — always many-to-one (e.g., `tie__order__placed_by__customer`)
  - `knot__<name>` (e.g., `knot__currency`)
  - `nexus__<name>` (e.g., `nexus__order_line`)
  - All snake_case, double underscore `__` as separator, NO mnemonics — full readable names

**opencode.json configuration:**
- Scaffolds with placeholder/no model assignments — agents are NOT pre-assigned to specific models
- Three-tier model profile system (mirrors GSD's set-profile): budget / standard / high
- Data Architect prompts user to choose tier on first interaction, then writes config
- `architect init` does NOT take a --tier flag

### Claude's Discretion

- Whether agent prompts include inline YAML spec examples or just reference the separate schema files
- Skill prompt completeness level (structural + basic instructions vs fully functional)
- Tool permissions per agent in opencode.json (read/write/shell access)

### Deferred Ideas (OUT OF SCOPE)

- Claude Code support (scaffolding into `.claude/` alongside OpenCode definitions) — future phase
- Per-agent model overrides (e.g., Opus for Architect, Sonnet for others within a tier) — could be a Phase 4 enhancement
</user_constraints>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| OpenCode | Latest 2026 | Multi-agent coding platform (Claude Code fork) | User's chosen platform; uses Agent Skills open standard |
| Agent Skills spec | 1.0 (Dec 2025) | Open standard for agent/skill definitions | Cross-platform (Anthropic, OpenAI), stable format |
| Python built-ins | 3.13+ | String templates, file I/O, Path operations | No dependencies for scaffolding |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| yaml (PyYAML) | 6.0.2+ | YAML parsing/generation (if needed) | Only if programmatic YAML manipulation required; template strings sufficient for scaffolding |
| gray-matter (Node.js) | Latest | YAML frontmatter parsing | If switching to Node.js for scaffolding |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Template strings | Jinja2/Mako | More power (conditionals, loops) but unnecessary dependency for static content |
| Python scaffolding | Node.js + inquirer.js | Node.js has richer CLI scaffolding ecosystem but adds language boundary |

**Installation:**

No additional dependencies required. Python 3.13 built-ins handle all scaffolding needs.

## Architecture Patterns

### Recommended Project Structure (after `architect init`)

```
project-root/
├── .opencode/
│   ├── agents/
│   │   ├── data-architect.md           # Primary agent, entry point
│   │   ├── business-analyst.md         # Subagent
│   │   ├── system-analyst.md           # Subagent
│   │   ├── data-engineer.md            # Subagent
│   │   ├── analytics-engineer.md       # Subagent
│   │   └── veteran-reviewer.md         # Subagent
│   └── skills/
│       ├── da-start/
│       │   ├── SKILL.md                # /da:start command
│       │   └── examples/               # Optional: example inputs
│       ├── da-review/
│       │   └── SKILL.md                # /da:review command
│       ├── da-status/
│       │   └── SKILL.md                # /da:status command
│       └── da-export/
│           └── SKILL.md                # /da:export command
├── AGENTS.md                            # Shared methodology context
└── opencode.json                        # Platform configuration
```

### Pattern 1: Agent Definition with YAML Frontmatter

**What:** Markdown file with YAML frontmatter configuring agent behavior, followed by system prompt in markdown body

**When to use:** Every agent definition in `.opencode/agents/`

**Example:**

```markdown
---
description: Entry point and design authority for data warehouse modeling
mode: primary
model: anthropic/claude-sonnet-4-20250514
temperature: 0.3
tools:
  read: true
  write: true
  bash: ask
permissions:
  edit: ask
  Task: allow
---

# Data Architect

You are the Data Architect, the entry point and orchestrator for all data warehouse modeling work...

## Your Role

- Lead the CLP (Curate, Leverage, Prioritize) debate process
- Synthesize input from specialists: @business-analyst, @system-analyst, @data-engineer, @analytics-engineer
- Ensure final design adheres to Anchor Modeling principles
- Present final design to @veteran-reviewer for critique

## Methodology Context

See AGENTS.md for full ADSS and Anchor Modeling methodology.

...
```

**Source:** [OpenCode Agents Documentation](https://opencode.ai/docs/agents/)

### Pattern 2: Skill Definition with Arguments

**What:** Skill files in `.opencode/skills/<name>/SKILL.md` with YAML frontmatter and markdown instructions, supporting dynamic arguments via `$ARGUMENTS` placeholder

**When to use:** All custom slash commands

**Example:**

```markdown
---
name: da-start
description: Start a data warehouse design session for a new domain
disable-model-invocation: true
context: fork
agent: data-architect
---

# Start Data Warehouse Design Session

Initialize a new data warehouse design session for domain: $ARGUMENTS

## Your Task

1. Greet the user and confirm the domain: "$ARGUMENTS"
2. Explain the CLP process (Curate, Leverage, Prioritize)
3. Ask initial discovery questions:
   - What business questions need answering?
   - What source systems exist?
   - What are the key business entities?
4. Document responses in session context
5. When ready, invoke @business-analyst and @system-analyst to begin requirements gathering

Route all work through your own context — do not invoke other agents directly from this skill.
```

**Source:** [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

### Pattern 3: Shared Methodology Context (AGENTS.md)

**What:** Single markdown file at project root providing shared context loaded into all agent conversations

**When to use:** Methodology, naming conventions, team interaction rules — anything all agents need to know

**Example:**

```markdown
# Shared Agent Context

This file provides shared methodology context for all data warehouse modeling agents.

## ADSS Three-Layer Architecture

ADSS (Agile Data Storage Solution) organizes the warehouse into three layers:

1. **DAB (Data Acquisition & Baseline)**: Raw data ingestion, minimal transformation, audit trails
2. **DAR (Data Analysis & Refinement)**: Business-aligned models, historization, derived metrics
3. **DAP (Data Access & Presentation)**: Consumption layer, reports, dashboards, APIs

The DAB layer uses Anchor Modeling to capture source data in a time-variant, highly normalized format...

## Anchor Modeling Core Concepts

- **Anchor**: Immutable entity identity (e.g., `anchor__customer`)
- **Attribute**: Historized property of an anchor (e.g., `anchor__customer__name`)
- **Tie**: Many-to-one relationship between anchors (e.g., `tie__order__placed_by__customer`)
- **Knot**: Shared reference data (e.g., `knot__currency`)
- **Nexus**: Many-to-many intersection (e.g., `nexus__order_line`)

## Naming Conventions

All database objects MUST follow these conventions:

- `anchor__<entity>` — e.g., `anchor__order`
- `anchor__<entity>__<attribute>` — e.g., `anchor__order__order_date`
- `tie__<from>__<verb>__<to>` — e.g., `tie__order__placed_by__customer` (always many-to-one)
- `knot__<name>` — e.g., `knot__currency`
- `nexus__<name>` — e.g., `nexus__order_line`

**Rules:**
- snake_case only
- Double underscore `__` as separator
- NO mnemonics (no abbreviations like "cust" for "customer")
- Full, readable names

...
```

**Source:** [OpenCode Rules/AGENTS.md Documentation](https://opencode.ai/docs/rules/)

### Pattern 4: Minimal opencode.json Configuration

**What:** JSON config file at project root with minimal scaffolded defaults, allowing user/agent to populate model selections later

**When to use:** Always scaffold this; agents populate tier-specific models on first interaction

**Example:**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "name": "data-architect",
  "default_agent": "data-architect",
  "agents": {
    "data-architect": {
      "mode": "primary"
    }
  },
  "instructions": ["AGENTS.md"],
  "autoupdate": true
}
```

**Source:** [OpenCode Config Documentation](https://opencode.ai/docs/config/)

### Pattern 5: Orchestration Through Primary Agent

**What:** Skills invoke the primary agent (`data-architect`), not subagents directly; primary agent orchestrates team via @mentions

**When to use:** All `/da:*` skills

**Why:** Maintains single entry point, ensures consistent debate flow, avoids skill-to-subagent direct coupling

**Example:**

```markdown
# /da:start skill

## Your Task

1. Acknowledge the user's domain request
2. Begin discovery with @business-analyst
3. Synthesize findings and propose next steps

Do NOT directly invoke @system-analyst or other specialists — route through your normal orchestration flow.
```

### Anti-Patterns to Avoid

- **Pre-assigning models in scaffolded agent files:** User hasn't chosen tier yet; leave model field empty or use placeholder. Data Architect prompts for tier on first interaction.
- **Skills invoking subagents directly:** Breaks orchestration model; skills should invoke primary agent (data-architect) only, who then coordinates team.
- **Hardcoding paths in `/da:export`:** Spec output location should be predictable but not user-configurable in Phase 3 (e.g., always write to `.data-architect/specs/`).
- **Mixing Claude Code and OpenCode conventions:** Phase 3 targets OpenCode only; `.claude/agents/` is out of scope (deferred idea).
- **Deep prompts in Phase 3:** User explicitly deferred "deep CLP debate protocol" to Phase 4; keep prompts structural with role + brief methodology, not behavioral depth.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML frontmatter parsing | Custom regex parser | Template strings for generation; gray-matter/PyYAML if parsing needed | Frontmatter spec is finicky (delimiters, nested objects); established libraries handle edge cases |
| CLI prompting/interaction | Raw input() calls | inquirer (Python) or built-in input() with validation wrapper | User decisions need validation; GSD uses simple input() + gsd-tools.js for state writes, mirror that |
| Agent Skills specification | Custom format | Agent Skills open standard (agentskills.io) | Cross-platform standard (Anthropic + OpenAI), stable since Dec 2025 |
| Multi-agent orchestration | Custom message passing | OpenCode's @mention system + Task tool | Platform provides routing, context management, permission controls |

**Key insight:** Scaffolding is template expansion (strings → files), not runtime behavior. Don't build CLI frameworks or agent systems; generate static files that OpenCode/Python runtime consumes.

## Common Pitfalls

### Pitfall 1: Model Assignment Before User Choice

**What goes wrong:** Scaffolding hardcodes model assignments (e.g., `model: anthropic/claude-sonnet-4-20250514`) in agent files, but user hasn't chosen budget/standard/high tier yet.

**Why it happens:** Templates show model field in examples; easy to assume it's required at init time.

**How to avoid:** Omit model field from scaffolded agent YAML frontmatter, OR use a comment placeholder like `# model: <set by tier choice>`. Data Architect agent prompts user for tier on first `/da:start` invocation, then writes models to opencode.json or agent files.

**Warning signs:** If `architect init` asks for `--tier` flag, you've fallen into this trap. User decision deferred until first interaction.

### Pitfall 2: Skills Invoking Subagents Directly

**What goes wrong:** Skill instructions say "invoke @business-analyst to gather requirements", bypassing the Data Architect orchestration layer.

**Why it happens:** Shorter path; seems more efficient than routing through primary agent.

**How to avoid:** Skills should invoke `@data-architect` (primary agent) or run in forked context with `agent: data-architect`. The Data Architect then delegates to specialists. User explicitly requires "all skills route through Data Architect as single orchestration point."

**Warning signs:** If skill instructions contain `@business-analyst` or `@system-analyst` mentions, red flag.

### Pitfall 3: Verbose Prompts in Phase 3

**What goes wrong:** Agent prompts include detailed CLP debate protocols, turn-taking rules, conflict resolution strategies — behavioral depth deferred to Phase 4.

**Why it happens:** Trying to create "complete" agents in one pass.

**How to avoid:** Phase 3 boundary is "structurally valid and recognized by OpenCode as a working agent team" with "real prompts with role + methodology context." Keep prompts to ~100-200 lines: role definition, what the agent does, brief ADSS/Anchor Modeling context, cross-references to other agents. Save debate protocols for Phase 4.

**Warning signs:** Agent prompt files exceeding 300 lines, or containing detailed "if X happens, then Y" behavioral rules.

### Pitfall 4: Creating Global Skills (~/.config/opencode/skills/)

**What goes wrong:** Scaffolding writes to global user config instead of project `.opencode/skills/`.

**Why it happens:** OpenCode docs mention global skills as an option; seems like a way to make skills available everywhere.

**How to avoid:** `architect init` is project-local scaffolding. Always write to `.opencode/skills/<name>/SKILL.md` relative to project root. Global skills are a user customization, not a project scaffolding concern.

**Warning signs:** If scaffold code uses `Path.home()` or `~/.config/opencode`, you're in the wrong scope.

### Pitfall 5: Overcomplicating Template Generation

**What goes wrong:** Implementing Jinja2/Mako/Mustache template engine for agent/skill content generation.

**Why it happens:** Templates have repeated patterns (YAML frontmatter structure); seems like a job for a template engine.

**How to avoid:** Phase 2 established the pattern: `TEMPLATES: dict[str, str]` with Python f-strings or raw strings. Agent prompts are static text (no conditionals, no loops). Multi-line strings are fine. Don't add dependencies for something simpler than the problem.

**Warning signs:** `pip install jinja2` in dependencies, or `{% if %}` syntax in template files.

## Code Examples

Verified patterns from official sources:

### Agent File with Explicit Permissions

```markdown
---
description: Physical modeling specialist for performance and orchestration
mode: subagent
temperature: 0.1
tools:
  read: true
  write: false
  bash: ask
permissions:
  edit: deny
  Task: allow
---

# Data Engineer

You are the Data Engineer, responsible for translating Anchor Model designs into performant physical implementations.

## Your Role

- Propose indexing strategies for anchors and ties
- Suggest partitioning schemes for time-variant attributes
- Identify performance bottlenecks in proposed designs
- Recommend orchestration patterns for data pipelines

## When Invoked

The @data-architect will invoke you after the initial design is drafted. Provide specific, actionable recommendations.

## Methodology Context

See AGENTS.md for full ADSS and Anchor Modeling reference.
```

**Source:** [OpenCode Agents - Permissions](https://opencode.ai/docs/agents/)

### Skill with Forked Context and Agent Assignment

```markdown
---
name: da-review
description: Review a draft Anchor Model spec for completeness and methodology compliance
disable-model-invocation: true
context: fork
agent: data-architect
---

# Review Anchor Model Spec

Review the provided YAML spec file: $ARGUMENTS

## Your Task

1. Load the spec file and parse its structure
2. Validate naming conventions (snake_case, double underscore separators, no mnemonics)
3. Check for methodology compliance:
   - All anchors have at least one attribute
   - Ties are many-to-one (from anchor to anchor)
   - Knots are reused where appropriate
4. Invoke @veteran-reviewer for anti-pattern detection
5. Summarize findings with specific line references

Return a structured review with sections: Naming Issues, Methodology Issues, Anti-Patterns, Recommendations.
```

**Source:** [Claude Code Skills - Subagent Execution](https://code.claude.com/docs/en/skills)

### AGENTS.md Naming Convention Section

```markdown
## Naming Conventions

All database objects MUST follow these conventions:

### Anchor

```
anchor__<entity>
```

Example: `anchor__customer`, `anchor__order`, `anchor__product`

### Attribute

```
anchor__<entity>__<attribute>
```

Example: `anchor__customer__name`, `anchor__order__order_date`

### Tie (always many-to-one)

```
tie__<from>__<verb>__<to>
```

Example: `tie__order__placed_by__customer`

The "from" side is many, the "to" side is one. Read as "many orders are placed_by one customer."

### Knot

```
knot__<name>
```

Example: `knot__currency`, `knot__country`

### Nexus (many-to-many)

```
nexus__<name>
```

Example: `nexus__order_line`

### Rules

1. **snake_case only** — no PascalCase, no camelCase
2. **Double underscore `__` as separator** — single underscore within words (e.g., `order_date`), double underscore between components
3. **NO mnemonics** — write `customer` not `cust`, `order` not `ord`
4. **Full readable names** — optimize for human understanding, not byte count
```

**Source:** User's CONTEXT.md decisions + Anchor Modeling convention standards

### opencode.json with Tier Placeholders

```json
{
  "$schema": "https://opencode.ai/config.json",
  "name": "data-architect",
  "default_agent": "data-architect",
  "agents": {
    "data-architect": {
      "mode": "primary",
      "description": "Entry point and design authority for data warehouse modeling"
    }
  },
  "instructions": ["AGENTS.md"],
  "autoupdate": true,
  "_comment": "Model tier (budget/standard/high) will be configured by Data Architect on first interaction"
}
```

**Source:** [OpenCode Config Schema](https://opencode.ai/docs/config/)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom agent formats per platform | Agent Skills open standard | Dec 2025 | Cross-platform compatibility (Anthropic, OpenAI, future tools) |
| Implicit tool permissions | Explicit YAML permissions (allow/ask/deny) | OpenCode fork | Security-first design; prevents accidental destructive operations |
| Single-agent CLI tools | Multi-agent orchestration with @mentions | 2025-2026 | Specialization enables better designs; mimics human team collaboration |
| Manual CLI init workflows | Declarative scaffolding with templates | Established pattern | Consistency across projects; reduces setup errors |

**Deprecated/outdated:**
- `.claude/commands/*.md` format: Still supported for backward compatibility, but `.opencode/skills/*/SKILL.md` is preferred (supports supporting files, better organization)
- Trust-based tool access (Claude Code): OpenCode requires explicit permissions; implicit "tools: [Read, Write]" is now "tools: {read: true, write: ask}"

## Open Questions

1. **YAML spec schema structure for Anchor Models**
   - What we know: Phase 3 scaffolds "example YAML spec schemas" so agents produce consistent output
   - What's unclear: Exact schema structure (flat vs nested, required fields, how to represent anchors/attributes/ties)
   - Recommendation: Create minimal example schemas (e.g., `examples/anchor.yaml`, `examples/tie.yaml`) showing structure; agents use these as reference. Planner should define schema format based on Anchor Modeling concepts.

2. **Model tier mapping (budget/standard/high)**
   - What we know: Three-tier system mirrors GSD; Data Architect prompts user on first interaction
   - What's unclear: Which Claude models map to each tier? Budget = Haiku, Standard = Sonnet, High = Opus? Or all Sonnet with different subagents?
   - Recommendation: Define tier → model mapping in planning. Likely: Budget (Haiku primary, Sonnet for Architect), Standard (Sonnet all), High (Opus for Architect, Sonnet for others). Check GSD's .claude/get-shit-done for tier definitions.

3. **CLP process structure**
   - What we know: User mentioned "CLP stages" and "debate expectations" in AGENTS.md context; basic structure in Phase 3
   - What's unclear: What are the CLP stages? Curate → Leverage → Prioritize? What happens in each?
   - Recommendation: Define CLP process structure in AGENTS.md with ~100-200 word overview. Detailed turn-taking/debate protocol deferred to Phase 4, but agents need to know the flow exists.

4. **Spec output location for /da:export**
   - What we know: "Fixed, predictable location (not user-chosen)"
   - What's unclear: What's the location? `.data-architect/specs/`? `.opencode/specs/`? Project root?
   - Recommendation: Define in planning. Suggest: `.data-architect/specs/<domain>-spec.yaml` — separate from OpenCode config, clear ownership.

## Sources

### Primary (HIGH confidence)

- [OpenCode Agents Documentation](https://opencode.ai/docs/agents/) - Agent file structure, YAML frontmatter fields, mode/permissions
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) - Skill structure, SKILL.md format, context forking, arguments
- [OpenCode Config Documentation](https://opencode.ai/docs/config/) - opencode.json structure, default_agent, model selection
- [OpenCode Rules/AGENTS.md Documentation](https://opencode.ai/docs/rules/) - Shared context file purpose and loading
- [Agent Skills Specification](https://agentskills.io/specification) - Open standard format (Dec 2025)

### Secondary (MEDIUM confidence)

- [Claude Code vs OpenCode Agents: Key Differences (GitHub Gist)](https://gist.github.com/RichardHightower/827c4b655f894a1dd2d14b15be6a33c0) - Architecture differences, configuration philosophy
- [AI Coding Tools Guide (Medium)](https://senrecep.medium.com/ai-coding-tools-the-complete-guide-to-claude-code-opencode-modern-development-eb9da4477dc1) - Relationship between Claude Code and OpenCode
- [Anchor Modeling Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) - Core concepts (anchors, attributes, ties, knots)
- [Data Vault Architecture Explained (OvalEdge)](https://www.ovaledge.com/blog/data-vault-architecture) - Three-layer architecture patterns

### Tertiary (LOW confidence)

- WebSearch results on ADSS methodology - No authoritative source found; appears to be project-specific terminology. Treating "ADSS three-layer architecture" as user-defined framework analogous to Data Vault 2.0.
- [Node.js CLI scaffolding patterns](https://oneuptime.com/blog/post/2026-01-22-nodejs-create-cli-tool/view) - General CLI patterns (not OpenCode-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - OpenCode and Agent Skills spec are documented with official sources; scaffolding pattern established in Phase 2
- Architecture: HIGH - OpenCode agent/skill file structure and configuration verified from official docs; orchestration pattern clear from user decisions
- Pitfalls: MEDIUM - Derived from user constraints (model assignment timing, skill routing) and general scaffolding anti-patterns; not empirically observed in OpenCode projects

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (30 days) - Stable domain (Agent Skills is a finalized standard; OpenCode architecture unlikely to change fundamentally)
