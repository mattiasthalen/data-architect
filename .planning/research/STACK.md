# Technology Stack

**Project:** Warehouse Architect
**Domain:** Claude Code skill (multi-agent orchestration, YAML/JSON specs, deterministic code generation)
**Researched:** 2026-02-07
**Overall confidence:** MEDIUM-HIGH

## Executive Summary

Building a Claude Code skill for data warehouse design requires three distinct technology layers: the Claude Agent SDK for multi-agent orchestration, schema validation libraries for YAML/JSON specifications, and template engines for deterministic code generation. This stack prioritizes TypeScript for the full pipeline, enabling type safety from specification through code generation.

**Key decision:** TypeScript over Python for the agent layer. While Python dominates traditional AI development, the Claude Agent SDK has first-class TypeScript support, and TypeScript's type system provides compile-time validation for both specifications and generated code.

## Recommended Stack

### Core Agent Framework

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **@anthropic-ai/claude-agent-sdk** | latest | Multi-agent orchestration engine | Official Claude Agent SDK with built-in tools (Read, Write, Edit, Bash, Glob, Grep), subagent support, hooks system, and session management. First-class TypeScript support. | HIGH |
| **Node.js** | 18+ | Runtime environment | Required by Claude Agent SDK. LTS versions ensure stability. | HIGH |
| **TypeScript** | 5.5+ | Type system for agent code | Zod requires 5.5+. Provides compile-time safety for agent orchestration logic, skill definitions, and generated code. Officially surpassed Python in 2025 GitHub language report. | HIGH |

**Rationale:** The Claude Agent SDK is the authoritative framework for building Claude Code skills. It provides the same tools, agent loop, and context management that power Claude Code itself. The SDK handles tool execution automatically - you don't implement the tool loop. Built-in subagent support enables the multi-agent pattern (Data Architect, Data Engineer, etc.) without custom orchestration code.

### Schema Definition & Validation

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **Zod** | 4.3+ | Runtime schema validation with TypeScript inference | TypeScript-first design. Bidirectional: schema → TypeScript types AND TypeScript types → validation. Simpler API than Ajv for spec validation. Supports complex refinements for business rules (e.g., anchor modeling constraints). | HIGH |
| **js-yaml** | 4.1+ | YAML parsing/serialization | Standard YAML parser for JavaScript. Fast PyYAML port completely rewritten. Supports YAML 1.2 spec. | MEDIUM |
| **@types/js-yaml** | 4.0+ | TypeScript definitions for js-yaml | Provides type safety for YAML operations. | MEDIUM |

**Rationale:** Zod over Ajv because Zod's TypeScript-first design means schemas ARE types. With Ajv, you define JSON Schema separately and TypeScript types separately. With Zod, `const AnchorSchema = z.object({...})` defines both. `type Anchor = z.infer<typeof AnchorSchema>` extracts the TypeScript type. This is critical for a specification system where you want compile-time safety.

**Alternative:** Ajv (8.17+) is faster for high-volume validation and supports JSON Schema draft 2020-12. Choose Ajv if performance profiling shows Zod is a bottleneck, or if you need to publish JSON Schemas as an open standard. Ajv's JSONSchemaType utility provides TypeScript integration but requires maintaining parallel schema and type definitions.

### Template Engines for Code Generation

| Technology | Version | Purpose | When to Use | Confidence |
|------------|---------|---------|-------------|------------|
| **Nunjucks** | 3.2+ | SQL DDL generation, dbt model generation | Primary template engine. Template inheritance for reusable SQL blocks (e.g., base anchor table template → specific anchor instances). Built-in async support. Fine whitespace control for readable generated SQL. | MEDIUM-HIGH |
| **Handlebars** | 4.7+ | Simple substitution templates (Mermaid diagrams, config files) | Simpler syntax than Nunjucks. Use for non-SQL generation where inheritance isn't needed. Precompiled templates for faster runtime. | MEDIUM |
| **ts-morph** | 24+ | TypeScript code generation (if generating TypeScript utilities) | Programmatic AST manipulation. Use if generating TypeScript code alongside SQL. Wraps TypeScript Compiler API with ergonomic methods. | MEDIUM |

**Rationale:** Nunjucks over Handlebars for SQL generation because SQL generation requires template inheritance. You'll define a base template for anchor tables (with standard historization columns, effective dates, etc.), then extend it for each specific anchor. Nunjucks provides `{% extends %}` and `{% block %}` for this pattern. Handlebars requires custom helpers for inheritance.

**Why templates over AST?** SQL doesn't have a standard TypeScript AST library. Template-based generation is the ecosystem standard. For reference: dbt Core uses Jinja (Python's Nunjucks) for SQL generation.

**Whitespace matters in SQL.** Nunjucks provides explicit whitespace control (`{%- -%}` syntax) so generated SQL is readable in diffs and debugging. Handlebars doesn't.

### Anchor Modeling & Data Warehouse Standards

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| **Anchor Modeler (reference)** | N/A | Conceptual reference for Anchor Modeling | Open-source tool by Roenbaeck on GitHub. Study the formalized translation rules (anchor → table, attribute → table, tie → table, knot → table). DO NOT use as a runtime dependency - it's a Java Swing GUI tool. Extract the modeling rules, not the tool. | MEDIUM |
| **Custom YAML schema** | N/A | ADSS/Anchor specifications | Define your own YAML schema for anchors, attributes, ties, knots. Zod validates against your schema. Templates generate SQL from validated specs. | HIGH |

**Rationale:** Anchor Modeling has formalized rules for translating conceptual models to 6NF physical schemas. These rules are deterministic (1:1 mapping between symbols and tables). Your system should encode these rules in templates, not call external tools. The Anchor Modeler GitHub repo is a reference implementation - study it to understand the rules, then implement them in your templates.

**No off-the-shelf Anchor Modeling library for TypeScript exists.** You are building this. That's the value proposition of Warehouse Architect.

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| **mermaid** | 11+ | Diagram generation (ER diagrams, flowcharts) | Render conceptual models as Mermaid syntax, let Mermaid render to SVG. Supports class diagrams (for entities), ER diagrams (for relationships), sequence diagrams (for data flows). | HIGH |
| **prettier** | 3+ | Format generated SQL/YAML/TypeScript | Ensures consistent output formatting. Supports SQL via prettier-plugin-sql. | HIGH |
| **vitest** | 2+ | Testing framework | Fast, TypeScript-native, Vite-powered test runner. Test spec validation, template rendering, agent orchestration. | HIGH |
| **tsx** | 4+ | TypeScript execution without compilation | Run TypeScript skills directly. Faster iteration during development. | MEDIUM |

**Rationale:** Mermaid is the standard for programmatic diagram generation. Generate Mermaid syntax strings (simple text concatenation or templates), not SVG/PNG directly. Let downstream tools render. Mermaid syntax is human-readable, version-controllable, and widely supported (GitHub, GitLab, VSCode, Notion).

## Installation

```bash
# Core agent framework
npm install @anthropic-ai/claude-agent-sdk

# Schema validation
npm install zod js-yaml
npm install -D @types/js-yaml

# Template engines
npm install nunjucks handlebars

# AST manipulation (optional, if generating TypeScript code)
npm install ts-morph

# Supporting libraries
npm install mermaid prettier
npm install -D vitest tsx

# Prettier SQL plugin (optional, for SQL formatting)
npm install -D prettier-plugin-sql
```

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative | Confidence |
|----------|-------------|-------------|-------------------------|------------|
| Agent Framework | Claude Agent SDK (TypeScript) | Claude Agent SDK (Python) | Use Python if your team has no TypeScript experience. Python SDK has feature parity. Trade-off: lose compile-time type safety for specs and generated code. | HIGH |
| Schema Validation | Zod | Ajv + TypeScript JSON Schema | Use Ajv if performance profiling shows Zod is a bottleneck (Ajv is 10-100x faster for high-volume validation), or if you need to publish JSON Schemas as an open standard for external consumers. | HIGH |
| Template Engine (SQL) | Nunjucks | Handlebars | Use Handlebars only for simple templates without inheritance (e.g., config files, Mermaid diagrams). Not recommended for SQL generation. | HIGH |
| Template Engine (SQL) | Nunjucks | Jinja (via Python subprocess) | DON'T. Adds Python dependency for marginal syntax compatibility with dbt. Nunjucks syntax is 95% compatible with Jinja. Not worth the complexity. | HIGH |
| TypeScript AST | ts-morph | TypeScript Compiler API (direct) | Use direct Compiler API if you're already familiar with it and need maximum performance. ts-morph is a wrapper that trades ~10% performance for 90% better DX. | MEDIUM |
| Diagram Generation | Mermaid | D3.js | Use D3.js only if you need highly custom interactive visualizations. Mermaid covers 95% of data modeling diagrams (ER, class, sequence, flowchart). D3 requires significantly more code. | HIGH |
| Diagram Generation | Mermaid | PlantUML | Use PlantUML if you need UML-strict diagrams. Mermaid's UML support is "UML-like" not UML-compliant. Trade-off: PlantUML requires Java runtime. | MEDIUM |

## What NOT to Use

| Avoid | Why | Use Instead | Confidence |
|-------|-----|-------------|------------|
| **LangChain / LangGraph** | Adds unnecessary abstraction layer over Claude Agent SDK. The SDK already handles tool execution, agent loops, and context management. LangChain abstracts these, but you WANT direct control for a skill. | Claude Agent SDK directly | HIGH |
| **Prisma / TypeORM / Knex** | These are database ORMs for runtime query building. You're generating SQL files, not executing queries at runtime. ORMs generate SQL optimized for a query builder API, not human-readable DDL. | Template engines (Nunjucks) | HIGH |
| **Ejs** | Older template engine with embedded JavaScript (`<% %>` syntax). Less powerful than Nunjucks (no inheritance), less secure (code injection risk), and less popular (declining adoption). | Nunjucks or Handlebars | HIGH |
| **Mustache** | Logic-less templates. Too restrictive for SQL generation. You need conditionals (e.g., "if this anchor has historization, add effective date columns") and loops (e.g., "for each attribute, generate a column"). | Nunjucks or Handlebars | HIGH |
| **JSON Schema (standalone)** | Maintains separate schema and TypeScript types. You'll write the schema in JSON Schema format, then separately write TypeScript interfaces. With Zod, schema IS type. | Zod | HIGH |
| **io-ts** | Alternative TypeScript runtime validation library. Less ergonomic than Zod (more verbose syntax), smaller ecosystem, and lower adoption. | Zod | MEDIUM |
| **Anchor Modeler (as dependency)** | Java Swing GUI application, not a library. Cannot be imported or called from Node.js. Use it as a reference to understand Anchor Modeling rules, then implement those rules in your templates. | Custom templates encoding Anchor Modeling rules | HIGH |
| **Python for templates** | Requires Python subprocess calls from Node.js for marginal benefit (Jinja compatibility with dbt). Adds complexity, deployment dependencies, and subprocess overhead. Nunjucks syntax is 95% compatible with Jinja. | Nunjucks (JavaScript-native) | HIGH |

## Stack Patterns by Use Case

### If building for dbt Core integration

```bash
# Use Nunjucks (Jinja-like syntax)
npm install nunjucks

# Generate dbt models as .sql files with Jinja-compatible syntax
# Nunjucks supports {{ var }}, {% if %}, {% for %}, {% macro %} - 95% Jinja-compatible
```

**Why:** dbt Core uses Jinja for templating. Nunjucks syntax is 95% compatible. Generated dbt models should be valid Jinja so users can extend them with dbt macros.

**Caveat:** Nunjucks and Jinja have minor syntax differences (e.g., Jinja's `{% raw %}` vs Nunjucks `{% verbatim %}`). Test generated models with dbt Core to catch incompatibilities.

### If generating TypeScript data utilities alongside SQL

```bash
# Add ts-morph for TypeScript AST manipulation
npm install ts-morph

# Generate both SQL DDL and TypeScript interfaces from same spec
```

**Why:** ts-morph wraps TypeScript Compiler API with ergonomic methods. Generate TypeScript types for your data models programmatically.

**Example:** Generate TypeScript interfaces for each anchor's structure. Users can import these for type-safe data loading scripts.

### If building interactive diagram preview UI

```bash
# Add Mermaid with a renderer
npm install mermaid

# In browser context:
import mermaid from 'mermaid';
mermaid.initialize({ startOnLoad: true });
```

**Why:** Mermaid can render diagrams in the browser. Your skill could generate an HTML preview file with embedded Mermaid diagrams.

**Alternative:** Generate Mermaid syntax strings only. Let users render with their preferred tool (GitHub, VSCode Mermaid Preview, Mermaid Live Editor).

## Multi-Agent Orchestration Patterns

Based on 2026 research, three patterns for multi-agent orchestration:

### 1. Centralized Orchestration (Recommended for v1)

```typescript
// Main agent delegates to specialists
const result = await query({
  prompt: "Design a data warehouse for e-commerce orders",
  options: {
    allowedTools: ["Read", "Write", "Task"],
    agents: {
      "data-architect": {
        description: "Designs conceptual data models using Anchor Modeling",
        prompt: "You are a data architect specializing in Anchor Modeling...",
        tools: ["Read", "Write"]
      },
      "data-engineer": {
        description: "Generates SQL DDL from specifications",
        prompt: "You are a data engineer who generates SQL from YAML specs...",
        tools: ["Read", "Write"]
      }
    }
  }
});
```

**Why:** Simple to implement and debug. Main agent has full context. Single point of control. Suitable for MVP.

**Trade-off:** Main agent must orchestrate everything. Can hit context limits with many specialists.

### 2. Hierarchical Orchestration (Recommended for v2+)

```typescript
// Tiered structure: manager → team leads → specialists
// Example: Architect → Conceptual/Logical/Physical → Individual modelers
```

**Why:** Scales better. Each tier has focused context. Mirrors real-world data team structure.

**Trade-off:** More complex. Requires careful context passing between tiers.

### 3. Sequential Pipeline (For deterministic workflows)

```typescript
// Linear pipeline: Spec validation → Template selection → Code generation → Validation
// Use for deterministic generation steps
```

**Why:** Deterministic, testable, and cacheable. Each step has clear inputs/outputs.

**Trade-off:** Less flexible. Not suitable for exploratory design phases.

**Recommendation for Warehouse Architect:** Use Centralized for v1 (all agents report to main orchestrator). Migrate to Hierarchical if context limits become an issue. Use Sequential Pipeline for the generation phase (spec → SQL) after design is finalized.

## Version Compatibility Matrix

Based on research conducted February 2026:

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| TypeScript | 5.5+ | Zod 4.3+, Claude Agent SDK | Zod requires 5.5+. Use latest stable (5.7+ as of Feb 2026). |
| Node.js | 18+ (LTS) | Claude Agent SDK | SDK supports Node 18+. Recommend 20+ for performance. |
| Zod | 4.3+ | TypeScript 5.5+ | Zod 4.x introduced breaking changes from 3.x. Review migration guide. |
| Nunjucks | 3.2+ | Node.js 18+ | Stable API. No breaking changes expected. |
| ts-morph | 24+ | TypeScript 5.5+ | Tracks TypeScript Compiler API version. Update ts-morph when updating TypeScript. |

**Critical compatibility note:** Zod 4.x has breaking changes from 3.x:
- `.pick()` and `.omit()` on refined object schemas now throw errors (previously silently dropped refinements)
- New `.xor()` type for exclusive unions
- New `.looseRecord()` for pattern properties

Review [Zod 4.x changelog](https://github.com/colinhacks/zod/releases) before upgrading from 3.x.

## Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **tsx** | Execute TypeScript directly (development) | Faster iteration. Use `tsx your-skill.ts` instead of `tsc && node`. |
| **vitest** | Test framework | Fast, TypeScript-native, good for testing templates and specs. |
| **prettier** | Code formatting | Format generated SQL, YAML, TypeScript with consistent style. |
| **eslint** | Linting | Catch agent orchestration bugs (e.g., missing error handling). |
| **@typescript-eslint/parser** | TypeScript ESLint support | Required for ESLint with TypeScript. |

## Architecture Decision Records

### ADR-001: TypeScript over Python for full stack

**Decision:** Use TypeScript for agent orchestration, schema validation, and code generation.

**Rationale:**
- Claude Agent SDK has first-class TypeScript support (feature parity with Python)
- TypeScript type system provides compile-time validation for specs and generated code
- Single language for full pipeline (agent → validation → generation) reduces context switching
- TypeScript surpassed Python in 2025 GitHub language report
- Zod's TypeScript-first design (schema IS type) is a killer feature for specification systems

**Trade-offs:**
- Team must learn TypeScript if Python-only background
- Python has larger AI ecosystem (but not relevant for deterministic code generation)

**Alternative considered:** Python for agents + TypeScript for generation. Rejected because adds language boundary and loses type safety across agent → spec → code pipeline.

### ADR-002: Zod over Ajv for schema validation

**Decision:** Use Zod for runtime validation and TypeScript type inference.

**Rationale:**
- Schema and type are unified: `const S = z.object({})` + `type T = z.infer<typeof S>`
- No separate JSON Schema + TypeScript interface to maintain
- Refinements for business logic: `.refine(data => anchorHasHistorization(data), "Invalid anchor")`
- Better developer experience (ergonomic API)

**Trade-offs:**
- Ajv is 10-100x faster for high-volume validation
- Ajv supports JSON Schema draft 2020-12 (standard format)

**Mitigation:** Profile performance in real usage. If validation is a bottleneck (unlikely for spec files), migrate to Ajv. If external consumers need JSON Schema format, generate it from Zod with `zod-to-json-schema`.

### ADR-003: Nunjucks over Handlebars for SQL generation

**Decision:** Use Nunjucks as primary template engine for SQL DDL generation.

**Rationale:**
- Template inheritance: Define base anchor template, extend for specific anchors
- Built-in async support (if templates need to read files)
- Fine whitespace control: Generated SQL must be human-readable
- 95% Jinja syntax compatibility (dbt Core uses Jinja)

**Trade-offs:**
- Handlebars has simpler syntax
- Handlebars has larger ecosystem

**Mitigation:** Use Handlebars for simple non-SQL templates (Mermaid diagrams, config files). Nunjucks for SQL only.

### ADR-004: Template-based over AST-based SQL generation

**Decision:** Generate SQL using templates (Nunjucks), not AST manipulation.

**Rationale:**
- SQL doesn't have a standard TypeScript AST library
- Template-based is the ecosystem standard (dbt Core uses Jinja)
- Templates are easier to understand and debug than AST code
- SQL DDL structure is predictable (anchor → table with standard columns)

**Trade-offs:**
- AST-based would provide stronger guarantees (syntactically valid SQL)
- AST-based could compose transformations

**Mitigation:** Validate generated SQL with SQL parser (e.g., `node-sql-parser`) in tests. Templates are deterministic - test once per template, not per generation.

### ADR-005: Mermaid over PlantUML for diagram generation

**Decision:** Generate Mermaid syntax for diagrams.

**Rationale:**
- No Java runtime dependency (PlantUML requires Java)
- Mermaid is JavaScript-native
- Wide tooling support (GitHub, GitLab, VSCode, Notion)
- Human-readable syntax (versionable, diffable)
- Covers all needed diagrams: ER, class, sequence, flowchart

**Trade-offs:**
- PlantUML is more UML-compliant (Mermaid is "UML-like")
- PlantUML has more diagram types

**Mitigation:** If strict UML compliance is required, add PlantUML generation as an alternative output format. Don't remove Mermaid - keep both.

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Agent Framework | HIGH | Claude Agent SDK is official and authoritative. Clear documentation. Active development. |
| Schema Validation | HIGH | Zod is mature (4.x stable), widely adopted, and TypeScript-native. Alternative (Ajv) is well-understood. |
| Template Engines | MEDIUM-HIGH | Nunjucks and Handlebars are stable and mature. Template-based SQL generation is proven pattern (dbt Core). Confidence reduced slightly because Anchor Modeling templates are custom (no reference implementation). |
| Anchor Modeling | MEDIUM | Anchor Modeler provides formalized rules, but no TypeScript library exists. Custom implementation required. Risk: May misinterpret modeling rules. Mitigation: Reference implementation exists (Java GUI), can validate against it. |
| Multi-Agent Orchestration | MEDIUM | Claude Agent SDK provides primitives (subagents, Task tool, hooks). 2026 patterns are emerging (centralized, hierarchical, sequential) but not yet standardized. Risk: May need to refactor orchestration as patterns mature. |
| Diagram Generation | HIGH | Mermaid is mature and widely adopted. Syntax is simple (string concatenation). |
| Overall Stack | MEDIUM-HIGH | Core technologies are stable and well-documented. Risk areas are custom implementations (Anchor Modeling rules, multi-agent orchestration patterns). These are inherent to the problem domain, not technology choices. |

## Open Questions & Research Gaps

### Anchor Modeling Implementation Details

**Gap:** No TypeScript reference implementation for translating Anchor Models to SQL DDL.

**Mitigation:**
1. Study [Anchor Modeler GitHub repo](https://github.com/Roenbaeck/anchor) for formalized rules
2. Review academic papers on Anchor Modeling for 6NF translation
3. Validate generated SQL against Anchor Modeler output (use Java tool as oracle)

**Phase recommendation:** Phase 1 should include deeper research on Anchor Modeling rules. Consider spawning a dedicated research task: "Survey Anchor Modeling translation rules for TypeScript implementation."

### Multi-Agent Context Management

**Gap:** How to manage context when agents produce intermediate YAML specs consumed by downstream agents?

**Mitigation:**
1. Use Claude Agent SDK's session management to persist context
2. Investigate file-based state (agents write specs to `.claude/state/`, downstream agents read)
3. Consider message passing patterns from multi-agent orchestration research

**Phase recommendation:** Phase 2 (multi-agent implementation) needs research spike on context passing patterns.

### dbt Integration Surface

**Gap:** What's the integration surface between generated SQL DDL and dbt models?

**Current assumption:** Generate dbt-compatible Jinja/SQL files. Users run `dbt run` on generated files.

**Validation needed:**
1. Test generated Jinja with dbt Core to identify incompatibilities
2. Determine if dbt-specific features (sources, tests, docs) should be generated
3. Investigate dbt packages for Anchor Modeling (if any exist)

**Phase recommendation:** Phase 3 (dbt integration) needs research on dbt project structure and Jinja compatibility testing.

## Sources

### Official Documentation (HIGH Confidence)
- [Claude Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview) - Core SDK capabilities
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) - Skill structure and best practices
- [Zod Documentation](https://zod.dev/) - Schema validation
- [Zod GitHub Releases](https://github.com/colinhacks/zod/releases) - Version 4.x features
- [ts-morph Documentation](https://ts-morph.com/) - TypeScript AST manipulation
- [Anchor Modeling GitHub](https://github.com/Roenbaeck/anchor) - Reference implementation
- [dbt SQL Models Documentation](https://docs.getdbt.com/docs/build/sql-models) - dbt templating patterns
- [Mermaid Documentation](https://mermaid.js.org/) - Diagram generation

### Ecosystem Research (MEDIUM Confidence)
- [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) - Anthropic engineering blog
- [Top 5 TypeScript AI Agent Frameworks 2026](https://blog.agentailor.com/posts/top-typescript-ai-agent-frameworks-2026) - Framework comparison
- [Multi-Agent Systems Guide 2026](https://dev.to/eira-wexford/how-to-build-multi-agent-systems-complete-2026-guide-1io6) - Orchestration patterns
- [Handlebars vs Nunjucks](https://stackshare.io/stackups/handlebars-vs-nunjucks) - Template engine comparison
- [Top 13 JavaScript Templating Engines 2026](https://colorlib.com/wp/top-templating-engines-for-javascript/) - Ecosystem survey
- [Using TypeScript AST](https://nabeelvalley.co.za/docs/javascript/typescript-ast/) - AST manipulation guide
- [Anchor Modeling Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) - Conceptual overview

### Community Resources (MEDIUM-LOW Confidence)
- [JSON Schema Everywhere - YAML](https://json-schema-everywhere.github.io/yaml) - YAML validation patterns
- [Ajv with TypeScript](https://ajv.js.org/guide/typescript.html) - Alternative validation approach
- [dbt Jinja and Macros](https://docs.getdbt.com/docs/build/jinja-macros) - Template patterns for SQL

### Version Information (LOW-MEDIUM Confidence)
- npm package pages searched but access blocked (403 errors)
- Version information sourced from GitHub releases and search results
- **Recommendation:** Verify versions with `npm view <package> version` before installation

---

*Stack research for: Warehouse Architect (Claude Code skill for data warehouse design)*
*Researched: 2026-02-07*
*Confidence: MEDIUM-HIGH (core technologies HIGH, domain-specific implementations MEDIUM)*
