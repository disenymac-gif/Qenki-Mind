"""BeliefArchival operator.

Authority: Learning & Reflection Organ (ADR-001, ADR-008).
Input:     a Belief entity path (BELIEFS/*.md) that is not already Archived.
Output:    updated Belief entity in 'Archived' state; co-archived Fact
           entity in 'Archived' state if a corresponding Fact exists in
           FACTS/fact-<stem>.md.

Contract:
- Raises BeliefAlreadyArchivedError if Belief.Epistemic State == 'Archived'.
- Accepted input states: 'Active', 'Promoted', 'Regressed',
  'Regression Pending', 'Conflicted'.
- On success:
    1. Transitions Belief Epistemic State and Current State to 'Archived'.
    2. Appends a Change History entry to the Belief.
    3. If a Fact entity exists at FACTS/fact-<stem>.md:
       a. Transitions the Fact Epistemic State and Current State to
          'Archived'.
       b. Appends a Change History entry to the Fact.
       c. Emits a FactArchived event in addition to BeliefArchived.
    4. Emits a BeliefArchived event always.
- Idempotent by guard: re-running on an already-Archived Belief raises
  BeliefAlreadyArchivedError rather than applying the transition twice.
- This operator is terminal: no further epistemic operators are defined
  for Archived Beliefs or Facts.
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from OPERATORS.engine import CognitiveOperator
import entity_markdown as em


# ---------------------------------------------------------------------------
# Domain exception
# ---------------------------------------------------------------------------

class BeliefAlreadyArchivedError(ValueError):
    """Belief is already in 'Archived' state."""


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(CognitiveOperator):
    """Belief (any non-Archived state) -> Archived terminal operator.

    Owned by the Learning & Reflection Organ. Implements the terminal
    transition in the ADR-008 Belief lifecycle: any Belief that is no
    longer operationally relevant may be archived. Co-archives the
    corresponding Fact if one has been promoted.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["belief_path"]

    def validate(self, belief_path, **kwargs):
        """Guard: raise if Belief is already Archived."""
        sections = em.load_entity(belief_path)
        state = sections.get("Epistemic State", "").strip()
        if state == "Archived":
            raise BeliefAlreadyArchivedError(
                f"Belief at '{belief_path}' is already Archived. "
                "Re-archival is not permitted."
            )
        return True

    def execute(self, belief_path, **kwargs):
        """Build updated Belief and optional updated Fact sections."""
        belief_path_obj = Path(belief_path)
        fact_path = _derive_fact_path(belief_path)
        has_fact = fact_path.exists()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        belief_sections = em.load_entity(belief_path_obj)
        previous_state = belief_sections.get("Epistemic State", "Unknown").strip()

        # ---- Update Belief -------------------------------------------------
        updated_belief = OrderedDict(belief_sections)
        updated_belief["Epistemic State"] = "Archived"
        updated_belief["Current State"] = "Archived"
        belief_history = belief_sections.get("Change History", "").strip()
        belief_entry = (
            f"- {today}: Epistemic State transitioned from '{previous_state}' "
            f"to 'Archived' by BeliefArchival operator."
            + (f" Co-archived Fact '{fact_path.name}'." if has_fact else "")
        )
        updated_belief["Change History"] = (
            belief_history + "\n" + belief_entry if belief_history else belief_entry
        )
        updated_belief["Last Updated"] = today

        # ---- Update Fact (optional) ----------------------------------------
        updated_fact = None
        if has_fact:
            fact_sections = em.load_entity(fact_path)
            updated_fact = OrderedDict(fact_sections)
            updated_fact["Epistemic State"] = "Archived"
            updated_fact["Current State"] = "Archived"
            fact_history = fact_sections.get("Change History", "").strip()
            fact_entry = (
                f"- {today}: Epistemic State set to 'Archived' by BeliefArchival "
                f"operator. Source Belief: {belief_path_obj}."
            )
            updated_fact["Change History"] = (
                fact_history + "\n" + fact_entry if fact_history else fact_entry
            )
            updated_fact["Last Updated"] = today

        return {
            "updated_belief_sections": updated_belief,
            "belief_path": belief_path_obj,
            "previous_state": previous_state,
            "updated_fact_sections": updated_fact,
            "fact_path": fact_path if has_fact else None,
            "has_fact": has_fact,
        }

    def persist(self, result, **kwargs):
        """Write updated Belief and (if present) updated Fact entities."""
        em.save_entity(result["belief_path"], result["updated_belief_sections"])
        if result["has_fact"] and result["fact_path"] is not None:
            em.save_entity(result["fact_path"], result["updated_fact_sections"])
        return result["belief_path"]

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        events = []
        events.append(
            self.event_bus.emit(
                "BeliefArchived",
                self.__class__.__name__,
                str(result["belief_path"]),
            )
        )
        if result["has_fact"] and result["fact_path"] is not None:
            events.append(
                self.event_bus.emit(
                    "FactArchived",
                    self.__class__.__name__,
                    str(result["fact_path"]),
                )
            )
        return events


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _derive_fact_path(belief_path) -> Path:
    """Derive the canonical Fact path from a Belief path.

    Convention (ADR-001 + ADR-008):
        BELIEFS/<stem>.md  ->  FACTS/fact-<stem>.md
    """
    stem = Path(belief_path).stem
    return Path("FACTS") / f"fact-{stem}.md"
