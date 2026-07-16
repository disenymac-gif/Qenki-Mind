"""
Functional tests for OpportunityToDecision operator.

Previously PENDING — now executable after REASONERS contract certification.

Certified contracts:
  EvidenceRanker.run(opportunity, world_state, objectives, memory)
    → list[dict] with keys: evidence_id, source, summary, weight

  HypothesisGenerator.run(opportunity, evidence_set)
    → list[str]

  ConfidenceEstimator.run(evidence_set)
    → float in [0.0, 1.0]

  DecisionSelector.run(opportunity, confidence)
    → dict: {selected: bool, rationale: str, predictions: list[str]}

Decision entity produced by persist() must satisfy MINIMAL_DECISION_STRUCTURE
so that DecisionToExpression can consume it directly.
"""

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


MINIMAL_DECISION_STRUCTURE = [
    "Identity", "Ownership", "Canonical Basis", "Context", "Hypotheses",
    "Predictions", "Consequences", "Learning", "Links", "Current State",
    "Change History", "Last Updated",
]


# ---------------------------------------------------------------------------
# execute() — reasoning chain
# ---------------------------------------------------------------------------

class TestOpportunityToDecisionExecute:
    def test_execute_returns_all_keys(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute(
            "OPP-001",
            world_state="stable",
            objectives="grow",
            memory=["past learning A"],
        )
        for key in ("opportunity_id", "decision_id", "evidence_set", "hypotheses",
                    "confidence", "selected", "rationale", "predictions"):
            assert key in result, f"Missing key: {key}"

    def test_execute_confidence_in_bounds(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("OPP-002", world_state="nominal", objectives="test")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_execute_decision_id_is_simple_string(self):
        """Identity must be a plain string, not a bullet list."""
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("OPP-003", world_state="stable", objectives="grow")
        assert isinstance(result["decision_id"], str)
        assert not result["decision_id"].startswith("- ")

    def test_execute_opp_prefix_maps_to_dec(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("OPP-alpha", world_state="stable", objectives="grow")
        assert result["decision_id"] == "DEC-alpha"

    def test_execute_no_opp_prefix_derives_decision_id(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("opportunity-growth", world_state="stable", objectives="grow")
        assert result["decision_id"].startswith("decision-")

    def test_execute_pulls_memory_from_session(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        from OPERATORS.engine import CognitiveSession
        session = CognitiveSession(trigger="test", root_entity="OPP-005",
                                   memory_loaded=["memory item X"])
        op = Operator()
        result = op.execute("OPP-005", session=session)
        assert any("memory item X" in item["summary"] for item in result["evidence_set"])

    def test_execute_selected_when_sufficient_evidence(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute(
            "OPP-006",
            world_state="stable",
            objectives="maximize growth",
            memory=["relevant learning"],
        )
        # With world_state + objectives, confidence = 0.4 + 0.35 = 0.75 ≥ 0.5
        assert result["selected"] is True

    def test_execute_rejected_without_evidence(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator()
        result = op.execute("OPP-007", world_state=None, objectives=None, memory=[])
        # No evidence → confidence = 0.0 < 0.5
        assert result["selected"] is False
        assert result["predictions"] == []


# ---------------------------------------------------------------------------
# persist() — artifact contract
# ---------------------------------------------------------------------------

class TestOpportunityToDecisionPersist:
    def _run_with_base(self, tmp_path, opportunity_id, **kwargs):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute(opportunity_id, **kwargs)
            artifact = op.persist(result)
            return op, result, artifact
        finally:
            otd_mod.BASE = original_base

    def test_persist_creates_evidence_file(self, tmp_path):
        _, _, artifact = self._run_with_base(
            tmp_path, "OPP-010",
            world_state="stable", objectives="grow"
        )
        evidence_dir = tmp_path / "EVIDENCE"
        assert any(evidence_dir.iterdir()), "EVIDENCE/ must contain at least one file"

    def test_persist_creates_decision_file_when_selected(self, tmp_path):
        _, result, artifact = self._run_with_base(
            tmp_path, "OPP-011",
            world_state="stable", objectives="grow"
        )
        if result["selected"]:
            assert artifact.parent.name == "DECISIONS"
            assert artifact.exists()

    def test_persist_decision_satisfies_minimal_structure(self, tmp_path):
        """Decision entity must be loadable and pass MINIMAL_DECISION_STRUCTURE."""
        _, result, artifact = self._run_with_base(
            tmp_path, "OPP-012",
            world_state="stable", objectives="grow"
        )
        if result["selected"]:
            sections = em.load_entity(artifact)
            em.validate_entity_structure(sections, MINIMAL_DECISION_STRUCTURE)

    def test_persist_decision_identity_is_simple_string(self, tmp_path):
        """Identity in the Decision file must be a plain string, not bullets."""
        _, result, artifact = self._run_with_base(
            tmp_path, "OPP-013",
            world_state="stable", objectives="grow"
        )
        if result["selected"]:
            sections = em.load_entity(artifact)
            identity = sections["Identity"]
            assert not identity.strip().startswith("- "), (
                f"Identity must be a simple string, got: {identity!r}"
            )

    def test_persist_returns_evidence_when_not_selected(self, tmp_path):
        _, result, artifact = self._run_with_base(
            tmp_path, "OPP-014",
            world_state=None, objectives=None, memory=[]
        )
        assert not result["selected"]
        assert artifact.parent.name == "EVIDENCE"

    def test_persist_last_artifacts_populated(self, tmp_path):
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        original_base = otd_mod.BASE
        otd_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator
            op = Operator()
            result = op.execute("OPP-015", world_state="stable", objectives="grow")
            op.persist(result)
            assert len(op.last_artifacts) >= 1
        finally:
            otd_mod.BASE = original_base


# ---------------------------------------------------------------------------
# emit_events()
# ---------------------------------------------------------------------------

class TestOpportunityToDecisionEmitEvents:
    def test_emits_decision_created_when_selected(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-decision-001"}
        op = Operator(event_bus=bus)
        result = op.execute("OPP-020", world_state="stable", objectives="grow")
        if result["selected"]:
            op.emit_events(result)
            call = bus.emit.call_args
            assert call[1].get("event_type") == "DecisionCreated" or \
                   call[0][0] == "DecisionCreated"

    def test_emits_decision_rejected_when_not_selected(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        bus = MagicMock()
        bus.emit.return_value = {"event_id": "evt-decision-002"}
        op = Operator(event_bus=bus)
        result = op.execute("OPP-021", world_state=None, objectives=None, memory=[])
        assert not result["selected"]
        op.emit_events(result)
        call = bus.emit.call_args
        assert call[1].get("event_type") == "DecisionRejected" or \
               call[0][0] == "DecisionRejected"

    def test_no_events_without_bus(self):
        from OPERATORS.OpportunityToDecision.operator import Operator
        op = Operator(event_bus=None)
        result = op.execute("OPP-022", world_state="stable", objectives="grow")
        assert op.emit_events(result) == []


# ---------------------------------------------------------------------------
# Pipeline: OpportunityToDecision → DecisionToExpression
# ---------------------------------------------------------------------------

class TestPipelineOpportunityToDecisionToExpression:
    def test_decision_feeds_expression_operator(self, tmp_path):
        """
        Decision entity produced by OpportunityToDecision.persist() must be
        directly consumable by DecisionToExpression without modification.
        """
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod

        original_otd_base = otd_mod.BASE
        original_dte_base = dte_mod.BASE
        otd_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        try:
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE

            # Step 1: Opportunity → Decision
            otd = OTD()
            result = otd.execute("OPP-PIPELINE", world_state="stable", objectives="grow")
            if not result["selected"]:
                pytest.skip("Opportunity not selected — pipeline test requires selection")
            decision_path = otd.persist(result)

            # Step 2: Decision → Expression
            dte = DTE()
            assert dte.validate(decision_path) is True, (
                "DecisionToExpression.validate() must accept OpportunityToDecision output"
            )
            expr_result = dte.execute(decision_path)
            expr_path = dte.persist(expr_result)

            assert expr_path.exists()
            expr_sections = em.load_entity(expr_path)
            assert "expression" in expr_sections["Identity"]
        finally:
            otd_mod.BASE = original_otd_base
            dte_mod.BASE = original_dte_base

    def test_full_pipeline_engine_opportunity_to_expression(self, tmp_path):
        """
        engine.run_pipeline() chains OpportunityToDecision → DecisionToExpression.
        """
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS import build_engine
        from OPERATORS.engine import CognitiveSession

        original_otd_base = otd_mod.BASE
        original_dte_base = dte_mod.BASE
        otd_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        try:
            engine = build_engine()
            session = CognitiveSession(
                trigger="test",
                root_entity="OPP-ENGINE",
                world_state_snapshot="stable",
                objectives_snapshot="grow",
            )
            decision_artifact = engine.run(
                "OpportunityToDecision", "OPP-ENGINE", session=session
            )
            if not (tmp_path / "DECISIONS").exists() or \
               not any((tmp_path / "DECISIONS").iterdir()):
                pytest.skip("Opportunity not selected — full pipeline test requires selection")

            expression_artifact = engine.run(
                "DecisionToExpression", decision_artifact, session=session
            )
            assert expression_artifact.exists()
            assert session.operators_executed[-1] == "DecisionToExpression"
        finally:
            otd_mod.BASE = original_otd_base
            dte_mod.BASE = original_dte_base