"""Tests for the BeliefRegression operator.

Covers:
- Happy path: Regression Pending Belief -> Regressed Fact + Active Belief
- BeliefNotRegressionPendingError for wrong Belief state
- FactNotFoundError when no corresponding Fact exists
- Change History accumulation on both entities
- Confidence preserved in Fact Regression Record
- FactRegressed event emitted
- No event emitted when no EventBus
- End-to-end: Evidence -> Belief -> Fact -> Regression full arc
"""
from __future__ import annotations

import pytest
from pathlib import Path
from collections import OrderedDict
from unittest.mock import MagicMock, patch

from OPERATORS.BeliefRegression.operator import (
    Operator,
    BeliefNotRegressionPendingError,
    FactNotFoundError,
    _derive_fact_path,
)
import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_belief(tmp_path, stem, epistemic_state="Regression Pending",
                 confidence="0.3500", history=""):
    """Write a minimal Belief entity and return its path."""
    path = tmp_path / "BELIEFS" / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", stem),
        ("Claim", f"Test claim for {stem}."),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Current State", epistemic_state),
        ("Supporting Evidence", "None."),
        ("Conflicting Evidence", "- EPISTEMIC_EVIDENCE/ev-001.md"),
        ("Change History", history),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_fact(tmp_path, stem, epistemic_state="Promoted",
               confidence="0.8500", history=""):
    """Write a minimal Fact entity and return its path."""
    path = tmp_path / "FACTS" / f"fact-{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", f"fact-{stem}"),
        ("Claim", f"Test claim for fact-{stem}."),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Current State", epistemic_state),
        ("Source Belief", f"BELIEFS/{stem}.md"),
        ("Promotion Record", f"Promoted on 2026-07-15 by BeliefToFact."),
        ("Change History", history),
        ("Last Updated", "2026-07-15"),
    ])
    em.save_entity(path, sections)
    return path


# ---------------------------------------------------------------------------
# _derive_fact_path helper
# ---------------------------------------------------------------------------

class TestDeriveFactPath:
    def test_derives_correct_path(self):
        result = _derive_fact_path("BELIEFS/some-belief.md")
        assert result == Path("FACTS/fact-some-belief.md")

    def test_derives_from_path_object(self):
        result = _derive_fact_path(Path("BELIEFS/another.md"))
        assert result == Path("FACTS/fact-another.md")

    def test_stem_only_no_directory(self):
        result = _derive_fact_path("bare.md")
        assert result == Path("FACTS/fact-bare.md")


# ---------------------------------------------------------------------------
# validate() guard conditions
# ---------------------------------------------------------------------------

class TestValidateGuards:
    def test_raises_if_belief_not_regression_pending(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b001", epistemic_state="Active")
        _make_fact(tmp_path, "b001")
        op = Operator()
        with pytest.raises(BeliefNotRegressionPendingError, match="Active"):
            op.validate(path)

    def test_raises_if_belief_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b002", epistemic_state="Promoted")
        _make_fact(tmp_path, "b002")
        op = Operator()
        with pytest.raises(BeliefNotRegressionPendingError, match="Promoted"):
            op.validate(path)

    def test_raises_if_belief_archived(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b003", epistemic_state="Archived")
        _make_fact(tmp_path, "b003")
        op = Operator()
        with pytest.raises(BeliefNotRegressionPendingError):
            op.validate(path)

    def test_raises_if_fact_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b004", epistemic_state="Regression Pending")
        # No corresponding Fact created.
        op = Operator()
        with pytest.raises(FactNotFoundError, match="fact-b004"):
            op.validate(path)

    def test_passes_with_regression_pending_and_existing_fact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b005", epistemic_state="Regression Pending")
        _make_fact(tmp_path, "b005")
        op = Operator()
        assert op.validate(path) is True


# ---------------------------------------------------------------------------
# execute() output structure
# ---------------------------------------------------------------------------

class TestExecuteOutput:
    def test_returns_required_keys(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b010")
        _make_fact(tmp_path, "b010")
        op = Operator()
        result = op.execute(path)
        assert "updated_fact_sections" in result
        assert "fact_path" in result
        assert "updated_belief_sections" in result
        assert "belief_path" in result
        assert "confidence" in result

    def test_fact_epistemic_state_regressed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b011")
        _make_fact(tmp_path, "b011")
        op = Operator()
        result = op.execute(path)
        assert result["updated_fact_sections"]["Epistemic State"] == "Regressed"
        assert result["updated_fact_sections"]["Current State"] == "Regressed"

    def test_belief_epistemic_state_active(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b012")
        _make_fact(tmp_path, "b012")
        op = Operator()
        result = op.execute(path)
        assert result["updated_belief_sections"]["Epistemic State"] == "Active"
        assert result["updated_belief_sections"]["Current State"] == "Active"

    def test_confidence_preserved_in_regression_record(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b013", confidence="0.3200")
        _make_fact(tmp_path, "b013")
        op = Operator()
        result = op.execute(path)
        assert "0.3200" in result["updated_fact_sections"]["Regression Record"]

    def test_fact_regression_record_contains_belief_ref(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b014")
        _make_fact(tmp_path, "b014")
        op = Operator()
        result = op.execute(path)
        assert "b014" in result["updated_fact_sections"]["Regression Record"]

    def test_fact_path_is_correct(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b015")
        _make_fact(tmp_path, "b015")
        op = Operator()
        result = op.execute(path)
        assert result["fact_path"] == Path("FACTS/fact-b015.md")


# ---------------------------------------------------------------------------
# Change History accumulation
# ---------------------------------------------------------------------------

class TestChangeHistoryAccumulation:
    def test_fact_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b020")
        _make_fact(tmp_path, "b020", history="- 2026-07-15: Promoted.")
        op = Operator()
        result = op.execute(path)
        history = result["updated_fact_sections"]["Change History"]
        assert "2026-07-15: Promoted" in history
        assert "Regressed" in history

    def test_belief_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(
            tmp_path, "b021",
            history="- 2026-07-15: Created.\n- 2026-07-16: Regression Pending."
        )
        _make_fact(tmp_path, "b021")
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "Created" in history
        assert "restored to Active" in history

    def test_fact_history_created_from_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b022")
        _make_fact(tmp_path, "b022", history="")
        op = Operator()
        result = op.execute(path)
        history = result["updated_fact_sections"]["Change History"]
        assert "Regressed" in history
        assert history.startswith("- ")


# ---------------------------------------------------------------------------
# persist() writes files
# ---------------------------------------------------------------------------

class TestPersist:
    def test_fact_file_updated(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b030")
        _make_fact(tmp_path, "b030")
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        fact_sections = em.load_entity(tmp_path / "FACTS" / "fact-b030.md")
        assert fact_sections["Epistemic State"] == "Regressed"

    def test_belief_file_updated(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b031")
        _make_fact(tmp_path, "b031")
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        belief_sections = em.load_entity(path)
        assert belief_sections["Epistemic State"] == "Active"

    def test_persist_returns_fact_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b032")
        _make_fact(tmp_path, "b032")
        op = Operator()
        result = op.execute(path)
        returned = op.persist(result)
        assert returned == Path("FACTS/fact-b032.md")


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------

class TestEventEmission:
    def test_fact_regressed_event_emitted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b040")
        _make_fact(tmp_path, "b040")
        bus = MagicMock()
        bus.emit.return_value = {"event": "FactRegressed"}
        op = Operator(event_bus=bus)
        result = op.execute(path)
        events = op.emit_events(result)
        bus.emit.assert_called_once_with(
            "FactRegressed",
            "Operator",
            str(Path("FACTS/fact-b040.md")),
        )
        assert len(events) == 1

    def test_no_event_without_event_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "b041")
        _make_fact(tmp_path, "b041")
        op = Operator()
        result = op.execute(path)
        events = op.emit_events(result)
        assert events == []


# ---------------------------------------------------------------------------
# End-to-end: Evidence -> Belief -> Fact -> Regression
# ---------------------------------------------------------------------------

class TestEndToEndRegressionArc:
    def test_full_arc(self, tmp_path, monkeypatch):
        """Evidence -> Belief -> Fact (promotion) -> Evidence -> Regression."""
        monkeypatch.chdir(tmp_path)

        # Step 1: create a Belief in Active state at promotion-level confidence.
        belief_path = tmp_path / "BELIEFS" / "arc-belief.md"
        belief_path.parent.mkdir(parents=True, exist_ok=True)
        belief_sections = OrderedDict([
            ("Identity", "arc-belief"),
            ("Claim", "The arc is complete."),
            ("Confidence", "0.8500"),
            ("Epistemic State", "Active"),
            ("Current State", "Active"),
            ("Supporting Evidence", "None."),
            ("Conflicting Evidence", "None."),
            ("Change History", "- 2026-07-16: Created."),
            ("Last Updated", "2026-07-16"),
        ])
        em.save_entity(belief_path, belief_sections)

        # Step 2: promote to Fact via BeliefToFact.
        from OPERATORS.BeliefToFact.operator import Operator as B2F
        b2f = B2F()
        b2f_result = b2f.execute(belief_path)
        b2f.persist(b2f_result)
        fact_path = tmp_path / "FACTS" / "fact-arc-belief.md"
        assert fact_path.exists()
        fact_s = em.load_entity(fact_path)
        assert fact_s["Epistemic State"] == "Promoted"

        # Step 3: apply contradicting Evidence that triggers Regression Pending.
        ev_path = tmp_path / "EPISTEMIC_EVIDENCE" / "ev-arc-001.md"
        ev_path.parent.mkdir(parents=True, exist_ok=True)
        ev_sections = OrderedDict([
            ("Identity", "ev-arc-001"),
            ("Valence", "Contradicting"),
            ("Strength", "0.45"),
            ("Linked Belief", str(belief_path)),
            ("Current State", "Pending"),
            ("Change History", ""),
            ("Last Updated", "2026-07-16"),
        ])
        em.save_entity(ev_path, ev_sections)

        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETB
        etb = ETB()
        etb_result = etb.execute(ev_path)
        etb.persist(etb_result)

        # Belief should now be Regression Pending.
        belief_s = em.load_entity(belief_path)
        assert belief_s["Epistemic State"] == "Regression Pending"

        # Step 4: apply BeliefRegression.
        op = Operator()
        reg_result = op.execute(belief_path)
        op.persist(reg_result)

        # Assert Fact is Regressed.
        fact_s2 = em.load_entity(fact_path)
        assert fact_s2["Epistemic State"] == "Regressed"
        assert fact_s2["Current State"] == "Regressed"
        assert "Regression Record" in fact_s2

        # Assert Belief is restored to Active.
        belief_s2 = em.load_entity(belief_path)
        assert belief_s2["Epistemic State"] == "Active"
        assert belief_s2["Current State"] == "Active"

        # Assert Change History on both is cumulative.
        assert "Regressed" in fact_s2["Change History"]
        assert "restored to Active" in belief_s2["Change History"]
