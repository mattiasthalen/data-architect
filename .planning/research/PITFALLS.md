# Pitfalls Research

**Domain:** AI-Driven Data Warehouse Design Tool (Multi-Agent, Anchor Modeling, ADSS)
**Researched:** 2026-02-07
**Confidence:** MEDIUM-HIGH

## Critical Pitfalls

### Pitfall 1: LLM Intent Errors That Look Valid

**What goes wrong:**
AI-generated SQL executes successfully and returns data, but answers the wrong question. The query runs perfectly, it just produces incorrect results. This is the most dangerous category because traditional validation (syntax checking, execution testing) fails to catch these errors.

**Why it happens:**
LLMs cannot infer implicit business logic from context. Missing filters (e.g., `WHERE status = 'active'`), incorrect aggregation logic, and schema misinterpretation create queries that are syntactically perfect but semantically wrong. Results can be 15-20% off from expected values, yet the query completes without error.

**How to avoid:**
- Never trust LLM-generated SQL without validating against known-good results
- Implement multi-agent debate specifically for SQL generation: have one agent generate, another critique with business rules
- Create a test suite of canonical queries with expected results
- Include business logic rules explicitly in context (e.g., "active customers means status='active' AND deleted_at IS NULL")
- Use deterministic validation: compare generated SQL structure against templates, not just execution

**Warning signs:**
- Results that are "close but not exact" to manual calculations
- Missing WHERE clauses in generated queries
- Aggregations that don't match business definitions
- Column names that exist but represent different concepts than intended

**Phase to address:**
Phase 1 (Foundation) - Establish validation framework and business rule encoding before any SQL generation occurs.

---

### Pitfall 2: Multi-Agent Infinite Debate Loops

**What goes wrong:**
Debate agents get stuck in circular disagreement, consuming tokens without converging on a solution. Agents repeat the same arguments, make trivial modifications, or oscillate between two positions indefinitely.

**Why it happens:**
Without bounded iterations or external variation signals, agents lack mechanisms to break deadlock. Systems that only limit max iterations without quality thresholds can run to exhaustion without producing valid output. Agents may lack sufficient context to recognize they're repeating themselves.

**How to avoid:**
- Implement bounded iterations with quality gates (e.g., max 5 rounds, but stop early if consensus score > 0.8)
- Use hybrid topology: preserve diversity while enabling coordination through structured communication
- Add external variation signals to prevent premature consensus AND infinite loops
- Implement debate state tracking: detect repeated arguments, flag circular reasoning
- Create explicit termination criteria beyond iteration count (convergence metrics, quality thresholds, novelty detection)
- Add a "mediator" agent with tie-breaking authority after N rounds

**Warning signs:**
- Debate logs showing repeated similar critiques
- Token consumption increasing linearly with no quality improvement
- Agents making only trivial changes between rounds
- Debate duration exceeding expected time by 3x+
- Logs showing phrase repetition across debate turns

**Phase to address:**
Phase 1 (Foundation) - Debate orchestration must include circuit breakers from day one. Cannot be added retroactively without breaking existing logic.

---

### Pitfall 3: Premature Physical Modeling (Skipping CLP Stages)

**What goes wrong:**
Teams jump from vague ideas directly to physical schema implementation, bypassing conceptual and logical modeling. This leads to schemas that can't be mapped back to business concepts, making maintenance and evolution nearly impossible. Requires complete rewrites when requirements change.

**Why it happens:**
Physical modeling feels like "real progress" - you're creating actual tables. Conceptual/logical modeling feels abstract and time-consuming. Pressure to "show something working" drives premature optimization. Teams treat normalization as religion rather than tool, over-normalizing or under-normalizing without understanding tradeoffs.

**How to avoid:**
- Enforce stage gates: cannot proceed to logical without conceptual approval, cannot proceed to physical without logical approval
- Use "just in time" design: model for today's realities, evolve as needed, not every hypothetical future
- Document the mapping: every physical table must trace to logical entity, every logical entity to conceptual domain
- For AI generation: generate conceptual model first, have agents debate it, THEN derive logical, THEN physical
- Treat normalization as tool with tradeoffs, not absolute goal
- Start simple (KISS), optimize iteratively based on actual workload, not assumptions

**Warning signs:**
- Physical schema doesn't map cleanly to business terminology
- Difficulty explaining table purpose without referencing technical implementation
- "Why is this table here?" questions have no business answer
- Schema changes require massive rewrites rather than incremental evolution
- Over-normalized (6NF) without using join elimination features
- Denormalized without documented performance justification

**Phase to address:**
Phase 2 (CLP Workflow) - Must be enforced in the workflow orchestration. Each stage should produce artifacts that feed the next stage, with validation preventing stage-skipping.

---

### Pitfall 4: Anchor Modeling Over-Application (6NF Performance Traps)

**What goes wrong:**
Applying Anchor Modeling's 6NF decomposition universally creates explosion of tables. Queries require massive joins that modern optimizers cannot eliminate. Performance degrades catastrophically. Cognitive overhead makes system unmaintainable - developers cannot reason about dozens of tables for a single logical entity.

**Why it happens:**
Anchor Modeling's theoretical elegance is appealing. Teams read that "modern databases use join elimination" and assume it solves all problems. They apply 6NF to reference data, dimensions that never change, and concepts that don't need temporal tracking. They don't test with realistic query patterns until production.

**How to avoid:**
- **Use Anchor Modeling selectively**: temporal, frequently-changing business entities only
- **NOT for**: static reference data, lookup tables, dimensions with rare changes, aggregation targets
- Test join elimination on YOUR database with YOUR query patterns BEFORE full implementation
- Set table count budget: if a single business entity exceeds N tables (e.g., 7-10), question the design
- Create views for common access patterns, measure view vs. table query performance
- For DAB layer specifically: Anchors for core business entities, traditional modeling for relationships
- Document decision criteria: "Entity X uses Anchor because it has 50 attributes changing independently at different rates"

**Warning signs:**
- Single entity queries joining 15+ tables
- Query plans showing joins that aren't eliminated
- Developers needing ER diagrams to write basic queries
- Performance degrading linearly with entity count
- Inability to explain which table contains "customer address"
- View performance slower than direct table access

**Phase to address:**
Phase 3 (Anchor Modeling Implementation) - Include performance testing and selective application criteria. Build prototype with both approaches, measure before committing.

---

### Pitfall 5: Schema Specification Drift (Generator-Spec Mismatch)

**What goes wrong:**
The YAML/JSON specification format and the code generator fall out of sync. Specification contains fields the generator ignores. Generator expects fields missing from spec. Versioning chaos means specs from last month cannot be processed. Silent failures where generator produces output but ignores sections of spec.

**Why it happens:**
Spec and generator evolve independently. No schema validation enforced at specification creation. Version numbers exist but nothing checks them. Generator has implicit assumptions not documented in spec schema. Teams hand-edit generated specs, adding fields generator doesn't recognize.

**How to avoid:**
- Use JSON Schema or YAML schema validation for ALL spec files - fail fast on invalid specs
- Version specs explicitly (e.g., `spec_version: "2.1"`) and generator checks compatibility on load
- Generate spec schema FROM generator code, or generate generator FROM spec schema (single source of truth)
- Add `--validate-only` mode to generator: parses spec, reports all unrecognized fields, exits without generating
- Include spec version in generated code comments so output can be traced to spec version
- Test suite: canonical specs for each version, generator must handle all of them
- Monitor for type drift: track when field types change (string → integer) in specs

**Warning signs:**
- Generated code missing expected elements
- Specs with fields that have no effect when changed
- Error messages like "unexpected field" appearing in logs but not failing generation
- Different developers' generators producing different output from same spec
- Spec versioning field present but never checked
- Manual spec editing more common than regeneration

**Phase to address:**
Phase 4 (Specification Format) - Validation must be built into spec format from the beginning. Retrofitting validation onto existing loose specs is extremely painful.

---

### Pitfall 6: Multi-Agent Premature Consensus (Rubber-Stamping)

**What goes wrong:**
Debate agents agree too quickly without genuine critical analysis. System Analyst proposes schema, Business Analyst rubber-stamps it with minor cosmetic feedback. Result lacks the diversity and error-correction that multi-agent debate should provide. Functionally equivalent to single-agent generation.

**Why it happens:**
Agents lack incentive structure for disagreement. Prompts emphasize "reaching consensus" over "finding flaws". Agents trained to be helpful default to agreement. No mechanism rewards finding genuine problems. Token/cost pressure encourages shorter debates. Agent personas too similar (both "helpful assistants").

**How to avoid:**
- Create adversarial incentives: reward agents for finding legitimate flaws, not for agreeing
- Use distinct, strong personas: System Analyst = "technical purist, performance-focused", Business Analyst = "domain expert, user-advocate"
- Require concrete objections with evidence: ban responses like "looks good" or "I agree"
- Set minimum debate rounds (e.g., must have at least 2 rounds even if initial agreement)
- Include "devil's advocate" agent whose job is specifically to criticize
- Measure debate quality: track how many changes occur between rounds (too few = rubber-stamping)
- Use FREE-MAD consensus-free approach: agents produce independent solutions, mediator synthesizes best elements

**Warning signs:**
- Most debates ending in first round
- Feedback dominated by "looks good", "minor suggestion", "I agree"
- Very few schema changes between initial proposal and final result
- Agent responses getting shorter over time
- Agents citing each other's arguments rather than independent reasoning
- Quality of multi-agent output similar to single-agent baseline

**Phase to address:**
Phase 1 (Foundation) - Debate incentive structure must be core to orchestration design. Changing agent behavior after system is built requires prompt rewriting across entire codebase.

---

### Pitfall 7: Claude Context Window Amnesia Across Sessions

**What goes wrong:**
Agent loses critical project context between sessions. Forgets naming conventions, business rules, domain terminology, and architectural decisions made previously. Each session starts fresh, making inconsistent decisions. Generated artifacts drift stylistically. Developers must repeatedly re-explain the same context.

**Why it happens:**
Claude has no cross-session memory - context window resets to empty. Project context must be explicitly reloaded each session. State stored in file system but not systematically surfaced to agent. Task system helps but requires explicit setup. Context window fills with conversation, pushing out project knowledge.

**How to avoid:**
- Implement persistent context files: `.planning/context/PROJECT_RULES.md`, `.planning/context/NAMING_CONVENTIONS.md`, `.planning/context/DOMAIN_MODEL.md`
- Use Claude Code Tasks feature to persist state across sessions with dependency tracking
- Add session bootstrap: first action loads context files, summarizes previous session state
- Implement context hierarchy: critical rules in system prompt, project details in early context, conversation fills remaining space
- Create memory checkpoints: after major decisions, write to `.planning/decisions/YYYY-MM-DD-topic.md`
- Use retrieval pattern: agent searches decision log before making new decisions
- Include version/timestamp in generated artifacts so they can be traced to session context

**Warning signs:**
- Agent asking same questions across sessions
- Inconsistent naming (UserAccount vs user_accounts vs Users) between sessions
- Violating constraints documented in previous sessions
- Starting over on partially complete work
- Developers copying-pasting context into every new conversation
- Generated code style drift over time

**Phase to address:**
Phase 1 (Foundation) - Context persistence must be architectural, not a bolt-on. Build context management into orchestration from day one.

---

### Pitfall 8: Hallucinated Schema Elements

**What goes wrong:**
AI confidently generates schemas with tables, columns, or relationships that don't align with business requirements. Creates `user_preferences` table when no such concept exists in domain. Invents columns like `account_status` that sound reasonable but don't match actual business states. Relates entities that should not be connected.

**Why it happens:**
LLMs pattern-match to common schemas they've seen (users, accounts, preferences). When under-specified, they fill gaps with plausible-sounding but incorrect elements. Generic domain knowledge overrides specific project requirements. Multi-agent debate validates consistency (do elements relate logically?) but not correctness (do they match reality?).

**How to avoid:**
- Provide explicit domain ontology: enumerate valid entities, attributes, relationships BEFORE generation
- Use controlled vocabulary: agent can only use terms from approved domain glossary
- Add verification agent with domain model: compares generated schema against canonical domain model, flags unknown elements
- Require traceability: every schema element must cite source requirement/business rule
- Human-in-loop for entity creation: AI proposes, human approves before elaboration
- Red team with "domain outsider" agent: identifies elements that weren't in requirements

**Warning signs:**
- Schema contains entities/attributes not mentioned in requirements
- Generated elements "sound right" but don't match stakeholder terminology
- Multiple plausible interpretations of same business concept
- Schema includes standard patterns (user_preferences, audit_log) without business justification
- Attributes that are technically consistent but business-meaningless

**Phase to address:**
Phase 2 (CLP Workflow) - During conceptual modeling, establish verification against domain model. Cannot be added after physical schema exists.

---

### Pitfall 9: Deterministic vs. Probabilistic Mismatch

**What goes wrong:**
Using LLM generation for tasks that should be deterministic. Template-based SQL generation is predictable and testable; LLM generation is neither. Team wastes time debugging non-deterministic generation when templates would be simpler, faster, and more reliable.

**Why it happens:**
AI hype creates pressure to "use AI for everything". Teams think flexibility of LLM generation is always superior to rigid templates. Underestimate cognitive overhead of validating probabilistic output. Don't recognize where deterministic approaches are better fit.

**How to avoid:**
- Use hybrid approach: LLM for conceptual/logical modeling (creative, requires judgment), deterministic generators for physical implementation (mechanical, requires precision)
- Spec → Code should be deterministic template generation (Jinja, Mustache, code generation)
- LLM generates spec; spec validates against schema; generator produces code
- Reserve LLMs for: requirement interpretation, design debate, anomaly detection, explanation generation
- Use deterministic for: SQL DDL/DML generation, configuration file output, consistent formatting
- Principle: "Maximize abstraction level, minimize LLM generation at lowest levels"

**Warning signs:**
- Non-deterministic output requiring manual review every time
- "AI-generated" code that's 90% template with 10% variables
- Debugging why the same spec produces different code
- Testing becoming harder because output varies
- Team longing for "old template system that just worked"

**Phase to address:**
Phase 4 (Specification Format) + Phase 5 (Code Generation) - Architecture decision: LLM stops at validated spec, deterministic generator produces code.

---

### Pitfall 10: Missing Historization Strategy (SCD Retrofitting)

**What goes wrong:**
Team starts with SCD Type 1 (overwrite) thinking they can "add history later". Discover that adding SCD Type 2 fundamentally changes what the dimension contains - cannot be added incrementally. Historical analysis impossible. Compliance requirements unmet. Major schema redesign required in production.

**Why it happens:**
SCD Type 2 looks complex upfront. Team wants to "start simple". Underestimate how historization changes data model fundamentally. Don't realize historical data is lost forever once overwritten. Business stakeholders don't articulate "we'll need to see how this looked 6 months ago" until 6 months pass.

**How to avoid:**
- Decide historization strategy DURING CONCEPTUAL MODELING, not during physical implementation
- Default to history unless proven unnecessary: "time-aware by default"
- Anchor Modeling's temporal support is primary advantage - use it
- Document explicitly: "Entity X has no history because [business justification]"
- For AI generation: include historization in conceptual model schema - is this concept time-varying?
- Test with temporal queries: "Show me customer address as of 2025-06-01" - if this query should work, you need history
- Consider compliance: GDPR, financial regulations, audit trails often mandate history

**Warning signs:**
- Requirements include terms like "changed", "was", "became", "historical"
- Business rules reference point-in-time state ("if status was X on date Y")
- Reporting needs "month-over-month" or "as-of-date" analysis
- Audit requirements for "who changed what when"
- Stakeholder questions like "when did this customer's address change?"
- Anchor Modeling used but historization attributes (`FROM_DATE`, `TO_DATE`) missing

**Phase to address:**
Phase 2 (CLP Workflow) - Historization is conceptual decision. Must be determined before logical or physical modeling begins.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip spec validation | Faster iteration | Silent failures, generator drift | Never - validation is cheap insurance |
| Single-agent generation | Simpler orchestration, lower cost | Higher error rate, no diversity | Prototyping only, never production |
| Hard-code business rules in generators | Easier than rule engine | Rules scattered, difficult to change | Small projects with stable rules |
| Skip conceptual modeling | "Get to code faster" | Unmaintainable schema, rewrites | Never - saves days, costs weeks |
| Use views for everything (avoid materialization) | Simple, "just works" | Performance degrades, query timeouts | Only when data volume is known-small |
| Store historical data outside warehouse | Simpler initial schema | Historical analysis impossible | When compliance forbids or data is truly write-once |
| Manual spec editing without regeneration | Quick fixes | Spec-code drift, lost source of truth | Emergency hotfixes only, followed by proper fix |
| Assume join elimination works | Clean 6NF design | Query performance cliff | Only after testing on target database with real queries |
| Store business logic in SQL generators | "Keep it in one place" | Logic invisible to business, hard to validate | Never - logic should be explicit in specs |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| dbt code generation | Generating complex macros with recursive CTEs | Generate simple, flat models; use dbt's ref() for dependencies |
| SQL dialect differences | Assuming PostgreSQL features work on Snowflake | Use dialect-aware generator or SQLAlchemy for portability |
| Claude API | Not handling rate limits in multi-agent systems | Implement exponential backoff, request queuing, token budgeting |
| Git operations in agent | Committing without seeing changes first | Always git status + git diff before commit |
| Context7 library queries | Assuming library exists without resolve step | Always resolve-library-id before query-docs |
| File operations | Using relative paths in agents | Always use absolute paths (cwd resets between calls) |
| Schema versioning | Storing version in comments only | Use explicit version fields in machine-readable format |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| View-on-view-on-view in dbt | Queries getting slower over time | Materialize intermediate views, monitor view depth | 3+ view layers, 100k+ rows |
| 6NF without join elimination | Queries joining 15+ tables, linear performance degradation | Test join elimination before full 6NF, use selectively | Query plans show actual joins |
| Unvalidated LLM SQL in production | Intermittent wrong results, 15-20% data discrepancies | Multi-agent validation, test against known results | When users start noticing inconsistencies |
| Context window filling with chat history | Agent forgetting project rules, inconsistent decisions | Context hierarchy, persistent rule files, session bootstrap | After 30-40 message conversation |
| Multi-agent debate with no bounds | Token consumption growing without quality improvement | Bounded iterations + quality gates + convergence metrics | After 5+ rounds with no convergence |
| Spec changes without versioning | Generator fails on old specs, silent field ignoring | Schema validation, version checking, migration tests | When specs from 3+ months ago stop working |
| Generated code without traceability | Unable to determine which spec version produced code | Include spec version + timestamp in generated comments | When debugging generated code issues |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Exposing business rules in generated SQL | Competitors reverse-engineer domain logic | Separate business logic into rule engine, not embedded in SQL |
| Storing specs with credentials | API keys, connection strings in YAML committed to git | Use environment variables, secret management, validate specs don't contain secrets |
| Generated code with SQL injection | Template string concatenation in LLM output | Use parameterized queries, validate all generated SQL through parser |
| No audit trail on AI decisions | Cannot explain why schema generated specific way | Log all agent debates, decisions, and rationale to `.planning/decisions/` |
| Unvalidated multi-agent output | Adversarial agents could collude on malicious schema | Include independent validator agent outside debate loop |
| PII in context window | Customer data sent to Claude API for "example queries" | Anonymize all examples, validate context contains no PII before API call |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress visibility during multi-agent debate | User doesn't know if system is working or stuck | Stream agent messages, show debate round counter, estimated time |
| Error messages from generator internals | "KeyError: 'anchor_name'" means nothing to user | Translate technical errors to domain terms: "Missing anchor name in specification for entity X" |
| No explanation for AI decisions | "Why did it create this table?" has no answer | Store agent reasoning in parallel with generated artifacts |
| Overwhelming with full debate transcript | Users see 50-message debate, can't parse it | Provide summary view with expandable details |
| Jargon mismatch | UI uses "6NF" but users think in "tables and columns" | Use business terminology in UI, technical terms in implementation |
| No preview before generation | Users see code only after full generation | Show conceptual/logical models for approval before physical generation |
| Silent degradation | Multi-agent system falls back to single agent without notification | Alert user when debate fails, show fallback mode explicitly |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Generated SQL:** Runs without error — verify it produces correct results against known-good test cases, not just executes successfully
- [ ] **Multi-agent debate:** Reaches consensus — verify agents actually critiqued (not rubber-stamped) by checking substantive changes between rounds
- [ ] **Anchor Model:** Tables created with temporal columns — verify join elimination works on your database with your queries, not just in theory
- [ ] **Specification:** Validates against schema — verify generator actually uses all fields, doesn't ignore sections silently
- [ ] **Historization:** SCD Type 2 columns present — verify temporal queries work, test "as-of-date" lookups return correct historical state
- [ ] **Context persistence:** Files in `.planning/` directory — verify agent actually loads them at session start, test by starting fresh session
- [ ] **Naming conventions:** Documented in `.planning/` — verify generator enforces them, test by generating schema for new entity
- [ ] **Code generation:** Produces valid SQL/dbt — verify it follows dialect requirements, test on actual target database platform
- [ ] **Business rules:** Encoded in specs — verify they're enforced in generated queries, test with edge cases
- [ ] **Error handling:** Try-catch blocks present — verify actual errors are caught and produce useful messages, test with invalid inputs

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| LLM Intent Errors in SQL | MEDIUM | Create validation test suite, regenerate SQL with explicit business rules in context, implement multi-agent SQL validation |
| Infinite Debate Loops | LOW | Add iteration limits retroactively, implement convergence metrics, restart with mediator agent |
| Skipped CLP Stages | HIGH | Reverse-engineer conceptual from physical (painful), document as-is, use as baseline for incremental improvement |
| Over-applied 6NF | MEDIUM-HIGH | Identify low-change entities, consolidate to 3NF, keep 6NF for high-change temporal entities |
| Spec-Generator Drift | MEDIUM | Add schema validation (will break existing specs), version migration scripts, audit which spec fields are unused |
| Premature Consensus | MEDIUM | Add adversarial agent to existing debate, strengthen agent personas, require minimum rounds |
| Context Amnesia | LOW | Create persistent context files retroactively, implement bootstrap process, migrate to Task system |
| Hallucinated Schemas | MEDIUM | Build domain model from existing schemas, add verification agent, create controlled vocabulary |
| Wrong Deterministic/Probabilistic Split | LOW-MEDIUM | Extract templates from LLM-generated code, move generation to deterministic layer, keep LLM for specs |
| Missing Historization | HIGH | Cannot add SCD Type 2 retroactively without data loss; requires schema redesign and migration |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| LLM Intent Errors | Phase 1: Foundation | Test suite with canonical queries, known-good results |
| Infinite Debate Loops | Phase 1: Foundation | Bounded iterations, convergence metrics in orchestration |
| Skipped CLP Stages | Phase 2: CLP Workflow | Stage gates enforced, cannot skip without explicit override |
| Over-applied 6NF | Phase 3: Anchor Modeling | Performance tests, selective application criteria documented |
| Spec-Generator Drift | Phase 4: Specification Format | Schema validation passes, versioning enforced |
| Premature Consensus | Phase 1: Foundation | Debate quality metrics, minimum substantive changes required |
| Context Amnesia | Phase 1: Foundation | Bootstrap loads context, test fresh session maintains consistency |
| Hallucinated Schemas | Phase 2: CLP Workflow | Verification agent, domain model validation |
| Deterministic/Probabilistic Split | Phase 4: Specification + Phase 5: Code Gen | LLM stops at spec, generator is deterministic |
| Missing Historization | Phase 2: CLP Workflow | Conceptual model includes time-variance decisions |

## Sources

**Anchor Modeling:**
- [Anchor modeling - Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling)
- [Database design using Anchor Modeling - codecentric](https://www.codecentric.de/en/knowledge-hub/blog/agile-database-design-using-anchor-modeling)
- [Anchor Modelling: Sixth Normal Form databases](https://itsalocke.com/blog/anchor-modelling-sixth-normal-form-databases/)
- [Understanding Anchor Modeling for Agile and Temporal Data](https://www.owox.com/glossary/anchor-modeling)

**Multi-Agent Debate:**
- [Minimizing Hallucinations and Communication Costs: Adversarial Debate and Voting Mechanisms in LLM-Based Multi-Agents](https://www.mdpi.com/2076-3417/15/7/3676)
- [Multi-Agent Debate Strategies](https://www.emergentmind.com/topics/multi-agent-debate-mad-strategies)
- [Mitigating LLM Hallucinations Using a Multi-Agent Framework](https://www.mdpi.com/2078-2489/16/7/517)
- [FREE-MAD: Consensus-Free Multi-Agent Debate](https://arxiv.org/pdf/2509.11035)
- [How to Build Multi-Agent Systems: Complete 2026 Guide](https://differ.blog/p/how-to-build-multi-agent-systems-complete-2026-guide-f50e02)

**Data Warehouse Design:**
- [6 data warehouse design mistakes to avoid - Computer Weekly](https://www.computerweekly.com/tip/6-data-warehouse-design-mistakes-to-avoid)
- [10 Pitfalls to Avoid with Data Warehouses - Medium](https://medium.com/ironkeel/10-pitfalls-to-avoid-with-data-warehouses-47019c0c41db)
- [Top Mistakes to Avoid When Building a Data Warehouse](https://tdan.com/top-mistakes-to-avoid-when-building-a-data-warehouse/4926)
- [Clarifying Data Warehouse Design with Historical Dimensions](https://www.red-gate.com/simple-talk/databases/sql-server/bi-sql-server/clarifying-data-warehouse-design-with-historical-dimensions/)

**dbt & SQL Generation:**
- [DBT Anti-patterns - MetaOps](https://metaops.solutions/blog/dbt-anti-patterns)
- [SQL Anti-Patterns You Should Avoid](https://datamethods.substack.com/p/sql-anti-patterns-you-should-avoid)

**LLM Code Generation:**
- [We Evaluated 50,000+ LLM-Generated SQL Queries. Here's What Actually Breaks.](https://www.usedatabrain.com/blog/llm-sql-evaluation)
- [Bridging Natural Language and Databases: Best Practices for LLM-Generated SQL](https://medium.com/@vi.ha.engr/bridging-natural-language-and-databases-best-practices-for-llm-generated-sql-fcba0449d4e5)
- [LLM text-to-SQL solutions: Top challenges and tips](https://www.k2view.com/blog/llm-text-to-sql/)

**Claude & Context:**
- [Claude Code Keeps Forgetting Your Project? Here's the Fix (2026)](https://dev.to/kiwibreaksme/claude-code-keeps-forgetting-your-project-heres-the-fix-2026-3flm)
- [Context windows - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [The 4-Step Protocol That Fixes Claude Code Agent's Context Amnesia](https://medium.com/@ilyas.ibrahim/the-4-step-protocol-that-fixes-claude-codes-context-amnesia-c3937385561c)

**Data Modeling:**
- [Conceptual vs Logical vs Physical Data Models](https://www.thoughtspot.com/data-trends/data-modeling/conceptual-vs-logical-vs-physical-data-models)
- [The Traditional Levels of Data Modeling](https://practicaldatamodeling.substack.com/p/the-traditional-levels-of-data-modeling)

**Schema Management:**
- [Schema Evolution in Data Pipelines: Tools, Versioning & Zero-Downtime](https://dataengineeracademy.com/module/best-practices-for-managing-schema-evolution-in-data-pipelines/)
- [Managing Schema Drift in Variant Data: A Practical Guide](https://estuary.dev/blog/schema-drift/)

**Naming Conventions:**
- [Data Warehouse Design: Naming Standards](https://recordlinker.com/data-warehouse-standards/)
- [What to Consider for Naming Conventions in Data Warehousing](https://www.scalefree.com/blog/data-warehouse/naming-conventions/)
- [Switching to a better data warehouse naming convention](https://dataform.co/blog/updating-warehouse-naming-convention)

**AI Code Generation (Hybrid Approaches):**
- [A generative AI cybersecurity risks mitigation model for code generation: using ANN-ISM hybrid approach](https://www.nature.com/articles/s41598-025-34350-3)
- [How far can we push AI autonomy in code generation?](https://martinfowler.com/articles/pushing-ai-autonomy.html)

**6NF & Performance:**
- [Sixth normal form - Wikipedia](https://en.wikipedia.org/wiki/Sixth_normal_form)

---
*Pitfalls research for: AI-Driven Data Warehouse Design Tool*
*Researched: 2026-02-07*
*Confidence: MEDIUM-HIGH - Based on verified sources for multi-agent systems, LLM code generation, and data warehouse design; some areas extrapolated from general patterns to this specific domain*
