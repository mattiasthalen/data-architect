# Feature Research: Python CLI Scaffolding + OpenCode Agent Definitions

**Domain:** CLI scaffolding tools, AI agent definition/scaffolding, data warehouse design tooling
**Researched:** 2026-02-07
**Confidence:** HIGH (CLI scaffolding patterns well-established; OpenCode agent format documented; data warehouse tooling mature)

## Context

This research covers features for `warehouse-architect`, a Python CLI with two commands:
- `architect init` -- scaffolds OpenCode agent definitions into `.opencode/` in the current working directory
- `architect generate` -- deterministic DAS/DAR script generation from YAML/JSON specs (milestone 2+)

**Milestone 1 scope: `architect init` + agent definitions only.** No generators.

The agents (Data Architect, System Analyst, Business Analyst, Data Engineer, Analytics Engineer, Veteran Reviewer) run in OpenCode and guide users through DAB layer design using Anchor Modeling methodology through CLP debate.

Research dimensions:
1. CLI scaffolding tools (cookiecutter, copier, yeoman) -- expected UX patterns
2. AI agent definition/scaffolding -- how tools set up agent configurations
3. Data warehouse design tools -- what domain-specific features matter
4. Code generation from specs -- standard patterns (deferred to milestone 2)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = users abandon the tool at first interaction.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Zero-config init command** | Every CLI scaffolding tool (cookiecutter, copier, PyScaffold) works with a single command. `architect init` must create all files without questions. Users expect `pip install warehouse-architect && architect init` to produce a working setup. | LOW | No prompts needed for milestone 1. Sensible defaults only. Copier/cookiecutter ask questions; we should not -- our output is fixed (opinionated agent team), not templated. |
| **Clear output showing what was created** | CLI UX guidelines (clig.dev) require confirming state changes. Users must see exactly which files were created and where. Scaffolding tools always list generated files. | LOW | Print each file path as it is created. Show a summary at the end. No silent file creation. |
| **Idempotent / safe re-run** | Copier supports `copier update`. Users will accidentally run `init` twice. Must either skip existing files, warn, or offer `--force` flag. Running `init` in a directory with existing `.opencode/` must not silently destroy customizations. | LOW | Default: skip existing with warning. `--force` flag to overwrite. This is table stakes for any scaffolding tool. |
| **Valid OpenCode agent format** | Agents must conform to OpenCode's documented format: markdown files with YAML frontmatter (description, model, tools, permission, temperature, steps, etc.) in `.opencode/agents/`. Invalid format = agents do not load = tool is broken. | MEDIUM | OpenCode validates frontmatter fields. Must match the spec exactly: `description` (required), `model`, `tools`, `permission`, `temperature`, `top_p`, `steps`, `hidden`, `color`, `disable`. Markdown body is the system prompt. |
| **Helpful error messages** | CLI best practices: catch errors, rewrite for humans, suggest next steps. "Command not found" or cryptic Python tracebacks are unacceptable. | LOW | Handle: directory not writable, not a git repo (warning not error), OpenCode not installed (info not error), existing files conflict. |
| **`--help` with examples** | Every CLI tool provides `--help`. Must show usage, what the command does, and an example invocation. Typer/Click generate this automatically from type hints and docstrings. | LOW | Typer gives this for free. Include description of what gets scaffolded and where. |
| **Works without OpenCode installed** | The CLI scaffolds files. It does not need to run OpenCode. Users may install the CLI first, inspect files, then install OpenCode. The tool must not check for or require OpenCode at init time. | LOW | File creation only. No runtime dependency on OpenCode. |
| **AGENTS.md / rules file** | OpenCode projects use `AGENTS.md` in the project root for project-level rules. Scaffolding should include this file with project context (ADSS methodology, Anchor Modeling rules, CLP workflow description) so agents have shared context. | MEDIUM | This is how OpenCode loads project-wide instructions. Without it, agents lack shared context about the methodology. Critical for coherent multi-agent behavior. |
| **pip-installable with entry point** | Standard for Python CLI tools. `pip install warehouse-architect` then `architect` command is available. Users expect this to just work. PyScaffold, copier, cookiecutter all follow this pattern. | LOW | UV builds, pyproject.toml `[project.scripts]` entry point. Standard Python packaging. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not expected from a scaffolding tool, but provide real value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Domain-expert agent personas** | Not generic "coding assistant" agents. Each agent has deep domain expertise: Data Architect knows Anchor Modeling rules, System Analyst understands source system patterns, Business Analyst thinks in business terms, Veteran Reviewer has seen every anti-pattern since Inmon. The prompt engineering IS the product. | HIGH | This is the core value. Agent prompts must encode genuine expertise, not surface-level role descriptions. Each agent needs: persona, expertise areas, debate style, decision criteria, methodology knowledge. Comparable tools (opencode-template) have generic roles; ours are data warehouse specialists. |
| **Structured debate protocol in agent prompts** | Agents do not just answer questions -- they argue through CLP stages. System Analyst and Business Analyst take opposing positions. Data Architect synthesizes. Veteran Reviewer critiques. The debate protocol is encoded in agent system prompts, not in external orchestration code. | HIGH | This is unique. No existing OpenCode agent template encodes multi-agent debate protocols. The protocol must specify: when to invoke which agent, what each agent argues for/against, how disagreements surface, how the user decides. All through prompt engineering in the agent markdown files. |
| **CLP workflow guidance embedded in agents** | Agents guide users through Conceptual -> Logical -> Physical progression. They refuse to jump to physical modeling prematurely. The workflow enforcement is in the prompts, not in code. | MEDIUM | Data Architect agent's system prompt must include CLP stage awareness, checkpoint criteria, and the discipline to enforce progression. This is methodology compliance through prompt design. |
| **Anchor Modeling methodology encoded** | Agent prompts contain Anchor Modeling rules: what qualifies as an anchor vs attribute vs tie vs knot, when to use historization, 6NF normalization criteria, naming conventions. This domain knowledge is the competitive moat. | HIGH | Must study Roenbaeck's reference implementation and encode rules into Data Architect and Veteran Reviewer prompts. No other tool provides Anchor Modeling expertise through AI agents. |
| **OpenCode skills for reusable capabilities** | Beyond agents, scaffold `.opencode/skills/` with reusable capabilities: YAML spec validation, naming convention checking, Mermaid diagram generation from specs. Skills are passive knowledge resources agents invoke on demand. | MEDIUM | OpenCode skills use `SKILL.md` files in `.opencode/skills/<name>/SKILL.md`. This gives agents access to structured capabilities without putting everything in the system prompt. Defers complexity from prompt to skill. |
| **opencode.json project configuration** | Scaffold an `opencode.json` that configures the agent team: default agent (Data Architect), model assignments per agent, tool permissions, MCP server configuration. Pre-configured so the team works out of the box. | MEDIUM | OpenCode merges project config with global config. We can set: `default_agent`, per-agent `model` overrides, `permission` defaults, `instructions` references. Users can customize later. |
| **Spec format bootstrapping** | Scaffold example YAML spec templates and JSON Schema for Anchor Model elements (anchors, attributes, ties, knots) so agents have a concrete target format when producing specs. Agents reference these schemas in their prompts. | MEDIUM | Creates `.warehouse/schemas/` or similar with the spec format. Agents know what format to produce output in. Without this, each agent invents its own output format. |
| **Dry-run mode (`--dry-run`)** | Show what would be created without creating it. Copier and cookiecutter both support this. Useful for reviewing scaffolded structure before committing. | LOW | Print file paths and sizes without writing. Low effort, high trust-building with cautious users. |
| **Output directory override (`--dir`)** | Allow scaffolding into a directory other than cwd. Useful for monorepos or non-standard project structures. | LOW | Default: cwd. `--dir path/to/project` overrides. Standard pattern from copier (`-d` flag) and cookiecutter. |

### Anti-Features (Deliberately NOT Building)

Features that seem good but create problems. Critical to document so scope stays controlled.

| Anti-Feature | Why Requested | Why Problematic | Alternative |
|--------------|---------------|-----------------|-------------|
| **Interactive prompts during init** | Cookiecutter and copier ask questions (project name, options, etc.). Seems natural for scaffolding. | Our agent team is opinionated and fixed. There is nothing to ask. Prompts add friction to the critical first experience. The whole point is: run one command, get working agents. Questions imply customization that does not exist yet. | Zero-config init. Customization happens by editing generated files after scaffolding. Add prompts later only if users genuinely need to choose between options (e.g., target database platform). |
| **Template engine / Jinja rendering** | Copier and cookiecutter use Jinja2 templates with variable substitution. Seems like the "right" way to scaffold. | Our files are not parameterized. Agent prompts are static markdown, not templates. Adding a template engine adds a dependency and complexity for zero benefit when files are not variable. | Write files directly from Python. If future milestones need parameterization (e.g., database dialect), add minimal templating then. YAGNI. |
| **Agent orchestration in the CLI** | "The CLI should coordinate the agents, manage debate rounds, track state." | The CLI scaffolds files. OpenCode runs agents. The user drives agents manually in OpenCode. Putting orchestration in the CLI creates a parallel runtime that conflicts with OpenCode's agent system. Clear separation: CLI writes files, OpenCode runs agents. | Encode orchestration guidance in agent system prompts. The Data Architect agent's prompt tells it how to invoke other agents, manage debate flow, and track decisions. The orchestration IS the prompt. |
| **Runtime dependency on OpenCode** | "Check if OpenCode is installed, validate version compatibility, auto-configure." | Creates a hard dependency on OpenCode's internals. OpenCode may change its CLI, installation method, or config format. The scaffolded files should work with any compatible version. | Scaffold files that conform to OpenCode's documented format. Mention OpenCode version compatibility in README/docs. Do not import or shell out to OpenCode. |
| **Auto-updating scaffolded files** | Copier's killer feature is `copier update` -- pull upstream template changes into existing projects. | Premature for milestone 1. Users will customize agent prompts. Auto-update would overwrite customizations. Need a merge strategy before offering updates. | Version the scaffolded files with a `.warehouse-architect-version` marker. Future milestone can add `architect update` with diff-based merging. |
| **Plugin system for custom agents** | "Let users define their own agents through a plugin API." | Premature abstraction. We do not know what users want to customize yet. Plugin APIs are expensive to design, impossible to change, and constrain internal evolution. | Users edit the generated markdown files directly. Markdown is the API. If patterns emerge for customization, extract a plugin system in v2+. |
| **Web UI / dashboard** | "Show agent conversations, debate history, model visualizations in a browser." | Out of scope. This is a CLI tool. OpenCode provides the conversation UI. Adding a web UI is a different product. | OpenCode's TUI is the interface. Agent conversations happen there. If visualization is needed, generate static Mermaid diagrams from specs. |
| **Multi-provider agent support** | "Support Claude, GPT, Gemini, Llama agents simultaneously." | OpenCode handles model routing. The CLI scaffolds agent definitions. Agent definitions can specify `model` in frontmatter, but the CLI should not try to configure or validate provider credentials. | Set reasonable model defaults in agent frontmatter (e.g., `anthropic/claude-sonnet-4-5`). Users change models in OpenCode config or agent frontmatter. |

## Feature Dependencies

```
[pip install warehouse-architect]
    |
    v
[architect init]
    |
    +--creates--> [.opencode/agents/*.md]  (6 agent definitions)
    |                 |
    |                 +--requires--> [Valid OpenCode frontmatter format]
    |                 +--requires--> [Domain expertise in system prompts]
    |                 +--requires--> [CLP debate protocol in prompts]
    |                 +--requires--> [Anchor Modeling rules in prompts]
    |
    +--creates--> [AGENTS.md]  (project-level rules)
    |                 |
    |                 +--requires--> [ADSS methodology description]
    |                 +--requires--> [CLP workflow overview]
    |                 +--requires--> [Naming conventions]
    |
    +--creates--> [opencode.json]  (project configuration)
    |                 |
    |                 +--requires--> [Agent team configuration]
    |                 +--requires--> [Default model selection]
    |                 +--requires--> [Tool permissions]
    |
    +--creates--> [.warehouse/schemas/]  (spec format templates)
    |                 |
    |                 +--requires--> [Anchor Model element definitions]
    |                 +--enables---> [Consistent agent output format]
    |
    +--creates--> [.opencode/skills/]  (optional, reusable capabilities)
                      |
                      +--requires--> [agents to exist first]
                      +--enhances--> [agent capabilities]

[Agent quality] ----requires----> [Prompt engineering depth]
                                       |
                                       +--requires--> [Anchor Modeling domain expertise]
                                       +--requires--> [CLP workflow expertise]
                                       +--requires--> [Debate protocol design]
                                       +--requires--> [Study of Roenbaeck reference]
```

### Dependency Notes

- **Agent definitions are the critical path.** Everything else (AGENTS.md, opencode.json, schemas, skills) supports agent quality but the agents ARE the product.
- **Prompt engineering gates everything.** The CLI is trivial (copy files to disk). The value is entirely in what those files contain. Prompt quality requires deep domain research.
- **AGENTS.md is force-multiplier.** OpenCode loads project rules into every agent context. Shared methodology context in AGENTS.md means each agent prompt can be shorter and more focused on its role.
- **opencode.json reduces user setup.** Without it, users must manually configure agents, models, and permissions. With it, `architect init` produces a fully configured project.
- **Skills decouple complexity from prompts.** Instead of putting spec validation logic in the Data Architect's system prompt, put it in a skill. The agent invokes the skill when needed.
- **Spec schemas enable consistent output.** Without a defined spec format, each agent invents its own. With schemas, agents can reference the expected output format.

## Milestone 1 Definition (init + agents)

### Launch With (v1 Milestone 1)

Minimum viable product -- validate that scaffolded agents provide genuine value through CLP debate in OpenCode.

- [ ] **`architect init` command** -- single command creates all files in cwd, no prompts, clear output
- [ ] **6 agent definition files** -- Data Architect, System Analyst, Business Analyst, Data Engineer, Analytics Engineer, Veteran Reviewer in `.opencode/agents/`
- [ ] **Data Architect as entry point** -- primary agent users talk to, orchestrates debate through prompt guidance
- [ ] **CLP debate protocol in prompts** -- agents argue through Conceptual -> Logical -> Physical stages
- [ ] **Anchor Modeling rules in prompts** -- Data Architect and Veteran Reviewer encode methodology rules
- [ ] **AGENTS.md with project rules** -- shared ADSS/Anchor Modeling context for all agents
- [ ] **opencode.json configuration** -- agent team pre-configured with model defaults and permissions
- [ ] **Idempotent re-run** -- skip existing files with warning, `--force` to overwrite
- [ ] **`--help` with usage examples** -- standard CLI help via Typer
- [ ] **Error handling** -- human-readable errors for common failure modes

### Add After Validation (v1.x)

Features to add once the agent experience is validated with real users.

- [ ] **`--dry-run` flag** -- trigger: users want to preview before scaffolding
- [ ] **`--dir` flag for output directory** -- trigger: monorepo users need non-cwd scaffolding
- [ ] **OpenCode skills** -- trigger: agent prompts become too long, need to extract reusable capabilities
- [ ] **Spec schema bootstrapping** -- trigger: agents need a concrete output format reference
- [ ] **`architect update`** -- trigger: prompt improvements need to reach existing projects
- [ ] **Agent personality configuration** -- trigger: users want conservative vs aggressive design philosophy
- [ ] **`architect generate` command (DAS scripts)** -- trigger: milestone 2 begins
- [ ] **`architect generate` command (DAR scripts)** -- trigger: milestone 2+ continues

### Future Consideration (v2+)

Features to defer until agent experience is proven and user base established.

- [ ] **Plugin system for custom agents** -- why defer: premature abstraction, markdown files ARE the API
- [ ] **Interactive init prompts** -- why defer: nothing to ask yet, adds friction to onboarding
- [ ] **Template engine integration** -- why defer: files are not parameterized in milestone 1
- [ ] **Auto-update with merge** -- why defer: need conflict resolution strategy first
- [ ] **Web-based agent conversation viewer** -- why defer: different product, OpenCode provides the UI
- [ ] **CI/CD integration (GitHub Actions)** -- why defer: validate manual workflow first

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority | Milestone |
|---------|------------|---------------------|----------|-----------|
| `architect init` command (Typer) | HIGH | LOW | P1 | M1 |
| 6 agent markdown files | HIGH | HIGH (prompt eng) | P1 | M1 |
| CLP debate protocol in prompts | HIGH | HIGH (design) | P1 | M1 |
| Anchor Modeling rules in prompts | HIGH | HIGH (domain) | P1 | M1 |
| AGENTS.md project rules | HIGH | MEDIUM | P1 | M1 |
| opencode.json configuration | MEDIUM | LOW | P1 | M1 |
| Idempotent re-run / --force | MEDIUM | LOW | P1 | M1 |
| --help with examples | MEDIUM | LOW | P1 | M1 |
| Error handling | MEDIUM | LOW | P1 | M1 |
| --dry-run flag | LOW | LOW | P2 | M1.x |
| --dir output directory | LOW | LOW | P2 | M1.x |
| OpenCode skills | MEDIUM | MEDIUM | P2 | M1.x |
| Spec schema bootstrapping | MEDIUM | MEDIUM | P2 | M1.x |
| architect update command | MEDIUM | HIGH | P2 | M1.x |
| architect generate (DAS) | HIGH | HIGH | P1 | M2 |
| architect generate (DAR) | HIGH | HIGH | P1 | M2+ |

**Priority key:**
- P1: Must have for milestone launch
- P2: Add when possible after milestone validation

## Competitor Feature Analysis

### CLI Scaffolding Tools Comparison

| Feature | Cookiecutter | Copier | Yeoman | skills-cli | Warehouse Architect |
|---------|-------------|--------|--------|------------|---------------------|
| **Language** | Python | Python | JavaScript | Python | Python |
| **Config format** | JSON | YAML | JavaScript | YAML frontmatter | None (opinionated) |
| **Interactive prompts** | Yes (required) | Yes (required) | Yes (required) | No | No (deliberate) |
| **Template engine** | Jinja2 | Jinja2 | EJS | None | None (deliberate) |
| **Update existing projects** | No | Yes (killer feature) | No | No | Future (architect update) |
| **Migrations** | No | Yes | No | No | Future |
| **Post-generation hooks** | Yes | Yes (tasks) | Yes | No | No (not needed) |
| **Validation** | Minimal | Schema-based | Programmatic | YAML frontmatter | OpenCode format compliance |
| **Zero-config mode** | No | No | No | Yes (skills create) | Yes (core UX) |
| **Domain-specific output** | Generic | Generic | Generic | Agent skills | Data warehouse agents |

**Key insight:** Every major scaffolding tool assumes the output is parameterized and requires user input. Our tool is the opposite: output is fixed, opinionated, and requires zero input. This is a feature, not a limitation. The value is in the content of the generated files, not in the generation mechanism.

### AI Agent Setup Tools Comparison

| Feature | opencode-template | rothnic/opencode-agents | skills-cli | Warehouse Architect |
|---------|-------------------|------------------------|------------|---------------------|
| **Agent count** | 10 (generic dev) | Variable (custom) | N/A (skills not agents) | 6 (domain-specific) |
| **Domain expertise** | Generic (frontend, backend, security) | Generic (user-defined) | Generic | Deep (DW design, Anchor Modeling) |
| **Debate protocol** | None | Orchestrator pattern | N/A | CLP debate with synthesis |
| **Multi-agent coordination** | Implicit (@mentions) | Orchestrator + sub-agents | N/A | Data Architect synthesizes |
| **Methodology enforcement** | None | None | None | Anchor Modeling rules, CLP gates |
| **Scaffolding tool** | Manual copy | CLI wizard | `skills create` | `architect init` |
| **Project configuration** | Manual | Partial | N/A | Full (opencode.json + AGENTS.md) |

**Key insight:** Existing OpenCode agent templates provide generic development roles. No template provides domain-specific data warehouse design expertise with structured debate protocols. This is the blue ocean.

### Data Warehouse Tool Feature Comparison (Agent Context)

| Capability | Ellie.ai | ER/Studio | Anchor Modeler | Warehouse Architect |
|------------|----------|-----------|----------------|---------------------|
| **AI-assisted design** | Single LLM | ERbert assistant | None | Multi-agent debate |
| **Anchor Modeling** | No | Partial (generic) | Full (reference) | Full (AI-guided) |
| **CLP workflow** | Yes | Yes | Implicit | Yes (enforced via agents) |
| **Multi-perspective analysis** | No | No | No | Yes (SA vs BA debate) |
| **Methodology critique** | No | No | No | Yes (Veteran Reviewer) |
| **Setup mechanism** | SaaS onboarding | Enterprise install | Web tool | `pip install` + `architect init` |
| **User drives process** | AI drives | User drives | User drives | User drives with AI guidance |

**Key insight:** No data warehouse design tool uses multi-agent debate for modeling decisions. Ellie.ai uses a single AI assistant. We provide six specialized agents who argue from different perspectives. The user remains in control, but has access to structured expert debate.

## Domain-Specific Considerations

### OpenCode Agent Format (Verified)

Based on official OpenCode documentation (HIGH confidence):

**Agent files:** Markdown with YAML frontmatter in `.opencode/agents/`
- Required field: `description` (string)
- Optional fields: `model` (provider/model-id), `temperature` (0.0-1.0), `top_p`, `tools` (object), `permission` (object with edit/bash/webfetch), `hidden` (boolean), `color` (string), `disable` (boolean), `steps` (number), `mode` (subagent/primary/all)
- Body: system prompt in markdown

**Project rules:** `AGENTS.md` in project root (loaded into all agent contexts)

**Project config:** `opencode.json` in project root (merges with global config)

**Skills:** `.opencode/skills/<name>/SKILL.md` with YAML frontmatter (name, description required)

### CLI Scaffolding UX (Verified)

Based on clig.dev and scaffolding tool analysis (HIGH confidence):

- **Zero-config is the gold standard** for opinionated tools. If there is nothing to ask, do not ask.
- **Always confirm what was created.** List files, show structure, suggest next steps.
- **Provide `--help` with examples.** Show the most common invocation first.
- **Handle re-runs gracefully.** Skip existing, warn, offer `--force`.
- **Errors are conversations.** Tell users what went wrong and what to do next.
- **Suggest next steps after completion.** "Now open OpenCode and start a conversation with @data-architect."

### Prompt Engineering as Product

The CLI is trivial. The prompts are the product. Research indicates:

- **Agent personas must be deeply specific.** Generic "you are a data architect" prompts produce generic output. The prompts must encode specific Anchor Modeling rules, CLP checkpoint criteria, debate positions, and decision frameworks.
- **Debate protocol must be explicit.** Without explicit protocol in prompts, agents will agree with each other (premature consensus). System Analyst and Business Analyst must have opposing default positions.
- **Methodology rules must be verifiable.** The Veteran Reviewer needs concrete anti-pattern checklists, not vague "review for quality" instructions.
- **Shared context (AGENTS.md) reduces prompt size.** Put methodology overview, naming conventions, and workflow rules in AGENTS.md. Agent prompts focus on role-specific behavior.

## Sources

**OpenCode Agent Format (HIGH confidence):**
- [Agents | OpenCode](https://opencode.ai/docs/agents/) -- Official agent definition format, frontmatter fields, directory structure
- [Config | OpenCode](https://opencode.ai/docs/config/) -- Project configuration format, opencode.json structure
- [Agent Skills | OpenCode](https://opencode.ai/docs/skills/) -- Skills format, SKILL.md structure, discovery mechanism
- [Rules | OpenCode](https://opencode.ai/docs/rules/) -- AGENTS.md format, project-level rules, instruction loading

**CLI Scaffolding Tools (HIGH confidence):**
- [Command Line Interface Guidelines](https://clig.dev/) -- CLI UX best practices, init command patterns
- [Copier Documentation](https://copier.readthedocs.io/en/stable/creating/) -- Template creation, update mechanism, migration support
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html) -- Hooks, prompts, conditional generation
- [Typer Documentation](https://typer.tiangolo.com/) -- Python CLI framework, auto-help, type hints

**OpenCode Agent Templates (MEDIUM confidence):**
- [Agent Directory | opencode-template | DeepWiki](https://deepwiki.com/julianromli/opencode-template/2.1-agent-directory) -- Example agent organization, role categories
- [rothnic/opencode-agents](https://github.com/rothnic/opencode-agents/blob/main/docs/custom-coding-agents.md) -- Custom agent setup, orchestrator pattern
- [skills-cli | PyPI](https://pypi.org/project/skills-cli/) -- Skills management CLI, create/validate/install commands

**Agent Scaffolding Concepts (MEDIUM confidence):**
- [Agent scaffolding: Architecture, types and enterprise applications | ZBrain](https://zbrain.ai/agent-scaffolding/) -- Agent scaffolding definition, architecture patterns
- [The Complete Guide to Agentic Coding Frameworks in 2026](https://ralphwiggum.org/blog/agentic-coding-frameworks-guide) -- Framework landscape, CLI patterns

**Data Warehouse Design (HIGH confidence from prior research):**
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) -- Methodology rules, 6NF patterns
- [Anchor Modeling - DBMS Tools](https://dbmstools.com/tools/anchor-modeling) -- Tool features, DDL generation, platform support
- [Ellie.ai](https://www.ellie.ai/) -- Competitor: single AI assistant for data modeling

**Python CLI Packaging (HIGH confidence):**
- [Building a Package - Typer](https://typer.tiangolo.com/tutorial/package/) -- pip-installable CLI with entry points
- [PyScaffold Documentation](https://pyscaffold.org/en/stable/usage.html) -- Python project scaffolding patterns

---
*Feature research for: Warehouse Architect -- Python CLI + OpenCode Agent Scaffolding*
*Researched: 2026-02-07*
*Confidence: HIGH -- CLI patterns well-established, OpenCode format verified from official docs, domain expertise requirements clear*
