"""
Integration test suite for Qenki-Mind cognitive operators.

Coverage:
  PASS  LearningToMemory       — full execute/persist/emit cycle
  PASS  MemoryToReasoning      — full execute/persist/emit cycle + session injection
  PASS  DecisionToExpression   — full execute/persist/emit cycle
  PASS  ExpressionToConsequence — full execute/persist/emit cycle
  PASS  ConsequenceToLearning  — full execute/persist/emit cycle
  PASS  OpportunityToDecision  — full execute/persist/emit cycle (selected + rejected paths)
  PASS  build_engine / default_registry — factory + registration check
  PASS  Pipeline LearningToMemory → MemoryToReasoning — chained artifact contract
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_learning_entity(path: Path, learning_text: str = "- Pattern A confirmed in context X.") -> Path:
    """Write a minimal canonical Learning entity to `path`."""
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Test ownership."),
        ("Canonical Basis", str(path)),
        ("Context", "Test context."),
        ("Hypotheses", "- Hypothesis alpha."),
        ("Predictions", "- [pred-001|active] Prediction one."),
        ("Consequences", "None inherited."),
        ("Learning", learning_text),
        ("Links", f"- {path}"),
        ("Current State", "Active"),
        ("Change History", "- 2026-01-01: Created for testing."),
        ("Last Updated", "2026-01-01"),
    ])
    em.save_entity(path, sections)
    return path


def _make_memory_entity(path: Path, learning_text: str = "- Pattern A confirmed in context X.") -> Path:
    """Write a minimal canonical Memory entity to `path`."""
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Memory Organ."),
        ("Canonical Basis", str(path)),
        ("Context", "Consolidated for reasoning."),
        ("Hypotheses", "- Hypothesis alpha."),
        ("Predictions", "- [pred-001|active] Prediction one."),
        ("Consequences", "None inherited."),
        ("Learning", learning_text),
        ("Links", f"- {path}"),
        ("Current State", "Consolidated"),
        ("Change History", "- 2026-01-01: Initialized."),
        ("Last Updated", "2026-01-01"),
    ])
    em.save_entity(path, sections)
    return path


def _make_decision_entity(path: Path) -> Path:
    """Write a minimal canonical Decision entity to `path`."""
    sections = OrderedDict([
        ("__title__", "Decision: test-decision"),
        ("Identity", path.stem),
        ("Ownership", "Owned by the Decision Organ."),
        ("Canonical Basis", str(path)),
        ("Context", "- World State: nominal\n- Objectives: test"),
        ("Hypotheses", "- Hypothesis alpha."),
        ("Predictions", "- [pred-001|active] Prediction one."),
        ("Consequences", "None inherited."),
        ("Learning", "None inherited."),
        ("Links", f"- {path}"),
        ("Current State", "Selected"),
        ("Change History", "- 2026-01-01: Initialized."),
        ("Last Updated", "2026-01-01"),
    ])
    em.save_entity(path, sections)
    return path


def _make_expression_entity(path: Path, predictions: str = "- [pred-001|confirmed] Prediction one confirmed.") -> Path:
    """Write a minimal canonical Expression entity to `path`."""
    sections = OrderedDict([
        ("__title__", "Expression: test-expression"),
        ("Identity", path.stem),
        ("Ownership", "Owned by the Expression Organ."),
        ("Canonical Basis", str(path)),
        ("Context", "Test context."),
        ("Hypotheses", "- Hypothesis alpha."),
        ("Predictions", predictions),
        ("Consequences", "None inherited."),
        ("Learning", "None inherited."),
        ("Links", f"- {path}"),
        ("Current State", "Drafted"),
        ("Change History", "- 2026-01-01: Initialized."),
        ("Last Updated", "2026-01-01"),
    ])
    em.save_entity(path, sections)
    return path


# ---------------------------------------------------------------------------
# Registry + factory
# ---------------------------------------------------------------------------

class TestRegistryAndFactory:
    def test_default_registry_has_six_operators(self):
        from OPERATORS import default_registry
        available = default_registry.available()
        expected = sorted([
            "LearningToMemory",
            "MemoryToReasoning",
            "OpportunityToDecision",
            "DecisionToExpression",
            "ExpressionToConsequence",
            "ConsequenceToLearning",
        ])
        assert available == expected

    def test_build_engine_returns_cognitive_engine(self):
        from OPERATORS import build_engine
        from OPERATORS.engine import CognitiveEngine
        engine = build_engine()
        assert isinstance(engine, CognitiveEngine)

    def test_build_engine_registry_has_all_operators(self):
        from OPERATORS import build_engine
        engine = build_engine()
        assert len(engine.registry.available()) == 6

    def test_build_engine_with_custom_event_bus(self):
        from OPERATORS import build_engine
        bus = MagicMock()
        engine = build_engine(event_bus=bus)
        assert engine.event_bus is bus


# ---------------------------------------------------------------------------
# LearningToMemory
# ---------------------------------------------------------------------------

class TestLearningToMemory:
    def test_validate_accepts_valid_entity(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-test.md")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator()
        assert op.validate(src) is True

    def test_validate_rejects_empty_learning(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-empty.md", learning_text="")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator()
        assert op.validate(src) is False

    def test_execute_returns_correct_memory_id(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-alpha.md")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator()
        result = op.execute(src)
        assert result["sections"]["Identity"] == "memory-learning-alpha"

    def test_persist_creates_memory_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-beta.md")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator()
        result = op.execute(src)
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.name == "memory-learning-beta.md"

    def test_persist_learning_content_is_preserved(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-gamma.md",
                                     learning_text="- Key insight preserved.")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator()
        result = op.execute(src)
        op.persist(result)
        loaded = em.load_entity(result["path"])
        assert "Key insight preserved." in loaded["Learning"]

    def test_emit_events_with_bus(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-delta.md")
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000001"}
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(src)
        events = op.emit_events(result)
        assert len(events) == 1
        bus.emit.assert_called_once()

    def test_emit_events_without_bus_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        src = _make_learning_entity(tmp_path / "learning-epsilon.md")
        from OPERATORS.LearningToMemory.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute(src)
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# MemoryToReasoning
# ---------------------------------------------------------------------------

class TestMemoryToReasoning:
    def test_validate_accepts_valid_memory(self, tmp_path):
        mem_path = tmp_path / "MEMORY" / "memory-test.md"
        _make_memory_entity(mem_path)
        from OPERATORS.MemoryToReasoning.operator import Operator
        op = Operator()
        assert op.validate(mem_path) is True

    def test_validate_rejects_empty_learning(self, tmp_path):
        mem_path = tmp_path / "MEMORY" / "memory-empty.md"
        _make_memory_entity(mem_path, learning_text="")
        from OPERATORS.MemoryToReasoning.operator import Operator, NoUsableLearningError
        op = Operator()
        with pytest.raises((NoUsableLearningError, Exception)):
            op.validate(mem_path)

    def test_execute_populates_session_memory_loaded(self, tmp_path):
        mem_path = tmp_path / "MEMORY" / "memory-session.md"
        _make_memory_entity(mem_path, learning_text="- Insight one.\n- Insight two.")
        from OPERATORS.MemoryToReasoning.operator import Operator
        from OPERATORS.engine import CognitiveSession
        session = CognitiveSession(trigger="test", root_entity=str(mem_path))
        op = Operator()
        result = op.execute(mem_path, session=session)
        assert "Insight one." in session.memory_loaded
        assert "Insight two." in session.memory_loaded

    def test_execute_deduplicates_session_memory(self, tmp_path):
        mem_path = tmp_path / "MEMORY" / "memory-dedup.md"
        _make_memory_entity(mem_path, learning_text="- Repeated insight.")
        from OPERATORS.MemoryToReasoning.operator import Operator
        from OPERATORS.engine import CognitiveSession
        session = CognitiveSession(trigger="test", root_entity=str(mem_path),
                                   memory_loaded=["Repeated insight."])
        op = Operator()
        op.execute(mem_path, session=session)
        assert session.memory_loaded.count("Repeated insight.") == 1

    def test_persist_creates_snapshot_file(self, tmp_path, monkeypatch):
        monkeypatch.syspath_prepend(str(tmp_path))
        mem_path = tmp_path / "MEMORY" / "memory-snap.md"
        _make_memory_entity(mem_path)
        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        original_base = mtr_mod.BASE
        mtr_mod.BASE = tmp_path
        try:
            from OPERATORS.MemoryToReasoning.operator import Operator
            op = Operator()
            result = op.execute(mem_path)
            artifact = op.persist(result)
            assert artifact.exists()
            assert "reasoning-context" in artifact.name
        finally:
            mtr_mod.BASE = original_base

    def test_emit_events_memory_projected(self, tmp_path):
        mem_path = tmp_path / "MEMORY" / "memory-evt.md"
        _make_memory_entity(mem_path)
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000002", "type": "MemoryProjected"}
        from OPERATORS.MemoryToReasoning.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(mem_path)
        events = op.emit_events(result)
        assert len(events) == 1
        call_kwargs = bus.emit.call_args
        assert call_kwargs[1]["event_type"] == "MemoryProjected" or \
               call_kwargs[0][0] == "MemoryProjected"


# ---------------------------------------------------------------------------
# DecisionToExpression
# ---------------------------------------------------------------------------

class TestDecisionToExpression:
    def test_validate_accepts_valid_decision(self, tmp_path):
        dec_path = tmp_path / "DECISIONS" / "decision-test.md"
        _make_decision_entity(dec_path)
        from OPERATORS.DecisionToExpression import operator as dte_mod
        dte_mod.BASE = tmp_path
        from OPERATORS.DecisionToExpression.operator import Operator
        op = Operator()
        assert op.validate(dec_path) is True

    def test_validate_rejects_missing_path(self, tmp_path):
        from OPERATORS.DecisionToExpression.operator import Operator
        op = Operator()
        with pytest.raises(ValueError):
            op.validate(tmp_path / "nonexistent.md")

    def test_execute_derives_expression_identity(self, tmp_path):
        dec_path = tmp_path / "DECISIONS" / "decision-alpha.md"
        _make_decision_entity(dec_path)
        from OPERATORS.DecisionToExpression import operator as dte_mod
        dte_mod.BASE = tmp_path
        from OPERATORS.DecisionToExpression.operator import Operator
        op = Operator()
        result = op.execute(dec_path)
        expr_id = result["expression_sections"]["Identity"]
        assert "expression" in expr_id or "alpha" in expr_id

    def test_persist_creates_expression_file(self, tmp_path):
        dec_path = tmp_path / "DECISIONS" / "decision-beta.md"
        _make_decision_entity(dec_path)
        from OPERATORS.DecisionToExpression import operator as dte_mod
        dte_mod.BASE = tmp_path
        from OPERATORS.DecisionToExpression.operator import Operator
        op = Operator()
        result = op.execute(dec_path)
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.parent.name == "EXPRESSIONS"

    def test_emit_events_expression_published(self, tmp_path):
        dec_path = tmp_path / "DECISIONS" / "decision-gamma.md"
        _make_decision_entity(dec_path)
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000003"}
        from OPERATORS.DecisionToExpression import operator as dte_mod
        dte_mod.BASE = tmp_path
        from OPERATORS.DecisionToExpression.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(dec_path)
        events = op.emit_events(result)
        assert len(events) == 1


# ---------------------------------------------------------------------------
# ExpressionToConsequence
# ---------------------------------------------------------------------------

class TestExpressionToConsequence:
    def test_validate_returns_false_without_evidence(self, tmp_path):
        expr_path = tmp_path / "EXPRESSIONS" / "expression-test.md"
        _make_expression_entity(expr_path)
        from OPERATORS.ExpressionToConsequence.operator import Operator
        op = Operator()
        assert op.validate(expr_path, evidence=None) is False

    def test_execute_resolves_predictions(self, tmp_path):
        expr_path = tmp_path / "EXPRESSIONS" / "expression-resolve.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|active] Prediction one."
        )
        evidence = {"pred-001": "confirmed"}
        from OPERATORS.ExpressionToConsequence.operator import Operator
        op = Operator()
        result = op.execute(expr_path, evidence=evidence, date="2026-07-16")
        assert result["changed"] is True

    def test_persist_rewrites_file_when_changed(self, tmp_path):
        expr_path = tmp_path / "EXPRESSIONS" / "expression-rewrite.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|active] Prediction one."
        )
        evidence = {"pred-001": "confirmed"}
        from OPERATORS.ExpressionToConsequence.operator import Operator
        op = Operator()
        result = op.execute(expr_path, evidence=evidence, date="2026-07-16")
        artifact = op.persist(result)
        assert artifact == Path(expr_path)
        reloaded = em.load_entity(artifact)
        assert "confirmed" in reloaded["Predictions"]

    def test_persist_does_not_rewrite_when_unchanged(self, tmp_path):
        expr_path = tmp_path / "EXPRESSIONS" / "expression-noop.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|confirmed] Already resolved."
        )
        evidence = {}
        from OPERATORS.ExpressionToConsequence.operator import Operator
        op = Operator()
        result = op.execute(expr_path, evidence=evidence, date="2026-07-16")
        mtime_before = expr_path.stat().st_mtime
        op.persist(result)
        mtime_after = expr_path.stat().st_mtime
        assert mtime_before == mtime_after

    def test_emit_events_operator_executed(self, tmp_path):
        expr_path = tmp_path / "EXPRESSIONS" / "expression-emit.md"
        _make_expression_entity(expr_path)
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000004"}
        from OPERATORS.ExpressionToConsequence.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(expr_path, evidence={}, date="2026-07-16")
        events = op.emit_events(result)
        assert len(events) == 1


# ---------------------------------------------------------------------------
# ConsequenceToLearning
# ---------------------------------------------------------------------------

class TestConsequenceToLearning:
    def test_validate_rejects_no_resolved_predictions(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        expr_path = tmp_path / "EXPRESSIONS" / "expression-noresolved.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|active] Still pending."
        )
        from OPERATORS.ConsequenceToLearning.operator import Operator, NoResolvedPredictionsError
        op = Operator()
        with pytest.raises(NoResolvedPredictionsError):
            op.validate(expr_path)

    def test_validate_accepts_resolved_predictions(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        expr_path = tmp_path / "EXPRESSIONS" / "expression-resolved.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|confirmed] Prediction confirmed."
        )
        from OPERATORS.ConsequenceToLearning.operator import Operator
        op = Operator()
        assert op.validate(expr_path) is True

    def test_execute_builds_learning_from_confirmed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        expr_path = tmp_path / "EXPRESSIONS" / "expression-learn.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|confirmed] Insight confirmed.\n- [pred-002|disconfirmed] Hypothesis wrong."
        )
        from OPERATORS.ConsequenceToLearning.operator import Operator
        op = Operator()
        result = op.execute(expr_path)
        learning_text = result["sections"]["Learning"]
        assert "Confirmed" in learning_text
        assert "Disconfirmed" in learning_text
        assert result["resolved_count"] == 2

    def test_persist_creates_learning_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        expr_path = tmp_path / "EXPRESSIONS" / "expression-persist.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|confirmed] Confirmed."
        )
        from OPERATORS.ConsequenceToLearning.operator import Operator
        op = Operator()
        result = op.execute(expr_path)
        artifact = op.persist(result)
        assert artifact.exists()
        assert artifact.name.startswith("learning-")

    def test_emit_events_operator_executed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        expr_path = tmp_path / "EXPRESSIONS" / "expression-evtemit.md"
        _make_expression_entity(
            expr_path,
            predictions="- [pred-001|confirmed] Confirmed."
        )
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000005"}
        from OPERATORS.ConsequenceToLearning.operator import Operator
        op = Operator(event_bus=bus)
        result = op.execute(expr_path)
        events = op.emit_events(result)
        assert len(events) == 1


# ---------------------------------------------------------------------------
# OpportunityToDecision — full functional coverage
# ---------------------------------------------------------------------------

class TestOpportunityToDecision:
    """
    Full execute/persist/emit cycle for OpportunityToDecision.

    REASONERS are deterministic and side-effect-free; no mocking required.

    Confidence arithmetic (from ConfidenceEstimator + EvidenceRanker):
      world_state  → ev-world-state  weight=0.40
      objectives   → ev-objectives   weight=0.35
      memory item  → ev-memory-001   weight=0.25 / max(len(memory), 1)

    Selected path  : world_state + objectives → confidence=0.75 >= 0.50 → selected=True
    Rejected path  : no inputs               → confidence=0.00 <  0.50 → selected=False
    """

    # --- availability (preserved from prior stub) ---

    def test_operator_importable(self):
        from OPERATORS.OpportunityToDecision.operator import Operator  # noqa: F401

    def test_operator_registered_in_default_registry(self):
        from OPERATORS import default_registry
        assert "OpportunityToDecision" in default_registry.available()

    def test_operator_instantiable(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        assert op.inputs() == ["opportunity_entity", "world_state", "objectives", "memory"]

    # --- validate ---

    def test_validate_accepts_non_empty_entity(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        assert op.validate("opportunity-growth-q3") is True

    def test_validate_rejects_empty_entity(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        with pytest.raises(ValueError):
            op.validate(None)

    def test_validate_rejects_empty_string(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        with pytest.raises(ValueError):
            op.validate("")

    # --- execute: selected path ---

    def test_execute_selected_when_world_state_and_objectives_present(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute(
            "opportunity-alpha",
            world_state="nominal",
            objectives="growth",
        )
        assert result["selected"] is True
        assert result["confidence"] >= 0.50
        assert len(result["predictions"]) >= 1
        assert len(result["hypotheses"]) >= 1
        assert len(result["evidence_set"]) == 2

    def test_execute_decision_id_derived_from_entity(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute(
            "opportunity-beta",
            world_state="nominal",
            objectives="alignment",
        )
        assert "decision" in result["decision_id"] or "beta" in result["decision_id"]

    def test_execute_memory_injected_into_evidence(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute(
            "opportunity-gamma",
            world_state="nominal",
            objectives="stability",
            memory=["Prior learning item one.", "Prior learning item two."],
        )
        sources = [e["source"] for e in result["evidence_set"]]
        assert "Memory" in sources
        assert result["confidence"] >= 0.50

    def test_execute_session_memory_loaded_consumed(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        from OPERATORS.engine import CognitiveSession
        session = CognitiveSession(
            trigger="test",
            root_entity="opportunity-session",
            memory_loaded=["Session memory item."],
        )
        op = Operator()
        result = op.execute(
            "opportunity-session",
            world_state="nominal",
            objectives="test",
            session=session,
        )
        memory_sources = [e for e in result["evidence_set"] if e["source"] == "Memory"]
        assert len(memory_sources) >= 1

    # --- execute: rejected path ---

    def test_execute_rejected_when_no_evidence(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("opportunity-no-evidence")
        assert result["selected"] is False
        assert result["confidence"] < 0.50
        assert result["predictions"] == []
        assert len(result["evidence_set"]) == 0

    def test_execute_rejected_confidence_is_zero_with_no_inputs(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("opportunity-zero")
        assert result["confidence"] == 0.0

    # --- persist: selected path ---

    def test_persist_selected_creates_decision_and_evidence_files(self, tmp_path):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute(
                "opportunity-persist-selected",
                world_state="nominal",
                objectives="growth",
            )
            artifact = op.persist(result)
            assert artifact.exists()
            assert artifact.parent.name == "DECISIONS"
            evidence_dir = tmp_path / "EVIDENCE"
            assert evidence_dir.exists()
            evidence_files = list(evidence_dir.glob("evidence_set_for_*.md"))
            assert len(evidence_files) == 1
        finally:
            otd_mod.BASE = original_base

    def test_persist_selected_decision_has_canonical_structure(self, tmp_path):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute(
                "opportunity-structure",
                world_state="stable",
                objectives="clarity",
            )
            decision_path = op.persist(result)
            sections = em.load_entity(decision_path)
            for field in ["Identity", "Ownership", "Canonical Basis", "Context",
                          "Hypotheses", "Predictions", "Consequences", "Learning",
                          "Links", "Current State", "Change History", "Last Updated"]:
                assert field in sections, f"Missing field: {field}"
            assert sections["Current State"] == "Selected"
        finally:
            otd_mod.BASE = original_base

    def test_persist_selected_decision_identity_compatible_with_decision_to_expression(self, tmp_path):
        """
        DecisionToExpression calls .replace('decision-', 'expression-', 1) on Identity.
        Identity must start with 'decision-' for the downstream contract to hold.
        """
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute(
                "opportunity-downstream",
                world_state="nominal",
                objectives="pipeline",
            )
            decision_path = op.persist(result)
            sections = em.load_entity(decision_path)
            assert sections["Identity"].startswith("decision-"), (
                f"Identity '{sections['Identity']}' must start with 'decision-' "
                f"for DecisionToExpression downstream contract."
            )
        finally:
            otd_mod.BASE = original_base

    def test_persist_selected_evidence_entity_has_confidence(self, tmp_path):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute(
                "opportunity-confidence-check",
                world_state="nominal",
                objectives="test",
            )
            op.persist(result)
            evidence_files = list((tmp_path / "EVIDENCE").glob("evidence_set_for_*.md"))
            sections = em.load_entity(evidence_files[0])
            assert "Confidence Estimate" in sections
            confidence_val = float(sections["Confidence Estimate"])
            assert 0.0 <= confidence_val <= 1.0
        finally:
            otd_mod.BASE = original_base

    # --- persist: rejected path ---

    def test_persist_rejected_creates_only_evidence_file(self, tmp_path):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute("opportunity-rejected")
            artifact = op.persist(result)
            assert artifact.exists()
            assert artifact.parent.name == "EVIDENCE"
            decisions_dir = tmp_path / "DECISIONS"
            if decisions_dir.exists():
                assert list(decisions_dir.glob("*.md")) == []
        finally:
            otd_mod.BASE = original_base

    # --- emit_events ---

    def test_emit_events_decision_created_when_selected(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000010", "type": "DecisionCreated"}
        op = Operator(event_bus=bus)
        result = op.execute(
            "opportunity-emit-selected",
            world_state="nominal",
            objectives="test",
        )
        events = op.emit_events(result)
        assert len(events) == 1
        call_kwargs = bus.emit.call_args
        event_type = (
            call_kwargs[1].get("event_type") or call_kwargs[0][0]
        )
        assert event_type == "DecisionCreated"

    def test_emit_events_decision_rejected_when_not_selected(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-000011", "type": "DecisionRejected"}
        op = Operator(event_bus=bus)
        result = op.execute("opportunity-emit-rejected")
        events = op.emit_events(result)
        assert len(events) == 1
        call_kwargs = bus.emit.call_args
        event_type = (
            call_kwargs[1].get("event_type") or call_kwargs[0][0]
        )
        assert event_type == "DecisionRejected"

    def test_emit_events_without_bus_returns_empty(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute("opportunity-no-bus")
        assert op.emit_events(result) == []

    # --- full cycle ---

    def test_full_cycle_selected_path(self, tmp_path):
        """validate → execute → persist → emit_events, selected branch."""
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-full-001"}
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator(event_bus=bus)
            entity = "opportunity-full-cycle"
            assert op.validate(entity) is True
            result = op.execute(entity, world_state="nominal", objectives="growth")
            assert result["selected"] is True
            artifact = op.persist(result)
            assert artifact.exists()
            assert artifact.parent.name == "DECISIONS"
            events = op.emit_events(result)
            assert len(events) == 1
        finally:
            otd_mod.BASE = original_base

    def test_full_cycle_rejected_path(self, tmp_path):
        """validate → execute → persist → emit_events, rejected branch."""
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-full-002"}
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator(event_bus=bus)
            entity = "opportunity-full-rejected"
            assert op.validate(entity) is True
            result = op.execute(entity)
            assert result["selected"] is False
            artifact = op.persist(result)
            assert artifact.exists()
            assert artifact.parent.name == "EVIDENCE"
            events = op.emit_events(result)
            assert len(events) == 1
        finally:
            otd_mod.BASE = original_base


# ---------------------------------------------------------------------------
# Pipeline integration: LearningToMemory → MemoryToReasoning
# ---------------------------------------------------------------------------

class TestPipelineLearningToMemoryToReasoning:
    def test_chain_produces_reasoning_snapshot(self, tmp_path, monkeypatch):
        """
        LearningToMemory writes to MEMORY/ (relative to cwd).
        MemoryToReasoning reads that artifact and writes to REASONING_PARAMETERS/.
        session.memory_loaded is populated end-to-end.
        """
        monkeypatch.chdir(tmp_path)
        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        original_base = mtr_mod.BASE
        mtr_mod.BASE = tmp_path
        try:
            src = _make_learning_entity(tmp_path / "learning-pipeline.md",
                                         learning_text="- End-to-end pipeline insight.")
            from OPERATORS import build_engine
            from OPERATORS.engine import CognitiveSession
            engine = build_engine()
            session = CognitiveSession(trigger="test", root_entity=str(src))

            memory_artifact = engine.run("LearningToMemory", src, session=session)
            assert memory_artifact.exists(), "LearningToMemory must produce a real file"

            reasoning_artifact = engine.run("MemoryToReasoning", memory_artifact, session=session)
            assert reasoning_artifact.exists(), "MemoryToReasoning must produce a real file"

            assert "End-to-end pipeline insight." in session.memory_loaded
            assert len(session.operators_executed) == 2
        finally:
            mtr_mod.BASE = original_base

    def test_run_pipeline_api_chains_correctly(self, tmp_path, monkeypatch):
        """run_pipeline() must chain artifact → artifact across operators."""
        monkeypatch.chdir(tmp_path)
        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        original_base = mtr_mod.BASE
        mtr_mod.BASE = tmp_path
        try:
            src = _make_learning_entity(tmp_path / "learning-pipeline2.md",
                                         learning_text="- Pipeline API verified.")
            from OPERATORS import build_engine
            from OPERATORS.engine import CognitiveSession
            engine = build_engine()
            session = CognitiveSession(trigger="test", root_entity=str(src))
            final_artifact = engine.run_pipeline(
                entity=src,
                pipeline=["LearningToMemory", "MemoryToReasoning"],
                session=session,
            )
            assert final_artifact.exists()
            assert session.final_state == "Completed"
        finally:
            mtr_mod.BASE = original_base
