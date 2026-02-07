# Project Research Summary

**Project:** Warehouse Architect
**Domain:** AI-driven data warehouse design tool with multi-agent orchestration and Anchor Modeling specialization
**Researched:** 2026-02-07
**Confidence:** MEDIUM-HIGH

## Executive Summary

Warehouse Architect is a Claude Code skill that uses multi-agent debate to design data warehouses using the Anchor Modeling methodology. This is a specialized tool in an emerging space: combining debate-based AI consensus with a niche (but powerful) data modeling approach that excels at temporal tracking and schema evolution. The research reveals three critical success factors: (1) proper multi-agent debate orchestration with bounded iterations and genuine critique, (2) enforcement of CLP (Conceptual-Logical-Physical) workflow stages to prevent premature optimization, and (3) deterministic code generation from validated specifications rather than probabilistic LLM output.

The recommended approach is TypeScript-based using the Claude Agent SDK, with a clear architectural separation: AI agents handle creative modeling decisions through structured debate, validated YAML specifications serve as source of truth, and deterministic template-based generators produce platform code. The biggest risk is applying Anchor Modeling's 6NF normalization too broadly—it's powerful for frequently-changing temporal entities but creates performance problems for static reference data. The mitigation is selective application: use Anchor Modeling for core business entities with independent temporal tracking needs, traditional modeling for everything else.

This is a blue ocean opportunity. No existing tool combines multi-agent debate with Anchor Modeling specialization. Competitors (Ellie.ai, ER/Studio) use single AI assistants and focus on Data Vault 2.0 or Kimball methodologies. The niche positioning enables deep specialization rather than attempting to support all modeling approaches.

## Key Findings

### Recommended Stack

TypeScript provides end-to-end type safety from specification validation through code generation. The Claude Agent SDK offers first-class multi-agent support with built-in tools (Read, Write, Edit, Bash, Task) and subagent spawning. Zod enables schema-as-type where specification validation and TypeScript interfaces are unified—critical for a specification-driven system. Nunjucks templates provide template inheritance for SQL generation with 95% Jinja compatibility (important for dbt integration). This stack prioritizes deterministic generation: LLMs debate and create specifications, templates transform specs to code.

**Core technologies:**
- **Claude Agent SDK + TypeScript**: Multi-agent orchestration with compile-time type safety for specs and generated code
- **Zod**: Runtime validation where schemas ARE types, enabling bidirectional spec validation and TypeScript inference
- **Nunjucks**: SQL template engine with inheritance support and Jinja compatibility for dbt model generation
- **Mermaid**: Diagram-as-code generation for GitOps workflows and automated documentation pipelines

**Critical decision:** Deterministic generation over LLM generation for code. Agents produce YAML specs, templates produce SQL/dbt. This separates creative (debate) from mechanical (generation) concerns, enabling testing and repeatability.

### Expected Features

Research reveals a clear feature landscape: table stakes features users assume exist, differentiators that provide competitive advantage, and anti-features that seem good but create problems.

**Must have (table stakes):**
- Schema visualization (ER diagrams) — all data modeling tools provide this
- DDL generation for target platforms — standard output expected
- YAML/JSON specification export — modern tools use declarative formats for version control
- Basic CLP workflow support — data professionals expect conceptual → logical → physical progression
- Model versioning — change tracking critical for production warehouses
- Validation & linting — catch design errors before deployment

**Should have (competitive advantage):**
- Multi-agent debate architecture — distinct personas (Data Architect, Engineer, Analyst) collaboratively design through structured disagreement; research shows 30-35% productivity gains
- Anchor Modeling specialization — purpose-built for anchor/attribute/tie/knot with 6NF and temporal support; competitors focus on Data Vault/Kimball
- Business domain → model extraction — LLM-powered NER to parse requirements and extract entities/relationships
- dbt model generation — bridge design → implementation gap with configs, tests, docs
- Historization pattern library — pre-built templates for SCD Types 1-7, bi-temporal, event sourcing
- Schema evolution non-destructive guarantees — append-only migrations preserve backward compatibility
- Diagram-as-code native — first-class Mermaid/PlantUML support for GitOps

**Defer (v2+):**
- Source question → model reverse engineering — complex LLM prompt engineering
- Data Vault 2.0 import bridge — niche use case, adds significant complexity
- Visual drag-drop editor — anti-feature that limits GitOps, doesn't scale to large models
- Real-time collaborative editing — conflicts with structured debate process, async PR workflow better
- Support all methodologies — dilutes specialization; focus on Anchor Modeling excellence

**Anti-features to explicitly avoid:**
- Drag-drop visual UI as primary interface (breaks GitOps, hard to diff, reduces agent autonomy)
- Fully autonomous deployment (schema changes need human approval for safety)
- One-size-fits-all templates (every business is unique; guide through process don't dictate)

### Architecture Approach

The architecture follows a layered design with clear separation of concerns: orchestration layer manages CLP workflow state and spawns agents, agent layer conducts debates and writes specifications, specification layer serves as source of truth in YAML format, and generator layer produces deterministic code from specs.

**Major components:**

1. **Workflow State Machine (Orchestrator)** — Coordinates CLP progression through stage gates, manages checkpoints between stages, spawns debate agents via Task tool. Maintains `.warehouse/state.yaml` to track current stage, completed checkpoints, pending debates, and decision history.

2. **Multi-Agent Debate System** — Four specialized agents: System Analyst (technical feasibility focus), Business Analyst (business value focus), Data Architect (synthesis and Anchor Modeling rules), Veteran Reviewer (quality critique). Implements DAB (Debate-Argumentation-Balance) pattern with bounded iterations and convergence metrics to prevent infinite loops.

3. **YAML Specification Files** — Source of truth organized by CLP stage (conceptual/, logical/, physical/). Defines anchors, attributes, ties, knots with progressive refinement. Validated against schema to prevent spec-generator drift.

4. **Checkpoint Validation System** — Quality gates between CLP stages. Validates Anchor Modeling methodology compliance (6NF normalization, temporal strategy), completeness criteria, and prevents progression until passing. Creates audit trail in `.warehouse/checkpoints/`.

5. **Deterministic Code Generators** — Template-based transformation from validated specs to platform code (SQL DDL, dbt models, documentation). Not AI agents—scripts/templates using Nunjucks for predictable, testable output.

**Key pattern:** Specification-driven generation. Specs are source of truth, code is generated artifact. Never reverse-engineer specs from code. This enables version control, platform portability, and deterministic regeneration.

### Critical Pitfalls

Research identified 10 critical pitfalls with detailed prevention strategies. The top 5 that must be addressed in early phases:

1. **LLM Intent Errors That Look Valid** — AI-generated SQL executes successfully but returns wrong results (15-20% off). Prevention: Multi-agent validation of SQL, test against known-good results, explicit business rules in context, never trust execution success alone. **Address in Phase 1.**

2. **Multi-Agent Infinite Debate Loops** — Agents stuck in circular disagreement consuming tokens without convergence. Prevention: Bounded iterations with quality gates, convergence metrics, external variation signals, mediator agent with tie-breaking authority after N rounds. **Address in Phase 1.**

3. **Premature Physical Modeling (Skipping CLP Stages)** — Teams jump to physical schema without conceptual/logical modeling, creating unmaintainable schemas requiring complete rewrites. Prevention: Enforce stage gates, document entity-to-table mappings, generate conceptual first then derive logical then physical. **Address in Phase 2.**

4. **Anchor Modeling Over-Application (6NF Performance Traps)** — Applying 6NF universally creates table explosions with joins that optimizers can't eliminate. Prevention: Use Anchor Modeling selectively for temporal, frequently-changing entities only; test join elimination on target database with real queries before committing; set table count budget per entity. **Address in Phase 3.**

5. **Schema Specification Drift (Generator-Spec Mismatch)** — Spec and generator fall out of sync, generators ignore fields, silent failures. Prevention: JSON Schema/Zod validation for all specs with version checking, generate schema from generator or vice versa (single source of truth), validate-only mode to report unrecognized fields. **Address in Phase 4.**

Additional critical pitfalls: premature consensus in debates (rubber-stamping), Claude context amnesia across sessions, hallucinated schema elements, deterministic vs probabilistic mismatch, missing historization strategy.

## Implications for Roadmap

Based on research dependencies and risk mitigation, I recommend a 5-phase structure that addresses architectural foundations before adding complexity:

### Phase 1: Foundation (Orchestration + Debate Core)

**Rationale:** Multi-agent debate orchestration is the architectural foundation. Must establish bounded iteration, convergence metrics, and debate quality mechanisms before any modeling work. Without this, the differentiated value proposition (multi-agent consensus) fails. Research shows this is the highest-risk area—infinite loops and premature consensus are critical pitfalls that cannot be fixed retroactively.

**Delivers:**
- CLP state machine workflow with stage tracking
- Basic 4-agent debate system (System Analyst, Business Analyst, Data Architect, Veteran Reviewer)
- Bounded iteration logic with convergence metrics
- Debate artifact recording (traceability)
- Context persistence framework (prevent amnesia)
- State management (`.warehouse/state.yaml`)

**Addresses:**
- Multi-agent debate architecture (differentiator from FEATURES.md)
- Basic CLP workflow support (table stakes)
- Agent personality configuration foundation

**Avoids:**
- Infinite debate loops (Pitfall 2) — bounded iterations + convergence from day one
- Premature consensus (Pitfall 6) — adversarial incentives, distinct personas
- Context amnesia (Pitfall 7) — persistent context files and bootstrap process

**Stack elements:** Claude Agent SDK, TypeScript, Node.js
**Research flag:** STANDARD PATTERNS — Multi-agent orchestration is well-documented in 2026 research; follow Google's 8 patterns and Claude SDK documentation.

---

### Phase 2: CLP Workflow + Specification System

**Rationale:** With debate orchestration working, establish the modeling workflow that differentiates this tool. CLP stage enforcement prevents the #3 critical pitfall (premature physical modeling). Specification system becomes source of truth for all downstream generation. This phase enables validation that specs match business domain (prevent hallucination).

**Delivers:**
- Three-stage CLP workflow (Conceptual → Logical → Physical) with stage gates
- Checkpoint validation system between stages
- YAML specification schema (anchors, attributes, ties, knots)
- Zod-based spec validation
- Conceptual entity extraction from business descriptions
- Domain model verification (prevent hallucinated schemas)

**Addresses:**
- CLP workflow support (table stakes) — enforced stage progression
- YAML/JSON specification export (table stakes)
- Validation & linting (table stakes)
- Business domain → model extraction (differentiator)

**Avoids:**
- Premature physical modeling (Pitfall 3) — stage gates prevent skipping
- Hallucinated schema elements (Pitfall 8) — domain verification agent
- Missing historization strategy (Pitfall 10) — historization decided during conceptual modeling

**Stack elements:** Zod for validation, js-yaml for parsing, custom YAML schemas
**Research flag:** NEEDS DEEPER RESEARCH — Anchor Modeling conceptual-to-logical translation rules. No TypeScript reference implementation exists. May need research spike on Anchor Modeler (Java) translation logic.

---

### Phase 3: Anchor Modeling Implementation

**Rationale:** With validated specs and CLP workflow, implement the core domain logic: Anchor Modeling rules. This phase operationalizes the methodology that makes this tool specialized. Critical to prevent over-application (Pitfall 4) by establishing selective application criteria and performance testing.

**Delivers:**
- Anchor/attribute/tie/knot classification logic in Data Architect agent
- 6NF normalization rules with selective application criteria
- Temporal/bi-temporal modeling patterns
- Historization pattern library (SCD Types 1-7, event sourcing)
- Logical checkpoint validation (methodology compliance)
- Performance testing framework (join elimination verification)

**Addresses:**
- Anchor Modeling core constructs (MVP requirement)
- Historization pattern library (differentiator)
- Schema evolution non-destructive guarantees (differentiator)

**Avoids:**
- Anchor Modeling over-application (Pitfall 4) — selective criteria + performance tests
- Missing historization strategy (Pitfall 10) — pattern library with guidance

**Stack elements:** Anchor Modeling rules encoded in agent prompts and validation logic
**Research flag:** NEEDS DEEPER RESEARCH — Anchor Modeling 6NF translation rules, join elimination behavior on Snowflake/PostgreSQL/BigQuery, performance characteristics at scale. Research spike: "Survey Anchor Modeler implementation for TypeScript translation rules."

---

### Phase 4: Deterministic Code Generation

**Rationale:** Specs validated, methodology applied—now generate executable artifacts. Architectural decision: deterministic template-based generation, not LLM generation. This addresses Pitfall 9 (wrong abstraction choice) and enables testing/repeatability. Version control between specs and generators prevents drift (Pitfall 5).

**Delivers:**
- SQL DDL generator for Snowflake + PostgreSQL (Nunjucks templates)
- Template inheritance for anchor/attribute/tie/knot patterns
- Generator versioning and spec compatibility checking
- Validate-only mode (detect unrecognized fields)
- Physical checkpoint validation (generated code compiles)
- Prettier integration for consistent SQL formatting

**Addresses:**
- DDL generation (table stakes) — Snowflake and PostgreSQL initially
- Diagram-as-code native (differentiator) — Mermaid ER diagrams from specs

**Avoids:**
- Spec-generator drift (Pitfall 5) — versioning + validation-only mode
- Deterministic vs probabilistic mismatch (Pitfall 9) — templates not LLMs

**Stack elements:** Nunjucks, Handlebars (for non-SQL), Prettier, prettier-plugin-sql
**Research flag:** STANDARD PATTERNS — SQL DDL generation is well-understood; dbt uses Jinja templates. Follow dbt patterns for Nunjucks compatibility.

---

### Phase 5: dbt + Platform Extensions

**Rationale:** With core workflow proven (Foundation → CLP → Anchor → DDL), extend to implementation tooling and additional platforms. dbt integration bridges the design-to-implementation gap for Analytics Engineers. Additional database platforms expand applicability.

**Delivers:**
- dbt model generator (staging, intermediate, marts)
- dbt YAML configs (tests, relationships, docs)
- BigQuery and Redshift SQL dialect support
- PlantUML diagram generation (enterprise C4/UML diagrams)
- Migration script generation (schema evolution)
- Anomaly detection and best practice linting

**Addresses:**
- dbt model generation (differentiator) — implementation-ready artifacts
- Additional target platforms (v1.x feature) — BigQuery, Redshift
- Anomaly detection (v1.x feature) — AI-powered design critique

**Avoids:**
- LLM intent errors (Pitfall 1) — dbt test generation catches logical errors

**Stack elements:** dbt-specific Nunjucks templates, SQL dialect adapters
**Research flag:** NEEDS RESEARCH — dbt project structure conventions, Jinja compatibility testing with Nunjucks templates, dbt-specific features (sources, tests, docs generation patterns).

---

### Phase Ordering Rationale

The sequence follows dependency chains revealed in research:

1. **Foundation first** because multi-agent debate is the core differentiator and highest-risk component. Cannot add debate circuit breakers retroactively.

2. **CLP workflow second** because it structures how agents interact with modeling stages. Prevents premature optimization that research shows is a critical failure mode.

3. **Anchor Modeling third** because it requires validated specs (from Phase 2) to have something to apply rules to. Research shows over-application is a major risk, requiring selective criteria established in this phase.

4. **Generation fourth** because deterministic generators consume validated specs (Phase 2) with methodology applied (Phase 3). Must separate creative (debate) from mechanical (generation).

5. **Extensions last** because dbt/additional platforms are valuable but not core to proving the concept. These can be added incrementally once the debate → CLP → Anchor → DDL pipeline works.

**Research-informed groupings:**
- Phases 1-2 establish the workflow (orchestration + stages)
- Phases 3-4 implement the domain logic (methodology + generation)
- Phase 5 extends to real-world toolchains (dbt + platforms)

### Research Flags

**Phases needing deeper research during planning:**

- **Phase 2 (CLP Workflow):** Anchor Modeling conceptual-to-logical translation rules. No TypeScript reference implementation; must study Java Anchor Modeler and academic papers. Consider research spike: "Map Anchor Modeler translation rules to TypeScript implementation."

- **Phase 3 (Anchor Implementation):** Join elimination behavior on target databases. Research shows 6NF can be problematic, but theory says modern optimizers handle it. Need actual testing with Snowflake, PostgreSQL, BigQuery query patterns. Research spike: "Profile join elimination on Snowflake/Postgres/BigQuery with Anchor Model queries."

- **Phase 5 (dbt Integration):** Nunjucks-Jinja compatibility edge cases. Research shows 95% compatibility but need to validate with actual dbt Core execution. What dbt-specific features should be generated (sources, tests, docs blocks)? Research spike: "Test Nunjucks-generated dbt models with dbt Core; identify incompatibilities."

**Phases with standard patterns (skip research-phase):**

- **Phase 1 (Foundation):** Multi-agent orchestration patterns well-documented in 2026 research. Google's 8 patterns, Claude SDK subagent documentation, debate-based consensus papers provide clear guidance.

- **Phase 4 (Generation):** Template-based SQL generation is established pattern. dbt Core uses Jinja for this exact purpose. Follow dbt patterns for DDL templates.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Claude Agent SDK is authoritative source; TypeScript/Zod/Nunjucks are mature with clear documentation. Version compatibility verified. Only gap: no TypeScript Anchor Modeling library (expected—we're building it). |
| Features | MEDIUM | Feature landscape clear from competitor analysis (Ellie.ai, ER/Studio) and general data modeling tools. Multi-agent debate differentiator validated by 2026 research showing 30-35% productivity gains. Uncertainty: market size for Anchor Modeling niche. |
| Architecture | HIGH | Multi-agent patterns well-documented (Google's 8 patterns, debate-based consensus research). CLP workflow is industry standard. Specification-driven generation proven by dbt. Clear separation of concerns. Risk: orchestration complexity underestimated. |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls validated by multiple sources (LLM SQL errors, infinite debate loops, 6NF performance). Some extrapolated to Anchor Modeling context. Mitigation strategies sourced from multi-agent research and data warehouse design literature. Uncertainty: which pitfalls manifest first in practice. |

**Overall confidence:** MEDIUM-HIGH

The core technologies and architectural patterns are well-documented and proven. The uncertainty lies in domain-specific application: Anchor Modeling implementation details and 6NF performance characteristics require validation through prototyping. The multi-agent debate system is cutting-edge but 2026 research provides clear implementation guidance.

### Gaps to Address

**Anchor Modeling Translation Rules:**
- **Gap:** No TypeScript implementation of Anchor Modeler's formalized translation rules (conceptual model → 6NF physical schema).
- **Mitigation:** Study [Roenbaeck's Anchor Modeler GitHub](https://github.com/Roenbaeck/anchor) Java implementation, validate against academic papers, test generated schemas against Anchor Modeler output as oracle.
- **Timeline:** Phase 2 research spike before logical modeling implementation.

**Join Elimination Reality:**
- **Gap:** Theory says modern optimizers eliminate 6NF joins; practice may differ by database platform and query pattern.
- **Mitigation:** Build performance testing framework in Phase 3, create canonical query suite, profile on Snowflake/PostgreSQL/BigQuery, establish selective application criteria based on measured results.
- **Timeline:** Phase 3, must complete before committing to full 6NF strategy.

**Multi-Agent Context Management:**
- **Gap:** How to persist context when agents produce intermediate specs consumed by downstream agents across sessions.
- **Mitigation:** Use Claude Agent SDK's session management + Tasks feature, investigate file-based state in `.warehouse/state.yaml`, implement context hierarchy (critical rules in system prompt, project details in early context).
- **Timeline:** Phase 1 foundation, test with multi-session workflow early.

**Nunjucks-Jinja Compatibility:**
- **Gap:** 95% compatibility claimed but edge cases unknown; dbt Core execution with Nunjucks-generated templates needs validation.
- **Mitigation:** Test suite of generated dbt models executed with dbt Core, document incompatibilities, provide migration guidance if needed.
- **Timeline:** Phase 5, validate before shipping dbt integration.

**Debate Quality Metrics:**
- **Gap:** How to measure whether debates are producing genuine critique vs rubber-stamping?
- **Mitigation:** Track substantive changes between rounds (schema modifications, new arguments), measure argument novelty (detect repetition), set minimum quality thresholds for checkpoint passage.
- **Timeline:** Phase 1 foundation, instrument from day one to gather data.

## Sources

### Primary (HIGH confidence)

**Official Documentation:**
- [Claude Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview) — Multi-agent orchestration, Task tool, subagent patterns
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) — Skill structure, command patterns
- [Zod Documentation](https://zod.dev/) — Schema validation, TypeScript type inference
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) — Methodology rules, 6NF patterns
- [Anchor Modeler GitHub](https://github.com/Roenbaeck/anchor) — Reference implementation (Java)
- [dbt SQL Models Documentation](https://docs.getdbt.com/docs/build/sql-models) — Template patterns, Jinja usage

**2026 Multi-Agent Research:**
- [Google's Eight Essential Multi-Agent Design Patterns - InfoQ](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/) — Sequential, coordinator, fan-out/gather patterns
- [How to Build Multi-Agent Systems: Complete 2026 Guide](https://dev.to/eira-wexford/how-to-build-multi-agent-systems-complete-2026-guide-1io6) — Architecture patterns, context management
- [Patterns for Democratic Multi-Agent AI: Debate-Based Consensus - Medium](https://medium.com/@edoardo.schepis/patterns-for-democratic-multi-agent-ai-debate-based-consensus-part-1-8ef80557ff8a) — DAB pattern implementation

### Secondary (MEDIUM confidence)

**Competitive Intelligence:**
- [Ellie.ai - Enterprise Data Modeling Powered by AI](https://www.ellie.ai/) — Competitor feature analysis, single-agent approach
- [17 Best Data Warehousing Tools in 2026 | Integrate.io](https://www.integrate.io/blog/17-best-data-warehousing-tools-and-resources/) — Market landscape
- [Top Data Warehouse Automation Tools 2026 Compared](https://barc.com/reviews/data-warehouse-automation/) — Feature comparison

**Data Warehouse Design:**
- [Conceptual vs Logical vs Physical Data Models - ThoughtSpot](https://www.thoughtspot.com/data-trends/data-modeling/conceptual-vs-logical-vs-physical-data-models) — CLP workflow standard
- [Data Modeling for Modern DWH: Data Vault 2.0 vs Kimball, Inmon, Anchor](https://www.analyticscreator.com/blog/how-to-choose-the-right-data-modeling-techniques-for-your-data-warehouse) — Methodology comparison

**Pitfalls & Anti-Patterns:**
- [We Evaluated 50,000+ LLM-Generated SQL Queries. Here's What Actually Breaks.](https://www.usedatabrain.com/blog/llm-sql-evaluation) — LLM intent errors, 15-20% accuracy issues
- [FREE-MAD: Consensus-Free Multi-Agent Debate - arXiv](https://arxiv.org/pdf/2509.11035) — Premature consensus prevention
- [6 data warehouse design mistakes to avoid - Computer Weekly](https://www.computerweekly.com/tip/6-data-warehouse-design-mistakes-to-avoid) — Premature optimization, normalization traps

### Tertiary (LOW-MEDIUM confidence)

**Code Generation:**
- [AI-Generated dbt Models Are Actually Good Now - Medium](https://medium.com/@reliabledataengineering/ai-generated-dbt-models-are-actually-good-now-i-tested-50-of-them-b87bd82bc7c2) — dbt generation patterns (needs validation)
- [From YAML to SQL: Generating Physical Models and Diagrams from Metadata - Medium](https://medium.com/towards-data-engineering/from-yaml-to-sql-generating-physical-models-and-diagrams-from-metadata-10324add354f) — Specification-driven generation examples

**Context Management:**
- [Claude Code Keeps Forgetting Your Project? Here's the Fix (2026) - DEV](https://dev.to/kiwibreaksme/claude-code-keeps-forgetting-your-project-heres-the-fix-2026-3flm) — Context persistence strategies
- [The 4-Step Protocol That Fixes Claude Code Agent's Context Amnesia - Medium](https://medium.com/@ilyas.ibrahim/the-4-step-protocol-that-fixes-claude-codes-context-amnesia-c3937385561c) — Bootstrap patterns

---

*Research completed: 2026-02-07*
*Ready for roadmap: YES*
*Next step: Requirements definition using this synthesis as foundation*
