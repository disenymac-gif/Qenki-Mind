"""
Test suite for BeliefToFact operator.

Coverage:
  PASS  validate — accepts eligible Belief; raises AlreadyPromotedError,
        ConflictedBeliefError, BelowPromotionThresholdError
  PASS  execute  — Fact identity, claim, confidence, state, sections;
        updated Belief sections; promotion record; threshold used
  PASS  persist  — creates FACTS/*.md; updates BELIEFS/*.md state;
        idempotent guard via AlreadyPromotedError
  PASS  emit_events — emits FactPromoted with bus, empty without bus
  PASS  _load_threshold — reads from parameter file; falls back to default
  PASS  full cycle — validate -> execute -> persist -> emit_events
  PASS  default_registry — BeliefToFact registered as eighth operator
  PASS  fact entity schema — all required sections present
  PASS  engine dispatch — CognitiveEngine.run() can call BeliefToFact
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_belief_entity(
    path: Path,
    confidence: str = "0.85",
    epistemic_state: str = "Active",
    claim: str = "Confirmed pattern: engagement drives quality.",
    supporting_evidence: str = "- [pred-001|confirmed] Outcome quality was high.",
) -> Path:
    """Write a minimal canonical Belief entity to `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership",
         "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", str(path)),
        ("Claim", claim),
        ("Confidence", confidence),
        ("Epistemic State", epistemic_state),
        ("Epistemic Completeness", "Partial."),
        ("Source Learning", "LEARNING/learning-001.md"),
        ("Supporting Evidence", supporting_evidence),
        ("Conflicting Evidence", "None recorded."),
        ("Links", f"- {path}\n- BELIEFS/README.md"),
        ("Current State", epistemic_state),
        ("Change History", "- 2026-07-16: Created for testing."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_parameter_file(tmp_path: Path, threshold: str = "0.80") -> Path:
    """Write a minimal belief_fact_promotion.md to the expected location."""
    param_dir = tmp_path / "REASONING_PARAMETERS"
    param_dir.mkdir(parents=True, exist_ok=True)
    param_path = param_dir / "belief_fact_promotion.md"
    content = (
        "# Reasoning Parameter: Belief-to-Fact Promotion\n\n"
        "## Identity\nName: Belief-to-Fact Promotion\n\n"
        "## Current Value\n\n"
        f"### promotion_threshold\n{threshold}\n\n"
        "## Change History\n- 2026-07-16: Initial calibration.\n"
    )
    param_path.write_text(content, encoding="utf-8")
    return param_path


_REQUIRED_FACT_SECTIONS = [
    "Identity",
    "Ownership",
    "Canonical Basis",
    "Claim",
    "Confidence",
    "Epistemic State",
    "Source Belief",
    "Supporting Evidence",
    "Promotion Record",
    "Links",
    "Current State",
    "Change History",
    "Last Updated",
]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_belief_to_fact_registered_as_eighth_operator(self):
        from OPERATORS import default_registry
        available = default_registry.available()
        assert "BeliefToFact" in available
        assert len(available) == 8

    def test_build_engine_has_eight_operators(self):
        from OPERATORS import build_engine
        engine = build_engine()
        assert len(engine.registry.available()) == 8


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_accepts_eligible_belief(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-valid.md",
            confidence="0.90",
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        assert op.validate(src) is True

    def test_raises_already_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-promoted.md",
            confidence="0.90",
            epistemic_state="Promoted",
        )
        from OPERATORS.BeliefToFact.operator import Operator, AlreadyPromotedError
        op = Operator()
        with pytest.raises(AlreadyPromotedError):
            op.validate(src)

    def test_raises_conflicted_belief(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-conflicted.md",
            confidence="0.95",
            epistemic_state="Conflicted",
        )
        from OPERATORS.BeliefToFact.operator import Operator, ConflictedBeliefError
        op = Operator()
        with pytest.raises(ConflictedBeliefError):
            op.validate(src)

    def test_raises_below_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path, threshold="0.80")
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-low.md",
            confidence="0.50",
        )
        from OPERATORS.BeliefToFact.operator import Operator, BelowPromotionThresholdError
        op = Operator()
        with pytest.raises(BelowPromotionThresholdError):
            op.validate(src)

    def test_accepts_confidence_exactly_at_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path, threshold="0.80")
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-boundary.md",
            confidence="0.80",
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        assert op.validate(src) is True


# ---------------------------------------------------------------------------
# _load_threshold
# ---------------------------------------------------------------------------

class TestLoadThreshold:
    def test_reads_threshold_from_parameter_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path, threshold="0.75")
        from OPERATORS.BeliefToFact.operator import _load_threshold
        assert _load_threshold() == pytest.approx(0.75)

    def test_falls_back_to_default_when_file_absent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        from OPERATORS.BeliefToFact.operator import _load_threshold, PROMOTION_THRESHOLD_DEFAULT
        assert _load_threshold() == pytest.approx(PROMOTION_THRESHOLD_DEFAULT)

    def test_falls_back_to_default_for_uncalibrated_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        param_dir = tmp_path / "REASONING_PARAMETERS"
        param_dir.mkdir()
        (param_dir / "belief_fact_promotion.md").write_text(
            "# Reasoning Parameter\n\n## Current Value\nNot yet calibrated.\n",
            encoding="utf-8",
        )
        from OPERATORS.BeliefToFact.operator import _load_threshold, PROMOTION_THRESHOLD_DEFAULT
        assert _load_threshold() == pytest.approx(PROMOTION_THRESHOLD_DEFAULT)


# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------

class TestExecute:
    def test_fact_identity_derived_from_belief_stem(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-alpha.md",
            confidence="0.88",
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["fact_sections"]["Identity"] == "fact-belief-alpha"

    def test_claim_transferred_from_belief(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-claim.md",
            confidence="0.90",
            claim="Sustained engagement correlates with outcome quality.",
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert "Sustained engagement" in result["fact_sections"]["Claim"]

    def test_fact_epistemic_state_is_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-state.md", confidence="0.85"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["fact_sections"]["Epistemic State"] == "Promoted"
        assert result["fact_sections"]["Current State"] == "Promoted"

    def test_promotion_record_contains_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path, threshold="0.80")
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-record.md", confidence="0.85"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        record = result["fact_sections"]["Promotion Record"]
        assert "0.80" in record or "0.8" in record

    def test_updated_belief_sections_epistemic_state_is_promoted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-update.md", confidence="0.85"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["updated_belief_sections"]["Epistemic State"] == "Promoted"

    def test_updated_belief_history_appended(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-history.md", confidence="0.85"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        history = result["updated_belief_sections"]["Change History"]
        assert "Promoted" in history
        assert "BeliefToFact" in history

    def test_fact_path_targets_facts_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-path.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert Path(result["fact_path"]).parent.name == "FACTS"

    def test_all_required_sections_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-schema.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        for section in _REQUIRED_FACT_SECTIONS:
            assert section in result["fact_sections"], f"Missing: '{section}'"


# ---------------------------------------------------------------------------
# persist
# ---------------------------------------------------------------------------

class TestPersist:
    def test_creates_fact_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-persist.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.parent.name == "FACTS"
        assert artifact.name == "fact-belief-persist.md"

    def test_updates_source_belief_epistemic_state(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-updated.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        op.persist(result)
        reloaded = em.load_entity(src)
        assert reloaded["Epistemic State"] == "Promoted"

    def test_persisted_fact_has_all_required_sections(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-sections.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        for section in _REQUIRED_FACT_SECTIONS:
            assert section in loaded, f"Persisted file missing: '{section}'"

    def test_fact_confidence_is_parseable_float(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-float.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        confidence = float(loaded["Confidence"])
        assert 0.0 <= confidence <= 1.0

    def test_creates_facts_directory_if_absent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        assert not (tmp_path / "FACTS").exists()
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-mkdir.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        op.persist(result)
        assert (tmp_path / "FACTS").exists()

    def test_claim_survives_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-roundtrip.md",
            confidence="0.90",
            claim="Roundtrip claim must survive fact promotion.",
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        assert "Roundtrip claim must survive fact promotion." in loaded["Claim"]


# ---------------------------------------------------------------------------
# emit_events
# ---------------------------------------------------------------------------

class TestEmitEvents:
    def test_emits_fact_promoted_event_with_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-emit.md", confidence="0.88"
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-fact-001", "type": "FactPromoted"}
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(src)
        events = op.emit_events(result)
        assert len(events) == 1
        call_args = bus.emit.call_args
        event_type = call_args[1].get("event_type") or call_args[0][0]
        assert event_type == "FactPromoted"

    def test_returns_empty_list_without_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-nobus.md", confidence="0.88"
        )
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute(src)
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# Full cycle
# ---------------------------------------------------------------------------

class TestFullCycle:
    def test_full_cycle_validate_execute_persist_emit(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-fullcycle.md",
            confidence="0.92",
            claim="Full cycle claim promoted to Fact.",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-full-fact-001"}
        from OPERATORS.BeliefToFact.operator import Operator
        op = Operator(event_bus=bus)

        assert op.validate(src) is True
        result = op.execute(src)
        assert result["fact_sections"]["Epistemic State"] == "Promoted"
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.parent.name == "FACTS"
        reloaded_belief = em.load_entity(src)
        assert reloaded_belief["Epistemic State"] == "Promoted"
        events = op.emit_events(result)
        assert len(events) == 1

    def test_second_validate_after_persist_raises_already_promoted(self, tmp_path, monkeypatch):
        """After persist, re-validating the same Belief raises AlreadyPromotedError."""
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-idempotent.md", confidence="0.90"
        )
        from OPERATORS.BeliefToFact.operator import Operator, AlreadyPromotedError
        op = Operator()
        result = op.execute(src)
        op.persist(result)
        with pytest.raises(AlreadyPromotedError):
            op.validate(src)

    def test_engine_run_belief_to_fact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _make_parameter_file(tmp_path)
        src = _make_belief_entity(
            tmp_path / "BELIEFS" / "belief-engine.md",
            confidence="0.88",
            claim="Engine-dispatched fact promotion.",
        )
        from OPERATORS import build_engine
        from OPERATORS.engine import CognitiveSession
        engine = build_engine()
        session = CognitiveSession(trigger="test", root_entity=str(src))
        artifact = engine.run("BeliefToFact", src, session=session)
        assert artifact.exists()
        assert artifact.parent.name == "FACTS"
        assert "BeliefToFact" in session.operators_executed
