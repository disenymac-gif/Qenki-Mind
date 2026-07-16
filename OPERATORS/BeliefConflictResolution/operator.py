"""BeliefConflictResolution operator.

Authority: Learning & Reflection Organ (ADR-001, ADR-008, ADR-009).
Input:     a Belief entity path (BELIEFS/*.md) in 'Conflicted' state.
Output:    updated Belief entity in 'Active' state with confidence
           re-evaluated from its Applied Evidence corpus.

Contract (ADR-009):
- Raises BeliefNotConflictedError if Belief.Epistemic State != 'Conflicted'.
- Reads every Applied Evidence entity referenced in the Belief's
  Supporting Evidence and Conflicting Evidence sections.
  Evidence entities that are not 'Applied' are skipped (not yet
  integrated into the Belief's authoritative confidence signal).
- Net confidence = sum(Supporting strengths) - sum(Contradicting strengths),
  clamped to [0.0, 1.0].
- Compares net confidence against promotion_threshold from
  REASONING_PARAMETERS/belief_fact_promotion.md.
- Sets Belief.Confidence to net confidence.
- Sets Belief.Epistemic State and Belief.Current State to 'Active'
  in both sub-cases (net >= threshold and net < threshold).
- Never directly promotes: BeliefToFact remains the sole promotion gate.
- Appends a Change History entry recording resolution date, net
  confidence, previous state, and eligibility outcome.
- Emits BeliefConflictResolved event.
- Evidence entities are read-only; their state is never mutated.
- Deterministic: same Evidence corpus + threshold always yields same result.
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

PROMOTION_THRESHOLD_DEFAULT: float = 0.80
PARAMETER_FILE = Path("REASONING_PARAMETERS") / "belief_fact_promotion.md"
CONFIDENCE_MIN: float = 0.0
CONFIDENCE_MAX: float = 1.0


# ---------------------------------------------------------------------------
# Domain exception
# ---------------------------------------------------------------------------

class BeliefNotConflictedError(ValueError):
    """Belief is not in 'Conflicted' state."""


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(CognitiveOperator):
    """Conflicted Belief -> Active (evidence-grounded resolution).

    Owned by Learning & Reflection Organ. Implements ADR-009:
    re-evaluates net confidence from all Applied Evidence, transitions
    Belief to Active, never promotes directly.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["belief_path"]

    def validate(self, belief_path, **kwargs):
        """Guard: raise if Belief is not in Conflicted state."""
        sections = em.load_entity(belief_path)
        state = sections.get("Epistemic State", "").strip()
        if state != "Conflicted":
            raise BeliefNotConflictedError(
                f"Belief at '{belief_path}' is in state '{state}', "
                f"not 'Conflicted'. BeliefConflictResolution requires a "
                f"Belief whose Epistemic State is 'Conflicted'."
            )
        return True

    def execute(self, belief_path, **kwargs):
        """Re-evaluate net confidence; build updated Belief sections."""
        belief_path_obj = Path(belief_path)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        threshold = _load_threshold()

        belief_sections = em.load_entity(belief_path_obj)
        supporting_refs = _parse_evidence_refs(
            belief_sections.get("Supporting Evidence", "")
        )
        conflicting_refs = _parse_evidence_refs(
            belief_sections.get("Conflicting Evidence", "")
        )

        supporting_sum = _sum_applied_strengths(supporting_refs)
        contradicting_sum = _sum_applied_strengths(conflicting_refs)
        net_confidence = _clamp(
            supporting_sum - contradicting_sum, CONFIDENCE_MIN, CONFIDENCE_MAX
        )

        eligible_for_promotion = net_confidence >= threshold
        eligibility_note = (
            f"eligible for promotion via BeliefToFact (net {net_confidence:.4f} "
            f">= threshold {threshold:.4f})"
            if eligible_for_promotion
            else
            f"below promotion threshold (net {net_confidence:.4f} "
            f"< threshold {threshold:.4f}); eligible for further Evidence "
            f"accumulation or Archival"
        )

        updated_belief = OrderedDict(belief_sections)
        updated_belief["Confidence"] = f"{net_confidence:.4f}"
        updated_belief["Epistemic State"] = "Active"
        updated_belief["Current State"] = "Active"

        history = belief_sections.get("Change History", "").strip()
        history_entry = (
            f"- {today}: Conflicted state resolved by BeliefConflictResolution. "
            f"Net confidence re-evaluated to {net_confidence:.4f} "
            f"(supporting={supporting_sum:.4f}, contradicting={contradicting_sum:.4f}). "
            f"Epistemic State restored to Active. {eligibility_note}."
        )
        updated_belief["Change History"] = (
            history + "\n" + history_entry if history else history_entry
        )
        updated_belief["Last Updated"] = today

        return {
            "updated_belief_sections": updated_belief,
            "belief_path": belief_path_obj,
            "net_confidence": net_confidence,
            "supporting_sum": supporting_sum,
            "contradicting_sum": contradicting_sum,
            "threshold": threshold,
            "eligible_for_promotion": eligible_for_promotion,
        }

    def persist(self, result, **kwargs):
        """Write updated Belief entity."""
        em.save_entity(result["belief_path"], result["updated_belief_sections"])
        return result["belief_path"]

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        event = self.event_bus.emit(
            "BeliefConflictResolved",
            self.__class__.__name__,
            str(result["belief_path"]),
        )
        return [event]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_evidence_refs(section_value: str) -> list[str]:
    """Extract file paths from a Supporting/Conflicting Evidence section.

    Accepts lines of the form:
        - EPISTEMIC_EVIDENCE/ev-001.md
        EPISTEMIC_EVIDENCE/ev-002.md
    Skips blank lines and 'None.' placeholders.
    """
    refs = []
    for line in section_value.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        if stripped and stripped.lower() not in ("none.", "none"):
            refs.append(stripped)
    return refs


def _sum_applied_strengths(evidence_refs: list[str]) -> float:
    """Sum the Strength of all Applied Evidence entities in refs.

    Evidence entities not in 'Applied' state are skipped (not yet
    integrated into the authoritative confidence signal).
    Unreadable or missing files are skipped silently.
    """
    total = 0.0
    for ref in evidence_refs:
        try:
            sections = em.load_entity(ref)
            state = sections.get("Current State", "").strip()
            if state != "Applied":
                continue
            total += _parse_float(sections.get("Strength", "0.0"))
        except Exception:
            continue
    return total


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _parse_float(value: str) -> float:
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return 0.0


def _load_threshold() -> float:
    """Read promotion_threshold from belief_fact_promotion.md."""
    try:
        sections = em.load_entity(PARAMETER_FILE)
        current_value = sections.get("Current Value", "")
        for line in current_value.splitlines():
            stripped = line.strip()
            try:
                candidate = float(stripped)
                if 0.0 < candidate <= 1.0:
                    return candidate
            except ValueError:
                continue
    except Exception:
        pass
    return PROMOTION_THRESHOLD_DEFAULT
