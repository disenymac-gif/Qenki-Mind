"""
decision_to_expression.py

Pure transformation operator: Decision (OrderedDict) -> Expression (OrderedDict).
No file I/O, no Markdown string handling. All parsing and serialization is
delegated to entity_markdown.py.

Field rule:
- GENERATED fields (Identity, Ownership, Canonical Basis, Links, Current State,
  Change History, Last Updated) carry destination-owned semantics and are
  always built explicitly by this operator, never copied verbatim from source.
- INHERITED fields (Context, Hypotheses, Predictions, Consequences, Learning)
  carry source content semantics and pass through unchanged.
"""
import datetime
from collections import OrderedDict
import entity_markdown as em

MINIMAL_ENTITY_STRUCTURE = [
    "Identity", "Ownership", "Canonical Basis", "Context", "Hypotheses",
    "Predictions", "Consequences", "Learning", "Links", "Current State",
    "Change History", "Last Updated"
]

INHERITED_FIELDS = ["Context", "Hypotheses", "Predictions", "Consequences", "Learning"]


def decision_to_expression(decision_sections: "OrderedDict[str, str]", decision_path: str) -> "OrderedDict[str, str]":
    em.validate_entity_structure(decision_sections, MINIMAL_ENTITY_STRUCTURE)

    source_identity = em.get_section(decision_sections, "Identity")
    existing_links = em.parse_bullet_list(em.get_section(decision_sections, "Links"))
    today = datetime.date.today().isoformat()

    expression = OrderedDict()
    expression["__title__"] = "Expression: Derived from Decision"

    expression["Identity"] = (
        source_identity.replace("decision-", "expression-", 1)
        if "decision-" in source_identity
        else f"expression-derived-from-{source_identity}"
    )
    expression["Ownership"] = (
        "Owned by the Expression Organ, per QENKI_MIND_ORGANS_v1.md. "
        "This document is a canonical reference entity, not an operational "
        "expression produced by the cognitive runtime."
    )
    expression["Canonical Basis"] = decision_path

    for field in INHERITED_FIELDS:
        expression[field] = em.get_section(decision_sections, field)

    expression_links = list(existing_links) + [decision_path]
    expression["Links"] = em.build_bullet_section(expression_links)
    expression["Current State"] = "Drafted"
    expression["Change History"] = em.build_bullet_section(
        [f"{today}: Initialized by DecisionToExpression operator from {decision_path}."]
    )
    expression["Last Updated"] = today

    return expression


if __name__ == "__main__":
    decision_sections = em.load_entity("DECISIONS/DECISION_REFERENCE.md")
    expression_sections = decision_to_expression(decision_sections, "DECISIONS/DECISION_REFERENCE.md")
    em.validate_entity_structure(expression_sections, MINIMAL_ENTITY_STRUCTURE)
    em.save_entity("EXPRESSIONS/EXPRESSION_REFERENCE.md", expression_sections)
    print("EXPRESSIONS/EXPRESSION_REFERENCE.md generated and validated.")
