---
phase: 03-agent-definitions-opencode-integration
plan: "01"
subsystem: agent-definitions
tags: [agents, opencode, methodology, templates]
completed: 2026-02-08

dependencies:
  requires:
    - phase: 02
      plan: "02"
      artifact: TEMPLATES dict
  provides:
    - AGENTS.md methodology primer
    - opencode.json configuration
    - 6 agent prompts with team awareness
    - 2 example spec schemas
  affects:
    - src/data_architect/templates.py

tech_stack:
  added:
    - OpenCode agent definitions (YAML frontmatter + markdown)
    - Agent Skills open standard patterns
  patterns:
    - Multi-agent orchestration via @mentions
    - Primary/subagent mode architecture
    - Explicit tool permissions (read/write/bash)

key_files:
  created:
    - AGENTS.md: Comprehensive ADSS/Anchor Modeling methodology context (~1000 words)
    - opencode.json: Platform configuration with tier placeholder system
    - .data-architect/specs/examples/anchor-example.yaml: Single anchor with attributes example
    - .data-architect/specs/examples/domain-example.yaml: E-commerce domain composition example
  modified:
    - src/data_architect/templates.py: Replaced stubs with full agent prompts and added 2 spec schemas (11 total templates)
    - tests/test_cli.py: Updated file count from 9 to 11
    - tests/test_scaffold.py: Updated file count from 9 to 11
    - pyproject.toml: Added E501 per-file ignore for templates.py

decisions:
  - key: agent-model-assignments
    decision: No hardcoded model assignments in agent frontmatter
    rationale: User chooses tier on first interaction; agents are not pre-assigned to models
    impact: Data Architect prompts for tier (budget/standard/high) on first /da:start
  - key: agent-temperature-settings
    decision: "data-architect: 0.3 (synthesis), system/business-analyst: 0.5 (debate), data-engineer/veteran-reviewer: 0.1 (precision), analytics-engineer: 0.3"
    rationale: Match role to creative/analytical needs
    impact: Agent responses tuned to role characteristics
  - key: anti-pattern-checklist
    decision: Veteran Reviewer has 10-item checklist from Phase 3
    rationale: Give reviewer teeth immediately, deepen in Phase 4
    impact: Methodology enforcement begins in Phase 3

metrics:
  duration_minutes: 7.5
  tasks_completed: 2
  commits: 2
  files_modified: 4
  lines_added: 758
  templates_total: 11
---

# Phase 3 Plan 1: Shared Context and Agent Prompts Summary

**One-liner:** Complete agent team definitions with ADSS/Anchor Modeling methodology, tier-based model selection, cross-team orchestration via @mentions, and 10-item anti-pattern checklist for Veteran Reviewer.

## What Was Built

This plan delivered the core content authoring for Phase 3 — transforming Phase 2's structural scaffolding into a working agent team recognized by OpenCode. The TEMPLATES dict now contains:

1. **AGENTS.md**: Comprehensive methodology primer covering ADSS three-layer architecture (DAS/DAB/DAR), Anchor Modeling core concepts (anchors, attributes, ties, knots, nexuses), CLP stages overview, USS basics, naming conventions (snake_case, double underscore separators, NO mnemonics), and team interaction rules.

2. **opencode.json**: Valid OpenCode configuration with `$schema`, `default_agent`, tier placeholder comment explaining budget/standard/high system, and `instructions: ["AGENTS.md"]` to load shared context.

3. **Six agent prompts** (data-architect, system-analyst, business-analyst, data-engineer, analytics-engineer, veteran-reviewer): Each agent has YAML frontmatter (description, mode, temperature, tools, permissions — NO model field) and markdown body with role definition, methodology context, cross-references by @name, and team awareness.

4. **Two example spec schemas**: `anchor-example.yaml` demonstrates single anchor with 4 attributes, `domain-example.yaml` demonstrates e-commerce domain with anchors/ties/knots/nexuses composition.

## Tasks Completed

### Task 1: Write shared context, config, and spec schema templates

**Commit:** db4b867

**Changes:**
- AGENTS.md: ~1000 words covering ADSS architecture, Anchor Modeling concepts, CLP stages, USS basics, naming conventions (exact format with examples), team interaction rules with escalation path
- opencode.json: Valid JSON with tier placeholder comment ("Model tier (budget/standard/high) will be configured by Data Architect agent on first /da:start interaction. Budget=fast+cheap, Standard=balanced, High=maximum quality.")
- anchor-example.yaml: Example anchor `anchor__customer` with 4 attributes demonstrating naming convention and historized vs static attributes
- domain-example.yaml: E-commerce domain example showing 3 anchors (customer, order, product), 2 ties, 2 knots, 1 nexus
- Updated tests to reflect 11 template files (was 9)
- Added E501 per-file ignore for templates.py (markdown prose in strings)

**Verification:** 11 entries in TEMPLATES dict, AGENTS.md has 500+ words, opencode.json has tier placeholder, spec schemas use correct naming conventions.

### Task 2: Write all six agent prompt bodies

**Commit:** d105027

**Changes:**
- **data-architect.md** (93 lines): Primary agent, entry point. Team orchestration section lists all 5 subagents. First interaction protocol for tier selection. Output format references spec schemas. Cross-references: @business-analyst, @system-analyst, @data-engineer, @analytics-engineer, @veteran-reviewer.

- **system-analyst.md** (60 lines): Source system expert. Advocates source-system fidelity. Reads source schemas from filesystem. Cross-references: @data-architect (orchestrator), @business-analyst (counterpart). Examples of productive conflict with @business-analyst.

- **business-analyst.md** (60 lines): Business domain expert. Advocates business meaning. Translates business questions to modeling requirements. Cross-references: @data-architect (orchestrator), @system-analyst (counterpart). Examples of productive conflict with @system-analyst.

- **data-engineer.md** (60 lines): Physical modeling specialist. Invoked after logical model drafted. Provides indexing strategies, partitioning schemes, orchestration patterns. Cross-references: @data-architect (orchestrator).

- **analytics-engineer.md** (66 lines): DAR consumption perspective. Validates DAB->DAR transform, evaluates against business questions. Cross-references: @data-architect (orchestrator), @business-analyst (for business question context).

- **veteran-reviewer.md** (131 lines): Grumpy methodology critic. **10-item anti-pattern checklist**: (1) God anchor, (2) Missing historization, (3) Circular ties, (4) Tie masquerading as anchor, (5) Orphan anchors, (6) Knot overuse, (7) Naming violations, (8) Missing business context, (9) Premature physical optimization, (10) Anchor/attribute confusion. Cross-references: @data-architect (orchestrator).

- **All agents**: YAML frontmatter includes description, mode (primary/subagent), temperature, tools (read/write/bash), permissions (edit/Task). **Removed `model: anthropic:claude-sonnet-4-20250514` from all 6 agents** per locked decision.

**Verification:** `make check` passes (lint, type, test). All 6 agents have real prompts (not TODO stubs). No agent contains `model:` in frontmatter. All agents contain at least one `@` cross-reference. Veteran Reviewer has 10-item checklist.

## Deviations from Plan

None — plan executed exactly as written. Both tasks completed without needing auto-fix rules (Rule 1-3) or architectural decisions (Rule 4).

## Verification Results

All plan verification criteria met:

1. ✓ `python -c "from data_architect.templates import TEMPLATES; print(len(TEMPLATES))"` outputs 11
2. ✓ All 6 agent files start with `---` (YAML frontmatter)
3. ✓ No agent file contains `model:` in frontmatter
4. ✓ All agent files contain at least one `@` cross-reference to another agent
5. ✓ AGENTS.md contains naming conventions with double underscore examples
6. ✓ opencode.json contains `"default_agent": "data-architect"` and tier comment
7. ✓ Example spec schemas use correct naming conventions
8. ✓ `make check` passes

## Self-Check

### Created Files

```bash
✓ FOUND: .data-architect/specs/examples/anchor-example.yaml (in TEMPLATES dict)
✓ FOUND: .data-architect/specs/examples/domain-example.yaml (in TEMPLATES dict)
✓ FOUND: AGENTS.md (in TEMPLATES dict)
✓ FOUND: opencode.json (in TEMPLATES dict)
✓ FOUND: All 6 agent prompts in TEMPLATES dict
```

### Commits

```bash
✓ FOUND: db4b867 (Task 1: shared context, config, and spec schemas)
✓ FOUND: d105027 (Task 2: all six agent prompts)
```

### Modified Files

```bash
✓ VERIFIED: src/data_architect/templates.py contains 11 entries (was 9)
✓ VERIFIED: tests/test_cli.py updated to reflect 11 files
✓ VERIFIED: tests/test_scaffold.py updated to reflect 11 files
✓ VERIFIED: pyproject.toml has E501 ignore for templates.py
```

**Self-Check: PASSED**

All claimed artifacts exist. All commits are in git history. All tests pass.

## Next Phase Readiness

Phase 3 Plan 2 (skills scaffolding) can proceed immediately. This plan provides:

- ✓ AGENTS.md for skill instructions to reference
- ✓ opencode.json structure for skills to extend
- ✓ Agent prompts for skills to invoke (@data-architect as orchestrator)
- ✓ Example spec schemas for skills to demonstrate output format

**Blockers:** None

**Risks:** None identified

## Lessons Learned

1. **Template string line length**: E501 violations are expected in markdown prose strings. Per-file ignore (`"src/data_architect/templates.py" = ["E501"]`) is the right pattern — breaking lines would corrupt markdown content.

2. **Test updates cascade**: Adding 2 template entries requires updating test assertions in both `test_cli.py` (CLI integration) and `test_scaffold.py` (scaffolding engine). Use `replace_all: true` for numerical assertions.

3. **Agent cross-references establish team awareness early**: Even without deep CLP protocol (Phase 4), agents referencing each other by @name creates team context. Example: "Your counterpart @business-analyst will often disagree with you" primes productive debate.

4. **Anti-pattern checklist gives Veteran Reviewer immediate value**: Phase 3 boundary is "structural validity, not behavioral depth," but a concrete 10-item checklist (god anchor, missing historization, etc.) makes the reviewer actionable from day one. Phase 4 can deepen the methodology critique without reworking the structure.

5. **Tier selection protocol defers model assignments correctly**: User chooses budget/standard/high on first interaction, not at `architect init` time. Scaffolded `opencode.json` has placeholder comment, no model assignments. Data Architect prompt includes exact tier selection protocol text.

---

**Plan completed:** 2026-02-08T00:35:42Z
**Duration:** ~7.5 minutes
**Commits:** db4b867, d105027
**Next:** Plan 03-02 (Skills scaffolding)
