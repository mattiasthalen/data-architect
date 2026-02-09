"""Referential integrity checks for Anchor Model specs."""

from __future__ import annotations

from data_architect.models.spec import Spec
from data_architect.validation.errors import ValidationError


def check_referential_integrity(
    spec: Spec, line_map: dict[str, int]
) -> list[ValidationError]:
    """Check referential integrity of the spec.

    Validates:
    - Attribute knotRange references exist
    - Tie role type references exist
    - Nexus role type references exist
    - Global mnemonic uniqueness (anchors, nexuses, knots)
    - Attribute mnemonic uniqueness per anchor/nexus
    - Tie has >= 2 anchor roles
    - Nexus has >= 1 non-knot role
    - No duplicate tie compositions

    Args:
        spec: Validated Spec model
        line_map: Field path to line number mapping

    Returns:
        List of validation errors
    """
    errors: list[ValidationError] = []

    # Build lookup sets
    anchor_mnemonics = {a.mnemonic for a in spec.anchors}
    knot_mnemonics = {k.mnemonic for k in spec.knots}
    nexus_mnemonics = {n.mnemonic for n in spec.nexuses}
    all_mnemonics = anchor_mnemonics | knot_mnemonics | nexus_mnemonics

    # Check global mnemonic uniqueness (sorted for deterministic ordering)
    mnemonic_to_entities: dict[str, list[tuple[str, str]]] = {}
    for anchor in sorted(spec.anchors, key=lambda a: a.descriptor):
        mnemonic_to_entities.setdefault(anchor.mnemonic, []).append(
            ("Anchor", anchor.descriptor)
        )
    for knot in sorted(spec.knots, key=lambda k: k.descriptor):
        mnemonic_to_entities.setdefault(knot.mnemonic, []).append(
            ("Knot", knot.descriptor)
        )
    for nexus in sorted(spec.nexuses, key=lambda n: n.descriptor):
        mnemonic_to_entities.setdefault(nexus.mnemonic, []).append(
            ("Nexus", nexus.descriptor)
        )

    for mnemonic, entities in mnemonic_to_entities.items():
        if len(entities) > 1:
            entity_names = " and ".join(
                [f"{e_type} '{e_name}'" for e_type, e_name in entities]
            )
            errors.append(
                ValidationError(
                    field_path=f"mnemonic.{mnemonic}",
                    message=f"Duplicate mnemonic '{mnemonic}' found in {entity_names}",
                )
            )

    # Check attribute knotRange references
    for i, anchor in enumerate(spec.anchors):
        # Check attribute mnemonic uniqueness within this anchor
        attr_mnemonics: dict[str, list[str]] = {}
        for j, attr in enumerate(anchor.attributes):
            attr_mnemonics.setdefault(attr.mnemonic, []).append(attr.descriptor)

            # Check knotRange reference
            if attr.knot_range and attr.knot_range not in knot_mnemonics:
                field_path = f"anchor[{i}].attribute[{j}].knotRange"
                line = line_map.get(field_path)
                errors.append(
                    ValidationError(
                        field_path=field_path,
                        message=(
                            f"Attribute '{attr.descriptor}' references "
                            f"nonexistent knot '{attr.knot_range}'"
                        ),
                        line=line,
                    )
                )

        # Check for duplicate attribute mnemonics
        for mnemonic, descriptors in attr_mnemonics.items():
            if len(descriptors) > 1:
                errors.append(
                    ValidationError(
                        field_path=f"anchor[{i}].attributes",
                        message=(
                            f"Duplicate attribute mnemonic '{mnemonic}' in "
                            f"anchor '{anchor.descriptor}': {', '.join(descriptors)}"
                        ),
                    )
                )

    # Check nexus attribute mnemonic uniqueness and knotRange references
    for i, nexus in enumerate(spec.nexuses):
        attr_mnemonics = {}
        for j, attr in enumerate(nexus.attributes):
            attr_mnemonics.setdefault(attr.mnemonic, []).append(attr.descriptor)

            # Check knotRange reference
            if attr.knot_range and attr.knot_range not in knot_mnemonics:
                field_path = f"nexus[{i}].attribute[{j}].knotRange"
                line = line_map.get(field_path)
                errors.append(
                    ValidationError(
                        field_path=field_path,
                        message=(
                            f"Attribute '{attr.descriptor}' references "
                            f"nonexistent knot '{attr.knot_range}'"
                        ),
                        line=line,
                    )
                )

        # Check for duplicate attribute mnemonics
        for mnemonic, descriptors in attr_mnemonics.items():
            if len(descriptors) > 1:
                errors.append(
                    ValidationError(
                        field_path=f"nexus[{i}].attributes",
                        message=(
                            f"Duplicate attribute mnemonic '{mnemonic}' in "
                            f"nexus '{nexus.descriptor}': {', '.join(descriptors)}"
                        ),
                    )
                )

        # Check nexus has at least one non-knot role
        non_knot_roles = [r for r in nexus.roles if r.type_ not in knot_mnemonics]
        if not non_knot_roles:
            errors.append(
                ValidationError(
                    field_path=f"nexus[{i}].roles",
                    message=(
                        f"Nexus '{nexus.descriptor}' must have at least one "
                        "non-knot role"
                    ),
                )
            )

    # Check tie role references and composition
    tie_compositions: list[tuple[str, ...]] = []
    for i, tie in enumerate(spec.ties):
        # Count anchor roles
        anchor_roles = [r for r in tie.roles if r.type_ in anchor_mnemonics]
        if len(anchor_roles) < 2:
            errors.append(
                ValidationError(
                    field_path=f"tie[{i}].roles",
                    message=(
                        f"Tie must have at least 2 anchor roles, "
                        f"found {len(anchor_roles)}"
                    ),
                )
            )

        # Check all role type references
        for j, role in enumerate(tie.roles):
            if role.type_ not in all_mnemonics:
                field_path = f"tie[{i}].role[{j}].type"
                line = line_map.get(field_path)
                errors.append(
                    ValidationError(
                        field_path=field_path,
                        message=(
                            f"Tie role '{role.role}' references "
                            f"nonexistent type '{role.type_}'"
                        ),
                        line=line,
                    )
                )

        # Track composition for duplicate detection
        # (sorted for deterministic comparison)
        composition = tuple(sorted(r.type_ for r in tie.roles))
        if composition in tie_compositions:
            errors.append(
                ValidationError(
                    field_path=f"tie[{i}]",
                    message=f"Duplicate tie composition: {', '.join(composition)}",
                )
            )
        tie_compositions.append(composition)

    # Check nexus role references
    for i, nexus in enumerate(spec.nexuses):
        for j, role in enumerate(nexus.roles):
            # Nexus roles can reference anchors or knots (not other nexuses)
            if role.type_ not in (anchor_mnemonics | knot_mnemonics):
                field_path = f"nexus[{i}].role[{j}].type"
                line = line_map.get(field_path)
                errors.append(
                    ValidationError(
                        field_path=field_path,
                        message=(
                            f"Nexus role '{role.role}' references "
                            f"invalid type '{role.type_}'"
                        ),
                        line=line,
                    )
                )

    return errors
