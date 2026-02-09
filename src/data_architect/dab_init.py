"""Generate blank YAML spec template with inline comments.

This module provides the `generate_spec_template()` function that creates
a self-documenting Anchor Model specification template using ruamel.yaml
with embedded comments explaining each section.
"""

from __future__ import annotations

from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq


def generate_spec_template() -> str:
    """Generate a blank YAML spec template with inline comments.

    Returns a YAML string with:
    - Top-level comments explaining the spec format
    - Example anchor with commented fields
    - Example attribute nested in anchor
    - Example knot with comments
    - Example tie with roles
    - Nexus section with comments
    - Comments about YAML extensions (staging mappings, keyset identity)

    The generated YAML is valid and parseable by ruamel.yaml.

    Returns:
        YAML string with inline comments and example structures.
    """
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping

    # Build the template structure using CommentedMap
    spec = CommentedMap()

    # Top-level header comment
    header = (
        "Anchor Model Specification\n"
        "Format: Data Architect YAML (superset of anchor.xsd)\n"
        "Docs: https://anchormodeling.com"
    )
    spec.yaml_set_start_comment(header)

    # ANCHOR section
    anchors = CommentedSeq()
    anchor_comment = (
        "Anchors represent entities or events in your domain.\n"
        "Each anchor has:\n"
        "  - mnemonic: Unique 2-3 letter code (e.g., 'AC', 'PR')\n"
        "  - descriptor: Human-readable name (e.g., 'Account', 'Product')\n"
        "  - identity: Surrogate key type ('int', 'guid', 'identity')\n"
        "  - attribute: List of properties (historized or static)"
    )
    anchors.yaml_set_comment_before_after_key(0, before=anchor_comment)

    # Example anchor
    example_anchor = CommentedMap()
    example_anchor["mnemonic"] = "XX"
    example_anchor.yaml_add_eol_comment("Unique 2-3 letter code", "mnemonic")
    example_anchor["descriptor"] = "ExampleEntity"
    example_anchor.yaml_add_eol_comment("Human-readable name", "descriptor")
    example_anchor["identity"] = "int"

    # Example attributes within anchor
    attributes = CommentedSeq()
    attr_comment = (
        "Attributes are properties of the anchor.\n"
        "Each attribute can have either:\n"
        "  - dataRange: SQL data type (e.g., 'varchar(100)', 'decimal(10,2)')\n"
        "  - knotRange: Reference to a knot mnemonic for shared value domains\n"
        "Optional: timeRange for historized attributes (bitemporal tracking)"
    )
    attributes.yaml_set_comment_before_after_key(0, before=attr_comment)

    example_attr = CommentedMap()
    example_attr["mnemonic"] = "NAM"
    example_attr["descriptor"] = "Name"
    example_attr["dataRange"] = "varchar(100)"
    attributes.append(example_attr)

    example_anchor["attribute"] = attributes
    anchors.append(example_anchor)
    spec["anchor"] = anchors

    # KNOT section
    knots = CommentedSeq()
    knot_comment = (
        "Knots represent shared value domains or lookup types.\n"
        "Use knots for:\n"
        "  - Status codes, type codes, categories\n"
        "  - Values that appear across multiple anchors\n"
        "  - Reference data with potential evolution over time\n"
        "Fields: mnemonic, descriptor, identity, dataRange"
    )
    knots.yaml_set_comment_before_after_key(0, before=knot_comment)

    example_knot = CommentedMap()
    example_knot["mnemonic"] = "ST"
    example_knot["descriptor"] = "Status"
    example_knot["identity"] = "int"
    example_knot["dataRange"] = "varchar(50)"
    knots.append(example_knot)
    spec["knot"] = knots

    # TIE section
    ties = CommentedSeq()
    tie_comment = (
        "Ties represent relationships between anchors.\n"
        "Each tie has:\n"
        "  - roles: 2 or more roles connecting anchors (or knots)\n"
        "  - Each role has 'type' (anchor/knot mnemonic) and 'role' (name)\n"
        "  - Optional timeRange for historized relationships (valid/recorded time)\n"
        "Ties model many-to-many relationships with temporal tracking."
    )
    ties.yaml_set_comment_before_after_key(0, before=tie_comment)

    example_tie = CommentedMap()
    example_tie["descriptor"] = "ExampleRelationship"

    roles = CommentedSeq()
    role1 = CommentedMap()
    role1["type"] = "XX"
    role1["role"] = "has"
    roles.append(role1)

    role2 = CommentedMap()
    role2["type"] = "XX"
    role2["role"] = "belongsTo"
    roles.append(role2)

    example_tie["role"] = roles
    ties.append(example_tie)
    spec["tie"] = ties

    # NEXUS section
    nexuses = CommentedSeq()
    nexus_comment = (
        "Nexuses represent n-ary relationships (3+ participants).\n"
        "Unlike ties, nexuses are first-class entities with:\n"
        "  - Their own attributes\n"
        "  - Their own identity\n"
        "  - roles connecting to anchors/knots\n"
        "Use when relationship itself has properties or complex cardinality."
    )
    nexuses.yaml_set_comment_before_after_key(0, before=nexus_comment)

    # Empty nexus list with comment (user can add as needed)
    spec["nexus"] = nexuses

    # Add YAML Extensions section as a comment block at the end
    yaml_ext_comment = (
        "\n"
        "YAML EXTENSIONS (not in anchor.xsd):\n"
        "\n"
        "1. STAGING MAPPINGS\n"
        "   Add 'staging_mappings' field to anchors to define column-level mappings\n"
        "   from staging tables to anchor model entities.\n"
        "\n"
        "2. KEYSET IDENTITY\n"
        "   Natural keys use format: entity@system~tenant|natural_key\n"
        "   Examples:\n"
        "     - customer@erp~acme|cust_id:12345\n"
        "     - product@ecom~global|sku:ABC-123\n"
        "   Components:\n"
        "     entity: Entity type (e.g., customer, product)\n"
        "     system: Source system (e.g., erp, crm, ecom)\n"
        "     tenant: Tenant/org identifier (e.g., acme, contoso)\n"
        "     natural_key: Business key from source (e.g., cust_id:12345)\n"
        "   Escape sequences: @ -> @@, ~ -> ~~, | -> ||, : -> ::\n"
        "   NULL natural key -> entire keyset NULL (not entity@system~tenant|)\n"
        "\n"
        "3. TEMPORAL TRACKING\n"
        "   Attributes and ties support bitemporal tracking via timeRange:\n"
        "     - changed_at: Valid time (when fact was true in reality)\n"
        "     - recorded_at: Transaction time (when fact entered system)\n"
        "   Both are optional; use based on business requirements.\n"
    )

    # Serialize to string
    stream = StringIO()
    yaml.dump(spec, stream)
    result = stream.getvalue()

    # Append extensions comment at the end
    result += "\n# " + yaml_ext_comment.replace("\n", "\n# ")

    return result
