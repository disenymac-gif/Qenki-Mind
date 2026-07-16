"""
Test suite for LearningToBelief operator.

Coverage:
  PASS  validate — accepts valid entity, raises on empty Learning section
  PASS  execute  — Belief identity, claim extraction, confidence, state, sections
  PASS  persist  — creates BELIEFS/*.md with canonical section order
  PASS  persist  — idempotent re-execution (overwrite, not duplicate)
  PASS  emit_events — emits BeliefCreated with bus, empty without bus
  PASS  full cycle — validate -> execute -> persist -> emit_events
  PASS  default_registry — LearningToBelief registered as seventh operator
  PASS  belief entity schema — all required sections present
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_learning_entity(
    path: Path,
    learning_text: str = "- Confirmed pattern: sustained engagement correlates with outcome quality.",
) -> Path:
    """Write a minimal canonical Learning entity to `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by Learning & Reflection."),
        ("Canonical Basis", str(path)),
        ("Context", "Weekly reflection cycle, 2026-07-16."),
        ("Hypotheses", "- Hypothesis alpha: engagement predicts quality."),
        ("Predictions", "- [pred-001|confirmed] Outcome quality was high."),
        ("Consequences", "None inherited."),
        ("Learning", learning_text),
        ("Links", f"- {path}"),
        ("Current State", "Active"),
        ("Change History", "- 2026-07-16: Created for testing."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


_REQUIRED_BELIEF_SECTIONS = [
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


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_learning_to_belief_registered_as_seventh_operator(self):
        from OPERATORS import default_registry
        available = default_registry.available()
        assert "LearningToBelief" in available
        assert len(available) == 7

    def test_build_engine_has_seven_operators(self):
        from OPERATORS import build_engine
        engine = build_engine()
        assert len(engine.registry.available()) == 7


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_accepts_entity_with_learning_content(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-valid.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        assert op.validate(src) is True

    def test_raises_on_empty_learning_section(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-empty.md",
            learning_text="",
        )
        from OPERATORS.LearningToBelief.operator import Operator, NoUsableLearningError
        op = Operator()
        with pytest.raises(NoUsableLearningError):
            op.validate(src)

    def test_raises_on_whitespace_only_learning_section(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-whitespace.md",
            learning_text="   \n  ",
        )
        from OPERATORS.LearningToBelief.operator import Operator, NoUsableLearningError
        op = Operator()
        with pytest.raises(NoUsableLearningError):
            op.validate(src)


# ---------------------------------------------------------------------------
# execute
# ---------------------------------------------------------------------------

class TestExecute:
    def test_belief_identity_derived_from_source_stem(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-alpha.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Identity"] == "belief-learning-alpha"

    def test_belief_id_key_present_in_result(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-beta.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["belief_id"] == "belief-learning-beta"

    def test_claim_extracted_from_first_bullet(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-claim.md",
            learning_text="- First claim extracted here.\n- Second claim ignored.",
        )
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Claim"] == "First claim extracted here."

    def test_claim_extracted_from_plain_text(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-plaintext.md",
            learning_text="Engagement drives quality.",
        )
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Claim"] == "Engagement drives quality."

    def test_confidence_initialised_at_neutral(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-conf.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Confidence"] == "0.50"

    def test_epistemic_state_initialised_as_active(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-state.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Epistemic State"] == "Active"
        assert result["sections"]["Current State"] == "Active"

    def test_epistemic_completeness_flags_partial(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-partial.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        completeness = result["sections"]["Epistemic Completeness"]
        assert "Partial" in completeness

    def test_source_learning_records_origin_path(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-origin.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert str(src) in result["sections"]["Source Learning"]

    def test_output_path_targets_beliefs_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-gamma.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert Path(result["path"]).parent.name == "BELIEFS"

    def test_conflicting_evidence_initialised_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-conflict.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Conflicting Evidence"] == "None recorded."

    def test_change_history_records_initialisation(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-history.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        history = result["sections"]["Change History"]
        assert "Initialised by LearningToBelief" in history

    def test_all_required_sections_present_in_result(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-schema.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        for section in _REQUIRED_BELIEF_SECTIONS:
            assert section in result["sections"], f"Missing required section: '{section}'"


# ---------------------------------------------------------------------------
# persist
# ---------------------------------------------------------------------------

class TestPersist:
    def test_creates_belief_file_in_beliefs_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-persist.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.parent.name == "BELIEFS"
        assert artifact.name == "belief-learning-persist.md"

    def test_persisted_file_has_all_required_sections(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-sections.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        for section in _REQUIRED_BELIEF_SECTIONS:
            assert section in loaded, f"Persisted file missing section: '{section}'"

    def test_persisted_confidence_is_parseable_float(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-float.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        confidence = float(loaded["Confidence"])
        assert 0.0 <= confidence <= 1.0

    def test_persist_is_idempotent(self, tmp_path, monkeypatch):
        """Re-running persist on the same source must overwrite, not duplicate."""
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-idem.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact1 = op.persist(result)
        artifact2 = op.persist(result)
        assert artifact1 == artifact2
        # Directory must contain exactly one file for this belief.
        belief_files = list((tmp_path / "BELIEFS").glob("belief-learning-idem.md"))
        assert len(belief_files) == 1

    def test_persist_creates_beliefs_directory_if_absent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / "BELIEFS").exists()
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-mkdir.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        op.persist(result)
        assert (tmp_path / "BELIEFS").exists()

    def test_claim_content_survives_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-roundtrip.md",
            learning_text="- Roundtrip claim must survive serialisation.",
        )
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        loaded = em.load_entity(artifact)
        assert "Roundtrip claim must survive serialisation." in loaded["Claim"]


# ---------------------------------------------------------------------------
# emit_events
# ---------------------------------------------------------------------------

class TestEmitEvents:
    def test_emits_belief_created_event_with_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-emit.md")
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-belief-001", "type": "BeliefCreated"}
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(src)
        events = op.emit_events(result)
        assert len(events) == 1
        call_args = bus.emit.call_args
        event_type = call_args[1].get("event_type") or call_args[0][0]
        assert event_type == "BeliefCreated"

    def test_returns_empty_list_without_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "LEARNING" / "learning-nobus.md")
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute(src)
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# Full cycle
# ---------------------------------------------------------------------------

class TestFullCycle:
    def test_full_cycle_validate_execute_persist_emit(self, tmp_path, monkeypatch):
        """validate -> execute -> persist -> emit_events, happy path."""
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-fullcycle.md",
            learning_text="- Full cycle claim verified end-to-end.",
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-full-belief-001"}
        from OPERATORS.LearningToBelief.operator import Operator
        op = Operator(event_bus=bus)

        assert op.validate(src) is True
        result = op.execute(src)
        assert result["sections"]["Epistemic State"] == "Active"
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.parent.name == "BELIEFS"
        events = op.emit_events(result)
        assert len(events) == 1

    def test_engine_run_learning_to_belief(self, tmp_path, monkeypatch):
        """CognitiveEngine.run() can dispatch LearningToBelief by name."""
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(
            tmp_path / "LEARNING" / "learning-engine.md",
            learning_text="- Engine-dispatched belief.",
        )
        from OPERATORS import build_engine
        from OPERATORS.engine import CognitiveSession
        engine = build_engine()
        session = CognitiveSession(trigger="test", root_entity=str(src))
        artifact = engine.run("LearningToBelief", src, session=session)
        assert artifact.exists()
        assert artifact.parent.name == "BELIEFS"
        assert "LearningToBelief" in session.operators_executed
