# Roadmap: Warehouse Architect

## Overview

This roadmap progresses from multi-agent debate foundation through CLP workflow enforcement to Anchor Modeling implementation and deterministic code generation. Each phase builds on the last: orchestration enables debate, debate produces specifications, specifications drive generation. The journey validates the core value — genuine agent collaboration producing methodology-compliant Anchor Models — through a working demo scenario.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Multi-agent debate orchestration and agent infrastructure
- [ ] **Phase 2: CLP Workflow** - Conceptual-Logical-Physical progression with specification system
- [ ] **Phase 3: Anchor Modeling** - Core methodology implementation with temporal and historization patterns
- [ ] **Phase 4: Code Generation** - Deterministic generators for SQL DDL, dbt, and diagrams
- [ ] **Phase 5: Validation** - End-to-end demo scenario proving the complete workflow

## Phase Details

### Phase 1: Foundation
**Goal**: Multi-agent debate system with bounded iteration, convergence metrics, and persistent context infrastructure that prevents infinite loops and enables genuine critique
**Depends on**: Nothing (first phase)
**Requirements**: ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-05, ORCH-06, ORCH-07, ORCH-08, AGNT-01, AGNT-02, AGNT-03, AGNT-04, AGNT-05, AGNT-06
**Success Criteria** (what must be TRUE):
  1. System Analyst and Business Analyst agents can debate a modeling decision through multiple rounds with distinct perspectives
  2. Data Architect agent synthesizes debate positions and produces a recommendation with supporting rationale
  3. Anchor Modeling methodology rules are automatically applied as objective validation on architect recommendations
  4. User receives full debate transcript (arguments, synthesis, rules check, recommendation) and makes final decision
  5. Veteran Reviewer agent critiques completed models and identifies anti-patterns or methodology violations
  6. Debate terminates after maximum iteration count to prevent infinite loops
  7. Workflow state persists to `.warehouse/state.yaml` and restores across sessions
  8. All debate decisions are logged with rationale in audit trail
**Plans**: TBD

Plans:
- [ ] TBD (to be planned)

### Phase 2: CLP Workflow
**Goal**: Enforced Conceptual-Logical-Physical progression with stage gates, YAML specification format, and business domain extraction that prevents premature physical modeling
**Depends on**: Phase 1
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05, MODL-01, MODL-02, MODL-03
**Success Criteria** (what must be TRUE):
  1. User can provide business description and get initial conceptual entities extracted through agent debate
  2. User can provide source schemas (Swagger, OData, ERD) and agents incorporate them into system perspective
  3. User can provide business questions and agents use them to inform what the warehouse must answer
  4. CLP workflow enforces checkpoint gates — cannot proceed to logical until conceptual passes validation
  5. YAML specification format with Zod schema validation stores all Anchor Model elements (anchors, attributes, ties, knots)
  6. Specs are versioned with explicit version field and organized by CLP stage (conceptual/, logical/, physical/)
  7. Markdown documentation auto-renders from YAML specs for human review
  8. Naming conventions are configurable and enforced during spec validation
**Plans**: TBD

Plans:
- [ ] TBD (to be planned)

### Phase 3: Anchor Modeling
**Goal**: Anchor Modeling methodology rules implemented with selective application criteria, temporal patterns, and historization strategies to prevent 6NF over-application
**Depends on**: Phase 2
**Requirements**: MODL-04, MODL-05, MODL-06, MODL-07, DEMO-02
**Success Criteria** (what must be TRUE):
  1. Data Architect agent correctly classifies entities as anchors, attributes, ties, or knots following Anchor Modeling rules
  2. Temporal extensions work for historized attributes with valid-from/valid-to timestamps
  3. Historization strategy is decided at conceptual level and enforced consistently through logical and physical stages
  4. Knot tables are used for static reference data with low cardinality instead of full anchor treatment
  5. Roenbaeck's Anchor Modeling repository (XML format, generators) has been studied and methodology rules validated against reference implementation
**Plans**: TBD

Plans:
- [ ] TBD (to be planned)

### Phase 4: Code Generation
**Goal**: Deterministic template-based generators producing SQL DDL, dbt models, and diagrams from validated specs with version compatibility checking
**Depends on**: Phase 3
**Requirements**: GENR-01, GENR-02, GENR-03, GENR-04, GENR-05, GENR-06, GENR-07
**Success Criteria** (what must be TRUE):
  1. SQL DDL generator produces CREATE TABLE statements from validated specs for multiple dialects (platform-agnostic with targets)
  2. dbt model generator produces dbt models with configs, tests, and docs from validated specs
  3. Mermaid diagram generator produces ER diagrams from specs showing anchors, attributes, ties, and knots
  4. Schema evolution generator produces non-destructive migration scripts (additive only, no DROP/ALTER destructive operations)
  5. All generators are deterministic — same spec input always produces identical output
  6. Generated code includes traceability comments with spec version and generation timestamp
  7. Generators validate spec version compatibility and reject incompatible versions with clear error messages
**Plans**: TBD

Plans:
- [ ] TBD (to be planned)

### Phase 5: Validation
**Goal**: Complete demo scenario (e-commerce) validates full workflow from business description through agent debate, CLP progression, Anchor Model specs, to generated code
**Depends on**: Phase 4
**Requirements**: DEMO-01
**Success Criteria** (what must be TRUE):
  1. Demo scenario executes complete workflow: business description input → conceptual entities → logical Anchor Model → physical specs → generated SQL DDL
  2. Demo includes System Analyst vs Business Analyst debates with Data Architect synthesis and user decisions
  3. Demo produces valid YAML specs that pass Zod validation
  4. Demo generates SQL DDL that executes successfully on target database (PostgreSQL or Snowflake)
  5. Demo generates dbt models that pass dbt compile and test
  6. Veteran Reviewer critiques demo output and identifies at least one improvement or validates methodology compliance
**Plans**: TBD

Plans:
- [ ] TBD (to be planned)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/TBD | Not started | - |
| 2. CLP Workflow | 0/TBD | Not started | - |
| 3. Anchor Modeling | 0/TBD | Not started | - |
| 4. Code Generation | 0/TBD | Not started | - |
| 5. Validation | 0/TBD | Not started | - |

---
*Roadmap created: 2026-02-07*
*Last updated: 2026-02-07*
