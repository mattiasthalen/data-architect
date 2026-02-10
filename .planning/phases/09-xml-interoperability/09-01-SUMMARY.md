---
phase: 09-xml-interoperability
plan: 01
subsystem: xml-interop
tags: [import, pydantic-xml, cli, testing]
dependency_graph:
  requires: []
  provides:
    - xml_interop module with import functions
    - pydantic-xml models for anchor.xsd elements
    - CLI import command (architect dab import)
  affects:
    - cli.py (new import command)
    - dependencies (pydantic-xml, lxml, lxml-stubs)
tech_stack:
  added:
    - pydantic-xml[lxml] (v2.18.0) - XML serialization/deserialization
    - lxml (v6.0.2) - XML parsing with namespace support
    - lxml-stubs (v0.5.1) - Type stubs for mypy
  patterns:
    - BaseXmlModel pattern for XML elements
    - Namespace stripping via tree rebuilding
    - Metadata extraction using lxml for xs:anyAttribute
    - YAML serialization with by_alias=True for field name mapping
key_files:
  created:
    - src/data_architect/xml_interop/__init__.py (8 lines)
    - src/data_architect/xml_interop/models.py (392 lines)
    - src/data_architect/xml_interop/import_xml.py (111 lines)
    - tests/test_xml_import.py (335 lines)
  modified:
    - src/data_architect/cli.py (+59 lines) - dab import command
    - pyproject.toml (+3 dependencies)
decisions:
  - decision: Use pydantic-xml BaseXmlModel for XML parsing instead of manual lxml parsing
    rationale: Type-safe, matches existing Pydantic model pattern, recommended by RESEARCH
    alternatives: [manual lxml parsing, xmltodict library]
  - decision: Separate XML models from YAML Pydantic models with to_yaml_model() conversion
    rationale: Clean separation of concerns, XML models are serialization-only
    alternatives: [single model with dual serialization, runtime model swapping]
  - decision: Strip namespaces by rebuilding tree instead of in-place modification
    rationale: lxml preserves xmlns in nsmap even after tag stripping, rebuild is cleaner
    alternatives: [regex replacement, dual namespace configs, namespace-aware parsing]
  - decision: Use dict comprehension with str/bytes handling for lxml attrib conversion
    rationale: lxml _Attrib type can have str or bytes keys/values, explicit conversion needed for type safety
    alternatives: [type ignore, cast to Any, use dict() directly]
metrics:
  duration: 11 minutes
  tasks_completed: 2
  files_created: 4
  files_modified: 2
  tests_added: 20
  coverage_change: "+4.0% (92.28% -> 96.28%)"
  completed_at: 2026-02-10T10:11:01Z
---

# Phase 09 Plan 01: XML Import Implementation Summary

**One-liner:** Import Anchor Modeler XML files to YAML specs using pydantic-xml with full namespace support and comprehensive testing

## Objective Achieved

Implemented complete XML import functionality allowing users to convert official Anchor Modeler XML files to the YAML superset format. The `architect dab import` command successfully imports example.xml preserving all 7 knots, 4 anchors, 1 nexus, and 7 ties with full metadata and key element support.

## Tasks Completed

### Task 1: XML Interop Module (6 min)

**What was built:**
- Installed pydantic-xml[lxml] (v2.18.0), lxml (v6.0.2), and lxml-stubs (v0.5.1) as dependencies
- Created `xml_interop` module with 12 BaseXmlModel classes mirroring anchor.xsd structure:
  - KeyXML, IdentifierXML, DescriptionXML, MetadataXML, LayoutXML
  - AttributeXML, RoleXML, AnchorXML, KnotXML, TieXML, NexusXML, SchemaXML
- Implemented `import_xml_to_spec()` and `import_xml_string_to_spec()` functions
- Each XML model has `to_yaml_model()` method for lossless conversion to existing Pydantic models
- Namespace handling via tree rebuilding to support both namespaced and un-namespaced XML
- Metadata extraction using lxml element iteration for xs:anyAttribute pattern

**Technical approach:**
```python
# Namespace stripping by rebuilding tree
def strip_ns(elem: etree._Element) -> etree._Element:
    tag = elem.tag.split("}", 1)[1] if "}" in elem.tag else elem.tag
    attribs: dict[str, str] = {
        (k if isinstance(k, str) else k.decode()): (
            v if isinstance(v, str) else v.decode()
        )
        for k, v in elem.attrib.items()
    }
    new_elem = etree.Element(tag, attrib=attribs)
    # Recursively process children...
```

**Verification:**
```bash
$ python -c "from data_architect.xml_interop import import_xml_to_spec; \
  spec = import_xml_to_spec('.references/anchor/example.xml'); \
  print(f'Knots: {len(spec.knots)}, Anchors: {len(spec.anchors)}')"
Knots: 7, Anchors: 4
```

### Task 2: CLI Command and Testing (5 min)

**What was built:**
- Added `architect dab import` command to cli.py with --output and --overwrite flags
- YAML serialization using ruamel.yaml with `by_alias=True` for correct field name mapping
- Comprehensive test suite covering all XML model types:
  - **Unit tests (7 tests):** Parse each XML element type individually
  - **Integration tests (5 tests):** Full import including example.xml, namespaced XML, key/identifier preservation
  - **CLI tests (4 tests):** File operations, error handling, overwrite behavior
  - **Edge cases (4 tests):** Empty schema, invalid XML, missing files, anchors without attributes
- All 266 tests pass (20 new), coverage 96.28% (up from 92.28%)

**CLI usage:**
```bash
$ architect dab import model.xml -o spec.yaml
✓ Imported model.xml -> spec.yaml

$ architect dab import model.xml -o spec.yaml --overwrite
✓ Imported model.xml -> spec.yaml
```

## Deviations from Plan

### Auto-fixed Issues (RULE 1)

**1. [Rule 1 - Type Safety] Added lxml-stubs dev dependency**
- **Found during:** Task 1 type checking
- **Issue:** mypy reported "Library stubs not installed for lxml"
- **Fix:** Added `lxml-stubs>=0.5.1` to dev dependencies
- **Files modified:** pyproject.toml
- **Commit:** cbb1ae8

**2. [Rule 1 - Type Safety] Fixed metadata attribute extraction with str/bytes handling**
- **Found during:** Task 1 type checking
- **Issue:** lxml _Attrib type can return str or bytes keys/values, mypy couldn't infer dict type
- **Fix:** Used explicit dict comprehension with isinstance checks for str/bytes conversion
- **Files modified:** src/data_architect/xml_interop/models.py
- **Commit:** cbb1ae8

**3. [Rule 1 - Namespace Handling] Fixed namespace stripping to rebuild tree**
- **Found during:** Task 2 testing (test_import_namespaced_xml)
- **Issue:** lxml preserves xmlns in nsmap even after tag stripping, causing pydantic-xml parsing errors
- **Fix:** Rebuilt entire tree recursively with new elements (no namespace), removing xmlns declarations
- **Files modified:** src/data_architect/xml_interop/import_xml.py
- **Commit:** cbb1ae8

**4. [Rule 1 - Format] Fixed line length in test file**
- **Found during:** Pre-commit ruff check
- **Issue:** Line 49 in test_xml_import.py exceeded 88 character limit
- **Fix:** Split XML attribute onto multiple lines
- **Files modified:** tests/test_xml_import.py
- **Commit:** cbb1ae8

### Design Changes

**Element Ordering Constraint**
- **Discovered:** pydantic-xml expects elements in definition order (knots, anchors, nexuses, ties)
- **Impact:** Tests required reordering to match anchor.xsd schema order
- **Decision:** Document constraint; anchor.xsd and example.xml already use this order
- **Rationale:** Official XML exports follow schema order, no real-world impact

## Verification Results

### Must-Have Truths ✓

1. **XML Parsing:** ✓ Both namespaced and un-namespaced XML parse into pydantic-xml models
2. **Lossless Conversion:** ✓ XML models convert to YAML Pydantic models preserving all anchor.xsd elements
3. **CLI Functionality:** ✓ `architect dab import model.xml` produces valid YAML spec file
4. **Example Import:** ✓ example.xml imports with all 7 knots, 4 anchors, 1 nexus, 7 ties preserved

### Artifact Validation ✓

| Artifact | Status | Evidence |
|----------|--------|----------|
| src/data_architect/xml_interop/__init__.py | ✓ Created | Exports import_xml_to_spec, import_xml_string_to_spec |
| src/data_architect/xml_interop/models.py | ✓ Created | 12 BaseXmlModel classes, 392 lines, SchemaXML present |
| src/data_architect/xml_interop/import_xml.py | ✓ Created | import_xml_to_spec() and import_xml_string_to_spec() functions |
| tests/test_xml_import.py | ✓ Created | 20 tests, 335 lines, includes example.xml round-trip test |

### Key Links ✓

| Link | Status | Pattern Found |
|------|--------|---------------|
| models.py → spec.py | ✓ Present | `to_yaml_model() -> Spec/Anchor/Attribute/etc` (12 conversions) |
| import_xml.py → models.py | ✓ Present | `SchemaXML.from_xml()` on line 59 |
| cli.py → import_xml.py | ✓ Present | `import_xml_to_spec()` on line 172 |

### Coverage Analysis

**xml_interop module coverage:**
- models.py: 92% (134 statements, 6 missed - unreachable metadata branches)
- import_xml.py: 100% (35 statements, full coverage)
- __init__.py: 100% (2 statements, full coverage)

**Overall project:** 96.28% (up from 92.28%, exceeds 90% requirement)

### End-to-End Verification ✓

```bash
# Import example.xml
$ architect dab import .references/anchor/example.xml -o /tmp/test.yaml
✓ Imported .references/anchor/example.xml -> /tmp/test.yaml

# Verify YAML loads correctly
$ python -c "from data_architect.validation.loader import validate_spec; \
  r = validate_spec(Path('/tmp/test.yaml')); \
  print(f'Parsed: {len(r.spec.knots)} knots, {len(r.spec.anchors)} anchors')"
Parsed: 7 knots, 4 anchors

# Verify all tests pass
$ make check
All checks passed!
266 passed, coverage: 96.28%
```

## Known Issues

**Referential Validation Edge Case**
- The example.xml has 1 validation warning when loaded: "tie[2] must have at least 2 anchor roles, found 1"
- This is because the tie references a nexus (EV) + anchor (AC), and the validator currently expects 2+ anchor roles
- The XML import is correct; the validation rule may need adjustment in a future phase
- Does not block import functionality - YAML loads and parses correctly with all entities preserved

## Self-Check: PASSED

### Created Files Verification ✓

```bash
$ ls -1 src/data_architect/xml_interop/
__init__.py
import_xml.py
models.py

$ wc -l src/data_architect/xml_interop/*.py
    8 __init__.py
  111 import_xml.py
  392 models.py
  511 total

$ ls tests/test_xml_import.py
tests/test_xml_import.py
```

### Commit Verification ✓

```bash
$ git log --oneline -1
cbb1ae8 feat(09-01): add XML import functionality with CLI and comprehensive tests

$ git show cbb1ae8 --stat | grep -E "(xml_interop|test_xml_import)"
 src/data_architect/xml_interop/__init__.py    |   8 +
 src/data_architect/xml_interop/import_xml.py  | 111 +++++
 src/data_architect/xml_interop/models.py      | 392 ++++++++++++++++++
 tests/test_xml_import.py                      | 335 +++++++++++++++
```

### Test Execution ✓

```bash
$ pytest tests/test_xml_import.py -v
======================== 20 passed in 2.41s ========================

$ make check
All checks passed!
lint: ✓ ruff check passed
format: ✓ 46 files formatted correctly
type: ✓ mypy found no issues (31 source files)
test: ✓ 266 passed, coverage 96.28% (exceeds 90%)
```

## Impact

**User-facing changes:**
- New `architect dab import` command enables XML-to-YAML conversion
- Users can migrate from official Anchor Modeler XML exports to YAML format
- Full compatibility with anchor.xsd specification (all element types supported)

**Developer impact:**
- xml_interop module provides reusable import functions for future export functionality (Phase 09-02)
- Pydantic-xml pattern established for XML serialization/deserialization
- Test coverage increased from 92.28% to 96.28%

**Dependencies added:**
- pydantic-xml[lxml] v2.18.0 (runtime)
- lxml v6.0.2 (runtime)
- lxml-stubs v0.5.1 (dev)

## Next Steps

Phase 09 Plan 02 will implement XML export (YAML → XML) using the same pydantic-xml models, completing bidirectional XML interoperability.
