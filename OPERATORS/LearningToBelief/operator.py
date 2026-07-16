"""LearningToBelief operator.

Authority: Learning & Reflection Organ (ADR-008).
Input:     a Learning entity path (LEARNING/*.md).
Output:    a Belief entity path (BELIEFS/*.md).

Contract:
- Reads a Learning entity and extracts belief-relevant content.
- Creates or updates a Belief entity in BELIEFS/.
- The Belief entity is the authoritative epistemic record for the claim
  extracted from this Learning event.
- Revision history is append-only; no entry is ever overwritten.
- Confidence is initialised at 0.50 (neutral) for new Beliefs;
  update semantics (convergence, promotion, regression) are delegated
  to future lifecycle operators (BeliefToFact, BeliefRegression).
- If the source Learning entity has no usable content, raises
  NoUsableLearningError rather than silently producing an empty Belief.
"""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

from OPERATORS.engine import CognitiveOperator
import entity_markdown as em


class NoUsableLearningError(ValueError):
    """Raised when the source Learning entity contains no extractable content."""


# Canonical section order for Belief entities.
_BELIEF_SECTION_ORDER = [
    "Identity",
    "Ownership",
    "Canonical Basis",
    "Claim",
    "Confidence",
    "Epistemic State",
    "Epistemic Completeness",
    "Source Learning",
    "Supporting Evidence",
    "Conflicting Evidence",
    "Links",
    "Current State",
    "Change History",
    "Last Updated",
]


class Operator(CognitiveOperator):
    """Learning -> Belief epistemic lifecycle operator.

    Owned by the Learning & Reflection Organ. Sole authority to enact
    authoritative Belief state changes in BELIEFS/, per ADR-008.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus

    # ------------------------------------------------------------------
    # CognitiveOperator interface
    # ------------------------------------------------------------------

    def inputs(self):
        return ["learning_path"]

    def validate(self, learning_path, **kwargs):
        """Return True if the Learning entity has extractable content.

        Raises NoUsableLearningError if the Learning section is empty,
        consistent with how MemoryToReasoning handles this case.
        """
        sections = em.load_entity(learning_path)
        learning_text = sections.get("Learning", "").strip()
        if not learning_text:
            raise NoUsableLearningError(
                f"Learning entity at '{learning_path}' has no content in "
                f"the 'Learning' section. Cannot produce a Belief."
            )
        return True

    def execute(self, learning_path, **kwargs):
        """Extract belief-relevant content and build Belief entity sections."""
        sections = em.load_entity(learning_path)
        source_path = Path(learning_path)
        belief_id = "belief-" + source_path.stem
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        learning_text = sections.get("Learning", "").strip()
        context_text = sections.get("Context", "").strip()
        hypotheses_text = sections.get("Hypotheses", "").strip()

        # Derive the claim: use the first bullet from Learning, or the
        # full learning text if it is not a bullet list.
        claim = _extract_primary_claim(learning_text)

        # Evidence references inherited from the source entity.
        supporting = sections.get("Predictions", "").strip() or "None at initialisation."

        belief_sections = OrderedDict([
            ("Identity", belief_id),
            ("Ownership",
             "Owned by the Learning & Reflection Organ, per ADR-008 and "
             "QENKI_MIND_ORGANS_v1.md. Enacting authority: LearningToBelief operator."),
            ("Canonical Basis", str(source_path)),
            ("Claim", claim),
            ("Confidence", "0.50"),
            ("Epistemic State", "Active"),
            ("Epistemic Completeness",
             "Partial — initialised from a single Learning event. "
             "Confidence reflects neutral initialisation, not convergent Evidence."),
            ("Source Learning", str(source_path)),
            ("Supporting Evidence", supporting),
            ("Conflicting Evidence", "None recorded."),
            ("Links",
             "- " + str(source_path) + "\n"
             "- BELIEFS/README.md"),
            ("Current State", "Active"),
            ("Change History",
             "- " + today + ": Initialised by LearningToBelief from "
             + str(source_path) + "."),
            ("Last Updated", today),
        ])

        # Carry context and hypotheses as supplementary metadata if present.
        if context_text:
            belief_sections["Context"] = context_text
        if hypotheses_text:
            belief_sections["Hypotheses"] = hypotheses_text

        target_path = Path("BELIEFS") / (belief_id + ".md")
        return {
            "sections": belief_sections,
            "path": target_path,
            "belief_id": belief_id,
            "source": str(source_path),
        }

    def persist(self, result, **kwargs):
        """Write the Belief entity to BELIEFS/.

        Creates the directory if it does not exist.
        If a Belief file for the same identity already exists, the
        existing file is overwritten (idempotent re-execution).
        """
        path = Path(result["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        em.save_entity(path, result["sections"],
                       section_order=_BELIEF_SECTION_ORDER)
        return path

    def emit_events(self, result, **kwargs):
        if not self.event_bus:
            return []
        event = self.event_bus.emit(
            "BeliefCreated",
            self.__class__.__name__,
            str(result["path"]),
        )
        return [event]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_primary_claim(learning_text: str) -> str:
    """Return the first meaningful sentence or bullet from learning_text.

    If the text is a bullet list, returns the content of the first bullet.
    Otherwise returns the first non-empty line.
    """
    for line in learning_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
        if stripped:
            return stripped
    return learning_text.strip()
