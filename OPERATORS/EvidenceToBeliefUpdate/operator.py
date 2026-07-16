"""EvidenceToBeliefUpdate operator.

Authority: Learning & Reflection Organ (ADR-001, ADR-008).
Input:     an epistemic Evidence entity path (EPISTEMIC_EVIDENCE/*.md).
Output:    updated Belief entity (BELIEFS/*.md) with revised confidence
           and updated Evidence sections; the Evidence entity's Current
           State is set to 'Applied'.

Contract:
- Reads `Valence`, `Strength`, `Linked Belief`, and `Current State` from
  the Evidence entity.
- Raises AlreadyAppliedError if Evidence.Current State == 'Applied'.
- Raises NeutralEvidenceSkippedInfo if Valence == 'Neutral' (no-op by
  design; caller should log and continue).
- Raises LinkedBeliefNotFoundError if the Linked Belief path does not
  exist.
- On Supporting valence: adds Strength to Belief.Confidence, clamps to
  [0.0, 1.0]; appends the Evidence reference to Supporting Evidence.
- On Contradicting valence: subtracts Strength from Belief.Confidence,
  clamps to [0.0, 1.0]; appends the Evidence reference to Conflicting
  Evidence. If updated confidence drops below regression_threshold (read
  from REASONING_PARAMETERS/belief_fact_promotion.md), sets Belief
  Epistemic State to 'Regression Pending' to signal that BeliefRegression
  should be invoked.
- Always: sets Evidence.Current State to 'Applied', appends Change
  History to both entities, updates Last Updated.
- Emits BeliefConfidenceUpdated event; emits BeliefRegressionPending
  event if regression threshold crossed.
- Idempotent guard: re-running on an Applied Evidence entity raises
  AlreadyAppliedError.
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from OPERATORS.engine import CognitiveOperator
import entity_markdown as em


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGRESSION_THRESHOLD_DEFAULT: float = 0.50
PROMOTION_PARAM_FILE = Path("REASONING_PARAMETERS") / "belief_fact_promotion.md"
CONFIDENCE_MIN: float = 0.0
CONFIDENCE_MAX: float = 1.0


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class AlreadyAppliedError(ValueError):
    """Evidence entity is already in 'Applied' state."""


class NeutralEvidenceSkippedInfo(ValueError):
    """Evidence Valence is Neutral — no confidence change applied."""


class LinkedBeliefNotFoundError(FileNotFoundError):
    """The Linked Belief path does not point to an existing entity."""


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(CognitiveOperator):
    """Routes new epistemic Evidence into the persistent epistemic layer.

    Owned by the Learning & Reflection Organ. Implements ADR-008
    Invariant 3: every authoritative Belief state change is traceable
    to supporting and/or contradicting Evidence.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["evidence_path"]

    def validate(self, evidence_path, **kwargs):
        sections = em.load_entity(evidence_path)

        state = sections.get("Current State", "").strip()
        if state == "Applied":
            raise AlreadyAppliedError(
                f"Evidence at '{evidence_path}' is already Applied. "
                "Re-application is not permitted."
            )

        valence = sections.get("Valence", "").strip()
        if valence == "Neutral":
            raise NeutralEvidenceSkippedInfo(
                f"Evidence at '{evidence_path}' has Neutral valence. "
                "No confidence change will be applied."
            )

        linked_belief = sections.get("Linked Belief", "").strip()
        if not linked_belief or not Path(linked_belief).exists():
            raise LinkedBeliefNotFoundError(
                f"Linked Belief '{linked_belief}' not found. "
                "Create the Belief entity before applying Evidence."
            )

        return True

    def execute(self, evidence_path, **kwargs):
        evidence_sections = em.load_entity(evidence_path)
        evidence_path_obj = Path(evidence_path)

        valence = evidence_sections.get("Valence", "").strip()
        strength = _parse_float(evidence_sections.get("Strength", "0.10"))
        linked_belief_path = Path(evidence_sections.get("Linked Belief", "").strip())
        evidence_ref = str(evidence_path_obj)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        belief_sections = em.load_entity(linked_belief_path)
        old_confidence = _parse_float(belief_sections.get("Confidence", "0.0"))

        if valence == "Supporting":
            new_confidence = min(CONFIDENCE_MAX, old_confidence + strength)
        else:  # Contradicting
            new_confidence = max(CONFIDENCE_MIN, old_confidence - strength)

        regression_threshold = _load_regression_threshold()
        regression_pending = (
            valence == "Contradicting"
            and new_confidence < regression_threshold
        )

        # Build updated Belief sections.
        updated_belief = OrderedDict(belief_sections)
        updated_belief["Confidence"] = f"{new_confidence:.4f}"

        if valence == "Supporting":
            existing_support = belief_sections.get("Supporting Evidence", "").strip()
            new_support = (
                existing_support + "\n- " + evidence_ref
                if existing_support
                else "- " + evidence_ref
            )
            updated_belief["Supporting Evidence"] = new_support
        else:
            existing_conflict = belief_sections.get("Conflicting Evidence", "").strip()
            new_conflict = (
                existing_conflict + "\n- " + evidence_ref
                if existing_conflict
                else "- " + evidence_ref
            )
            updated_belief["Conflicting Evidence"] = new_conflict

        if regression_pending:
            updated_belief["Epistemic State"] = "Regression Pending"
            updated_belief["Current State"] = "Regression Pending"

        belief_history = belief_sections.get("Change History", "").strip()
        belief_history_entry = (
            f"- {today}: Confidence updated {old_confidence:.4f} -> "
            f"{new_confidence:.4f} by EvidenceToBeliefUpdate "
            f"(valence={valence}, strength={strength:.4f}, "
            f"evidence={evidence_ref})."
            + (" Epistemic State set to 'Regression Pending'." if regression_pending else "")
        )
        updated_belief["Change History"] = (
            belief_history + "\n" + belief_history_entry
            if belief_history
            else belief_history_entry
        )
        updated_belief["Last Updated"] = today

        # Build updated Evidence sections (only Current State changes).
        updated_evidence = OrderedDict(evidence_sections)
        updated_evidence["Current State"] = "Applied"
        evidence_history = evidence_sections.get("Change History", "").strip()
        evidence_history_entry = (
            f"- {today}: State set to Applied by EvidenceToBeliefUpdate. "
            f"Confidence delta applied to {linked_belief_path}."
        )
        updated_evidence["Change History"] = (
            evidence_history + "\n" + evidence_history_entry
            if evidence_history
            else evidence_history_entry
        )
        updated_evidence["Last Updated"] = today

        return {
            "updated_belief_sections": updated_belief,
            "belief_path": linked_belief_path,
            "updated_evidence_sections": updated_evidence,
            "evidence_path": evidence_path_obj,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "valence": valence,
            "strength": strength,
            "regression_pending": regression_pending,
            "regression_threshold": regression_threshold,
        }

    def persist(self, result, **kwargs):
        """Write updated Belief and updated Evidence entities."""
        em.save_entity(result["belief_path"], result["updated_belief_sections"])
        em.save_entity(result["evidence_path"], result["updated_evidence_sections"])
        return result["belief_path"]

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        events = []
        evt = self.event_bus.emit(
            "BeliefConfidenceUpdated",
            self.__class__.__name__,
            str(result["belief_path"]),
        )
        events.append(evt)
        if result["regression_pending"]:
            evt2 = self.event_bus.emit(
                "BeliefRegressionPending",
                self.__class__.__name__,
                str(result["belief_path"]),
            )
            events.append(evt2)
        return events


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_float(value: str) -> float:
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return 0.0


def _load_regression_threshold() -> float:
    """Read regression_threshold from belief_fact_promotion.md.

    Falls back to REGRESSION_THRESHOLD_DEFAULT if absent or unparseable.
    """
    try:
        sections = em.load_entity(PROMOTION_PARAM_FILE)
        current_value = sections.get("Current Value", "")
        # Scan for a line headed '### regression_threshold' followed by a float.
        lines = current_value.splitlines()
        for i, line in enumerate(lines):
            if "regression_threshold" in line.lower():
                for subsequent in lines[i + 1:]:
                    stripped = subsequent.strip()
                    try:
                        candidate = float(stripped)
                        if 0.0 < candidate <= 1.0:
                            return candidate
                    except ValueError:
                        if stripped:
                            break
    except Exception:
        pass
    return REGRESSION_THRESHOLD_DEFAULT
