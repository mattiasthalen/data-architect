# Architecture Research

**Domain:** Claude Code Multi-Agent Skill with Debate Orchestration
**Researched:** 2026-02-07
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Slash Commands   │  │ AskUserQuestion  │  │ Checkpoint UI    │       │
│  │ (/wa:start-model)│  │ (Debate Results) │  │ (Human Review)   │       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
├───────────┴─────────────────────┴─────────────────────┴─────────────────┤
│                    ORCHESTRATOR LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              Workflow State Machine (Main Orchestrator)          │   │
│  │  - CLP Stage Coordinator (Conceptual → Logical → Physical)       │   │
│  │  - Checkpoint Manager (Validation gates between stages)          │   │
│  │  - Agent Spawner (Task tool with subagent_type)                  │   │
│  │  - Debate Moderator (Collects arguments, triggers resolution)    │   │
│  └────┬────────────┬────────────┬────────────┬──────────┬─────────┘   │
│       │            │            │            │          │              │
├───────┴────────────┴────────────┴────────────┴──────────┴─────────────┤
│                         AGENT LAYER                                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌─────────────┐      │
│  │  System    │  │  Business  │  │    Data    │  │  Veteran    │      │
│  │  Analyst   │  │  Analyst   │  │  Architect │  │  Reviewer   │      │
│  │            │  │            │  │            │  │             │      │
│  │ (Technical │  │ (Business  │  │ (Synthesis │  │ (Quality    │      │
│  │  focus)    │  │  focus)    │  │  + rules)  │  │  critique)  │      │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └──────┬──────┘      │
│        │               │               │                 │             │
├────────┴───────────────┴───────────────┴─────────────────┴─────────────┤
│                    SPECIFICATION LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               YAML/JSON Specification Files                      │  │
│  │  - anchors.yaml (Entities with identity)                         │  │
│  │  - attributes.yaml (Temporal properties)                         │  │
│  │  - ties.yaml (Relationships)                                     │  │
│  │  - knots.yaml (Static reference data)                            │  │
│  └────────────────────┬─────────────────────────────────────────────┘  │
├───────────────────────┴─────────────────────────────────────────────────┤
│                    GENERATOR LAYER                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  SQL DDL     │  │  DBT Models  │  │  Docs/ERD    │                  │
│  │  Generator   │  │  Generator   │  │  Generator   │                  │
│  │              │  │              │  │              │                  │
│  │ (Deterministic code generation from specs)                          │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Workflow State Machine** | Coordinates CLP progression, manages checkpoints, spawns agents | Markdown command file with workflow logic |
| **System Analyst Agent** | Argues technical feasibility, data source constraints, schema design | Subagent with technical prompting (`.claude/agents/wa-system-analyst.md`) |
| **Business Analyst Agent** | Argues business value, user needs, reporting requirements | Subagent with business prompting (`.claude/agents/wa-business-analyst.md`) |
| **Data Architect Agent** | Synthesizes debate into Anchor Model elements, applies methodology rules | Subagent with Anchor Modeling knowledge (`.claude/agents/wa-data-architect.md`) |
| **Veteran Reviewer Agent** | Reviews synthesized model for methodology compliance, flags issues | Subagent with quality gates (`.claude/agents/wa-veteran-reviewer.md`) |
| **Checkpoint Manager** | Validates stage completion, gates progression to next stage | Logic embedded in orchestrator workflow |
| **Specification Writer** | Writes YAML/JSON files for Anchor Model elements | Logic in Data Architect agent |
| **Deterministic Generators** | Transforms specs to platform code (SQL DDL, DBT, docs) | Scripts/templates in `.claude/generators/` |

## Recommended Project Structure

```
.claude/
├── agents/                      # Agent definitions (Markdown with YAML frontmatter)
│   ├── wa-system-analyst.md     # Technical perspective debater
│   ├── wa-business-analyst.md   # Business perspective debater
│   ├── wa-data-architect.md     # Synthesis and Anchor Modeling expert
│   ├── wa-veteran-reviewer.md   # Methodology compliance reviewer
│   └── wa-orchestrator.md       # Optional: CLP workflow coordinator
├── commands/                    # User-facing slash commands
│   └── wa/
│       ├── start-model.md       # Initiate new modeling session
│       ├── debate-anchor.md     # Run debate on specific anchor
│       ├── checkpoint.md        # Force checkpoint validation
│       └── generate.md          # Run generators on specs
├── hooks/                       # Lifecycle hooks
│   ├── pre-debate.sh            # Validate debate inputs
│   └── post-checkpoint.sh       # Auto-commit specs on checkpoint pass
├── generators/                  # Deterministic code generators
│   ├── sql-ddl/                 # SQL DDL generator
│   │   ├── anchor.sql.tmpl      # Anchor table template
│   │   ├── attribute.sql.tmpl   # Attribute table template
│   │   └── generate.sh          # Generator entry point
│   ├── dbt/                     # DBT model generator
│   │   └── generate.sh
│   └── docs/                    # Documentation generator
│       └── generate.sh
├── templates/                   # Specification and workflow templates
│   ├── anchor-spec.yaml         # Template for anchor definition
│   ├── attribute-spec.yaml      # Template for attribute definition
│   ├── debate-context.md        # Debate session context template
│   └── checkpoint-report.md     # Checkpoint validation report
└── references/                  # Domain knowledge
    ├── anchor-modeling.md       # Anchor Modeling methodology reference
    ├── debate-protocol.md       # How DAB debate works
    └── clp-workflow.md          # CLP stage definitions

.warehouse/                      # Warehouse modeling workspace (not .planning)
├── specs/                       # Specification files (source of truth)
│   ├── conceptual/              # CLP Stage 1
│   │   ├── anchors.yaml         # Entity definitions
│   │   └── relationships.md     # High-level relationships
│   ├── logical/                 # CLP Stage 2
│   │   ├── anchors.yaml         # Refined anchors with metadata
│   │   ├── attributes.yaml      # Temporal attributes
│   │   ├── ties.yaml            # Relationships between anchors
│   │   └── knots.yaml           # Static reference data
│   └── physical/                # CLP Stage 3
│       ├── anchors.yaml         # Physical naming, indexing
│       ├── attributes.yaml      # Column types, constraints
│       ├── ties.yaml            # Foreign key mappings
│       └── deployment.yaml      # Platform-specific config
├── debates/                     # Debate session artifacts
│   ├── 001-customer-anchor/
│   │   ├── system-argument.md   # System Analyst position
│   │   ├── business-argument.md # Business Analyst position
│   │   ├── resolution.md        # Data Architect synthesis
│   │   └── review.md            # Veteran Reviewer critique
│   └── 002-order-anchor/
│       └── ...
├── checkpoints/                 # Checkpoint validation reports
│   ├── conceptual-complete.md   # Stage 1 validation
│   ├── logical-complete.md      # Stage 2 validation
│   └── physical-complete.md     # Stage 3 validation
└── generated/                   # Output from deterministic generators
    ├── sql/                     # SQL DDL
    │   ├── schema.sql
    │   └── indexes.sql
    ├── dbt/                     # DBT models
    │   ├── models/
    │   └── dbt_project.yml
    └── docs/                    # Documentation
        ├── erd.md
        └── data-dictionary.md
```

### Structure Rationale

- **`.claude/agents/`**: Agent definitions live in skill directory for portability. Each agent is a Markdown file with role definition and prompting strategy.
- **`.claude/generators/`**: Deterministic generators are scripts/templates, not AI agents. They consume YAML specs and produce platform code.
- **`.warehouse/specs/`**: Source of truth specification files organized by CLP stage. Progressive refinement from conceptual → logical → physical.
- **`.warehouse/debates/`**: Debate artifacts for traceability. Each debate session captured for review and learning.
- **`.warehouse/checkpoints/`**: Validation gates between CLP stages. Must pass to progress.
- **`.warehouse/generated/`**: Output directory for generated artifacts. Treated as disposable (regenerate from specs).

## Architectural Patterns

### Pattern 1: DAB (Debate-Argumentation-Balance) Orchestration

**What:** Multi-agent debate pattern where System Analyst and Business Analyst argue opposing perspectives, Data Architect synthesizes, Veteran Reviewer critiques, and user decides.

**When to use:** Modeling decisions with inherent technical vs business tension (e.g., granularity of temporal tracking, anchor vs attribute classification).

**Trade-offs:**
- **Pros:** Surfaces hidden assumptions, explores design space, produces well-reasoned decisions
- **Cons:** Higher token cost, requires orchestrator complexity, can produce analysis paralysis

**Example:**
```yaml
# Debate session configuration
debate:
  topic: "Should OrderStatus be an Anchor or Attribute of Order?"
  participants:
    - agent: wa-system-analyst
      stance: "Attribute - low cardinality, tightly coupled to Order lifecycle"
    - agent: wa-business-analyst
      stance: "Anchor - business process stages, independent temporal tracking"
  synthesizer: wa-data-architect
  reviewer: wa-veteran-reviewer
  decision_gate: user  # human decides after review
```

**Orchestrator logic:**
```markdown
1. Spawn System Analyst with topic prompt → collect argument
2. Spawn Business Analyst with topic + System arg → collect counter-argument
3. Spawn Data Architect with both arguments → synthesize recommendation
4. Spawn Veteran Reviewer with synthesis → critique
5. Present all to user via AskUserQuestion → user decides
6. Record decision in debate artifact
```

### Pattern 2: CLP Progressive Refinement Workflow

**What:** Stage-gated workflow moving from Conceptual (entities, relationships) → Logical (Anchor Model elements) → Physical (platform-specific implementation).

**When to use:** Data warehouse modeling where premature physical decisions constrain logical design.

**Trade-offs:**
- **Pros:** Prevents premature optimization, enforces separation of concerns, enables platform portability
- **Cons:** Requires discipline to not skip stages, overhead of multiple spec refinements

**Example:**
```markdown
## CLP Workflow State Machine

State: CONCEPTUAL
- Identify business entities (Anchors)
- Define high-level relationships
- No temporal or physical concerns yet
Checkpoint: All business entities identified? Relationships clear?
→ LOGICAL

State: LOGICAL
- Classify Anchor elements (anchors, attributes, ties, knots)
- Define temporal tracking strategy (historization, point-in-time)
- Apply Anchor Modeling methodology rules
Checkpoint: Methodology compliance? 6NF normalized? Temporal strategy complete?
→ PHYSICAL

State: PHYSICAL
- Map to target platform (Snowflake, BigQuery, Postgres)
- Define indexing, partitioning, clustering
- Generate DDL, DBT models, documentation
Checkpoint: Platform-specific optimizations applied? Generated code compiles?
→ COMPLETE
```

### Pattern 3: Specification-Driven Generation

**What:** Deterministic code generators consume YAML/JSON specifications and produce platform-specific artifacts (SQL DDL, DBT models, documentation).

**When to use:** When generated code must be repeatable, auditable, and version-controlled alongside specs.

**Trade-offs:**
- **Pros:** Single source of truth (specs), regeneration on spec change, platform portability
- **Cons:** Requires maintaining generator templates, debugging generation errors harder than handwritten code

**Example:**
```yaml
# specs/logical/anchors.yaml
anchors:
  - name: Customer
    identity: CustomerID
    business_key: EmailAddress
    description: Individual or organization placing orders
    historization: true
    metadata:
      source_system: CRM
      data_owner: Sales Team

  - name: Order
    identity: OrderID
    business_key: OrderNumber
    description: Purchase transaction
    historization: true
    metadata:
      source_system: ERP
      data_owner: Operations Team
```

**Generator transformation:**
```sql
-- Generated from specs/logical/anchors.yaml
CREATE TABLE Customer_Anchor (
    CustomerID BIGINT PRIMARY KEY,
    LoadedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LoadedBy VARCHAR(255) NOT NULL DEFAULT CURRENT_USER
);

CREATE TABLE Customer_EmailAddress (
    CustomerID BIGINT NOT NULL,
    EmailAddress VARCHAR(255) NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NULL,
    LoadedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer_Anchor(CustomerID)
);
```

### Pattern 4: Checkpoint-Gated Progression

**What:** Validation gates between CLP stages that must pass before workflow continues. Prevents moving to Physical with incomplete Logical design.

**When to use:** Multi-stage workflows where later stages depend on earlier stage completeness.

**Trade-offs:**
- **Pros:** Enforces quality gates, prevents downstream rework, creates audit trail
- **Cons:** Can feel bureaucratic, requires thoughtful checkpoint criteria

**Example:**
```markdown
## Logical → Physical Checkpoint

Validation criteria:
- [ ] All anchors have identity and business key defined
- [ ] All attributes reference valid anchors
- [ ] All ties define both anchor endpoints
- [ ] Knot cardinality validated (< 1000 values)
- [ ] 6NF normalization verified
- [ ] Temporal strategy consistent across model
- [ ] Veteran Reviewer flagged zero critical issues

Result: PASS / FAIL (with issues list)

If PASS: Write checkpoint/.../logical-complete.md, transition to PHYSICAL
If FAIL: Present issues to user, remain in LOGICAL stage
```

## Data Flow

### Request Flow

```
User initiates modeling session
    ↓
/wa:start-model → Orchestrator creates CLP state machine
    ↓
Orchestrator loads Conceptual stage → User defines entities
    ↓
For each entity decision requiring debate:
    ↓
Orchestrator spawns DAB debate:
    System Analyst → argument.md
    Business Analyst → counter-argument.md
    Data Architect → synthesis.md
    Veteran Reviewer → critique.md
    ↓
User reviews debate output → AskUserQuestion → decision
    ↓
Orchestrator records decision → updates spec YAML
    ↓
Repeat for all Conceptual decisions
    ↓
Orchestrator triggers Conceptual checkpoint → validation
    ↓
Checkpoint PASS → transition to Logical stage
    ↓
Repeat debate/checkpoint pattern for Logical stage
    ↓
Logical checkpoint PASS → transition to Physical stage
    ↓
Physical stage refines specs → triggers generators
    ↓
Generators produce SQL DDL, DBT, docs → written to generated/
    ↓
Physical checkpoint validates generated artifacts
    ↓
Workflow COMPLETE
```

### State Management

```
[Orchestrator State File: .warehouse/state.yaml]
    ↓ (read/write)
Orchestrator tracks:
- current_stage: conceptual | logical | physical | complete
- completed_checkpoints: [list]
- pending_debates: [list]
- decisions: [{topic, result, timestamp}]
    ↓ (spawns agents via Task tool)
Agents read state → produce artifacts → write to debates/
    ↓ (triggers validation)
Checkpoint logic reads specs + debates → produces checkpoint report
    ↓ (updates state on pass)
Orchestrator updates state.yaml → transitions to next stage
```

### Key Data Flows

1. **Debate Flow:** User question → Orchestrator spawns 4 agents in sequence → agents write Markdown artifacts → Orchestrator presents to user → User decision recorded
2. **Spec Flow:** Agent decisions → Data Architect writes YAML → Checkpoint reads YAML → Validation rules check YAML → Checkpoint report
3. **Generation Flow:** Specs YAML → Generator templates → Generated code (SQL/DBT/Docs) → Output to generated/ directory

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1-5 anchors | Single orchestrator, sequential debates, human checkpoints sufficient |
| 5-20 anchors | Parallelize debates (debate multiple anchors simultaneously), automated checkpoint validation, batch generation |
| 20+ anchors | Introduce debate prioritization (high-impact decisions first), checkpoint caching (skip re-validation of unchanged specs), incremental generation (only regenerate changed entities) |

### Scaling Priorities

1. **First bottleneck:** Debate latency — mitigate with parallel debate spawning (independent anchors can be debated simultaneously)
2. **Second bottleneck:** Checkpoint validation cost — mitigate with incremental validation (only validate changed specs, cache validation results)
3. **Third bottleneck:** Generation time — mitigate with incremental generation (detect spec changes, regenerate only affected artifacts)

## Anti-Patterns

### Anti-Pattern 1: Skipping CLP Stages

**What people do:** Jump directly to Physical (SQL DDL) without Conceptual/Logical modeling
**Why it's wrong:** Embeds platform assumptions early, prevents portability, mixes business logic with physical optimization
**Do this instead:** Follow CLP progression strictly. Enforce checkpoint gates. Physical specs should be pure refinement of Logical specs.

### Anti-Pattern 2: AI Agents in Generators

**What people do:** Use LLM agents to generate SQL DDL from specs
**Why it's wrong:** Non-deterministic output, unpredictable token costs, hard to debug, breaks repeatability
**Do this instead:** Deterministic template-based generation. Generators are scripts/Jinja2 templates, not AI agents. Specs → Templates → Code.

### Anti-Pattern 3: Debate without Decision Recording

**What people do:** Run debates, user decides, but decision rationale not captured
**Why it's wrong:** Lost institutional knowledge, debate must be re-run when revisiting decision, no audit trail
**Do this instead:** Every debate session writes artifacts (arguments, synthesis, critique, decision). Store in `.warehouse/debates/[topic]/` for traceability.

### Anti-Pattern 4: Monolithic Orchestrator

**What people do:** Single massive Markdown file with all CLP logic, debate spawning, checkpoint validation
**Why it's wrong:** Hard to maintain, hard to test individual stages, can't reuse debate logic across skills
**Do this instead:** Modular orchestrator composition. `/wa:start-model` orchestrates CLP flow. `/wa:debate-anchor` is reusable debate command. Checkpoint logic in separate files.

### Anti-Pattern 5: User as Rubber Stamp

**What people do:** Present debate results with pre-selected "correct" answer
**Why it's wrong:** Defeats purpose of debate, user loses agency, debate becomes theater
**Do this instead:** Present all perspectives neutrally. AskUserQuestion with options for each agent's recommendation plus "custom decision". User is final authority.

### Anti-Pattern 6: Specs as Documentation

**What people do:** Treat YAML specs as generated from code (reverse-engineering)
**Why it's wrong:** Specs lose status as source of truth, become stale, generation becomes impossible
**Do this instead:** Specs are source of truth. Code is generated from specs. Never reverse-engineer specs from generated code.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **Git** | Checkpoint commits specs + debates | Use hooks to auto-commit on checkpoint pass |
| **Data Catalog** | Export metadata from specs YAML | Generated docs include data lineage, ownership |
| **DBT** | Generate DBT models from specs | DBT project structure follows Anchor naming conventions |
| **BI Tools** | Generate semantic layer from specs | Anchor → Fact, Attribute → Dimension mappings |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **Orchestrator ↔ Agents** | Task tool with structured prompts | Agents are stateless, orchestrator maintains conversation context |
| **Agents ↔ Specs** | File I/O (Read YAML, Write YAML) | Data Architect agent writes YAML, other agents read for context |
| **Orchestrator ↔ Generators** | Bash execution with spec paths | Generators are scripts, not agents. Orchestrator calls via Bash tool |
| **Checkpoint ↔ Specs** | YAML validation logic | Checkpoint reads specs, applies Anchor Modeling rules, produces report |

## Build Order Implications

**Phase 1: Core Orchestrator (Foundation)**
- CLP state machine workflow
- Basic checkpoint validation logic
- Spec file I/O (read/write YAML)
- State management (`.warehouse/state.yaml`)

**Phase 2: Agent System (Debate Capability)**
- System Analyst agent definition
- Business Analyst agent definition
- Data Architect agent (synthesis + spec writing)
- Veteran Reviewer agent (quality gates)
- Debate orchestration command (`/wa:debate-anchor`)

**Phase 3: Specification System (Source of Truth)**
- YAML schema definitions (anchors, attributes, ties, knots)
- Spec validation logic (JSON Schema or custom)
- Spec versioning (track changes across CLP stages)

**Phase 4: Checkpoint System (Quality Gates)**
- Conceptual checkpoint criteria
- Logical checkpoint criteria (Anchor Modeling rules)
- Physical checkpoint criteria (platform-specific validation)
- Checkpoint reporting (`checkpoint-report.md`)

**Phase 5: Generator System (Code Production)**
- SQL DDL generator (Anchor → tables)
- DBT model generator (Anchor → DBT models)
- Documentation generator (ERD, data dictionary)
- Generator orchestration (`/wa:generate` command)

**Dependencies:**
- Phase 2 depends on Phase 1 (agents need orchestrator)
- Phase 3 depends on Phase 2 (specs written by Data Architect agent)
- Phase 4 depends on Phase 3 (checkpoints validate specs)
- Phase 5 depends on Phase 4 (generators consume validated specs)

## Sources

**Multi-Agent Orchestration:**
- [AI Agent Orchestration Patterns - Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Choosing the Right Multi-Agent Architecture - LangChain](https://blog.langchain.com/choosing-the-right-multi-agent-architecture/)
- [Google's Eight Essential Multi-Agent Design Patterns - InfoQ](https://www.infoq.com/news/2026/01/multi-agent-design-patterns/)
- [Model Context Protocol architecture patterns for multi-agent AI systems - IBM](https://developer.ibm.com/articles/mcp-architecture-patterns-ai-systems/)

**Debate Systems:**
- [AI models that simulate internal debate dramatically improve accuracy - VentureBeat](https://venturebeat.com/orchestration/ai-models-that-simulate-internal-debate-dramatically-improve-accuracy-on)
- [Patterns for Democratic Multi-Agent AI: Debate-Based Consensus - Medium](https://medium.com/@edoardo.schepis/patterns-for-democratic-multi-agent-ai-debate-based-consensus-part-1-8ef80557ff8a)
- [Multi-Agent Debate Strategies to Enhance Requirements Engineering - arXiv](https://arxiv.org/html/2507.05981v1)

**Workflow Orchestration:**
- [Temporal: Beyond State Machines for Reliable Distributed Applications](https://temporal.io/blog/temporal-replaces-state-machines-for-distributed-applications)
- [Checkpointing and Resuming Workflows - Microsoft Learn](https://learn.microsoft.com/en-us/agent-framework/tutorials/workflows/checkpointing-and-resuming)
- [Agentic Workflows in 2026: The ultimate guide - Vellum](https://www.vellum.ai/blog/agentic-workflows-emerging-architectures-and-design-patterns)

**Claude Code Architecture:**
- [Build Agent Skills Faster with Claude Code 2.1 - Medium](https://medium.com/@richardhightower/build-agent-skills-faster-with-claude-code-2-1-release-6d821d5b8179)
- [Claude Skills vs Sub-agents: Architecture and Patterns - Medium](https://medium.com/@SandeepTnvs/claude-skills-vs-sub-agents-architecture-use-cases-and-effective-patterns-3e535c9e0122)
- [Claude Code Swarm Orchestration Skill - GitHub](https://gist.github.com/kieranklaassen/4f2aba89594a4aea4ad64d753984b2ea)

**Data Modeling Workflow:**
- [Data Modeling: Conceptual vs Logical vs Physical - Visual Paradigm](https://online.visual-paradigm.com/knowledge/visual-modeling/conceptual-vs-logical-vs-physical-data-model/)
- [The Traditional Levels of Data Modeling - Practical Data Modeling](https://practicaldatamodeling.substack.com/p/the-traditional-levels-of-data-modeling)
- [Developing Data Workflows: From Conceptual Blueprints to Physical Implementation - MDPI](https://www.mdpi.com/2306-5729/10/7/97)

**Specification-Driven Generation:**
- [Understanding Specification-Driven Code Generation - arXiv](https://arxiv.org/pdf/2601.03878)
- [Deterministic code generation - Intent Architect](https://docs.intentarchitect.com/articles/key-concepts/deterministic-codegen.html)

**Anchor Modeling:**
- [Anchor Modeling - Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling)
- [Anchor Modeling - Official Site](https://www.anchormodeling.com/)
- [Anchor Modeling - ResearchGate](https://www.researchgate.net/publication/229347991_Anchor_modeling_-_Agile_information_modeling_in_evolving_data_environments)

---
*Architecture research for: Warehouse Architect (Claude Code Multi-Agent Skill)*
*Researched: 2026-02-07*
