---
status: complete
phase: 09-xml-interoperability
source: [09-01-SUMMARY.md, 09-02-SUMMARY.md]
started: 2026-02-10T17:00:00Z
updated: 2026-02-10T17:02:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Import XML to YAML
expected: Running `architect dab import model.xml -o spec.yaml` converts an Anchor Modeler XML file to YAML format. The command outputs "✓ Imported model.xml -> spec.yaml" and creates a valid YAML spec file with all entities preserved (knots, anchors, ties, nexuses).
result: skipped

### 2. Import Namespaced XML
expected: Importing XML files with namespace declarations (xmlns="http://anchormodeling.com/schema") works correctly. Both namespaced and un-namespaced XML parse successfully into the same YAML structure.
result: skipped
reason: User skipped UAT session

### 3. Import Preserves All Entity Types
expected: Importing example.xml preserves all 7 knots, 4 anchors, 1 nexus, and 7 ties. Metadata attributes (mnemonic, descriptor, etc.) are preserved from xs:anyAttribute elements.
result: skipped
reason: User skipped UAT session

### 4. Import Preserves Keys and Identifiers
expected: XML key and identifier elements survive import. The YAML spec contains the same key/identifier structure that was in the original XML.
result: skipped
reason: User skipped UAT session

### 5. Import Overwrite Protection
expected: Running import without --overwrite flag when output file exists produces an error. With --overwrite flag, the file is replaced successfully.
result: skipped
reason: User skipped UAT session

### 6. Export YAML to XML
expected: Running `architect dab export spec.yaml -o model.xml` converts a YAML spec to Anchor Modeler XML format. The command outputs "✓ Exported spec.yaml -> model.xml" and creates valid XML with namespace declaration.
result: skipped
reason: User skipped UAT session

### 7. Export Extension Warning
expected: When exporting a YAML spec that contains YAML-only extensions (staging_mappings, staging_column), the command warns about features that can't be represented in XML and requires --force flag to proceed. Without --force, export is blocked. With --force, export continues and drops the extensions.
result: skipped
reason: User skipped UAT session

### 8. Export Passes XSD Validation
expected: Exported XML files pass validation against anchor.xsd. The XML structure matches the official Anchor Modeler schema with proper namespace and element ordering.
result: skipped
reason: User skipped UAT session

### 9. Export Preserves Metadata Attributes
expected: When exporting entities with metadata attributes (mnemonic, descriptor, etc.), the exported XML contains these attributes on the appropriate elements (anchor, attribute, role, etc.). The xs:anyAttribute pattern is correctly serialized.
result: skipped
reason: User skipped UAT session

### 10. XML Round-trip Equivalence
expected: Importing an XML file to YAML and then exporting back to XML produces semantically equivalent XML. The round-trip comparison uses C14N canonicalization to ignore formatting differences (whitespace, attribute order, namespace declarations).
result: skipped
reason: User skipped UAT session

### 11. Example XML Round-trip
expected: The .references/anchor/example.xml file can be imported to YAML and exported back to XML without data loss for XML-compatible features. All 7 knots, 4 anchors, 1 nexus, and 7 ties survive the round-trip.
result: skipped
reason: User skipped UAT session

### 12. Export Overwrite Protection
expected: Running export without --overwrite flag when output file exists produces an error. With --overwrite flag, the file is replaced successfully.
result: skipped
reason: User skipped UAT session

## Summary

total: 12
passed: 0
issues: 0
pending: 0
skipped: 12

## Gaps

[none yet]
