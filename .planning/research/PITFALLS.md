# Pitfalls Research

**Domain:** Python CLI + OpenCode.ai Agents for Data Warehouse Design (ADSS/Anchor Modeling)
**Researched:** 2026-02-07 (post-pivot from TypeScript Claude Code skill to Python CLI + OpenCode agents)
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: Shallow Immutability Illusion with frozen=True

**What goes wrong:**
The project mandates pure functional Python with immutable data using `@dataclass(frozen=True)`. But `frozen=True` only prevents field reassignment -- nested mutable objects (lists, dicts) inside frozen dataclasses can still be mutated. A spec dataclass containing `attributes: list[Attribute]` is "frozen" but the list is fully mutable. Code that appends to `spec.attributes` silently violates the immutability contract. Bugs appear as unexpected state changes that bypass the frozen guarantee.

**Why it happens:**
Python's `frozen=True` enforces shallow immutability only. There is no deep freeze in the stdlib. Developers assume "frozen" means "truly immutable" and write code that passes frozen dataclasses around, trusting they cannot change. The 2.4x instantiation overhead of frozen dataclasses creates pressure to skip freezing on "internal" data structures, creating an inconsistent immutability boundary.

**How to avoid:**
- Use tuples and frozensets instead of lists and sets in all frozen dataclasses. Enforce via a linting rule or `__post_init__` validation using `object.__setattr__` to convert collections.
- Define a project convention: all collection fields must be `tuple[T, ...]` or `frozenset[T]`, never `list` or `set`.
- Use `dataclasses.replace()` for functional updates instead of mutation. Build helper functions for common transformations (add attribute, remove tie, etc.).
- Consider `NamedTuple` for simpler data carriers where the tuple guarantee of immutability is stronger.
- Write a custom mypy plugin or use a lint rule to flag `list` or `dict` fields in frozen dataclasses.

**Warning signs:**
- Frozen dataclass fields typed as `list[...]` or `dict[...]` in type hints
- Tests that mutate dataclass contents after construction
- `object.__setattr__` appearing outside `__post_init__`
- Intermittent test failures where data appears "changed" between function calls

**Phase to address:**
Phase 1 (Foundation) -- Establish the immutable data convention before any domain types are defined. Retrofitting tuple-based collections onto existing list-based dataclasses is painful.

---

### Pitfall 2: "No Classes" Rule Collides with Python's stdlib

**What goes wrong:**
The constraint says "no classes, pure functions + immutable data." But Python's stdlib and ecosystem assume OOP pervasively. Exceptions are classes. Context managers require `__enter__`/`__exit__`. `pathlib.Path` is a class. `argparse.ArgumentParser` returns namespace objects. Click uses decorator-based class registration. File handles are objects. The "no classes" rule creates constant friction with every stdlib interaction, leading to either: (a) creeping OOP through "allowed exceptions" that erode the constraint, or (b) awkward wrapper functions that obscure intent.

**Why it happens:**
Python is fundamentally multi-paradigm with OOP deeply embedded. A strict "no classes" rule works in languages designed for it (Haskell, Clojure) but fights Python's grain. The rule's intent (immutability, testability, simplicity) is sound, but the implementation "zero classes" is too absolute for Python.

**How to avoid:**
- Redefine the constraint precisely: "No behavior-bearing classes. Dataclasses/NamedTuples for data only (no methods except `__post_init__` for validation). All behavior lives in module-level pure functions. Stdlib classes used as-is at boundaries."
- Create an explicit boundary layer: functions that accept/return stdlib objects (Path, argparse.Namespace) but convert to frozen dataclasses at the boundary.
- Document the "allowed OOP" list: frozen dataclasses, NamedTuples, Exceptions, context managers via `contextlib.contextmanager`, and stdlib types.
- For error handling: use a Result type pattern (tuple of `(value, error)` or a simple `Result` frozen dataclass) instead of raising exceptions inside pure functions. Reserve exceptions for truly exceptional I/O failures at boundaries.

**Warning signs:**
- Increasing number of "exceptions to the no-classes rule"
- Wrapper functions that do nothing but call a method on a stdlib object
- Team debates about whether `@dataclass(frozen=True)` counts as "a class"
- Test files importing classes despite the "no classes" rule

**Phase to address:**
Phase 1 (Foundation) -- Must be resolved before writing any code. The exact boundary between "functional core" and "imperative shell" must be defined in coding conventions.

---

### Pitfall 3: OpenCode.ai Platform Instability

**What goes wrong:**
OpenCode releases approximately every 1-3 days (20 versions in two weeks as of early 2026). The platform is in early development with features that "may change, break, or be incomplete." Agent definition format, frontmatter fields, directory conventions, and the skill/plugin system are all actively evolving. The project scaffolds agent definitions into `.opencode/agents/` -- if OpenCode changes the agent format, directory structure, or registration mechanism, every user who ran `architect init` has stale/broken agent files in their project.

**Why it happens:**
OpenCode explicitly warns it is "not yet ready for production use." Recent changelog shows reverted features (Trinity model support removed), rapid iteration on agent prompting (developer messages vs. user messages), and active bugs in the plugin system. Targeting an unstable platform means building on shifting sand.

**How to avoid:**
- Pin to a specific OpenCode version range in documentation. Test agent definitions against that version.
- Implement an `architect update-agents` command that regenerates agent definitions in-place, preserving any user customizations (via merge strategy, not overwrite).
- Keep agent definitions as thin as possible: minimal frontmatter, system prompt in the markdown body, no dependency on advanced features (skills, plugins, modes) until they stabilize.
- Use only the documented stable features: `description`, `model`, `tools`, and markdown body content. Avoid `mode`, `plugins`, `hidden`, `steps`, and other fields marked experimental.
- Abstract the agent format behind a Python data structure so the project can target multiple formats (OpenCode, Claude Code, Cursor) without rewriting agent logic.
- Monitor the OpenCode changelog (`opencode.ai/changelog`) in CI -- at minimum, run agent validation tests against the latest OpenCode release weekly.

**Warning signs:**
- OpenCode changelog entries that modify agent loading, frontmatter parsing, or directory discovery
- User bug reports that `architect init` produces agents that OpenCode doesn't recognize
- OpenCode renaming `.opencode/` directory conventions (they already support both singular and plural subdirectory names for backwards compatibility)
- Agent features you depend on appearing in OpenCode's "experimental" section

**Phase to address:**
Phase 1 (Foundation) -- Agent scaffolding is the core Milestone 1 deliverable. Must design for platform instability from day one. Include version detection and compatibility checking.

---

### Pitfall 4: Scaffold Drift (Bundled Agent Templates vs. CLI Version)

**What goes wrong:**
Users run `architect init` at version 1.0, which scaffolds agent definitions. Later, `architect` updates to version 2.0 with improved agents (better prompts, new debate patterns, fixed methodology rules). Users who already ran `init` have stale v1.0 agents. There is no upgrade path. Users don't know their agents are outdated. The CLI version and agent version diverge silently.

**Why it happens:**
Scaffolding tools generate files and then abandon them. Unlike a library (where updating the dependency updates behavior), scaffolded files are owned by the user's project. The CLI has no mechanism to detect, diff, or update previously scaffolded files. This is the fundamental tension of scaffold-based tools: generate once vs. keep current.

**How to avoid:**
- Embed a version marker in every scaffolded file: `<!-- warehouse-architect: v1.2.0 -->` in agent markdown frontmatter or as a comment.
- Implement `architect check` command that: reads version markers from scaffolded files, compares against current CLI version, reports which agents are outdated and what changed.
- Implement `architect update-agents` that: shows a diff of what will change, applies updates to non-customized files, flags conflicts in user-customized files (like git merge conflicts).
- Use a layered architecture: scaffolded agents `{% include %}` or reference shared instructions from a central file that CAN be updated independently. Keep user customizations in a separate file that imports the base.
- Never put methodology rules directly in agent prompts. Put them in a `references/` file that agents read at runtime. Updating references doesn't require re-scaffolding.

**Warning signs:**
- Users reporting different behavior with same business inputs (different agent versions)
- No version marker in scaffolded files
- `architect init` overwrites without prompting when run twice
- Agent definitions containing inline methodology rules instead of referencing external documents

**Phase to address:**
Phase 1 (Foundation) -- Design the scaffolding system with update-ability from the start. Retrofitting version tracking onto existing scaffolded files requires a migration.

---

### Pitfall 5: Dynamic Git-Tag Versioning Breaks in CI/CD

**What goes wrong:**
The project uses dynamic versioning from git tags (no hardcoded version strings). This works locally but fails in CI/CD when: (a) GitHub Actions checkout uses `fetch-depth: 1` (shallow clone, no tags), (b) the build happens on a Dependabot PR with no tag context, (c) `uv build` is run in a detached HEAD state after checkout, (d) the version falls back to `0.0.0` silently and publishes a broken package to PyPI.

**Why it happens:**
Dynamic versioning (setuptools-scm, uv-dynamic-versioning, hatch-vcs) relies on git metadata that CI environments don't always provide. Shallow clones lack tag history. Detached HEAD states confuse tag resolution. The fallback version mechanism is meant to prevent build failures but can silently publish incorrect versions.

**How to avoid:**
- Configure GitHub Actions with `fetch-depth: 0` (full clone) AND `fetch-tags: true` in the checkout step.
- Set a fallback version in `pyproject.toml` that is obviously wrong (e.g., `fallback-version = "0.0.0.dev0+unknown"`) so accidental publishes are immediately visible.
- Add a CI validation step that checks the resolved version matches the git tag before publishing: `python -c "from importlib.metadata import version; v = version('warehouse-architect'); assert v != '0.0.0.dev0+unknown', f'Bad version: {v}'"`.
- Never publish from a workflow that doesn't trigger on a tag push. Use `on: push: tags: ['v*']` as the publish trigger.
- Test the version resolution in a separate CI job before the publish job.
- Use `uv-dynamic-versioning` (latest 0.13.0) which is designed for uv/hatch projects specifically, rather than `setuptools-scm` which may have compatibility issues with uv's build system.

**Warning signs:**
- Local `uv build` produces correct version but CI produces `0.0.0`
- Published packages on TestPyPI with version `0.0.0.dev0` or similar
- CI logs showing "tag not found" or "no version detected" warnings
- Version mismatch between `__version__` and the package metadata version

**Phase to address:**
Phase 1 (Foundation) -- CI/CD pipeline setup. Must be validated with a TestPyPI publish before the first real release.

---

### Pitfall 6: Anchor Modeling Over-Application (6NF Performance Traps)

**What goes wrong:**
Applying Anchor Modeling's 6NF decomposition universally creates an explosion of tables. A single business entity like "Customer" becomes 10-15 tables (one per attribute). Queries require massive joins that modern optimizers cannot always eliminate. Performance degrades catastrophically on databases that don't support join elimination. Cognitive overhead makes the system unmaintainable.

**Why it happens:**
Anchor Modeling's theoretical elegance is appealing. The agents may recommend 6NF for everything because the methodology rules say to. Teams read that "modern databases use join elimination" and assume it works universally. They apply 6NF to reference data, dimensions that never change, and concepts that don't need temporal tracking.

**How to avoid:**
- Encode selective application criteria in the Data Architect agent's prompt: "Use Anchor Modeling for temporal, frequently-changing business entities ONLY. Use traditional modeling for static reference data, lookup tables, and rarely-changing dimensions."
- Set a table count budget per entity (e.g., max 7-10 tables). If exceeded, the Veteran Reviewer agent must flag it.
- Require the debate to explicitly justify 6NF for each entity: "Entity X uses Anchor because attributes change independently at different rates."
- Use knot tables for static reference data with low cardinality instead of full anchor treatment.
- Include performance testing guidance in generated specs: "Test join elimination on target database before committing to this design."

**Warning signs:**
- Single entity queries joining 15+ tables
- Agents recommending anchors for lookup/reference data
- No knot tables in the model (everything is an anchor)
- Performance complaints on generated schemas

**Phase to address:**
Phase 3 (Anchor Modeling) per the roadmap. Build selective application criteria into agent prompts and validation rules.

---

### Pitfall 7: LLM Intent Errors in Agent Debate Output

**What goes wrong:**
AI agents in the debate produce modeling recommendations that sound correct but contain subtle errors: wrong entity classification (attribute vs. anchor), incorrect temporal strategy, relationships that don't match the business domain, or hallucinated entities from the LLM's training data that don't exist in the user's business. The debate process validates internal consistency but not external correctness.

**Why it happens:**
LLMs pattern-match against common data models they've seen (e-commerce, CRM, ERP). When under-specified, they fill gaps with plausible-sounding but incorrect elements. The System Analyst and Business Analyst agents may debate vigorously but both start from the same flawed assumption. Multi-agent debate validates coherence, not truth.

**How to avoid:**
- Require the Data Architect agent to trace every modeling element to a specific user input (business description, source schema field, or business question). No untraceable elements.
- Include a "domain verification" step in the debate: "List all entities. For each, cite the exact user input that justifies its existence."
- Have the Veteran Reviewer specifically check for hallucinated elements: "Flag any entity, attribute, or relationship not explicitly mentioned or directly derivable from user inputs."
- Implement a controlled vocabulary: agents can only use terms from the user's domain glossary, not introduce new terminology.
- Present debate output to the user with explicit traceability: "Customer anchor justified by: business description paragraph 2, source schema CRM.customers table."

**Warning signs:**
- Agents introducing entities the user never mentioned
- Standard-sounding elements (user_preferences, audit_log) without business justification
- Debate reaching consensus quickly (no genuine disagreement)
- Agent output using generic terminology instead of the user's domain language

**Phase to address:**
Phase 1 (Foundation) -- Traceability and domain verification must be built into the debate protocol from the start.

---

### Pitfall 8: Multi-Agent Infinite Debate Loops

**What goes wrong:**
System Analyst and Business Analyst agents get stuck in circular disagreement, consuming tokens without converging. Agents repeat similar arguments, make trivial modifications, or oscillate between two positions. The user waits while agents burn context window and API costs without producing a decision.

**Why it happens:**
Without bounded iterations, convergence metrics, or mediator tie-breaking, agents lack mechanisms to break deadlock. OpenCode agents are user-driven (not orchestrated by the CLI), so there is no automated circuit breaker. The agents' instructions must encode debate termination logic in their prompts.

**How to avoid:**
- Encode maximum debate rounds in the Data Architect agent's instructions: "After 3 rounds of debate without convergence, synthesize the best elements from both positions and present a recommendation with explicit tradeoffs."
- Include convergence detection in agent prompts: "If the System Analyst and Business Analyst are repeating the same arguments, escalate to the user for a decision."
- Give the Veteran Reviewer tie-breaking authority: "If debate has not converged after review, the Veteran Reviewer makes a binding recommendation."
- Design debate artifacts so each round must introduce NEW information or arguments. Repeating a previous argument signals convergence failure.

**Warning signs:**
- Debate transcripts showing repeated similar critiques across rounds
- Agent responses getting longer without new substance
- Users reporting "stuck" agents that keep going back and forth
- Token consumption for a single modeling decision exceeding budget

**Phase to address:**
Phase 1 (Foundation) -- Debate termination logic must be in agent prompts from day one. Cannot be added retroactively without rewriting all agent definitions.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Using `list` in frozen dataclasses | Natural Python, no friction | Shallow immutability, mutation bugs | Never -- use `tuple` from day one |
| Allowing classes "just for this one thing" | Quick fix for stdlib integration | Erosion of functional constraint, inconsistent codebase | Only at documented boundary layer |
| Hardcoding OpenCode agent format | Faster scaffolding implementation | Locked to one platform, no portability | Early prototype only, refactor by Phase 1 end |
| Skipping `architect update-agents` | Simpler initial release | Users stuck on stale agents, no upgrade path | v0.1 only, must ship update before v1.0 |
| Inline methodology rules in prompts | Easier to write agent definitions | Rules duplicated across agents, inconsistent updates | Never -- extract to reference files |
| Publishing without version validation | Simpler CI pipeline | Silent 0.0.0 publishes to PyPI | Never -- add validation step immediately |
| Skipping TestPyPI dry run | Faster release cycle | Broken packages discovered by users on real PyPI | Never -- always test on TestPyPI first |
| Using `dict` for spec data | Flexible, no schema overhead | No type safety, silent key errors, untestable | Prototype only, migrate to frozen dataclasses immediately |
| Mocking stdlib in tests | Easier to isolate pure functions | Tests pass but integration breaks, mock drift | Only for I/O boundaries, never for pure logic |

## Integration Gotchas

Common mistakes when connecting to external services and platforms.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenCode agent discovery | Assuming `.opencode/agents/` is the only location | OpenCode merges from multiple locations (global, project, env var). Test with all discovery paths. |
| OpenCode agent format | Using advanced frontmatter fields (`steps`, `plugins`, `hidden`) | Stick to stable fields: `description`, `model`, `tools`, `permission`, `color`. Avoid experimental features. |
| UV build system | Using `setuptools-scm` with UV/Hatchling backend | Use `uv-dynamic-versioning` which is designed for UV/Hatch projects. setuptools-scm may conflict with Hatchling. |
| PyPI trusted publishing | Using reusable GitHub Actions workflows | Trusted publishing does not work from reusable workflows. Must use a non-reusable workflow with `id-token: write` permission. |
| PyPI publishing | Building and publishing in the same job | Separate build and publish into different jobs. Prevents privilege escalation with trusted publishing. |
| Git shallow clone in CI | `fetch-depth: 1` (default) loses tag history | Use `fetch-depth: 0` and `fetch-tags: true` for dynamic versioning. |
| YAML spec files | Using PyYAML's `yaml.load()` without `Loader` | Always use `yaml.safe_load()`. `yaml.load()` executes arbitrary Python code. |
| Makefile venv activation | `source .venv/bin/activate` in Makefile recipe | Each recipe runs in a new shell. Use `.venv/bin/python` or `.venv/bin/pytest` directly. |
| Package data in wheel | Expecting non-Python files to be included automatically | Explicitly configure package data in `pyproject.toml`. Inspect built wheel with `zipinfo` before publishing. |
| Agent file encoding | Assuming UTF-8 for all markdown agent files | Explicitly set encoding. Windows users may have different defaults. |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| frozen dataclass 2.4x instantiation overhead | Slow spec processing with many entities | Profile early. Consider `NamedTuple` for hot paths. Use `__slots__=True` with frozen dataclasses. | 100+ entity specs with nested structures |
| `dataclasses.replace()` deep copy chain | Creating new objects for every small change | Batch updates with builder pattern (accumulate changes, create once) | Specs with 50+ attributes being modified iteratively |
| Recursive pure functions without tail call optimization | Stack overflow on deeply nested specs | Python has no TCO. Use iterative solutions with explicit stacks for tree traversals. | Spec hierarchies deeper than ~1000 levels |
| String template concatenation for SQL generation | Memory pressure with large schemas | Use streaming/generator-based template rendering | Schemas with 500+ tables |
| Loading all agent definitions into memory | Slow `architect init` on resource-constrained machines | Lazy loading, generate one agent at a time | Not a real risk at current scale (6 agents) |

## Security Mistakes

Domain-specific security issues beyond general concerns.

| Mistake | Risk | Prevention |
|---------|------|------------|
| YAML spec files containing database credentials | Credentials committed to git, exposed in generated SQL | Validate specs contain no credential-like strings. Use environment variable references in connection configs. |
| Agent prompts containing proprietary methodology details | Methodology IP exposed in user's `.opencode/` directory | Keep methodology rules at appropriate abstraction level. Detailed IP stays in the CLI package, not scaffolded files. |
| Generated SQL with string interpolation | SQL injection if generated DDL is used in dynamic contexts | All generated SQL should use parameterized patterns. Never interpolate user strings into DDL templates. |
| PyPI package with embedded API keys | API keys published to public PyPI | Pre-commit hook scanning for secrets. CI step to scan built wheel. Never store credentials in source. |
| OpenCode agents reading arbitrary filesystem paths | Agent reads sensitive files outside project scope | Limit agent tool permissions in frontmatter. Use `permission: ask` for filesystem operations outside project root. |

## UX Pitfalls

Common user experience mistakes for CLI scaffolding tools.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| `architect init` overwrites without warning | User loses customized agent definitions | Check for existing `.opencode/agents/`, prompt before overwrite, offer `--force` flag |
| No feedback during scaffolding | User thinks command hung | Print each file as it's created: "Created .opencode/agents/data-architect.md" |
| Unclear which OpenCode version is required | Agents fail with cryptic errors on wrong OpenCode version | Print required OpenCode version after init. Check OpenCode version if detectable. |
| `architect generate` fails with unhelpful error on missing specs | "FileNotFoundError" on first use | Check for spec files first, print: "No specs found. Run your agents in OpenCode first to produce specs." |
| Version mismatch between CLI and scaffolded agents | Silent behavior differences | `architect check` command that validates agent version markers against CLI version |
| No way to preview what `init` will create | Users wary of running commands that modify their project | `architect init --dry-run` showing what files would be created/modified |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Frozen dataclasses:** All fields are frozen -- verify nested collections are immutable types (tuple, frozenset), not list/dict
- [ ] **Agent scaffolding:** Files created in `.opencode/agents/` -- verify OpenCode actually loads and recognizes them by running OpenCode with the agents
- [ ] **Dynamic versioning:** `uv build` produces correct version locally -- verify CI produces correct version too (test with shallow clone, detached HEAD, no tags)
- [ ] **PyPI package:** Installs with `pip install` -- verify it also installs with `uv pip install` and that the `architect` console script entry point works
- [ ] **Makefile `check` target:** Runs lint+type+test -- verify it fails fast on first error and reports which step failed
- [ ] **Agent debate termination:** Max rounds configured -- verify agents actually stop (test by providing contradictory inputs that force disagreement)
- [ ] **Pure functional code:** No classes in module -- verify dataclasses used for data only (no methods beyond `__post_init__`), no class inheritance
- [ ] **Spec validation:** Schema validates all fields -- verify generators actually use all validated fields (no silently ignored fields)
- [ ] **Template version markers:** Present in scaffolded files -- verify `architect check` actually reads and compares them
- [ ] **Package wheel contents:** Code is included -- verify non-Python files (agent templates, reference docs) are also included by inspecting with `zipinfo`

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Shallow immutability bugs | MEDIUM | Audit all frozen dataclasses for mutable fields. Replace `list` with `tuple`, `dict` with `types.MappingProxyType` or frozen dataclass. Update all construction sites. |
| "No classes" rule erosion | LOW | Audit codebase for class definitions. Extract behavior to module functions. Convert data classes to frozen dataclasses. Document the boundary layer. |
| OpenCode format breaking change | MEDIUM | Update agent templates in CLI. Ship new CLI version. Users run `architect update-agents`. Provide migration guide. |
| Scaffold drift (stale agents) | MEDIUM | Implement `architect update-agents` retroactively. Add version markers to existing files via migration script. |
| CI publishes wrong version | HIGH | Yank the bad version from PyPI (`pip install --yank`). Fix CI pipeline. Re-tag and re-publish. Communicate to users. Cannot un-publish from PyPI, only yank. |
| 6NF over-application | MEDIUM-HIGH | Identify low-change entities. Consolidate to traditional modeling. Keep 6NF for genuinely temporal entities. Regenerate from updated specs. |
| LLM intent errors in debate | MEDIUM | Add traceability requirements to agent prompts. Re-run debates with updated instructions. Validate output against user inputs. |
| Infinite debate loops | LOW | Add max round limits to agent prompts. Implement convergence detection. Restart with mediator tie-breaking. |
| Dynamic versioning silent fallback | LOW | Add version validation to CI. Fix shallow clone. Re-build with correct tags. |
| Missing package data in wheel | LOW | Update `pyproject.toml` package data config. Rebuild and re-publish. |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Shallow immutability | Phase 1: Foundation | Lint rule or mypy plugin flags `list`/`dict` in frozen dataclasses |
| "No classes" rule collision | Phase 1: Foundation | Coding conventions document with explicit boundary layer definition |
| OpenCode platform instability | Phase 1: Foundation | Agent definitions tested against pinned OpenCode version in CI |
| Scaffold drift | Phase 1: Foundation | Version markers in every scaffolded file, `architect check` command |
| Dynamic versioning CI failure | Phase 1: Foundation | CI validation step confirms version before publish; TestPyPI dry run passes |
| Anchor Modeling over-application | Phase 3: Anchor Modeling | Selective application criteria in agent prompts; table count budget per entity |
| LLM intent errors | Phase 1: Foundation | Traceability requirement in debate protocol; verification step in agent flow |
| Infinite debate loops | Phase 1: Foundation | Max round limits in agent prompts; convergence detection instructions |
| Spec-generator drift | Phase 4: Code Generation | Schema validation on all specs; validate-only mode in generators |
| Missing historization strategy | Phase 2: CLP Workflow | Historization decided at conceptual level; checkpoint validates temporal strategy |
| PyPI publishing errors | Phase 1: Foundation | Trusted publisher configured; separate build/publish jobs; version validation |
| Package content errors | Phase 1: Foundation | Wheel inspection step in CI; install-and-test step before publish |

## Sources

**Pure Functional Python:**
- [Functional Programming HOWTO -- Python 3.14 docs](https://docs.python.org/3/howto/functional.html)
- [When are classes (thinking OOP) too much? -- Python Discussions](https://discuss.python.org/t/when-are-classes-thinking-oop-too-much/77026)
- [Python as functional programming language -- Python Discussions](https://discuss.python.org/t/python-as-functional-programming-language/38402)
- [Avoiding Common Pitfalls in Python Functional Programming -- Moldstud](https://moldstud.com/articles/p-avoiding-common-pitfalls-in-python-functional-programming-with-practical-tips-and-insights)
- [Functional vs Imperative Programming in Python -- Medium](https://medium.com/@denis.volokh/functional-vs-imperative-programming-in-python-a-practical-guide-aba1eb40652d)

**Frozen Dataclass Immutability:**
- [dataclasses -- Python 3.14 docs](https://docs.python.org/3/library/dataclasses.html)
- [Statically enforcing frozen data classes -- Redowan's Reflections](https://rednafi.com/python/statically-enforcing_frozen_dataclasses/)
- [How to achieve Partial Immutability with Python? -- Medium](https://noklam-data.medium.com/how-to-achieve-partial-immutability-with-python-dataclasses-or-attrs-0baa0d818898)
- [Semi-immutable Python objects with frozen dataclasses -- TestDriven.io](https://testdriven.io/tips/671b59e7-ba72-4201-82d4-473c8e594c55/)
- [Static-only frozen data classes -- Python Discussions](https://discuss.python.org/t/static-only-frozen-data-classes-or-other-ways-to-avoid-runtime-overhead/46968)

**OpenCode.ai Platform:**
- [Agents -- OpenCode Docs](https://opencode.ai/docs/agents/)
- [Config -- OpenCode Docs](https://opencode.ai/docs/config/)
- [OpenCode Changelog](https://opencode.ai/changelog)
- [OpenCode GitHub](https://github.com/opencode-ai/opencode)
- [OpenCode: an Open-source AI Coding Agent -- InfoQ](https://www.infoq.com/news/2026/02/opencode-coding-agent/)
- [Agent System -- DeepWiki](https://deepwiki.com/sst/opencode/3.2-agent-system)

**UV / Dynamic Versioning:**
- [uv-dynamic-versioning -- PyPI](https://pypi.org/project/uv-dynamic-versioning/)
- [How to add dynamic versioning to uv projects -- PyDevTools](https://pydevtools.com/handbook/how-to/how-to-add-dynamic-versioning-to-uv-projects/)
- [UV Python Package Manager Quirks -- Plotly Blog](https://plotly.com/blog/uv-python-package-manager-quirks/)
- [FR: uv build accepts a dynamic package version argument -- GitHub Issue](https://github.com/astral-sh/uv/issues/8714)
- [Dynamic versioning with pyproject.toml -- GitHub Discussion](https://github.com/pypa/setuptools/discussions/3630)

**PyPI Publishing:**
- [Publishing with GitHub Actions CI/CD -- Python Packaging Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Common Python Packaging Mistakes -- jwodder](https://jwodder.github.io/kbits/posts/pypkg-mistakes/)
- [PyPI Trusted Publisher Troubleshooting -- PyPI Docs](https://docs.pypi.org/trusted-publishers/troubleshooting/)
- [pypa/gh-action-pypi-publish -- GitHub](https://github.com/pypa/gh-action-pypi-publish)

**TDD with Functional Python:**
- [Chicago and London TDD Styles for Functional Programming -- DEV](https://dev.to/jesterxl/chicago-and-london-tdd-styles-for-functional-programming-455h)
- [Modern Test-Driven Development in Python -- TestDriven.io](https://testdriven.io/blog/modern-tdd/)

**Data Warehouse Design:**
- [6 data warehouse design mistakes to avoid -- Computer Weekly](https://www.computerweekly.com/tip/6-data-warehouse-design-mistakes-to-avoid)
- [Anchor Modeling -- Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling)
- [Anchor Modeling -- Official Site](https://www.anchormodeling.com/)

**Error Handling in Functional Python:**
- [Python Functors and Monads -- ArjanCodes](https://arjancodes.com/blog/python-functors-and-monads/)
- [Beyond Try-Except: Python's Frontier of Error Handling -- PyConES 2024](https://pretalx.com/pycones-2024/talk/7TKB3L/)

---
*Pitfalls research for: Python CLI + OpenCode.ai Agents for Data Warehouse Design*
*Researched: 2026-02-07 (post-pivot)*
*Confidence: MEDIUM-HIGH -- Python functional programming pitfalls verified against official docs and community sources; OpenCode instability verified against live changelog; UV/versioning pitfalls verified against official issues and PyDevTools; Anchor Modeling pitfalls carried forward from pre-pivot research with HIGH confidence*
