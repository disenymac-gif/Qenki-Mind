"""_belief_utils.py

Shared utility functions for epistemic lifecycle operators.

All helpers here are pure functions with no side-effects. They are
intentionally narrow in scope: each solves exactly one problem that
was previously duplicated across two or more operators.

Imported by:
- BeliefToFact.operator
- EvidenceToBeliefUpdate.operator
- BeliefConflictResolution.operator
- BeliefRegression.operator
- BeliefArchival.operator

Do not import from this module outside OPERATORS/. It is an internal
utility layer, not part of the public Qenki-Mind API.
"""
from __future__ import annotations

from pathlib import Path

import entity_markdown as em


# ---------------------------------------------------------------------------
# Constants — canonical parameter file location
# ---------------------------------------------------------------------------

_PARAMETER_FILE = Path("REASONING_PARAMETERS") / "belief_fact_promotion.md"
_PROMOTION_THRESHOLD_DEFAULT: float = 0.80
_REGRESSION_THRESHOLD_DEFAULT: float = 0.50


# ---------------------------------------------------------------------------
# parse_float
# ---------------------------------------------------------------------------

def parse_float(value: object) -> float:
    """Parse a float from a string (or any object via str()). Returns 0.0 on failure.

    Used for Confidence and Strength fields across all epistemic operators.
    Equivalent to the private _parse_float / _parse_confidence helpers
    that were previously duplicated in BeliefToFact, EvidenceToBeliefUpdate,
    BeliefConflictResolution, and BeliefRegression.
    """
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# load_promotion_threshold
# ---------------------------------------------------------------------------

def load_promotion_threshold() -> float:
    """Read promotion_threshold from belief_fact_promotion.md.

    The parameter file is expected to contain a 'Current Value' section
    whose content includes a bare float on one of its lines (e.g. '0.80').

    Falls back to _PROMOTION_THRESHOLD_DEFAULT (0.80) if:
    - the parameter file does not exist;
    - the 'Current Value' section is absent;
    - no parseable float in (0, 1] is found.

    This function consolidates the previously duplicated _load_threshold()
    helpers in BeliefToFact, EvidenceToBeliefUpdate, and
    BeliefConflictResolution.
    """
    try:
        sections = em.load_entity(_PARAMETER_FILE)
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
    return _PROMOTION_THRESHOLD_DEFAULT


# ---------------------------------------------------------------------------
# load_regression_threshold
# ---------------------------------------------------------------------------

def load_regression_threshold() -> float:
    """Read regression_threshold from belief_fact_promotion.md.

    The parameter file's 'Current Value' section is expected to contain
    a line headed '### regression_threshold' (or any line containing
    'regression_threshold') followed by a bare float on a subsequent line.

    Falls back to _REGRESSION_THRESHOLD_DEFAULT (0.50) if:
    - the parameter file does not exist;
    - no regression_threshold marker is found;
    - no parseable float in (0, 1] follows the marker.

    This function consolidates the previously duplicated
    _load_regression_threshold() helper in EvidenceToBeliefUpdate.
    """
    try:
        sections = em.load_entity(_PARAMETER_FILE)
        current_value = sections.get("Current Value", "")
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
    return _REGRESSION_THRESHOLD_DEFAULT


# ---------------------------------------------------------------------------
# derive_fact_path
# ---------------------------------------------------------------------------

def derive_fact_path(belief_path: object) -> Path:
    """Derive the canonical Fact path from a Belief path.

    Convention (ADR-001 + ADR-008):
        BELIEFS/<stem>.md  ->  FACTS/fact-<stem>.md

    This function consolidates the previously duplicated _derive_fact_path()
    helpers in BeliefRegression and BeliefArchival.
    """
    stem = Path(belief_path).stem
    return Path("FACTS") / f"fact-{stem}.md"
