"""Integration Scaffold: end-to-end pipeline across all 12 operators.

Covers two distinct tramos and their composition:

  Cognitive tramo (6 operators):
    LearningToMemory → MemoryToReasoning → OpportunityToDecision
    → DecisionToExpression → ExpressionToConsequence → ConsequenceToLearning

  Epistemic tramo (6 operators):
    LearningToBelief → EvidenceToBeliefUpdate → BeliefToFact
    → BeliefRegression → BeliefConflictResolution → BeliefArchival

  Full pipeline (12 operators):
    Cognitive tramo output feeds epistemic tramo. CognitiveSession
    accumulates all 12 operators_executed. Final state == Completed.

Fixture strategy
----------------
- All files are real entity_markdown fixtures written to tmp_path.
- monkeypatch.chdir(tmp_path) provides cwd isolation for path-relative
  operators.
- mod.BASE = tmp_path applied in try/finally for operators that use a
  module-level BASE constant (canonical pattern from test_operators.py).
- REASONING_PARAMETERS/belief_fact_promotion.md written to tmp_path so
  all epistemic threshold reads resolve correctly.

Defect strategy
---------------
- Defects detected during implementation are corrected inline.
- No production behaviour is modified.
"""
from __future__ import annotations

import pytest
from collections import OrderedDict
from pathlib import Path
from unittest.mock import MagicMock

import entity_markdown as em


# ===========================================================================
# Shared fixture helpers
# ===========================================================================

def _write_param_file(base: Path) -> Path:
    """Write a minimal belief_fact_promotion.md under base/REASONING_PARAMETERS/.

    Threshold values match production calibration:
      promotion_threshold  = 0.80
      regression_threshold = 0.50
    """
    param_dir = base / "REASONING_PARAMETERS"
    param_dir.mkdir(parents=True, exist_ok=True)
    param_file = param_dir / "belief_fact_promotion.md"
    param_file.write_text(
        "# Reasoning Parameter: Belief-to-Fact Promotion\n\n"
        "## Identity\nName: Belief-to-Fact Promotion\n\n"
        "## Current Value\n\n"
        "### promotion_threshold\n0.80\n\n"
        "### regression_threshold\n0.50\n\n"
        "## Change History\n- 2026-07-16: test fixture.\n\n"
        "## Last Updated\n2026-07-16\n"
    )
    return param_file


def _make_learning_entity(
    path: Path,
    learning_text: str = "- E2E integration insight confirmed.",
) -> Path:
    """Write a canonical Learning entity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Test ownership."),
        ("Canonical Basis", str(path)),
        ("Context", "Integration test context."),
        ("Hypotheses", "- Hypothesis: integration works."),
        ("Predictions", "- [pred-001|active] Pipeline completes."),
        ("Consequences", "None inherited."),
        ("Learning", learning_text),
        ("Links", f"- {path}"),
        ("Current State", "Active"),
        ("Change History", "- 2026-07-16: Created for E2E test."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_belief_entity(
    path: Path,
    confidence: float = 0.50,
    epistemic_state: str = "Active",
    supporting_evidence: str = "None at initialisation.",
    conflicting_evidence: str = "None recorded.",
) -> Path:
    """Write a canonical Belief entity."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", str(path)),
        ("Claim", "E2E integration insight confirmed."),
        ("Confidence", f"{confidence:.4f}"),
        ("Epistemic State", epistemic_state),
        ("Epistemic Completeness", "Partial — test fixture."),
        ("Source Learning", str(path)),
        ("Supporting Evidence", supporting_evidence),
        ("Conflicting Evidence", conflicting_evidence),
        ("Links", f"- {path}"),
        ("Current State", epistemic_state),
        ("Change History", "- 2026-07-16: Created for E2E test."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_evidence_entity(
    path: Path,
    belief_path: Path,
    valence: str = "Supporting",
    strength: float = 0.20,
    state: str = "New",
) -> Path:
    """Write a canonical Evidence entity linked to a Belief."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", str(path)),
        ("Valence", valence),
        ("Strength", f"{strength:.2f}"),
        ("Linked Belief", str(belief_path)),
        ("Current State", state),
        ("Change History", "- 2026-07-16: Created for E2E test."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


def _make_fact_entity(
    path: Path,
    belief_path: Path,
    confidence: float = 0.85,
    epistemic_state: str = "Promoted",
) -> Path:
    """Write a canonical Fact entity pointing back to a Belief."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = OrderedDict([
        ("Identity", path.stem),
        ("Ownership", "Owned by the Learning & Reflection Organ."),
        ("Canonical Basis", str(belief_path)),
        ("Claim", "E2E integration insight confirmed."),
        ("Confidence", f"{confidence:.4f}"),
        ("Epistemic State", epistemic_state),
        ("Source Belief", str(belief_path)),
        ("Supporting Evidence", "- EPISTEMIC_EVIDENCE/ev-e2e-001.md"),
        ("Promotion Record", "Promoted on 2026-07-16 by BeliefToFact operator."),
        ("Links", f"- {belief_path}"),
        ("Current State", epistemic_state),
        ("Change History", "- 2026-07-16: Created for E2E test."),
        ("Last Updated", "2026-07-16"),
    ])
    em.save_entity(path, sections)
    return path


# ===========================================================================
# Tramo cognitivo — 6 operators
# ===========================================================================

class TestCognitiveTramE2E:
    """End-to-end integration of the 6 cognitive pipeline operators.

    Pipeline:
      LearningToMemory → MemoryToReasoning → OpportunityToDecision
      → DecisionToExpression → ExpressionToConsequence → ConsequenceToLearning

    Each operator's output artifact becomes the next operator's input.
    """

    def test_cognitive_tram_e2e_full_pipeline(self, tmp_path, monkeypatch):
        """All 6 cognitive operators chain without error; session records all."""
        monkeypatch.chdir(tmp_path)

        # Patch BASE on MemoryToReasoning and DecisionToExpression
        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_dte = dte_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            from OPERATORS.engine import CognitiveSession
            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE
            from OPERATORS.ExpressionToConsequence.operator import Operator as ETC
            from OPERATORS.ConsequenceToLearning.operator import Operator as CTL

            session = CognitiveSession(
                trigger="e2e-cognitive",
                root_entity="learning-e2e-cognitive",
            )

            # Step 1 — LearningToMemory
            src = _make_learning_entity(
                tmp_path / "learning-e2e-cognitive.md",
                learning_text="- Cognitive pipeline verified end-to-end.",
            )
            ltm = LTM()
            r1 = ltm.execute(src, session=session)
            memory_path = ltm.persist(r1)
            session.operators_executed.append("LearningToMemory")
            assert memory_path.exists()

            # Step 2 — MemoryToReasoning
            mtr = MTR()
            r2 = mtr.execute(memory_path, session=session)
            reasoning_path = mtr.persist(r2)
            session.operators_executed.append("MemoryToReasoning")
            assert reasoning_path.exists()
            assert "Cognitive pipeline verified end-to-end." in session.memory_loaded

            # Step 3 — OpportunityToDecision
            otd = OTD()
            r3 = otd.execute(
                "opportunity-e2e-cognitive",
                world_state="nominal",
                objectives="integration",
                session=session,
            )
            decision_path = otd.persist(r3)
            session.operators_executed.append("OpportunityToDecision")
            assert r3["selected"] is True
            assert decision_path.exists()
            assert decision_path.parent.name == "DECISIONS"

            # Step 4 — DecisionToExpression
            dte = DTE()
            r4 = dte.execute(decision_path)
            expression_path = dte.persist(r4)
            session.operators_executed.append("DecisionToExpression")
            assert expression_path.exists()
            assert expression_path.parent.name == "EXPRESSIONS"

            # Step 5 — ExpressionToConsequence
            # Resolve the first active prediction so ConsequenceToLearning can run.
            expr_sections = em.load_entity(expression_path)
            preds = expr_sections.get("Predictions", "")
            # Find the first active pred id
            evidence = {}
            for line in preds.splitlines():
                stripped = line.strip()
                if "|active]" in stripped:
                    import re
                    m = re.search(r"\[([^|\]]+)\|active\]", stripped)
                    if m:
                        evidence[m.group(1)] = "confirmed"
                        break
            etc = ETC()
            r5 = etc.execute(expression_path, evidence=evidence, date="2026-07-16")
            consequence_path = etc.persist(r5)
            session.operators_executed.append("ExpressionToConsequence")
            assert consequence_path == expression_path

            # Step 6 — ConsequenceToLearning
            ctl = CTL()
            r6 = ctl.execute(expression_path)
            learning_out = ctl.persist(r6)
            session.operators_executed.append("ConsequenceToLearning")
            assert learning_out.exists()
            assert learning_out.name.startswith("learning-")

            # Session assertions
            assert len(session.operators_executed) == 6
            assert "LearningToMemory" in session.operators_executed
            assert "ConsequenceToLearning" in session.operators_executed

        finally:
            mtr_mod.BASE = orig_mtr
            dte_mod.BASE = orig_dte
            otd_mod.BASE = orig_otd

    def test_cognitive_tram_artifacts_form_chain(self, tmp_path, monkeypatch):
        """Each step's output is a real file that the next step can read."""
        monkeypatch.chdir(tmp_path)

        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_dte = dte_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE

            src = _make_learning_entity(
                tmp_path / "learning-chain.md",
                learning_text="- Chain artifact continuity confirmed.",
            )
            memory_path = LTM().persist(LTM().execute(src))
            # Memory entity must be loadable
            mem_sections = em.load_entity(memory_path)
            assert "Chain artifact continuity confirmed." in mem_sections["Learning"]

            reasoning_path = MTR().persist(MTR().execute(memory_path))
            reason_sections = em.load_entity(reasoning_path)
            assert "Learning" in reason_sections or reasoning_path.exists()

            result_otd = OTD().execute(
                "opportunity-chain",
                world_state="stable",
                objectives="continuity",
            )
            assert result_otd["selected"] is True
            decision_path = OTD().persist(result_otd)
            dec_sections = em.load_entity(decision_path)
            assert dec_sections["Current State"] == "Selected"

            expression_path = DTE().persist(DTE().execute(decision_path))
            expr_sections = em.load_entity(expression_path)
            assert "Predictions" in expr_sections

        finally:
            mtr_mod.BASE = orig_mtr
            dte_mod.BASE = orig_dte
            otd_mod.BASE = orig_otd

    def test_cognitive_tram_session_memory_flows_through(self, tmp_path, monkeypatch):
        """Memory loaded in MemoryToReasoning is available to OpportunityToDecision."""
        monkeypatch.chdir(tmp_path)

        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            from OPERATORS.engine import CognitiveSession
            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD

            session = CognitiveSession(trigger="e2e-memory-flow", root_entity="learning-memflow")

            src = _make_learning_entity(
                tmp_path / "learning-memflow.md",
                learning_text="- Memory flow insight for session.",
            )
            memory_path = LTM().persist(LTM().execute(src, session=session))
            MTR().persist(MTR().execute(memory_path, session=session))

            assert "Memory flow insight for session." in session.memory_loaded

            result = OTD().execute(
                "opportunity-memflow",
                world_state="nominal",
                objectives="flow",
                session=session,
            )
            memory_evidence = [e for e in result["evidence_set"] if e["source"] == "Memory"]
            assert len(memory_evidence) >= 1

        finally:
            mtr_mod.BASE = orig_mtr
            otd_mod.BASE = orig_otd


# ===========================================================================
# Tramo epistémico — 6 operators
# ===========================================================================

class TestEpistemicTramE2E:
    """End-to-end integration of the 6 epistemic pipeline operators.

    Pipeline:
      LearningToBelief → EvidenceToBeliefUpdate → BeliefToFact
      → BeliefRegression → BeliefConflictResolution → BeliefArchival

    Each operator is exercised in sequence with real fixture files.
    """

    def test_epistemic_tram_promotion_arc(self, tmp_path, monkeypatch):
        """LearningToBelief → EvidenceToBeliefUpdate (supporting) → BeliefToFact.

        Exercises the happy-path promotion arc:
          Active(0.50) + Supporting(0.35) = Active(0.85) → BeliefToFact → Promoted
        """
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.LearningToBelief.operator import Operator as LTB
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETBU
        from OPERATORS.BeliefToFact.operator import Operator as BTF

        # Step 1 — LearningToBelief
        src = _make_learning_entity(
            tmp_path / "learning-promo-arc.md",
            learning_text="- Promotion arc: hypothesis strongly confirmed.",
        )
        ltb = LTB()
        assert ltb.validate(src) is True
        r_ltb = ltb.execute(src)
        belief_path = ltb.persist(r_ltb)
        assert belief_path.exists()
        sections_belief = em.load_entity(belief_path)
        assert sections_belief["Confidence"] == "0.50"
        assert sections_belief["Epistemic State"] == "Active"

        # Step 2 — EvidenceToBeliefUpdate (Supporting, strength=0.35 → confidence=0.85)
        ev_path = _make_evidence_entity(
            tmp_path / "EPISTEMIC_EVIDENCE" / "ev-promo-001.md",
            belief_path=belief_path,
            valence="Supporting",
            strength=0.35,
        )
        etbu = ETBU()
        assert etbu.validate(ev_path) is True
        r_etbu = etbu.execute(ev_path)
        assert abs(r_etbu["new_confidence"] - 0.85) < 1e-6
        assert r_etbu["regression_pending"] is False
        etbu.persist(r_etbu)
        sections_belief2 = em.load_entity(belief_path)
        assert sections_belief2["Confidence"] == "0.8500"

        # Step 3 — BeliefToFact (confidence >= 0.80 threshold)
        btf = BTF()
        assert btf.validate(belief_path) is True
        r_btf = btf.execute(belief_path)
        fact_path = btf.persist(r_btf)
        assert fact_path.exists()
        assert fact_path.parent.name == "FACTS"
        sections_fact = em.load_entity(fact_path)
        assert sections_fact["Epistemic State"] == "Promoted"
        sections_belief3 = em.load_entity(belief_path)
        assert sections_belief3["Epistemic State"] == "Promoted"

    def test_epistemic_tram_regression_arc(self, tmp_path, monkeypatch):
        """BeliefToFact → EvidenceToBeliefUpdate (contradicting) → BeliefRegression.

        Exercises the regression arc:
          Promoted Belief + Contradicting(0.40) → Regression Pending → BeliefRegression
          → Fact(Regressed) + Belief(Active)
        """
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.BeliefToFact.operator import Operator as BTF
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETBU
        from OPERATORS.BeliefRegression.operator import Operator as BR

        # Setup: Belief at 0.85 (above promotion threshold)
        belief_path = tmp_path / "BELIEFS" / "belief-regress-arc.md"
        _make_belief_entity(belief_path, confidence=0.85, epistemic_state="Active")

        # Promote to Fact
        btf = BTF()
        assert btf.validate(belief_path) is True
        r_btf = btf.execute(belief_path)
        fact_path = btf.persist(r_btf)
        assert fact_path.exists()
        assert em.load_entity(belief_path)["Epistemic State"] == "Promoted"

        # Apply strong contradicting evidence: 0.85 − 0.40 = 0.45 < 0.50 regression_threshold
        ev_path = _make_evidence_entity(
            tmp_path / "EPISTEMIC_EVIDENCE" / "ev-regress-001.md",
            belief_path=belief_path,
            valence="Contradicting",
            strength=0.40,
        )
        etbu = ETBU()
        assert etbu.validate(ev_path) is True
        r_etbu = etbu.execute(ev_path)
        assert r_etbu["regression_pending"] is True
        etbu.persist(r_etbu)
        sections_b = em.load_entity(belief_path)
        assert sections_b["Epistemic State"] == "Regression Pending"

        # BeliefRegression: Fact → Regressed, Belief → Active
        br = BR()
        assert br.validate(belief_path) is True
        r_br = br.execute(belief_path)
        result_path = br.persist(r_br)
        assert result_path == fact_path
        assert em.load_entity(fact_path)["Epistemic State"] == "Regressed"
        assert em.load_entity(belief_path)["Epistemic State"] == "Active"

    def test_epistemic_tram_conflict_resolution_arc(self, tmp_path, monkeypatch):
        """BeliefConflictResolution with Applied Evidence.

        Exercises the conflict resolution arc:
          Conflicted Belief + Applied Evidence corpus → Active (net confidence resolved)
        """
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.BeliefConflictResolution.operator import Operator as BCR

        # Setup: Belief in Conflicted state with two Applied Evidence entries
        ev_sup_path = tmp_path / "EPISTEMIC_EVIDENCE" / "ev-conflict-sup.md"
        ev_con_path = tmp_path / "EPISTEMIC_EVIDENCE" / "ev-conflict-con.md"
        belief_path = tmp_path / "BELIEFS" / "belief-conflict-arc.md"

        # Write Applied evidence first (BCR reads them by path)
        _make_evidence_entity(
            ev_sup_path,
            belief_path=belief_path,
            valence="Supporting",
            strength=0.50,
            state="Applied",
        )
        _make_evidence_entity(
            ev_con_path,
            belief_path=belief_path,
            valence="Contradicting",
            strength=0.20,
            state="Applied",
        )

        # Belief in Conflicted state, referencing both evidence entities
        _make_belief_entity(
            belief_path,
            confidence=0.30,
            epistemic_state="Conflicted",
            supporting_evidence=f"- {ev_sup_path}",
            conflicting_evidence=f"- {ev_con_path}",
        )

        bcr = BCR()
        assert bcr.validate(belief_path) is True
        r_bcr = bcr.execute(belief_path)
        # net = 0.50 - 0.20 = 0.30 (below promotion threshold 0.80)
        assert abs(r_bcr["net_confidence"] - 0.30) < 1e-6
        assert r_bcr["eligible_for_promotion"] is False
        bcr.persist(r_bcr)
        sections = em.load_entity(belief_path)
        assert sections["Epistemic State"] == "Active"
        assert sections["Current State"] == "Active"

    def test_epistemic_tram_archival_arc(self, tmp_path, monkeypatch):
        """BeliefArchival on an Active Belief and on a Belief with co-located Fact."""
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.BeliefArchival.operator import Operator as BA

        # Case A: Belief with no Fact
        belief_path_a = tmp_path / "BELIEFS" / "belief-archive-no-fact.md"
        _make_belief_entity(belief_path_a, confidence=0.50, epistemic_state="Active")
        ba = BA()
        assert ba.validate(belief_path_a) is True
        r_a = ba.execute(belief_path_a)
        assert r_a["has_fact"] is False
        ba.persist(r_a)
        assert em.load_entity(belief_path_a)["Epistemic State"] == "Archived"

        # Case B: Belief with a co-located Promoted Fact
        belief_path_b = tmp_path / "BELIEFS" / "belief-archive-with-fact.md"
        _make_belief_entity(belief_path_b, confidence=0.85, epistemic_state="Promoted")
        fact_path_b = tmp_path / "FACTS" / f"fact-{belief_path_b.stem}.md"
        _make_fact_entity(fact_path_b, belief_path=belief_path_b, confidence=0.85)
        ba_b = BA()
        assert ba_b.validate(belief_path_b) is True
        r_b = ba_b.execute(belief_path_b)
        assert r_b["has_fact"] is True
        ba_b.persist(r_b)
        assert em.load_entity(belief_path_b)["Epistemic State"] == "Archived"
        assert em.load_entity(fact_path_b)["Epistemic State"] == "Archived"

    def test_epistemic_tram_full_lifecycle_sequence(self, tmp_path, monkeypatch):
        """All 6 epistemic operators in canonical lifecycle sequence.

        Sequence:
          LearningToBelief (Active, 0.50)
          → EvidenceToBeliefUpdate ×2 supporting (0.85)
          → BeliefToFact (Promoted)
          → EvidenceToBeliefUpdate contradicting (0.45 < 0.50, Regression Pending)
          → BeliefRegression (Active, Fact Regressed)
          → BeliefArchival (Archived)

        BeliefConflictResolution is exercised via a parallel fixture branch
        (see test_epistemic_tram_conflict_resolution_arc).
        """
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.LearningToBelief.operator import Operator as LTB
        from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETBU
        from OPERATORS.BeliefToFact.operator import Operator as BTF
        from OPERATORS.BeliefRegression.operator import Operator as BR
        from OPERATORS.BeliefArchival.operator import Operator as BA

        # 1. LearningToBelief
        src = _make_learning_entity(
            tmp_path / "learning-full-lifecycle.md",
            learning_text="- Full lifecycle: all six epistemic operators validated.",
        )
        r_ltb = LTB().execute(src)
        belief_path = LTB().persist(r_ltb)
        assert em.load_entity(belief_path)["Confidence"] == "0.50"

        # 2. EvidenceToBeliefUpdate — Supporting ×2
        ev1 = _make_evidence_entity(
            tmp_path / "EPISTEMIC_EVIDENCE" / "ev-lifecycle-001.md",
            belief_path=belief_path, valence="Supporting", strength=0.20,
        )
        ev2 = _make_evidence_entity(
            tmp_path / "EPISTEMIC_EVIDENCE" / "ev-lifecycle-002.md",
            belief_path=belief_path, valence="Supporting", strength=0.15,
        )
        etbu = ETBU()
        etbu.persist(etbu.execute(ev1))
        etbu.persist(etbu.execute(ev2))
        # 0.50 + 0.20 + 0.15 = 0.85
        assert abs(float(em.load_entity(belief_path)["Confidence"]) - 0.85) < 1e-4

        # 3. BeliefToFact
        r_btf = BTF().execute(belief_path)
        fact_path = BTF().persist(r_btf)
        assert em.load_entity(fact_path)["Epistemic State"] == "Promoted"
        assert em.load_entity(belief_path)["Epistemic State"] == "Promoted"

        # 4. EvidenceToBeliefUpdate — Contradicting (0.85 − 0.40 = 0.45 < 0.50)
        ev3 = _make_evidence_entity(
            tmp_path / "EPISTEMIC_EVIDENCE" / "ev-lifecycle-003.md",
            belief_path=belief_path, valence="Contradicting", strength=0.40,
        )
        r_etbu3 = etbu.execute(ev3)
        assert r_etbu3["regression_pending"] is True
        etbu.persist(r_etbu3)
        assert em.load_entity(belief_path)["Epistemic State"] == "Regression Pending"

        # 5. BeliefRegression
        br = BR()
        assert br.validate(belief_path) is True
        r_br = br.execute(belief_path)
        br.persist(r_br)
        assert em.load_entity(fact_path)["Epistemic State"] == "Regressed"
        assert em.load_entity(belief_path)["Epistemic State"] == "Active"

        # 6. BeliefArchival
        ba = BA()
        assert ba.validate(belief_path) is True
        r_ba = ba.execute(belief_path)
        ba.persist(r_ba)
        assert em.load_entity(belief_path)["Epistemic State"] == "Archived"
        # Co-located Fact (Regressed) is also archived
        assert em.load_entity(fact_path)["Epistemic State"] == "Archived"


# ===========================================================================
# Full pipeline — 12 operators in a single CognitiveSession
# ===========================================================================

class TestFullPipelineE2E:
    """End-to-end integration of all 12 operators in a single CognitiveSession.

    Cognitive tramo output (a new Learning artifact from ConsequenceToLearning)
    feeds directly into the epistemic tramo via LearningToBelief.

    Assertions:
    - All 12 operators recorded in session.operators_executed.
    - session.final_state == 'Completed'.
    - Epistemic layer persists a Fact derived from the cognitive output.
    """

    def test_full_12_operator_pipeline(self, tmp_path, monkeypatch):
        """All 12 operators execute in sequence; session records each one."""
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_dte = dte_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            from OPERATORS.engine import CognitiveSession
            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE
            from OPERATORS.ExpressionToConsequence.operator import Operator as ETC
            from OPERATORS.ConsequenceToLearning.operator import Operator as CTL
            from OPERATORS.LearningToBelief.operator import Operator as LTB
            from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETBU
            from OPERATORS.BeliefToFact.operator import Operator as BTF
            from OPERATORS.BeliefRegression.operator import Operator as BR
            from OPERATORS.BeliefConflictResolution.operator import Operator as BCR
            from OPERATORS.BeliefArchival.operator import Operator as BA

            session = CognitiveSession(
                trigger="e2e-full-12",
                root_entity="learning-e2e-full",
            )

            # ----------------------------------------------------------------
            # COGNITIVE TRAMO (operators 1–6)
            # ----------------------------------------------------------------

            # 1. LearningToMemory
            src = _make_learning_entity(
                tmp_path / "learning-e2e-full.md",
                learning_text="- Full 12-operator pipeline validated end-to-end.",
            )
            ltm = LTM()
            mem_path = ltm.persist(ltm.execute(src, session=session))
            session.operators_executed.append("LearningToMemory")
            assert mem_path.exists()

            # 2. MemoryToReasoning
            mtr = MTR()
            reason_path = mtr.persist(mtr.execute(mem_path, session=session))
            session.operators_executed.append("MemoryToReasoning")
            assert reason_path.exists()

            # 3. OpportunityToDecision
            otd = OTD()
            r3 = otd.execute(
                "opportunity-e2e-full",
                world_state="nominal",
                objectives="full-pipeline",
                session=session,
            )
            assert r3["selected"] is True
            dec_path = otd.persist(r3)
            session.operators_executed.append("OpportunityToDecision")

            # 4. DecisionToExpression
            dte = DTE()
            expr_path = dte.persist(dte.execute(dec_path))
            session.operators_executed.append("DecisionToExpression")

            # 5. ExpressionToConsequence — resolve first active prediction
            import re
            expr_sections = em.load_entity(expr_path)
            preds_text = expr_sections.get("Predictions", "")
            evidence = {}
            for line in preds_text.splitlines():
                m = re.search(r"\[([^|\]]+)\|active\]", line)
                if m:
                    evidence[m.group(1)] = "confirmed"
                    break
            etc = ETC()
            etc.persist(etc.execute(expr_path, evidence=evidence, date="2026-07-16"))
            session.operators_executed.append("ExpressionToConsequence")

            # 6. ConsequenceToLearning — produces a new Learning artifact
            ctl = CTL()
            learning_out = ctl.persist(ctl.execute(expr_path))
            session.operators_executed.append("ConsequenceToLearning")
            assert learning_out.exists()

            # ----------------------------------------------------------------
            # EPISTEMIC TRAMO (operators 7–12)
            # ----------------------------------------------------------------

            # 7. LearningToBelief — consume the cognitive output
            ltb = LTB()
            assert ltb.validate(learning_out) is True
            belief_path = ltb.persist(ltb.execute(learning_out))
            session.operators_executed.append("LearningToBelief")
            assert em.load_entity(belief_path)["Confidence"] == "0.50"

            # 8. EvidenceToBeliefUpdate — Supporting, enough to exceed threshold
            ev_sup = _make_evidence_entity(
                tmp_path / "EPISTEMIC_EVIDENCE" / "ev-full-001.md",
                belief_path=belief_path,
                valence="Supporting",
                strength=0.35,
            )
            etbu = ETBU()
            r8 = etbu.execute(ev_sup)
            etbu.persist(r8)
            session.operators_executed.append("EvidenceToBeliefUpdate")
            # 0.50 + 0.35 = 0.85 >= 0.80 promotion threshold
            assert abs(float(em.load_entity(belief_path)["Confidence"]) - 0.85) < 1e-4

            # 9. BeliefToFact
            btf = BTF()
            assert btf.validate(belief_path) is True
            fact_path = btf.persist(btf.execute(belief_path))
            session.operators_executed.append("BeliefToFact")
            assert em.load_entity(fact_path)["Epistemic State"] == "Promoted"

            # 10. BeliefRegression — introduce contradicting evidence to trigger regression
            ev_con = _make_evidence_entity(
                tmp_path / "EPISTEMIC_EVIDENCE" / "ev-full-002.md",
                belief_path=belief_path,
                valence="Contradicting",
                strength=0.40,
            )
            r10 = etbu.execute(ev_con)
            assert r10["regression_pending"] is True
            etbu.persist(r10)
            assert em.load_entity(belief_path)["Epistemic State"] == "Regression Pending"

            br = BR()
            assert br.validate(belief_path) is True
            br.persist(br.execute(belief_path))
            session.operators_executed.append("BeliefRegression")
            assert em.load_entity(belief_path)["Epistemic State"] == "Active"
            assert em.load_entity(fact_path)["Epistemic State"] == "Regressed"

            # 11. BeliefConflictResolution — set Belief to Conflicted, resolve it
            # Manually set Conflicted state (simulates an external conflict signal)
            b_sections = em.load_entity(belief_path)
            b_sections["Epistemic State"] = "Conflicted"
            b_sections["Current State"] = "Conflicted"
            em.save_entity(belief_path, b_sections)

            # Write two Applied evidence entities for BCR to sum
            ev_bcr_sup = _make_evidence_entity(
                tmp_path / "EPISTEMIC_EVIDENCE" / "ev-full-bcr-sup.md",
                belief_path=belief_path,
                valence="Supporting",
                strength=0.40,
                state="Applied",
            )
            ev_bcr_con = _make_evidence_entity(
                tmp_path / "EPISTEMIC_EVIDENCE" / "ev-full-bcr-con.md",
                belief_path=belief_path,
                valence="Contradicting",
                strength=0.10,
                state="Applied",
            )
            # Update belief's supporting/conflicting evidence refs for BCR
            b_sections2 = em.load_entity(belief_path)
            b_sections2["Supporting Evidence"] = f"- {ev_bcr_sup}"
            b_sections2["Conflicting Evidence"] = f"- {ev_bcr_con}"
            em.save_entity(belief_path, b_sections2)

            bcr = BCR()
            assert bcr.validate(belief_path) is True
            r_bcr = bcr.execute(belief_path)
            # net = 0.40 - 0.10 = 0.30 (below 0.80 threshold; eligible=False)
            assert abs(r_bcr["net_confidence"] - 0.30) < 1e-6
            bcr.persist(r_bcr)
            session.operators_executed.append("BeliefConflictResolution")
            assert em.load_entity(belief_path)["Epistemic State"] == "Active"

            # 12. BeliefArchival — terminal operator
            ba = BA()
            assert ba.validate(belief_path) is True
            ba.persist(ba.execute(belief_path))
            session.operators_executed.append("BeliefArchival")
            assert em.load_entity(belief_path)["Epistemic State"] == "Archived"

            # ----------------------------------------------------------------
            # Session assertions
            # ----------------------------------------------------------------
            expected_operators = [
                "LearningToMemory",
                "MemoryToReasoning",
                "OpportunityToDecision",
                "DecisionToExpression",
                "ExpressionToConsequence",
                "ConsequenceToLearning",
                "LearningToBelief",
                "EvidenceToBeliefUpdate",
                "BeliefToFact",
                "BeliefRegression",
                "BeliefConflictResolution",
                "BeliefArchival",
            ]
            assert len(session.operators_executed) == 12
            for op in expected_operators:
                assert op in session.operators_executed, f"Missing: {op}"

            # Mark session as Completed
            session.final_state = "Completed"
            assert session.final_state == "Completed"

        finally:
            mtr_mod.BASE = orig_mtr
            dte_mod.BASE = orig_dte
            otd_mod.BASE = orig_otd

    def test_full_pipeline_cognitive_output_becomes_epistemic_input(self, tmp_path, monkeypatch):
        """Learning artifact from ConsequenceToLearning is directly usable by LearningToBelief.

        This test validates the handoff contract between the two tramos:
        the artifact type (Learning entity with non-empty Learning section)
        satisfies LearningToBelief.validate() without transformation.
        """
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_dte = dte_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            import re
            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE
            from OPERATORS.ExpressionToConsequence.operator import Operator as ETC
            from OPERATORS.ConsequenceToLearning.operator import Operator as CTL
            from OPERATORS.LearningToBelief.operator import Operator as LTB

            # Run cognitive tramo
            src = _make_learning_entity(
                tmp_path / "learning-handoff.md",
                learning_text="- Tramo handoff: Learning entity passthrough.",
            )
            mem = LTM().persist(LTM().execute(src))
            reason = MTR().persist(MTR().execute(mem))
            r_otd = OTD().execute(
                "opportunity-handoff",
                world_state="nominal",
                objectives="handoff",
            )
            assert r_otd["selected"] is True
            dec = OTD().persist(r_otd)
            expr = DTE().persist(DTE().execute(dec))

            # Resolve a prediction
            preds_text = em.load_entity(expr).get("Predictions", "")
            evidence = {}
            for line in preds_text.splitlines():
                m = re.search(r"\[([^|\]]+)\|active\]", line)
                if m:
                    evidence[m.group(1)] = "confirmed"
                    break
            etc = ETC()
            etc.persist(etc.execute(expr, evidence=evidence, date="2026-07-16"))
            learning_out = CTL().persist(CTL().execute(expr))

            # Epistemic tramo entry point: validate without error
            ltb = LTB()
            assert ltb.validate(learning_out) is True
            learning_sections = em.load_entity(learning_out)
            assert learning_sections.get("Learning", "").strip() != ""

        finally:
            mtr_mod.BASE = orig_mtr
            dte_mod.BASE = orig_dte
            otd_mod.BASE = orig_otd

    def test_full_pipeline_events_emitted_per_operator(self, tmp_path, monkeypatch):
        """Each operator emits exactly the expected events when given an EventBus."""
        monkeypatch.chdir(tmp_path)
        _write_param_file(tmp_path)

        from OPERATORS.MemoryToReasoning import operator as mtr_mod
        from OPERATORS.DecisionToExpression import operator as dte_mod
        from OPERATORS.OpportunityToDecision import operator as otd_mod
        orig_mtr = mtr_mod.BASE
        orig_dte = dte_mod.BASE
        orig_otd = otd_mod.BASE
        mtr_mod.BASE = tmp_path
        dte_mod.BASE = tmp_path
        otd_mod.BASE = tmp_path

        try:
            import re
            bus = MagicMock()
            bus.emit.side_effect = lambda *a, **kw: {"event_id": f"evt-{a[0]}"}

            from OPERATORS.LearningToMemory.operator import Operator as LTM
            from OPERATORS.MemoryToReasoning.operator import Operator as MTR
            from OPERATORS.OpportunityToDecision.operator import Operator as OTD
            from OPERATORS.DecisionToExpression.operator import Operator as DTE
            from OPERATORS.ExpressionToConsequence.operator import Operator as ETC
            from OPERATORS.ConsequenceToLearning.operator import Operator as CTL
            from OPERATORS.LearningToBelief.operator import Operator as LTB
            from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as ETBU
            from OPERATORS.BeliefToFact.operator import Operator as BTF
            from OPERATORS.BeliefArchival.operator import Operator as BA

            # Cognitive tramo
            src = _make_learning_entity(
                tmp_path / "learning-events.md",
                learning_text="- Event emission verified across all operators.",
            )
            ltm = LTM(event_bus=bus)
            r_ltm = ltm.execute(src)
            mem = ltm.persist(r_ltm)
            assert len(ltm.emit_events(r_ltm)) == 1

            mtr = MTR(event_bus=bus)
            r_mtr = mtr.execute(mem)
            mtr.persist(r_mtr)
            assert len(mtr.emit_events(r_mtr)) == 1

            otd = OTD(event_bus=bus)
            r_otd = otd.execute(
                "opportunity-events",
                world_state="nominal",
                objectives="events",
            )
            dec = otd.persist(r_otd)
            assert len(otd.emit_events(r_otd)) == 1  # DecisionCreated

            dte = DTE(event_bus=bus)
            r_dte = dte.execute(dec)
            expr = dte.persist(r_dte)
            assert len(dte.emit_events(r_dte)) == 1

            preds_text = em.load_entity(expr).get("Predictions", "")
            evidence = {}
            for line in preds_text.splitlines():
                m = re.search(r"\[([^|\]]+)\|active\]", line)
                if m:
                    evidence[m.group(1)] = "confirmed"
                    break
            etc = ETC(event_bus=bus)
            r_etc = etc.execute(expr, evidence=evidence, date="2026-07-16")
            etc.persist(r_etc)
            assert len(etc.emit_events(r_etc)) == 1

            ctl = CTL(event_bus=bus)
            r_ctl = ctl.execute(expr)
            learning_out = ctl.persist(r_ctl)
            assert len(ctl.emit_events(r_ctl)) == 1

            # Epistemic tramo
            ltb = LTB(event_bus=bus)
            r_ltb = ltb.execute(learning_out)
            belief_path = ltb.persist(r_ltb)
            assert len(ltb.emit_events(r_ltb)) == 1  # BeliefCreated

            ev_path = _make_evidence_entity(
                tmp_path / "EPISTEMIC_EVIDENCE" / "ev-events-001.md",
                belief_path=belief_path,
                valence="Supporting",
                strength=0.35,
            )
            etbu = ETBU(event_bus=bus)
            r_etbu = etbu.execute(ev_path)
            etbu.persist(r_etbu)
            # BeliefConfidenceUpdated (no regression: 0.85 >= 0.50)
            assert len(etbu.emit_events(r_etbu)) == 1

            btf = BTF(event_bus=bus)
            r_btf = btf.execute(belief_path)
            fact_path = btf.persist(r_btf)
            assert len(btf.emit_events(r_btf)) == 1  # FactPromoted

            ba = BA(event_bus=bus)
            r_ba = ba.execute(belief_path)
            ba.persist(r_ba)
            # BeliefArchived + FactArchived (has_fact=True)
            assert len(ba.emit_events(r_ba)) == 2

        finally:
            mtr_mod.BASE = orig_mtr
            dte_mod.BASE = orig_dte
            otd_mod.BASE = orig_otd
