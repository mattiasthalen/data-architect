# Warehouse Architect

## What This Is

A Claude Code skill that orchestrates a team of AI agents — each playing a real data team role — to design data warehouses using Patrik Lager's Analytical Data Storage System (ADSS). Users describe their business, optionally provide source schemas and business questions, and the agents collaborate through Conceptual, Logical, and Physical modeling to produce structured specifications. Deterministic generators then transform those specs into platform-specific SQL, dbt models, and diagrams.

## Core Value

The DAB layer must produce a correct, methodology-compliant Anchor Model through genuine agent debate — system analyst vs. business analyst, architect synthesis, rule validation, user decision — not just template generation.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Agent team: Data Architect, Data Engineer, Analytics Engineer, System/Integration Analyst, Business Analyst, Veteran Reviewer
- [ ] DAB modeling through CLP progression (Conceptual → Logical → Physical)
- [ ] System Analyst and Business Analyst debate pattern for DAB modeling
- [ ] Data Architect synthesizes debate and recommends resolution
- [ ] Anchor Modeling rules applied as objective check
- [ ] User makes final decision on modeling disputes
- [ ] Veteran Reviewer critiques output for anti-patterns and methodology violations
- [ ] YAML/JSON specification format as source of truth
- [ ] Markdown rendering of specs for human consumption
- [ ] Multiple entry points: business description, source schemas (Swagger, ERD, OData), business questions
- [ ] Deterministic generators: specs → platform-specific DDL, dbt models, diagrams
- [ ] Demo scenario validation (e-commerce or similar)

### Out of Scope

- DAS layer implementation — v2 (historized raw data, simpler than DAB)
- DAR layer implementation — v2 (Unified Star Schema, depends on DAB being solid)
- Web UI — this is a Claude Code skill, not a web app
- Real-time streaming support — batch-first for v1
- Specific database platform optimization — platform-agnostic generators first

## Context

**Methodology Stack:**
- **ADSS** (Patrik Lager): Three-layer architecture — DAS (Data According to System), DAB (Data According to Business), DAR (Data According to Requirements). Unidirectional flow DAS → DAB → DAR. Each layer decouples the next from upstream changes.
- **Anchor Modeling** (DAB): Highly normalized technique — anchors, attributes, ties, knots. Each attribute is its own table. Schema evolution is non-destructive (additive only). Designed for agility and resilience to change.
- **Unified Star Schema** (Francesco Puppini, DAR): Single bridge table connecting all dimensions to facts. Eliminates fan traps and chasm traps. Isolated data products per ADSS principles.
- **CLP**: Conceptual → Logical → Physical modeling. The classic progression from business truth to implementation.

**Architecture Pattern:**
- AI agents handle creative/analytical work (understanding the business, debating models, checking methodology)
- Deterministic code generators handle mechanical transformation (specs → SQL/dbt/diagrams)
- Specs (YAML/JSON) are the contract between agents and generators

**Agent Team Roles:**
- **Data Architect**: Overall design authority. Reviews debates, synthesizes recommendations, enforces naming standards and consistency across the model.
- **Data Engineer**: Physical modeling specialist. Performance, indexing, partitioning, orchestration concerns.
- **Analytics Engineer**: DAR layer owner (v2). Understands how the warehouse will be consumed.
- **System/Integration Analyst**: Source system expert. Understands what data exists, how it's structured, what it means technically.
- **Business Analyst**: Business domain expert. Understands what the business needs, how they think about their data, what questions they ask.
- **Veteran Reviewer**: Grumpy, battle-scarred DW engineer who's seen every anti-pattern since Inmon's early days. Critiques everything. If it smells wrong, he'll tell you why — and what disaster he saw it cause in 2003.

**Debate Pattern (DAB):**
1. System Analyst presents source-system perspective on entities and relationships
2. Business Analyst presents business-domain perspective
3. They argue through CLP stages — what's an anchor? what's an attribute? what's a tie?
4. Data Architect synthesizes and recommends
5. Anchor Modeling methodology rules are applied as an objective check
6. User gets the full picture and makes the final call
7. Veteran Reviewer critiques the final model

**Delivery:**
- Claude Code skill (like GSD / get-shit-done)
- Orchestrator prompts, specialized agent prompts, templates
- Target user: data engineers

## Constraints

- **Platform**: Claude Code skill — must work within Claude Code's agent/tool framework
- **Architecture**: Must follow GSD-like patterns — orchestrators, agents, templates, structured artifacts
- **Methodology**: ADSS + Anchor Modeling + USS are non-negotiable. This is the opinion.
- **v1 Focus**: DAB layer with Anchor Modeling and CLP debate. DAS/DAR deferred to v2.
- **Spec Format**: YAML/JSON source of truth, Markdown rendered. Generators consume specs, not prose.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| DAB-first for v1 | Hardest layer, most value, proves the debate pattern | — Pending |
| Specs as contract between agents and generators | Clean separation of AI creativity and deterministic output | — Pending |
| YAML/JSON + rendered Markdown | Machine-readable for generators, human-readable for review | — Pending |
| Anchor Modeling for DAB | Maximum agility — non-destructive schema evolution, resilient to change | — Pending |
| Agent roles mirror real data team | Natural division of concerns, realistic debate dynamics | — Pending |
| Veteran Reviewer as quality gate | Catches anti-patterns, enforces methodology, adds personality | — Pending |

---
*Last updated: 2026-02-07 after initialization*
