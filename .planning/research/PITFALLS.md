# Pitfalls Research

**Domain:** DAB Code Generator (YAML-to-SQL for Anchor Modeling)
**Researched:** 2026-02-09
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Lossy XML-YAML Bidirectional Transformation

**What goes wrong:**
When converting from official Anchor XML format to YAML (for superset features), then back to XML for export, critical metadata is lost or corrupted. Features added in the YAML superset cannot be represented in the XML subset, leading to silent data loss during round-trip conversions. YAML 1.1 vs YAML 1.2 parsers produce different results, causing schema validation to succeed in one environment and fail in another.

**Why it happens:**
YAML supersets create an asymmetric relationship - every XML structure maps to YAML, but not every YAML structure maps back to XML. Developers assume bidirectional fidelity without explicitly modeling which YAML features are "export-safe." YAML version ambiguity (1.1 treats `1e2` as string, 1.2 as number) causes parsers to interpret the same document differently.

**How to avoid:**
- Implement a three-layer schema: XML-compatible core, YAML-safe extensions, export warnings
- Tag YAML-only features with `# @export-incompatible` comments during parsing
- Fail loudly on export if YAML-only features are present (unless `--force-lossy` flag)
- Enforce YAML 1.2 with explicit `%YAML 1.2` headers in all generated files
- Add round-trip validation tests: XML → YAML → XML → compare with original
- Document the "YAML superset compatibility matrix" showing which features export cleanly

**Warning signs:**
- Export succeeds but re-imported model has fewer features
- Test cases validate YAML → SQL but not XML → YAML → XML
- No explicit YAML version headers in spec files
- Schema validation passes but semantic validation fails after export

**Phase to address:**
Phase 1 (YAML Schema Foundation) - establish the three-layer schema and export validation upfront

---

### Pitfall 2: Keyset Identity Delimiter Collision

**What goes wrong:**
The keyset identity format `entity@system~tenant|natural_key` breaks when natural keys contain delimiter characters (`@`, `~`, `|`). A product SKU like `ACME~2024|SPECIAL@OFFER` parses incorrectly, creating phantom entities or silently truncating keys. Escaping is inconsistent (some modules escape `@`, others don't), leading to parse failures in downstream SQL where the same key is interpreted differently.

**Why it happens:**
Delimiter collision is inevitable when user-controlled data (natural keys) is combined with structured formats. Developers assume delimiters won't appear in business data or rely on "just escape it" without defining a canonical escaping scheme. The security implication (SQL injection via crafted keys) is overlooked.

**How to avoid:**
- Use content boundary delimiters: `<<ENTITY>>value<<SYSTEM>>value<<TENANT>>value<<KEY>>value`
- Or use ASCII armor: base64-encode natural keys before embedding in keyset identity
- Define a canonical escape sequence in schema: `@@` for `@`, `~~` for `~`, `||` for `|`
- Implement a `KeysetIdentity` dataclass with `.parse()` and `.format()` methods (single source of truth)
- Add property-based tests with randomly generated keys containing all delimiters
- Reject keys containing delimiter sequences during validation phase (fail fast)
- Document the escape scheme in YAML schema with examples

**Warning signs:**
- Integration tests use sanitized keys without special characters
- Parsing code has multiple `split()` implementations across modules
- No escape/unescape functions or inconsistent implementations
- SQL errors with "unexpected character" in generated WHERE clauses

**Phase to address:**
Phase 1 (YAML Schema Foundation) - define and enforce keyset identity format during schema validation

---

### Pitfall 3: Idempotent SQL Dialect Divergence

**What goes wrong:**
SQL marked as "idempotent" works in PostgreSQL (`CREATE TABLE IF NOT EXISTS`) but fails in SQL Server (no IF NOT EXISTS before SQL Server 2016) or Oracle (different syntax). Generated scripts run successfully in dev (PostgreSQL) but error in production (Oracle), or succeed but create duplicate data due to different UPSERT semantics (INSERT ... ON CONFLICT in PostgreSQL vs MERGE in SQL Server vs INSERT /*+ IGNORE_ROW_ON_DUPKEY_INDEX */ in Oracle).

**Why it happens:**
Developers test with one dialect and assume idempotency patterns transfer. The nuances of behavior and syntax support across dialects are worse than expected - even "standard SQL" features have implementation differences. Template-based generation (Jinja2) makes it easy to generate syntactically correct but semantically wrong SQL for untested dialects.

**How to avoid:**
- Build a dialect abstraction layer with explicit operations: `dialect.create_table_idempotent()`, `dialect.upsert_rows()`
- Implement per-dialect test suites that verify idempotency (run twice, compare results)
- Use tools like sqldef patterns: calculate diff between desired and current schema
- Document dialect support matrix: which operations are supported per dialect with version requirements
- For unsupported dialects, generate transactional scripts with explicit checks instead of failing silently
- Add SQL linting that detects dialect-specific syntax in "dialect-agnostic" templates

**Warning signs:**
- Generated SQL only tested against one database
- `IF EXISTS` or `IF NOT EXISTS` hardcoded in templates without dialect checks
- No integration tests that verify scripts run successfully on target dialects
- Template variables like `{{ create_table }}` without dialect dispatch logic

**Phase to address:**
Phase 2 (SQL Generation Engine) - implement dialect abstraction before generating any SQL

---

### Pitfall 4: Multi-Source Merge Conflict Mishandling

**What goes wrong:**
When the same anchor is fed by multiple staging tables (e.g., Customer from CRM and ERP), the system generates SQL that silently drops conflicting updates, loads data in non-deterministic order (last-write-wins with undefined "last"), or creates duplicate records when natural keys collide across sources. Policy-based conflict resolution ("CRM wins for email, ERP wins for address") is hardcoded in SQL instead of declared in YAML, making it impossible to audit or modify without regenerating code.

**Why it happens:**
Multi-source scenarios are treated as "just another data load" instead of requiring explicit conflict resolution strategy. Developers assume source systems have non-overlapping natural keys or that timestamp-based resolution is sufficient. The complexity of attribute-level conflict rules (different policies per attribute) is underestimated.

**How to avoid:**
- Require explicit conflict resolution strategy in YAML schema per anchor-source pair:
  ```yaml
  anchors:
    - name: Customer
      sources:
        - system: CRM
          priority: 1
          wins_for: [email, phone]
        - system: ERP
          priority: 2
          wins_for: [billing_address, credit_limit]
      default_strategy: reject_conflict  # fail loudly
  ```
- Generate SQL with explicit conflict detection logging (write conflicts to audit table)
- Implement deterministic ordering: sort sources by declared priority, then by system name
- For timestamp-based resolution, require explicit valid-time vs transaction-time semantics
- Add validation: detect when sources have overlapping `wins_for` attributes (configuration error)
- Generate conflict reports during load: "10 Customer records had conflicting emails (CRM won)"

**Warning signs:**
- No conflict resolution strategy in YAML schema
- Generated SQL has `INSERT` without conflict handling
- Integration tests use non-overlapping source data (no actual conflicts tested)
- No audit trail of which source won for each attribute

**Phase to address:**
Phase 3 (Multi-Source Staging) - design conflict resolution schema before implementing merge logic

---

### Pitfall 5: Anchor Modeling Mnemonic Naming Collisions

**What goes wrong:**
Automatically generated mnemonics create collisions: `Customer` → `CU`, `Currency` → `CU`, leading to table name conflicts like `CU_Name` (Customer.Name attribute or Currency.Name?). The 30-character Oracle limit forces aggressive truncation (`VeryLongAnchorName_VeryLongAttributeName` → unreadable hash), making generated SQL impossible to debug. Mnemonic generation is non-deterministic across runs (depends on parse order), causing schema drift.

**Why it happens:**
Mnemonic generation algorithms prioritize brevity over uniqueness. The "first two letters" heuristic works until it doesn't. Developers don't reserve mnemonics for knots/anchors separately. Oracle's 30-character limit (older versions) interacts poorly with verbose Anchor Modeling naming conventions (MA_delim_identity patterns).

**How to avoid:**
- Implement collision detection: track used mnemonics in a registry during parse phase
- Use conflict resolution: `Customer` → `CU`, `Currency` → `CY` (fall back to first+last letter)
- Allow explicit mnemonic override in YAML:
  ```yaml
  anchors:
    - name: Customer
      mnemonic: CUS  # override auto-generation
  ```
- Enforce deterministic generation: sort entities by name before assigning mnemonics
- For Oracle, implement intelligent truncation with collision detection (append `_1`, `_2` if truncated names collide)
- Validate against target database identifier length limits during schema validation
- Generate mnemonic collision report during validation phase

**Warning signs:**
- No collision detection in mnemonic generation code
- Mnemonics generated during SQL generation (too late to detect conflicts)
- No support for explicit mnemonic overrides
- Tests don't verify deterministic mnemonic generation across multiple runs

**Phase to address:**
Phase 1 (YAML Schema Foundation) - validate mnemonic uniqueness during schema parse, before SQL generation

---

### Pitfall 6: Bruin Asset YAML Frontmatter Malformation

**What goes wrong:**
Generated Bruin asset files have invalid YAML frontmatter: missing required fields (`type`, `name`), incorrect dependency format (string instead of array), or frontmatter not separated from SQL body. Bruin CLI rejects files or silently ignores assets. Materialization strategy (`table`, `view`, `incremental`) doesn't match the generated SQL semantics (SQL has `CREATE OR REPLACE VIEW` but frontmatter says `type: table`).

**Why it happens:**
Bruin asset format is treated as "YAML with SQL appended" instead of a structured schema. Developers hand-craft templates without validating against Bruin's schema. Dependency format (`depends: [AssetA, AssetB]` vs `dependencies: [{name: AssetA}]`) is ambiguous in documentation. The frontmatter/SQL separation requirement (requires `---` delimiter or specific line count) is implicit.

**How to avoid:**
- Parse Bruin's official schema (if available) or reverse-engineer from examples
- Implement Bruin asset dataclass with required fields: `name`, `type`, `owner`, `dependencies`, `materialization`
- Validate generated assets with Bruin CLI in CI: `bruin validate .`
- Add schema validation: check that materialization strategy matches SQL DDL verbs
  - `CREATE TABLE` → `materialization: table`
  - `CREATE VIEW` → `materialization: view`
  - `CREATE OR REPLACE` + time-based filter → `materialization: incremental`
- Generate frontmatter with explicit YAML library, not string concatenation
- Document Bruin asset template with all required/optional fields and examples

**Warning signs:**
- Frontmatter generated via f-strings: `f"name: {name}\ntype: {type}\n---\n{sql}"`
- No Bruin CLI validation in tests
- Materialization field hardcoded to single value for all assets
- Dependency format varies across generated files

**Phase to address:**
Phase 2 (SQL Generation Engine) - implement Bruin asset schema before generating first asset file

---

### Pitfall 7: Pure-Functional Python State Leakage in Generator

**What goes wrong:**
Code generation functions mutate global state (shared mnemonic registry, SQL dialect settings), causing tests to fail non-deterministically depending on execution order. Caching "optimizations" (cache generated SQL for reuse) break when YAML schema changes mid-session. Generator functions have side effects (writing to filesystem during "validation"), violating pure-functional constraints and making it impossible to test generation logic without I/O.

**Why it happens:**
Stateful patterns are natural for code generation (build up context, emit code incrementally). Developers add mutable registries for performance without considering thread-safety or test isolation. TDD discipline erodes when stateful helpers are added outside test coverage.

**How to avoid:**
- All generator functions return new immutable objects: `generate_sql(schema: Schema) -> GeneratedSQL`
- Use immutable data structures (dataclasses with `frozen=True`, or pyrsistent library)
- Thread context through function parameters instead of globals:
  ```python
  def generate_anchor_sql(anchor: Anchor, context: GenerationContext) -> tuple[str, GenerationContext]:
      # Returns updated context without mutation
  ```
- Separate pure logic (generate AST) from I/O effects (write files):
  ```python
  def generate_code(schema: Schema) -> dict[str, str]:  # pure
      return {"file1.sql": "...", "file2.sql": "..."}

  def write_files(files: dict[str, str], output_dir: Path):  # impure
      for name, content in files.items():
          (output_dir / name).write_text(content)
  ```
- Add property-based tests that verify pure functions: same input always produces same output
- Use pytest fixtures to reset any shared state between tests (fail tests if state detected)

**Warning signs:**
- Generator functions modify parameters or global variables
- Tests have `setUp` methods that reset global state
- Generator functions call `Path.write_text()` directly instead of returning content
- Tests fail when run in different order or parallelized

**Phase to address:**
Phase 2 (SQL Generation Engine) - establish pure-functional architecture before implementing complex generators

---

### Pitfall 8: YAML Schema Validation Escape Hatches

**What goes wrong:**
YAML schema validation is implemented but has "temporary" bypass flags (`--skip-validation`) that become permanent. Invalid YAML passes validation because any construct not explicitly forbidden is allowed (YAML's flexibility). Users embed arbitrary Python expressions in YAML comments (`# {{ __import__('os').system('rm -rf /') }}`), which are later eval'd during template rendering, creating remote code execution vulnerabilities.

**Why it happens:**
Schema validation is added late, after YAML files exist in the wild, forcing backward compatibility. The "be liberal in what you accept" philosophy leads to under-specification. Jinja2 template injection risks are underestimated when YAML is treated as "just configuration data."

**How to avoid:**
- Define explicit schema with closed-world assumption: only explicitly allowed constructs are valid
- Use schema validation library (Yamale, Pydantic) with strict mode
- Reject unknown fields, not just warn: `additionalProperties: false` in JSON Schema terms
- Never eval/exec YAML content or embed it in Jinja2 templates without sanitization
- Use Jinja2 sandboxed environment if YAML content is rendered in templates
- Add schema versioning: reject YAML without explicit schema version header
- Remove validation bypass flags or make them require explicit confirmation (not just CLI flag)
- Implement schema evolution policy: how to deprecate fields, migrate old YAML

**Warning signs:**
- Schema validation has many warnings but no errors
- `--skip-validation` flag exists in production code
- YAML parsing code uses `yaml.unsafe_load()` instead of `yaml.safe_load()`
- Comments in YAML are preserved and processed instead of stripped

**Phase to address:**
Phase 1 (YAML Schema Foundation) - enforce strict validation from day one, no bypass flags

---

### Pitfall 9: Temporal Data INSERT Idempotency Failure

**What goes wrong:**
Generated INSERT statements for temporal/bitemporal attributes are not truly idempotent. Re-running the script creates duplicate historical records with identical valid-time ranges but different transaction-times, or overwrites history when correcting errors (losing audit trail). Temporal corrections (updating "what we believed in the past") require complex SQL that is buggy - closed intervals overlap, gaps appear in history.

**Why it happens:**
Idempotency for temporal data requires understanding four datetime dimensions: valid-from, valid-to, transaction-from, transaction-to. Developers implement "simple" idempotency (INSERT ... ON CONFLICT DO NOTHING) which ignores temporal semantics. The distinction between correcting current state vs correcting historical state is collapsed into one code path.

**How to avoid:**
- For uni-temporal (valid-time only): use UPSERT with valid-time key matching:
  ```sql
  INSERT ... ON CONFLICT (anchor_id, valid_from, valid_to) DO UPDATE SET value = EXCLUDED.value
  ```
- For bitemporal: never UPDATE, only INSERT with new transaction-time (preserves correction audit trail)
- Implement temporal assertion helpers in SQL generation:
  - Assert no overlapping valid-time ranges for same anchor+attribute
  - Assert no gaps in required-continuous attributes
- Generate separate SQL for "load new data" vs "correct historical data" operations
- Add temporal integrity tests: verify idempotent script maintains temporal constraints
- Document temporal semantics in generated SQL comments:
  ```sql
  -- Idempotent: safe to rerun, will update only if valid-time range matches exactly
  ```

**Warning signs:**
- INSERT statements for temporal attributes lack ON CONFLICT clauses
- No tests verify temporal constraint preservation after multiple runs
- Generated SQL treats all attributes uniformly (no temporal vs non-temporal distinction)
- Temporal corrections require manual SQL instead of regenerating from YAML

**Phase to address:**
Phase 2 (SQL Generation Engine) - implement temporal-aware idempotency patterns for attribute INSERT generation

---

### Pitfall 10: Integration Test Data Unrealism

**What goes wrong:**
Integration tests use sanitized "happy path" data: no special characters in keys, no source conflicts, no long names hitting identifier limits, no YAML edge cases (multi-line strings, unicode). Tests pass but production fails immediately on real data: customer names with apostrophes break SQL, product SKUs with delimiters crash parser, long German compound nouns exceed Oracle limits.

**Why it happens:**
Test data is manually crafted to be "clean" and demonstrate core functionality. Property-based testing (generating random, adversarial inputs) is perceived as overkill. Integration tests focus on "does it work" not "what breaks it."

**How to avoid:**
- Adopt property-based testing with Hypothesis library:
  ```python
  @given(st.text(alphabet=st.characters()), st.text(alphabet=st.characters()))
  def test_keyset_identity_roundtrip(entity, system):
      keyset = KeysetIdentity.format(entity, system, "tenant", "key")
      parsed = KeysetIdentity.parse(keyset)
      assert parsed.entity == entity
  ```
- Create adversarial test dataset:
  - Names: `O'Brien`, `Robert'); DROP TABLE anchors;--`, `مُحَمَّد`
  - Keys: `KEY@WITH~DELIMS|HERE`, `  spaces  `, empty string
  - Long names: 100+ character identifiers
  - YAML edge cases: `!!python/object` tags, `---` in values, tab-based indentation
- Run integration tests against all supported database dialects in CI
- Add fuzzing: generate random YAML and verify parser doesn't crash
- Test failure modes: intentionally malformed YAML, conflicting multi-source data, invalid mnemonics

**Warning signs:**
- All test YAML files have ASCII-only, alphanumeric identifiers
- No property-based tests or fuzzing
- Integration tests only run against SQLite or PostgreSQL
- Test data doesn't include known problematic patterns (SQL injection strings, unicode, etc.)

**Phase to address:**
Phase 1 (YAML Schema Foundation) - establish property-based testing for parser/validator before building on top

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single-dialect SQL generation (PostgreSQL only) | Fast MVP, simpler templates | Vendor lock-in, costly migration for customers | Only if target dialect is contractually guaranteed |
| String-based SQL generation (f-strings) | Simple to implement, readable | SQL injection risks, no syntax validation | Never for user-controlled data |
| YAML validation warnings (not errors) | Backward compatibility with existing files | Invalid YAML passes through, runtime failures | Migration period with sunset date |
| Hardcoded conflict resolution (CRM always wins) | Avoids complex configuration schema | Inflexible, requires code changes per customer | Single-customer deployments only |
| Mutable global mnemonic registry | Simpler code, "stateful makes sense here" | Thread-unsafe, test isolation issues, breaks TDD | Never in pure-functional codebase |
| Skipping temporal idempotency tests | Faster test suite | Silent data corruption in production | Never (temporal bugs are expensive) |
| Template-based Bruin asset generation (no validation) | Quick initial implementation | Bruin CLI rejects files, debugging nightmare | Prototype phase only, must add validation before MVP |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Official Anchor XML Parser | Assume valid XML equals valid Anchor model | Validate Anchor Modeling semantics separately (e.g., anchors must have identities, attributes reference existing anchors) |
| Bruin CLI | Generate assets but never run `bruin validate` | Add Bruin validation to CI pipeline |
| Database Dialects | Test SQL with Python sqlite3 module | Test against actual target database (PostgreSQL, SQL Server, Oracle) with same version as production |
| YAML Parser | Use `yaml.load()` (unsafe) for convenience | Always use `yaml.safe_load()` to prevent code execution |
| Jinja2 Templates | Render user-controlled YAML data directly | Use sandboxed environment or escape all user input |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Load all anchors into memory before generation | Simple code, works fine | Stream YAML parsing, generate SQL per-anchor | >1000 anchors or >100MB YAML file |
| Generate single monolithic SQL file | Easy to review, one script to run | Split by anchor/entity, parallel generation | >10K lines SQL, slow execution |
| Revalidate entire schema on every change | Thorough validation | Incremental validation (only changed anchors) | >100 entities, slow feedback loop |
| String concatenation for SQL generation | Simple implementation | Use SQL builder library or AST | >1000 lines generated SQL, unreadable output |
| Synchronous database validation (test idempotency) | Straightforward test code | Parallel test execution per dialect | >10 test cases per dialect |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Eval YAML comments as Jinja2 templates | Remote code execution | Strip comments, never eval user content |
| No SQL sanitization in keyset identities | SQL injection via crafted natural keys | Use parameterized queries, validate key format |
| Expose YAML superset features in exported XML | Data exfiltration via hidden YAML fields | Audit export, warn on lossy conversion |
| Trust mnemonic uniqueness without validation | Table name collision, data corruption | Enforce unique mnemonics in schema validation |
| Use yaml.unsafe_load for "flexibility" | Arbitrary Python object instantiation | Always use yaml.safe_load |
| Store database credentials in YAML | Credential leakage in version control | Use environment variables, separate config |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent lossy XML export | User loses YAML-only features without warning | Explicit warning with list of dropped features |
| Cryptic mnemonic collision errors | "CU already exists" - which entity? | "Mnemonic 'CU' collision: Customer vs Currency" |
| No conflict resolution visibility | User doesn't know which source won | Generate conflict report: "CRM won 45/100 conflicts" |
| Regenerate all SQL on schema change | Slow feedback, unnecessary churn | Incremental generation (only changed entities) |
| Generic "invalid YAML" errors | User can't locate error | Line numbers, YAML path, expected vs actual |
| No preview mode for SQL generation | User must commit to see output | `--dry-run` flag showing generated SQL without writing |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **YAML Parser:** Often missing explicit version header enforcement - verify parser rejects YAML 1.1 documents
- [ ] **Keyset Identity:** Often missing escape sequence handling - verify round-trip with delimiter characters
- [ ] **SQL Generation:** Often missing dialect-specific idempotency - verify scripts work on all target databases
- [ ] **Multi-Source Merge:** Often missing conflict logging - verify audit trail of resolution decisions
- [ ] **Mnemonic Generation:** Often missing determinism - verify same YAML produces same mnemonics across runs
- [ ] **Bruin Assets:** Often missing frontmatter validation - verify Bruin CLI accepts generated files
- [ ] **Temporal SQL:** Often missing bitemporal correction logic - verify UPDATE history preserves audit trail
- [ ] **XML Export:** Often missing lossy conversion warnings - verify user is informed of dropped features
- [ ] **Pure Functions:** Often missing immutability enforcement - verify no global state mutation
- [ ] **Integration Tests:** Often missing adversarial data - verify tests include special characters, long names, unicode

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Lossy XML Export | MEDIUM | Warn user, offer YAML-to-YAML migration tool, document unsupported features |
| Keyset Identity Collision | HIGH | Implement escape sequences retroactively, migrate existing data with new encoding |
| Idempotent SQL Failure | HIGH | Implement per-dialect abstractions, regenerate all SQL, test against all databases |
| Multi-Source Conflicts | MEDIUM | Add conflict resolution schema, regenerate with explicit strategy, audit existing data |
| Mnemonic Collisions | LOW | Allow manual override, regenerate with deterministic algorithm, update schema |
| Bruin Asset Malformation | LOW | Implement schema validation, regenerate assets, test with Bruin CLI |
| State Leakage | MEDIUM | Refactor to pure functions, add immutability checks, expand test coverage |
| Schema Validation Bypass | HIGH | Remove bypass flags, enforce strict validation, migrate invalid YAML |
| Temporal Idempotency Failure | HIGH | Rewrite temporal SQL generation, add constraint validation, audit historical data |
| Unrealistic Test Data | MEDIUM | Add property-based tests, create adversarial dataset, expand dialect coverage |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Lossy XML-YAML Transformation | Phase 1: YAML Schema Foundation | Round-trip tests: XML → YAML → XML equality |
| Keyset Identity Delimiter Collision | Phase 1: YAML Schema Foundation | Property-based tests with random delimiter-heavy strings |
| Idempotent SQL Dialect Divergence | Phase 2: SQL Generation Engine | Multi-dialect integration tests (PostgreSQL, SQL Server, Oracle) |
| Multi-Source Merge Conflict Mishandling | Phase 3: Multi-Source Staging | Integration tests with intentional conflicts, verify audit logs |
| Anchor Modeling Mnemonic Naming Collisions | Phase 1: YAML Schema Foundation | Determinism tests (same YAML → same mnemonics), collision detection |
| Bruin Asset YAML Frontmatter Malformation | Phase 2: SQL Generation Engine | `bruin validate` in CI pipeline |
| Pure-Functional Python State Leakage | Phase 2: SQL Generation Engine | Immutability tests, parallelized test execution |
| YAML Schema Validation Escape Hatches | Phase 1: YAML Schema Foundation | Strict schema enforcement, no bypass flags in codebase |
| Temporal Data INSERT Idempotency Failure | Phase 2: SQL Generation Engine | Idempotency tests (run script twice, verify single result set) |
| Integration Test Data Unrealism | Phase 1: YAML Schema Foundation | Hypothesis property-based tests, adversarial dataset |

## Sources

### Anchor Modeling
- [Anchor Modeling Support](https://www.anchormodeling.com/support/) - MEDIUM confidence
- [Anchor Modeling - Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) - MEDIUM confidence
- [Anchor Modeling Naming Convention PDF](https://www.anchormodeling.com/wp-content/uploads/2010/09/AM-Naming.pdf) - HIGH confidence (attempted but 403 error)

### YAML and Schema Validation
- [The YAML Document from Hell](https://ruudvanasseldonk.com/2023/01/11/the-yaml-document-from-hell) - HIGH confidence
- [JSON is not a YAML subset](https://john-millikin.com/json-is-not-a-yaml-subset) - HIGH confidence
- [Yamale - Schema validator for YAML](https://github.com/23andMe/Yamale) - MEDIUM confidence

### SQL Generation and Dialects
- [Idempotent SQL DDL](https://medium.com/full-stack-architecture/idempotent-sql-ddl-ca354a1eee62) - HIGH confidence
- [sqldef - Idempotent schema management](https://github.com/sqldef/sqldef) - MEDIUM confidence
- [AI SQL Generation: Dialect-specific syntax errors](https://gavinray97.github.io/blog/overcoming-dialect-sql-generation-limits) - MEDIUM confidence

### Multi-Source Data Integration
- [Data level conflicts resolution for multi-sources heterogeneous databases](https://www.researchgate.net/publication/313545369_Data_level_conflicts_resolution_for_multi-sources_heterogeneous_databases) - MEDIUM confidence
- [Conflict resolution strategies in Data Synchronization](https://mobterest.medium.com/conflict-resolution-strategies-in-data-synchronization-2a10be5b82bc) - MEDIUM confidence

### Bruin Data Pipeline
- [Bruin Asset Definition Schema](https://bruin-data.github.io/bruin/assets/definition-schema.html) - HIGH confidence
- [Bruin CLI GitHub](https://github.com/bruin-data/bruin) - HIGH confidence

### Delimiter Collision and Parsing
- [Delimiter Collision - Wikipedia](https://en.wikipedia.org/wiki/Delimiter_collision) - HIGH confidence
- [Data Parsing: Delimiters, Encodings, and Edge Cases](https://rvrsh3ll.net/data-parsing-in-the-real-world-delimiters-encodings-and-edge-cases) - MEDIUM confidence

### Idempotency in Data Engineering
- [Core Data Engineering: Idempotency](https://medium.com/@danthelion/core-data-engineering-idempotency-3f5b8d782cd) - MEDIUM confidence
- [How to make data pipelines idempotent](https://www.startdataengineering.com/post/why-how-idempotent-data-pipeline/) - MEDIUM confidence
- [Idempotency in Data Engineering](https://blog.dataengineerthings.org/idempotency-in-data-engineering-why-it-matters-and-how-to-embrace-it-ec3fb0aec118) - MEDIUM confidence

### Temporal and Bitemporal Data
- [Bitemporal History - Martin Fowler](https://martinfowler.com/articles/bitemporal-history.html) - HIGH confidence
- [Bitemporal Data Modeling: How to Learn from History](https://www.dataversity.net/bitemporal-data-modeling-learn-history/) - MEDIUM confidence
- [Bitemporal Modeling - Wikipedia](https://en.wikipedia.org/wiki/Bitemporal_modeling) - MEDIUM confidence

### Surrogate Keys and Natural Keys
- [A complete guide to surrogate keys](https://www.getdbt.com/blog/guide-to-surrogate-key) - MEDIUM confidence
- [Surrogate Key vs Natural Key Differences](https://www.mssqltips.com/sqlservertip/5431/surrogate-key-vs-natural-key-differences-and-when-to-use-in-sql-server/) - MEDIUM confidence

### Data Vault Naming Conventions
- [Data Vault 2.0 Suggested Object Naming Conventions](https://datavaultalliance.com/news/dv/dv-standards/data-vault-2-0-suggested-object-naming-conventions/) - MEDIUM confidence
- [Data Vault Naming Standards](https://patrickcuba.medium.com/data-vault-naming-standards-76c93413d3c7) - MEDIUM confidence

### Python Functional Programming
- [Pyrsistent - Persistent/Immutable data structures](https://github.com/tobgu/pyrsistent) - HIGH confidence
- [Functional Programming in Python: Immutable data structures](https://opensource.com/article/18/10/functional-programming-python-immutable-data-structures) - MEDIUM confidence
- [Core Functional Programming Principles for Python](https://arjancodes.com/blog/functional-programming-principles-in-python/) - MEDIUM confidence

### Jinja2 Security
- [Python vulnerabilities: Code execution in Jinja templates](https://podalirius.net/en/articles/python-vulnerabilities-code-execution-in-jinja-templates/) - HIGH confidence
- [SSTI Vulnerability in Jinja2](https://github.com/thautwarm/vscode-diana/issues/1) - MEDIUM confidence

### Test-Driven Development
- [Test-Driven Development for Code Generation](https://arxiv.org/abs/2402.13521) - MEDIUM confidence
- [TDD and Functional Programming in TypeScript](https://adam.fanello.net/tdd-and-fp-study) - MEDIUM confidence

---
*Pitfalls research for: DAB Code Generator (YAML-to-SQL for Anchor Modeling)*
*Researched: 2026-02-09*
*Overall confidence: MEDIUM - Most findings verified through multiple sources, but Anchor Modeling specific issues have fewer authoritative sources*
