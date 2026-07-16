"""
Test suite for EvidenceToBeliefUpdate operator.

Coverage:
  PASS  validate — accepts eligible Evidence; raises AlreadyAppliedError,
        NeutralEvidenceSkippedInfo, LinkedBeliefNotFoundError
  PASS  execute  — Supporting: confidence increases, Supporting Evidence appended
  PASS  execute  — Contradicting: confidence decreases, Conflicting Evidence appended
  PASS  execute  — confidence clamped to [0.0, 1.0]
  PASS  execute  — regression_pending flag set when confidence drops below threshold
  PASS  execute  — Belief Epistemic State set to 'Regression Pending' when triggered
  PASS  execute  — Evidence Current State set to 'Applied'
  PASS  execute  — Change History appended to both entities
  PASS  persist  — Belief file updated on disk
  PASS  persist  — Evidence file Current State 'Applied' on disk
  PASS  persist  — idempotent guard: second validate raises AlreadyAppliedError
  PASS  emit_events — emits BeliefConfidenceUpdated always; BeliefRegressionPending when regression
  PASS  emit_events — returns empty list without bus
  PASS  full cycle — validate -> execute -> persist -> emit_events
  PASS  registry  — EvidenceToBeliefUpdate registered as ninth operator
  PASS  engine dispatch — CognitiveEngine.run() can call EvidenceToBeliefUpdate
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_belief(
    path: Path,
    confidence: str = "0.60",
    epistemic_state: str = "Active",
    claim: str = "Test claim.",
    supporting_evidence: str = "None recorded.",
    conflicting_evidence: str = "None recorded.",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", str(path)),
        ("Claim", claim),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Epistemic Completeness", "Partial."),
        ("Source Learning", "LEARNING/learning-test.md"),
        ("Supporting Evidence", supporting_evidence),
        ("Conflicting Evidence", conflicting_evidence),
        ("Links", f"- {path}\n- BELIEFS/README.md"),
        ("Current State", epistemic_state),
        ("Change History", "- 2026-07-16: Created for testing."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_evidence(
    path: Path,
    linked_belief: Path,
    valence: str = "Supporting",
    strength: str = "0.10",
    current_state: str = "Pending",
    claim: str = "Test claim.",
    source: str = "source-alpha",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", "LEARNING/learning-test.md"),
        ("Claim", claim),
        ("Valence", valence),
        ("Strength", strength),
        ("Source", source),
        ("Linked Belief", str(linked_belief)),
        ("Current State", current_state),
        ("Change History", "- 2026-07-16: Created for testing."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_promotion_param_file(tmp_path: Path, regression_threshold: str = "0.50") -> Path:
    param_dir = tmp_path / "REASONING_PARAMETERS"
    param_dir.mkdir(parents=True, exist_ok=True)
    param_path = param_dir / "belief_fact_promotion.md"
    content = (
        "# Reasoning Parameter: Belief-to-Fact Promotion\n\n"
        "## Identity\nName: Belief-to-Fact Promotion\n\n"
        "## Current Value\n\n"
        "### promotion_threshold\n0.80\n\n"
        f"### regression_threshold\n{regression_threshold}\n\n"
        "## Change History\n- 2026-07-16: Initial calibration.\n"
    )
    param_path.write_text(content, encoding="utf-8")
    return param_path


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_evidence_to_belief_update_registered_as_ninth_operator(self):
        from OPERATORS import default_registry
        available = default_registry.available()
        assert "EvidenceToBeliefUpdate" in available
        assert len(available) == 9

    def test_build_engine_has_nine_operators(self):
        from OPERATORS import build_engine
        engine = build_engine()
        assert len(engine.registry.available()) == 9


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_accepts_pending_supporting_evidence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        belief = _make_belief(tmp_path / "BELIEFS" / "belief-a.md")
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-a.md",
            linked_belief=belief,
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        assert Operator().validate(ev) is True

    def test_raises_already_applied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        belief = _make_belief(tmp_path / "BELIEFS" / "belief-b.md")
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-b.md",
            linked_belief=belief,
            current_state="Applied",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator, AlreadyAppliedError
        with pytest.raises(AlreadyAppliedError):
            Operator().validate(ev)

    def test_raises_neutral_valence(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        belief = _make_belief(tmp_path / "BELIEFS" / "belief-c.md")
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-c.md",
            linked_belief=belief,
            valence="Neutral",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator, NeutralEvidenceSkippedInfo
        with pytest.raises(NeutralEvidenceSkippedInfo):
            Operator().validate(ev)

    def test_raises_linked_belief_not_found(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-d.md",
            linked_belief=tmp_path / "BELIEFS" / "nonexistent.md",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator, LinkedBeliefNotFoundError
        with pytest.raises(LinkedBeliefNotFoundError):
            Operator().validate(ev)


# ---------------------------------------------------------------------------
# execute — Supporting
# ---------------------------------------------------------------------------

class TestExecuteSupporting:
    def test_confidence_increases(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-sup.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-sup.md",
            linked_belief=belief, valence="Supporting", strength="0.15",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(0.75)

    def test_supporting_evidence_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-sup2.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-sup2.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert "evidence-sup2" in result["updated_belief_sections"]["Supporting Evidence"]

    def test_regression_pending_false_for_supporting(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-sup3.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-sup3.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["regression_pending"] is False


# ---------------------------------------------------------------------------
# execute — Contradicting
# ---------------------------------------------------------------------------

class TestExecuteContradicting:
    def test_confidence_decreases(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-con.md", confidence="0.70"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-con.md",
            linked_belief=belief, valence="Contradicting", strength="0.15",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(0.55)

    def test_conflicting_evidence_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-con2.md", confidence="0.70"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-con2.md",
            linked_belief=belief, valence="Contradicting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert "evidence-con2" in result["updated_belief_sections"]["Conflicting Evidence"]

    def test_regression_pending_set_when_below_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path, regression_threshold="0.50")
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-reg.md", confidence="0.55"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-reg.md",
            linked_belief=belief, valence="Contradicting", strength="0.10",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(0.45)
        assert result["regression_pending"] is True
        assert result["updated_belief_sections"]["Epistemic State"] == "Regression Pending"

    def test_regression_pending_false_just_above_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path, regression_threshold="0.50")
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-no-reg.md", confidence="0.65"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-no-reg.md",
            linked_belief=belief, valence="Contradicting", strength="0.10",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(0.55)
        assert result["regression_pending"] is False


# ---------------------------------------------------------------------------
# execute — clamping
# ---------------------------------------------------------------------------

class TestConfidenceClamping:
    def test_supporting_clamps_at_1(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-clamp-hi.md", confidence="0.95"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-clamp-hi.md",
            linked_belief=belief, valence="Supporting", strength="0.20",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(1.0)

    def test_contradicting_clamps_at_0(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-clamp-lo.md", confidence="0.05"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-clamp-lo.md",
            linked_belief=belief, valence="Contradicting", strength="0.20",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["new_confidence"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# execute — Change History
# ---------------------------------------------------------------------------

class TestChangeHistory:
    def test_belief_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-hist.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-hist.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        history = result["updated_belief_sections"]["Change History"]
        assert "EvidenceToBeliefUpdate" in history

    def test_evidence_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-ehist.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-ehist.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        history = result["updated_evidence_sections"]["Change History"]
        assert "Applied" in history

    def test_evidence_current_state_applied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-state.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-state.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        result = Operator().execute(ev)
        assert result["updated_evidence_sections"]["Current State"] == "Applied"


# ---------------------------------------------------------------------------
# persist
# ---------------------------------------------------------------------------

class TestPersist:
    def test_belief_confidence_updated_on_disk(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-persist.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-persist.md",
            linked_belief=belief, valence="Supporting", strength="0.15",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator()
        result = op.execute(ev)
        op.persist(result)
        reloaded = em.load_entity(belief)
        assert float(reloaded["Confidence"]) == pytest.approx(0.75)

    def test_evidence_state_applied_on_disk(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-ev-disk.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-ev-disk.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator()
        result = op.execute(ev)
        op.persist(result)
        reloaded_ev = em.load_entity(ev)
        assert reloaded_ev["Current State"] == "Applied"

    def test_second_validate_after_persist_raises_already_applied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-idem.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-idem.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator, AlreadyAppliedError
        op = Operator()
        result = op.execute(ev)
        op.persist(result)
        with pytest.raises(AlreadyAppliedError):
            op.validate(ev)


# ---------------------------------------------------------------------------
# emit_events
# ---------------------------------------------------------------------------

class TestEmitEvents:
    def test_emits_belief_confidence_updated_always(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-emit.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-emit.md",
            linked_belief=belief, valence="Supporting",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-001"}
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(ev)
        events = op.emit_events(result)
        assert len(events) == 1
        event_type = bus.emit.call_args_list[0][0][0]
        assert event_type == "BeliefConfidenceUpdated"

    def test_emits_regression_pending_event_when_triggered(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path, regression_threshold="0.50")
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-reg-evt.md", confidence="0.55"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-reg-evt.md",
            linked_belief=belief, valence="Contradicting", strength="0.10",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-002"}
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(ev)
        events = op.emit_events(result)
        assert len(events) == 2
        event_types = [call[0][0] for call in bus.emit.call_args_list]
        assert "BeliefRegressionPending" in event_types

    def test_returns_empty_without_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-nobus.md", confidence="0.60"
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-nobus.md",
            linked_belief=belief, valence="Supporting",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute(ev)
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# Full cycle
# ---------------------------------------------------------------------------

class TestFullCycle:
    def test_full_supporting_cycle(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-full.md",
            confidence="0.65",
            claim="Full cycle claim.",
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-full.md",
            linked_belief=belief, valence="Supporting", strength="0.15",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-full"}
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator(event_bus=bus)

        assert op.validate(ev) is True
        result = op.execute(ev)
        assert result["new_confidence"] == pytest.approx(0.80)
        artifact = op.persist(result)
        reloaded = em.load_entity(artifact)
        assert float(reloaded["Confidence"]) == pytest.approx(0.80)
        events = op.emit_events(result)
        assert len(events) == 1

    def test_full_contradicting_cycle_triggers_regression_pending(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path, regression_threshold="0.50")
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-contra-full.md",
            confidence="0.55",
            claim="Contra full cycle claim.",
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-contra-full.md",
            linked_belief=belief, valence="Contradicting", strength="0.10",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-contra"}
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator
        op = Operator(event_bus=bus)

        assert op.validate(ev) is True
        result = op.execute(ev)
        assert result["new_confidence"] == pytest.approx(0.45)
        assert result["regression_pending"] is True
        artifact = op.persist(result)
        reloaded_belief = em.load_entity(artifact)
        assert reloaded_belief["Epistemic State"] == "Regression Pending"
        events = op.emit_events(result)
        assert len(events) == 2

    def test_engine_dispatch_evidence_to_belief_update(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-engine.md",
            confidence="0.60",
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-engine.md",
            linked_belief=belief, valence="Supporting", strength="0.15",
        )
        from OPERATORS import build_engine
        from OPERATORS.engine import CognitiveSession
        engine = build_engine()
        session = CognitiveSession(trigger="test", root_entity=str(ev))
        artifact = engine.run("EvidenceToBeliefUpdate", ev, session=session)
        reloaded = em.load_entity(artifact)
        assert float(reloaded["Confidence"]) == pytest.approx(0.75)
        assert "EvidenceToBeliefUpdate" in session.operators_executed

    def test_evidence_then_belief_to_fact_pipeline(self, tmp_path, monkeypatch):
        """Evidence boosts Belief to >= 0.80, then BeliefToFact promotes it."""
        monkeypatch.chdir(tmp_path)
        _make_promotion_param_file(tmp_path)
        belief = _make_belief(
            tmp_path / "BELIEFS" / "belief-pipeline.md",
            confidence="0.72",
            claim="Pipeline integration claim.",
        )
        ev = _make_evidence(
            tmp_path / "EPISTEMIC_EVIDENCE" / "evidence-pipeline.md",
            linked_belief=belief, valence="Supporting", strength="0.15",
        )
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as E2BU
        from OPERATORS.BeliefToFact.operator import Operator as B2F

        # Step 1: apply evidence.
        e2bu = E2BU()
        assert e2bu.validate(ev) is True
        r1 = e2bu.execute(ev)
        assert r1["new_confidence"] == pytest.approx(0.87)
        e2bu.persist(r1)

        # Step 2: promote belief to fact.
        b2f = B2F()
        assert b2f.validate(belief) is True
        r2 = b2f.execute(belief)
        fact_path = b2f.persist(r2)
        assert fact_path.exists()
        assert fact_path.parent.name == "FACTS"
