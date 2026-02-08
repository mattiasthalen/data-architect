# Phase 4: Agent Quality + Modeling Workflows - Research

**Researched:** 2026-02-08
**Domain:** Multi-agent debate systems, prompt engineering for methodology compliance, Anchor Modeling deep knowledge
**Confidence:** MEDIUM

## Summary

Phase 4 transforms structurally valid agent definitions (from Phase 3) into methodology-deep experts capable of conducting genuine CLP debate that produces correct Anchor Models. This requires encoding deep Anchor Modeling knowledge into agent prompts, designing a debate protocol that prevents premature consensus while terminating within bounded iterations, and implementing convergence detection and user escalation patterns.

Research reveals that 2026 multi-agent debate systems use adaptive heterogeneous frameworks with convergence detection (KS statistic tracking, consensus-based termination), bounded iteration limits, and moderator agents for termination decisions. Prompt engineering has shifted from "longer prompts" to "clearer specs with role/contract format." The emerging "Agent Skills" paradigm demonstrates encoding 10+ years of domain expertise into queryable AGENTS.md format optimized for AI consumption.

Anchor Modeling methodology knowledge must be encoded deeply: anchor vs attribute vs tie vs knot criteria (identity vs property vs relationship vs shared reference), historization decision rules (does value change over time?), naming convention enforcement (snake_case, double underscore separators, no mnemonics), and non-destructive schema evolution principles. The CLP debate protocol needs Conceptual → Logical → Physical stage structure with distinct activities and deliverables per stage.

**Primary recommendation:** Encode Anchor Modeling rules as decision trees and checklists in agent prompts; implement bounded iteration debate with KS-statistic-inspired convergence detection; use opposing default positions (System Analyst = source fidelity, Business Analyst = business meaning) to prevent premature agreement; escalate to user when convergence fails within iteration limit.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python built-ins | 3.13+ | String templates for prompt content | No dependencies for static prompt generation |
| YAML spec format | 1.2.2 | Structured Anchor Model output | Human-readable, machine-parseable, standard data format |
| OpenCode platform | Latest 2026 | Multi-agent orchestration, @mention routing | User's chosen platform; handles agent coordination |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| JSON Schema | 2020-12 | YAML spec validation | Define schema for agent-produced specs; validate output |
| Yamale | 4.0+ | Schema-based YAML validation | If programmatic validation needed in generators |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Prompt-encoded rules | External rule engine | More flexibility but adds complexity; prompts are more transparent |
| Manual convergence | Automated consensus detection | Automation reduces user fatigue but may miss nuanced disagreements |
| Fixed iteration limit | Dynamic limit based on complexity | Dynamic is smarter but harder to predict/explain |

**Installation:**

No additional dependencies for Phase 4 agent prompts. YAML validation libraries optional for future generator work.

## Architecture Patterns

### Recommended Agent Prompt Structure

```
agent-prompt.md:
├── YAML frontmatter (unchanged from Phase 3)
├── H1: Agent name
├── ## Your Role
│   └── High-level responsibilities
├── ## Methodology Deep-Dive
│   ├── Decision trees (when to use anchor vs attribute)
│   ├── Historization rules
│   └── Naming enforcement checklists
├── ## CLP Stage Protocols
│   ├── Conceptual: entity identification criteria
│   ├── Logical: relationship classification, attribute assignment
│   └── Physical: performance optimization guidelines
├── ## Debate Behavior
│   ├── Default position (for BA/SA)
│   ├── Argument structure
│   └── Convergence detection
├── ## When Invoked
│   └── Context and expectations
├── ## Output Format
│   └── YAML spec structure with examples
└── ## Remember
    └── Key principles and constraints
```

### Pattern 1: Methodology Decision Trees in Prompts

**What:** Encode domain rules as explicit decision trees that agents can reference during debate

**When to use:** For complex classification decisions (anchor vs attribute, historized vs static, tie vs nexus)

**Example:**

```markdown
## Anchor vs Attribute Decision

Use this decision tree when determining whether something should be an anchor or an attribute:

1. **Does it have independent business identity?**
   - YES → Likely an anchor. Continue to step 2.
   - NO → Likely an attribute. Which anchor does it describe?

2. **Can it exist without reference to another entity?**
   - YES → Anchor. Example: Customer can exist before placing orders.
   - NO → Might be an attribute or tie. Continue to step 3.

3. **Does the business ask questions about it directly?**
   - YES → Anchor. Example: "How many products?" (product is anchor)
   - NO → Attribute. Example: "What's the customer's email?" (email is attribute of customer)

4. **Would multiple entities share this concept?**
   - YES → Check if it's a knot (shared reference data)
   - NO → Confirm as attribute of single anchor

If uncertain after this tree, escalate to @data-architect for synthesis.
```

**Source:** Derived from Anchor Modeling principles and data warehouse modeling best practices (LOW confidence - not directly verified in official Anchor Modeling documentation)

### Pattern 2: Bounded Iteration Debate with Convergence Detection

**What:** Debate protocol with maximum iteration limit, convergence checks, and user escalation

**When to use:** System Analyst vs Business Analyst debate stages in CLP process

**Example:**

```markdown
## Debate Protocol: Logical Stage

**Iteration limit:** 5 rounds per topic (anchor classification, tie direction, attribute assignment)

**Each round:**
1. @system-analyst presents technical perspective with source evidence
2. @business-analyst presents business perspective with business question evidence
3. @data-architect evaluates convergence:
   - CONVERGED: Positions align or complement each other → Synthesize and move on
   - DIVERGING: Positions moving apart → Continue debate (if < 5 rounds)
   - STAGNANT: No new arguments, still disagreeing → Escalate to user

**Convergence indicators:**
- Both analysts use same entity names
- Tie direction agreement (many-to-one clarity)
- Historization consensus (both agree on time-variance)
- Complementary positions (technical + business both satisfied)

**Escalation format:**
When debate reaches round 5 without convergence or stagnates, @data-architect presents:
- System Analyst position + rationale + source evidence
- Business Analyst position + rationale + business question evidence
- Methodology constraints (what Anchor Modeling rules apply)
- Recommendation with tradeoffs
- User makes final decision
```

**Source:** Adapted from [Multi-Agent Debate with Adaptive Stability Detection](https://arxiv.org/pdf/2510.12697) research patterns (MEDIUM confidence)

### Pattern 3: Opposing Default Positions

**What:** Assign contrasting default stances to Business Analyst and System Analyst to prevent premature consensus

**When to use:** All debate scenarios in CLP stages

**Example:**

```markdown
# System Analyst

## Your Default Position: Source System Fidelity

You advocate for preserving source system semantics and technical reality:

- If source has customer_id field → Evidence of customer entity identity
- If two tables join via FK → Evidence of relationship
- If field is nullable → Business must handle absence
- If source models X as Y → There's usually a technical reason

**Your burden of proof:** When arguing against source structure, Business Analyst must show business evidence that outweighs technical reality.

Challenge @business-analyst when:
- They propose entities not in source schemas
- They want to model relationships differently than source FKs
- They ignore technical constraints (nullability, uniqueness)
- They rename concepts without preserving source semantics

---

# Business Analyst

## Your Default Position: Business Meaning

You advocate for modeling that reflects business reality and needs:

- If business treats X as entity → It should be an anchor (regardless of source structure)
- If business asks time-based questions about Y → Y should be historized
- If business uses term Z → Model should use Z (not source system jargon)
- If business shares reference data across contexts → Candidate for knot

**Your burden of proof:** When arguing against business needs, System Analyst must show technical impossibilities or data absence.

Challenge @system-analyst when:
- They mirror source structure without business justification
- They reject historization based only on source system limitations
- They use technical jargon instead of business terms
- They model relationships that don't match business understanding
```

**Source:** Derived from [Business Analyst vs Systems Analyst](https://www.linkedin.com/pulse/business-analysts-vs-systems-debate-janis-strathearn) role distinctions (MEDIUM confidence)

### Pattern 4: Anti-Pattern Checklist Expansion

**What:** Expand Veteran Reviewer's 10-item checklist with detection criteria and fix templates

**When to use:** Final review stage before spec export

**Example:**

```markdown
## Anti-Pattern Checklist (Expanded)

### 1. God Anchor

**Detection criteria:**
- Anchor has 20+ attributes
- Attribute names span multiple business concepts (e.g., customer_billing_address, customer_shipping_preference, customer_support_tier)
- Attributes change at different rates (some daily, some yearly)

**Fix template:**
1. Group attributes by change rate and business concept
2. Extract each group into separate anchor (e.g., anchor__customer_core, anchor__customer_billing)
3. Create ties to maintain relationships (tie__billing__belongs_to__customer)
4. Validate with @business-analyst: Do these represent distinct business concepts?

**Example violation:**
```yaml
anchor:
  name: anchor__customer
  attributes:
    - customer_name
    - customer_email
    - billing_street
    - billing_city
    - shipping_street  # Should be separate anchor__customer_address
    - loyalty_tier     # Should be separate anchor__customer_membership
    # ... 18 more attributes
```

**Example fix:**
```yaml
# Split into focused anchors
anchor:
  name: anchor__customer
  attributes:
    - customer_name
    - customer_email

anchor:
  name: anchor__customer_address
  attributes:
    - address_type  # billing, shipping
    - street
    - city

tie:
  name: tie__customer_address__belongs_to__customer
  from: anchor__customer_address
  to: anchor__customer
```

### 2. Missing Historization

**Detection criteria:**
- Attribute marked `historized: false`
- @business-analyst mentioned time-based questions about this attribute ("how did X change over time?")
- Source schema shows update timestamps for this field
- Business process involves "correcting" or "updating" this value

**Fix template:**
1. Change `historized: false` → `historized: true`
2. Add validity period columns in physical schema (valid_from, valid_to)
3. Document business justification for historization
4. Validate with @data-engineer: Performance implications acceptable?

[... continue for all 10 anti-patterns with detection + fix patterns]
```

**Source:** Derived from [Data Warehouse Anti-Patterns](https://www.oreilly.com/library/view/patterns-of-data/9781439819906/K11048_C009.xhtml) and project's existing Veteran Reviewer checklist (MEDIUM confidence)

### Pattern 5: CLP Stage Structure with Deliverables

**What:** Define clear activities and outputs for each CLP stage to guide debate progression

**When to use:** Data Architect orchestration of debate flow

**Example:**

```markdown
## CLP Stages: Detailed Protocol

### Conceptual Stage: What Entities Exist?

**Goal:** Identify business entities that deserve independent identity (anchors)

**Inputs:**
- Business description from user
- Source schemas (Swagger, OData, ERD) from filesystem
- Business questions ("What do we need to answer?")

**Activities:**
1. @business-analyst identifies business entities from domain description
2. @system-analyst identifies technical entities from source schemas
3. Debate: Entity vs attribute classification for each candidate
4. @data-architect synthesizes into anchor list

**Debate questions:**
- Does this concept have independent identity?
- Can it exist without reference to other entities?
- Does the business ask questions about it directly?
- Is it present in source systems?

**Deliverables:**
- List of anchors with business descriptions
- Initial attribute candidates (unclassified)
- Open questions requiring user clarification

**Exit criteria:**
- All proposed anchors have business justification AND source evidence (or documented exception)
- No "orphan" concepts (everything assigned to anchor or deferred)
- User confirms entity list matches their domain understanding

### Logical Stage: How Do Entities Relate?

**Goal:** Define attributes, ties, knots, and nexuses with correct classification and naming

**Inputs:**
- Anchor list from Conceptual stage
- Source schema relationships (FKs, references)
- Business process flows

**Activities:**
1. For each anchor, classify properties as attributes vs ties vs knots
2. @system-analyst maps source FKs to tie candidates
3. @business-analyst validates relationship directions match business understanding
4. Debate: Historization decisions for each attribute
5. @analytics-engineer validates consumption patterns supported
6. @data-architect enforces naming conventions

**Debate questions:**
- Is this property a characteristic (attribute) or relationship (tie)?
- Does this value change over time (historized = true)?
- Is this reference data shared across anchors (knot candidate)?
- Is relationship many-to-one (tie) or many-to-many (nexus)?
- What's the correct tie direction ("many X related to one Y")?

**Deliverables:**
- Complete YAML spec with anchors, attributes, ties, knots, nexuses
- All elements follow naming conventions (snake_case, double underscore, no mnemonics)
- Historization flags set with justification
- Relationship directions validated

**Exit criteria:**
- Every attribute has data type and historization flag
- Every tie has clear many-to-one direction
- All names pass convention check (no mnemonics, double underscores)
- @analytics-engineer confirms business questions answerable

### Physical Stage: How to Implement Performantly?

**Goal:** Add indexing, partitioning, and orchestration recommendations

**Inputs:**
- Complete logical model from Logical stage
- Expected data volumes
- Query patterns from business questions

**Activities:**
1. @data-engineer analyzes cardinality and query patterns
2. Recommend indexes on anchors, ties, time-variant attributes
3. Propose partitioning schemes for high-volume historized attributes
4. Suggest orchestration patterns (incremental vs full refresh)

**Debate questions:**
- Which attributes will have high update frequency?
- Which ties will be queried most often?
- What's the expected data volume growth?
- Are there performance-critical business questions?

**Deliverables:**
- Physical optimization annotations in YAML spec
- Index recommendations with justification
- Partitioning schemes for time-variant tables
- Orchestration guidance (separate doc or inline comments)

**Exit criteria:**
- All performance recommendations documented
- @data-engineer confirms no severe bottlenecks identified
- User approves physical design approach
```

**Source:** Anchor Modeling CLP pattern adapted from [Anchor Modeling Tutorials](https://www.anchormodeling.com/tutorials/) and general data warehouse design stages (MEDIUM confidence)

### Pattern 6: Source Schema Reading Protocol

**What:** Structured approach for agents to read and interpret Swagger, OData, ERD files from filesystem

**When to use:** System Analyst initial analysis, source evidence gathering

**Example:**

```markdown
# System Analyst: Source Schema Reading

## When @data-architect Points to Source Files

You'll be given filesystem paths to source schemas. Read them systematically:

### For Swagger/OpenAPI Files (.json, .yaml)

1. **Read file from filesystem** using available tools
2. **Extract entities:** Each schema definition under `components.schemas` is a candidate entity
3. **Extract attributes:** Properties within each schema
4. **Extract relationships:** Look for `$ref` references between schemas (foreign key equivalents)
5. **Note constraints:** Required fields, nullable fields, enum values
6. **Present findings:**

```
Source System Analysis (Swagger: api-spec.yaml)

Entities Identified:
- Customer (properties: id, name, email, created_at)
- Order (properties: id, customer_id, order_date, total_amount)
- Product (properties: id, name, price, category)

Relationships:
- Order.customer_id → Customer.id (many orders to one customer)
- OrderLine.order_id → Order.id (many order lines to one order)
- OrderLine.product_id → Product.id (many order lines to one product)

Constraints:
- Customer.email is unique, required
- Order.customer_id is required (every order has a customer)
- Product.price is nullable (can be NULL if not set)
```

### For OData Metadata ($metadata)

1. **Read XML metadata document**
2. **Extract EntityTypes:** Each `<EntityType>` is a candidate entity
3. **Extract Properties:** `<Property>` elements within EntityTypes
4. **Extract Associations:** `<NavigationProperty>` defines relationships
5. **Present findings** similar to Swagger format

### For ERD/Database Schemas (.sql, .dbml)

1. **Read schema definition**
2. **Extract tables:** Each CREATE TABLE is a candidate entity
3. **Extract columns:** Column definitions are candidate attributes
4. **Extract foreign keys:** FK constraints define relationships
5. **Present findings** similar to Swagger format

### Evidence-Based Argumentation

When debating with @business-analyst, cite specific source evidence:

✅ GOOD: "The source schema shows Order.customer_id as a required FK to Customer.id, indicating every order MUST have a customer. This supports modeling as tie__order__placed_by__customer."

❌ BAD: "I think orders are probably related to customers."

Always provide file paths and specific lines/properties when citing source evidence.
```

**Source:** Adapted from [OpenAPI/Swagger for LLM Function Calling](https://dev.to/samchon/i-made-openapi-and-llm-schema-definitions-1mn0) and semantic kernel OpenAPI plugin patterns (MEDIUM confidence)

### Anti-Patterns to Avoid

- **Vague methodology prompts:** "Follow Anchor Modeling principles" is useless. Encode specific decision trees and checklists.
- **Unbounded debate:** No iteration limit leads to infinite loops. Always cap at 3-5 rounds per topic.
- **Forced consensus:** Don't require agents to agree. If they can't converge, escalate to user — that's valuable signal.
- **Generic anti-pattern review:** "Check for problems" produces generic output. Expand Veteran Reviewer's checklist with detection criteria and fix templates.
- **Assuming LLMs "know" Anchor Modeling:** Training data is stale. Encode methodology explicitly in prompts; don't rely on pre-existing knowledge.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Convergence detection algorithm | Custom similarity scoring | Consensus-based termination (positions align or complement) + iteration limit | Simpler and more transparent; complex metrics (KS statistic) are overkill for text debate |
| YAML schema validation | Custom parser/validator | JSON Schema + Yamale | Standard schemas provide clear contracts; custom validation is error-prone |
| Debate state machine | Custom orchestration logic | OpenCode's @mention + Task tool + bounded iteration in prompts | Platform handles routing; prompts guide behavior |
| Anchor Modeling reference | Inline all rules in every prompt | Shared AGENTS.md with deep methodology + agent-specific decision trees | DRY principle; shared context reduces prompt bloat |

**Key insight:** Phase 4 is about prompt content depth, not code complexity. Encode knowledge explicitly, provide decision trees and checklists, trust the OpenCode platform to orchestrate. The "implementation" is writing better prompts.

## Common Pitfalls

### Pitfall 1: Assuming LLMs Know Anchor Modeling

**What goes wrong:** Agent prompts say "follow Anchor Modeling principles" without encoding what those principles are, assuming training data covered it.

**Why it happens:** Anchor Modeling is niche (insurance/financial sectors in Sweden primarily); LLM training data has limited coverage. Researchers report that even GPT-4 lacks deep knowledge of specialized methodologies.

**How to avoid:** Encode Anchor Modeling rules explicitly in prompts:
- Anchor = immutable identity (never changes, never represents different entity)
- Attribute = historized property (each attribute is own table with validity period)
- Tie = many-to-one relationship (directional, from-side many, to-side one)
- Knot = shared reference data (currency codes, status values)
- Nexus = many-to-many intersection
Provide decision trees for anchor vs attribute vs tie classification.

**Warning signs:** Agent outputs inconsistent classifications, ignores historization, uses wrong naming patterns despite "knowing" Anchor Modeling.

### Pitfall 2: Unbounded Debate Loops

**What goes wrong:** System Analyst and Business Analyst argue indefinitely, never reaching consensus or escalation.

**Why it happens:** No termination condition; agents continue generating arguments as long as they can find differences.

**How to avoid:** Bounded iteration protocol:
- Maximum 5 rounds per topic
- Convergence check after each round (positions align? new arguments?)
- Stagnation detection (same arguments repeated → escalate)
- User escalation format predefined

Research shows consensus-based termination (if agents agree, stop) combined with maximum iteration limit (if not converged by round N, escalate) prevents loops while preserving debate quality.

**Warning signs:** Phase 4 testing shows agents repeating same arguments across 10+ rounds without resolution.

### Pitfall 3: Premature Consensus

**What goes wrong:** System Analyst and Business Analyst agree too quickly, producing shallow models that miss nuances.

**Why it happens:** LLMs are trained to be helpful and agreeable; without opposing default positions, they converge to "sounds reasonable" without deep analysis.

**How to avoid:** Assign contrasting default stances:
- System Analyst: Advocate for source fidelity ("preserve technical reality")
- Business Analyst: Advocate for business meaning ("model business perspective")
Require each analyst to present evidence (source schemas vs business questions) and argue their position before Data Architect synthesizes.

Research on multi-agent debate shows heterogeneous agent positions (opposing defaults) improve output quality by 4-6% over homogeneous agents.

**Warning signs:** Debate completes in 1-2 rounds with no disagreements; final model mirrors source structure without business interpretation or vice versa.

### Pitfall 4: Vague Anti-Pattern Detection

**What goes wrong:** Veteran Reviewer says "this looks good" or "check for god anchors" without specific findings.

**Why it happens:** Generic prompts like "review for anti-patterns" produce generic output; LLMs need concrete checklists to apply.

**How to avoid:** Expand anti-pattern checklist with:
- Detection criteria (specific counts, patterns to match)
- Examples of violations
- Fix templates (step-by-step remediation)
For each of the 10 anti-patterns, provide "if you see X, then check Y, fix with Z" structure.

**Warning signs:** Veteran Reviewer produces 2-sentence reviews; no specific anchor/attribute names cited; no actionable fix recommendations.

### Pitfall 5: CLP Stage Confusion

**What goes wrong:** Agents jump between Conceptual, Logical, and Physical concerns; debate lacks structure; deliverables unclear.

**Why it happens:** Prompts say "conduct CLP debate" without defining what happens in each stage or when to transition.

**How to avoid:** Define CLP stages explicitly:
- Conceptual: Entity identification (what anchors exist?)
- Logical: Relationship definition (how do anchors relate? which attributes? historization?)
- Physical: Performance optimization (indexing, partitioning, orchestration)
Each stage has clear inputs, activities, debate questions, deliverables, and exit criteria.

**Warning signs:** Agents discuss indexing during entity identification; relationship debates continue after logical stage "complete"; unclear when to transition between stages.

## Code Examples

### Anchor vs Attribute Decision Tree (Encoded in Prompt)

```markdown
## Decision Tree: Is This an Anchor or Attribute?

When you encounter a concept in source schemas or business requirements, apply this tree:

**Step 1: Identity Check**
Question: Does this concept have independent business identity?
- YES → Continue to Step 2
- NO → It's an ATTRIBUTE. Ask: "Which anchor does it describe?"

Example: "Customer name" has no independent identity — it describes a customer. ATTRIBUTE.

**Step 2: Existence Check**
Question: Can this concept exist without reference to another entity?
- YES → Continue to Step 3
- NO → It's an ATTRIBUTE or TIE. Ask: "Is it a property or relationship?"

Example: "Order" can't exist without a customer reference in most businesses. But "Order" has independent identity (order ID), so continue.

**Step 3: Business Question Check**
Question: Does the business ask direct questions about this concept?
- "How many X do we have?"
- "What's the status of X?"
- "When was X created?"

If YES → ANCHOR
If NO → ATTRIBUTE

Example: "How many orders?" → Order is ANCHOR. "What's the customer's email?" → Email is ATTRIBUTE.

**Step 4: Shared Concept Check**
Question: Is this concept shared across multiple anchors as reference data?
- YES → It's a KNOT (shared reference data)
- NO → Confirm as ATTRIBUTE

Example: "Currency code" used by orders, products, invoices → KNOT. "Customer email" used only by customer → ATTRIBUTE.

**If uncertain after all steps:** Escalate to @data-architect with your reasoning.
```

**Source:** Derived from Anchor Modeling identity principles (LOW confidence - interpretation of methodology, not direct citation)

### Convergence Detection in Data Architect Prompt

```markdown
## Debate Convergence Assessment

After each debate round between @system-analyst and @business-analyst, evaluate:

**Convergence Indicators (positions align):**
- Both use same entity names → Naming consensus
- Both agree on anchor vs attribute classification → Conceptual alignment
- Both agree on tie direction (many-to-one clarity) → Logical alignment
- Both agree on historization (time-variance understanding) → Temporal alignment
- Positions complement (technical + business both satisfied) → Synthesis ready

**Divergence Indicators (positions moving apart):**
- Entity names diverging (System: "customer_account", Business: "subscriber")
- Classification conflict increasing (one says anchor, other says attribute, arguments strengthening)
- New disagreements emerging (started on ties, now debating attributes too)

**Stagnation Indicators (no progress):**
- Same arguments repeated from previous round
- No new evidence presented (no new source citations, no new business questions)
- Talking past each other (not addressing counterarguments)

**Termination Decision:**
- IF convergence indicators present → SYNTHESIZE and document consensus
- IF divergence and round < 5 → CONTINUE debate with focused questions
- IF divergence and round >= 5 → ESCALATE to user with structured presentation
- IF stagnation detected → ESCALATE immediately (more rounds won't help)

**Escalation Format:**
```
We've reached an impasse on: [topic]

**System Analyst Position:**
[Summary of technical perspective]
Evidence: [Source schema citations]

**Business Analyst Position:**
[Summary of business perspective]
Evidence: [Business questions, process descriptions]

**Anchor Modeling Constraints:**
[Which methodology rules apply to this decision]

**My Recommendation:**
[Synthesis with tradeoffs]

What's your decision? [Clear options for user to choose]
```
```

**Source:** Adapted from [Multi-Agent Debate with Adaptive Stability Detection](https://arxiv.org/pdf/2510.12697) convergence detection patterns (MEDIUM confidence)

### Business Questions as Modeling Evidence

```markdown
# Business Analyst: Using Business Questions as Evidence

## When Arguing for Design Decisions

Business questions are your strongest evidence. Structure arguments:

**Template:**
"The business needs to answer: [question]. This requires [anchor/attribute/tie] because [reasoning]."

**Examples:**

✅ GOOD:
"The business needs to answer: 'What was the customer's loyalty tier on the date of this order?' This requires anchor__order__loyalty_tier_at_purchase with historized=true, because the customer's current tier may have changed since the order was placed."

✅ GOOD:
"The business asks: 'How many orders did each sales rep close last quarter?' This requires tie__order__closed_by__sales_rep (many orders to one rep), not an attribute, because sales rep is an independent business entity we track separately."

❌ BAD:
"I think customer tier should be historized."

❌ BAD:
"Sales rep is probably a relationship."

## Gathering Business Questions

When @data-architect invokes you during Conceptual or Logical stages:

1. **Ask user directly:** "What business questions does this warehouse need to answer?"
2. **Infer from business description:** If user describes "monthly sales reports by region," infer question: "What were sales by region for month X?"
3. **Challenge assumptions:** If @system-analyst proposes design, ask: "What business question does this answer?"

Document all business questions in session context. Reference them during debate.
```

**Source:** Standard business analysis practices (MEDIUM confidence)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic "help me model this" prompts | Domain methodology encoded as decision trees in prompts | 2025-2026 | LLMs produce methodology-compliant output; "Agent Skills" paradigm |
| Unbounded debate until consensus | Bounded iteration + convergence detection + user escalation | 2026 research | Prevents infinite loops; surfaces unresolvable conflicts to human authority |
| Single-agent modeling | Multi-agent debate with opposing positions | 2025-2026 | 4-6% accuracy improvement; prevents premature consensus |
| Implicit prompt engineering | Structured role/contract format with clear sections | 2026 | "Clearer specs" over "longer prompts"; better LLM adherence |
| Assuming LLM "knows" domain | Explicit domain encoding in AGENTS.md + agent prompts | 2026 (Vercel react-best-practices example) | Overcomes stale training data; makes methodology queryable |

**Deprecated/outdated:**
- Relying on LLM pre-training for niche methodologies: Training data is 6-18 months stale; Anchor Modeling not widely covered. Must encode explicitly.
- Open-ended debate: Early multi-agent systems (2024) had no termination logic; 2026 best practice is bounded iterations with escalation.
- Vague anti-pattern checklists: "Review for quality" prompts are 2024-era. 2026 approach: Detection criteria + fix templates + specific examples.

## Open Questions

1. **Iteration limit per CLP stage**
   - What we know: Bounded iteration prevents loops; research uses 5-10 rounds typical
   - What's unclear: Should limit be per-topic (5 rounds for anchor classification, 5 for ties) or per-stage (5 rounds total for Logical stage)?
   - Recommendation: Per-topic limit (5 rounds per anchor/tie/attribute debate) with stage-level ceiling (15 total escalations before requiring user to slow down and clarify). Track in Data Architect session context.

2. **YAML spec schema strictness**
   - What we know: Agents produce YAML specs; Phase 3 has example schemas
   - What's unclear: Should schema be strictly validated (reject malformed YAML) or loosely interpreted (agents fix minor errors)?
   - Recommendation: Strict validation. Use JSON Schema to define anchor/attribute/tie/knot/nexus structure. Agents must produce valid YAML or iteration doesn't count as "complete." Prevents garbage-in to generators.

3. **Historization default (when uncertain)**
   - What we know: Historized attributes track changes over time; missing historization loses history
   - What's unclear: When in doubt, default to `historized: true` or `historized: false`?
   - Recommendation: Default to TRUE. Rationale: "You can always ignore history in queries, but you can't recover lost history." Anchor Modeling principle: non-destructive evolution. Prompts should encode: "If uncertain, historize. Storage is cheap; lost data is expensive."

4. **Source evidence vs business evidence weighting**
   - What we know: System Analyst cites source schemas; Business Analyst cites business questions
   - What's unclear: When evidence conflicts (source says X, business says Y), which wins?
   - Recommendation: Neither "wins" automatically — escalate to user. But guide with: "DAB layer is about business meaning, not source mirroring. If business evidence is strong and source can provide the data, favor business perspective. If source data doesn't exist, can't invent it." Encode in Data Architect synthesis logic.

5. **Veteran Reviewer invocation timing**
   - What we know: Veteran Reviewer critiques final output using anti-pattern checklist
   - What's unclear: Invoke after Logical stage? After Physical stage? Multiple times?
   - Recommendation: Two reviews: (1) After Logical stage (before Physical) — catches structural issues early. (2) After Physical stage (before export) — final check. Each review uses full 10-item checklist but focuses on stage-relevant items (logical review emphasizes god anchors, missing historization, circular ties; physical review emphasizes premature optimization).

## Sources

### Primary (HIGH confidence)

- [Anchor Modeling Official Site](https://www.anchormodeling.com/) - Core concepts, tutorials, naming conventions
- [Anchor Modeling Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) - Methodology overview, history, principles
- [YAML Specification 1.2.2](https://yaml.org/spec/1.2.2/) - YAML format standard for spec output
- [JSON Schema 2020-12](https://json-schema.org/specification) - Schema validation for YAML specs

### Secondary (MEDIUM confidence)

- [Multi-Agent Debate with Adaptive Stability Detection](https://arxiv.org/pdf/2510.12697) - Convergence detection, KS statistic tracking, termination patterns
- [Adaptive Heterogeneous Multi-Agent Debate](https://link.springer.com/article/10.1007/s44443-025-00353-3) - Opposing positions improve accuracy by 4-6%
- [Multi-Agent Debate Strategies for Requirements Engineering](https://arxiv.org/html/2507.05981v1) - Debate-based consensus, bounded iterations
- [Claude Prompt Engineering Best Practices 2026](https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026) - Role/contract format, structured prompts
- [Vercel React Best Practices as Agent Skill](https://reading.torqsoftware.com/notes/software/ai-ml/agentic-coding/2026-01-15-vercel-react-best-practices-agent-skill/) - Domain encoding in AGENTS.md format
- [Business Analyst vs Systems Analyst Debate](https://www.linkedin.com/pulse/business-analysts-vs-systems-debate-janis-strathearn) - Role distinctions, opposing perspectives
- [Data Warehouse Anti-Patterns](https://www.oreilly.com/library/view/patterns-of-data/9781439819906/K11048_C009.xhtml) - Common pitfalls, detection strategies
- [OpenAPI for LLM Function Calling](https://dev.to/samchon/i-made-openapi-and-llm-schema-definitions-1mn0) - Schema reading patterns for agents

### Tertiary (LOW confidence)

- [YAML Schema Validation Tools](https://github.com/23andMe/Yamale) - Yamale library for YAML validation
- [How to Build Multi-Agent Systems 2026](https://differ.blog/p/how-to-build-multi-agent-systems-complete-2026-guide-f50e02) - General multi-agent patterns (not data modeling specific)
- Data warehouse modeling general practices - Multiple sources, no single authoritative 2026 reference found

## Metadata

**Confidence breakdown:**
- Anchor Modeling methodology: MEDIUM - Official site exists but lacks detailed CLP protocol documentation; applying general data modeling patterns to AM context
- Multi-agent debate patterns: MEDIUM - Recent research (2025-2026) provides convergence detection and bounded iteration patterns; adapted to data modeling domain
- Prompt engineering: HIGH - Well-documented 2026 best practices (role/contract format, explicit encoding) from multiple sources
- CLP stage structure: LOW - Inferred from general data warehouse design stages (conceptual/logical/physical) + Anchor Modeling principles; not verified in official AM documentation
- Anti-pattern detection: MEDIUM - General data warehouse anti-patterns well-documented; applied to Anchor Modeling context

**Research date:** 2026-02-08
**Valid until:** 2026-03-08 (30 days) - Domain evolving (multi-agent debate is active research area); Anchor Modeling stable but CLP application not widely documented

**Gaps and limitations:**
- ADSS (Agile Data Storage Solution) methodology not found in external sources — appears to be project-specific terminology. DAS/DAB/DAR layer definitions derived from project documentation, not external validation.
- CLP stage protocol (Conceptual → Logical → Physical) structure inferred from general data modeling patterns, not verified in Anchor Modeling official documentation.
- Bounded iteration limits (5 rounds per topic) adapted from general debate research, not specifically validated for data modeling debates.
- Anti-pattern checklist expansion (detection criteria, fix templates) derived from general data warehouse patterns, not Anchor Modeling-specific sources.
