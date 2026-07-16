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
- Cognitive pipeline: 11 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`,
  `LearningToBelief`, `BeliefToFact`, `EvidenceToBeliefUpdate`,
  `BeliefRegression`, `BeliefArchival`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`, `tests/test_learning_to_belief.py`,
  `tests/test_belief_to_fact.py`, `tests/test_evidence_to_belief_update.py`,
  `tests/test_belief_regression.py`, `tests/test_belief_archival.py`
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
- `BeliefRegression` operator: Belief (Regression Pending) → Fact (Regressed)
  + Belief (Active); derives Fact path by convention (fact-<stem>.md);
  appends Change History to both entities; emits FactRegressed event;
  idempotent guard (BeliefNotRegressionPendingError + FactNotFoundError)
- `BeliefArchival` operator: Belief (any non-Archived state) → Belief (Archived);
  co-archives corresponding Fact if present (FACTS/fact-<stem>.md → Archived);
  appends Change History to both entities; emits BeliefArchived +
  optional FactArchived; idempotent guard (BeliefAlreadyArchivedError);
  terminal operator — no further epistemic operators defined for Archived state
- `REASONING_PARAMETERS/belief_fact_promotion.md`: calibrated
  (`promotion_threshold: 0.80`; `minimum_independent_sources: 1`;
  `regression_threshold: 0.50`)
- ADR-001: Learning → Belief → Fact arc fully operational
  (reinforcement + regression + archival directions all implemented)
- ADR-008: Closed (topology materialized + full lifecycle implemented)
- Integration tests: Evidence → Belief → Fact pipeline (end-to-end);
  Evidence → Belief → Fact → Regression full arc (end-to-end);
  Belief → Fact → Archival arc (end-to-end);
  Belief → Regression → Archival arc (end-to-end)
- `PROJECT_STATE.md` (this document)

## Open Work
- `BeliefConflictResolution` operator: not yet implemented.
  Resolves a 'Conflicted' Belief by adjudicating competing Evidence;
  transitions to 'Active' or 'Archived'; requires defining the
  conflict-resolution decision rule (no canonical ADR yet — ADR-009
  is the natural home).
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
`BeliefConflictResolution` requires a canonical decision on how conflicted
Beliefs are adjudicated. ADR-008 establishes the 'Conflicted' state and
the invariant that conflicted Beliefs may not be promoted, but does not
specify the resolution algorithm. An ADR-009 is needed before implementation
can proceed.

A lean resolution rule sufficient to unblock implementation:
  "A Conflicted Belief is resolved by re-evaluating net confidence from
   all Applied Evidence. If net confidence >= promotion_threshold the
   Belief is restored to Active (eligible for promotion). If net confidence
   < promotion_threshold the Belief is restored to Active at its current
   confidence (eligible for further Evidence accumulation or Archival).
   The operator never directly promotes; it only resolves the Conflicted
   state. The ConflictedBeliefError guard in BeliefToFact is the sole
   gate on promotion eligibility."

This rule is expressible as a one-ADR decision. Awaiting confirmation
before opening ADR-009.

## Blocked Decisions
- `BeliefConflictResolution`: blocked on ADR-009 (conflict resolution rule).

## Recent Decisions
- **2026-07-16** — `BeliefArchival` operator implemented and test-covered
  (31 tests). Terminal epistemic transition. Full Belief lifecycle
  (Active → Promoted → Regressed → Archived) now operational.
  Next unblocked work: ADR-009 + `BeliefConflictResolution`.
- **2026-07-16** — `BeliefRegression` operator implemented and
  test-covered (28 tests). Full reinforcement + regression epistemic
  cycle now operational.
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
Open ADR-009 to canonicalise the `BeliefConflictResolution` rule.
Proposed decision text is already drafted in Current Bottleneck above.
Awaiting confirmation to proceed.

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
