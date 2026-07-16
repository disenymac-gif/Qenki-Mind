"""BeliefRegression operator.

Authority: Learning & Reflection Organ (ADR-001, ADR-008).
Input:     a Belief entity path (BELIEFS/*.md) in 'Regression Pending'
           state.
Output:    updated Belief entity restored to 'Active' epistemic state;
           corresponding Fact entity (FACTS/fact-<stem>.md) transitioned
           to 'Regressed' state.

Contract:
- Raises BeliefNotRegressionPendingError if the Belief is not in
  'Regression Pending' state.
- Raises FactNotFoundError if the corresponding Fact entity does not
  exist in FACTS/ (regression requires a previously promoted Fact).
- On success:
    1. Transitions the Fact entity's Epistemic State and Current State
       to 'Regressed' and appends a Change History entry.
    2. Restores the Belief entity's Epistemic State and Current State
       to 'Active' and appends a Change History entry.
    3. Emits a FactRegressed event.
- Idempotent by guard: re-running on an Active Belief (after a
  successful regression) raises BeliefNotRegressionPendingError.
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from OPERATORS.engine import CognitiveOperator
import entity_markdown as em


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class BeliefNotRegressionPendingError(ValueError):
    """Belief is not in 'Regression Pending' state."""


class FactNotFoundError(FileNotFoundError):
    """The corresponding Fact entity does not exist in FACTS/."""


# ---------------------------------------------------------------------------
# Canonical section order for regressed Fact entities
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
    "Regression Record",
    "Links",
    "Current State",
    "Change History",
    "Last Updated",
]


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(CognitiveOperator):
    """Fact -> Regression epistemic demotion operator.

    Owned by the Learning & Reflection Organ. Invoked when
    EvidenceToBeliefUpdate has driven a Belief's confidence below
    regression_threshold, setting the Belief's Epistemic State to
    'Regression Pending'. This operator completes the regression arc:
    it demotes the corresponding Fact to 'Regressed' and restores the
    Belief to 'Active' so the epistemic cycle can continue.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["belief_path"]

    def validate(self, belief_path, **kwargs):
        """Guard: Belief must be in 'Regression Pending' state."""
        sections = em.load_entity(belief_path)
        epistemic_state = sections.get("Epistemic State", "").strip()
        if epistemic_state != "Regression Pending":
            raise BeliefNotRegressionPendingError(
                f"Belief at '{belief_path}' is in state '{epistemic_state}', "
                f"not 'Regression Pending'. BeliefRegression requires a Belief "
                f"whose Epistemic State is 'Regression Pending'."
            )

        fact_path = _derive_fact_path(belief_path)
        if not fact_path.exists():
            raise FactNotFoundError(
                f"Fact entity '{fact_path}' not found. "
                f"BeliefRegression requires a previously promoted Fact. "
                f"Promote the Belief via BeliefToFact before regressing."
            )
        return True

    def execute(self, belief_path, **kwargs):
        """Build updated Fact (Regressed) and updated Belief (Active)."""
        belief_path_obj = Path(belief_path)
        fact_path = _derive_fact_path(belief_path)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        belief_sections = em.load_entity(belief_path_obj)
        fact_sections = em.load_entity(fact_path)

        confidence = belief_sections.get("Confidence", "0.0000").strip()

        # ---- Update Fact entity ----------------------------------------
        updated_fact = OrderedDict(fact_sections)
        updated_fact["Epistemic State"] = "Regressed"
        updated_fact["Current State"] = "Regressed"
        updated_fact["Regression Record"] = (
            f"Regressed on {today} by BeliefRegression operator. "
            f"Belief confidence at regression: {confidence}. "
            f"Source Belief: {belief_path_obj}."
        )
        fact_history = fact_sections.get("Change History", "").strip()
        fact_history_entry = (
            f"- {today}: Epistemic State set to Regressed by BeliefRegression. "
            f"Belief confidence dropped to {confidence}."
        )
        updated_fact["Change History"] = (
            fact_history + "\n" + fact_history_entry
            if fact_history
            else fact_history_entry
        )
        updated_fact["Last Updated"] = today

        # ---- Update Belief entity --------------------------------------
        updated_belief = OrderedDict(belief_sections)
        updated_belief["Epistemic State"] = "Active"
        updated_belief["Current State"] = "Active"
        belief_history = belief_sections.get("Change History", "").strip()
        belief_history_entry = (
            f"- {today}: Epistemic State restored to Active by BeliefRegression. "
            f"Corresponding Fact '{fact_path.name}' transitioned to Regressed."
        )
        updated_belief["Change History"] = (
            belief_history + "\n" + belief_history_entry
            if belief_history
            else belief_history_entry
        )
        updated_belief["Last Updated"] = today

        return {
            "updated_fact_sections": updated_fact,
            "fact_path": fact_path,
            "updated_belief_sections": updated_belief,
            "belief_path": belief_path_obj,
            "confidence": confidence,
        }

    def persist(self, result, **kwargs):
        """Write updated Fact to FACTS/ and updated Belief to BELIEFS/."""
        em.save_entity(
            result["fact_path"],
            result["updated_fact_sections"],
            section_order=_FACT_SECTION_ORDER,
        )
        em.save_entity(result["belief_path"], result["updated_belief_sections"])
        return result["fact_path"]

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        event = self.event_bus.emit(
            "FactRegressed",
            self.__class__.__name__,
            str(result["fact_path"]),
        )
        return [event]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_fact_path(belief_path) -> Path:
    """Derive the canonical Fact path from a Belief path.

    Convention (ADR-001 + ADR-008):
        BELIEFS/<stem>.md  ->  FACTS/fact-<stem>.md
    """
    stem = Path(belief_path).stem
    return Path("FACTS") / f"fact-{stem}.md"
