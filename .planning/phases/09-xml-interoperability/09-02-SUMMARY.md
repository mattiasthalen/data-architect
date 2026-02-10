---
phase: 09-xml-interoperability
plan: 02
subsystem: xml-interop
tags: [xml, export, xsd-validation, round-trip, cli]
dependency-graph:
  requires: [09-01]
  provides: [xml-export, xsd-validation, round-trip-testing]
  affects: [cli, xml_interop]
tech-stack:
  added: []
  patterns: [xsd-validation, c14n-canonicalization, metadata-serialization]
key-files:
  created:
    - src/data_architect/xml_interop/export_xml.py
    - src/data_architect/xml_interop/validation.py
    - src/data_architect/xml_interop/roundtrip.py
    - tests/test_xml_export.py
    - tests/test_xml_roundtrip.py
  modified:
    - src/data_architect/xml_interop/__init__.py
    - src/data_architect/xml_interop/models.py
    - src/data_architect/cli.py
    - pyproject.toml
decisions:
  - use-exclude-none-for-serialization
  - namespace-stripping-for-round-trip-comparison
  - spec-level-round-trip-verification
  - metadata-post-processing-approach
metrics:
  duration: 16
  completed: 2026-02-10
---

# Phase 09 Plan 02: XML Export and Round-trip Summary

**One-liner:** Complete XML export with XSD validation, extension warnings with --force flag, and comprehensive round-trip testing using C14N canonicalization.

## Completed Tasks

| Task | Name | Commit | Key Changes |
|------|------|--------|-------------|
| 1 | Export function, XSD validation, and extension warnings | 433344b | Added from_yaml_model() to all XML models, export_spec_to_xml(), check_yaml_extensions(), validate_xml_against_xsd(), canonicalize_xml() |
| 2 | CLI export command and comprehensive tests | 433344b | Added `dab export` CLI command, 38 new tests (24 export + 14 round-trip) |

## What Was Built

**XML Export Functionality:**
- `export_spec_to_xml()`: Converts YAML Spec to Anchor Modeler XML with namespace and XSD validation
- `check_yaml_extensions()`: Detects staging_mappings and staging_column that can't be represented in XML
- `from_yaml_model()` class methods on all XML models for Spec → XML conversion
- Default namespace handling: `xmlns="http://anchormodeling.com/schema"` without prefix
- Metadata attribute serialization via post-processing (handles xs:anyAttribute pattern)

**XSD Validation:**
- `validate_xml_against_xsd()`: Validates against anchor.xsd with XSD 1.0 compatibility
- Strips xs:assert elements at load time (lxml doesn't support XSD 1.1 assertions)
- Caches compiled XMLSchema for performance
- Returns detailed error messages with line/column numbers

**Round-trip Utilities:**
- `canonicalize_xml()`: C14N canonicalization with namespace stripping and whitespace normalization
- `assert_roundtrip_equivalent()`: Semantic XML comparison for round-trip verification
- Namespace-aware element comparison (original XML may lack xmlns, export always includes it)

**CLI Integration:**
- `dab export` command with --force and --overwrite flags
- Extension warning system: warns about YAML-only features that will be dropped
- Requires --force to proceed when extensions detected
- XSD validation in export pipeline ensures output validity

## Test Coverage

**New Tests: 38 (24 export + 14 round-trip)**

Export tests (test_xml_export.py):
- Extension detection: 5 tests (no extensions, staging_mappings, staging_column, multiple, nexus)
- Export function: 9 tests (simple spec, namespace, declaration, all entity types, timerange, keys, identifiers, force flag behavior)
- XSD validation: 3 tests (valid XML, invalid XML, exported XML passes)
- CLI integration: 7 tests (creates XML, spec not found, warns extensions, --force, --overwrite)

Round-trip tests (test_xml_roundtrip.py):
- Canonicalization: 4 tests (attribute order, whitespace, passes, fails)
- Full round-trip: 10 tests (simple anchor, knots, ties, nexus, example.xml, spec-level, metadata, keys, identifiers, historized)

**Overall Coverage: 93.41%** (304 tests passing)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Functionality] Metadata attribute export required post-processing**
- **Found during:** Task 1
- **Issue:** pydantic-xml creates metadata elements but doesn't populate xs:anyAttribute attributes. Metadata dict needs manual serialization to XML attributes.
- **Fix:** Implemented `_set_metadata_attrs()` helper that post-processes XML tree to add metadata attributes after serialization. Uses namespace-aware element finding.
- **Files modified:** src/data_architect/xml_interop/models.py, src/data_architect/xml_interop/export_xml.py
- **Commit:** 433344b

**2. [Rule 1 - Bug] Nested metadata processing was incorrectly scoped**
- **Found during:** Task 2 (round-trip testing)
- **Issue:** Attribute/role metadata only processed if parent anchor/nexus/tie had metadata, due to indentation bug in _add_namespace_and_metadata()
- **Fix:** Moved child metadata processing outside parent metadata conditional blocks
- **Files modified:** src/data_architect/xml_interop/export_xml.py
- **Commit:** 433344b

**3. [Rule 2 - Missing Functionality] Namespace stripping for round-trip comparison**
- **Found during:** Task 2
- **Issue:** Original XML lacks namespace, exported XML has xmlns attribute. C14N comparison failed due to namespace differences.
- **Fix:** Implemented `_strip_namespace()` that removes namespace tags and rebuilds element tree without xmlns in nsmap
- **Files modified:** src/data_architect/xml_interop/roundtrip.py
- **Commit:** 433344b

## Key Decisions

**use-exclude-none-for-serialization:** Used `exclude_none=True` instead of `skip_empty=True` for pydantic-xml serialization to preserve empty metadata elements that need attribute population

**namespace-stripping-for-round-trip-comparison:** Strip xmlns from both original and exported XML before C14N comparison, since namespace presence is a formatting difference not a semantic one

**spec-level-round-trip-verification:** For example.xml round-trip test, use Spec-level comparison (import → export → import → compare Specs) instead of XML-level comparison, as non-standard attributes may not survive

**metadata-post-processing-approach:** Serialize XML with pydantic-xml first, then post-process the lxml tree to add metadata attributes, rather than trying to configure pydantic-xml to handle xs:anyAttribute

## Dependencies

**Requires:**
- Phase 09 Plan 01 (XML import functionality, pydantic-xml models with to_yaml_model())

**Provides:**
- XML export functionality for bi-directional YAML ↔ XML conversion
- XSD validation for exported XML
- Round-trip testing utilities
- Extension detection for YAML-only features

**Affects:**
- CLI: Added `dab export` command
- xml_interop module: Complete export/validation/round-trip utilities

## Next Steps

Phase 09 complete. All XML interoperability requirements met:
- INTOP-01: XML import (Plan 01) ✓
- INTOP-02: XML export with extension warnings (Plan 02) ✓
- INTOP-03: XSD validation (Plan 02) ✓
- INTOP-04: Round-trip verification (Plan 02) ✓

Ready for Phase 10 or other roadmap priorities.

## Self-Check: PASSED

Files created:
- FOUND: src/data_architect/xml_interop/export_xml.py
- FOUND: src/data_architect/xml_interop/validation.py
- FOUND: src/data_architect/xml_interop/roundtrip.py
- FOUND: tests/test_xml_export.py
- FOUND: tests/test_xml_roundtrip.py

Commits exist:
- FOUND: 433344b (feat(09-02): add CLI export command and comprehensive tests)

All must-haves verified:
- ✓ YAML spec exports to XML that passes lxml XSD validation
- ✓ Export warns about YAML-only extensions (staging_mappings, staging_column, keyset identity)
- ✓ Export requires --force when extensions present
- ✓ Export without extensions does not require --force
- ✓ XML→YAML→XML round-trips produce semantically equivalent XML for XML-compatible core
- ✓ Round-trip uses C14N canonicalization to ignore formatting differences
