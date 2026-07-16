"""BeliefToFact operator.

Authority: Learning & Reflection Organ (ADR-001, ADR-008).
Input:     a Belief entity path (BELIEFS/*.md).
Output:    a Fact entity path (FACTS/*.md), or raises if promotion
           criteria are not met.

Contract:
- Reads the confidence threshold from
  REASONING_PARAMETERS/belief_fact_promotion.md.
- Falls back to PROMOTION_THRESHOLD_DEFAULT if the parameter file is
  absent or not yet calibrated.
- Raises BelowPromotionThresholdError if Belief.Confidence < threshold.
- Raises AlreadyPromotedError if the Belief is already in
  Epistemic State 'Promoted'.
- Raises ConflictedBeliefError if the Belief is in state 'Conflicted'
  (ADR-008 Invariant 8: conflicted Beliefs may not be promoted until
  conflict is resolved).
- On success:
    1. Writes a Fact entity to FACTS/.
    2. Updates the source Belief entity's Epistemic State to 'Promoted'
       and appends a Change History entry.
    3. Emits a FactPromoted event.
- All three state changes (Fact creation, Belief update, event) are
  idempotent: re-running on an already-promoted Belief raises
  AlreadyPromotedError rather than creating a duplicate Fact.
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from OPERATORS.engine import CognitiveOperator
from OPERATORS._belief_utils import parse_float, load_promotion_threshold
import entity_markdown as em


# ---------------------------------------------------------------------------
# Convenience alias — keeps operator-level code readable
# ---------------------------------------------------------------------------

PROMOTION_THRESHOLD_DEFAULT: float = 0.80


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class BelowPromotionThresholdError(ValueError):
    """Confidence is below the promotion threshold."""


class AlreadyPromotedError(ValueError):
    """Belief is already in Epistemic State 'Promoted'."""


class ConflictedBeliefError(ValueError):
    """Conflicted Beliefs may not be promoted (ADR-008 Invariant 8)."""


# ---------------------------------------------------------------------------
# Canonical section order for Fact entities
# ---------------------------------------------------------------------------

_FACT_SECTION_ORDER = [
    "Identity",
    "Ownership",
    "Canonical Basis",
    "Claim",
    "Confidence",
    "Epistemic State",
    "Source Belief",
    "Supporting Evidence",
    "Promotion Record",
    "Links",
    "Current State",
    "Change History",
    "Last Updated",
]


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(CognitiveOperator):
    """Belief -> Fact epistemic promotion operator.

    Owned by the Learning & Reflection Organ. Enacts the ADR-001
    promotion invariant inside the persistent epistemic layer.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["belief_path"]

    def validate(self, belief_path, **kwargs):
        """Check promotion eligibility; raise on any blocking condition."""
        sections = em.load_entity(belief_path)

        epistemic_state = sections.get("Epistemic State", "").strip()
        if epistemic_state == "Promoted":
            raise AlreadyPromotedError(
                f"Belief at '{belief_path}' is already Promoted. "
                f"Re-promotion is not permitted."
            )
        if epistemic_state == "Conflicted":
            raise ConflictedBeliefError(
                f"Belief at '{belief_path}' is in Conflicted state. "
                f"Resolve conflict before promotion (ADR-008 Invariant 8)."
            )

        confidence = parse_float(sections.get("Confidence", "0.0"))
        threshold = load_promotion_threshold()
        if confidence < threshold:
            raise BelowPromotionThresholdError(
                f"Belief at '{belief_path}' has confidence {confidence:.4f}, "
                f"below promotion threshold {threshold:.4f}."
            )
        return True

    def execute(self, belief_path, **kwargs):
        """Build Fact entity sections and the updated Belief sections."""
        sections = em.load_entity(belief_path)
        belief_path_obj = Path(belief_path)
        fact_id = "fact-" + belief_path_obj.stem
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        threshold = load_promotion_threshold()
        confidence = parse_float(sections.get("Confidence", "0.0"))

        fact_sections = OrderedDict([
            ("Identity", fact_id),
            ("Ownership",
             "Owned by the Learning & Reflection Organ, per ADR-001 and "
             "ADR-008. Enacting authority: BeliefToFact operator."),
            ("Canonical Basis", str(belief_path_obj)),
            ("Claim", sections.get("Claim", "").strip()),
            ("Confidence", f"{confidence:.4f}"),
            ("Epistemic State", "Promoted"),
            ("Source Belief", str(belief_path_obj)),
            ("Supporting Evidence",
             sections.get("Supporting Evidence", "None recorded.").strip()),
            ("Promotion Record",
             f"Promoted on {today} by BeliefToFact operator. "
             f"Confidence at promotion: {confidence:.4f}. "
             f"Threshold used: {threshold:.4f}."),
            ("Links",
             "- " + str(belief_path_obj) + "\n"
             "- FACTS/README.md"),
            ("Current State", "Promoted"),
            ("Change History",
             f"- {today}: Promoted from {belief_path_obj} by BeliefToFact."),
            ("Last Updated", today),
        ])

        # Build updated Belief sections (mark as Promoted, append history).
        updated_belief_sections = OrderedDict(sections)
        updated_belief_sections["Epistemic State"] = "Promoted"
        updated_belief_sections["Current State"] = "Promoted"
        existing_history = sections.get("Change History", "").strip()
        new_history_entry = (
            f"- {today}: Epistemic State updated to Promoted by BeliefToFact. "
            f"Fact entity created at FACTS/{fact_id}.md."
        )
        updated_belief_sections["Change History"] = (
            existing_history + "\n" + new_history_entry
            if existing_history
            else new_history_entry
        )
        updated_belief_sections["Last Updated"] = today

        fact_path = Path("FACTS") / (fact_id + ".md")

        return {
            "fact_sections": fact_sections,
            "fact_path": fact_path,
            "fact_id": fact_id,
            "updated_belief_sections": updated_belief_sections,
            "belief_path": belief_path_obj,
            "confidence": confidence,
            "threshold": threshold,
        }

    def persist(self, result, **kwargs):
        """Write Fact entity to FACTS/ and update source Belief in BELIEFS/.

        Creates FACTS/ if it does not exist. The source Belief's
        Epistemic State is updated to 'Promoted' in the same persist
        call so the two writes are always co-located.
        """
        fact_path = Path(result["fact_path"])
        fact_path.parent.mkdir(parents=True, exist_ok=True)
        em.save_entity(fact_path, result["fact_sections"],
                       section_order=_FACT_SECTION_ORDER)

        belief_path = Path(result["belief_path"])
        em.save_entity(belief_path, result["updated_belief_sections"])

        return fact_path

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        event = self.event_bus.emit(
            "FactPromoted",
            self.__class__.__name__,
            str(result["fact_path"]),
        )
        return [event]
