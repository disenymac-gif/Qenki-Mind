"""Tests for the BeliefArchival operator.

Covers:
- Happy path with corresponding Fact present
- Happy path with no corresponding Fact (Belief only)
- BeliefAlreadyArchivedError idempotent guard
- Change History accumulation on Belief
- Change History accumulation on Fact when co-archived
- previous_state captured correctly for all input states
- Belief-only persist writes correct Epistemic State
- Fact co-archived: persist writes 'Archived' on Fact
- persist returns belief_path
- BeliefArchived event emitted always
- FactArchived event emitted only when Fact exists
- No events when no EventBus
- E2E full arc: Learning -> Belief -> Fact -> Archival
- E2E Regression -> Archival arc
"""
from __future__ import annotations

import pytest
from pathlib import Path
from collections import OrderedDict
from unittest.mock import MagicMock

from OPERATORS.BeliefArchival.operator import (
    Operator,
    BeliefAlreadyArchivedError,
    _derive_fact_path,
)
import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_belief(tmp_path, stem, epistemic_state="Active",
                 confidence="0.7500", history=""):
    path = tmp_path / "BELIEFS" / f"{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", stem),
        ("Claim", f"Test claim for {stem}."),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Current State", epistemic_state),
        ("Supporting Evidence", "None."),
        ("Conflicting Evidence", "None."),
        ("Change History", history),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_fact(tmp_path, stem, epistemic_state="Promoted", history=""):
    path = tmp_path / "FACTS" / f"fact-{stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", f"fact-{stem}"),
        ("Claim", f"Test claim for fact-{stem}."),
        ("Confidence", "0.8500"),
        ("Epistemic State", epistemic_state),
        ("Current State", epistemic_state),
        ("Source Belief", f"BELIEFS/{stem}.md"),
        ("Promotion Record", f"Promoted on 2026-07-16 by BeliefToFact."),
        ("Change History", history),
        ("Last Updated", "2026-07-16"),
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


# ---------------------------------------------------------------------------
# validate() guard
# ---------------------------------------------------------------------------

class TestValidateGuard:
    def test_raises_if_already_archived(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a001", epistemic_state="Archived")
        op = Operator()
        with pytest.raises(BeliefAlreadyArchivedError, match="already Archived"):
            op.validate(path)

    def test_passes_for_active(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a002", epistemic_state="Active")
        op = Operator()
        assert op.validate(path) is True

    def test_passes_for_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a003", epistemic_state="Promoted")
        op = Operator()
        assert op.validate(path) is True

    def test_passes_for_regressed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a004", epistemic_state="Regressed")
        op = Operator()
        assert op.validate(path) is True

    def test_passes_for_regression_pending(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a005", epistemic_state="Regression Pending")
        op = Operator()
        assert op.validate(path) is True

    def test_passes_for_conflicted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a006", epistemic_state="Conflicted")
        op = Operator()
        assert op.validate(path) is True


# ---------------------------------------------------------------------------
# execute() — Belief only (no corresponding Fact)
# ---------------------------------------------------------------------------

class TestExecuteBeliefOnly:
    def test_belief_state_archived(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a010")
        op = Operator()
        result = op.execute(path)
        assert result["updated_belief_sections"]["Epistemic State"] == "Archived"
        assert result["updated_belief_sections"]["Current State"] == "Archived"

    def test_has_fact_false_when_no_fact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a011")
        op = Operator()
        result = op.execute(path)
        assert result["has_fact"] is False
        assert result["updated_fact_sections"] is None
        assert result["fact_path"] is None

    def test_previous_state_captured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a012", epistemic_state="Regressed")
        op = Operator()
        result = op.execute(path)
        assert result["previous_state"] == "Regressed"

    def test_history_entry_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a013",
                            history="- 2026-07-15: Created.")
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "2026-07-15: Created" in history
        assert "Archived" in history

    def test_history_created_from_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a014", history="")
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "Archived" in history
        assert history.startswith("- ")


# ---------------------------------------------------------------------------
# execute() — with corresponding Fact
# ---------------------------------------------------------------------------

class TestExecuteWithFact:
    def test_has_fact_true(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a020")
        _make_fact(tmp_path, "a020")
        op = Operator()
        result = op.execute(path)
        assert result["has_fact"] is True

    def test_fact_state_archived(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a021")
        _make_fact(tmp_path, "a021")
        op = Operator()
        result = op.execute(path)
        assert result["updated_fact_sections"]["Epistemic State"] == "Archived"
        assert result["updated_fact_sections"]["Current State"] == "Archived"

    def test_fact_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a022")
        _make_fact(tmp_path, "a022", history="- 2026-07-15: Promoted.")
        op = Operator()
        result = op.execute(path)
        history = result["updated_fact_sections"]["Change History"]
        assert "2026-07-15: Promoted" in history
        assert "Archived" in history

    def test_belief_history_references_fact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a023")
        _make_fact(tmp_path, "a023")
        op = Operator()
        result = op.execute(path)
        history = result["updated_belief_sections"]["Change History"]
        assert "fact-a023" in history


# ---------------------------------------------------------------------------
# persist()
# ---------------------------------------------------------------------------

class TestPersist:
    def test_belief_written_archived(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a030")
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        sections = em.load_entity(path)
        assert sections["Epistemic State"] == "Archived"

    def test_fact_written_archived_when_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a031")
        fact_path = _make_fact(tmp_path, "a031")
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        fact_s = em.load_entity(fact_path)
        assert fact_s["Epistemic State"] == "Archived"

    def test_persist_returns_belief_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a032")
        op = Operator()
        result = op.execute(path)
        returned = op.persist(result)
        assert returned == path

    def test_persist_no_fact_file_not_created(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a033")
        op = Operator()
        result = op.execute(path)
        op.persist(result)
        fact_path = tmp_path / "FACTS" / "fact-a033.md"
        assert not fact_path.exists()


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------

class TestEventEmission:
    def test_belief_archived_event_always(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a040")
        bus = MagicMock()
        bus.emit.return_value = {"event": "ok"}
        op = Operator(event_bus=bus)
        result = op.execute(path)
        events = op.emit_events(result)
        calls = [c.args[0] for c in bus.emit.call_args_list]
        assert "BeliefArchived" in calls
        assert len(events) == 1

    def test_fact_archived_event_when_fact_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a041")
        _make_fact(tmp_path, "a041")
        bus = MagicMock()
        bus.emit.return_value = {"event": "ok"}
        op = Operator(event_bus=bus)
        result = op.execute(path)
        events = op.emit_events(result)
        calls = [c.args[0] for c in bus.emit.call_args_list]
        assert "BeliefArchived" in calls
        assert "FactArchived" in calls
        assert len(events) == 2

    def test_no_fact_archived_event_without_fact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a042")
        bus = MagicMock()
        bus.emit.return_value = {"event": "ok"}
        op = Operator(event_bus=bus)
        result = op.execute(path)
        events = op.emit_events(result)
        calls = [c.args[0] for c in bus.emit.call_args_list]
        assert "FactArchived" not in calls
        assert len(events) == 1

    def test_no_events_without_event_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        path = _make_belief(tmp_path, "a043")
        op = Operator()
        result = op.execute(path)
        events = op.emit_events(result)
        assert events == []


# ---------------------------------------------------------------------------
# E2E: Learning -> Belief -> Fact -> Archival
# ---------------------------------------------------------------------------

class TestEndToEndArchivalArc:
    def test_promotion_then_archival(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        # Create Belief at promotion-level confidence.
        belief_path = tmp_path / "BELIEFS" / "arc-archival.md"
        belief_path.parent.mkdir(parents=True, exist_ok=True)
        belief_sections = OrderedDict([
            ("Identity", "arc-archival"),
            ("Claim", "This belief will be archived after promotion."),
            ("Confidence", "0.9000"),
            ("Epistemic State", "Active"),
            ("Current State", "Active"),
            ("Supporting Evidence", "None."),
            ("Conflicting Evidence", "None."),
            ("Change History", "- 2026-07-16: Created."),
            ("Last Updated", "2026-07-16"),
        ])
        em.save_entity(belief_path, belief_sections)

        # Promote to Fact.
        from OPERATORS.BeliefToFact.operator import Operator as B2F
        b2f = B2F()
        b2f.persist(b2f.execute(belief_path))
        fact_path = tmp_path / "FACTS" / "fact-arc-archival.md"
        assert fact_path.exists()

        # Archive.
        op = Operator()
        result = op.execute(belief_path)
        op.persist(result)

        belief_s = em.load_entity(belief_path)
        assert belief_s["Epistemic State"] == "Archived"

        fact_s = em.load_entity(fact_path)
        assert fact_s["Epistemic State"] == "Archived"

        # History on Belief must mention co-archival of Fact.
        assert "fact-arc-archival" in belief_s["Change History"]

    def test_regression_then_archival(self, tmp_path, monkeypatch):
        """Belief that went through regression is archivable."""
        monkeypatch.chdir(tmp_path)

        belief_path = tmp_path / "BELIEFS" / "arc-regression.md"
        belief_path.parent.mkdir(parents=True, exist_ok=True)
        belief_sections = OrderedDict([
            ("Identity", "arc-regression"),
            ("Claim", "A regressed belief that gets archived."),
            ("Confidence", "0.3000"),
            ("Epistemic State", "Active"),
            ("Current State", "Active"),
            ("Supporting Evidence", "None."),
            ("Conflicting Evidence", "None."),
            ("Change History", "- 2026-07-16: Created."),
            ("Last Updated", "2026-07-16"),
        ])
        em.save_entity(belief_path, belief_sections)

        # Create a Fact manually to simulate prior promotion+regression cycle.
        fact_path = tmp_path / "FACTS" / "fact-arc-regression.md"
        fact_path.parent.mkdir(parents=True, exist_ok=True)
        fact_sections = OrderedDict([
            ("Identity", "fact-arc-regression"),
            ("Claim", "Regressed fact."),
            ("Confidence", "0.3000"),
            ("Epistemic State", "Regressed"),
            ("Current State", "Regressed"),
            ("Source Belief", str(belief_path)),
            ("Promotion Record", "Promoted on 2026-07-15."),
            ("Change History", "- 2026-07-16: Regressed."),
            ("Last Updated", "2026-07-16"),
        ])
        em.save_entity(fact_path, fact_sections)

        # Set Belief to Active (post-regression state).
        reloaded = em.load_entity(belief_path)
        reloaded["Epistemic State"] = "Active"
        reloaded["Current State"] = "Active"
        em.save_entity(belief_path, reloaded)

        op = Operator()
        result = op.execute(belief_path)
        op.persist(result)

        assert em.load_entity(belief_path)["Epistemic State"] == "Archived"
        assert em.load_entity(fact_path)["Epistemic State"] == "Archived"
