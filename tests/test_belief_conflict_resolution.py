"""Tests for the BeliefConflictResolution operator.

Covers:
- BeliefNotConflictedError for all non-Conflicted states
- validate() passes for Conflicted state
- execute() with only Supporting Evidence
- execute() with only Contradicting Evidence
- execute() with mixed Evidence
- execute() with no Evidence (net confidence = 0.0)
- execute() with non-Applied Evidence skipped
- net confidence clamped to [0.0, 1.0]
- eligible_for_promotion flag correct in both sub-cases
- Belief Epistemic State and Current State -> Active in both sub-cases
- Change History entry appended (accumulation)
- Change History records net, supporting, contradicting sums
- persist() writes updated Belief
- persist() returns belief_path
- BeliefConflictResolved event emitted
- No event without EventBus
- E2E: Evidence -> Belief (Conflicted) -> Resolution -> BeliefToFact
- E2E: Resolution below threshold -> Active (not promoted directly)
"""
from __future__ import annotations

import pytest
from pathlib import Path
from collections import OrderedDict
from unittest.mock import MagicMock

from OPERATORS.BeliefConflictResolution.operator import (
    Operator,
    BeliefNotConflictedError,
    _parse_evidence_refs,
    _sum_applied_strengths,
)
import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_belief(tmp_path, stem, epistemic_state="Conflicted",
                 confidence="0.5000",
                 supporting="None.", conflicting="None.", history=""):
    path = tmp_path / "BELIEFS" / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", stem),
        ("Claim", f"Test claim for {stem}."),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Current State", epistemic_state),
        ("Supporting Evidence", supporting),
        ("Conflicting Evidence", conflicting),
        ("Change History", history),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_evidence(tmp_path, stem, valence, strength, state="Applied"):
    path = tmp_path / "EPISTEMIC_EVIDENCE" / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", stem),
        ("Valence", valence),
        ("Strength", str(strength)),
        ("Linked Belief", ""),
        ("Current State", state),
        ("Change History", ""),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_param_file(tmp_path, threshold=0.80):
    path = tmp_path / "REASONING_PARAMETERS" / "belief_fact_promotion.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Parameter Definition", "promotion_threshold"),
        ("Current Value", str(threshold)),
        ("Change History", ""),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


# ---------------------------------------------------------------------------
# validate() guard
# ---------------------------------------------------------------------------

class TestValidateGuard:
    @pytest.mark.parametrize("state", [
        "Active", "Promoted", "Regressed", "Regression Pending", "Archived"
    ])
    def test_raises_for_non_conflicted(self, tmp_path, monkeypatch, state):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, f"c-{state.replace(' ', '-').lower()}",
                            epistemic_state=state)
        op = Operator()
        with pytest.raises(BeliefNotConflictedError, match=state):
            op.validate(path)

    def test_passes_for_conflicted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c-pass", epistemic_state="Conflicted")
        op = Operator()
        assert op.validate(path) is True


# ---------------------------------------------------------------------------
# execute() — net confidence calculation
# ---------------------------------------------------------------------------

class TestNetConfidenceCalculation:
    def test_supporting_only(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(tmp_path, "ev-s01", "Supporting", 0.30)
        path = _make_belief(tmp_path, "c001",
                            supporting=f"- {ev}", conflicting="None.")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert abs(result["net_confidence"] - 0.30) < 1e-6
        assert abs(result["supporting_sum"] - 0.30) < 1e-6
        assert abs(result["contradicting_sum"] - 0.00) < 1e-6

    def test_contradicting_only(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(tmp_path, "ev-c01", "Contradicting", 0.40)
        path = _make_belief(tmp_path, "c002",
                            supporting="None.", conflicting=f"- {ev}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        # net = 0 - 0.40 clamped to 0
        assert result["net_confidence"] == 0.0
        assert abs(result["contradicting_sum"] - 0.40) < 1e-6

    def test_mixed_evidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev_s = _make_evidence(tmp_path, "ev-m01", "Supporting", 0.60)
        ev_c = _make_evidence(tmp_path, "ev-m02", "Contradicting", 0.25)
        path = _make_belief(tmp_path, "c003",
                            supporting=f"- {ev_s}",
                            conflicting=f"- {ev_c}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert abs(result["net_confidence"] - 0.35) < 1e-6

    def test_no_evidence_net_zero(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c004",
                            supporting="None.", conflicting="None.")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert result["net_confidence"] == 0.0

    def test_non_applied_evidence_skipped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev_applied = _make_evidence(tmp_path, "ev-a01", "Supporting", 0.50,
                                    state="Applied")
        ev_pending = _make_evidence(tmp_path, "ev-p01", "Supporting", 0.30,
                                    state="Pending")
        path = _make_belief(tmp_path, "c005",
                            supporting=f"- {ev_applied}\n- {ev_pending}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        # Only Applied evidence counted
        assert abs(result["net_confidence"] - 0.50) < 1e-6

    def test_clamped_to_max_one(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev1 = _make_evidence(tmp_path, "ev-hi01", "Supporting", 0.80)
        ev2 = _make_evidence(tmp_path, "ev-hi02", "Supporting", 0.80)
        path = _make_belief(tmp_path, "c006",
                            supporting=f"- {ev1}\n- {ev2}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert result["net_confidence"] == 1.0


# ---------------------------------------------------------------------------
# execute() — state and eligibility
# ---------------------------------------------------------------------------

class TestStateAndEligibility:
    def test_belief_active_above_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(tmp_path, "ev-e01", "Supporting", 0.90)
        path = _make_belief(tmp_path, "c010",
                            supporting=f"- {ev}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert result["updated_belief_sections"]["Epistemic State"] == "Active"
        assert result["updated_belief_sections"]["Current State"] == "Active"
        assert result["eligible_for_promotion"] is True

    def test_belief_active_below_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(tmp_path, "ev-e02", "Supporting", 0.50)
        path = _make_belief(tmp_path, "c011",
                            supporting=f"- {ev}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert result["updated_belief_sections"]["Epistemic State"] == "Active"
        assert result["eligible_for_promotion"] is False

    def test_confidence_updated_in_sections(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev_s = _make_evidence(tmp_path, "ev-e03", "Supporting", 0.70)
        ev_c = _make_evidence(tmp_path, "ev-e04", "Contradicting", 0.10)
        path = _make_belief(tmp_path, "c012",
                            supporting=f"- {ev_s}",
                            conflicting=f"- {ev_c}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        conf = float(result["updated_belief_sections"]["Confidence"])
        assert abs(conf - 0.60) < 1e-4


# ---------------------------------------------------------------------------
# Change History
# ---------------------------------------------------------------------------

class TestChangeHistory:
    def test_history_entry_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c020",
                            history="- 2026-07-15: Created.")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "2026-07-15: Created" in history
        assert "BeliefConflictResolution" in history

    def test_history_records_net_confidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(tmp_path, "ev-h01", "Supporting", 0.45)
        path = _make_belief(tmp_path, "c021",
                            supporting=f"- {ev}")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "0.4500" in history

    def test_history_created_from_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c022", history="")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert history.startswith("- ")


# ---------------------------------------------------------------------------
# persist()
# ---------------------------------------------------------------------------

class TestPersist:
    def test_belief_written_active(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c030")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        sections = em.load_entity(path)
        assert sections["Epistemic State"] == "Active"

    def test_persist_returns_belief_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c031")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        returned = op.persist(result)
        assert returned == path


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------

class TestEventEmission:
    def test_conflict_resolved_event_emitted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c040")
        _make_param_file(tmp_path, threshold=0.80)
        bus = MagicMock()
        bus.emit.return_value = {"event": "ok"}
        op = Operator(event_bus=bus)
        result = op.execute(path)
        op.emit_events(result)
        bus.emit.assert_called_once_with(
            "BeliefConflictResolved",
            "Operator",
            str(path),
        )

    def test_no_event_without_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "c041")
        _make_param_file(tmp_path, threshold=0.80)
        op = Operator()
        result = op.execute(path)
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# E2E: Resolution above threshold -> eligible for BeliefToFact
# ---------------------------------------------------------------------------

class TestEndToEndConflictResolutionArc:
    def test_resolution_above_threshold_then_promotable(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_param_file(tmp_path, threshold=0.80)

        ev_s1 = _make_evidence(tmp_path, "ev-arc-s01", "Supporting", 0.60)
        ev_s2 = _make_evidence(tmp_path, "ev-arc-s02", "Supporting", 0.35)
        ev_c1 = _make_evidence(tmp_path, "ev-arc-c01", "Contradicting", 0.10)

        # net = 0.60 + 0.35 - 0.10 = 0.85 >= 0.80 threshold
        path = _make_belief(
            tmp_path, "arc-conflict",
            epistemic_state="Conflicted",
            supporting=f"- {ev_s1}\n- {ev_s2}",
            conflicting=f"- {ev_c1}",
        )

        op = Operator()
        result = op.execute(path)
        op.persist(result)

        sections = em.load_entity(path)
        assert sections["Epistemic State"] == "Active"
        assert float(sections["Confidence"]) >= 0.80
        assert result["eligible_for_promotion"] is True

        # Now BeliefToFact should succeed (no ConflictedBeliefError).
        from OPERATORS.BeliefToFact.operator import Operator as B2F
        b2f = B2F()
        assert b2f.validate(path) is True

    def test_resolution_below_threshold_active_not_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_param_file(tmp_path, threshold=0.80)

        ev_s = _make_evidence(tmp_path, "ev-arc2-s01", "Supporting", 0.40)
        ev_c = _make_evidence(tmp_path, "ev-arc2-c01", "Contradicting", 0.20)
        # net = 0.40 - 0.20 = 0.20 < 0.80

        path = _make_belief(
            tmp_path, "arc-conflict-low",
            epistemic_state="Conflicted",
            supporting=f"- {ev_s}",
            conflicting=f"- {ev_c}",
        )

        op = Operator()
        result = op.execute(path)
        op.persist(result)

        sections = em.load_entity(path)
        assert sections["Epistemic State"] == "Active"
        assert result["eligible_for_promotion"] is False

        # BeliefToFact should raise BelowPromotionThresholdError, not
        # ConflictedBeliefError, because the Belief is now Active.
        from OPERATORS.BeliefToFact.operator import (
            Operator as B2F,
            BelowPromotionThresholdError,
        )
        from OPERATORS.BeliefConflictResolution.operator import BeliefNotConflictedError
        b2f = B2F()
        with pytest.raises(BelowPromotionThresholdError):
            b2f.validate(path)
        # Confirm it does NOT raise BeliefNotConflictedError.
        op2 = Operator()
        with pytest.raises(BeliefNotConflictedError):
            op2.validate(path)  # now Active, not Conflicted
