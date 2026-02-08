---
phase: 04-agent-quality-modeling-workflows
plan: 02
subsystem: agent-prompts
tags: [anchor-modeling, debate-protocols, anti-patterns, evidence-based-argumentation]

# Dependency graph
requires:
  - phase: 04-01
    provides: Decision trees, CLP stage protocols, Data Architect debate logic
provides:
  - System Analyst source schema reading protocols (Swagger, OData, ERD)
  - Business Analyst business question evidence templates
  - Opposing position enforcement with burden-of-proof rules
  - Veteran Reviewer expanded anti-pattern checklist (detection criteria, fix templates)
  - Data Engineer deepened physical patterns
  - Analytics Engineer DAB-to-DAR mapping checklist
affects: [04-03, modeling-workflows, agent-quality]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Evidence-based argumentation with burden-of-proof
    - Source schema reading protocols (Swagger, OData, ERD)
    - Anti-pattern detection with measurable criteria
    - DAB-to-DAR mapping checklist

key-files:
  created: []
  modified:
    - src/data_architect/templates.py
    - tests/test_scaffold.py

key-decisions:
  - "System Analyst and Business Analyst both have burden-of-proof requirements to elevate debate quality"
  - "Veteran Reviewer has two-stage review protocol (first after Logical, final after Physical)"
  - "Each anti-pattern has detection criteria, example violation, and step-by-step fix template"

patterns-established:
  - "Evidence-based argumentation: cite specific source evidence or business questions, not opinions"
  - "Anti-pattern detection: measurable criteria (count attributes, trace tie chains, check anchor properties)"
  - "Physical patterns: specific index and partitioning guidance for each Anchor Modeling construct"

# Metrics
duration: 5min 35sec
completed: 2026-02-08
---

# Phase 04 Plan 02: Deepen Subagent Prompts Summary

**Source schema reading protocols, evidence-based argumentation with burden-of-proof, 10-item anti-pattern checklist with detection criteria and fix templates, and DAB-to-DAR mapping for consumption validation**

## Performance

- **Duration:** 5 min 35 sec
- **Started:** 2026-02-08T07:33:32Z
- **Completed:** 2026-02-08T07:39:07Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- System Analyst has complete source schema reading protocols for Swagger/OpenAPI, OData, and ERD with structured extraction steps
- Business Analyst has business question evidence templates with good/bad examples and gathering strategies
- Both analysts have explicit burden-of-proof requirements and challenge criteria for opposing their counterpart
- Veteran Reviewer's 10-item anti-pattern checklist expanded with detection criteria, example violations, and fix templates for each item
- Data Engineer has deepened Anchor Modeling physical patterns (indexes, partitioning, composite indexes)
- Analytics Engineer has DAB-to-DAR mapping checklist linking anchors to dimensions, ties to hierarchies, nexuses to facts

## Task Commits

Each task was committed atomically:

1. **Task 1: Deepen System Analyst and Business Analyst with opposing positions and evidence protocols** - `d145dda` (feat)
2. **Task 2: Expand Veteran Reviewer anti-pattern checklist and deepen Data Engineer + Analytics Engineer** - `bc5bfae` (feat)

## Files Created/Modified

- `src/data_architect/templates.py` - Added source schema reading protocols to System Analyst, business question evidence templates to Business Analyst, expanded all 10 anti-patterns in Veteran Reviewer with detection criteria and fix templates, deepened Data Engineer physical patterns, added DAB-to-DAR mapping to Analytics Engineer
- `tests/test_scaffold.py` - Added 7 new tests verifying deepened content (source_schema_protocol, evidence_templates, burden_of_proof, detection_criteria, fix_templates, physical_patterns, dar_mapping)

## Decisions Made

- **Evidence structure for System Analyst**: Source schema reading protocol structured by file type (Swagger/OData/ERD) with explicit extraction steps for entities, attributes, relationships, constraints
- **Evidence structure for Business Analyst**: Template format "The business needs to answer: [question]. This requires [anchor/attribute/tie] because [reasoning]." with 2-3 good/bad examples
- **Burden-of-proof symmetry**: Both analysts have explicit burden rules - System Analyst must show technical impossibility/data absence, Business Analyst must show business evidence outweighing technical reality
- **Anti-pattern expansion approach**: Each of 10 items gets detection criteria (measurable), example violation (concrete YAML), and fix template (step-by-step remediation)
- **Review protocol timing**: First review after Logical stage (focus structural issues 1-5, 7-8), final review after Physical stage (full checklist with emphasis on premature optimization)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All five subagent prompts (System Analyst, Business Analyst, Veteran Reviewer, Data Engineer, Analytics Engineer) have deep methodology-specific content
- Agents now have the tools, templates, and rules needed for genuine CLP debate
- System Analyst can read source schemas systematically and argue with evidence
- Business Analyst can gather/structure business questions and argue with evidence
- Veteran Reviewer can detect anti-patterns with measurable criteria and provide step-by-step fixes
- Data Engineer and Analytics Engineer have deepened guidance for their respective stages
- Ready for 04-03: test suite verifying agent interactions and debate protocols

## Self-Check: PASSED

All files exist and all commits verified:

```bash
# Template count verification
uv run python -c "from data_architect.templates import TEMPLATES; print(f'Template count: {len(TEMPLATES)}')"
# Output: Template count: 14

# Content verification
uv run python -c "
from data_architect.templates import TEMPLATES
sa = TEMPLATES['.opencode/agents/system-analyst.md']
ba = TEMPLATES['.opencode/agents/business-analyst.md']
vr = TEMPLATES['.opencode/agents/veteran-reviewer.md']
de = TEMPLATES['.opencode/agents/data-engineer.md']
ae = TEMPLATES['.opencode/agents/analytics-engineer.md']
print(f'System Analyst - Source Schema Reading: {\"Source Schema Reading\" in sa}')
print(f'System Analyst - Swagger: {\"Swagger\" in sa}')
print(f'System Analyst - OData: {\"OData\" in sa}')
print(f'System Analyst - ERD: {\"ERD\" in sa}')
print(f'System Analyst - burden: {\"burden\" in sa.lower()}')
print(f'Business Analyst - Business Question Evidence: {\"Business Question Evidence\" in ba}')
print(f'Business Analyst - burden: {\"burden\" in ba.lower()}')
print(f'Veteran Reviewer - Detection criteria count: {vr.lower().count(\"detection criteria\")}')
print(f'Veteran Reviewer - Fix template count: {vr.lower().count(\"fix template\")}')
print(f'Veteran Reviewer - Review Protocol: {\"Review Protocol\" in vr}')
print(f'Data Engineer - Anchor Modeling Physical Patterns: {\"Anchor Modeling Physical Patterns\" in de}')
print(f'Data Engineer - valid_from: {\"valid_from\" in de}')
print(f'Data Engineer - composite index: {\"composite index\" in de}')
print(f'Analytics Engineer - DAB to DAR: {\"DAB to DAR\" in ae}')
print(f'Analytics Engineer - bridge table: {\"bridge table\" in ae}')
"
# All checks: True

# Commit verification
git log --oneline | grep d145dda  # Task 1 commit exists
git log --oneline | grep bc5bfae  # Task 2 commit exists

# Test verification
uv run pytest -v
# 44 passed (40 from 04-01, 7 new from this plan: 3 in Task 1, 4 in Task 2)
```

---
*Phase: 04-agent-quality-modeling-workflows*
*Completed: 2026-02-08*
