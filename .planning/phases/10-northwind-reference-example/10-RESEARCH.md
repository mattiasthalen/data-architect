# Phase 10: Northwind Reference Example - Research

**Researched:** 2026-02-10
**Domain:** Reference implementation, end-to-end validation, example data
**Confidence:** HIGH

## Summary

Phase 10 implements a complete, production-ready Northwind Anchor Model specification that validates every feature of the v0.3.0 DAB generation pipeline end-to-end. The reference example serves three critical purposes: (1) validates the full feature stack (keyset identity, staging mappings, multi-source, bitemporal columns, XML round-trip), (2) provides a concrete learning resource for users adopting the tool, and (3) serves as a comprehensive regression test suite for future development.

The Northwind database is the industry-standard reference schema—a well-understood domain (specialty food import/export) with rich relationships (11 entities, composite keys, hierarchical structures) and available OData metadata. The schema includes all Anchor Modeling construct types: anchors (Customer, Product, Order, Employee), knots (Category, Region, Shipper, Supplier), ties (OrderDetail as many-to-many, EmployeeTerritory as junction), and temporal attributes (OrderDate, ShippedDate, HireDate).

End-to-end validation in 2026 follows a five-phase framework: (1) requirements gathering (what must be true), (2) artifact creation (the spec itself), (3) generation execution (architect dab generate), (4) syntactic validation (SQL parses, XSD validates), and (5) semantic validation (idempotency, determinism, feature presence). The validation must be automated, repeatable, and serve as documentation.

**Primary recommendation:** Create a pre-filled northwind.yaml spec covering 7 core entities (Orders, Customers, Products, Employees, Suppliers, Categories, Shippers) with keyset identity (`entity@northwind~default|natural_key`), staging mappings from Northwind OData columns, and multi-source examples (e.g., Products from both Northwind and a hypothetical SAP system). Write pytest-based validation tests that verify SQL generation exercises all features, validate round-trip XML export/import, and confirm deterministic/idempotent output. Place spec in examples/northwind/ directory with comprehensive inline YAML comments explaining design decisions.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **pytest** | >=8.0.0 | Test framework for validation assertions | Already in dev dependencies, standard for Python testing |
| **architect CLI** | v0.3.0 | Generate SQL from northwind.yaml | The tool being validated |
| **SQLGlot** | >=28.10.0 | Parse generated SQL to verify structure | Already in dependencies (Phase 7), enables semantic SQL testing |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Hypothesis** | >=6.151.0 | Property-based validation of keyset format | Already in dev dependencies (Phase 8), validate keyset parsing |
| **lxml** | >=5.0.0 | XSD validation of exported XML | Already in dependencies (Phase 9), validate XML round-trip |
| **difflib** (stdlib) | Python 3.13 | Compare generated SQL for determinism | Use for byte-identical output verification (GEN-08) |
| **pathlib** (stdlib) | Python 3.13 | File path manipulation | Use for creating output directories, reading generated files |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Northwind schema | Chinook, AdventureWorks | Northwind is most recognized, has OData endpoint, smaller/simpler than AdventureWorks |
| YAML spec | Generate from OData | Manual spec validates user workflow and serves as documentation—auto-generation would test generator, not end-to-end flow |
| Inline YAML in tests | Separate examples/ directory | Separate directory makes spec discoverable to users, serves dual purpose as test fixture and learning resource |
| Manual validation | Automated test suite | Manual validation doesn't scale, doesn't prevent regressions, doesn't serve as documentation |

**Installation:**
```bash
# All dependencies already in pyproject.toml from prior phases
# No new dependencies required
```

## Architecture Patterns

### Recommended Project Structure

```
data-architect/
├── examples/                        # NEW: Reference implementations
│   └── northwind/                   # NEW: Northwind example
│       ├── northwind.yaml           # NEW: Pre-filled spec with comments
│       ├── README.md                # NEW: Explanation of modeling decisions
│       └── expected_output/         # NEW: Baseline SQL for regression testing
│           ├── CU_Customer.sql      # Anchor DDL + DML
│           ├── CU_NAM.sql          # Attribute DDL + DML
│           ├── OR_Order.sql        # Anchor DDL + DML
│           └── ...                  # All generated entities
├── tests/
│   ├── examples/                    # NEW: End-to-end validation tests
│   │   ├── test_northwind_generation.py  # NEW: Generate and validate SQL
│   │   └── test_northwind_roundtrip.py   # NEW: XML import/export validation
│   └── fixtures/                    # EXISTING: Test fixtures
│       └── valid_spec.yaml          # EXISTING: Minimal valid spec
└── src/data_architect/              # EXISTING: Tool implementation
```

### Pattern 1: Comprehensive Reference Spec with Inline Comments

**What:** A production-ready YAML spec with extensive inline comments explaining every modeling decision

**When to use:** Creating reference examples that serve both as validation and user education

**Example:**
```yaml
# northwind.yaml - Northwind Specialty Foods Anchor Model
#
# This reference implementation demonstrates all v0.3.0 features:
# - Keyset identity with system/tenant encoding
# - Multi-source staging mappings (Products from Northwind + SAP)
# - Temporal attributes (OrderDate, ShippedDate, HireDate)
# - Composite natural keys (OrderDetail: OrderID + ProductID)
# - Knots for static reference data (Category, Region, Shipper)
# - Ties for many-to-many relationships (OrderDetail, EmployeeTerritory)
#
# Business Context:
# Northwind Traders is a specialty food import/export company. The model tracks
# customers, orders, products, suppliers, employees, and shipping logistics.

knot:
  # Categories are static reference data (Beverages, Condiments, etc.)
  # Use knot for low-cardinality, stable dimensions that never change
  - mnemonic: CAT
    descriptor: Category
    identity: int
    dataRange: varchar(15)
    # Staging from Northwind OData Categories entity
    staging_mappings:
      - staging_table: stg_northwind_categories
        system: northwind
        tenant: default
        natural_key:
          - CategoryID
        columns:
          - CategoryID
          - CategoryName
          - Description
        column_mappings:
          CAT_Value: CategoryName  # Knot value comes from CategoryName

anchor:
  # Customer is a core business entity with temporal attributes
  - mnemonic: CU
    descriptor: Customer
    identity: varchar(5)  # Northwind uses ALFKI, ANATR-style IDs
    attribute:
      # Customer name can change over time (company rebrands, acquisitions)
      - mnemonic: NAM
        descriptor: Name
        timeRange: datetime  # Track history of name changes
        dataRange: varchar(40)
      # Contact information changes over time
      - mnemonic: CNT
        descriptor: ContactName
        timeRange: datetime
        dataRange: varchar(30)
      # Static attributes (don't need history)
      - mnemonic: COU
        descriptor: Country
        dataRange: varchar(15)
    # Staging from Northwind OData Customers entity
    staging_mappings:
      - staging_table: stg_northwind_customers
        system: northwind
        tenant: default
        natural_key:
          - CustomerID  # Single-column natural key
        columns:
          - CustomerID
          - CompanyName
          - ContactName
          - Country
        column_mappings:
          CU_NAM: CompanyName
          CU_CNT: ContactName
          CU_COU: Country

  # Product demonstrates multi-source staging (Northwind + SAP)
  - mnemonic: PR
    descriptor: Product
    identity: int
    attribute:
      - mnemonic: NAM
        descriptor: Name
        timeRange: datetime
        dataRange: varchar(40)
      - mnemonic: PRC
        descriptor: UnitPrice
        timeRange: datetime
        dataRange: money
      - mnemonic: STK
        descriptor: UnitsInStock
        timeRange: datetime
        dataRange: smallint
      - mnemonic: CAT
        descriptor: Category
        knotRange: CAT  # Reference to Category knot
    # Multi-source: Products come from both Northwind and SAP
    staging_mappings:
      # Source 1: Northwind (priority 1 - wins conflicts)
      - staging_table: stg_northwind_products
        system: northwind
        tenant: default
        priority: 1
        natural_key:
          - ProductID
        columns:
          - ProductID
          - ProductName
          - UnitPrice
          - UnitsInStock
          - CategoryID
        column_mappings:
          PR_NAM: ProductName
          PR_PRC: UnitPrice
          PR_STK: UnitsInStock
          PR_CAT: CategoryID
      # Source 2: SAP (priority 2 - fallback if Northwind missing)
      - staging_table: stg_sap_materials
        system: sap
        tenant: default
        priority: 2
        natural_key:
          - MaterialID
        columns:
          - MaterialID
          - MaterialName
          - StandardPrice
          - AvailableStock
          - ProductCategory
        column_mappings:
          PR_NAM: MaterialName
          PR_PRC: StandardPrice
          PR_STK: AvailableStock
          PR_CAT: ProductCategory

tie:
  # OrderDetail is a many-to-many relationship with composite natural key
  - role:
      - role: for
        type: OR
        identifier: true  # Part of natural key
      - role: contains
        type: PR
        identifier: true  # Part of natural key
      - role: withQuantity
        type: QTY  # Could be a knot or attribute
        identifier: false
    # Staging from Northwind OData Order_Details entity
    staging_mappings:
      - staging_table: stg_northwind_order_details
        system: northwind
        tenant: default
        natural_key:
          - OrderID
          - ProductID  # Composite key: Order + Product
        columns:
          - OrderID
          - ProductID
          - Quantity
          - UnitPrice
        column_mappings:
          OR_ID: OrderID
          PR_ID: ProductID
          QTY_Value: Quantity
```

### Pattern 2: End-to-End Validation Test Suite

**What:** Automated tests that verify generated SQL exercises all features and matches expected structure

**When to use:** Validating reference implementations and preventing regressions

**Example:**
```python
# tests/examples/test_northwind_generation.py
# Source: E2E testing best practices 2026 + pytest patterns
from pathlib import Path
import subprocess
from sqlglot import parse_one
import pytest

NORTHWIND_SPEC = Path("examples/northwind/northwind.yaml")
OUTPUT_DIR = Path("tests/tmp/northwind_output")

def test_northwind_spec_exists():
    """Reference spec file exists and is valid YAML."""
    assert NORTHWIND_SPEC.exists(), "northwind.yaml not found"
    # Parse YAML to verify syntax
    from data_architect.validation.loader import load_spec
    spec = load_spec(NORTHWIND_SPEC)
    assert spec is not None

def test_northwind_generates_without_errors():
    """architect dab generate succeeds on northwind.yaml."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "architect", "dab", "generate",
            str(NORTHWIND_SPEC),
            "--output", str(OUTPUT_DIR),
            "--dialect", "postgres",
            "--format", "raw",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Generation failed: {result.stderr}"

def test_northwind_generates_all_expected_entities():
    """Generated SQL includes all anchors, knots, ties from spec."""
    expected_files = [
        "CAT_Category.sql",  # Knot
        "CU_Customer.sql",   # Anchor
        "CU_NAM.sql",        # Temporal attribute
        "PR_Product.sql",    # Anchor with multi-source
        "PR_Product_northwind.sql",  # Multi-source: Northwind
        "PR_Product_sap.sql",        # Multi-source: SAP
        "OR_Order.sql",      # Anchor
        "OR_PR_tie.sql",     # Tie (OrderDetail)
    ]
    for filename in expected_files:
        filepath = OUTPUT_DIR / filename
        assert filepath.exists(), f"Missing expected file: {filename}"

def test_northwind_sql_is_valid():
    """Generated SQL parses without syntax errors."""
    for sql_file in OUTPUT_DIR.glob("*.sql"):
        with open(sql_file) as f:
            sql = f.read()
        # SQLGlot parse validates syntax
        try:
            parse_one(sql, dialect="postgres")
        except Exception as e:
            pytest.fail(f"Invalid SQL in {sql_file.name}: {e}")

def test_northwind_ddl_includes_keyset_column():
    """Staging tables include keyset_id computed column."""
    # Check stg_northwind_customers DDL
    staging_ddl = OUTPUT_DIR / "stg_northwind_customers.sql"
    assert staging_ddl.exists()
    with open(staging_ddl) as f:
        sql = f.read()
    assert "keyset_id" in sql.lower()
    assert "generated always as" in sql.lower() or "as (" in sql.lower()  # Computed column

def test_northwind_dml_references_keyset_id():
    """Anchor MERGE statements reference source.keyset_id."""
    anchor_dml = OUTPUT_DIR / "CU_Customer_dml.sql"
    assert anchor_dml.exists()
    with open(anchor_dml) as f:
        sql = f.read()
    # Verify keyset pattern: Customer@northwind~default|
    assert "source.keyset_id" in sql.lower()
    assert "@northwind~default|" in sql

def test_northwind_multi_source_generates_separate_merges():
    """Multi-source anchor (Product) generates one MERGE per source."""
    northwind_merge = OUTPUT_DIR / "PR_Product_northwind_dml.sql"
    sap_merge = OUTPUT_DIR / "PR_Product_sap_dml.sql"
    assert northwind_merge.exists()
    assert sap_merge.exists()

    # Verify system identifiers in keysets
    with open(northwind_merge) as f:
        nw_sql = f.read()
    assert "@northwind~default|" in nw_sql

    with open(sap_merge) as f:
        sap_sql = f.read()
    assert "@sap~default|" in sap_sql

def test_northwind_generation_is_deterministic():
    """Running generate twice produces byte-identical output (GEN-08)."""
    # Generate first time
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["architect", "dab", "generate", str(NORTHWIND_SPEC),
         "--output", str(OUTPUT_DIR), "--dialect", "postgres"],
        check=True,
    )
    first_run = {f.name: f.read_text() for f in OUTPUT_DIR.glob("*.sql")}

    # Clean and generate second time
    for f in OUTPUT_DIR.glob("*.sql"):
        f.unlink()
    subprocess.run(
        ["architect", "dab", "generate", str(NORTHWIND_SPEC),
         "--output", str(OUTPUT_DIR), "--dialect", "postgres"],
        check=True,
    )
    second_run = {f.name: f.read_text() for f in OUTPUT_DIR.glob("*.sql")}

    # Compare
    assert first_run.keys() == second_run.keys()
    for filename in first_run:
        assert first_run[filename] == second_run[filename], \
            f"Non-deterministic output in {filename}"

def test_northwind_ddl_is_idempotent():
    """Generated DDL includes IF NOT EXISTS (GEN-04)."""
    ddl_file = OUTPUT_DIR / "CU_Customer.sql"
    with open(ddl_file) as f:
        sql = f.read()
    # Check for idempotent pattern
    assert "if not exists" in sql.lower() or "create or replace" in sql.lower()

def test_northwind_includes_bitemporal_columns():
    """Temporal attributes include changed_at and recorded_at (GEN-06)."""
    temporal_attr = OUTPUT_DIR / "CU_NAM.sql"
    with open(temporal_attr) as f:
        sql = f.read()
    assert "changed_at" in sql.lower()
    assert "recorded_at" in sql.lower()

def test_northwind_includes_metadata_columns():
    """All tables include metadata columns (GEN-07)."""
    anchor_file = OUTPUT_DIR / "CU_Customer.sql"
    with open(anchor_file) as f:
        sql = f.read()
    assert "metadata_recorded_at" in sql.lower()
    assert "metadata_recorded_by" in sql.lower()
    assert "metadata_id" in sql.lower()
```

### Pattern 3: XML Round-Trip Validation

**What:** Test that northwind.yaml can be exported to XML, imported back to YAML, and generate equivalent SQL

**When to use:** Validating XML interoperability with reference examples

**Example:**
```python
# tests/examples/test_northwind_roundtrip.py
from pathlib import Path
import subprocess
from lxml import etree

NORTHWIND_YAML = Path("examples/northwind/northwind.yaml")
NORTHWIND_XML = Path("tests/tmp/northwind.xml")
NORTHWIND_REIMPORTED = Path("tests/tmp/northwind_reimported.yaml")
ANCHOR_XSD = Path(".references/anchor/anchor.xsd")

def test_northwind_exports_to_valid_xml():
    """Export northwind.yaml to XML that validates against anchor.xsd."""
    # Export (requires --force because of YAML extensions)
    result = subprocess.run(
        ["architect", "dab", "export", str(NORTHWIND_YAML),
         "--output", str(NORTHWIND_XML), "--force"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Export failed: {result.stderr}"
    assert NORTHWIND_XML.exists()

    # Validate against XSD
    schema = etree.XMLSchema(etree.parse(str(ANCHOR_XSD)))
    xml_doc = etree.parse(str(NORTHWIND_XML))
    assert schema.validate(xml_doc), \
        f"Invalid XML: {schema.error_log}"

def test_northwind_xml_imports_without_errors():
    """Import generated XML back to YAML."""
    result = subprocess.run(
        ["architect", "dab", "import", str(NORTHWIND_XML),
         "--output", str(NORTHWIND_REIMPORTED)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert NORTHWIND_REIMPORTED.exists()

def test_northwind_roundtrip_preserves_xml_core():
    """XML → YAML → XML preserves XML-core fields (INTOP-04)."""
    # Import XML
    subprocess.run(
        ["architect", "dab", "import", str(NORTHWIND_XML),
         "--output", str(NORTHWIND_REIMPORTED)],
        check=True,
    )

    # Re-export
    roundtrip_xml = Path("tests/tmp/northwind_roundtrip.xml")
    subprocess.run(
        ["architect", "dab", "export", str(NORTHWIND_REIMPORTED),
         "--output", str(roundtrip_xml), "--force"],
        check=True,
    )

    # Compare XML semantically (ignoring whitespace, attribute order)
    from lxml import etree
    original = etree.parse(str(NORTHWIND_XML))
    roundtrip = etree.parse(str(roundtrip_xml))

    # Canonicalize (C14N) for byte-identical comparison
    c14n_original = etree.tostring(original, method="c14n")
    c14n_roundtrip = etree.tostring(roundtrip, method="c14n")

    assert c14n_original == c14n_roundtrip, \
        "Round-trip XML does not match original (XML-core fields lost)"
```

### Pattern 4: Baseline Regression Testing

**What:** Store expected SQL output as baseline files, compare generated SQL against baseline to detect unintended changes

**When to use:** Preventing regressions when refactoring SQL generation logic

**Example:**
```python
# tests/examples/test_northwind_regression.py
from pathlib import Path
import difflib
import subprocess

NORTHWIND_SPEC = Path("examples/northwind/northwind.yaml")
BASELINE_DIR = Path("examples/northwind/expected_output")
ACTUAL_DIR = Path("tests/tmp/northwind_regression")

def test_northwind_matches_baseline():
    """Generated SQL matches committed baseline (regression test)."""
    # Generate fresh SQL
    ACTUAL_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["architect", "dab", "generate", str(NORTHWIND_SPEC),
         "--output", str(ACTUAL_DIR), "--dialect", "postgres"],
        check=True,
    )

    # Compare each file to baseline
    mismatches = []
    for baseline_file in BASELINE_DIR.glob("*.sql"):
        actual_file = ACTUAL_DIR / baseline_file.name
        assert actual_file.exists(), f"Missing file in output: {baseline_file.name}"

        baseline_sql = baseline_file.read_text()
        actual_sql = actual_file.read_text()

        if baseline_sql != actual_sql:
            # Generate diff for debugging
            diff = difflib.unified_diff(
                baseline_sql.splitlines(keepends=True),
                actual_sql.splitlines(keepends=True),
                fromfile=f"baseline/{baseline_file.name}",
                tofile=f"actual/{baseline_file.name}",
            )
            mismatches.append(f"\n{''.join(diff)}")

    assert not mismatches, \
        f"Generated SQL differs from baseline:\n{''.join(mismatches)}"
```

### Anti-Patterns to Avoid

- **Minimal example that doesn't exercise features:** Don't create a toy spec with 2 anchors and no staging mappings. Reference example must be comprehensive.
- **Auto-generated spec without comments:** Generated YAML lacks educational value. Manual spec with inline comments serves as documentation.
- **Manual validation without automation:** "Run generate and eyeball the SQL" doesn't scale. Automated tests catch regressions.
- **Testing only happy path:** Include edge cases like composite keys, multi-source conflicts, NULL natural keys, empty staging tables.
- **Hardcoded paths in tests:** Use pathlib and relative paths for cross-platform compatibility.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Northwind schema definition | Reverse-engineer from SQL dumps | OData $metadata endpoint | Official OData metadata is machine-readable, canonical source |
| SQL validation | Regex pattern matching | SQLGlot parse_one() | Regex fragile, SQLGlot validates syntax correctly |
| XML comparison | String diff | lxml C14N canonicalization | Whitespace, attribute order, namespace prefixes vary—C14N normalizes |
| Test data generation | Faker/factory libraries | Real Northwind sample data | Reference example should use realistic, recognizable data |
| Baseline updates | Manual file copying | pytest --update-baselines flag pattern | Manual updates error-prone, automated flag prevents mistakes |

**Key insight:** Reference examples are high-leverage—they validate the tool, educate users, and prevent regressions. Invest in comprehensive coverage (all features) and thorough validation (automated tests). A weak example undermines confidence in the tool.

## Common Pitfalls

### Pitfall 1: Incomplete Feature Coverage

**What goes wrong:** Reference example doesn't exercise multi-source, or composite keys, or temporal attributes—leaving features untested in real-world context.

**Why it happens:** Focus on getting "something working" quickly instead of comprehensive validation.

**How to avoid:**
- Checklist all v0.3.0 features: keyset identity ✓, multi-source ✓, composite keys ✓, temporal attributes ✓, knots ✓, ties ✓, staging mappings ✓
- Review requirements NWND-01 and NWND-02 explicitly
- Each feature should appear in at least one entity in the spec

**Warning signs:**
- All anchors have single-column natural keys (missing composite key testing)
- No multi-source staging_mappings (missing conflict resolution testing)
- No temporal attributes with timeRange (missing bitemporality testing)

### Pitfall 2: Stale Baseline Files

**What goes wrong:** Baseline SQL in expected_output/ becomes outdated when generator improves, causing false test failures.

**Why it happens:** Forgetting to update baselines after intentional SQL generation changes.

**How to avoid:**
- Document when to update baselines (pytest flag pattern: `pytest --update-baselines`)
- Baselines are not gold standard—they detect unintended changes, not all changes
- Review baseline diffs before committing—ensure changes are intentional

**Warning signs:**
- Many test failures after refactoring SQL generation
- Baseline SQL contains obvious bugs
- Baselines haven't been updated in months despite active development

### Pitfall 3: Non-Deterministic Test Environment

**What goes wrong:** Tests pass locally but fail in CI due to environment differences (Python version, SQLGlot version, file ordering).

**Why it happens:** Tests depend on implicit environment state (current directory, installed packages).

**How to avoid:**
- Use pathlib with absolute or relative-to-test-file paths
- Pin all dependencies in pyproject.toml (no floating versions)
- Run tests with `pytest --strict-markers --strict-config` to catch issues
- Test in clean virtualenv before committing

**Warning signs:**
- "Works on my machine" syndrome
- CI failures that can't be reproduced locally
- Tests fail after `pip install --upgrade`

### Pitfall 4: Mixing Test Code with Example Code

**What goes wrong:** Test helpers, fixtures, mock data mixed into examples/ directory, confusing users looking for reference implementations.

**Why it happens:** Convenience—putting test utilities near the example being tested.

**How to avoid:**
- `examples/northwind/` contains only user-facing artifacts: northwind.yaml, README.md, expected_output/
- `tests/examples/` contains test code: test_northwind_generation.py, test_northwind_roundtrip.py
- Test fixtures (mock data, test-only specs) stay in `tests/fixtures/`

**Warning signs:**
- Files named `test_*.py` in examples/ directory
- README references pytest or test utilities
- Users asking "what is conftest.py for?" when looking at example

### Pitfall 5: Missing Documentation of Modeling Decisions

**What goes wrong:** northwind.yaml exists but doesn't explain why Customer is an anchor, why Category is a knot, why OrderDetail is a tie.

**Why it happens:** Focus on "making it work" without documenting reasoning.

**How to avoid:**
- Inline YAML comments for every entity: "Customer is an anchor because..."
- README.md in examples/northwind/ explaining Anchor Modeling concepts applied to Northwind
- Document design alternatives considered: "We could make Category an anchor, but knot is better because..."

**Warning signs:**
- Users ask "why is this modeled this way?" frequently
- No comments in YAML spec
- README just lists entities without explanation

## Code Examples

Verified patterns from official sources:

### Comprehensive YAML Spec with Comments

```yaml
# examples/northwind/northwind.yaml (abbreviated)
# Full spec would include all 7 entities from NWND-01 requirement

# Knots: Static reference data that rarely changes
knot:
  - mnemonic: SHP
    descriptor: Shipper
    identity: int
    dataRange: varchar(40)
    # Shipper names are stable (FedEx, UPS, DHL)
    # Knot because: low cardinality (<10), no temporal attributes needed
    staging_mappings:
      - staging_table: stg_northwind_shippers
        system: northwind
        tenant: default
        natural_key:
          - ShipperID
        columns: [ShipperID, CompanyName]
        column_mappings:
          SHP_Value: CompanyName

# Anchors: Core business entities with identity and temporal attributes
anchor:
  - mnemonic: EM
    descriptor: Employee
    identity: int
    # Employees have temporal attributes (title changes, salary changes)
    attribute:
      - mnemonic: NAM
        descriptor: LastName
        timeRange: datetime  # Name changes (marriage, legal change)
        dataRange: varchar(20)
      - mnemonic: TTL
        descriptor: Title
        timeRange: datetime  # Title changes (promotions)
        dataRange: varchar(30)
      - mnemonic: HRD
        descriptor: HireDate
        dataRange: datetime  # Hire date is static (doesn't change)
      - mnemonic: MGR
        descriptor: ReportsTo
        timeRange: datetime  # Manager changes (org restructuring)
        dataRange: int  # References another employee
    staging_mappings:
      - staging_table: stg_northwind_employees
        system: northwind
        tenant: default
        natural_key:
          - EmployeeID
        columns:
          - EmployeeID
          - LastName
          - Title
          - HireDate
          - ReportsTo
        column_mappings:
          EM_NAM: LastName
          EM_TTL: Title
          EM_HRD: HireDate
          EM_MGR: ReportsTo

  - mnemonic: OR
    descriptor: Order
    identity: int
    attribute:
      - mnemonic: DAT
        descriptor: OrderDate
        dataRange: datetime
      - mnemonic: SHP
        descriptor: ShippedDate
        dataRange: datetime
      - mnemonic: FRT
        descriptor: Freight
        dataRange: money
      - mnemonic: SHP_REF
        descriptor: ShipVia
        knotRange: SHP  # Reference to Shipper knot
    staging_mappings:
      - staging_table: stg_northwind_orders
        system: northwind
        tenant: default
        natural_key:
          - OrderID
        columns:
          - OrderID
          - OrderDate
          - ShippedDate
          - Freight
          - ShipVia
        column_mappings:
          OR_DAT: OrderDate
          OR_SHP: ShippedDate
          OR_FRT: Freight
          OR_SHP_REF: ShipVia

# Ties: Many-to-many relationships
tie:
  # OrderDetail: Which products were in which orders (with quantity/price)
  - role:
      - role: for
        type: OR
        identifier: true  # Part of composite key
      - role: contains
        type: PR
        identifier: true  # Part of composite key
    # Note: Quantity and UnitPrice could be modeled as attributes on the tie
    # For simplicity, we'll include them in staging but not model as formal attributes
    staging_mappings:
      - staging_table: stg_northwind_order_details
        system: northwind
        tenant: default
        natural_key:
          - OrderID
          - ProductID  # Composite natural key
        columns:
          - OrderID
          - ProductID
          - Quantity
          - UnitPrice
        column_mappings:
          OR_ID: OrderID
          PR_ID: ProductID
```

### End-to-End Test with Feature Checklist

```python
# tests/examples/test_northwind_feature_coverage.py
"""Validate that northwind.yaml exercises all v0.3.0 features."""
import pytest
from pathlib import Path
from data_architect.validation.loader import load_spec

NORTHWIND_SPEC = Path("examples/northwind/northwind.yaml")

def test_northwind_includes_keyset_identity():
    """All anchors have staging_mappings with system/tenant (KEY-01, KEY-03)."""
    spec = load_spec(NORTHWIND_SPEC)
    for anchor in spec.anchors:
        assert anchor.staging_mappings, \
            f"Anchor {anchor.mnemonic} missing staging_mappings (keyset identity)"
        for mapping in anchor.staging_mappings:
            assert mapping.system, f"{anchor.mnemonic}: missing system identifier"
            assert mapping.tenant, f"{anchor.mnemonic}: missing tenant identifier"
            assert mapping.natural_key, f"{anchor.mnemonic}: missing natural_key"

def test_northwind_includes_multi_source():
    """At least one anchor has multiple staging_mappings (STG-02, STG-05)."""
    spec = load_spec(NORTHWIND_SPEC)
    multi_source = [a for a in spec.anchors if len(a.staging_mappings) > 1]
    assert multi_source, "No anchors demonstrate multi-source staging"

def test_northwind_includes_composite_keys():
    """At least one tie has composite natural_key (KEY-01 edge case)."""
    spec = load_spec(NORTHWIND_SPEC)
    composite_key_ties = []
    for tie in spec.ties:
        for mapping in tie.staging_mappings:
            if len(mapping.natural_key) > 1:
                composite_key_ties.append(tie)
    assert composite_key_ties, "No ties demonstrate composite natural keys"

def test_northwind_includes_temporal_attributes():
    """At least one attribute has timeRange (GEN-06 bitemporality)."""
    spec = load_spec(NORTHWIND_SPEC)
    temporal_attrs = []
    for anchor in spec.anchors:
        temporal_attrs.extend([a for a in anchor.attributes if a.time_range])
    assert temporal_attrs, "No attributes demonstrate temporal (timeRange)"

def test_northwind_includes_knots():
    """Spec includes knots for reference data (SPEC-01)."""
    spec = load_spec(NORTHWIND_SPEC)
    assert spec.knots, "No knots defined (missing reference data modeling)"

def test_northwind_includes_ties():
    """Spec includes ties for relationships (SPEC-01)."""
    spec = load_spec(NORTHWIND_SPEC)
    assert spec.ties, "No ties defined (missing relationship modeling)"

def test_northwind_includes_column_mappings():
    """Staging mappings include column_mappings for lineage (STG-01)."""
    spec = load_spec(NORTHWIND_SPEC)
    for anchor in spec.anchors:
        for mapping in anchor.staging_mappings:
            assert mapping.column_mappings, \
                f"{anchor.mnemonic}: missing column_mappings in staging"

def test_northwind_entities_match_requirement():
    """Spec covers 7 entities from NWND-01."""
    spec = load_spec(NORTHWIND_SPEC)
    anchor_descriptors = {a.descriptor for a in spec.anchors}
    knot_descriptors = {k.descriptor for k in spec.knots}

    required = {"Order", "Customer", "Product", "Employee", "Supplier", "Category", "Shipper"}
    all_descriptors = anchor_descriptors | knot_descriptors

    missing = required - all_descriptors
    assert not missing, f"Missing required entities: {missing}"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual SQL writing and visual inspection | Automated test suite with assertions | 2020+ (pytest era) | Regression prevention, CI integration, documentation as code |
| Toy examples (2-3 entities) | Comprehensive reference implementations | 2015+ (microservices era) | Real-world validation, user education, production-readiness signal |
| String-based SQL comparison | AST-based semantic comparison | 2020+ (SQLGlot) | Resilient to formatting changes, validates structure not whitespace |
| Snapshot testing with manual updates | Baseline regression with automated updates | 2018+ (pytest-snapshot) | Faster feedback, explicit intent (--update-baselines flag) |
| Separate validation scripts | Integrated E2E tests in test suite | 2016+ (testing best practices) | Single test command, CI integration, consistent with unit tests |

**Deprecated/outdated:**
- **Manual validation checklists:** Error-prone, slow, doesn't prevent regressions. Automated tests are now standard.
- **Minimal "hello world" examples:** Don't validate real-world complexity. Comprehensive examples are expected in 2026.
- **XML-only reference formats:** YAML is more readable for documentation. XML export is tested but YAML is primary.

## Open Questions

1. **Northwind sample data population**
   - What we know: OData endpoint provides metadata, not sample data
   - What's unclear: Should examples/ include CSV fixtures with sample rows (ALFKI customer, etc.)?
   - Recommendation: Not required for Phase 10—spec and SQL generation are sufficient. Sample data could be Phase 11.

2. **Multi-tenant example**
   - What we know: Keyset supports tenant identifier (entity@system~tenant|key)
   - What's unclear: Should Northwind example demonstrate multi-tenant (northwind~eu, northwind~us)?
   - Recommendation: Use single tenant "default" for simplicity. Multi-tenant example could be separate reference later.

3. **Bruin format validation**
   - What we know: --format bruin generates SQL with YAML frontmatter (GEN-09)
   - What's unclear: Should tests validate Bruin format in addition to raw SQL?
   - Recommendation: Yes—add test_northwind_generates_bruin_format() to verify frontmatter structure.

4. **Expected output baseline format**
   - What we know: Baseline SQL files enable regression testing
   - What's unclear: Should baselines be PostgreSQL, Snowflake, or both?
   - Recommendation: PostgreSQL only for Phase 10—single dialect keeps scope manageable. Multi-dialect baselines could be added later if needed.

5. **Documentation location**
   - What we know: examples/northwind/README.md should explain modeling decisions
   - What's unclear: Should there be a top-level docs/examples.md or docs/northwind-walkthrough.md for users?
   - Recommendation: README.md in examples/northwind/ is sufficient—keeps documentation with the code.

## Sources

### Primary (HIGH confidence)
- [Northwind OData V4 Metadata](https://services.odata.org/v4/northwind/northwind.svc/$metadata) - Canonical schema definition
- [Anchor Modeling Official Site](https://www.anchormodeling.com/) - Methodology documentation
- [Anchor Modeling Tutorials](https://www.anchormodeling.com/tutorials/) - Design pattern guidance
- [End-to-End Testing Guide 2026](https://www.leapwork.com/blog/end-to-end-testing) - E2E validation best practices
- [Data Quality Testing Guide 2026](https://www.ovaledge.com/blog/data-quality-testing-guide) - Validation methodologies
- [Modern Data Warehouse Testing Strategy Guide 2026](https://blog.qasource.com/how-to-build-an-end-to-end-data-warehouse-testing-strategy) - DWH testing patterns
- Project files: REQUIREMENTS.md (NWND-01, NWND-02), STATE.md (Phase 8/9 summaries), prior RESEARCH.md files (Phases 7, 8, 9)

### Secondary (MEDIUM confidence)
- [Data Validation in ETL - 2026 Guide](https://www.integrate.io/blog/data-validation-etl/) - ETL validation patterns
- [Northwind Database Diagram - Microsoft Support](https://support.microsoft.com/en-us/office/northwind-database-diagram-cd422d47-e4e3-4819-8100-cdae6aaa0857) - ERD reference
- [Data Warehouse Implementation Guide](https://www.scnsoft.com/data/data-warehouse/implementation) - Implementation phases
- [Anchor Modeling Wikipedia](https://en.wikipedia.org/wiki/Anchor_modeling) - General overview

### Tertiary (LOW confidence)
- Community blog posts on Anchor Modeling - Useful examples but verify against official docs
- Stack Overflow discussions on Northwind schema - Dated, verify with OData metadata

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All tools already in project dependencies (pytest, SQLGlot, lxml), patterns established in prior phases
- Architecture: HIGH - Reference example pattern is well-established (examples/ directory standard), test structure follows pytest conventions
- Pitfalls: HIGH - E2E testing pitfalls documented in 2026 sources, regression testing patterns verified in Python testing community

**Research date:** 2026-02-10
**Valid until:** 2026-04-10 (60 days - stable domain, testing patterns mature)

**Key risks mitigated:**
- Incomplete feature coverage (NWND-02) → Checklist all v0.3.0 features against spec entities
- Non-deterministic tests → Use pathlib, pin dependencies, avoid implicit environment state
- Stale baselines → Document update process, review diffs before committing
- Missing documentation → Inline YAML comments + README.md explaining decisions
- Mixing test/example code → Clear separation: examples/ (user-facing) vs tests/examples/ (test code)

**Next steps for planner:**
- Plan 10-01: Create northwind.yaml spec with inline comments covering all 7 entities (Orders, Customers, Products, Employees, Suppliers, Categories, Shippers) with keyset identity, staging mappings, multi-source example, composite keys, temporal attributes, knots, and ties. Write comprehensive test suite validating feature coverage, SQL generation, determinism, idempotency, and XML round-trip. Place spec in examples/northwind/ with README.md explaining modeling decisions.
