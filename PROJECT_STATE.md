# Project State

## Repository
disenymac-gif/Qenki-Mind

## Branch
main

## Baseline Commit
6add39f4480a6c81e621de5ad936b69e1a7c6d6b

## Last Updated
2026-07-16

## Current Architecture
Eight ADRs total. ADR-001 through ADR-008 all Closed. Six canonical
documents frozen. Full reference: `QENKI_MIND_GOVERNANCE_RULES_v1.md`
and `REPOSITORY_MAP.md`.

## Implemented
- Cognitive pipeline: 9 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`,
  `LearningToBelief`, `BeliefToFact`, `EvidenceToBeliefUpdate`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`, `tests/test_learning_to_belief.py`,
  `tests/test_belief_to_fact.py`, `tests/test_evidence_to_belief_update.py`
- `BELIEFS/` runtime artifact store: persistent epistemic layer (ADR-007/ADR-008)
- `FACTS/` runtime artifact store: Fact domain materialized (ADR-001 + ADR-008)
- `EPISTEMIC_EVIDENCE/` runtime artifact store: epistemic Evidence schema
  (distinct from `EVIDENCE/` which is owned by Decision Organ)
- `LearningToBelief` operator: Learning → Belief; BeliefCreated event
- `BeliefToFact` operator: Belief → Fact; reads `promotion_threshold` from
  `REASONING_PARAMETERS/belief_fact_promotion.md`; updates source Belief
  Epistemic State; FactPromoted event; idempotent guard (AlreadyPromotedError)
- `EvidenceToBeliefUpdate` operator: epistemic Evidence → Belief confidence
  delta; Supporting adds strength, Contradicting subtracts strength; clamps
  [0.0, 1.0]; sets Epistemic State to 'Regression Pending' when confidence
  drops below regression_threshold; emits BeliefConfidenceUpdated +
  BeliefRegressionPending; idempotent guard (AlreadyAppliedError)
- `REASONING_PARAMETERS/belief_fact_promotion.md`: calibrated
  (`promotion_threshold: 0.80`; `minimum_independent_sources: 1`;
  `regression_threshold: 0.50`)
- ADR-001: Learning → Belief → Fact arc now fully operational
- ADR-008: Closed (topology materialized + operators implemented)
- Integration test: Evidence → Belief → Fact pipeline (end-to-end)
- `PROJECT_STATE.md` (this document)

## Open Work
- Belief lifecycle operators not yet implemented:
  `BeliefRegression` (Fact → Belief on contradicting Evidence),
  `BeliefArchival`, `BeliefConflictResolution`.
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
The epistemic arc Evidence → Belief → Fact is now complete in the
reinforcement direction. The regression direction remains unimplemented:
`BeliefRegression` handles the transition Fact → Belief when contradicting
Evidence drives confidence below `regression_threshold: 0.50`.

`EvidenceToBeliefUpdate` already sets Epistemic State to 'Regression
Pending' and emits `BeliefRegressionPending` when the threshold is crossed,
so the triggering mechanism is now in place. `BeliefRegression` reads a
Belief in 'Regression Pending' state, demotes its corresponding Fact to
'Regressed', restores the Belief to 'Active' with the updated confidence,
and records the full regression history on both entities.

This is the next unblocked bottleneck: all inputs and output domains are
defined, no new canonical decisions are required, and no structural
blockers exist.

## Blocked Decisions
None currently blocking. `BeliefRegression` is implementable against
existing canonical basis (ADR-001 + ADR-008).

## Recent Decisions
- **2026-07-16** — `EvidenceToBeliefUpdate` operator implemented and
  test-covered (25 tests). `EPISTEMIC_EVIDENCE/` topology materialized.
  Evidence → Belief → Fact end-to-end pipeline validated.
- **2026-07-16** — `BeliefToFact` operator implemented and test-covered
  (22 tests). `FACTS/` topology materialized. `belief_fact_promotion.md`
  calibrated. ADR-001 Learning→Belief→Fact arc fully operational.
- **2026-07-16** — `BELIEFS/` topology materialized per ADR-007/ADR-008.
  `LearningToBelief` operator implemented and test-covered (18 tests).
  ADR-008 transitioned to Closed.
- **2026-07-16** — ADR-008 accepted and absorbed into canonical documents.
- **2026-07-16** — `PROJECT_STATE.md` introduced as operational context snapshot.
- **2026-07-16** — Session persistence implemented and test-covered.
- **2026-07-16** — Root-level `engine.py` shim added.

## Next Iteration
Implement `BeliefRegression`: reads a Belief entity in 'Regression Pending'
state, locates the corresponding Fact entity in `FACTS/` (by deriving
`fact-<belief-stem>.md`), transitions the Fact to 'Regressed' state,
restores the Belief's Epistemic State to 'Active', appends Change History
to both entities, and emits a `FactRegressed` event. Raises
`BeliefNotRegressionPendingError` if the Belief is not in that state.
Implementable against ADR-001 + ADR-008 with no new canonical decisions.

## Working Contract
- Branch: `main`. All work committed directly to `main`.
- No local artifacts unless a real technical blocker prevents GitHub writes.
- After each relevant implementation: commit + push + verify SHA + respond
  with `STATUS: PUSHED` block.
- `PROJECT_STATE.md` is updated in the same commit as the implementation
  it records. It is never updated in a standalone commit unless the only
  change is a state correction.
- Information here must be verifiable against actual repository content.
  Do not add items that are designed but not yet committed.
- Continue automatically with the next unblocked bottleneck from
  `PROJECT_STATE.md` without asking between iterations.
