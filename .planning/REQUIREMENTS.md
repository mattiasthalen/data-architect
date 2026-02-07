# Requirements: Warehouse Architect

**Defined:** 2026-02-07
**Core Value:** The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate — not template generation.

## v1 Requirements

### Orchestration

- [ ] **ORCH-01**: CLP workflow enforces Conceptual → Logical → Physical progression with checkpoint gates between stages
- [ ] **ORCH-02**: System Analyst and Business Analyst agents debate each modeling decision through structured argumentation
- [ ] **ORCH-03**: Data Architect agent synthesizes debate positions and produces a recommendation
- [ ] **ORCH-04**: Anchor Modeling methodology rules are applied as an objective check on architect's recommendation
- [ ] **ORCH-05**: User receives full debate context (arguments, synthesis, rules check) and makes final decision
- [ ] **ORCH-06**: Veteran Reviewer agent critiques completed model for anti-patterns and methodology violations
- [ ] **ORCH-07**: Workflow state persists across sessions (current CLP stage, decisions made, pending debates)
- [ ] **ORCH-08**: Each debate decision is logged with rationale for audit trail

### Agent Definitions

- [ ] **AGNT-01**: System/Integration Analyst agent with technical/source-system persona and prompting
- [ ] **AGNT-02**: Business Analyst agent with domain/business-needs persona and prompting
- [ ] **AGNT-03**: Data Architect agent with Anchor Modeling expertise and synthesis capability
- [ ] **AGNT-04**: Data Engineer agent with physical modeling and performance optimization focus
- [ ] **AGNT-05**: Analytics Engineer agent with consumption/reporting layer focus
- [ ] **AGNT-06**: Veteran Reviewer agent with grumpy veteran persona, anti-pattern detection, methodology critique

### Modeling

- [ ] **MODL-01**: User can start from business description ("we sell bikes") and get initial conceptual entities extracted
- [ ] **MODL-02**: User can provide source schemas (Swagger, OData, ERD) to understand existing source systems
- [ ] **MODL-03**: User can provide business questions to inform what the warehouse must answer
- [ ] **MODL-04**: Anchor Model core constructs supported: anchors, attributes, ties, knots
- [ ] **MODL-05**: Temporal extensions supported: historized attributes with valid-from/valid-to
- [ ] **MODL-06**: Historization strategy decided at conceptual level and enforced through logical and physical
- [ ] **MODL-07**: Knot tables for static reference data with low cardinality

### Specifications

- [ ] **SPEC-01**: YAML/JSON specification format for all Anchor Model elements with Zod schema validation
- [ ] **SPEC-02**: Specs versioned with explicit version field; generators check compatibility
- [ ] **SPEC-03**: Markdown documentation auto-rendered from YAML/JSON specs
- [ ] **SPEC-04**: Naming conventions configurable and enforced during spec validation
- [ ] **SPEC-05**: Specs organized by CLP stage (conceptual/, logical/, physical/)

### Code Generation

- [ ] **GENR-01**: SQL DDL generator produces CREATE TABLE statements from validated specs
- [ ] **GENR-02**: DDL generation supports multiple SQL dialects (platform-agnostic with targets)
- [ ] **GENR-03**: dbt model generator produces dbt models from validated specs
- [ ] **GENR-04**: Mermaid diagram generator produces ER diagrams from specs
- [ ] **GENR-05**: Schema evolution generator produces non-destructive migration scripts (additive only)
- [ ] **GENR-06**: All generators are deterministic — same spec always produces same output
- [ ] **GENR-07**: Generated code includes traceability comments (spec version, generation timestamp)

### Reference Implementation

- [ ] **DEMO-01**: Demo scenario (e-commerce) validates full workflow from business description through generated code
- [ ] **DEMO-02**: Roenbaeck's Anchor Modeling repo (XML format, generators) studied and referenced for methodology rules

## v2 Requirements

### DAS Layer (Data According to System)

- **DAS-01**: Historized raw data ingestion from source systems
- **DAS-02**: Source system metadata tracking and provenance
- **DAS-03**: DAS → DAB transformation orchestration

### DAR Layer (Data According to Requirements)

- **DAR-01**: Unified Star Schema (Puppini) for reporting/consumption layer
- **DAR-02**: Isolated data products per ADSS principles
- **DAR-03**: DAB → DAR transformation orchestration

### Extended Platform Support

- **PLAT-01**: Additional SQL dialect generators (BigQuery, Redshift, Databricks)
- **PLAT-02**: Agent personality configuration (conservative vs aggressive design)
- **PLAT-03**: Schema evolution impact analysis before applying migrations

## Out of Scope

| Feature | Reason |
|---------|--------|
| Visual drag-drop modeling UI | YAML-first, GitOps approach — diagrams generated from specs, not the other way around |
| Real-time collaborative editing | Anchor Modeling requires deliberation; async PR-based workflow with structured debate rounds |
| Support all modeling methodologies | Opinionated: ADSS + Anchor Modeling + USS. Diluting focus defeats the purpose |
| Fully autonomous deployment | Schema changes require human approval; AI generates, humans review and execute |
| Web application | Claude Code skill — runs in CLI, not browser |
| Real-time streaming support | Batch-first for v1; different problem domain |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ORCH-01 | Phase 1 | Pending |
| ORCH-02 | Phase 1 | Pending |
| ORCH-03 | Phase 1 | Pending |
| ORCH-04 | Phase 1 | Pending |
| ORCH-05 | Phase 1 | Pending |
| ORCH-06 | Phase 1 | Pending |
| ORCH-07 | Phase 1 | Pending |
| ORCH-08 | Phase 1 | Pending |
| AGNT-01 | Phase 1 | Pending |
| AGNT-02 | Phase 1 | Pending |
| AGNT-03 | Phase 1 | Pending |
| AGNT-04 | Phase 1 | Pending |
| AGNT-05 | Phase 1 | Pending |
| AGNT-06 | Phase 1 | Pending |
| MODL-01 | Phase 2 | Pending |
| MODL-02 | Phase 2 | Pending |
| MODL-03 | Phase 2 | Pending |
| MODL-04 | Phase 3 | Pending |
| MODL-05 | Phase 3 | Pending |
| MODL-06 | Phase 3 | Pending |
| MODL-07 | Phase 3 | Pending |
| SPEC-01 | Phase 2 | Pending |
| SPEC-02 | Phase 2 | Pending |
| SPEC-03 | Phase 2 | Pending |
| SPEC-04 | Phase 2 | Pending |
| SPEC-05 | Phase 2 | Pending |
| GENR-01 | Phase 4 | Pending |
| GENR-02 | Phase 4 | Pending |
| GENR-03 | Phase 4 | Pending |
| GENR-04 | Phase 4 | Pending |
| GENR-05 | Phase 4 | Pending |
| GENR-06 | Phase 4 | Pending |
| GENR-07 | Phase 4 | Pending |
| DEMO-01 | Phase 5 | Pending |
| DEMO-02 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 35 total
- Mapped to phases: 35 (100% coverage)
- Unmapped: 0

**Phase Distribution:**
- Phase 1 (Foundation): 14 requirements
- Phase 2 (CLP Workflow): 8 requirements
- Phase 3 (Anchor Modeling): 5 requirements
- Phase 4 (Code Generation): 7 requirements
- Phase 5 (Validation): 1 requirement

---
*Requirements defined: 2026-02-07*
*Last updated: 2026-02-07 after roadmap creation*
