# Project Research Summary

**Project:** Warehouse Architect
**Domain:** Python CLI tool + OpenCode.ai agent scaffolding for data warehouse design (Anchor Modeling / ADSS methodology)
**Researched:** 2026-02-07
**Confidence:** HIGH

## Executive Summary

Warehouse Architect is a Python CLI tool (`architect`) with two core commands: `architect init` scaffolds a team of six OpenCode.ai agent definitions into a project's `.opencode/agents/` directory, and `architect generate` (milestone 2) deterministically transforms YAML/JSON specs into DAS/DAR SQL scripts. The CLI itself is straightforward engineering -- the real product is the content of the agent definition files. These agents encode deep domain expertise in Anchor Modeling methodology, enforce a Conceptual-Logical-Physical (CLP) debate workflow, and guide users through data warehouse design via structured multi-agent debate within OpenCode. No existing tool in the OpenCode ecosystem provides domain-specific data warehouse agents with structured debate protocols. This is the blue ocean.

The recommended approach is a pure-functional Python stack built on the Astral ecosystem (UV, Ruff, Hatchling) with Typer for the CLI, frozen dataclasses for immutable data, Jinja2 for code generation, and pytest + Hypothesis for TDD. The architecture follows a "thin CLI shell over pure logic" pattern: CLI handles I/O and formatting, all business logic lives in pure functions that transform immutable data, and side effects are pushed to the edges. Agent definition files are static Markdown with YAML frontmatter, bundled via `importlib.resources` and copied verbatim during scaffolding -- no templating during init. The `src/` layout and snapshot testing ensure packaging correctness and deterministic output.

The three highest-risk areas are: (1) OpenCode platform instability -- it releases every 1-3 days and the agent format may change, requiring a decoupled template layer and version markers; (2) shallow immutability in frozen dataclasses -- nested `list` and `dict` fields silently break the immutability contract, demanding a project-wide convention of `tuple` and `frozenset` from day one; and (3) prompt engineering quality -- the agents ARE the product, and shallow role descriptions will produce generic output, so substantial domain research into Anchor Modeling rules, CLP checkpoint criteria, and debate termination logic must happen before agent definitions are written.

## Key Findings

### Recommended Stack

The stack centers on the Astral ecosystem (UV + Ruff) for modern Python tooling, with Hatchling for builds and uv-dynamic-versioning for git-tag-based versioning. All choices are HIGH confidence, verified from official documentation. See [STACK.md](./STACK.md) for full details including pyproject.toml configuration, CI/CD workflows, and version compatibility matrix.

**Core technologies:**
- **Python >=3.13 + UV >=0.10.0**: Runtime and package management. UV replaces pip/poetry/pyenv with 10-100x faster operations and cross-platform lockfile.
- **Typer >=0.21.0**: CLI framework. Function-based API aligns with functional Python mandate. Auto-generates help and supports subcommands.
- **Hatchling + uv-dynamic-versioning**: Build backend with automatic version derivation from git tags. No hardcoded version strings.
- **Ruff >=0.15.0 + Mypy >=1.19.0**: Linting/formatting (single tool, Rust-speed) and strict static type checking. Enforces functional style through annotations.
- **pytest >=9.0.0 + Hypothesis >=6.151.0**: TDD-first testing with property-based testing for spec parsing invariants.
- **Frozen dataclasses (stdlib)**: Immutable data structures. No external FP libraries needed -- `tuple` fields + `dataclasses.replace()` cover all requirements.
- **Jinja2 >=3.1 + PyYAML >=6.0**: Template rendering for SQL/dbt generation (milestone 2) and YAML spec parsing. Jinja2 is the dbt standard.

**Critical version requirement:** CI must use `fetch-depth: 0` and `fetch-tags: true` for dynamic versioning to work.

### Expected Features

Milestone 1 is `architect init` + agent definitions only. The CLI is trivial; the value is entirely in prompt engineering quality. See [FEATURES.md](./FEATURES.md) for full feature landscape, competitor analysis, and dependency graph.

**Must have (table stakes):**
- Zero-config `architect init` -- single command, no prompts, creates all files with sensible defaults
- Clear output showing every file created, with next-step guidance
- Idempotent re-run -- skip existing files with warning, `--force` to overwrite
- Valid OpenCode agent format -- Markdown + YAML frontmatter conforming to OpenCode spec exactly
- AGENTS.md project rules file -- shared ADSS/Anchor Modeling context for all agents
- opencode.json pre-configured -- agent team works out of the box
- Helpful error messages with human-readable suggestions
- `--help` with examples (Typer provides this automatically)

**Should have (differentiators):**
- Domain-expert agent personas -- not generic "coding assistant" roles but deep Anchor Modeling expertise
- Structured CLP debate protocol encoded in agent system prompts
- Anchor Modeling methodology rules in Data Architect and Veteran Reviewer prompts
- OpenCode skills for reusable capabilities (CLP debate, Anchor Modeling rules)
- Spec format bootstrapping -- example YAML schemas so agents produce consistent output
- `--dry-run` and `--dir` flags for preview and non-cwd scaffolding

**Defer (v2+):**
- Interactive init prompts (nothing to ask; adds friction)
- Plugin system for custom agents (premature abstraction; Markdown IS the API)
- Template engine during init (files are not parameterized)
- Auto-update with merge (needs conflict resolution strategy first)
- Web UI / dashboard (different product; OpenCode provides the conversation UI)

### Architecture Approach

The architecture follows a layered pattern: thin CLI shell (Typer/Click) dispatches to pure function modules (scaffold, generate), which operate on immutable data (frozen dataclasses) and push all side effects to the edges. Agent templates are bundled as package data accessed via `importlib.resources`, not `__file__` path hacking. The `src/` layout prevents accidental imports and catches packaging bugs early. See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system diagram, data flows, and anti-patterns.

**Major components:**
1. **CLI Entry Point** (`cli.py`) -- Parses commands, formats output, handles errors. Zero business logic.
2. **Scaffolder** (`scaffold.py`) -- Pure functions: reads bundled agent templates via `importlib.resources`, writes to target `.opencode/agents/`. One-way file copy, no state.
3. **Spec System** (`spec.py`) -- Frozen dataclasses (Spec, Anchor, Attribute, Tie, Knot) + pure parsing/validation functions. The contract between agent debate output and deterministic generators.
4. **DAS/DAR Generators** (`das/`, `dar/`) -- Pure transform pipelines: Spec -> intermediate context dicts -> Jinja2 template rendering -> SQL/dbt output. Deterministic: same spec always produces same output.
5. **Bundled Agent Templates** (`_agents/`) -- Static Markdown files with YAML frontmatter. Copied verbatim during scaffold. The actual product.

**Key architectural decisions:**
- `src/` layout (not flat) for packaging correctness
- `importlib.resources` (not `__file__`) for template bundling
- Snapshot testing (Syrupy) for deterministic output verification
- Templates do NO logic -- all decisions made in pure Python transform functions
- Spec files are the contract boundary between probabilistic agents and deterministic generators

### Critical Pitfalls

See [PITFALLS.md](./PITFALLS.md) for complete pitfall inventory with recovery strategies and phase mapping.

1. **Shallow immutability in frozen dataclasses** -- `frozen=True` only prevents field reassignment; nested `list`/`dict` fields remain mutable. Prevention: enforce `tuple[T, ...]` and `frozenset[T]` for all collection fields from day one. Use `__post_init__` validation. This is a Phase 1 concern that cannot be retrofitted.

2. **OpenCode platform instability** -- OpenCode releases every 1-3 days with breaking changes possible. Prevention: use only stable frontmatter fields (`description`, `model`, `tools`, `permission`), embed version markers in scaffolded files, design for update-ability from the start, and decouple agent format behind a Python data structure.

3. **Prompt engineering depth gates all value** -- Generic "you are a data architect" prompts produce generic output. The agents must encode specific Anchor Modeling rules, CLP checkpoint criteria, debate positions, and decision frameworks. Prevention: deep domain research before writing any agent definitions; study Roenbaeck's reference implementation.

4. **Multi-agent debate loops** -- Without bounded iterations and convergence detection, agents can loop indefinitely, burning tokens without decisions. Prevention: encode max round limits (3 rounds), convergence detection, and Veteran Reviewer tie-breaking authority directly in agent prompts.

5. **Dynamic versioning fails in CI** -- Shallow clones lose git tag history, causing silent `0.0.0` version fallback. Prevention: `fetch-depth: 0` + `fetch-tags: true` in CI; version validation step before any publish; obviously wrong fallback version (`0.0.0.dev0+unknown`).

## Implications for Roadmap

Based on combined research, the following phase structure follows the dependency chain identified in architecture research, aligns with the milestone definitions from feature research, and addresses pitfalls at the earliest possible phase.

### Phase 1: Project Foundation + CLI Skeleton
**Rationale:** Everything depends on the package existing and being installable. Establishes the functional Python conventions, build system, CI pipeline, and the `architect init` command skeleton. Must resolve the "no classes" boundary definition and immutability conventions before any domain code is written.
**Delivers:** pyproject.toml with UV/Hatchling config, Makefile, src/ package skeleton, `architect init` command (Typer), `scaffold.py` with placeholder agent, CI pipeline (lint + type + test), dynamic versioning validated on TestPyPI.
**Addresses features:** `architect init` command, `--help`, error handling, pip-installable entry point, idempotent re-run / `--force`.
**Avoids pitfalls:** Shallow immutability (convention established), "no classes" rule collision (boundary documented), dynamic versioning CI failure (validated early), package data inclusion (wheel inspected).

### Phase 2: Agent Definitions + Debate Protocol
**Rationale:** The agents ARE the product. Once the scaffold mechanism works (Phase 1), the focus must shift to prompt engineering. This requires deep Anchor Modeling domain research and CLP workflow design. Agent definitions must be written before the spec system (Phase 3) because agents need to reference the spec format, and the spec format should be informed by what agents actually produce during debate.
**Delivers:** All six agent `.md` files (Data Architect, System Analyst, Business Analyst, Data Engineer, Analytics Engineer, Veteran Reviewer), AGENTS.md with shared methodology context, opencode.json configuration, CLP debate protocol, Anchor Modeling rules encoded in prompts, debate termination logic.
**Addresses features:** Domain-expert agent personas, structured debate protocol, CLP workflow guidance, Anchor Modeling methodology, AGENTS.md project rules, opencode.json configuration.
**Avoids pitfalls:** LLM intent errors (traceability requirements in prompts), infinite debate loops (max rounds + convergence detection), OpenCode instability (minimal stable frontmatter fields only), scaffold drift (version markers embedded).

### Phase 3: Spec System + Validation
**Rationale:** Generators consume specs. The spec format must be defined and validated before DAS/DAR generation can begin. This phase creates the contract boundary between the probabilistic world (agent debate) and the deterministic world (code generation). Informed by the agent definitions from Phase 2 so specs match what agents actually produce.
**Delivers:** Frozen dataclasses (Spec, Anchor, Attribute, Tie, Knot), `read_spec()` and `validate_spec()` pure functions, YAML/JSON parsing with schema validation, Hypothesis property-based tests, spec format documentation for agents to reference.
**Addresses features:** Spec schema bootstrapping, consistent agent output format.
**Avoids pitfalls:** Shallow immutability (tuple-only collections enforced), spec-generator drift (schema validation on all specs).

### Phase 4: DAS Generation (Source to Staging)
**Rationale:** DAS is simpler than DAR (more direct mapping from source schema to staging tables). Proves the generation pipeline pattern (spec -> transform -> Jinja2 render -> SQL output) before tackling the more complex DAR transforms. Delivers the `architect generate` command.
**Delivers:** `das/transforms.py` pure transform functions, `templates/das/*.sql.j2` Jinja2 templates, `generate` CLI command (DAS target), snapshot tests for generated SQL, deterministic output guarantee.
**Addresses features:** `architect generate` command (DAS scripts).
**Avoids pitfalls:** Jinja2 templates with logic (all decisions in Python, templates do simple iteration only), testing through CLI only (pure functions tested directly, CliRunner for integration only).

### Phase 5: DAR Generation + End-to-End Validation
**Rationale:** DAR transforms are more complex (Unified Star Schema, bridge tables, dimension/fact derivation). Requires the proven generation pipeline from Phase 4. Concludes with end-to-end validation: scaffold agents -> write spec -> generate scripts -> validate output.
**Delivers:** `dar/transforms.py` pure transform functions (USS pattern), `templates/dar/*.sql.j2` (bridge, dimension, fact), DAR target in generate command, e-commerce demo scenario, end-to-end integration test, PyPI publish preparation.
**Addresses features:** `architect generate` command (DAR scripts).
**Avoids pitfalls:** Anchor Modeling over-application (selective application criteria in validation), 6NF performance traps (table count budget per entity).

### Phase Ordering Rationale

- **Foundation first (Phase 1)** because every subsequent phase depends on the package structure, build system, and functional Python conventions being established. You cannot write agents without a scaffold mechanism, and you cannot write generators without a package.
- **Agents before specs (Phase 2 before 3)** because the spec format should be informed by what agents actually produce during debate. Writing specs first risks creating a format the agents cannot practically generate. The agents are also the milestone 1 deliverable and core product value.
- **Specs before generation (Phase 3 before 4-5)** because generators consume specs. The Spec type is the contract that connects agents to generators.
- **DAS before DAR (Phase 4 before 5)** because DAS is simpler and proves the generation pipeline pattern. DAR builds on the proven pattern with more complex transforms.
- **This ordering addresses pitfalls early:** immutability conventions (Phase 1), OpenCode format stability (Phase 1-2), debate protocol (Phase 2), and defers the riskiest domain work (6NF application) to Phase 5 when the team has the most context.

### Research Flags

**Phases likely needing deeper research during planning:**
- **Phase 2 (Agent Definitions):** Deep domain research required. Anchor Modeling rules from Roenbaeck reference implementation, CLP workflow checkpoint criteria, debate protocol patterns for multi-agent systems. No existing template provides this. This is where the product's competitive moat is built.
- **Phase 5 (DAR Generation):** Unified Star Schema patterns have sparser documentation than Anchor Modeling. Bridge table derivation logic needs domain expertise research.

**Phases with standard patterns (can skip research-phase):**
- **Phase 1 (Foundation):** Well-documented patterns. UV, Typer, Hatchling, pytest, GitHub Actions all have official guides with complete examples. The STACK.md research already provides ready-to-use configurations.
- **Phase 3 (Spec System):** Standard frozen dataclass + YAML parsing. Hypothesis property-based testing is well-documented.
- **Phase 4 (DAS Generation):** Jinja2 SQL template rendering is a standard pattern used by dbt. Staging layer transforms are well-understood in data engineering.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified from official documentation. Version compatibility confirmed. Complete pyproject.toml and CI configurations provided. |
| Features | HIGH | CLI scaffolding UX patterns well-established (clig.dev, copier, cookiecutter). OpenCode agent format verified from official docs. Feature prioritization clear. |
| Architecture | HIGH | Pure functional Python patterns documented in official Python HOWTO. importlib.resources, src/ layout, and snapshot testing are standard practices. Component boundaries well-defined. |
| Pitfalls | MEDIUM-HIGH | Python FP pitfalls verified against official docs. OpenCode instability confirmed from live changelog. Anchor Modeling pitfalls from domain expertise. Some pitfalls (debate loops, LLM intent errors) are harder to validate without runtime testing. |

**Overall confidence:** HIGH

### Gaps to Address

- **Anchor Modeling rule encoding:** Research confirms this is critical but the specific rules (what qualifies as anchor vs. attribute, historization criteria, naming conventions) require study of Roenbaeck's reference implementation. Must happen during Phase 2 planning.
- **CLP debate protocol design:** No existing template for multi-agent debate in OpenCode. The protocol (how agents invoke each other, when to escalate, how to terminate) must be designed from first principles. Phase 2 research task.
- **OpenCode format stability:** The format is documented but OpenCode releases every 1-3 days. The specific frontmatter fields and directory conventions should be re-verified at the start of each phase.
- **Ruff enforcement of functional style:** No Ruff rule can ban class definitions. Enforcement relies on code review conventions and documentation. Consider a custom Ruff plugin if the team grows.
- **ty (Astral type checker):** Currently beta, may replace Mypy by late 2026. Monitor but do not adopt yet. The switch will be trivial when ready.

## Sources

### Primary (HIGH confidence)
- [OpenCode.ai Agents Docs](https://opencode.ai/docs/agents/) -- Agent definition format, frontmatter fields, modes
- [OpenCode.ai Config Docs](https://opencode.ai/docs/config/) -- opencode.json schema, configuration merging
- [OpenCode.ai Skills Docs](https://opencode.ai/docs/skills/) -- Skill format, SKILL.md structure
- [OpenCode.ai Rules Docs](https://opencode.ai/docs/rules/) -- AGENTS.md rules format
- [UV Working on Projects](https://docs.astral.sh/uv/guides/projects/) -- pyproject.toml, uv sync, uv build
- [UV GitHub Actions Guide](https://docs.astral.sh/uv/guides/integration/github/) -- CI/CD workflows
- [Typer Documentation](https://typer.tiangolo.com/) -- CLI framework, function-based API
- [Python Packaging User Guide: src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) -- Package structure
- [importlib.resources -- Python 3 Official Docs](https://docs.python.org/3/library/importlib.resources.html) -- Package data access
- [Command Line Interface Guidelines](https://clig.dev/) -- CLI UX best practices
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/) -- Property-based testing
- [Python dataclasses -- Official Docs](https://docs.python.org/3/library/dataclasses.html) -- Frozen dataclass behavior
- [Python Functional Programming HOWTO](https://docs.python.org/3/howto/functional.html) -- Functional patterns in Python

### Secondary (MEDIUM confidence)
- [uv-dynamic-versioning on PyPI](https://pypi.org/project/uv-dynamic-versioning/) -- Dynamic versioning plugin
- [OpenCode GitHub (sst/opencode)](https://github.com/sst/opencode) -- Platform evolution, release cadence
- [Claude Code to OpenCode Agent Conversion Guide](https://gist.github.com/RichardHightower/827c4b655f894a1dd2d14b15be6a33c0) -- Agent format migration patterns
- [Copier Documentation](https://copier.readthedocs.io/) -- Scaffolding tool patterns
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) -- Methodology rules, 6NF patterns
- [Syrupy Snapshot Testing](https://til.simonwillison.net/pytest/syrupy) -- Snapshot testing patterns

### Tertiary (needs validation during implementation)
- Debate protocol design -- no existing template; must be designed from first principles
- Anchor Modeling rule encoding -- requires Roenbaeck reference study
- OpenCode format stability -- must be re-verified at start of each phase

---
*Research completed: 2026-02-07*
*Ready for roadmap: yes*
